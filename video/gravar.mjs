// Grava a landing quadro a quadro: tempo e rolagem controlados, sem depender do relógio real.
// Uso: com a página servida (python3 -m http.server 8000), rode `npm run gravar`.
import { chromium } from 'playwright';
import fs from 'fs';

const URL_PAGINA = process.env.URL_PAGINA || 'http://localhost:8000/index.html';
const FPS = 30, OUT = new URL('./frames', import.meta.url).pathname;
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on('pageerror', e => console.log('pageerror', e.message));
await page.goto(URL_PAGINA + '?rec=1');
await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });
const A = await page.evaluate(() => window.__anchors());

// roteiro (segundo, scrollY): pausas são pontos repetidos
const K = [
  [0, 0], [3.8, 0],
  [5.6, A.notas],
  [12.8, A.notasFim],
  [14.4, A.tiles + 60],
  [17.6, A.tilesFim],
  [18.4, A.tilesFim],
  [19.8, A.col],
  [25.4, A.colFim],
  [27.2, A.max], [30, A.max],
];
// interpolação monotônica (Fritsch–Carlson): velocidade contínua, sem passar do alvo
const xs = K.map(k => k[0]), ys = K.map(k => k[1]), n = K.length;
const h = [], d = [];
for (let i = 0; i < n - 1; i++) { h[i] = xs[i + 1] - xs[i]; d[i] = (ys[i + 1] - ys[i]) / h[i]; }
const m = new Array(n).fill(0);
for (let i = 1; i < n - 1; i++) {
  if (d[i - 1] * d[i] > 0) { const w1 = 2 * h[i] + h[i - 1], w2 = h[i] + 2 * h[i - 1]; m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]); }
}
function scrollAt(t) {
  if (t >= xs[n - 1]) return ys[n - 1];
  let i = 0; while (t > xs[i + 1]) i++;
  const s = (t - xs[i]) / h[i], s2 = s * s, s3 = s2 * s;
  return (2 * s3 - 3 * s2 + 1) * ys[i] + (s3 - 2 * s2 + s) * h[i] * m[i] + (-2 * s3 + 3 * s2) * ys[i + 1] + (s3 - s2) * h[i] * m[i + 1];
}

const N = Math.round(xs[n - 1] * FPS);
const t0 = Date.now();
for (let f = 0; f < N; f++) {
  const t = f / FPS, y = Math.round(scrollAt(t));
  await page.evaluate(([t, y]) => window.__frame(t, y), [t, y]);
  await page.screenshot({ path: `${OUT}/${String(f).padStart(4, '0')}.png` });
  if (f % 150 === 0) console.log(f, '/', N, Math.round((Date.now() - t0) / 1000) + 's');
}
console.log('ok', N, 'quadros', Math.round((Date.now() - t0) / 1000) + 's');
await browser.close();
