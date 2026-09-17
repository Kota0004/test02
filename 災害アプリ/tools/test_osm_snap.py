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


def test_name_tokens():
    """路線名・通称から、照合に使える手がかりだけを取り出す。"""
    cases = [
        # (路線名, 通称, 道路種別, 期待する番号, 期待する名称の一部)
        ("国道356号", "国道356号バイパス", "国道", {"356"}, None),
        ("297号", "五井アンダーパス", "国道（県管理）", {"297"}, "五井"),
        ("市道00-002号線", "袖ケ浦1丁目11番地先", "市道", set(), None),
        ("新港穴川線", "新港穴川線地下道", "市道", set(), "新港穴川"),
    ]
    for road, name, rt, want_refs, want_name in cases:
        refs, names = osm.name_tokens(road, name, rt)
        check(f"番号の抽出 {road}", refs == want_refs, f"実際={sorted(refs)} 期待={sorted(want_refs)}")
        if want_name:
            check(f"名称の抽出 {road}", want_name in names, f"実際={sorted(names)}")
        else:
            check(f"住所や整理番号を名称にしない {road}",
                  not any(("丁目" in n or "番地先" in n) for n in names), f"実際={sorted(names)}")

    check("一般語（アンダーパス）だけでは一致させない",
          osm.name_bonus(*osm.name_tokens("", "五井アンダーパス"),
                         {"name": "○○アンダーパス"})[0] == 0)
    check("市道の整理番号を国道の ref に一致させない",
          osm.name_bonus(*osm.name_tokens("市道00-002号線", "袖ケ浦1丁目11番地先", "市道"),
                         {"ref": "2", "highway": "trunk"})[0] == 0)
    refs, names = osm.name_tokens("国道356号", "国道356号バイパス", "国道")
    check("複数の ref を持つ線でも一致する",
          osm.name_bonus(refs, names, {"ref": "126;356"})[0] == osm.REF_BONUS_M)


def test_name_match_wins():
    """名前が一致する線は、多少遠くても優先される。"""
    spot = {"lon": 140.1000, "lat": 35.6000, "road": "297号",
            "road_type": "国道（県管理）", "name": "五井アンダーパス"}
    near_other = line(140.0990, 35.6005, 140.1010, 35.6005,
                      highway="residential", tunnel="yes", name="無関係なトンネル")   # 約55m
    far_match = line(140.0990, 35.6014, 140.1010, 35.6014,
                     highway="trunk", tunnel="yes", ref="297", name="国道297号")      # 約155m
    r = osm.snap_one(spot, [near_other, far_match], max_move=300)
    check("路線番号が一致する線を選ぶ（多少遠くても）",
          r and r["osm_name"] == "国道297号", str(r and r["osm_name"]))
    check("一致の理由が記録される", r and "297" in r["name_match"], str(r and r["name_match"]))
    check("確からしさが「高」になる", r and r["snap_confidence"] == "高", str(r and r["snap_confidence"]))

    # 名前が一致しなければ、近い方が選ばれる
    r2 = osm.snap_one({"lon": 140.1000, "lat": 35.6000, "road": "", "name": ""},
                      [near_other, far_match], max_move=300)
    check("名前の手がかりが無ければ近い方を選ぶ",
          r2 and r2["osm_name"] == "無関係なトンネル", str(r2 and r2["osm_name"]))


def test_line_normalization():
    """「JR総武線」と「総武本線」は同じ路線として扱う。"""
    cases = [("JR総武線下", {"総武"}), ("総武本線", {"総武"}),
             ("JR常磐線中原ガード", {"常磐"}), ("東武野田線下", {"東武野田"}),
             ("JR武蔵野線下", {"武蔵野"}), ("総武緩行線", {"総武緩行"})]
    for text, want in cases:
        got = osm.line_cores(text)
        check(f"路線名の正規化 {text}", got == want, f"実際={sorted(got)} 期待={sorted(want)}")

    check("JR総武線 と 総武本線 は同一",
          osm.lines_agree(osm.line_cores("JR総武線"), osm.line_cores("総武本線")))
    check("東武野田線 と 野田線 は同一",
          osm.lines_agree(osm.line_cores("東武野田線"), osm.line_cores("野田線")))
    check("JR常磐線 と 東武野田線 は別",
          not osm.lines_agree(osm.line_cores("JR常磐線"), osm.line_cores("東武野田線")))


def test_line_conflict():
    """資料と違う路線に寄せない。動かさずにヒントだけ残す。"""
    spot = {"lon": 140.1000, "lat": 35.6000, "name": "JR常磐線中原ガード", "road": ""}
    wrong = line(140.0990, 35.6013, 140.1010, 35.6013,
                 railway="rail", bridge="yes", name="東武野田線")     # 約144m
    r = osm.snap_one(spot, [wrong], max_move=300, max_move_unnamed=150)
    check("別路線でも候補としては返る（ヒントに使う）", r is not None)
    check("食い違いとして印が付く", osm.is_conflict(r), str(r and r.get("conflict_note")))
    check("確からしさは 低", r and r["snap_confidence"] == "低", str(r and r["snap_confidence"]))
    check("理由に資料の路線が出る", r and "常磐" in r["conflict_note"], str(r and r["conflict_note"]))
    check("一致扱いにはしない", r and r["name_match"] == "", str(r and r["name_match"]))

    right = line(140.0990, 35.6013, 140.1010, 35.6013,
                 railway="rail", bridge="yes", name="常磐線")
    r2 = osm.snap_one(spot, [right], max_move=300, max_move_unnamed=150)
    check("同じ路線なら一致扱い", r2 and not osm.is_conflict(r2) and r2["snap_confidence"] == "高",
          str(r2 and (r2["snap_confidence"], r2["name_match"])))

    # 「JR総武線」の地点が「総武本線」に当たれば一致（かつては食い違い扱いだった）
    spot2 = {"lon": 140.1000, "lat": 35.6000, "name": "JR総武線下", "road": ""}
    honsen = line(140.0990, 35.6005, 140.1010, 35.6005,
                  railway="rail", bridge="yes", name="総武本線")
    r3 = osm.snap_one(spot2, [honsen], max_move=300, max_move_unnamed=150)
    check("JR総武線 → 総武本線 は一致として扱う",
          r3 and r3["snap_confidence"] == "高" and "総武本線" in r3["name_match"],
          str(r3 and (r3["snap_confidence"], r3["name_match"])))


def test_conflict_not_applied():
    """食い違う地点は座標を動かさず、ヒントだけ記録する。"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        sp = tmp / "spots.json"
        sp.write_text(json.dumps({"version": "test", "spots": [
            {"id": "x", "name": "JR常磐線中原ガード", "kind": "underpass_gravity",
             "lon": 140.1000, "lat": 35.6000, "evidence": {"verified_at": None}}]},
            ensure_ascii=False), encoding="utf-8")
        cache = tmp / "osm.json"
        cache.write_text(json.dumps({"ways": [
            line(140.0990, 35.6013, 140.1010, 35.6013,
                 railway="rail", bridge="yes", name="東武野田線")]}), encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "osm_snap.py"),
             "--spots", str(sp), "--cache", str(cache), "--apply"],
            capture_output=True, text=True)
        check("食い違いがあってもCLIは正常終了する", r.returncode == 0, (r.stderr or "")[:100])
        check("食い違いとして報告される", "路線が食い違うため動かさない: 1" in r.stdout,
              [l for l in r.stdout.splitlines() if "食い違" in l][:1])
        after = json.loads(sp.read_text(encoding="utf-8"))["spots"][0]
        check("座標は動かさない", after["lat"] == 35.6000 and after["lon"] == 140.1000,
              f"{after['lat']},{after['lon']}")
        hint = (after.get("params") or {}).get("snap_hint")
        check("近くに何があったかをヒントとして残す",
              hint and "東武野田線" in hint["nearby"] and hint["not_applied"] is True,
              json.dumps(hint, ensure_ascii=False) if hint else "なし")
        check("探すべき路線を注記に書く", "常磐" in after["evidence"]["note"],
              after["evidence"]["note"])


def test_snap_confidence():
    check("名前一致は 高", osm.snap_confidence(
        {"name_match": "路線番号が一致（297）", "distance_m": 250})[0] == "高")
    check("名前不一致でも近ければ 中", osm.snap_confidence(
        {"name_match": "", "distance_m": 60})[0] == "中")
    check("名前不一致で80m超は 低", osm.snap_confidence(
        {"name_match": "", "distance_m": 100})[0] == "低")
    check("名前一致で大きく動いた場合は理由に注記",
          "元の座標" in osm.snap_confidence(
              {"name_match": "名称が一致（五香アンダーパス）", "distance_m": 258})[1])
    check("名前不一致で遠ければ 低", osm.snap_confidence(
        {"name_match": "", "distance_m": 260})[0] == "低")
    lv, why = osm.snap_confidence({"name_match": "", "distance_m": 260})
    check("低のときは理由が出る", "別の構造物" in why, why)


def test_max_move():
    spot = {"lon": 140.1000, "lat": 35.6000}
    ways = [line(140.0990, 35.6050, 140.1010, 35.6050, highway="residential", tunnel="yes")]
    check("上限を超える距離には寄せない", osm.snap_one(spot, ways, max_move=100) is None)
    check("上限内なら寄せる", osm.snap_one(spot, ways, max_move=800) is not None)


def test_two_tier_limit():
    """名前が一致する線は遠くても、一致しない線は近くだけ。

    実データで「名前が合わないのに240〜296m動く」候補がほぼ別の構造物だったため、
    名前の一致有無で上限を分ける。誤った位置に置くより、動かさない方が安全。
    """
    # 約255m離れた線
    far_named = line(140.0990, 35.6023, 140.1010, 35.6023,
                     highway="residential", tunnel="yes", name="五香アンダーパス")
    far_other = line(140.0990, 35.6023, 140.1010, 35.6023,
                     highway="residential", tunnel="yes", name="無関係な通り")
    near_unnamed = line(140.0990, 35.6005, 140.1010, 35.6005,
                        highway="residential", tunnel="yes")

    named = {"lon": 140.1000, "lat": 35.6000, "road": "", "road_type": "市道", "name": "五香立体"}
    plain = {"lon": 140.1000, "lat": 35.6000, "road": "", "road_type": "市道", "name": "八幡1丁目"}

    r = osm.snap_one(named, [far_named], max_move=300, max_move_unnamed=150)
    check("名前が一致すれば255mでも寄せる", r is not None and r["snap_confidence"] == "高",
          str(r and (r["distance_m"], r["snap_confidence"])))
    check("大きく動いた場合は注記が出る",
          r is not None and "元の座標" in r["why"], str(r and r["why"]))

    check("名前が一致しない255mには寄せない",
          osm.snap_one(plain, [far_other], max_move=300, max_move_unnamed=150) is None)

    r3 = osm.snap_one(plain, [near_unnamed], max_move=300, max_move_unnamed=150)
    check("名前が一致しなくても近ければ寄せる",
          r3 is not None and r3["snap_confidence"] == "中",
          str(r3 and (r3["distance_m"], r3["snap_confidence"])))

    check("上限を揃えれば従来どおり（後方互換）",
          osm.snap_one(plain, [far_other], max_move=300) is not None)


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
    test_name_tokens()
    test_name_match_wins()
    test_line_normalization()
    test_line_conflict()
    test_conflict_not_applied()
    test_snap_confidence()
    test_max_move()
    test_two_tier_limit()
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
