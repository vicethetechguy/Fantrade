const { chromium } = require('C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');

const root = path.resolve(__dirname, '..');
const pages = [
  'dashboard.html', 'exchange.html', 'asset.html', 'trade.html', 'clubs.html',
  'club-builder.html', 'fanplay.html', 'liveboard.html', 'ftr.html', 'send.html',
  'receive.html', 'swap.html', 'buy.html', 'activity.html', 'portfolio.html',
  'leaderboard.html', 'divisions.html', 'notifications.html', 'account.html',
  'onboarding.html'
];

const server = http.createServer((request, response) => {
  const file = path.resolve(root, '.' + decodeURIComponent(request.url.split('?')[0]));
  if (!file.startsWith(root + path.sep)) return response.writeHead(403).end();
  fs.readFile(file, (error, data) => {
    if (error) return response.writeHead(404).end();
    response.setHeader('Content-Type', file.endsWith('.html') ? 'text/html' : 'application/octet-stream');
    response.end(data);
  });
});

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const base = `http://127.0.0.1:${server.address().port}`;
  const output = path.join(root, 'artifacts', 'mobile-audit');
  fs.mkdirSync(output, { recursive: true });
  let failed = false;

  for (const width of [320, 390, 430]) {
    await page.setViewportSize({ width, height: 844 });
    for (const name of pages) {
    await page.goto(`${base}/${name}`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(width === 390 ? 900 : 80);
    const result = await page.evaluate(() => {
      const wrapper = document.querySelector('[class*="kc-"][class*="-wrap"], main > .wrap');
      const wr = wrapper && wrapper.getBoundingClientRect();
      const wrapperStyle = wrapper && getComputedStyle(wrapper);
      const first = wrapper && wrapper.firstElementChild && wrapper.firstElementChild.getBoundingClientRect();
      const firstCore = document.querySelector('.bezel > .core');
      const cr = firstCore && firstCore.getBoundingClientRect();
      const firstCoreChild = firstCore && firstCore.firstElementChild && firstCore.firstElementChild.getBoundingClientRect();
      const overflowing = [...document.querySelectorAll('main *')].filter(element => {
        const style = getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return style.position !== 'fixed' && rect.width > 0 && (rect.left < -1 || rect.right > innerWidth + 1);
      }).slice(0, 8).map(element => `${element.tagName.toLowerCase()}.${element.className}`);
      return {
        documentOverflow: document.documentElement.scrollWidth > innerWidth + 1,
        wrapperLeft: wr ? Math.round(wr.left) : null,
        wrapperRight: wr ? Math.round(innerWidth - wr.right) : null,
        wrapperPadding: wrapperStyle ? [wrapperStyle.paddingLeft, wrapperStyle.paddingRight] : null,
        firstChildLeft: first ? Math.round(first.left) : null,
        coreLeft: cr ? Math.round(cr.left) : null,
        coreContentLeft: firstCoreChild ? Math.round(firstCoreChild.left) : null,
        overflowing
      };
    });
    const leftPadding = result.wrapperPadding ? parseFloat(result.wrapperPadding[0]) : 16;
    const rightPadding = result.wrapperPadding ? parseFloat(result.wrapperPadding[1]) : 16;
    if (result.documentOverflow || leftPadding < 12 || rightPadding < 12) failed = true;
    console.log(`${width}px ${name}`, JSON.stringify(result));
    if (width === 390) await page.screenshot({ path: path.join(output, name.replace('.html', '.png')), fullPage: false });
    }
  }

  await browser.close();
  server.close();
  if (failed) process.exitCode = 1;
})().catch(error => {
  console.error(error);
  server.close();
  process.exitCode = 1;
});
