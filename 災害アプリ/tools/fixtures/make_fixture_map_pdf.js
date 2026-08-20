/* 「1ページ目が地図（番号だけ）、2ページ目が一覧表」という実物に近い構成の
   テスト用PDFを生成する。--inspect が一覧表のページを正しく見つけられるかの検証用。

   使い方: node tools/fixtures/make_fixture_map_pdf.js  （要 playwright） */
const { chromium } = require('playwright');
const path = require('path');

const NUMS = Array.from({ length: 95 }, (_, i) => i + 1);
/* 実物（国交省 千葉県内 アンダーパス部等の道路冠水注意箇所）と同じ列構成にしてある。
   列: No. / 市町村名 / 道路種別 / 路線名 / 地先名又は通称名 / 問合せ先(国・県・市町村) */
const HEADER = ['No.', '市町村名', '道路種別', '路線名', '地先名又は通称名', '国', '県', '市町村'];
const ROWS_P2 = [
  ['1', 'サンプル市', '市道', 'サンプル00-002号線', 'サンプル町1-1（サンプル地下道）', '', '', '○'],
  ['2', 'サンプル市', '県道', 'サンプル123号',      'サンプル台2-3（ポンプ有アンダーパス）', '', '○', ''],
  ['3', 'テスト市',   '国道', 'サンプル14号',        'テスト3-4（サンプル橋詰め）', '○', '', ''],
];
// 続きのページ（2/2）には見出し行が無い。これを読み落とすと後半が丸ごと消える。
const ROWS_P3 = [
  ['4', 'テスト市',   '市道', 'サンプル18号線', 'テスト4191-1（サンプル連絡道ガード下）', '', '', '○'],
  ['5', 'ダミー町',   '町道', 'サンプル5号線',  'ダミー字くぼ地5-6', '', '', '○'],
];

const html = `<!doctype html><html lang="ja"><meta charset="utf-8">
<style>
  @page{size:A4;margin:15mm}
  body{font-family:'Noto Sans CJK JP','Noto Sans JP',sans-serif;margin:0}
  .page{page-break-after:always;height:250mm;position:relative}
  .page:last-child{page-break-after:auto}
  h1{font-size:12pt;margin:0 0 6mm}
  .num{position:absolute;font-size:7pt}
  table{border-collapse:collapse;width:100%}
  th,td{border:1px solid #333;padding:3px 6px;font-size:9pt}
  th{background:#eee}
</style>
<div class="page">
  <h1>■千葉県内におけるアンダーパス部等の道路冠水注意箇所マップ（テスト用ダミー）</h1>
  ${NUMS.map(n => `<div class="num" style="left:${(n*37)%160+10}mm;top:${(n*23)%200+20}mm">${n}</div>`).join('')}
</div>
<div class="page">
  <h1>■サンプル県内におけるアンダーパス部等の道路冠水注意箇所（１／２）（テスト用ダミー）</h1>
  <table>
    <tr>${HEADER.map(h => `<th>${h}</th>`).join('')}</tr>
    ${ROWS_P2.map(r => '<tr>' + r.map(c => `<td>${c}</td>`).join('') + '</tr>').join('\n    ')}
  </table>
</div>
<div class="page">
  <h1>■サンプル県内におけるアンダーパス部等の道路冠水注意箇所（２／２）（テスト用ダミー）</h1>
  <table>
    ${ROWS_P3.map(r => '<tr>' + r.map(c => `<td>${c}</td>`).join('') + '</tr>').join('\n    ')}
  </table>
</div>
</html>`;

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'load' });
  const out = path.join(__dirname, 'sample_map_then_list.pdf');
  await page.pdf({ path: out, format: 'A4', printBackground: true });
  await browser.close();
  console.log('生成:', out);
})();
