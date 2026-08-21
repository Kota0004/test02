#!/usr/bin/env python3
"""osm_snap.py の検証（ネットワーク不要・合成データ）

    python3 tools/test_osm_snap.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import geo  # noqa: E402
import osm_snap as osm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ok, ng = [], []
def check(name, cond, extra=""):
    (ok if cond else ng).append(name + (f" — {extra}" if extra else ""))


def line(lon0, lat0, lon1, lat1, **tags):
    """2点からなる線を作る（idはタグから適当に）"""
    return {"type": "way", "id": abs(hash(json.dumps(tags, sort_keys=True))) % 100000,
            "tags": tags,
            "geometry": [{"lon": lon0, "lat": lat0}, {"lon": lon1, "lat": lat1}]}


def test_categorize():
    cases = [
        ({"highway": "residential", "tunnel": "yes"}, "道路トンネル"),
        ({"highway": "primary", "layer": "-1"}, "掘割・地下（layer<0）"),
        ({"railway": "rail", "bridge": "yes"}, "鉄道橋（ガード下の手がかり）"),
        ({"highway": "residential", "tunnel": "no"}, "その他"),
        ({"highway": "residential"}, "その他"),
    ]
    for tags, want in cases:
        _, got = osm.categorize(tags)
        check(f"種類の判定 {tags}", got == want, f"実際={got}")


def test_snap_nearest():
    spot = {"lon": 140.1000, "lat": 35.6000}
    # 東西の道路トンネル（約110m北）と、さらに遠いトンネル
    ways = [
        line(140.0990, 35.6010, 140.1010, 35.6010, highway="residential", tunnel="yes", name="近いトンネル"),
        line(140.0990, 35.6050, 140.1010, 35.6050, highway="residential", tunnel="yes", name="遠いトンネル"),
    ]
    r = osm.snap_one(spot, ways, max_move=300)
    check("近い方のトンネルへ寄せる", r and r["osm_name"] == "近いトンネル", str(r and r["osm_name"]))
    check("移動距離が妥当（約110m）", r and 100 <= r["distance_m"] <= 120, str(r and r["distance_m"]))
    check("寄せた先の座標が線の上にある", r and abs(r["lat"] - 35.6010) < 1e-4,
          str(r and r["lat"]))


def test_priority():
    spot = {"lon": 140.1000, "lat": 35.6000}
    near_bridge = line(140.0990, 35.6002, 140.1010, 35.6002,
                       railway="rail", bridge="yes", name="すぐ上の鉄道橋")   # 約22m
    far_tunnel = line(140.0990, 35.6022, 140.1010, 35.6022,
                      highway="residential", tunnel="yes", name="遠い道路トンネル")  # 約243m
    r = osm.snap_one(spot, [near_bridge, far_tunnel], max_move=300)
    check("すぐ近くの鉄道橋は、遠い道路トンネルより優先される",
          r and r["osm_name"] == "すぐ上の鉄道橋", str(r and r["osm_name"]))

    close_tunnel = line(140.0990, 35.6003, 140.1010, 35.6003,
                        highway="residential", tunnel="yes", name="近い道路トンネル")  # 約33m
    r2 = osm.snap_one(spot, [near_bridge, close_tunnel], max_move=300)
    check("同じくらいの距離なら道路トンネルを選ぶ",
          r2 and r2["osm_name"] == "近い道路トンネル", str(r2 and r2["osm_name"]))


def test_max_move():
    spot = {"lon": 140.1000, "lat": 35.6000}
    ways = [line(140.0990, 35.6050, 140.1010, 35.6050, highway="residential", tunnel="yes")]
    check("上限を超える距離には寄せない", osm.snap_one(spot, ways, max_move=100) is None)
    check("上限内なら寄せる", osm.snap_one(spot, ways, max_move=800) is not None)


def test_bbox():
    spots = [{"lon": 140.0, "lat": 35.5}, {"lon": 140.5, "lat": 35.9},
             {"lon": None, "lat": None}]
    b = osm.spots_bbox(spots, margin_deg=0.01)
    check("bboxが全地点を含む", b[0] < 35.5 and b[1] < 140.0 and b[2] > 35.9 and b[3] > 140.5, str(b))
    q = osm.build_query(b)
    check("Overpassクエリに3種類の条件が入る",
          q.count("way[") == 3 and "out geom;" in q, q.replace("\\n", " ")[:80])


def test_http_headers_ascii():
    """HTTPヘッダに日本語を入れない。

    requests はヘッダを latin-1 で送るため、日本語が入っていると
    通信する前に UnicodeEncodeError になる（実際にこれで取得に失敗した）。
    再発防止のため、全ツールの User-Agent を機械的に点検する。
    """
    import re

    check("osm_snap の User-Agent が latin-1 で送れる",
          _latin1_ok(osm.USER_AGENT), osm.USER_AGENT)

    pat = re.compile(r'User-Agent"\]?\s*[:=]\s*"([^"]*)"')
    checked = 0
    for path in sorted((ROOT / "tools").glob("*.py")):
        for ua in pat.findall(path.read_text(encoding="utf-8")):
            checked += 1
            check(f"{path.name} の User-Agent が latin-1 で送れる", _latin1_ok(ua), ua)
    check("User-Agent を1つ以上点検した", checked >= 4, f"点検数={checked}")


def _latin1_ok(v: str) -> bool:
    try:
        v.encode("latin-1")
        return True
    except UnicodeEncodeError:
        return False


def test_cli_end_to_end():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        spots = {"version": "test", "spots": [
            {"id": "a", "name": "寄せる対象", "kind": "underpass_gravity",
             "lon": 140.1000, "lat": 35.6000, "evidence": {"verified_at": None}},
            {"id": "b", "name": "確認済み", "kind": "underpass_gravity",
             "lon": 140.1000, "lat": 35.6000, "evidence": {"verified_at": "2026-08-20"}},
            {"id": "c", "name": "近くに何もない", "kind": "lowland",
             "lon": 141.5000, "lat": 35.6000, "evidence": {"verified_at": None}},
        ]}
        sp = tmp / "spots.json"
        sp.write_text(json.dumps(spots, ensure_ascii=False), encoding="utf-8")
        cache = tmp / "osm.json"
        cache.write_text(json.dumps({"ways": [
            line(140.0990, 35.6010, 140.1010, 35.6010,
                 highway="residential", tunnel="yes", name="テストトンネル")]}), encoding="utf-8")

        def run(*extra):
            return subprocess.run(
                [sys.executable, str(ROOT / "tools" / "osm_snap.py"),
                 "--spots", str(sp), "--cache", str(cache), *extra],
                capture_output=True, text=True)

        r = run("--dry-run")
        check("--dry-run が正常終了する", r.returncode == 0, (r.stderr or "")[:100])
        check("--dry-run では書き換えない",
              json.loads(sp.read_text(encoding="utf-8"))["spots"][0]["lat"] == 35.6000)
        check("確認済みの地点は対象外と表示される", "確認済みのため対象外: 1" in r.stdout,
              [l for l in r.stdout.splitlines() if "対象外" in l])
        check("近くに無い地点が報告される", "見つからない: 1" in r.stdout,
              [l for l in r.stdout.splitlines() if "見つからない" in l])

        r = run("--apply")
        check("--apply が正常終了する", r.returncode == 0, (r.stderr or "")[:100])
        after = json.loads(sp.read_text(encoding="utf-8"))
        a = next(x for x in after["spots"] if x["id"] == "a")
        b = next(x for x in after["spots"] if x["id"] == "b")
        check("対象の座標が線の上へ移動する", abs(a["lat"] - 35.6010) < 1e-4, str(a["lat"]))
        check("確認済みの地点は動かさない", b["lat"] == 35.6000, str(b["lat"]))
        check("寄せた根拠が記録される",
              a["params"]["snap"]["matched"] == "道路トンネル"
              and a["params"]["snap"]["osm_name"] == "テストトンネル"
              and a["params"]["snap"]["moved_m"] > 0,
              json.dumps(a["params"]["snap"], ensure_ascii=False))
        check("目視確認を促す注記が入る", "確認してください" in a["evidence"]["note"],
              a["evidence"]["note"])
        check("OSMの出典が記録される",
              any("OpenStreetMap" in x for x in after.get("attribution", [])),
              str(after.get("attribution")))
        check("反映前のバックアップが作られる",
              (tmp / "spots.json.pre-snap.bak").exists())


def main():
    test_categorize()
    test_snap_nearest()
    test_priority()
    test_max_move()
    test_bbox()
    test_http_headers_ascii()
    test_cli_end_to_end()
    print("===== osm_snap.py 検証 =====")
    for s in ok:
        print("  ✅ " + s)
    for s in ng:
        print("  ❌ " + s)
    print(f"\n合計: {len(ok)} 件成功 / {len(ng)} 件失敗")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
