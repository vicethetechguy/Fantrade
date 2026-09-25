"""Player details: a focused market view in the onboarding design system."""
from common import ic

HTML = '''<main><div class="asset-page">
  <header class="asset-topbar">
    <a class="asset-back" id="assetBack" href="exchange.html" aria-label="Back"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
    <div class="asset-chip">
      <div class="asset-portrait" id="assetPortrait"></div>
      <div class="asset-name"><h1 id="assetName">Find a player</h1><p id="assetSubtitle">Search the exchange</p></div>
      <svg class="asset-chip-caret" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9.5l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <button type="button" class="asset-chip-button" id="assetSwitch" aria-haspopup="dialog" aria-label="Switch player"></button>
    </div>
    <button type="button" id="assetFavorite" class="asset-favorite" aria-label="Add to watchlist" aria-pressed="false">''' + ic('star', 'ic') + '''</button>
  </header>
  <section class="asset-missing" id="assetMissing" hidden>
    <h1>Share not found</h1><p>Search the exchange for a player or coach.</p>
    <a class="app-primary" href="exchange.html">Explore the exchange</a>
  </section>
  <div id="assetContent">
    <div class="asset-layout">
      <section class="asset-market" aria-label="Share price and chart">
        <p class="asset-label">Price per share · FTR <span class="ft-live-dot">Live</span></p>
        <div class="asset-price" id="assetPrice"></div>
        <p class="asset-price-usd" id="assetPriceUsd"></p>
        <p class="asset-movement"><strong id="assetChange"></strong><span>past 24 hours</span></p>
        <div class="asset-chart-controls">
          <div class="asset-periods" id="assetPeriods" role="group" aria-label="Chart period">
            <button type="button" data-period="1D" aria-pressed="true">1D</button>
            <button type="button" data-period="1W" aria-pressed="false">1W</button>
            <button type="button" data-period="1M" aria-pressed="false">1M</button>
            <button type="button" data-period="1Y" aria-pressed="false">1Y</button>
          </div>
          <button type="button" id="assetChartType" class="asset-chart-toggle" aria-pressed="false">Candles</button>
        </div>
        <figure class="asset-chart"><div id="assetChart" role="img" aria-label="Illustrative share price history"></div>
          <div id="assetChartAxis" class="asset-chart-axis" aria-hidden="true"></div>
          <figcaption>Illustrative prices</figcaption>
        </figure>
        <dl class="asset-stats">
          <div><dt>24h high</dt><dd id="assetHigh"></dd></div>
          <div><dt>24h low</dt><dd id="assetLow"></dd></div>
          <div><dt>24h volume</dt><dd id="assetVolume"></dd></div>
        </dl>
        <section class="asset-trades" aria-labelledby="assetTradesTitle">
          <div class="asset-section-heading"><h2 id="assetTradesTitle">Recent trades</h2><span class="ft-live-dot">Live</span></div>
          <div class="asset-trades-labels" aria-hidden="true"><span>Price · FTR</span><span>Shares</span><span>Time</span></div>
          <div id="assetTrades"></div>
        </section>
      </section>
      <aside class="asset-position" aria-labelledby="assetPositionTitle">
        <div class="asset-section-heading"><h2 id="assetPositionTitle">Your position</h2><a href="wallet.html">Wallet</a></div>
        <div id="assetHolding" aria-live="polite"></div>
        <div class="asset-trade-actions">
          <a class="app-primary" id="assetBuy" href="trade.html">Buy shares</a>
          <a class="asset-secondary" id="assetSell" href="trade.html">Sell shares</a>
        </div>
        <section class="asset-use"><span class="asset-use-icon">''' + ic('ball', 'ic') + '''</span><h2>More than a share.</h2>
          <p>Bring your eligible shares into FanPlay and back your predictions on matchday.</p>
          <a href="fanplay.html">Explore FanPlay <span aria-hidden="true">↗</span></a>
        </section>
      </aside>
      <section class="asset-details" aria-labelledby="assetDetailsTitle">
        <h2 id="assetDetailsTitle">A closer look</h2>
        <details open id="assetBio" hidden><summary>About the player</summary>
          <p class="asset-detail-note" id="assetAbout"></p>
          <dl class="asset-facts" id="assetBioFacts"></dl>
          <p class="asset-photo-credit" id="assetCredit"></p>
        </details>
        <details open><summary>About this share</summary>
          <dl class="asset-facts">
            <div><dt>Club</dt><dd id="assetClub"></dd></div>
            <div><dt>Role</dt><dd id="assetRole"></dd></div>
            <div><dt>Share symbol</dt><dd id="assetSymbol"></dd></div>
            <div><dt>Fixed supply</dt><dd>10 million shares</dd></div>
          </dl>
        </details>
        <details id="assetDepth" open><summary>Market depth</summary>
          <p class="asset-detail-note">Buy and sell orders around the current price.</p>
          <div class="asset-book">
            <div><h3>Buy orders</h3><div class="asset-book-labels"><span>Price · FTR</span><span>Shares</span></div><div id="assetBids"></div></div>
            <div><h3>Sell orders</h3><div class="asset-book-labels"><span>Price · FTR</span><span>Shares</span></div><div id="assetAsks"></div></div>
          </div>
        </details>
      </section>
    </div>
  </div>
  <dialog id="assetPicker" class="asset-picker" aria-labelledby="assetPickerTitle">
    <div class="asset-picker-heading"><h2 id="assetPickerTitle">Find your next player.</h2><button type="button" id="assetPickerClose" aria-label="Close player search">''' + ic('cross', 'ic') + '''</button></div>
    <label for="assetSearch">Search players, coaches or clubs</label>
    <input id="assetSearch" type="search" placeholder="Try Saka or Arsenal" autocomplete="off">
    <p id="assetSearchStatus" class="asset-search-status" role="status"></p>
    <div id="assetSearchResults" class="asset-search-results"></div>
  </dialog>
</div></main>'''

JS = r'''
(function(){
  var byId = function(id){ return document.getElementById(id); };
  var requested = new URLSearchParams(location.search).get('a') || 'FSAKA';
  var asset = ASSETS.find(function(a){ return a.t.toLowerCase() === requested.toLowerCase() || ftSym(a.t).toLowerCase() === requested.toLowerCase(); });
  var picker = byId('assetPicker');
  function money(value){ return pxFmt(value); }
  function live(value){ return pxLive(value); }
  function escapeText(value){ var node = document.createElement('span'); node.textContent = value; return node.innerHTML; }
  function renderSearch(){
    var query = byId('assetSearch').value.trim().toLowerCase();
    var matches = ASSETS.filter(function(a){ return (a.n + ' ' + a.t + ' ' + a.club).toLowerCase().includes(query); });
    byId('assetSearchStatus').textContent = matches.length ? matches.length + ' shares' : 'No matches. Try another name or club.';
    byId('assetSearchResults').innerHTML = matches.map(function(a){
      return '<a class="asset-search-row" href="asset.html?a=' + encodeURIComponent(a.t) + '"' + (asset && a.t === asset.t ? ' aria-current="page"' : '') + '>'
        + playerPhoto(a.t,a.n) + '<span><b>' + escapeText(a.n) + '</b><small>' + escapeText(ftSym(a.t) + ' · ' + a.club) + '</small></span>'
        + '<span class="asset-search-price">' + money(a.p) + '<small>FTR</small></span></a>';
    }).join('');
  }
  byId('assetBack').addEventListener('click',function(event){
    // Go back to wherever the player was opened from, when that was this app.
    try { if(document.referrer && new URL(document.referrer).origin === location.origin && history.length > 1){ event.preventDefault(); history.back(); } } catch(e){}
  });
  byId('assetSwitch').addEventListener('click',function(){
    byId('assetSearch').value=''; renderSearch(); picker.showModal();
    document.body.classList.add('asset-picker-open'); byId('assetSearch').focus();
  });
  byId('assetPickerClose').addEventListener('click',function(){ picker.close(); });
  picker.addEventListener('keydown',function(event){
    if(event.key==='Escape'){event.preventDefault();picker.close();}
  });
  picker.addEventListener('close',function(){ document.body.classList.remove('asset-picker-open'); byId('assetSwitch').focus(); });
  picker.addEventListener('click',function(event){
    var rect=picker.getBoundingClientRect();
    if(event.target===picker && (event.clientX<rect.left || event.clientX>rect.right || event.clientY<rect.top || event.clientY>rect.bottom)) picker.close();
  });
  byId('assetSearch').addEventListener('input',renderSearch);
  if(!asset){ byId('assetMissing').hidden=false; byId('assetContent').hidden=true; byId('assetFavorite').hidden=true; return; }

  document.title=asset.n + ' shares — Fantrade';
  byId('assetName').textContent=asset.n;
  byId('assetSubtitle').textContent=ftSym(asset.t) + ' · ' + asset.club;
  byId('assetPortrait').innerHTML=playerPhoto(asset.t,asset.n);
  function renderQuote(){
    byId('assetPrice').textContent=live(asset.p);
    // The valuation implied by the live share price.
    var val = asset.p * FTR_USD * 1e7;
    byId('assetPriceUsd').textContent = '≈ ' + usdFmt(asset.p) + ' a share · valuation $' + (val >= 1e6 ? (val / 1e6).toFixed(1) + 'M' : Math.round(val).toLocaleString('en-US'));
    byId('assetChange').textContent=(asset.d>=0?'+':'') + asset.d.toFixed(2) + '%';
    byId('assetChange').className=asset.d>=0?'asset-up':'asset-down';
    byId('assetHigh').textContent=money(asset.h);
    byId('assetLow').textContent=money(asset.low);
    byId('assetVolume').textContent=asset.vol + ' shares';
  }
  renderQuote();
  byId('assetClub').textContent=asset.club;
  /* The admin's profile for this player, when there is one. */
  function renderBio(){
    var p = (typeof PLAYER_PROFILES !== 'undefined') && PLAYER_PROFILES[asset.t], box = byId('assetBio');
    if(!p || !box) return;
    if(p.photo) byId('assetPortrait').innerHTML = playerPhoto(asset.t, asset.n);
    if(p.club) byId('assetClub').textContent = p.club;
    var facts = [];
    if(p.known_as) facts.push(['Known as', p.known_as]);
    if(p.country) facts.push(['Country', p.country]);
    if(p.dob){ var d = new Date(p.dob), n = new Date(), age = n.getFullYear() - d.getFullYear() - ((n.getMonth() < d.getMonth() || (n.getMonth() === d.getMonth() && n.getDate() < d.getDate())) ? 1 : 0);
      if(!isNaN(age)) facts.push(['Age', age + ' · born ' + d.toLocaleDateString('en-GB', {day:'numeric', month:'short', year:'numeric'})]); }
    if(p.number) facts.push(['Shirt number', '#' + p.number]);
    if(p.height) facts.push(['Height', p.height + ' cm']);
    if(p.foot) facts.push(['Stronger foot', p.foot]);
    if(!facts.length && !p.about) return;
    byId('assetAbout').textContent = p.about || ''; byId('assetAbout').hidden = !p.about;
    byId('assetBioFacts').innerHTML = facts.map(function(f){ return '<div><dt>' + escapeText(f[0]) + '</dt><dd>' + escapeText(f[1]) + '</dd></div>'; }).join('');
    byId('assetCredit').textContent = p.photo && p.credit ? 'Photo: ' + p.credit : '';
    box.hidden = false;
  }
  renderBio(); window.addEventListener('fantrade:profiles', renderBio);
  byId('assetRole').textContent=asset.c?'Coach':({FWD:'Forward',MID:'Midfielder',DEF:'Defender',GK:'Goalkeeper'}[asset.pos]||asset.pos);
  byId('assetSymbol').textContent=ftSym(asset.t);
  byId('assetBuy').href='trade.html?a='+encodeURIComponent(asset.t)+'&side=buy';
  byId('assetSell').href='trade.html?a='+encodeURIComponent(asset.t)+'&side=sell';
  function renderPosition(){
    var state=FT.getState();
    var key=Object.keys(state.holdings).find(function(k){return k.toLowerCase()===asset.t.toLowerCase();});
    var holding=key?state.holdings[key]:null;
    var shares=holding?Number(holding.shares)||0:0;
    byId('assetSell').hidden=shares<=0;
    if(shares>0){
      var value=shares*asset.p, average=Number(holding.avg)||0, pnl=value-shares*average;
      byId('assetHolding').innerHTML='<p class="asset-position-value">'+money(value)+'<small>FTR</small></p>'
        +'<p class="asset-position-shares">'+shares.toLocaleString('en-US')+' shares held</p>'
        +'<dl class="asset-position-facts"><div><dt>Average cost</dt><dd>'+money(average)+' FTR</dd></div>'
        +'<div><dt>Unrealized return</dt><dd class="'+(pnl>=0?'asset-up':'asset-down')+'">'+(pnl>=0?'+':'')+money(pnl)+' FTR</dd></div></dl>';
    }else{
      byId('assetHolding').innerHTML='<p class="asset-empty-title">Your first share starts here.</p><p class="asset-empty-copy">You don’t hold '+escapeText(asset.t)+' yet. Buy shares to start your position.</p>';
    }
    var favorite=FT.isFav(asset.t), button=byId('assetFavorite');
    button.setAttribute('aria-pressed',String(favorite));
    button.setAttribute('aria-label',favorite?'Remove from watchlist':'Add to watchlist');
    button.title=favorite?'Saved to watchlist':'Add to watchlist';
  }
  byId('assetFavorite').addEventListener('click',function(){ FT.toggleFav(asset.t); renderPosition(); });
  window.addEventListener('fantrade:statechange',renderPosition);
  window.addEventListener('pageshow',renderPosition);
  renderPosition();

  var period='1D', candles=false, series={}, liveCount=0;
  function seriesFor(p){
    if(!series[p]){
      var config=chartConfig[p];
      // Preview history, scaled to end at the current price.
      var data=candleData(config[0],asset.p,config[1],config[2]);
      var factor=asset.p/data[data.length-1].c;
      data.forEach(function(d){ ['o','h','l','c'].forEach(function(k){d[k]*=factor;}); });
      // The day's chart opens where the 24h change says it did.
      if(p==='1D'){
        var tilt=(asset.p/(1+asset.d/100))/data[0].o, n=data.length-1;
        data.forEach(function(d,i){ var f=Math.pow(tilt,1-i/n); ['o','h','l','c'].forEach(function(k){d[k]*=f;}); });
      }
      series[p]=data;
    }
    return series[p];
  }
  var chartConfig={'1D':[36,.007,17,['24h ago','12h ago','Now']], '1W':[42,.014,29,['7 days ago','3 days ago','Now']], '1M':[40,.026,41,['30 days ago','15 days ago','Now']], '1Y':[48,.05,67,['1 year ago','6 months ago','Now']]};
  function renderChart(){
    var config=chartConfig[period];
    var data=seriesFor(period);
    var low=Math.min.apply(null,data.map(function(d){return d.l;})),high=Math.max.apply(null,data.map(function(d){return d.h;}));
    var span=high-low||1,w=640,h=250,left=4,right=574,top=18,bottom=222;
    function x(i){return left+i*(right-left)/(data.length-1);}
    function y(p){return bottom-(p-low)/span*(bottom-top);}
    var line=data.map(function(d,i){return (i?'L':'M')+x(i).toFixed(1)+','+y(d.c).toFixed(1);}).join(' ');
    var color=data[data.length-1].c>=data[0].o?'#24c86b':'#ff5668', markup='';
    [high,(high+low)/2,low].forEach(function(p){markup+='<text x="638" y="'+(y(p)+4).toFixed(1)+'" text-anchor="end" fill="#979c96" font-size="11">'+pxFix(p)+'</text>';});
    if(candles){
      data.forEach(function(d,i){var c=d.c>=d.o?'#24c86b':'#ff5668';markup+='<line x1="'+x(i)+'" x2="'+x(i)+'" y1="'+y(d.h)+'" y2="'+y(d.l)+'" stroke="'+c+'" stroke-width="1.5"/><rect x="'+(x(i)-3)+'" y="'+y(Math.max(d.o,d.c))+'" width="6" height="'+Math.max(2,Math.abs(y(d.o)-y(d.c)))+'" rx="1" fill="'+c+'"/>';});
    }else{
      markup+='<defs><linearGradient id="assetChartFill" x1="0" y1="0" x2="0" y2="1"><stop stop-color="'+color+'" stop-opacity=".16"/><stop offset="1" stop-color="'+color+'" stop-opacity="0"/></linearGradient></defs>'
        +'<path d="'+line+' L'+right+','+(h-2)+' L'+left+','+(h-2)+' Z" fill="url(#assetChartFill)"/>'
        +'<path d="'+line+'" fill="none" stroke="'+color+'" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'
        +'<circle cx="'+right+'" cy="'+y(asset.p)+'" r="4" fill="'+color+'"/>';
    }
    byId('assetChart').innerHTML='<svg viewBox="0 0 '+w+' '+h+'" aria-hidden="true">'+markup+'</svg>';
    byId('assetChart').setAttribute('aria-label',period+' illustrative '+(candles?'candlestick':'line')+' chart for '+asset.n+', ending at '+money(asset.p)+' FTR per share.');
    byId('assetChartAxis').innerHTML=config[3].map(function(label){return '<span>'+label+'</span>';}).join('');
  }
  byId('assetPeriods').querySelectorAll('button').forEach(function(button){button.addEventListener('click',function(){
    period=button.dataset.period;
    byId('assetPeriods').querySelectorAll('button').forEach(function(b){b.setAttribute('aria-pressed',String(b===button));});
    renderChart();
  });});
  byId('assetChartType').addEventListener('click',function(){candles=!candles;this.setAttribute('aria-pressed',String(candles));renderChart();});
  renderChart();
  /* Order book around the live price. Sizes drift a little every tick, the way
     resting orders come and go. */
  var bookSeed=[0,1,2,3,4,5].map(function(i){ return [Math.round(1200+Math.abs(Math.sin(i*2.3))*8200), Math.round(1200+Math.abs(Math.sin(i*2.3+1))*8200)]; });
  function renderBook(){
    ['Bids','Asks'].forEach(function(side){
      var buy=side==='Bids',rows=[],total=0,sizes=[];
      for(var i=0;i<6;i++){
        var s=bookSeed[i][buy?0:1]=Math.max(150,Math.round(bookSeed[i][buy?0:1]*(1+(Math.random()-.5)*.18)));
        sizes.push(s);
      }
      var shareScale=Math.max(1,Math.round(8/Math.max(asset.p,.0001)))/8;
      for(i=0;i<6;i++){
        total+=sizes[i];
        var px=asset.p*(1+(buy?-1:1)*(i+1)*.0018),amount=Math.round(sizes[i]*shareScale);
        rows.push('<div class="asset-book-row"><i aria-hidden="true" style="width:'+Math.min(100,Math.round(total/sizes.reduce(function(a,b){return a+b;},0)*100))+'%"></i><span class="'+(buy?'asset-up':'asset-down')+'">'+live(px)+'</span><span>'+amount.toLocaleString('en-US')+'</span></div>');
      }
      byId('asset'+side).innerHTML=rows.join('');
    });
  }
  renderBook();

  /* Recent trades on this share. */
  function tradeRow(tr){
    var buy=tr.side==='buy';
    return '<div class="asset-trade-row"><span class="'+(buy?'asset-up':'asset-down')+'">'+live(tr.p)+'</span><span>'+tr.q.toLocaleString('en-US')+'</span><span data-at="'+tr.at+'">'+ftAgo(tr.at)+'</span></div>';
  }
  function renderTrades(){
    var list=(typeof FTSim!=='undefined'?FTSim.trades(asset.t):[]).slice(0,8);
    byId('assetTrades').innerHTML=list.length?list.map(tradeRow).join(''):'<p class="asset-detail-note">No trades yet today.</p>';
  }
  renderTrades();

  if(typeof FTSim!=='undefined') FTSim.focus(asset.t);
  window.addEventListener('fantrade:tick',function(e){
    var dir=e.detail.changed[asset.t];
    byId('assetTrades').querySelectorAll('[data-at]').forEach(function(el){ el.textContent=ftAgo(Number(el.dataset.at)); });
    if(!dir) return;
    renderQuote(); ftFlash(byId('assetPrice'),dir);
    // The live price moves the newest candle; every few moves a new one opens.
    liveCount++;
    Object.keys(series).forEach(function(p){
      var data=series[p], last=data[data.length-1];
      if(p==='1D' && liveCount%10===0){ data.shift(); data.push({o:last.c,h:Math.max(last.c,asset.p),l:Math.min(last.c,asset.p),c:asset.p}); }
      else { last.c=asset.p; last.h=Math.max(last.h,asset.p); last.l=Math.min(last.l,asset.p); }
    });
    renderChart(); renderBook(); renderPosition();
    var mine=e.detail.trades.filter(function(tr){ return tr.t===asset.t; });
    if(mine.length){
      var box=byId('assetTrades'); if(box.querySelector('p')) box.innerHTML='';
      box.insertAdjacentHTML('afterbegin',mine.map(tradeRow).join(''));
      var first=box.firstElementChild; if(first) first.classList.add('is-new');
      while(box.children.length>8) box.removeChild(box.lastChild);
    }
  });
})();
'''
