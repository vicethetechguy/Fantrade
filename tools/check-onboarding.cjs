const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs'), path = require('path'), http = require('http'), assert = require('assert');
const root = path.resolve(__dirname, '..');
const server = http.createServer((req, res) => {
  const file = path.resolve(root, '.' + decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(root + path.sep)) return res.writeHead(403).end();
  fs.readFile(file, (error, data) => {
    if (error) return res.writeHead(404).end();
    res.setHeader('Content-Type', ({ '.html': 'text/html', '.js': 'text/javascript', '.webp': 'image/webp', '.png': 'image/png' })[path.extname(file)] || 'application/octet-stream');
    res.end(data);
  });
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  const output = path.join(root, 'artifacts', 'onboarding');
  fs.mkdirSync(output, { recursive: true });
  try {
    for (const width of [320, 390, 768, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 844 }, reducedMotion: 'reduce' });
      await page.route('http://localhost:3001/**', route => route.abort());
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(`http://127.0.0.1:${server.address().port}/onboarding.html`);
      await page.evaluate(() => document.fonts.ready);
      const state = () => page.evaluate(() => JSON.parse(localStorage.getItem('fantrade_v1_state')));
      async function verifyStep(step) {
        assert(await page.locator(`[data-pane="${step}"].on`).isVisible());
        assert(!(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)), `Overflow at ${width}, step ${step}`);
        assert.equal(await page.locator('footer').count(), 0);
        assert.equal(await page.locator('.bezel').count(), 0);
        assert(await page.locator('.nav-min').evaluate(e => e.getBoundingClientRect().top === 0));
        await page.waitForFunction(() => document.querySelectorAll('.ft-toast').length === 0);
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.screenshot({ path: path.join(output, `step-${step + 1}-${width}.png`), fullPage: true });
      }
      await verifyStep(0);
      assert(await page.locator('#obNext').isHidden());
      assert.equal(await page.locator('#obPicks img').evaluateAll(images => images.filter(img => !img.naturalWidth).length), 0);
      await page.locator('[data-sym="$Bruno"]').click();
      await page.locator('#obShares').fill('0');
      await page.locator('#obBuy').click();
      assert(await page.locator('[data-pane="0"].on').isVisible());
      await page.locator('#obShares').fill('9999999');
      await page.locator('#obBuy').click();
      assert(await page.locator('#obBuy').isEnabled());
      await page.locator('[data-s="100"]').click();
      assert.equal(await page.locator('#obTot').innerText(), '3,991 $FTR');
      const beforeBalance = Number((await page.locator('#sumWallet').innerText()).replace(/[^0-9.]/g, ''));
      await page.locator('#obBuy').click();
      await page.locator('[data-pane="1"].on').waitFor();
      const after = await state();
      assert(Math.abs(beforeBalance - after.wallet.balance - 3991) < 0.01, 'Exactly one purchase is charged');
      await verifyStep(1);
      await page.locator('#handle').fill('!');
      await page.locator('#obNext').click();
      assert(await page.locator('#f-handle').evaluate(e => e.classList.contains('bad')));
      await page.locator('#handle').fill('fan_manager');
      await page.locator('#region').selectOption({ label: 'Nigeria' });
      await page.locator('#obNext').click();
      await verifyStep(2);
      await page.locator('#clubName').fill('A');
      await page.locator('#obNext').click();
      assert(await page.locator('#f-clubName').evaluate(e => e.classList.contains('bad')));
      await page.locator('#clubName').fill('Lagos United');
      await page.locator('#obForms button').filter({ hasText: '4-4-2' }).click();
      await page.locator('#obSw [aria-label="Amber"]').click();
      await page.locator('#obBack').click();
      assert.equal(await page.locator('#handle').inputValue(), 'fan_manager');
      await page.locator('#obNext').click();
      assert.equal(await page.locator('#clubName').inputValue(), 'Lagos United');
      await page.locator('#obNext').click();
      await verifyStep(3);
      assert.equal(await page.locator('#sumClub').innerText(), 'Lagos United');
      assert.equal(await page.locator('#sumFormation').innerText(), '4-4-2');
      assert.equal(await page.locator('#sumRegion').innerText(), 'Nigeria');
      assert.equal(await page.locator('#sumAsset').innerText(), '$Bruno');
      await page.locator('#obNext').click();
      await page.waitForURL('**/dashboard.html');
      const done = await state();
      assert(done.auth.onboarded);
      const club = done.clubs.find(club => club.id === done.activeClub);
      assert.equal(club.name, 'Lagos United');
      assert.equal(club.formation, '4-4-2');
      assert.equal(club.colorName, 'Amber');
      assert.deepEqual(errors, []);
      console.log(`${width}px: all 4 steps, purchase, validation, back navigation and saved setup passed.`);
      await page.close();
    }
  } finally { await browser.close(); server.close(); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
