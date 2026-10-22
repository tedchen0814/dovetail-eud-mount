// 把本資料夾的網頁正本複製到 dist/，供 Vercel 部署（只部署 dist/）。
const fs = require('fs');
const path = require('path');
const out = path.join(__dirname, 'dist');
fs.mkdirSync(out, { recursive: true });
const pages = [
  ['首頁總覽.html', 'index.html'],
  ['中央軌道提案動畫.html', 'rail.html'],
  ['中央軌道_3D.html', 'rail-3d.html'],
  ['邊緣卡合提案動畫.html', 'edge.html'],
  ['邊緣卡合_3D.html', 'edge-3d.html']
];
for (const [src, dst] of pages) {
  const html = fs.readFileSync(path.join(__dirname, src), 'utf8');
  fs.writeFileSync(path.join(out, dst), html);
  console.log('dist/' + dst, html.length, 'bytes');
}

// 舊網址轉到新頁面（保留 #提案 錨點），避免舊連結 404
const redirects = [
  ['combo-a-3d.html', 'rail-3d.html', '#ca'],
  ['edge-lock-3d.html', 'edge-3d.html', '']
];
for (const [from, to, defHash] of redirects) {
  const html = `<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>頁面已搬移</title>
<meta http-equiv="refresh" content="0; url=${to}${defHash}">
<script>location.replace("${to}" + (location.hash || "${defHash}"));</script>
<style>body { margin: 0; padding: 40px 16px; font-family: system-ui, sans-serif; background: #ECEEE9; color: #1E2523; }
@media (prefers-color-scheme: dark) { body { background: #141816; color: #E4E9E5; } a { color: #F07A42; } }</style>
</head>
<body><p>這一頁已搬到 <a href="${to}${defHash}">${to}</a>。</p></body>
</html>
`;
  fs.writeFileSync(path.join(out, from), html);
  console.log('dist/' + from, '→', to);
}
