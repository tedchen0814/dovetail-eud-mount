// 把本資料夾的網頁正本複製到 dist/，供 Vercel 部署（只部署 dist/）。
const fs = require('fs');
const path = require('path');
const out = path.join(__dirname, 'dist');
fs.mkdirSync(out, { recursive: true });
const pages = [
  ['鳩尾槽提案動畫.html', 'index.html'],
  ['組合A_3D.html', 'combo-a-3d.html']
];
for (const [src, dst] of pages) {
  const html = fs.readFileSync(path.join(__dirname, src), 'utf8');
  fs.writeFileSync(path.join(out, dst), html);
  console.log('dist/' + dst, html.length, 'bytes');
}
