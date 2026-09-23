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
    var listerHtml = '';
    var claims = state.listerClaims || [];
    if(claims.length){
      listerHtml = '<div class="kc-group-box" style="margin-bottom:28px;background:#121411;border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:22px">'
        + '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">'
        + '  <div><h3 style="margin:0;font-size:18px;font-family:Archivo,sans-serif;color:var(--ink)">Lister Allocations & Vesting</h3>'
        + '  <p style="margin:4px 0 0;font-size:12px;color:var(--dim)">Whitepaper v2.0 §8 · 1% daily trading release & 30% trading fee participation</p></div>'
        + '  <span style="background:rgba(24,0,173,.3);color:#a596ed;padding:4px 12px;border-radius:999px;font-size:11px;font-weight:600">' + claims.length + ' Launched</span>'
        + '</div>'
        + '<div style="display:grid;gap:12px">'
        + claims.map(function(cl){
            var daysLeft = Math.max(0, Math.ceil((cl.vestingUntil - Date.now()) / (1000 * 3600 * 24)));
            var dailyAvail = Math.max(0, cl.dailyLimit - (cl.tradedToday || 0));
            return '<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:14px;padding:16px;display:grid;grid-template-columns:auto 1fr auto;gap:16px;align-items:center">'
              + playerPhoto(cl.assetId, cl.name, 'kc-avatar')
              + '<div><div style="display:flex;align-items:center;gap:8px"><b>' + esc(cl.name) + '</b> <span style="background:#1800ad;color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:6px">' + esc(cl.ticker) + '</span></div>'
              + '<div style="font-size:12px;color:var(--dim);margin-top:4px">Level ' + cl.level + ' (' + cl.percent + '% of 10M) · <b>' + Number(cl.shares).toLocaleString() + ' shares</b> · ' + cl.vestingYears + '-year vesting (' + daysLeft + ' days remaining)</div>'
              + '<div style="font-size:11px;color:#a596ed;margin-top:4px">Daily Trading Release (1%): <b>' + Number(dailyAvail).toLocaleString() + ' / ' + Number(cl.dailyLimit).toLocaleString() + ' shares available today</b></div></div>'
              + '<div style="text-align:right"><div style="font-size:11px;color:var(--dim)">30% Fee Share Earned</div><b style="font-size:14px;color:var(--positive)">+' + Number(cl.feeShareEarned || 0).toLocaleString() + ' $FTR</b>'
              + '<div style="font-size:11px;color:var(--dim);margin-top:4px">Lister FP: <b style="color:var(--ink)">+' + Number(cl.listerFp || 0).toLocaleString() + ' FP</b></div></div>'
              + '</div>';
          }).join('')
        + '</div></div>';
    }
    var listerWrap = el('pfListerAllocations');
    if(!listerWrap){
      var host = el('pfRows');
      if(host && host.parentNode){
        var div = document.createElement('div');
        div.id = 'pfListerAllocations';
        host.parentNode.insertBefore(div, host);
        listerWrap = div;
      }
    }
    if(listerWrap) listerWrap.innerHTML = listerHtml;

    el('pfRows').innerHTML=shown.map(function(k){
      var h=state.holdings[k],pnl=h.shares*(h.p-h.avg),position=h.inClub&&h.inClub!=='SUB';
      return '<div class="portfolio-row"><a class="portfolio-player" href="asset.html?a='+encodeURIComponent(k)+'">'+playerPhoto(k,h.n)+'<span><b>'+esc(h.n)+'</b><small><b>'+esc(ftSym(k))+'</b> · '+fmt(h.shares)+' shares'+(h.isLister?' · <span style="color:#a596ed">Lister Allocation (1%/day trade limit)</span>':'')+(position?' · In club':'')+'</small></span></a>'
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
    Object.keys(state.holdings).forEach(function(k){var h=state.holdings[k];rows.push([ftSym(k),h.shares,h.avg,h.p,h.shares*h.p]);});
    function cell(value){var s=String(value==null?'':value);if(typeof value==='string'&&/^[=+\-@\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';}
    var url=URL.createObjectURL(new Blob([rows.map(function(row){return row.map(cell).join(',');}).join('\r\n')],{type:'text/csv;charset=utf-8'}));
    var link=document.createElement('a');link.href=url;link.download='fantrade-ledger.csv';document.body.appendChild(link);link.click();link.remove();setTimeout(function(){URL.revokeObjectURL(url);},1000);
  });
  render();window.addEventListener('fantrade:statechange',render);window.addEventListener('pageshow',render);
})();
'''
