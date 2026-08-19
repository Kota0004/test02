#!/usr/bin/env python3
"""標高タイルから各地点の相対標高 dz を求めて spots データに書き戻す（docs/04-3-2）

dz = 地点の標高 − 半径100mの円周上の標高の中央値

負の値ほど「周囲より窪んでいる」＝水が集まりやすい。これを冠水閾値 T60 の補正に使う。
出典データ: 国土地理院 標高タイル（https://maps.gsi.go.jp/development/demtile.html）

使い方:
    python3 tools/enrich_dem.py --in data/spots_chiba.json --out data/spots_chiba.json
    python3 tools/enrich_dem.py --in data/spots_chiba.json --dry-run     # 表示のみ
"""
from __future__ import annotations

import argparse
import io
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import geo  # noqa: E402


class ElevationSampler:
    """地理院 PNG 標高タイルから標高を引く。タイルはメモリにキャッシュする。

    テストではこのクラスを継承して fetch_tile を差し替える（ネットワーク不要）。
    """

    def __init__(self, zoom: int = 15, session=None):
        self.zoom = zoom
        self.cache: dict[str, object] = {}
        self.session = session
        self.misses = 0

    def fetch_tile(self, url: str):
        from PIL import Image
        if self.session is None:
            import requests
            self.session = requests.Session()
            self.session.headers["User-Agent"] = "mizumichi-enrich-dem/0.1"
        r = self.session.get(url, timeout=20)
        if r.status_code == 404:
            return None                      # そのタイル種別に該当データなし
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content)).convert("RGB")

    def elevation(self, lon: float, lat: float) -> float | None:
        """解像度の高いタイルから順に試し、最初に有効値が取れたものを返す。"""
        for name, tmpl, maxz in geo.DEM_TILES:
            z = min(self.zoom, maxz)
            tx, ty, px, py = geo.lonlat_to_tile_pixel(lon, lat, z)
            url = tmpl.format(z=z, x=tx, y=ty)
            if url not in self.cache:
                try:
                    self.cache[url] = self.fetch_tile(url)
                except Exception as e:                      # noqa: BLE001
                    print(f"  ! タイル取得失敗 {url}: {e}", file=sys.stderr)
                    self.cache[url] = None
            img = self.cache[url]
            if img is None:
                continue
            r, g, b = img.getpixel((px, py))[:3]
            h = geo.decode_dem_pixel(r, g, b)
            if h == h:                        # NaN でなければ有効
                return h
        self.misses += 1
        return None


def relative_elevation(sampler: ElevationSampler, lon: float, lat: float,
                       radius_m: float = 100.0, n: int = 8) -> tuple[float | None, dict]:
    """dz と内訳を返す。"""
    center = sampler.elevation(lon, lat)
    if center is None:
        return None, {"reason": "中心の標高が取得できない"}
    ring = []
    for dlon, dlat in geo.ring_offsets(radius_m, lat, n):
        h = sampler.elevation(lon + dlon, lat + dlat)
        if h is not None:
            ring.append(h)
    if len(ring) < 3:
        return None, {"reason": f"周囲の標高が{len(ring)}点しか取得できない"}
    med = statistics.median(ring)
    return center - med, {"center": center, "ring_median": med, "ring_n": len(ring)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", default=None)
    ap.add_argument("--radius", type=float, default=100.0, help="比較する円の半径[m]")
    ap.add_argument("--zoom", type=int, default=15)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(Path(args.src).read_text(encoding="utf-8"))
    spots = data["spots"]
    sampler = ElevationSampler(zoom=args.zoom)

    updated = skipped = 0
    for s in spots:
        if s.get("lon") is None or s.get("lat") is None:
            skipped += 1
            continue
        dz, info = relative_elevation(sampler, s["lon"], s["lat"], args.radius)
        if dz is None:
            print(f"  - {s['id']} {s['name']}: dz を算出できません（{info.get('reason')}）")
            skipped += 1
            continue
        s["dz"] = round(dz, 2)
        s.setdefault("params", {})["dz_source"] = f"地理院標高タイル z{args.zoom} r{args.radius:.0f}m"
        updated += 1
        print(f"  + {s['id']} {s['name']}: dz={dz:+.2f}m "
              f"(標高 {info['center']:.1f}m / 周囲中央値 {info['ring_median']:.1f}m)")

    print(f"\n更新 {updated} 件 / スキップ {skipped} 件")
    if args.dry_run:
        print("(--dry-run のため書き込みません)")
        return 0
    out = Path(args.dst or args.src)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"出力: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
