const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const pages = [
  'dashboard.html','exchange.html','asset.html','trade.html','clubs.html','club-builder.html',
  'fanplay.html','liveboard.html','ftr.html','send.html','receive.html','swap.html','buy.html',
  'activity.html','portfolio.html','leaderboard.html','divisions.html','notifications.html',
  'account.html','settings.html','settings-profile.html','settings-club.html',
  'settings-security.html','settings-alerts.html','settings-wallet.html','settings-play.html',
  'settings-data.html','onboarding.html'
];
const shots = new Set(['dashboard.html','exchange.html','clubs.html','fanplay.html','leaderboard.html','notifications.html','account.html']);
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
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.route('https://fonts.googleapis.com/**', route => route.abort());
  await page.route('https://fonts.gstatic.com/**', route => route.abort());
  const output = path.join(root, 'artifacts', 'app-reference');
  fs.mkdirSync(output, { recursive: true });
  try {
    for (const width of [320, 390, 768, 1280]) {
      await page.setViewportSize({ width, height: width >= 1000 ? 900 : 844 });
      for (const name of pages) {
        await page.goto(`${base}/${name}`, { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(60);
        const result = await page.evaluate(() => {
          const dock = document.querySelector('.taskbar');
          const rect = dock && dock.getBoundingClientRect();
          return {
            overflow: document.documentElement.scrollWidth > innerWidth + 1,
            brokenImages: [...document.images].filter(image => image.complete && image.naturalWidth === 0).map(image => image.getAttribute('src')),
            dockLinks: dock ? dock.querySelectorAll('a').length : 0,
            dockInside: !rect || (rect.left >= -1 && rect.right <= innerWidth + 1)
          };
        });
        assert(!result.overflow, `${name} overflows at ${width}px`);
        assert.deepEqual(result.brokenImages, [], `${name} has broken images at ${width}px`);
        assert.equal(result.dockLinks, name === 'asset.html' ? 0 : 5, `${name} has an unexpected primary dock`);
        assert(result.dockInside, `${name} dock leaves the viewport at ${width}px`);
        if (shots.has(name) && (width === 390 || width === 1280)) {
          await page.waitForTimeout(650);
          await page.screenshot({ path: path.join(output, `${name.replace('.html','')}-${width}.png`), fullPage: false });
        }
      }
      console.log(`App UI pass: ${width}px across ${pages.length} pages`);
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`${base}/notifications.html`, { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => scrollTo(0, 420));
    await page.waitForTimeout(250);
    const notificationLayout = await page.evaluate(() => {
      const title = document.querySelector('.notifications-page > .kc-p-topbar');
      const feed = document.querySelector('.notification-feed > .core');
      const titleStyle = getComputedStyle(title);
      const feedStyle = getComputedStyle(feed);
      return {
        titleTop: Math.round(title.getBoundingClientRect().top),
        titlePosition: titleStyle.position,
        titleBackground: titleStyle.backgroundColor,
        feedBorder: feedStyle.borderTopWidth,
        feedBackground: feedStyle.backgroundColor
      };
    });
    assert.equal(notificationLayout.titlePosition, 'fixed', 'Notification title is not fixed while scrolling');
    assert(notificationLayout.titleTop >= 57, 'Notification content scrolls over the app header');
    assert.equal(notificationLayout.feedBorder, '0px', 'Notification feed still has a card border');
    assert(notificationLayout.feedBackground === 'rgba(0, 0, 0, 0)', 'Notification feed still has a card background');
    await page.screenshot({ path: path.join(output, 'notifications-scroll-390.png'), fullPage: false });
    assert.deepEqual(errors, [], `Browser errors: ${errors.join('; ')}`);
  } finally {
    await browser.close();
    server.close();
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
