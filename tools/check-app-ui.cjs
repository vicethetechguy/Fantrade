const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const pages = [
  'dashboard.html','exchange.html','asset.html','trade.html','clubs.html','club-builder.html',
  'fanplay.html','liveboard.html','ftr.html','send.html','receive.html','swap.html','buy.html',
  'activity.html','wallet.html','withdraw.html','leaderboard.html','divisions.html','notifications.html',
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
    response.setHeader('Content-Type', ({ '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.ttf':'font/ttf' })[path.extname(file)] || 'application/octet-stream');
    response.end(data);
  });
});

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  const page = await browser.newPage();
  await page.addInitScript(() => {
    try {
      if (!localStorage.getItem('fantrade_v1_state')) localStorage.setItem('fantrade_v1_state', JSON.stringify({ auth: { signedIn: true, user: { email: 'demo@fantrade.app' } } }));
    } catch (e) {}
  });
  const errors = [];
  page.on('pageerror', error => { console.log('PAGE ERROR ON ' + page.url() + ': ' + error.message); errors.push(error.message); });
  await page.route('https://fonts.googleapis.com/**', route => route.abort());
  await page.route('https://fonts.gstatic.com/**', route => route.abort());
  const output = path.join(root, 'artifacts', 'app-reference');
  fs.mkdirSync(output, { recursive: true });
  try {
    for (const width of [320, 390, 768, 1280]) {
      await page.setViewportSize({ width, height: width >= 1000 ? 900 : 844 });
      for (const name of pages) {
        await page.goto(`${base}/${name}`, { waitUntil: 'domcontentloaded' });
        await page.evaluate(() => document.fonts.ready);
        await page.waitForTimeout(60);
        const result = await page.evaluate(() => {
          const dock = document.querySelector('.taskbar');
          const rect = dock && dock.getBoundingClientRect();
          return {
            overflow: document.documentElement.scrollWidth > innerWidth + 1,
            brokenImages: [...document.images].filter(image => image.complete && image.naturalWidth === 0).map(image => image.getAttribute('src')),
            dockLinks: dock ? dock.querySelectorAll('a').length : 0,
            dockInside: !rect || (rect.left >= -1 && rect.right <= innerWidth + 1),
            bodyFont: getComputedStyle(document.body).fontFamily,
            headingWeights: [...document.querySelectorAll('h1,h2,h3,h4')].map(el => getComputedStyle(el).fontWeight),
            brandFontsLoaded: document.fonts.check('400 16px Montserrat') && document.fonts.check('800 24px Montserrat')
          };
        });
        const fieldFocus = await page.evaluate(() => {
          const fields = [...document.querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="range"]),textarea')]
            .filter(el => el.getBoundingClientRect().width > 0 && !el.disabled);
          const outlined = [];
          fields.forEach(el => {
            el.focus();
            const style = getComputedStyle(el);
            if (style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) > 0) outlined.push(el.id || el.name);
            if (style.boxShadow !== 'none') outlined.push((el.id || el.name) + ':shadow');
            el.blur();
          });
          scrollTo(0, 0);
          return outlined;
        });
        assert.deepEqual(fieldFocus, [], `${name} shows a focus border on typing fields at ${width}px`);
        assert(!result.overflow, `${name} overflows at ${width}px`);
        assert(result.bodyFont.startsWith('Montserrat') && result.brandFontsLoaded, `${name} must load local Montserrat fonts`);
        assert(result.headingWeights.every(weight => weight === '800'), `${name} headings must use ExtraBold`);
        assert.deepEqual(result.brokenImages, [], `${name} has broken images at ${width}px`);
        assert.equal(result.dockLinks, ['asset.html', 'onboarding.html'].includes(name) ? 0 : 5, `${name} has an unexpected primary dock`);
        assert(result.dockInside, `${name} dock leaves the viewport at ${width}px`);
        if (shots.has(name) && (width === 390 || width === 1280)) {
          await page.waitForTimeout(650);
          await page.screenshot({ path: path.join(output, `${name.replace('.html','')}-${width}.png`), fullPage: false });
        }
      }
      console.log(`App UI pass: ${width}px across ${pages.length} pages`);
    }
    // Verify the journeys changed by the UI audit, using this isolated preview session.
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`${base}/exchange.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    assert.equal(await page.locator('.market-filters').evaluate(el => el.open), false, 'Mobile filters should start collapsed');
    await page.locator('.market-filters > summary').click();
    await page.locator('[data-sub="holdings"]').click();
    assert.equal(await page.locator('[data-sub="holdings"]').getAttribute('aria-pressed'), 'true');
    await page.setViewportSize({ width: 1280, height: 900 });
    assert.equal(await page.locator('.market-filters').evaluate(el => el.open), true, 'Desktop filters must remain visible');

    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`${base}/settings-alerts.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(150);
    await page.locator('.settings-switcher > summary').click();
    assert(await page.locator('.settings-nav a[href="settings-security.html"]').isVisible(), 'Settings destinations must be discoverable');
    assert.equal(await page.locator('button.tgl:not([aria-label])').count(), 0, 'Every settings toggle needs a name');
    await page.locator('.settings-switcher > summary').focus();
    await page.keyboard.press('Shift+Tab');
    await page.keyboard.press('Tab');
    assert.equal(await page.locator('.settings-switcher > summary').evaluate(el => getComputedStyle(el).outlineStyle), 'solid', 'Keyboard focus must be visible');

    await page.evaluate(() => localStorage.setItem('ft_market_v1', JSON.stringify({ ftr_usd: 5 })));
    await page.goto(`${base}/onboarding.html`, { waitUntil: 'domcontentloaded' });
    const starterPrice = Number(await page.locator('#obPicks [data-sym="FSAKA"]').getAttribute('data-px'));
    assert(Math.abs(starterPrice - .00252208) < .00002, 'Onboarding must use the market $FTR quote instead of its old fixed price');
    await page.goto(`${base}/exchange.html`, { waitUntil: 'domcontentloaded' });
    const exchangePrice = Number((await page.locator('a.kc-row[href*="FSAKA"] .kc-price-main').innerText()).replace(/,/g, ''));
    assert(Math.abs(exchangePrice - starterPrice) < .0001, 'Onboarding and Exchange prices must agree');

    await page.goto(`${base}/wallet.html`, { waitUntil: 'domcontentloaded' });
    assert(await page.locator('#walAvailable').isVisible(), 'Spendable tokens must be distinct from portfolio value');
    assert(await page.locator('#walCoachAmt').isVisible(), 'Coach shares must be identifiable in allocation');
    await page.locator('#walEyeBtn').click();
    assert((await page.locator('#walAvailable').innerText()).includes('•'), 'Balance privacy must also cover available tokens');

    await page.evaluate(() => {
      const state = JSON.parse(localStorage.getItem('fantrade_v1_state'));
      state.holdings = {
        '$Mbappe': { n: 'Kylian Mbappé', shares: 801, avg: 11, p: 11, c: false },
        FARTETA: { n: 'Mikel Arteta', shares: 24, avg: 1, p: 1, c: true }
      };
      localStorage.setItem('fantrade_v1_state', JSON.stringify(state));
    });
    await page.goto(`${base}/wallet.html`, { waitUntil: 'domcontentloaded' });
    await page.locator('#walAssets a[href*="FKM7"]').click();
    assert.equal(await page.locator('#assetName').innerText(), 'Kylian Mbappé', 'Wallet legacy shares must open the correct player');
    assert(await page.locator('#assetContent').isVisible(), 'Player detail UI must be present');
    assert((await page.locator('#assetHolding').innerText()).includes('801 shares held'), 'Legacy holding quantity must appear in player details');
    for (const [symbol, name] of [['FMBAPPE','Kylian Mbappé'], ['$bellingham','Jude Bellingham'], ['FARTETA','Mikel Arteta'], ['$Guardiola','Pep Guardiola']]) {
      await page.goto(`${base}/asset.html?a=${encodeURIComponent(symbol)}`, { waitUntil: 'domcontentloaded' });
      assert.equal(await page.locator('#assetName').innerText(), name, `${symbol} must resolve to the proper share`);
    }
    console.log('Wallet detail links and legacy player/coach symbols pass');

    await page.evaluate(() => {
      const state = JSON.parse(localStorage.getItem('fantrade_v1_state'));
      state.holdings = {};
      state.fanplay = { activeEntries: [], history: [] };
      localStorage.setItem('fantrade_v1_state', JSON.stringify(state));
    });
    await page.goto(`${base}/fanplay.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    assert.equal(await page.locator('#stepAssetGrid .fp-asset-card').count(), 0, 'An empty portfolio must never be replaced with sample owned players');
    assert(await page.locator('#stepAssetGrid a[href="exchange.html"]').isVisible(), 'Empty portfolio needs a next action');
    assert(await page.locator('#fpProgressText').isVisible(), 'Mobile FanPlay progress must be readable');
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
    const actionClear = await page.locator('#stepBox1 .fp-nav-btns').evaluate(el => {
      const action = el.getBoundingClientRect(), dock = document.querySelector('.taskbar').getBoundingClientRect();
      return action.bottom <= dock.top;
    });
    assert(actionClear, 'FanPlay next action must stay above the taskbar');
    console.log('UI journeys pass: filters, settings, focus, prices, wallet privacy, owned shares and taskbar clearance');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`${base}/notifications.html`, { waitUntil: 'load' });
    await page.waitForTimeout(300);
    await page.evaluate(() => scrollTo(0, 420));
    await page.waitForTimeout(250);
    const notificationLayout = await page.evaluate(() => {
      const title = document.querySelector('.notifications-page > .kc-p-topbar') || document.querySelector('.inbox-sticky');
      const feed = document.querySelector('.notification-feed > .core') || document.querySelector('#ntFeed');
      if (!title || !feed) return { ok: true };
      const titleStyle = getComputedStyle(title);
      const feedStyle = getComputedStyle(feed);
      return {
        ok: true,
        titleTop: Math.round(title.getBoundingClientRect().top),
        titlePosition: titleStyle.position,
        titleBackground: titleStyle.backgroundColor,
        feedBorder: feedStyle.borderTopWidth,
        feedBackground: feedStyle.backgroundColor
      };
    });
    if (notificationLayout.titlePosition) {
      assert(notificationLayout.titlePosition === 'fixed' || notificationLayout.titlePosition === 'sticky', 'Notification title is not fixed/sticky while scrolling');
      assert(notificationLayout.titleTop >= 0, 'Notification content scrolls over the app header');
    }
    await page.screenshot({ path: path.join(output, 'notifications-scroll-390.png'), fullPage: false });
    assert.deepEqual(errors, [], `Browser errors: ${errors.join('; ')}`);
  } finally {
    await browser.close();
    server.close();
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
