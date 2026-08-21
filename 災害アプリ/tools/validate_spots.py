#!/usr/bin/env python3
"""危険箇所データの点検（公開・配布の前に必ず通す）

座標の妥当性、重複、レビューの進み具合、閾値の分布、危険度の出方をまとめて調べる。
「誤った地点を危険と表示する」ことを防ぐための最後の関門（docs/07）。

    python3 tools/validate_spots.py --spots data/spots_chiba.json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import geo  # noqa: E402
import risk  # noqa: E402

# 都道府県のおおよその範囲（はみ出していたら座標がおかしい）
BBOXES = {
    "chiba": (139.74, 34.87, 140.90, 36.11),
}
# トンネル・立体は、標高データが「上の地形」を測るため大きな高低差が出て当然。
# 座標のずれとは区別する。
TUNNELISH_RE = re.compile(r"(トンネル|隧道|立体)")
DUP_M = 30.0
IMPLAUSIBLE_DZ_M = 6.0

problems: list[str] = []
notes: list[str] = []


def head(t):
    print(f"\n── {t} " + "─" * max(0, 46 - len(t)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spots", required=True)
    ap.add_argument("--area", default="chiba")
    ap.add_argument("--rains", default="30,50,80,100", help="危険度を試算する時間雨量")
    args = ap.parse_args()

    S = json.loads(Path(args.spots).read_text(encoding="utf-8"))["spots"]
    live = [x for x in S if (x.get("review") or {}).get("status") != "excluded"]

    head("レビューの進み具合")
    st = collections.Counter((x.get("review") or {}).get("status", "pending") for x in S)
    print(f"  全 {len(S)} 件: 確認済み {st['ok']} / 除外 {st['excluded']} / 未確定 {st['pending']}")
    if st["pending"]:
        pend = [x["id"] for x in S if (x.get("review") or {}).get("status", "pending") == "pending"]
        problems.append(f"未確定が {st['pending']} 件あります（{pend[0]}〜{pend[-1]}）。"
                        "未確定のまま公開・配布しないでください")
        print(f"  未確定: {pend[0]}〜{pend[-1]}")

    head("座標の妥当性")
    noxy = [x["id"] for x in live if x.get("lon") is None]
    if noxy:
        problems.append(f"座標が無い地点が {len(noxy)} 件: {noxy[:5]}")
    print(f"  座標なし: {len(noxy)} 件")

    bb = BBOXES.get(args.area)
    if bb:
        out = [x["id"] for x in live if x.get("lon") is not None
               and not (bb[0] <= x["lon"] <= bb[2] and bb[1] <= x["lat"] <= bb[3])]
        if out:
            problems.append(f"対象地域の外に出ている地点が {len(out)} 件: {out[:5]}")
        print(f"  対象地域の外: {len(out)} 件")

    dups = []
    pts = [x for x in live if x.get("lon") is not None]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            a, b = pts[i], pts[j]
            dd = geo.haversine_m(a["lon"], a["lat"], b["lon"], b["lat"])
            if dd < DUP_M:
                dups.append((a, b, dd))
    print(f"  {DUP_M:.0f}m以内に重なる組: {len(dups)} 件")
    for a, b, dd in dups:
        mark = "★同じ座標" if dd < 1 else ""
        print(f"    {a['id']} {a['name'][:18]:<20} ↔ {b['id']} {b['name'][:18]:<20} {dd:>4.0f}m {mark}")
    if dups:
        problems.append(f"座標が重なる組が {len(dups)} 件あります。"
                        "別の構造物なら、どちらかの位置が誤っています")

    head("標高（dz）")
    dz = sorted(x.get("dz", 0) for x in live)
    if dz:
        print(f"  最小 {dz[0]:+.2f}m / 中央 {dz[len(dz)//2]:+.2f}m / 最大 {dz[-1]:+.2f}m")
        print(f"  窪地(<-1m) {sum(1 for v in dz if v < -1)} / "
              f"平坦(±1m) {sum(1 for v in dz if -1 <= v <= 1)} / "
              f"高い(>+1m) {sum(1 for v in dz if v > 1)} 件")
    odd_real, odd_tunnel = [], []
    for x in live:
        if abs(x.get("dz", 0)) <= IMPLAUSIBLE_DZ_M:
            continue
        (odd_tunnel if TUNNELISH_RE.search(x.get("name", "")) else odd_real).append(x)
    if odd_tunnel:
        print(f"\n  高低差が大きいが構造上そうなるもの（トンネル・立体）: {len(odd_tunnel)} 件")
        for x in odd_tunnel:
            print(f"    {x['id']} {x['name'][:22]:<24} dz={x['dz']:+.2f}m")
        notes.append("トンネル・立体は標高データが『上の地形』を測るため、"
                     "大きな高低差が出ても座標の誤りとは限りません")
    if odd_real:
        print(f"\n  高低差が不自然（座標のずれを疑う）: {len(odd_real)} 件")
        for x in odd_real:
            print(f"    {x['id']} {x['name'][:22]:<24} dz={x['dz']:+.2f}m")
        problems.append(f"高低差が不自然な地点が {len(odd_real)} 件（トンネル以外）。"
                        "座標を確認してください")

    head("種別の根拠")
    ks = collections.Counter(x.get("kind_source", "(記録なし)") for x in live)
    for k, v in ks.most_common():
        print(f"  {v:>3} 件  {k}")
    default_n = sum(v for k, v in ks.items() if "既定値" in k)
    if default_n:
        notes.append(f"種別が既定値のままの地点が {default_n} 件。"
                     "ポンプ設備の有無が分かれば閾値が 35→55mm/h に変わります（docs/08 の質問4）")

    head("冠水閾値 T60 の分布")
    rows = []
    for x in live:
        sp = risk.Spot(id=x["id"], name=x.get("name", ""), kind=x.get("kind", "lowland"),
                       lon=x.get("lon") or 0, lat=x.get("lat") or 0,
                       dz=x.get("dz", 0), hist=x.get("hist", 0))
        rows.append((sp.t60, x))
    rows.sort(key=lambda r: r[0])
    vals = [r[0] for r in rows]
    print(f"  最小 {vals[0]:.1f} / 中央 {vals[len(vals)//2]:.1f} / 最大 {vals[-1]:.1f} mm/h"
          f"（幅 {vals[-1]-vals[0]:.1f}）")
    print("  最も危険（閾値が低い）3件:")
    for v, x in rows[:3]:
        print(f"    {v:5.1f} mm/h  {x['id']} {x['name'][:22]}")
    print("  最も鈍い（閾値が高い）3件:")
    for v, x in rows[-3:]:
        print(f"    {v:5.1f} mm/h  {x['id']} {x['name'][:22]}")

    head("時間雨量ごとの危険度")
    print("        " + "".join(f"{'Lv'+str(k):>7}" for k in range(5)))
    flat = []
    for r60 in [float(v) for v in args.rains.split(",")]:
        c = collections.Counter()
        for _, x in rows:
            sp = risk.Spot(id=x["id"], name=x.get("name", ""), kind=x.get("kind", "lowland"),
                           lon=x.get("lon") or 0, lat=x.get("lat") or 0,
                           dz=x.get("dz", 0), hist=x.get("hist", 0))
            c[risk.score(sp, r60=r60)["level"]] += 1
        print(f"  {r60:>4.0f}mm " + "".join(f"{c[k]:>7}" for k in range(5)))
        top = max(c.values())
        if top == len(rows):
            flat.append(r60)
    if flat:
        problems.append(
            f"時間雨量 {'/'.join(f'{v:.0f}' for v in flat)}mm で、全地点が同じレベルになります。"
            "その雨量では『どこが特に危ないか』を伝えられません（docs/04 の較正が必要）")

    print("\n" + "=" * 52)
    if problems:
        print(f"⚠ 対応が必要: {len(problems)} 件")
        for i, p in enumerate(problems, 1):
            print(f"  {i}. {p}")
    else:
        print("✅ 対応が必要な問題は見つかりませんでした")
    if notes:
        print(f"\n参考: {len(notes)} 件")
        for i, n in enumerate(notes, 1):
            print(f"  {i}. {n}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
