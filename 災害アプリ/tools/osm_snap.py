#!/usr/bin/env python3
"""OpenStreetMap のトンネル情報を使って、危険箇所の座標を実際の構造物へ寄せる

住所からのジオコーディングは「町丁目の代表点」を返すため、アンダーパスや
ガード下そのものは指さない（実データでも、住所は合っているのに位置が
数十〜数百mずれる、という状態になった）。

OSM には日本のアンダーパスが tunnel / layer=-1 として登録されているので、
各地点の近くにあるトンネル区間へ寄せることで、レビューの出発点を良くする。

⚠️ 自動で寄せた位置も**確定ではない**。必ず review_spots.py で目視確認すること。
   寄せた根拠と移動距離は params.snap に記録される。

使い方:
    # 1) 対象範囲のトンネル情報をまとめて取得（Overpass API に1回だけ問い合わせ）
    python3 tools/osm_snap.py --spots data/spots_chiba.json --fetch

    # 2) 寄せてみる（まず確認だけ）
    python3 tools/osm_snap.py --spots data/spots_chiba.json --dry-run

    # 3) 反映する
    python3 tools/osm_snap.py --spots data/spots_chiba.json --apply

データ出典: © OpenStreetMap contributors（ODbL）。利用時は出典表示が必要。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import geo  # noqa: E402

OVERPASS = "https://overpass-api.de/api/interpreter"

# HTTPヘッダは latin-1 でしか送れないため、日本語を入れてはいけない。
# （入れると UnicodeEncodeError になり、通信する前に失敗する）
USER_AGENT = "mizumichi-osm-snap/0.1 (disaster-prevention research; +https://github.com/Kota0004/test02)"

# 寄せ先の候補。上にあるものほど信頼できる。
# ガード下は「道路側にタグが無く、跨いでいる鉄道側が bridge」という登録も多いので、
# 見つからないときの手がかりとして鉄道橋も拾う。
CATEGORIES = [
    ("道路トンネル", 'way["highway"]["tunnel"]["tunnel"!~"^no$"]'),
    ("掘割・地下（layer<0）", 'way["highway"]["layer"~"^-[0-9]"]'),
    ("鉄道橋（ガード下の手がかり）", 'way["railway"]["bridge"]["bridge"!~"^no$"]'),
]


def build_query(bbox: tuple[float, float, float, float], timeout: int = 180) -> str:
    """bbox = (lat_min, lon_min, lat_max, lon_max)"""
    b = f"({bbox[0]:.5f},{bbox[1]:.5f},{bbox[2]:.5f},{bbox[3]:.5f})"
    parts = "\n  ".join(f"{sel}{b};" for _, sel in CATEGORIES)
    return f"[out:json][timeout:{timeout}];\n(\n  {parts}\n);\nout geom;"


def spots_bbox(spots: list[dict], margin_deg: float = 0.01) -> tuple[float, float, float, float]:
    lons = [s["lon"] for s in spots if s.get("lon") is not None]
    lats = [s["lat"] for s in spots if s.get("lat") is not None]
    if not lons:
        raise SystemExit("座標のある地点がありません。先に build_spots.py を実行してください。")
    return (min(lats) - margin_deg, min(lons) - margin_deg,
            max(lats) + margin_deg, max(lons) + margin_deg)


def fetch(bbox, cache: Path, retries: int = 2) -> dict:
    import requests

    query = build_query(bbox)
    print("Overpass API に問い合わせます（1回だけ・数十秒かかることがあります）")
    print(f"  範囲: 緯度 {bbox[0]:.3f}〜{bbox[2]:.3f} / 経度 {bbox[1]:.3f}〜{bbox[3]:.3f}")
    last = None
    for attempt in range(1, retries + 2):
        try:
            r = requests.post(OVERPASS, data={"data": query}, timeout=240,
                              headers={"User-Agent": USER_AGENT})
            if r.status_code in (429, 504):
                raise requests.exceptions.RetryError(f"混雑しています (HTTP {r.status_code})")
            r.raise_for_status()
            data = r.json()
            break
        except requests.exceptions.RequestException as e:
            # 通信まわりの失敗だけ再試行する。
            # 設定ミスなど、待っても直らないものを再試行すると時間を無駄にするだけ。
            last = e
            if attempt <= retries:
                wait = 20 * attempt
                print(f"  失敗（{e}）。{wait}秒待って再試行します…")
                time.sleep(wait)
            else:
                raise SystemExit(f"Overpass API から取得できませんでした: {last}")
        except Exception as e:                              # noqa: BLE001
            raise SystemExit(
                f"取得に失敗しました（再試行しても直らない種類の失敗です）: "
                f"{type(e).__name__}: {e}")

    ways = [e for e in data.get("elements", []) if e.get("type") == "way" and e.get("geometry")]
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"fetched_at": date.today().isoformat(),
                                 "bbox": bbox, "ways": ways},
                                ensure_ascii=False), encoding="utf-8")
    print(f"  取得: {len(ways)} 本の線 → {cache}")
    return {"ways": ways}


def categorize(tags: dict) -> tuple[int, str]:
    """寄せ先の種類と優先度（小さいほど信頼できる）"""
    if tags.get("highway") and tags.get("tunnel") not in (None, "no"):
        return 0, "道路トンネル"
    if tags.get("highway") and str(tags.get("layer", "")).startswith("-"):
        return 1, "掘割・地下（layer<0）"
    if tags.get("railway") and tags.get("bridge") not in (None, "no"):
        return 2, "鉄道橋（ガード下の手がかり）"
    return 3, "その他"


# 種類ごとのペナルティ[m]。道路トンネルを優先しつつ、
# すぐ近くに鉄道橋（ガード下）があればそちらを選べるようにする。
PRIO_PENALTY_M = 60.0


def snap_one(spot: dict, ways: list[dict], max_move: float) -> dict | None:
    """最も「もっともらしい」線へ寄せる。

    単純な最短距離ではなく、種類のペナルティを足した距離で比べる。
    そうしないと、たまたま近くを通る鉄道橋が、本命の道路トンネルより
    優先されてしまう（逆に、真上に鉄道橋があるガード下は拾えなくなる）。
    """
    best = None
    for w in ways:
        prio, label = categorize(w.get("tags") or {})
        hit = geo.nearest_on_ways(spot["lon"], spot["lat"], [w], max_m=max_move)
        if not hit:
            continue
        effective = hit["distance_m"] + prio * PRIO_PENALTY_M
        if best is None or effective < best["effective"]:
            tags = w.get("tags") or {}
            best = {
                "effective": effective,
                "lon": round(hit["lon"], 6),
                "lat": round(hit["lat"], 6),
                "distance_m": round(hit["distance_m"], 1),
                "matched": label,
                "osm_id": w.get("id"),
                "osm_name": tags.get("name") or tags.get("ref") or "",
            }
    if best:
        best.pop("effective")
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spots", required=True)
    ap.add_argument("--cache", default="data/osm_underpasses.json")
    ap.add_argument("--fetch", action="store_true", help="OSMからトンネル情報を取得する")
    ap.add_argument("--apply", action="store_true", help="寄せた座標を書き込む")
    ap.add_argument("--dry-run", action="store_true", help="寄せる内容を表示するだけ")
    ap.add_argument("--max-move", type=float, default=300.0,
                    help="これ以上離れた線へは寄せない[m]（既定300）")
    ap.add_argument("--include-reviewed", action="store_true",
                    help="人手で確認済みの地点も動かす（既定は動かさない）")
    args = ap.parse_args()

    spots_path = Path(args.spots)
    data = json.loads(spots_path.read_text(encoding="utf-8"))
    spots = data["spots"]
    cache = Path(args.cache)

    if args.fetch:
        fetch(spots_bbox(spots), cache)
        if not (args.apply or args.dry_run):
            print("\n次: python3 tools/osm_snap.py --spots "
                  f"{args.spots} --dry-run  で寄せる内容を確認してください")
            return 0

    if not cache.exists():
        print(f"OSMデータがありません: {cache}\n  先に --fetch を実行してください。", file=sys.stderr)
        return 1
    ways = json.loads(cache.read_text(encoding="utf-8"))["ways"]
    print(f"OSMの線: {len(ways)} 本")

    moved, skipped_reviewed, not_found = [], 0, []
    for s in spots:
        if s.get("lon") is None:
            continue
        if not args.include_reviewed and (s.get("evidence") or {}).get("verified_at"):
            skipped_reviewed += 1
            continue

        res = snap_one(s, ways, args.max_move)
        if not res:
            not_found.append(s["id"])
            continue

        moved.append((s, res))
        if args.apply:
            s["lon"], s["lat"] = res["lon"], res["lat"]
            s.setdefault("params", {})["snap"] = {
                "moved_m": res["distance_m"],
                "matched": res["matched"],
                "osm_id": res["osm_id"],
                "osm_name": res["osm_name"],
                "applied_at": date.today().isoformat(),
                "source": "© OpenStreetMap contributors (ODbL)",
            }
            s.setdefault("evidence", {})["note"] = (
                f"OSMの{res['matched']}へ {res['distance_m']:.0f}m 寄せた位置です。目視で確認してください")

    print(f"\n寄せられた地点: {len(moved)} 件 / 近くに見つからない: {len(not_found)} 件"
          + (f" / 確認済みのため対象外: {skipped_reviewed} 件" if skipped_reviewed else ""))

    if moved:
        dists = sorted(r["distance_m"] for _, r in moved)
        print(f"  移動距離: 中央値 {dists[len(dists)//2]:.0f}m / 最大 {dists[-1]:.0f}m")
        by_cat: dict[str, int] = {}
        for _, r in moved:
            by_cat[r["matched"]] = by_cat.get(r["matched"], 0) + 1
        for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1]):
            print(f"  {k}: {v} 件")
        print("\n  例（移動距離の大きい順に5件）:")
        for s, r in sorted(moved, key=lambda x: -x[1]["distance_m"])[:5]:
            print(f"    {s['id']} {s.get('name','')[:20]:<20} {r['distance_m']:>5.0f}m "
                  f"→ {r['matched']} {r['osm_name']}")
    if not_found:
        print(f"  近くにトンネルが見つからない: {not_found[:10]}"
              + (" ほか" if len(not_found) > 10 else ""))
        print("    → これらは手で位置を確認してください（OSMに未登録の可能性）")

    if args.dry_run or not args.apply:
        print("\n(--dry-run のため書き込んでいません。反映するには --apply)")
        return 0

    bak = spots_path.with_suffix(spots_path.suffix + ".pre-snap.bak")
    if not bak.exists():
        bak.write_text(json.dumps(json.loads(spots_path.read_text(encoding="utf-8")),
                                  ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nバックアップ: {bak}")
    data.setdefault("attribution", []).append("© OpenStreetMap contributors (ODbL)")
    data["attribution"] = sorted(set(data["attribution"]))
    spots_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"書き込み: {spots_path}")
    print("\n次: python3 tools/review_spots.py --spots "
          f"{args.spots} --ipad  で目視確認してください")
    return 0


if __name__ == "__main__":
    sys.exit(main())
