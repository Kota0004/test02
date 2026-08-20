# tools — データ整備・取込ツール

[docs/06_開発ロードマップ.md](../docs/06_開発ロードマップ.md) の「次にやること」を実行するためのスクリプト群。

> 手順を最初から追いたい場合は [はじめかた.md](../はじめかた.md) を見てください。
> 迷ったら `python3 tools/doctor.py` を打てば「次にやること」が出ます。

## セットアップ

```bash
pip install -r tools/requirements.txt
# プロトタイプの自動検証を使う場合のみ
npm i playwright && npx playwright install chromium
```

## 実行順

### ① プロトタイプを動かして確認する

```bash
cd 災害アプリ/prototype && python3 -m http.server 8000 &
open http://localhost:8000/          # 手で触る
node ../tools/verify_prototype.js    # 自動検証（13項目）
node ../tools/verify_ipad.js         # iPadの画面・タッチでの検証（14項目）
```

### ①' いまの状態を診断する

```bash
python3 tools/doctor.py
```

Python・ライブラリ・node・外部サイトへの到達性・データの進み具合をまとめて確認し、
**次にやることを1つだけ提示**する。詰まったらまずこれ。

### ② 道路冠水注意箇所（千葉県内95箇所）を座標付きデータにする

```bash
# 1. PDFを入手（国交省 千葉国道事務所）
#    https://www.ktr.mlit.go.jp/chiba/chiba_index030.html

# 2. まず何が読めるかを確認する
python3 tools/build_spots.py --pdf 一覧表.pdf --dump-text | head -50

# 3. 抽出だけ試す（ジオコーディングなし）
python3 tools/build_spots.py --pdf 一覧表.pdf --no-geocode --out /tmp/dry.json

# 4. 座標を付けて出力（国土地理院の住所検索APIを使用・無料/キー不要）
python3 tools/build_spots.py --pdf 一覧表.pdf --area chiba \
    --source "国交省千葉国道事務所 道路冠水箇所マップ（2026-06-30版）" \
    --out data/spots_chiba.json

# 5. 標高タイルから相対標高 dz を付けて閾値を補正できるようにする
python3 tools/enrich_dem.py --in data/spots_chiba.json --out data/spots_chiba.json

# 6. ★人手レビュー：地図上で座標を確認・修正する（その場でJSONに保存される）
python3 tools/review_spots.py --spots data/spots_chiba.json

# iPad / GitHub Codespaces から使う場合
python3 tools/review_spots.py --spots data/spots_chiba.json --ipad
```

**レビューは省略しない。** 住所からの機械変換は丁目レベルで外れることがあり、
誤った地点を「危険」と表示するのは見逃しとは別種の害になる（docs/07）。
`review_spots.py` は要レビューの地点を順に出し、マーカーのドラッグで座標を直して
Enter で確定できる。航空写真に切り替えればアンダーパスかどうかを目視で確認できる。
変更は操作のたびに保存され、初回に `.bak` が作られる。

PDFのレイアウトは事務所ごとに違う。表として抽出できない場合は `--dump-text` の
出力を見て `build_spots.py` の `HEADER_MAP` / `LINE_RE` を調整する。

### ③ アメダスのリアルタイム雨量を取り込んで危険度を出す

```bash
# 通信あり（気象庁の実データ）
python3 tools/fetch_amedas.py --spots data/spots_chiba.json --out data/risk_latest.json

# 通信なし（フィクスチャで動作確認）
python3 tools/fetch_amedas.py --spots prototype/data/sample_spots.json \
    --fixture-dir tools/fixtures/amedas --out /tmp/risk.json
```

### ④ 千葉市 地下道冠水情報システムのデータ取得口を調べる

```bash
python3 tools/probe_endpoints.py --url https://pub.os-alert.info/chiba/devmap --browser
```

結果を踏まえて [docs/08_自治体連携_打診文案.md](../docs/08_自治体連携_打診文案.md) の文案を送る。

## 検証

```bash
./tools/run_tests.sh
```

すべてネットワーク不要（フィクスチャを使用）。内訳:

| テスト | 確認内容 |
|-------|---------|
| `test_risk_parity.py` | `risk.py` と `prototype/risk.js` が**全2,700ケースで一致**すること、docs/04 の計算例と合うこと |
| `test_build_spots.py` | PDFからの表抽出、種別推定、住所正規化、ジオコーディング結果の信頼度判定 |
| `test_enrich_dem.py` | 標高タイルのRGBデコード（往復・無効値）、相対標高 dz の算出、dz が閾値に効くこと |
| `test_fetch_amedas.py` | アメダスJSONの解釈（品質フラグ・[度,分]変換）、IDW内挿、危険度出力 |
| `test_review_spots.py` | レビュー画面のサーバ側（保存・バックアップ・進捗集計・異常系・再開） |
| `verify_prototype.js` | ブラウザでの実動作13項目（雨量フィルタ・現在地アラート・クールダウン・ラベル・障害時の劣化動作） |
| `verify_ipad.js` | iPad 横/縦でのはみ出し・タップ領域・主要操作 14項目 |

## ファイル

| ファイル | 役割 |
|---------|------|
| `risk.py` | 危険度判定エンジン（サーバ側）。`prototype/risk.js` と同一の式 |
| `geo.py` | タイル座標変換、標高タイルのデコード、IDW内挿 |
| `build_spots.py` | ② 一覧PDF → 座標付き spots JSON + レビュー用CSV |
| `enrich_dem.py` | ② 標高タイルから相対標高 dz を付与 |
| `fetch_amedas.py` | ③ アメダス10分値 → 各地点の雨量と危険度 |
| `probe_endpoints.py` | ④ 公開ページのデータ取得口を調査 |
| `review_spots.py` / `.html` | ② 座標を地図上で確認・修正するレビュー画面（ローカルサーバ） |
| `doctor.py` | 環境診断と「次にやること」の提示 |
| `verify_prototype.js` | ① プロトタイプの自動検証 |
| `fixtures/` | ネットワーク不要のテスト用データ（すべてダミー） |

## ⚠️ 注意

- 気象庁のJSON・タイルは**公式APIとして仕様保証されたものではない**。
  スキーマが変わったら、誤った雨量で誤報を出さないよう**取り込みを止める**こと（docs/07）。
- `fixtures/` のデータはすべて**動作確認用のダミー**で、実在の観測値・危険箇所ではない。
- スクレイピングを行う前に、対象サイトの利用規約と robots.txt を確認すること。
