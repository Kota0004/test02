/* 「1ページ目が地図（番号だけ）、2ページ目が一覧表」という実物に近い構成の
   テスト用PDFを生成する。--inspect が一覧表のページを正しく見つけられるかの検証用。

   使い方: node tools/fixtures/make_fixture_map_pdf.js  （要 playwright） */
const { chromium } = require('playwright');
const path = require('path');

const NUMS = Array.from({ length: 95 }, (_, i) => i + 1);
const ROWS = [
  ['1', '国道○号', 'サンプル地下道A', '千葉市中央区サンプル町1-1', 'アンダーパス', '国交省'],
  ['2', '国道○号', 'サンプル地下道B', '千葉市花見川区サンプル2-3', 'アンダーパス（ポンプ有）', '国交省'],
  ['3', '県道○号', 'サンプル橋詰め',   '船橋市サンプル3-4',         '橋詰め',       '千葉県'],
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
  <h1>道路冠水注意箇所一覧表（テスト用ダミー）</h1>
  <table>
    <tr><th>番号</th><th>路線名</th><th>箇所名</th><th>所在地</th><th>種別</th><th>管理者</th></tr>
    ${ROWS.map(r => '<tr>' + r.map(c => `<td>${c}</td>`).join('') + '</tr>').join('\n    ')}
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
