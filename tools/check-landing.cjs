const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(err,data)=>{if(err)return res.writeHead(404).end();const ext=path.extname(file);res.setHeader('Content-Type',({'.html':'text/html','.webp':'image/webp','.svg':'image/svg+xml','.woff2':'font/woff2'})[ext]||'application/octet-stream');res.end(data);});});
(async()=>{
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const browser=await chromium.launch({headless:true,channel:'msedge'});
  try{
    const page=await browser.newPage({reducedMotion:'reduce'}), errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    const base='http://127.0.0.1:'+server.address().port;
    fs.mkdirSync(path.join(root,'artifacts','landing'),{recursive:true});
    for(const width of [320,390,768,1024,1440]){
      await page.setViewportSize({width,height:900});await page.goto(base+'/index.html');await page.evaluate(()=>document.fonts.ready);
      await page.evaluate(async()=>{for(const img of document.images){img.loading='eager';await img.decode().catch(()=>{});}});
      const result=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src),links:[...document.querySelectorAll('a')].map(a=>a.getAttribute('href')),astronaut:Math.round(document.querySelector('.astronaut').getBoundingClientRect().width),footer:document.querySelectorAll('footer').length}));
      assert(!result.overflow,`Page overflow at ${width}`);assert.deepEqual(result.broken,[],`Broken assets at ${width}`);assert.equal(result.footer,1);
      for(const href of result.links){if(href.startsWith('#'))continue;assert(fs.existsSync(path.resolve(root,href.split('#')[0].split('?')[0])),`Missing destination ${href}`);}
      if(width<800){await page.locator('#landingMenu').click();assert.equal(await page.locator('#landingMenu').getAttribute('aria-expanded'),'true');assert(await page.locator('#landingNav').isVisible());await page.keyboard.press('Escape');assert.equal(await page.locator('#landingMenu').getAttribute('aria-expanded'),'false');}
      await page.screenshot({path:path.join(root,'artifacts','landing',`home-${width}.png`),fullPage:true});
      console.log(`${width}px: no overflow, images loaded, destinations valid, menu checked; astronaut ${result.astronaut}px`);
    }
    assert.deepEqual(errors,[],'Browser errors');
    console.log('Landing checks passed.');
  }finally{await browser.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
