#!/usr/bin/env python3
"""build_spots.py の検証（ネットワーク不要）

    python3 tools/test_build_spots.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_spots as bs  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "sample_kansui_list.pdf"
FIXTURE_MAP = Path(__file__).resolve().parent / "fixtures" / "sample_map_then_list.pdf"

ok, ng = [], []
def check(name, cond, extra=""):
    (ok if cond else ng).append(name + (f" — {extra}" if extra else ""))


def test_guess_kind():
    cases = {
        "アンダーパス": "underpass_gravity",
        "アンダーパス（ポンプ有）": "underpass_pump",
        "ガード下": "underpass_gravity",
        "立体交差": "underpass_gravity",
        "地下道": "underpass_gravity",
        "橋詰め": "bridge_approach",
        "低地": "lowland",
        "くぼ地": "lowland",
        "河川隣接": "river_adjacent",
        "": "underpass_gravity",          # 不明なときは安全側（閾値が低い方）
    }
    for text, want in cases.items():
        got = bs.guess_kind(text)
        check(f"種別推定 {text or '(空)'!r} → {want}", got == want, f"実際={got}")


def test_norm_and_headers():
    check("全角/空白の正規化", bs.norm(" 千葉　市 ") == "千葉市", bs.norm(" 千葉　市 "))
    hm = bs.map_headers(["番号", "路線名", "箇所名", "所在地", "種別", "管理者"])
    check("ヘッダ対応づけ", hm == {0: "no", 1: "road", 2: "name", 3: "address", 4: "kind_raw", 5: "admin"}, str(hm))
    hm2 = bs.map_headers(["No.", "道路名", "地点名", "住所"])
    check("ヘッダの表記ゆれ吸収", hm2 == {0: "no", 1: "road", 2: "name", 3: "address"}, str(hm2))


def test_confidence():
    q = "千葉県千葉市中央区サンプル町1-1"
    check("完全一致は confidence 1.0",
          bs.confidence_of(q, {"title": q, "lon": 0, "lat": 0})[0] == 1.0)
    check("市区町村止まりは低信頼",
          bs.confidence_of(q, {"title": "千葉市", "lon": 0, "lat": 0})[0] <= 0.3)
    check("失敗は 0.0", bs.confidence_of(q, None)[0] == 0.0)


def test_extract():
    if not FIXTURE.exists():
        check("フィクスチャPDFが存在する", False,
              "node tools/fixtures/make_fixture_pdf.js で生成してください")
        return
    rows = bs.extract_rows(FIXTURE)
    check("PDFから8行抽出できる", len(rows) == 8, f"実際={len(rows)}行")
    if len(rows) == 8:
        kinds = [bs.guess_kind(r.get("kind_raw", ""), r.get("name", ""), r.get("road", ""))
                 for r in rows]
        want = ["underpass_gravity", "underpass_pump", "bridge_approach", "lowland",
                "underpass_gravity", "river_adjacent", "lowland", "underpass_gravity"]
        check("種別が期待どおり推定される", kinds == want, f"実際={kinds}")
        check("所在地が読めている", all(r.get("address") for r in rows))


def test_map_and_list_pdf():
    """1ページ目が地図（番号だけ）、2ページ目が一覧表、という実物に近い構成。

    実際の国交省の資料がこの形（地図PDFに住所が入っていない）だったため、
    どのページが一覧表かを見つけられること、そのページだけを読めることを確認する。
    """
    if not FIXTURE_MAP.exists():
        check("地図＋一覧表のフィクスチャがある", False,
              "node tools/fixtures/make_fixture_map_pdf.js で生成してください")
        return

    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        bs.inspect_pdf(FIXTURE_MAP)
    out = buf.getvalue()
    check("--inspect が一覧表のページ(2)を指す", "一覧表がありそうなページ: [2]" in out,
          [ln for ln in out.splitlines() if "ありそうな" in ln])
    check("--inspect が1ページ目を地図と判定する", "1ページ: 地図（番号だけ）らしい" in out,
          [ln for ln in out.splitlines() if ln.startswith("--- 1ページ")])

    rows_all = bs.extract_rows(FIXTURE_MAP)
    check("全ページ走査でも一覧表の3行だけが取れる（地図から誤検出しない）",
          len(rows_all) == 3, f"実際={len(rows_all)}行")

    rows_p2 = bs.extract_rows(FIXTURE_MAP, only_page=2)
    check("--page 2 でそのページだけ読める", len(rows_p2) == 3, f"実際={len(rows_p2)}行")

    rows_p1 = bs.extract_rows(FIXTURE_MAP, only_page=1)
    check("--page 1（地図）からは行が取れない", len(rows_p1) == 0, f"実際={len(rows_p1)}行")


def test_geocode_with_fake_session():
    """ネットワークを使わずジオコーディング処理の形を確認する。"""
    class FakeResp:
        def __init__(self, data): self._d = data
        def raise_for_status(self): pass
        def json(self): return self._d

    class FakeSession:
        calls = []
        def get(self, url, timeout=0):
            FakeSession.calls.append(url)
            return FakeResp([{
                "geometry": {"coordinates": [140.1065, 35.6108]},
                "properties": {"title": "千葉県千葉市中央区サンプル町1-1"},
            }])

    cache = {}
    s = FakeSession()
    res = bs.geocode("千葉県千葉市中央区サンプル町1-1", s, 0.0, cache)
    check("ジオコーディング結果を座標に変換できる",
          res and abs(res["lon"] - 140.1065) < 1e-9 and abs(res["lat"] - 35.6108) < 1e-9, str(res))
    bs.geocode("千葉県千葉市中央区サンプル町1-1", s, 0.0, cache)
    check("同一クエリはキャッシュされ再リクエストしない", len(FakeSession.calls) == 1,
          f"リクエスト数={len(FakeSession.calls)}")


def main():
    test_guess_kind()
    test_norm_and_headers()
    test_confidence()
    test_extract()
    test_map_and_list_pdf()
    test_geocode_with_fake_session()
    print("===== build_spots.py 検証 =====")
    for s in ok:
        print("  ✅ " + s)
    for s in ng:
        print("  ❌ " + s)
    print(f"\n合計: {len(ok)} 件成功 / {len(ng)} 件失敗")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
