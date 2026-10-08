const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(err,data)=>{if(err)return res.writeHead(404).end();res.setHeader('Content-Type',({'.html':'text/html','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.ttf':'font/ttf'})[path.extname(file)]||'application/octet-stream');res.end(data);});});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const base='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage(),errors=[]; await page.route('**/rest/v1/rpc/ft_market',route=>route.fulfill({json:{ftr_usd:20,max_supply:1000000}})); await page.route('http://localhost:3001/**',route=>route.abort());page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(()=>{if(!localStorage.getItem('fantrade_v1_state'))localStorage.setItem('fantrade_v1_state',JSON.stringify({auth:{signedIn:true},user:{name:'Test Fan',handle:'@testfan',avatar:'assets/players/saka.webp'}}));});
  for(const width of [320,390,768,1280]){
   await page.setViewportSize({width,height:900});await page.goto(base+'/exchange.html');
   assert(await page.locator('#kcCatTabs').evaluate(el=>{const ys=[...el.children].map(b=>b.getBoundingClientRect().top);return Math.max(...ys)-Math.min(...ys)<2;}),'Categories must stay on one line');
   await page.locator('#kcCatTabs [data-cat="coaches"]').click();assert(await page.locator('#kcCatTabs [data-cat="coaches"]').evaluate(el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth;}),'Last category must be reachable');
   assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)),'Exchange must not overflow');
  }
  await page.setViewportSize({width:390,height:900});await page.goto(base+'/asset.html?a=FSAKA#feed');
  assert.equal(await page.locator('#feedMe img').getAttribute('src'),'assets/players/saka.webp');
  await page.locator('#feedText').fill('Great match ');await page.locator('[data-tag="feedText"]').click();
  await page.locator('#feedCompose .feed-mentions button').first().click();
  assert((await page.locator('#feedText').inputValue()).includes('@'),'Selecting a suggestion inserts a tag');
  await page.locator('#feedPost').click();const post=page.locator('.asset-post').first();
  assert.equal(await post.locator('.asset-post-head img').getAttribute('src'),'assets/players/saka.webp');
  assert.equal(await post.locator('.feed-mention').count(),1);
  await post.locator('[data-like]').click();assert.equal(await post.locator('[data-like]').getAttribute('aria-pressed'),'true');
  await post.locator('[data-reply]').click();await post.locator('textarea').fill('Agree @testfan <img src=x onerror=alert(1)>');
  await post.locator('[data-comment-form] button[type="submit"]').click();
  assert.equal(await post.locator('.feed-comment').count(),1);assert.equal(await post.locator('.feed-comment img').count(),1,'Comment text cannot inject an image');
  const id=await post.getAttribute('data-id');await page.reload();const saved=page.locator('.asset-post[data-id="'+id+'"]');
  assert.equal(await saved.locator('[data-like]').getAttribute('aria-pressed'),'true');await saved.locator('[data-reply]').click();
  assert.equal(await saved.locator('.feed-comment').count(),1,'Comments survive refresh');assert((await saved.locator('.feed-comment p').innerText()).includes('<img'));
  await page.goto(base+'/wallet.html'); assert((await page.locator('#walAvailable').innerText()).includes('1,000'),'Preview allocation must be smaller than total supply');
  await page.evaluate(()=>dispatchEvent(new CustomEvent('fantrade:market',{detail:{ftr_usd:5,max_supply:10000000}})));
  await page.goto(base+'/asset.html?a=FSAKA'); const before=await page.locator('#assetPrice').innerText(); await page.evaluate(()=>dispatchEvent(new CustomEvent('fantrade:market',{detail:{ftr_usd:5,max_supply:10000000}}))); await page.waitForFunction(previous=>document.querySelector('#assetPrice').textContent!==previous,before); assert.notEqual(await page.locator('#assetPrice').innerText(),before,'Live quote reprices the share');
  await page.goto(base+'/asset.html?a=FSAKA#feed'); await page.locator('.asset-post[data-id="'+id+'"] [data-reply]').click();
  fs.mkdirSync(path.join(root,'artifacts','feed'),{recursive:true});
  for(const width of [320,390,1280]){await page.setViewportSize({width,height:900});assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)),'Feed comments must fit every screen');await page.screenshot({path:path.join(root,'artifacts','feed','feed-'+width+'.png'),fullPage:false});}
  await page.evaluate(()=>{const s=JSON.parse(localStorage.getItem('fantrade_v1_state'));s.wallet={balance:950000,locked:0};s.demoGrant1M=true;s.previewSupplyV3=false;s.liveWallet=false;localStorage.setItem('fantrade_v1_state',JSON.stringify(s));});
  await page.goto(base+'/wallet.html'); assert((await page.locator('#walAvailable').innerText()).includes('1,000'),'Legacy synthetic allocation is corrected');
  await page.evaluate(()=>{const s=JSON.parse(localStorage.getItem('fantrade_v1_state'));s.wallet={balance:950000,locked:0};s.previewSupplyV3=false;s.liveWallet=true;localStorage.setItem('fantrade_v1_state',JSON.stringify(s));});
  await page.reload(); assert((await page.locator('#walAvailable').innerText()).includes('950,000'),'Real-wallet snapshots must not be reduced');
  await page.goto(base+'/trade.html?a=FBRN&side=buy');await page.locator('#tTypeBtn').click();await page.locator('[data-order-type=market]').click();await page.locator('#tQty').fill('1');const quote=Number((await page.locator('#tTot').innerText()).replace(/[^0-9.]/g,''));assert(quote>0&&quote<1,'Small share quote retains fractional tokens');await page.locator('#tGo').click();const charged=await page.evaluate(()=>JSON.parse(localStorage.getItem('fantrade_v1_state')).transactions[0].total);assert(charged>0&&charged<1,'Small share purchase must not be free');
  assert.deepEqual(errors,[]);console.log('Single-line categories, profile photos, safe mentions, likes/comments persistence and preview/live pricing passed');
 }finally{await browser.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
