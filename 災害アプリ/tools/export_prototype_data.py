#!/usr/bin/env python3
"""レビュー済みデータを、アプリ（prototype）が読む形に書き出す

公開されるファイルなので、次を守る:
  ・除外した地点は出さない
  ・人手で未確認の地点は verified=false を付けて出す（確認済みと偽らない）
  ・出典を必ず埋め込む

    python3 tools/export_prototype_data.py --in data/spots_chiba.json \\
        --out prototype/data/spots_chiba.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import risk  # noqa: E402

KEEP = ("id", "name", "kind", "lon", "lat", "dz", "hist", "road", "road_type", "address")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    ap.add_argument("--area-name", default="千葉県")
    args = ap.parse_args()

    src = json.loads(Path(args.src).read_text(encoding="utf-8"))
    out, skipped = [], 0
    for s in src["spots"]:
        status = (s.get("review") or {}).get("status", "pending")
        if status == "excluded" or s.get("lon") is None:
            skipped += 1
            continue
        ev = s.get("evidence") or {}
        rec = {k: s.get(k) for k in KEEP if s.get(k) is not None}
        rec["verified"] = bool(ev.get("verified_at"))
        rec["t60"] = round(risk.compute_t60(s), 1)
        snap = (s.get("params") or {}).get("snap")
        if snap:
            rec["snap"] = {"moved_m": snap.get("moved_m"), "matched": snap.get("matched"),
                           "confidence": snap.get("confidence")}
        out.append(rec)

    verified = sum(1 for r in out if r["verified"])
    payload = {
        "version": "1.0.0",
        "generated_at": date.today().isoformat(),
        "area": args.area_name,
        "counts": {"total": len(out), "verified": verified,
                   "unverified": len(out) - verified},
        "attribution": [
            "危険箇所: " + (src.get("spots", [{}])[0].get("evidence", {}) or {}).get(
                "source", "国土交通省 道路冠水注意箇所マップ"),
            "位置の補正: © OpenStreetMap contributors (ODbL)",
            "地図・標高: 地理院タイル（国土地理院）",
        ],
        "disclaimer": (
            "参考情報です。通行の可否を保証するものではありません。"
            "最終判断は現地の状況で行ってください。"
            f"位置が人手で未確認の地点が {len(out) - verified} 件含まれます。"),
        "spots": out,
    }
    dst = Path(args.dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"書き出し: {dst}")
    print(f"  {len(out)} 件（確認済み {verified} / 未確認 {len(out)-verified}）"
          f" ／ 除外・座標なしで省いた {skipped} 件")
    print(f"  閾値 T60: {min(r['t60'] for r in out):.0f}〜{max(r['t60'] for r in out):.0f} mm/h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
