"""Portfolio: balances, holdings and activity without duplicate dashboards."""
from app_design import intro

HTML = '<main><div class="secondary-page portfolio-page">' + intro('Your portfolio', 'See what you own. Decide what comes next.', '<button class="quiet-button" id="pfExport" type="button">Export CSV</button>') + '''
<section class="portfolio-overview" aria-label="Portfolio balances">
  <div class="portfolio-total"><p class="quiet-label">Total value · FTR</p><h2 id="pfNet">—</h2><p class="quiet-note">Your shares, available balance and locked funds.</p></div>
  <dl class="portfolio-balances"><div><dt>Available balance</dt><dd id="pfAvailable">—</dd></div><div><dt>Locked funds</dt><dd id="pfLocked">—</dd></div><div><dt>Unrealized return</dt><dd id="pfPnl">—</dd></div></dl>
</section>
<nav class="quiet-tabs" id="pfViews" aria-label="Portfolio view"><button type="button" data-view="holdings" aria-pressed="true">Holdings</button><button type="button" data-view="activity" aria-pressed="false">Activity</button></nav>
<section id="pfHoldingsView" aria-label="Your holdings">
  <div class="portfolio-filters"><div class="quiet-filters" id="pfFilter" role="group" aria-label="Filter holdings"><button type="button" data-f="all" aria-pressed="true">All</button><button type="button" data-f="player" aria-pressed="false">Players</button><button type="button" data-f="coach" aria-pressed="false">Coaches</button><button type="button" data-f="club" aria-pressed="false">In your club</button></div>
  <label class="quiet-search"><span class="sr-only">Search your holdings</span><input type="search" id="pfSearch" placeholder="Search your shares" autocomplete="off"></label></div>
  <p class="quiet-note" id="pfCount" role="status"></p>
  <div id="pfRows" class="portfolio-rows"></div>
  <a class="app-primary portfolio-explore" href="exchange.html">Explore the exchange</a>
</section>
<section id="pfActivityView" aria-label="Your transactions" hidden><div class="section-heading"><h2>Recent activity</h2><a href="activity.html">View all activity</a></div><div id="pfLedger"></div></section>
</div></main>'''

JS = r'''
(function(){
  var el=function(id){return document.getElementById(id);},filter='all';
  function fmt(value){return Number(value||0).toLocaleString('en-US',{maximumFractionDigits:2});}
  function esc(value){var node=document.createElement('span');node.textContent=value;return node.innerHTML.replace(/"/g,'&quot;');}
  function render(){
    var state=FT.getState(),keys=Object.keys(state.holdings).filter(function(k){return state.holdings[k].shares>0;}),value=0,cost=0;
    keys.forEach(function(k){var h=state.holdings[k];value+=h.shares*h.p;cost+=h.shares*h.avg;});
    el('pfNet').textContent=fmt(value+state.wallet.balance+state.wallet.locked);
    el('pfAvailable').textContent=fmt(state.wallet.balance)+' FTR';el('pfLocked').textContent=fmt(state.wallet.locked)+' FTR';
    el('pfPnl').textContent=(value-cost>=0?'+':'')+fmt(value-cost)+' FTR';el('pfPnl').className=value-cost>=0?'positive':'negative';
    var query=el('pfSearch').value.trim().toLowerCase();
    var shown=keys.filter(function(k){var h=state.holdings[k];return (filter==='all'||filter==='player'&&!h.c||filter==='coach'&&h.c||filter==='club'&&h.inClub&&h.inClub!=='SUB')&&(k+' '+h.n).toLowerCase().includes(query);});
    el('pfCount').textContent=shown.length+' of '+keys.length+' positions · Values in FTR';
    el('pfRows').innerHTML=shown.map(function(k){
      var h=state.holdings[k],pnl=h.shares*(h.p-h.avg),position=h.inClub&&h.inClub!=='SUB';
      return '<div class="portfolio-row"><a class="portfolio-player" href="asset.html?a='+encodeURIComponent(k)+'">'+playerPhoto(k,h.n)+'<span><b>'+esc(h.n)+'</b><small>'+esc(k)+' · '+fmt(h.shares)+' shares'+(position?' · In club':'')+'</small></span></a>'
        +'<div class="portfolio-cost"><span>Average cost</span><b>'+fmt(h.avg)+' FTR</b></div><div class="portfolio-value"><b>'+fmt(h.shares*h.p)+' <small>FTR</small></b><span class="'+(pnl>=0?'positive':'negative')+'">'+(pnl>=0?'+':'')+fmt(pnl)+' FTR return</span></div>'
        +'<a class="quiet-button portfolio-trade" aria-label="Trade '+esc(h.n)+'" href="trade.html?a='+encodeURIComponent(k)+'">Trade</a></div>';
    }).join('')||'<div class="quiet-empty"><h2>'+(keys.length?'No matching shares.':'Your portfolio starts here.')+'</h2><p>'+(keys.length?'Try another name or filter.':'Buy player or coach shares on the exchange and follow them here.')+'</p></div>';
    el('pfLedger').innerHTML=state.transactions.slice(0,20).map(function(t){
      var negative=['BUY','STAKE','SEND','WITHDRAW'].includes(t.type);
      var label=({BUY:'Bought shares',SELL:'Sold shares',STAKE:'FanPlay stake',PAYOUT:'Payout',DEPOSIT:'Deposit',CONVERT:'Conversion',SWAP:'Swap'})[t.type]||t.type;
      return '<div class="activity-row"><div><b>'+esc(label)+'</b><p>'+esc(t.asset)+' · '+esc(t.time)+'</p></div><span class="'+(negative?'negative':'positive')+'">'+(negative?'−':'+')+fmt(t.total)+' FTR</span></div>';
    }).join('')||'<div class="quiet-empty"><h2>No activity yet.</h2><p>Your transactions will appear here.</p></div>';
  }
  el('pfSearch').addEventListener('input',render);
  el('pfFilter').querySelectorAll('button').forEach(function(button){button.addEventListener('click',function(){filter=button.dataset.f;el('pfFilter').querySelectorAll('button').forEach(function(b){b.setAttribute('aria-pressed',String(b===button));});render();});});
  el('pfViews').querySelectorAll('button').forEach(function(button){button.addEventListener('click',function(){el('pfViews').querySelectorAll('button').forEach(function(b){b.setAttribute('aria-pressed',String(b===button));});el('pfHoldingsView').hidden=button.dataset.view!=='holdings';el('pfActivityView').hidden=button.dataset.view!=='activity';});});
  el('pfExport').addEventListener('click',function(){
    var state=FT.getState(),rows=[['Type','Asset','Units','Price (FTR)','Total (FTR)','When']];
    state.transactions.forEach(function(t){rows.push([t.type,t.asset,t.shares,t.price,t.total,t.time]);});
    rows.push([],['Holding','Shares','Average cost','Price','Value']);
    Object.keys(state.holdings).forEach(function(k){var h=state.holdings[k];rows.push([k,h.shares,h.avg,h.p,h.shares*h.p]);});
    function cell(value){var s=String(value==null?'':value);if(typeof value==='string'&&/^[=+\-@\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';}
    var url=URL.createObjectURL(new Blob([rows.map(function(row){return row.map(cell).join(',');}).join('\r\n')],{type:'text/csv;charset=utf-8'}));
    var link=document.createElement('a');link.href=url;link.download='fantrade-ledger.csv';document.body.appendChild(link);link.click();link.remove();setTimeout(function(){URL.revokeObjectURL(url);},1000);
  });
  render();window.addEventListener('fantrade:statechange',render);window.addEventListener('pageshow',render);
})();
'''
