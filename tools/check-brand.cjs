const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const server=http.createServer((req,res)=>{
  const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));
  if(!file.startsWith(root+path.sep))return res.writeHead(403).end();
  fs.readFile(file,(err,data)=>{
    if(err)return res.writeHead(404).end();
    res.setHeader('Content-Type',({'.html':'text/html','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.ttf':'font/ttf'})[path.extname(file)]||'application/octet-stream');
    res.end(data);
  });
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({headless:true,channel:'msedge'});
  const output=path.join(root,'artifacts','brand');fs.mkdirSync(output,{recursive:true});
  try{
    const page=await browser.newPage({reducedMotion:'reduce'});
    await page.route('https://fonts.googleapis.com/**',route=>route.abort());
    await page.route('https://fonts.gstatic.com/**',route=>route.abort());
    for(const width of [320,390,1280]){
      await page.setViewportSize({width,height:900});
      for(const name of ['index.html','signin.html','signup.html','admin.html']){
        await page.goto(`http://127.0.0.1:${server.address().port}/${name}`,{waitUntil:'networkidle'});
        await page.evaluate(()=>document.fonts.ready);
        const result=await page.evaluate(()=>({
          overflow:document.documentElement.scrollWidth>innerWidth+1,
          font:getComputedStyle(document.body).fontFamily,
          weights:[...document.querySelectorAll('h1,h2,h3,h4')].map(el=>getComputedStyle(el).fontWeight),
          broken:[...document.images].filter(el=>el.complete&&!el.naturalWidth).map(el=>el.src),
          oldLogo:[...document.images].some(el=>/fantrade-(?:outline-)?logo\.png|assets\/logo\.png/.test(el.src)),
          faces:[...document.fonts].filter(face=>face.family==='Montserrat'&&face.status==='loaded').length
        }));
        assert(!result.overflow,`${name} overflows at ${width}px`);
        assert(result.font.startsWith('Montserrat')&&result.faces>=2,`${name} must load both local Montserrat weights`);
        assert(result.weights.every(weight=>weight==='800'),`${name} must use ExtraBold headings`);
        assert(!result.oldLogo,`${name} still uses old branding`);
        assert.deepEqual(result.broken,[],`${name} has broken images`);
        await page.screenshot({path:path.join(output,`${name.replace('.html','')}-${width}.png`),fullPage:false});
      }
      console.log(`Brand, authentication and admin checks passed at ${width}px`);
    }
  }finally{await browser.close();server.close();}
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
