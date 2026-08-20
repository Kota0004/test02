#!/usr/bin/env python3
"""環境診断 — 「いま何ができて、次に何をすればいいか」を1コマンドで出す。

    python3 tools/doctor.py

Python・必要なライブラリ・node・外部サイトへの到達性・データの進み具合を調べ、
最後に「次にやること」を1つだけ提示する。
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OK, WARN, NG = "✅", "⚠️ ", "❌"

# 到達できないと困る外部サイト（用途つき）
SITES = [
    ("www.jma.go.jp", "気象庁（アメダス・ナウキャスト）", True),
    ("cyberjapandata.gsi.go.jp", "国土地理院（地図タイル・標高タイル）", True),
    ("msearch.gsi.go.jp", "国土地理院（住所→座標の変換）", True),
    ("www.ktr.mlit.go.jp", "国交省 関東地整（冠水箇所PDF）", False),
    ("pub.os-alert.info", "千葉市 地下道冠水情報システム", False),
]

results: list[tuple[str, str]] = []
next_steps: list[str] = []


def say(mark: str, text: str) -> None:
    results.append((mark, text))
    print(f"  {mark} {text}")


def head(title: str) -> None:
    print(f"\n── {title} " + "─" * max(0, 46 - len(title)))


def check_python() -> None:
    head("Python")
    v = sys.version_info
    if v >= (3, 9):
        say(OK, f"Python {v.major}.{v.minor}.{v.micro}")
    else:
        say(NG, f"Python {v.major}.{v.minor} — 3.9 以上が必要です")
        next_steps.append("Python 3.9 以上をインストールしてください")


def check_libs() -> None:
    head("Python ライブラリ")
    need = {
        "pdfplumber": "② PDFから冠水箇所の表を読む",
        "PIL": "② 標高タイル・降水タイルの画素を読む（Pillow）",
        "requests": "②③ 気象庁・国土地理院への通信",
    }
    missing = []
    for mod, why in need.items():
        try:
            __import__(mod)
            say(OK, f"{mod} — {why}")
        except Exception:                                   # noqa: BLE001
            say(NG, f"{mod} が入っていません — {why}")
            missing.append(mod)
    if missing:
        next_steps.append("pip install -r tools/requirements.txt を実行してください")


def check_node() -> None:
    head("Node.js（あると便利／必須ではない）")
    if shutil.which("node"):
        v = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip()
        say(OK, f"node {v} — プロトタイプの自動検証に使えます")
        try:
            subprocess.run(["node", "-e", "require('playwright')"],
                           capture_output=True, check=True)
            say(OK, "playwright — 自動検証・サイト調査が使えます")
        except Exception:                                   # noqa: BLE001
            say(WARN, "playwright は未導入（自動検証を使うなら npm i playwright）")
    else:
        say(WARN, "node がありません（手で触って確認するなら不要です）")


def check_network() -> None:
    head("外部サイトへの到達性")
    try:
        import requests
    except Exception:                                       # noqa: BLE001
        say(WARN, "requests が無いため確認できません")
        return
    blocked_required = []
    for host, why, required in SITES:
        try:
            r = requests.get(f"https://{host}/", timeout=10,
                             headers={"User-Agent": "mizumichi-doctor/0.1"})
            say(OK, f"{host} — {why}（HTTP {r.status_code}）")
        except Exception as e:                              # noqa: BLE001
            mark = NG if required else WARN
            say(mark, f"{host} に到達できません — {why}（{type(e).__name__}）")
            if required:
                blocked_required.append(host)
    if blocked_required:
        next_steps.append(
            "必須サイトに到達できません。社内ネットワーク・プロキシ・VPNを確認するか、"
            "別のネットワークで実行してください")


def check_tests() -> None:
    head("同梱ツールの自己検証")
    script = ROOT / "tools" / "run_tests.sh"
    if not script.exists():
        say(NG, "tools/run_tests.sh が見つかりません")
        return
    r = subprocess.run(["bash", str(script)], capture_output=True, text=True)
    fails = [ln for ln in r.stdout.splitlines() if ln.strip().startswith("❌")]
    if r.returncode == 0 and not fails:
        say(OK, "ツールの検証はすべて成功（ネットワーク不要のテスト）")
    else:
        say(NG, f"検証に失敗があります（{len(fails)} 件）")
        for ln in fails[:5]:
            print(f"      {ln.strip()}")
        next_steps.append("./tools/run_tests.sh の失敗内容を確認してください")


def check_data() -> None:
    head("データの進み具合")
    spots_files = sorted((ROOT / "data").glob("spots_*.json"))
    if not spots_files:
        say(WARN, "data/ に危険箇所データがまだありません（ステップ②が未実施）")
        next_steps.append(
            "国交省のPDFを入手して、次を実行してください:\n"
            "        python3 tools/build_spots.py --pdf 一覧表.pdf --area chiba "
            "--out data/spots_chiba.json")
        return

    for f in spots_files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:                              # noqa: BLE001
            say(NG, f"{f.name} を読めません（{e}）")
            continue
        spots = d.get("spots", [])
        with_xy = [s for s in spots if s.get("lon") is not None]
        verified = [s for s in spots if (s.get("evidence") or {}).get("verified_at")]
        with_dz = [s for s in spots if s.get("dz")]
        say(OK, f"{f.name}: {len(spots)} 件")
        print(f"      座標あり {len(with_xy)} / 標高補正済み {len(with_dz)} / "
              f"レビュー済み {len(verified)}")
        if len(verified) < len(spots):
            next_steps.append(
                f"{len(spots) - len(verified)} 件が未レビューです。次で地図を開いて確認できます:\n"
                f"        python3 tools/review_spots.py --spots {f.relative_to(ROOT)}")
        elif not with_dz:
            next_steps.append(
                f"標高補正がまだです:\n"
                f"        python3 tools/enrich_dem.py --in {f.relative_to(ROOT)} "
                f"--out {f.relative_to(ROOT)}")
        else:
            next_steps.append(
                f"雨量を取り込んで危険度を出せます:\n"
                f"        python3 tools/fetch_amedas.py --spots {f.relative_to(ROOT)} "
                f"--out data/risk_latest.json")


def main() -> int:
    print("みずみち 環境診断")
    print(f"リポジトリ: {ROOT}")
    check_python()
    check_libs()
    check_node()
    check_network()
    check_tests()
    check_data()

    ng = sum(1 for m, _ in results if m == NG)
    warn = sum(1 for m, _ in results if m == WARN)
    print("\n" + "=" * 52)
    print(f"結果: 問題 {ng} 件 / 注意 {warn} 件")

    print("\n▶ 次にやること")
    if not next_steps:
        print("  特にありません。")
    else:
        for i, s in enumerate(next_steps, 1):
            print(f"  {i}. {s}")
    print("\n困ったら 災害アプリ/はじめかた.md を見てください。")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
