"""Player details: a focused market view in the onboarding design system."""
from common import ic

HTML = '''<main><div class="asset-page">
  <header class="asset-topbar">
    <div class="asset-who">
      <svg class="asset-who-caret" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9.5l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <div class="asset-portrait" id="assetPortrait"></div>
      <div class="asset-name"><p id="assetSubtitle">Search the exchange</p><h1 id="assetName">Find a player</h1></div>
      <button type="button" class="asset-who-button" id="assetSwitch" aria-haspopup="dialog" aria-label="Switch player"></button>
    </div>
    <div class="asset-topbar-actions">
      <button type="button" id="assetFavorite" class="asset-favorite" aria-label="Add to watchlist" aria-pressed="false">''' + ic('star', 'ic') + '''</button>
      <a class="back-btn asset-back" id="assetBack" href="exchange.html">Back</a>
    </div>
  </header>
  <section class="asset-missing" id="assetMissing" hidden>
    <h1>Share not found</h1><p>Search the exchange for a player or coach.</p>
    <a class="app-primary" href="exchange.html">Explore the exchange</a>
  </section>
  <div id="assetContent">
    <nav class="kc-cat-tabs asset-tabs" id="assetTabs" role="tablist" aria-label="Share sections">
      <button type="button" class="kc-cat-tab on" role="tab" id="tab-chart" data-tab="chart" aria-controls="panel-chart" aria-selected="true">Chart</button>
      <button type="button" class="kc-cat-tab" role="tab" id="tab-feed" data-tab="feed" aria-controls="panel-feed" aria-selected="false" tabindex="-1">Feed</button>
      <button type="button" class="kc-cat-tab" role="tab" id="tab-info" data-tab="info" aria-controls="panel-info" aria-selected="false" tabindex="-1">AS info</button>
      <button type="button" class="kc-cat-tab" role="tab" id="tab-discover" data-tab="discover" aria-controls="panel-discover" aria-selected="false" tabindex="-1">Discover</button>
    </nav>
    <div class="asset-layout">
      <div class="asset-panels">
      <section class="asset-market asset-panel" id="panel-chart" role="tabpanel" aria-labelledby="tab-chart">
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
        <section class="asset-trades asset-depth" id="assetDepth" aria-labelledby="assetDepthTitle">
          <div class="asset-section-heading"><h2 id="assetDepthTitle">Market depth</h2></div>
          <p class="asset-detail-note">Buy and sell orders around the current price.</p>
          <div class="asset-book">
            <div><h3>Buy orders</h3><div class="asset-book-labels"><span>Price · FTR</span><span>Shares</span></div><div id="assetBids"></div></div>
            <div><h3>Sell orders</h3><div class="asset-book-labels"><span>Price · FTR</span><span>Shares</span></div><div id="assetAsks"></div></div>
          </div>
        </section>
      </section>

      <section class="asset-panel asset-feed-panel" id="panel-feed" role="tabpanel" aria-labelledby="tab-feed" hidden>
        <div class="asset-subtabs" role="group" aria-label="Feed">
          <button type="button" data-feed="posts" aria-pressed="true">Fan posts</button>
          <button type="button" data-feed="updates" aria-pressed="false">Market updates</button>
          <span class="ft-live-dot">Live</span>
        </div>
        <div id="feedPostsWrap">
          <form class="asset-compose" id="feedCompose">
            <span class="asset-avatar" id="feedMe" aria-hidden="true"></span>
            <div class="asset-compose-main">
              <label class="sr-only" for="feedText">Your post</label>
              <textarea id="feedText" rows="2" maxlength="280" placeholder="Share your take"></textarea>
              <div class="asset-compose-foot"><span id="feedCount">0 / 280</span><button type="submit" class="asset-post-btn" id="feedPost" disabled>Post</button></div>
            </div>
          </form>
          <div class="asset-feed" id="feedPosts" aria-live="polite"></div>
          <p class="asset-feed-note">Posts are fans' own views, not advice.</p>
        </div>
        <div class="asset-feed" id="feedUpdates" hidden></div>
      </section>

      <section class="asset-panel asset-info" id="panel-info" role="tabpanel" aria-labelledby="tab-info" hidden>
        <p class="asset-info-note">An Activity Share's value comes from the player's real-world dollar valuation and from trading on Fantrade. Figures here update with the market.</p>
        <div class="asset-info-head"><h2 id="infoName"></h2><span class="asset-rank" id="infoRank"></span></div>
        <dl class="asset-info-grid" id="infoGrid"></dl>
        <section class="asset-info-block" id="assetBio" hidden><h3>About the player</h3>
          <p class="asset-detail-note" id="assetAbout"></p>
          <dl class="asset-facts" id="assetBioFacts"></dl>
          <p class="asset-photo-credit" id="assetCredit"></p>
        </section>
        <section class="asset-info-block"><h3>About this share</h3>
          <dl class="asset-facts">
            <div><dt>Club</dt><dd id="assetClub"></dd></div>
            <div><dt>Role</dt><dd id="assetRole"></dd></div>
            <div><dt>Share symbol</dt><dd id="assetSymbol"></dd></div>
            <div><dt>Fixed supply</dt><dd>10,000,000 shares</dd></div>
            <div><dt>Priced in</dt><dd>$FTR</dd></div>
          </dl>
        </section>
        <section class="asset-info-block"><h3>What is an Activity Share?</h3>
          <p class="asset-detail-note">Every player and coach on Fantrade has 10,000,000 Activity Shares, and that number never changes. A share is worth the player's dollar valuation divided by 10,000,000, paid in $FTR at the live $FTR price. Hold shares to build your Dream Club, back your predictions in FanPlay, or trade them on the exchange.</p>
        </section>
      </section>

      <section class="asset-panel asset-discover" id="panel-discover" role="tabpanel" aria-labelledby="tab-discover" hidden>
        <div class="asset-disc-grid">
          <a class="asset-disc-card" href="fanplay.html">
            <span class="asset-disc-tag">FanPlay</span>
            <h3>Back <span class="js-short"></span> on matchday.</h3>
            <p>Bring your eligible shares into FanPlay and back your predictions.</p>
            <span class="asset-disc-go">Explore FanPlay <span aria-hidden="true">→</span></span>
          </a>
          <a class="asset-disc-card" href="club-builder.html">
            <span class="asset-disc-tag">Dream Club</span>
            <h3>Put <span class="js-short"></span> in your Dream Club.</h3>
            <p>Build your side from the shares you hold and climb the division.</p>
            <span class="asset-disc-go">Build your club <span aria-hidden="true">→</span></span>
          </a>
          <a class="asset-disc-card" id="discSwap" href="swap.html">
            <span class="asset-disc-tag">Swap</span>
            <h3>Swap into <span class="js-short"></span>.</h3>
            <p>Move from shares you hold into <span class="js-sym"></span> in one step.</p>
            <span class="asset-disc-go">Swap shares <span aria-hidden="true">→</span></span>
          </a>
          <a class="asset-disc-card" href="dashboard.html">
            <span class="asset-disc-tag">Claim</span>
            <h3><span id="discOpen"></span> open to claim.</h3>
            <p>Be the first to claim a player or coach and launch their shares.</p>
            <span class="asset-disc-go">Find a player <span aria-hidden="true">→</span></span>
          </a>
        </div>
        <section class="asset-info-block"><div class="asset-section-heading"><h2>Similar shares</h2><a href="exchange.html">Exchange</a></div>
          <div id="discSimilar" class="asset-similar"></div>
        </section>
      </section>
      </div>
      <aside class="asset-position" aria-labelledby="assetPositionTitle">
        <div class="asset-section-heading"><h2 id="assetPositionTitle">Your position</h2><a href="wallet.html">Wallet</a></div>
        <div id="assetHolding" aria-live="polite"></div>
        <div class="asset-trade-actions">
          <a class="app-primary" id="assetBuy" href="trade.html">Buy shares</a>
          <a class="asset-secondary" id="assetSell" href="trade.html">Sell shares</a>
        </div>
      </aside>
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
    if(!byId('panel-chart').hidden) renderChart(); renderBook(); renderPosition();
    var mine=e.detail.trades.filter(function(tr){ return tr.t===asset.t; });
    if(mine.length){
      var box=byId('assetTrades'); if(box.querySelector('p')) box.innerHTML='';
      box.insertAdjacentHTML('afterbegin',mine.map(tradeRow).join(''));
      var first=box.firstElementChild; if(first) first.classList.add('is-new');
      while(box.children.length>8) box.removeChild(box.lastChild);
    }
  });

  /* ── Sections: Chart, Feed, AS info, Discover ─────────────────────── */
  var TABS=['chart','feed','info','discover'], tabBtns=[].slice.call(document.querySelectorAll('#assetTabs [data-tab]'));
  function showTab(k, focus){
    if(TABS.indexOf(k)<0) k='chart';
    tabBtns.forEach(function(b){ var on=b.dataset.tab===k; b.classList.toggle('on',on); b.setAttribute('aria-selected',String(on)); b.tabIndex=on?0:-1; if(on&&focus) b.focus(); });
    TABS.forEach(function(t){ byId('panel-'+t).hidden = t!==k; });
    if(k==='chart') renderChart();
    if(k==='info') renderInfo();
    if(k==='feed') renderFeed();
    if(k==='discover') renderDiscover();
    try { history.replaceState(null,'',location.pathname+location.search+(k==='chart'?'':'#'+k)); } catch(e){}
  }
  tabBtns.forEach(function(b,i){
    b.addEventListener('click',function(){ showTab(b.dataset.tab); });
    b.addEventListener('keydown',function(e){
      var d=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0; if(!d) return;
      e.preventDefault(); showTab(tabBtns[(i+d+tabBtns.length)%tabBtns.length].dataset.tab,true);
    });
  });

  var shortName=(function(){ var p=(typeof PLAYER_PROFILES!=='undefined'&&PLAYER_PROFILES[asset.t])||{}; if(p.known_as) return p.known_as;
    var w=asset.n.split(' '); return w.length>1?w[w.length-1]:asset.n; })();
  document.querySelectorAll('.js-short').forEach(function(el){ el.textContent=shortName; });
  document.querySelectorAll('.js-sym').forEach(function(el){ el.textContent=ftSym(asset.t); });
  byId('feedText').placeholder='Share your take on '+shortName;
  function usdBig(n){ n=Number(n)||0; var a=Math.abs(n);
    if(a>=1e9) return '$'+(n/1e9).toFixed(2)+'B'; if(a>=1e6) return '$'+(n/1e6).toFixed(2)+'M'; if(a>=1e4) return '$'+Math.round(n).toLocaleString('en-US');
    return '$'+pxFmt(n); }
  function volNum(v){ var m=String(v||'0').match(/([\d.]+)\s*([KM]?)/i); return m?Number(m[1])*({K:1e3,M:1e6}[m[2].toUpperCase()]||1):0; }
  function rankOf(){ var list=ASSETS.slice().sort(function(a,b){ return b.p-a.p; }); return list.indexOf(asset)+1; }

  /* AS info */
  function renderInfo(){
    var cap=asset.p*FTR_USD*1e7, vol=volNum(asset.vol), volUsd=vol*asset.p*FTR_USD, year=seriesFor('1Y');
    var hi=Math.max.apply(null,year.map(function(d){return d.h;})), lo=Math.min.apply(null,year.map(function(d){return d.l;}));
    var st=FT.getState(), key=Object.keys(st.holdings).find(function(k){return k.toLowerCase()===asset.t.toLowerCase();}), mine=key?Number(st.holdings[key].shares)||0:0;
    byId('infoName').textContent=asset.n;
    byId('infoRank').textContent='No. '+rankOf();
    byId('infoRank').title='Ranked by market cap among '+ASSETS.length+' shares on Fantrade';
    var rows=[
      ['Market cap', usdBig(cap), pxFmt(asset.p*1e7)+' $FTR'],
      ['Real-world valuation', asset.v?usdBig(asset.v):'—', asset.c?'Fantrade estimate':'Transfer-market value'],
      ['Price per share', live(asset.p)+' $FTR', '≈ '+usdFmt(asset.p)],
      ['Total supply', '10,000,000', 'shares, fixed'],
      ['24h volume', asset.vol+' shares', '≈ '+usdBig(volUsd)],
      ['24h volume / market cap', (cap?(volUsd/cap*100):0).toFixed(2)+'%', 'share of value traded today'],
      ['1-year high', live(hi)+' $FTR', '≈ '+usdFmt(hi)],
      ['1-year low', live(lo)+' $FTR', '≈ '+usdFmt(lo)],
      ['Your shares', mine.toLocaleString('en-US'), (mine/1e7*100).toFixed(mine?4:0)+'% of supply']
    ];
    if(asset.launched) rows.push(['Launched on Fantrade', new Date(asset.launched).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'}), asset.launchedBy?'claimed by @'+asset.launchedBy:'']);
    byId('infoGrid').innerHTML=rows.map(function(r){ return '<div><dt>'+r[0]+'</dt><dd>'+escapeText(r[1])+'</dd><small>'+escapeText(r[2])+'</small></div>'; }).join('');
  }

  /* Discover */
  function renderDiscover(){
    var open=(typeof ELIGIBLE!=='undefined'?ELIGIBLE:[]).filter(function(e){ return !FT.isLaunched || !FT.isLaunched(e.t); }).length;
    byId('discOpen').textContent=open+(open===1?' player':' players and coaches');
    byId('discSwap').href='swap.html?to='+encodeURIComponent(asset.t);
    var same=ASSETS.filter(function(a){ return a!==asset && !!a.c===!!asset.c; }).map(function(a){
      var score=(a.club===asset.club?3:0)+(a.pos===asset.pos?2:0)+(a.lg===asset.lg?1:0)+(!!a.w===!!asset.w?1:0); return {a:a,s:score}; })
      .sort(function(x,y){ return y.s-x.s || Math.abs(x.a.p-asset.p)-Math.abs(y.a.p-asset.p); }).slice(0,5);
    byId('discSimilar').innerHTML=same.map(function(o){ var a=o.a, up=a.d>=0;
      return '<a class="asset-similar-row" href="asset.html?a='+encodeURIComponent(a.t)+'">'+playerPhoto(a.t,a.n)
        +'<span><b>'+escapeText(a.n)+'</b><small>'+escapeText(ftSym(a.t)+' · '+(a.club||''))+'</small></span>'
        +'<span class="asset-similar-px">'+live(a.p)+'<small class="'+(up?'asset-up':'asset-down')+'">'+(up?'+':'')+a.d.toFixed(2)+'%</small></span></a>'; }).join('');
  }

  /* Feed: fans' posts and the share's market updates. The posts are the
     demo community (plus anything you post, kept in this browser). */
  var FANS=[['Amaka Obi','amaka_fc'],['Tobi Adeyemi','tobi_eleven'],['Jess Morgan','gooner_jess'],['Kwame Mensah','kwame_m'],['Liam Price','lp_scout'],
    ['Sofia Reyes','sofi_r'],['Daniel Okoro','dan_okoro'],['Priya Shah','priya_fc'],['Tom Harris','tomh'],['Chioma Eze','chioma_e'],['Marcus Lee','marcus_l'],['Zara Ahmed','zara_fc']];
  var TPL=asset.c?[
    '{n} in my Dream Club dugout. The coach boost is underrated.',
    'The set-up at {club} is why I keep holding {sym}.',
    'Added {sym} before the weekend. Coach shares move slower, which suits me.',
    '{sym} is my steady hold while I trade the forwards.',
    'Took a little profit on {sym} after the run. Still holding most of it.',
    'Set a buy order just under the last price on {sym}. Let us see if it fills.',
    'Swapped some of my forwards into {sym} this week. Balance matters.',
    'Holding {sym} for the long run. Small dips do not bother me.'
  ]:[
    'Added more {sym} on the dip today. {n} is the one I want to hold all season.',
    '{n} is in my FanPlay entry this weekend. Backing a goal contribution.',
    'Anyone else building their Dream Club around {n}?',
    'Volume on {sym} has picked up. Watching how it closes the day.',
    'Took some profit on {sym} after the run up. Still holding a core position.',
    '{club} fans, how many {sym} are you holding?',
    'My first Activity Share was {sym}. Not selling.',
    'Set a buy order a little under the last price on {sym}. Let us see if it fills.',
    'Holding {sym} for the long run. Small dips do not bother me.',
    'Swapped some of my other shares into {sym} this week.',
    'Watching the order book on {sym}. Buyers keep stepping in.',
    '{n} is the first name on my Dream Club team sheet.'
  ];
  var seed=0; for(var si=0;si<asset.t.length;si++) seed=(seed*31+asset.t.charCodeAt(si))>>>0;
  function rnd(){ seed=(seed*1664525+1013904223)>>>0; return seed/4294967296; }
  function fill(t){ return t.replace(/\{n\}/g,shortName).replace(/\{sym\}/g,ftSym(asset.t)).replace(/\{club\}/g,asset.club||'Club'); }
  // Cycle through shuffled templates and fans so the feed does not repeat itself.
  function shuffled(n){ var a=[]; for(var i=0;i<n;i++) a.push(i); for(i=n-1;i>0;i--){ var j=Math.floor(rnd()*(i+1)), t=a[i]; a[i]=a[j]; a[j]=t; } return a; }
  var tOrder=shuffled(TPL.length), fOrder=shuffled(FANS.length), tI=0, fI=0;
  function makePost(at){ var f=FANS[fOrder[fI++%FANS.length]];
    return { id:'p'+Math.floor(rnd()*1e9), name:f[0], handle:f[1], text:fill(TPL[tOrder[tI++%TPL.length]]), at:at, likes:Math.floor(Math.pow(rnd(),2)*140), replies:Math.floor(rnd()*12) }; }
  var posts=[], agoMs=[9,26,48,95,160,300,540,900,1500,2600].map(function(m){ return m*60000; });
  agoMs.forEach(function(ms){ posts.push(makePost(Date.now()-ms-Math.floor(rnd()*300000))); });
  function readJSON(k,d){ try { return JSON.parse(localStorage.getItem(k)||'null')||d; } catch(e){ return d; } }
  function writeJSON(k,v){ try { localStorage.setItem(k,JSON.stringify(v)); } catch(e){} }
  var ownPosts=readJSON('ft_feed_v1',{}), liked=readJSON('ft_feed_likes',{});
  function initialsOf(n){ var w=String(n||'?').trim().split(/\s+/); return ((w[0]||'?')[0]+(w.length>1?w[w.length-1][0]:'')).toUpperCase(); }
  function feedAgo(ms){ var s=Math.max(1,Math.round((Date.now()-ms)/1000)); return s<60?'just now':s<3600?Math.floor(s/60)+'m':s<86400?Math.floor(s/3600)+'h':Math.floor(s/86400)+'d'; }
  var ICON_HEART='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-7-4.4-7-10a4 4 0 017-2.6A4 4 0 0119 10c0 5.6-7 10-7 10z"/></svg>';
  var ICON_REPLY='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5h14v10H9l-4 4z"/></svg>';
  var ICON_SHARE='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 5l6 6-6 6M20 11H9a5 5 0 00-5 5v2"/></svg>';
  function postHtml(p){
    var on=!!liked[p.id], likes=p.likes+(on?1:0), up=asset.d>=0;
    return '<article class="asset-post'+(p.fresh?' is-new':'')+'" data-id="'+p.id+'">'
      +'<div class="asset-post-head"><span class="asset-avatar'+(p.mine?' me':'')+'" aria-hidden="true">'+initialsOf(p.name)+'</span><div><b>'+escapeText(p.name)+'</b><small>@'+escapeText(p.handle)+' · <span data-at="'+p.at+'">'+feedAgo(p.at)+'</span></small></div></div>'
      +'<p>'+escapeText(p.text)+'</p>'
      +'<span class="asset-post-tag">'+escapeText(ftSym(asset.t))+' <span class="'+(up?'asset-up':'asset-down')+'">'+(up?'+':'')+asset.d.toFixed(2)+'%</span></span>'
      +'<div class="asset-post-actions"><button type="button" data-like aria-pressed="'+on+'" aria-label="Like">'+ICON_HEART+'<span>'+likes+'</span></button>'
      +'<span>'+ICON_REPLY+'<span>'+p.replies+'</span></span>'
      +'<button type="button" data-share aria-label="Share">'+ICON_SHARE+'<span>Share</span></button></div></article>';
  }
  var feedView='posts';
  function allPosts(){ return (ownPosts[asset.t]||[]).map(function(p){ return Object.assign({mine:true,replies:0},p); }).concat(posts).sort(function(a,b){ return b.at-a.at; }); }
  function renderPosts(){ byId('feedPosts').innerHTML=allPosts().map(postHtml).join(''); }
  function renderUpdates(){
    var cap=asset.p*FTR_USD*1e7, up=asset.d>=0, now=Date.now(), items=[
      ['Price', ftSym(asset.t)+' is at '+live(asset.p)+' $FTR (≈ '+usdFmt(asset.p)+'), '+(up?'up ':'down ')+Math.abs(asset.d).toFixed(2)+'% in 24 hours.', now],
      ['Range', 'Today’s range is '+live(asset.low)+' to '+live(asset.h)+' $FTR.', now-4*60000],
      ['Volume', asset.vol+' shares traded in the last 24 hours.', now-11*60000],
      ['Rank', shortName+' is No. '+rankOf()+' by market cap on Fantrade, at '+usdBig(cap)+'.', now-38*60000]];
    if(asset.v) items.push(['Valuation', 'Real-world valuation: '+usdBig(asset.v)+'. Each share is worth a ten-millionth of it.', now-3*3600000]);
    if(asset.launched) items.push(['Launch', ftSym(asset.t)+' launched on Fantrade'+(asset.launchedBy?', claimed by @'+asset.launchedBy:'')+'.', asset.launched]);
    byId('feedUpdates').innerHTML=items.map(function(u){ return '<article class="asset-update"><span class="asset-disc-tag">'+u[0]+'</span><p>'+escapeText(u[1])+'</p><small data-at="'+u[2]+'">'+feedAgo(u[2])+'</small></article>'; }).join('');
  }
  function renderFeed(){
    var me=FT.getState().user||{}; byId('feedMe').textContent=initialsOf(me.name||me.handle||'You');
    byId('feedPostsWrap').hidden=feedView!=='posts'; byId('feedUpdates').hidden=feedView!=='updates';
    if(feedView==='posts') renderPosts(); else renderUpdates();
  }
  document.querySelectorAll('[data-feed]').forEach(function(b){ b.addEventListener('click',function(){
    feedView=b.dataset.feed; document.querySelectorAll('[data-feed]').forEach(function(x){ x.setAttribute('aria-pressed',String(x===b)); }); renderFeed(); }); });
  byId('feedText').addEventListener('input',function(){ var n=this.value.trim().length; byId('feedCount').textContent=this.value.length+' / 280'; byId('feedPost').disabled=!n; });
  byId('feedCompose').addEventListener('submit',function(e){
    e.preventDefault(); var t=byId('feedText').value.trim(); if(!t) return;
    var me=FT.getState().user||{}, list=ownPosts[asset.t]=ownPosts[asset.t]||[];
    list.unshift({ id:'m'+Date.now(), name:me.name||'You', handle:me.handle||'you', text:t.slice(0,280), at:Date.now(), likes:0, fresh:true });
    writeJSON('ft_feed_v1',ownPosts); byId('feedText').value=''; byId('feedCount').textContent='0 / 280'; byId('feedPost').disabled=true; renderPosts();
    if(typeof showToast==='function') showToast('Posted to the '+ftSym(asset.t)+' feed');
  });
  byId('feedPosts').addEventListener('click',function(e){
    var art=e.target.closest('.asset-post'); if(!art) return;
    if(e.target.closest('[data-like]')){ var id=art.dataset.id; if(liked[id]) delete liked[id]; else liked[id]=1; writeJSON('ft_feed_likes',liked);
      var b=e.target.closest('[data-like]'), n=b.querySelector('span'); b.setAttribute('aria-pressed',String(!!liked[id])); n.textContent=Number(n.textContent)+(liked[id]?1:-1); }
    if(e.target.closest('[data-share]')){ var url=location.origin+location.pathname+'?a='+encodeURIComponent(asset.t)+'#feed', txt=art.querySelector('p').textContent;
      if(navigator.share) navigator.share({title:asset.n+' on Fantrade',text:txt,url:url}).catch(function(){});
      else if(navigator.clipboard) navigator.clipboard.writeText(url).then(function(){ if(typeof showToast==='function') showToast('Link copied'); }).catch(function(){}); }
  });
  // With the demo market running, the feed keeps moving too.
  var feedTicks=0;
  window.addEventListener('fantrade:tick',function(e){
    document.querySelectorAll('#panel-feed [data-at]').forEach(function(el){ el.textContent=feedAgo(Number(el.dataset.at)); });
    if(++feedTicks%28===0){ var p=makePost(Date.now()); p.fresh=true; posts.unshift(p); posts=posts.slice(0,30);
      if(!byId('panel-feed').hidden && feedView==='posts') renderPosts(); }
    if(e.detail.changed[asset.t]){
      if(!byId('panel-info').hidden) renderInfo();
      if(!byId('panel-feed').hidden && feedView==='updates') renderUpdates();
    }
  });
  showTab((location.hash||'').replace('#',''));
})();
'''
