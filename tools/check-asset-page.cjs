const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const server=http.createServer((req,res)=>{
  const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));
  if(!file.startsWith(root+path.sep))return res.writeHead(403).end();
  fs.readFile(file,(error,data)=>{
    if(error)return res.writeHead(404).end();
    res.setHeader('Content-Type',({'.html':'text/html','.css':'text/css','.js':'text/javascript','.png':'image/png','.webp':'image/webp','.woff2':'font/woff2'})[path.extname(file)]||'application/octet-stream');res.end(data);
  });
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({channel:'msedge',headless:true});
  try{
    const page=await browser.newPage({reducedMotion:'reduce'}),errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    await page.route('http://localhost:3001/**',route=>route.fulfill({status:503,json:{error:{message:'Test backend unavailable'}}}));
    const base='http://127.0.0.1:'+server.address().port;
    const output=path.join(root,'artifacts','asset-refresh');fs.mkdirSync(output,{recursive:true});
    async function layout(label){
      const result=await page.evaluate(async()=>{
        await document.fonts.ready;
        for(const image of document.images){image.loading='eager';await image.decode().catch(()=>{});}
        return {overflow:document.documentElement.scrollWidth>innerWidth+1,background:getComputedStyle(document.body).backgroundColor,
          broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),
          missingIcons:[...document.querySelectorAll('use')].map(i=>i.getAttribute('href')).filter(h=>h&&h.startsWith('#')&&!document.querySelector(h)),
          footer:document.querySelectorAll('footer').length};
      });
      assert(!result.overflow,label+' horizontal overflow');assert.equal(result.background,'rgb(5, 5, 5)');assert.deepEqual(result.broken,[]);assert.deepEqual(result.missingIcons,[]);assert.equal(result.footer,0);
    }
    for(const width of [320,390,768,1280]){
      await page.setViewportSize({width,height:844});await page.goto(base+'/asset.html?a=%24Saka');
      await layout('Saka '+width);assert.equal(await page.locator('#assetName').innerText(),'Bukayo Saka');
      assert((await page.locator('#assetHolding').innerText()).includes('10,000 shares held'));
      const dock=await page.locator('.asset-trade-actions').boundingBox();assert(dock.x>=0&&dock.x+dock.width<=width+1);
      await page.locator('#assetDepth summary').click();await layout('Depth '+width);
      await page.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));
      const clearance=await page.evaluate(()=>{
        const details=document.querySelector('.asset-details').getBoundingClientRect(),dock=document.querySelector('.asset-trade-actions');
        return getComputedStyle(dock).position!=='fixed'||details.bottom<=dock.getBoundingClientRect().top;
      });assert(clearance,'Trading actions obscure final section');
      const header=await page.locator('.nav-island.topbar').evaluate(el=>({position:getComputedStyle(el).position,background:getComputedStyle(el,'::before').backgroundColor}));
      assert.equal(header.position,'fixed');assert.equal(header.background,'rgb(5, 5, 5)');
      await page.evaluate(()=>window.scrollTo(0,0));
      if(width===390||width===1280)await page.screenshot({path:path.join(output,'asset-'+width+'.png'),fullPage:true});
      await page.locator('#assetSwitch').click();assert(await page.locator('#assetSearch').evaluate(el=>document.activeElement===el));
      await layout('Picker '+width);
      if(width===390)await page.screenshot({path:path.join(output,'picker-390.png')});
      await page.locator('#assetSearch').fill('Arsenal');assert.equal(await page.locator('.asset-search-row').count(),3);
      await page.locator('#assetSearch').fill('not-a-player');assert.equal(await page.locator('.asset-search-row').count(),0);assert((await page.locator('#assetSearchStatus').innerText()).includes('No matches'));
      await page.keyboard.press('Escape');assert(!(await page.locator('#assetPicker').isVisible()));assert(await page.locator('#assetSwitch').evaluate(el=>document.activeElement===el));
      console.log(width+'px: layout, portraits, market depth, fixed header, actions and search passed');
    }
    await page.setViewportSize({width:390,height:844});
    await page.locator('#assetFavorite').click();assert.equal(await page.locator('#assetFavorite').getAttribute('aria-pressed'),'true');
    await page.reload();assert.equal(await page.locator('#assetFavorite').getAttribute('aria-pressed'),'true');
    await page.locator('#assetFavorite').click();assert.equal(await page.locator('#assetFavorite').getAttribute('aria-pressed'),'false');
    const firstChart=await page.locator('#assetChart').innerHTML();await page.locator('[data-period="1M"]').click();
    assert.notEqual(await page.locator('#assetChart').innerHTML(),firstChart);assert.equal(await page.locator('[data-period="1M"]').getAttribute('aria-pressed'),'true');
    await page.locator('#assetChartType').click();assert.equal(await page.locator('#assetChartType').getAttribute('aria-pressed'),'true');assert(await page.locator('#assetChart rect').count()>20);
    await page.locator('#assetChartType').click();assert.equal(await page.locator('#assetChart rect').count(),0);
    await page.locator('#assetBuy').click();assert(new URL(page.url()).searchParams.get('a')==='$Saka');assert(new URL(page.url()).searchParams.get('side')==='buy');
    await page.goBack();await page.locator('#assetSell').click();assert(new URL(page.url()).searchParams.get('side')==='sell');
    await page.goto(base+'/asset.html?a=%24Mbappe');await layout('Unheld player');assert(await page.locator('#assetSell').isHidden());assert((await page.locator('#assetHolding').innerText()).includes('Your first share'));
    await page.screenshot({path:path.join(output,'unheld-390.png'),fullPage:true});
    await page.locator('#assetSwitch').click();await page.locator('#assetSearch').fill('Arteta');await page.locator('.asset-search-row').click();
    assert.equal(await page.locator('#assetName').innerText(),'Mikel Arteta');assert.equal(await page.locator('#assetRole').innerText(),'Coach');await layout('Coach');
    for(const symbol of ['unknown','%E0%A4%A']){await page.goto(base+'/asset.html?a='+symbol);assert(await page.locator('#assetMissing').isVisible());assert(await page.locator('#assetContent').isHidden());await layout('Missing asset');}
    assert.deepEqual(errors,[]);console.log('Watchlist persistence, chart controls, buy/sell links, unheld shares, coach search and invalid shares passed.');
  }finally{await browser.close();server.close();}
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
