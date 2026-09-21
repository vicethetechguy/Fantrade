const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const server=http.createServer((req,res)=>{
  const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));if(!file.startsWith(root+path.sep))return res.writeHead(403).end();
  fs.readFile(file,(error,data)=>{if(error)return res.writeHead(404).end();res.setHeader('Content-Type',({'.html':'text/html','.css':'text/css','.js':'text/javascript','.png':'image/png','.webp':'image/webp','.woff2':'font/woff2'})[path.extname(file)]||'application/octet-stream');res.end(data);});
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const browser=await chromium.launch({channel:'msedge',headless:true});
  try{
    const page=await browser.newPage({reducedMotion:'reduce'}),errors=[];page.on('pageerror',error=>errors.push(error.message));
    await page.route('http://localhost:3001/**',route=>route.fulfill({status:503,json:{error:{message:'Test backend unavailable'}}}));
    const base='http://127.0.0.1:'+server.address().port,output=path.join(root,'artifacts','community-refresh');fs.mkdirSync(output,{recursive:true});
    async function layout(label){const result=await page.evaluate(async()=>{
      await document.fonts.ready;for(const image of document.images){image.loading='eager';await image.decode().catch(()=>{});}
      return {overflow:document.documentElement.scrollWidth>innerWidth+1,background:getComputedStyle(document.body).backgroundColor,footer:!!document.querySelector('footer'),
        broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),missingIcons:[...document.querySelectorAll('use')].map(i=>i.getAttribute('href')).filter(h=>h&&h.startsWith('#')&&!document.querySelector(h)),
        clipped:[...document.querySelectorAll('.secondary-page input,.portfolio-row,.formation-row,.match-row,.division-tier')].filter(e=>e.getClientRects().length&&!e.closest('[hidden]')).filter(e=>{const r=e.getBoundingClientRect();return r.left<0||r.right>innerWidth+1;}).map(e=>e.className||e.id)};
    });assert(!result.overflow,label+' overflow');assert.equal(result.background,'rgb(5, 5, 5)');assert(!result.footer);assert.deepEqual(result.broken,[],label+' artwork');assert.deepEqual(result.missingIcons,[]);assert.deepEqual(result.clipped,[],label+' clipping');}
    for(const width of [320,390,768,1280]){
      await page.setViewportSize({width,height:900});
      for(const name of ['portfolio','clubs','club-builder','liveboard','divisions']){
        await page.goto(base+'/'+name+'.html');await layout(name+' '+width);
        if(name==='portfolio')assert(await page.locator('#pfNet').evaluate(e=>parseFloat(getComputedStyle(e).fontSize)>=32));
        if(name==='club-builder')for(const shape of ['3-5-2','4-4-2','4-2-3-1','4-3-3']){await page.locator('[data-shape="'+shape+'"]').click();assert.equal(await page.locator('#builderPitch .formation-row .formation-player').count(),11);await layout(shape+' '+width);}
        if(width===390||width===1280)await page.screenshot({path:path.join(output,name+'-'+width+'.png'),fullPage:true});
        await page.evaluate(()=>window.scrollTo(0,300));const header=await page.locator('.nav-island.topbar').evaluate(e=>({position:getComputedStyle(e).position,bg:getComputedStyle(e,'::before').backgroundColor}));assert.equal(header.position,'fixed');assert.equal(header.bg,'rgb(5, 5, 5)');
      }
      console.log(width+'px: five destinations, four formations, artwork, header and layout passed');
    }
    await page.setViewportSize({width:390,height:844});await page.goto(base+'/portfolio.html');
    assert.equal(await page.locator('.portfolio-row').count(),4);assert.equal(await page.locator('#pfNet').innerText(),'1,050,450');
    await page.locator('[data-f="coach"]').click();assert.equal(await page.locator('.portfolio-row').count(),1);
    await page.locator('[data-f="all"]').click();await page.locator('#pfSearch').fill('Saka');assert.equal(await page.locator('.portfolio-row').count(),1);
    await page.locator('.portfolio-player').click();assert.equal(new URL(page.url()).searchParams.get('a'),'$Saka');await page.goBack();
    await page.locator('#pfSearch').fill('no-result');assert(await page.locator('.quiet-empty').isVisible());await page.locator('#pfSearch').fill('');
    await page.locator('[data-view="activity"]').click();assert(await page.locator('#pfActivityView').isVisible());assert(await page.locator('#pfHoldingsView').isHidden());await layout('Portfolio activity');
    const downloadPromise=page.waitForEvent('download');await page.locator('#pfExport').click();const download=await downloadPromise;assert.equal(download.suggestedFilename(),'fantrade-ledger.csv');
    const csv=fs.readFileSync(await download.path(),'utf8');assert(csv.includes('"Holding","Shares","Average cost"'));assert(csv.includes('$Saka'));assert(csv.includes('BUY'));
    await page.goto(base+'/clubs.html');await page.locator('#clubRail button').nth(1).click();assert.equal(await page.locator('#clName').innerText(),'North Bank XI');assert.equal(await page.locator('#clubShape').innerText(),'4-2-3-1');assert((await page.locator('.formation-coach').innerText()).includes('$Pep'));
    await page.goto(base+'/divisions.html');assert((await page.locator('.division-tier.current').innerText()).includes('Contender'));assert.equal(await page.locator('.tier-current:visible').count(),1);
    await page.goto(base+'/club-builder.html?new=1');assert.equal(await page.locator('#clubNameInput').inputValue(),'');assert((await page.locator('.formation-coach').innerText()).includes('$Arteta'));
    await page.locator('#clubNameInput').fill('Northern Lights');await page.locator('#clubStadiumInput').fill('Aurora Park');await page.locator('[data-shape="3-5-2"]').click();await page.locator('[data-colour="Violet"]').click();
    assert.equal(await page.locator('#previewName').innerText(),'Northern Lights');assert.equal(await page.locator('#previewShape').innerText(),'3-5-2');await page.locator('#saveClubBtn').click();assert((await page.locator('#clubSaveStatus').innerText()).includes('Saved'));
    await page.reload();assert.equal(await page.locator('#clubNameInput').inputValue(),'Northern Lights');assert.equal(await page.locator('[data-colour="Violet"]').getAttribute('aria-pressed'),'true');assert.equal(await page.locator('[data-shape="3-5-2"]').getAttribute('aria-pressed'),'true');
    await page.locator('#clubNameInput').fill('Northern Stars');await page.locator('#saveClubBtn').click();await page.goto(base+'/clubs.html');assert.equal(await page.locator('#clName').innerText(),'Northern Stars');assert.equal(await page.locator('#clubRail button').count(),3);
    await page.goto(base+'/club-builder.html?new=1');await page.locator('#clubNameInput').fill('Northern Stars');await page.locator('#saveClubBtn').click();assert((await page.locator('#clubSaveStatus').innerText()).includes('already have'));
    await page.goto(base+'/liveboard.html');assert.equal(await page.locator('.match-row:visible').count(),9);
    await page.locator('[data-filter="live"]').click();assert.equal(await page.locator('.match-row:visible').count(),4);
    await page.locator('[data-filter="following"]').click();assert.equal(await page.locator('.match-row:visible').count(),1);
    await page.locator('.match-row:visible .match-follow').click();assert(await page.locator('#boardEmpty').isVisible());await page.locator('#boardReset').click();assert.equal(await page.locator('.match-row:visible').count(),9);
    await page.locator('#boardSearch').fill('Bayern');assert.equal(await page.locator('.match-row:visible').count(),1);await page.locator('.match-row:visible .match-follow').click();await page.reload();await page.locator('[data-filter="following"]').click();assert.equal(await page.locator('.match-row:visible').count(),1);assert((await page.locator('.match-row:visible').innerText()).includes('Bayern'));
    await page.locator('#boardSearch').fill('unknown-team');assert(await page.locator('#boardEmpty').isVisible());await page.locator('#boardReset').click();
    await page.goto(base+'/portfolio.html');await page.evaluate(()=>{const s=JSON.parse(localStorage.getItem('fantrade_v1_state'));s.holdings={};s.transactions=[];s.wallet.balance=0;s.wallet.locked=0;localStorage.setItem('fantrade_v1_state',JSON.stringify(s));});await page.reload();assert.equal(await page.locator('#pfNet').innerText(),'0');assert((await page.locator('#pfRows').innerText()).includes('Your portfolio starts here'));await page.locator('[data-view="activity"]').click();assert((await page.locator('#pfLedger').innerText()).includes('No activity yet'));await layout('Empty portfolio');
    assert.deepEqual(errors,[]);console.log('Portfolio balances, filters, deep links, CSV, empty states; club switching, create/edit persistence, duplicate validation; division state and fixture filters/follow persistence passed.');
  }finally{await browser.close();server.close();}
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
