#!/usr/bin/env python3
"""道路冠水注意箇所の一覧PDF → 座標つき spots データ（docs/05-4-2 の「公的PDFルート」）

国土交通省 各地方整備局が公開している「道路冠水注意箇所マップ／一覧表」はPDFでしか
提供されていないため、機械可読なデータに起こす必要がある。本スクリプトは

    PDF → 表の抽出 → 種別の推定 → 住所のジオコーディング → spots JSON + レビュー用CSV

までを行う。**最後の人手レビューは省略しないこと**（docs/05-4-2）。
誤った地点を「危険」と表示するのは、見逃しとは別種の害になる。

使い方:
    # 1) まずPDFを入手（千葉県内: https://www.ktr.mlit.go.jp/chiba/chiba_index030.html）
    python3 tools/build_spots.py --pdf 一覧表.pdf --area chiba --out data/spots_chiba.json

    # ジオコーディングを行わず、抽出結果だけ確認する
    python3 tools/build_spots.py --pdf 一覧表.pdf --no-geocode --out /tmp/dry.json

    # 表として抽出できない場合、何が読めているかを見る
    python3 tools/build_spots.py --pdf 一覧表.pdf --dump-text | head -50
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))

GEOCODER = "https://msearch.gsi.go.jp/address-search/AddressSearch?q={}"

# 表ヘッダの表記ゆれ → 内部キー
HEADER_MAP = {
    "no": ["no", "no.", "番号", "整理番号", "通し番号", "地点番号", "箇所番号"],
    "road": ["路線名", "路線", "道路名", "路線番号"],
    "name": ["箇所名", "地点名", "名称", "冠水箇所", "交差点名", "アンダーパス名", "箇所"],
    "address": ["所在地", "住所", "市町村", "市区町村", "位置"],
    "kind_raw": ["種別", "構造", "区分", "形式", "備考"],
    "admin": ["管理者", "道路管理者", "管理機関"],
}

# 記載文言 → docs/04-3-1 の kind
KIND_RULES = [
    (("ポンプ",), "underpass_pump"),
    (("アンダーパス", "アンダー", "地下道", "立体交差", "ガード", "こ道橋", "掘割"), "underpass_gravity"),
    (("橋詰", "橋詰め", "取付", "橋梁"), "bridge_approach"),
    (("河川", "川沿", "堤内"), "river_adjacent"),
    (("低地", "窪地", "くぼ地", "凹部"), "lowland"),
]


def norm(s: str | None) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFKC", str(s))
    return re.sub(r"\s+", "", s).strip()


def guess_kind(*texts: str) -> str:
    blob = norm("".join(t or "" for t in texts))
    for keys, kind in KIND_RULES:
        if any(k in blob for k in keys):
            return kind
    # 判別できない場合は最も安全側（閾値が低い＝危険と判定されやすい）に倒す。
    # docs/03「安全側に倒す」より。
    return "underpass_gravity"


def map_headers(header_row: list[str]) -> dict[int, str]:
    """表の1行目から「列インデックス → 内部キー」を作る。"""
    out = {}
    for i, cell in enumerate(header_row):
        c = norm(cell).lower().replace("　", "")
        for key, alts in HEADER_MAP.items():
            if any(a in c for a in alts):
                out.setdefault(i, key)
                break
    return out


def extract_rows(pdf_path: Path, dump_text: bool = False) -> list[dict]:
    import logging

    import pdfplumber

    # pdfminer は埋め込みフォントの不備で大量の警告を出すが、表の抽出には影響しない
    logging.getLogger("pdfminer").setLevel(logging.ERROR)

    rows: list[dict] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            if dump_text:
                print(f"--- page {pno} ---")
                print(page.extract_text() or "(テキストなし)")
                continue

            for table in page.extract_tables() or []:
                if len(table) < 2:
                    continue
                # ヘッダ行を探す（先頭3行のうち最も多くのキーに当たる行）
                best_i, best_map = None, {}
                for i in range(min(3, len(table))):
                    m = map_headers([c or "" for c in table[i]])
                    if len(m) > len(best_map):
                        best_i, best_map = i, m
                if not best_map:
                    continue
                for raw in table[best_i + 1:]:
                    rec = {"_page": pno}
                    for idx, key in best_map.items():
                        if idx < len(raw):
                            rec[key] = norm(raw[idx])
                    if any(rec.get(k) for k in ("name", "address", "road")):
                        rows.append(rec)

    if dump_text:
        return []

    if not rows:
        # 表として取れない場合のフォールバック: 行テキストから拾う
        rows = extract_rows_from_text(pdf_path)
    return rows


LINE_RE = re.compile(
    r"^\s*(?P<no>\d{1,4})[\s.、]+(?P<rest>.+?)\s*$")


def extract_rows_from_text(pdf_path: Path) -> list[dict]:
    """罫線のないPDF向けのフォールバック。「番号 + 本文」の行を拾う。"""
    import pdfplumber

    rows = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            for line in (page.extract_text() or "").splitlines():
                m = LINE_RE.match(line)
                if not m:
                    continue
                rest = m.group("rest")
                parts = re.split(r"[\s　]{1,}", rest.strip())
                if len(parts) < 2:
                    continue
                rows.append({
                    "_page": pno,
                    "no": m.group("no"),
                    "road": norm(parts[0]),
                    "name": norm(parts[1]) if len(parts) > 1 else "",
                    "address": norm(parts[2]) if len(parts) > 2 else "",
                    "kind_raw": norm(" ".join(parts[3:])) if len(parts) > 3 else "",
                })
    return rows


def geocode(query: str, session, sleep_s: float, cache: dict) -> dict | None:
    """国土地理院 住所検索API。無料・キー不要。連続アクセスは控えめに。"""
    if query in cache:
        return cache[query]
    url = GEOCODER.format(quote(query))
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:                                  # noqa: BLE001
        print(f"  ! ジオコーディング失敗: {query} ({e})", file=sys.stderr)
        cache[query] = None
        return None
    time.sleep(sleep_s)
    if not data:
        cache[query] = None
        return None
    top = data[0]
    res = {
        "lon": top["geometry"]["coordinates"][0],
        "lat": top["geometry"]["coordinates"][1],
        "title": top["properties"].get("title", ""),
        "n_candidates": len(data),
    }
    cache[query] = res
    return res


def confidence_of(query: str, res: dict | None) -> tuple[float, str]:
    """ジオコーディング結果の確からしさ。低いものは人手レビューに回す。"""
    if not res:
        return 0.0, "ジオコーディング失敗"
    title = norm(res["title"])
    q = norm(query)
    if title == q:
        return 1.0, ""
    if q.startswith(title) and len(title) >= len(q) - 6:
        return 0.8, "住所の末尾（丁目・番地）が一致しない"
    if len(title) <= 6:
        return 0.3, "市区町村レベルまでしか特定できていない"
    return 0.5, "部分一致"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", required=True, help="一覧表PDFのパス、または https:// のURL")
    ap.add_argument("--area", default="chiba", help="ID接頭辞に使うエリア名（既定: chiba）")
    ap.add_argument("--pref", default="千葉県", help="住所に都道府県が無い場合に補う（既定: 千葉県）")
    ap.add_argument("--out", default="data/spots.json")
    ap.add_argument("--review", default=None, help="レビュー用CSVの出力先（既定: --out と同名の .csv）")
    ap.add_argument("--no-geocode", action="store_true", help="座標を付けずに抽出結果だけ出す")
    ap.add_argument("--sleep", type=float, default=1.0, help="ジオコーディングの間隔[秒]")
    ap.add_argument("--limit", type=int, default=0, help="先頭N件だけ処理（動作確認用）")
    ap.add_argument("--dump-text", action="store_true", help="PDFのテキストを表示して終了")
    ap.add_argument("--source", default="", help="出典表記（例: 国交省千葉国道事務所 2026-06-30版）")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if str(args.pdf).startswith("http"):
        import requests
        pdf_path = Path("/tmp") / Path(args.pdf).name
        print(f"PDFを取得: {args.pdf}")
        pdf_path.write_bytes(requests.get(args.pdf, timeout=60).content)

    if not pdf_path.exists():
        print(f"PDFが見つかりません: {pdf_path}", file=sys.stderr)
        return 1

    rows = extract_rows(pdf_path, dump_text=args.dump_text)
    if args.dump_text:
        return 0
    if args.limit:
        rows = rows[:args.limit]
    print(f"抽出した行数: {len(rows)}")
    if not rows:
        print("表を抽出できませんでした。--dump-text で中身を確認し、"
              "HEADER_MAP / LINE_RE を実際のPDFに合わせて調整してください。", file=sys.stderr)
        return 2

    session = None
    if not args.no_geocode:
        import requests
        session = requests.Session()
        session.headers["User-Agent"] = "mizumichi-build-spots/0.1"

    cache: dict = {}
    spots, review = [], []
    for i, r in enumerate(rows, 1):
        addr = r.get("address", "")
        if addr and not addr.startswith(args.pref) and not re.match(r"^..[都道府県]", addr):
            addr = args.pref + addr
        query = addr or f"{args.pref}{r.get('name','')}"
        res = geocode(query, session, args.sleep, cache) if session else None
        conf, note = confidence_of(query, res)

        sid = f"{args.area}-{int(r.get('no') or i):04d}"
        spot = {
            "id": sid,
            "name": r.get("name") or r.get("road") or sid,
            "kind": guess_kind(r.get("kind_raw", ""), r.get("name", ""), r.get("road", "")),
            "lon": res["lon"] if res else None,
            "lat": res["lat"] if res else None,
            "dz": 0.0,                    # enrich_dem.py で埋める
            "hist": 0,                    # 履歴が判明したら更新
            "road": r.get("road", ""),
            "address": addr,
            "evidence": {
                "source": args.source or f"{pdf_path.name}",
                "confidence": round(conf, 2),
                "verified_at": None,      # 人手レビューで日付を入れる
            },
        }
        spots.append(spot)
        review.append({
            "id": sid, "name": spot["name"], "road": spot["road"], "address": addr,
            "kind": spot["kind"], "kind_raw": r.get("kind_raw", ""),
            "lon": spot["lon"], "lat": spot["lat"],
            "geocode_title": res["title"] if res else "",
            "confidence": round(conf, 2), "note": note,
            "needs_review": "YES" if conf < 0.8 else "",
        })
        if i % 20 == 0:
            print(f"  {i}/{len(rows)} 件処理")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "0.1.0",
        "generated_at": date.today().isoformat(),
        "area": args.area,
        "source": args.source or pdf_path.name,
        "note": "★人手レビュー前のデータです。evidence.verified_at が null の地点は未確認。",
        "spots": spots,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    rev = Path(args.review) if args.review else out.with_suffix(".review.csv")
    with rev.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(review[0].keys()))
        w.writeheader()
        w.writerows(review)

    need = sum(1 for r in review if r["needs_review"])
    print(f"\n出力: {out}  ({len(spots)} 件)")
    print(f"レビュー用CSV: {rev}")
    print(f"要レビュー: {need} 件 / {len(review)} 件")
    print("\n次の手順: CSVを開いて座標を地図で確認し、正しいものは confidence を 1.0、"
          "evidence.verified_at に日付を入れてから本番データに昇格させてください。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
