// 把本資料夾的動畫網頁正本複製成 dist/index.html，供 Vercel 部署（只部署 dist/）。
const fs = require('fs');
const path = require('path');
const out = path.join(__dirname, 'dist');
fs.mkdirSync(out, { recursive: true });
const html = fs.readFileSync(path.join(__dirname, '鳩尾槽提案動畫.html'), 'utf8');
fs.writeFileSync(path.join(out, 'index.html'), html);
console.log('dist/index.html', html.length, 'bytes');
