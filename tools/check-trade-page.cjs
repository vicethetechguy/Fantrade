const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const server=http.createServer((req,res)=>{
  const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));
  if(!file.startsWith(root+path.sep))return res.writeHead(403).end();
  fs.readFile(file,(error,data)=>{if(error)return res.writeHead(404).end();res.setHeader('Content-Type',({'.html':'text/html','.css':'text/css','.js':'text/javascript','.png':'image/png','.webp':'image/webp','.woff2':'font/woff2'})[path.extname(file)]||'application/octet-stream');res.end(data);});
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({channel:'msedge',headless:true});
  try{
    const page=await browser.newPage({reducedMotion:'reduce'}),errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    await page.route('http://localhost:3001/**',route=>route.fulfill({status:503,json:{error:{message:'Test backend unavailable'}}}));
    const base='http://127.0.0.1:'+server.address().port,output=path.join(root,'artifacts','trade-refresh');fs.mkdirSync(output,{recursive:true});
    async function layout(label){
      const result=await page.evaluate(async()=>{await document.fonts.ready;for(const i of document.images){i.loading='eager';await i.decode().catch(()=>{});}return {
        overflow:document.documentElement.scrollWidth>innerWidth+1,background:getComputedStyle(document.body).backgroundColor,
        broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),
        missingIcons:[...document.querySelectorAll('use')].map(i=>i.getAttribute('href')).filter(h=>h&&h.startsWith('#')&&!document.querySelector(h))};});
      assert(!result.overflow,label+' overflow');assert.equal(result.background,'rgb(5, 5, 5)');assert.deepEqual(result.broken,[]);assert.deepEqual(result.missingIcons,[]);
    }
    for(const width of [320,390,768,1280]){
      await page.setViewportSize({width,height:900});await page.goto(base+'/trade.html?a=%24Saka');await layout('Buy '+width);
      assert.equal(await page.locator('#tQty').inputValue(),'');assert.equal(await page.locator('#tradeDepth').evaluate(el=>el.open),width>900);
      if(width===390||width===1280)await page.screenshot({path:path.join(output,'trade-'+width+'.png'),fullPage:true});
      for(const mode of ['sell','swap','buy']){await page.locator('#tMode [data-m="'+mode+'"]').click();await layout(mode+' '+width);}
      if(width<=900)await page.locator('#tradeDepth summary').click();await layout('Market depth '+width);
      await page.locator('#tBids .b2row').first().focus();await page.keyboard.press('Enter');assert.equal(await page.locator('#tLimit').inputValue(),await page.locator('#tBids .b2row').first().getAttribute('data-px'));
      for(const ledger of ['fills','assets','open']){await page.locator('#tLedgerTabs [data-l="'+ledger+'"]').click();await layout('Ledger '+ledger+' '+width);}
      console.log(width+'px: buy, sell, swap, depth keyboard access and all ledger views passed');
    }
    await page.setViewportSize({width:390,height:844});await page.goto(base+'/trade.html?a=%24Haaland&side=sell');
    assert.equal(await page.locator('#tMode [data-m="sell"]').getAttribute('aria-pressed'),'true');assert.equal(await page.locator('#tPlayerName').innerText(),'Erling Haaland');
    assert(await page.locator('#tDelta').evaluate(el=>el.classList.contains('down')));
    await page.locator('#tType').selectOption('market');assert(await page.locator('#tLimitWrap').isHidden());assert((await page.locator('#tradeTypeHelp').innerText()).includes('final price may vary'));
    await page.locator('#tQty').fill('10');assert.notEqual(await page.locator('#tTot').innerText(),'0 $FTR');
    await page.locator('#tType').selectOption('limit');assert(await page.locator('#tLimitWrap').isVisible());
    await page.locator('#tGo').click();assert((await page.locator('#tcOpen').innerText()).includes('3'));
    await page.locator('#tLedger [data-cancel]').first().click();assert((await page.locator('#tcOpen').innerText()).includes('2'));
    await page.locator('#tQty').fill('');await page.locator('#tGo').click();assert((await page.locator('#ftToastContainer').innerText()).includes('Enter how many shares'));assert((await page.locator('#tcOpen').innerText()).includes('2'));
    await page.locator('#tChart').click();assert.equal(new URL(page.url()).searchParams.get('a'),'$Haaland');assert.equal(await page.locator('#assetName').innerText(),'Erling Haaland');
    assert.deepEqual(errors,[]);console.log('Sell deep links, player context, order type help, preview order/cancel and empty quantity validation passed.');
  }finally{await browser.close();server.close();}
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
