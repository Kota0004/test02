/* 検証スクリプトの共通処理 */

/* CDN（unpkg）に出られない環境向けの逃げ道。
 *
 *   MAPLIBRE_DIR=$PWD/node_modules/maplibre-gl/dist node verify_prototype.js
 *
 * のように node_modules/maplibre-gl/dist を渡すと、MapLibre をそこから読ませる。
 * 未設定なら何もしないので、CDN に出られる環境（CI 含む）の挙動は変わらない。
 * アプリ側は書き換えないので、検証しているのは本番と同じコード。
 */
async function useLocalMaplibre(page) {
  const dir = process.env.MAPLIBRE_DIR;
  if (!dir) return false;
  const fs = require('fs'), path = require('path');
  await page.route('**/unpkg.com/maplibre-gl**', route => {
    const css = route.request().url().endsWith('.css');
    const file = css ? 'maplibre-gl.css' : 'maplibre-gl.js';
    route.fulfill({
      status: 200,
      contentType: css ? 'text/css' : 'application/javascript',
      body: fs.readFileSync(path.join(dir, file))
    });
  });
  return true;
}

module.exports = { useLocalMaplibre };
