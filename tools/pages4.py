# -*- coding: utf-8 -*-
"""Drill-down screens: one asset's market page, the trade terminal, the club
builder and the division structure. Each one is a destination reached from a
list, never a section stacked onto it."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import head, atmosphere, nav, footer, ic, JS_SHELL

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ARROW = '<span class="cap">' + ic("arrow", "ic") + '</span>'


def T(tpl, *args):
    out = tpl
    for a in args:
        out = out.replace("@@", str(a), 1)
    return out


def btn(label, cls="btn-lime", href="#", tag="a", extra=""):
    return '<%s class="btn %s" %s %s>%s%s</%s>' % (
        tag, cls, ('href="%s"' % href) if tag == "a" else "", extra, label, ARROW, tag)


def page(fname, title, body, js="", css="", app=True):
    html = (head(title, css) + atmosphere() + nav(fname, app) + body + footer() +
            "<script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)


def crumb(href, label):
    return '<a class="crumb" href="%s">%s%s</a>' % (href, ic("arrow", "ic"), label)


# Shared: read ?a= and find the asset in the ticker array from JS_SHELL.
PICK_JS = r"""
function param(k){
  var m = new RegExp('[?&]' + k + '=([^&]*)').exec(window.location.search);
  return m ? decodeURIComponent(m[1].replace(/\+/g, ' ')) : '';
}
var SYM = param('a') || '$Saka';
var A = ASSETS.filter(function(x){ return x.t.toLowerCase() === SYM.toLowerCase(); })[0] || ASSETS[0];
function fmt(n){ return Math.round(n).toLocaleString('en-US'); }
function money(n){ return n.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}); }
function held(){ return FT.getState().holdings[A.t] || null; }

// order book built deterministically around the last price
function bookRows(box, side, count){
  var out = [], px = A.p, total = 0;
  for(var i = 0; i < count; i++){
    var step = (i + 1) * (px * 0.0018);
    var p = side === 'bid' ? px - step : px + step;
    var size = Math.round(4200 + Math.abs(Math.sin((i + 1) * 2.7)) * 38000);
    total += size;
    out.push({ p: p, s: size, t: total });
  }
  var max = out[out.length - 1].t;
  document.getElementById(box).innerHTML = out.map(function(r){
    return '<div class="brow"><i style="width:' + (r.t / max * 100).toFixed(0) + '%"></i>'
      + '<span>' + r.p.toFixed(2) + '</span><span>' + fmt(r.s) + '</span></div>';
  }).join('');
}
"""

# ══════════════════════════════════════════════════════════════════
# ASSET — one player or coach's market page
# ══════════════════════════════════════════════════════════════════
asset = [T('<main><section class="app-head" style="padding-bottom:26px"><div class="wrap">'
           '<div data-reveal>@@</div>'
           '<div class="asset-head" style="margin-top:22px" data-reveal>'
           '<span class="coin" id="aCoin">@@</span>'
           '<div style="min-width:0"><div class="nm" id="aName">Bukayo Saka</div>'
           '<div class="sym"><span id="aSym">$Saka</span> · <span id="aRole">Right winger · Arsenal</span></div></div>'
           '<div class="px"><div class="v" id="aPx">48.20<small style="font-size:15px;color:var(--faint)">'
           ' $FTR</small></div><div class="d" id="aDelta">+6.4% today</div></div>'
           '</div>'
           '<div class="acts" style="margin-top:26px" data-reveal>@@@@</div>'
           '</div></section>',
           crumb("exchange.html", "All markets"), ic("boot", "ic"),
           btn("Trade this asset", href="#", extra='id="aTrade"'),
           btn("Add to club", "btn-glass", "clubs.html"))]

asset.append('<section style="padding:6px 0 130px"><div class="wrap"><div class="bento">')

# price chart
asset.append(T('<div class="bezel c8" data-reveal><div class="core pad">'
               '<div class="rowhead"><div class="k-label">Price</div>'
               '<div class="range" id="aRange" style="margin-left:auto">'
               '<button type="button" aria-pressed="true" data-r="1D">1D</button>'
               '<button type="button" aria-pressed="false" data-r="1W">1W</button>'
               '<button type="button" aria-pressed="false" data-r="1M">1M</button>'
               '<button type="button" aria-pressed="false" data-r="1Y">1Y</button>'
               '<button type="button" aria-pressed="false" data-r="All">All</button></div></div>'
               '<div class="bal-chart" id="aChart"></div>'
               '<div class="statgrid" style="margin-top:20px">'
               '<div class="mini"><div class="k">Market cap</div><div class="v" id="sCap">—</div></div>'
               '<div class="mini"><div class="k">Held by fans</div><div class="v lime" id="sHeld">—</div></div>'
               '<div class="mini"><div class="k">24h volume</div><div class="v" id="sVol">—</div></div>'
               '<div class="mini"><div class="k">Fixed supply</div><div class="v">10.00M</div></div>'
               '<div class="mini"><div class="k">52-week high</div><div class="v" id="sHigh">—</div></div>'
               '<div class="mini"><div class="k">52-week low</div><div class="v" id="sLow">—</div></div>'
               '</div></div></div>'))

# your position
asset.append(T('<div class="bezel c4" data-reveal><div class="core pad">'
               '<div class="k-label">Your position</div><div id="aPos"></div>'
               '<div class="k-label" style="margin-top:28px">Matchday value</div>'
               '<div class="b-row"><span>Season FP contributed</span><b id="aFp">—</b></div>'
               '<div class="b-row"><span>Tactical perk</span><b id="aPerk">—</b></div>'
               '<div class="b-row"><span>Eligible for</span><b>Club XI · FanPlay</b></div>'
               '<div class="b-row total"><span>Form, last five</span>'
               '<b><span class="form5" style="justify-content:flex-end"><i class="w">W</i><i class="w">W</i>'
               '<i class="d">D</i><i class="l">L</i><i class="w">W</i></span></b></div>'
               '<div style="margin-top:22px">@@</div></div></div>',
               btn("Open trade terminal", href="#",
                   extra='id="aTrade2" style="width:100%;justify-content:space-between"')))

# order book
asset.append('<div class="bezel c7" data-reveal><div class="core pad">'
             '<div class="rowhead"><div class="k-label">Order book</div>'
             '<span class="tag lime" style="margin-left:auto">Live depth</span></div>'
             '<div class="book">'
             '<div class="side bid"><div class="h"><span>Bid $FTR</span><span>Shares</span></div>'
             '<div id="aBids"></div></div>'
             '<div class="side ask"><div class="h"><span>Ask $FTR</span><span>Shares</span></div>'
             '<div id="aAsks"></div></div></div>'
             '<div class="spread" id="aSpread">—</div>'
             '<p style="font-size:11.5px;color:var(--faint);font-weight:300;margin:0;line-height:1.6">'
             'Depth is aggregated across the whole book. Market orders fill from the top down and the '
             'average fill price is shown before you confirm.</p></div></div>')

# recent trades
asset.append('<div class="bezel c5" data-reveal><div class="core pad">'
             '<div class="k-label">Recent trades</div>'
             '<div class="tr-row" style="color:var(--faint);font-size:9px;letter-spacing:.14em;'
             'text-transform:uppercase;border-bottom:1px solid var(--hair);padding-bottom:10px">'
             '<span>Price</span><span style="text-align:center">Shares</span>'
             '<span style="text-align:right">Time</span></div>'
             '<div id="aTrades"></div></div></div>')

ASSET_JS = PICK_JS + r"""
document.title = A.t + ' — Fantrade';
var el = function(id){ return document.getElementById(id); };
el('aCoin').className = 'coin' + (A.c ? ' am' : '');
el('aCoin').innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-' + (A.c ? 'whistle' : 'boot')
  + '"/></svg>';
el('aName').textContent = A.n;
el('aSym').textContent = A.t;
el('aRole').textContent = A.c ? 'Coach' : 'Player';
el('aPx').innerHTML = A.p.toFixed(2) + '<small style="font-size:15px;color:var(--faint)"> $FTR</small>';
el('aDelta').textContent = (A.d >= 0 ? '+' : '') + A.d.toFixed(1) + '% today';
el('aDelta').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
['aTrade','aTrade2'].forEach(function(i){ el(i).href = 'trade.html?a=' + encodeURIComponent(A.t); });

el('sCap').textContent = A.cap;
el('sHeld').textContent = A.h.toFixed(1) + '%';
el('sVol').textContent = fmt(A.p * 184000) ;
el('sHigh').textContent = (A.p * 1.34).toFixed(2);
el('sLow').textContent = (A.p * 0.58).toFixed(2);
el('aFp').textContent = (A.c ? 'Team outcomes' : fmt(A.p * 18) + ' FP');
el('aPerk').textContent = A.c ? '+5.0% tactical synergy' : '+9% key pass weighting';

var ASERIES = { '1D': series(30, A.d / 24, 2.4, 13), '1W': series(34, A.d / 8, 3.6, 29),
                '1M': series(40, A.d / 3, 5.4, 61), '1Y': series(48, 1.6, 7.8, 97),
                'All': series(56, 2.3, 9.4, 149) };
function apaint(r){ drawArea(el('aChart'), ASERIES[r], A.d >= 0); }
document.querySelectorAll('#aRange button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#aRange button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true');
    apaint(b.dataset.r);
  });
});
apaint('1D');

function renderPos(){
  var h = held(), box = el('aPos');
  if(!h){
    box.innerHTML = '<div class="empty-state" style="padding:26px 0">'
      + '<svg class="ic-xl" aria-hidden="true"><use href="#i-supply"/></svg>'
      + 'You do not hold ' + A.t + ' yet.</div>';
    return;
  }
  var val = h.shares * h.p, cost = h.shares * h.avg, pnl = val - cost;
  box.innerHTML = '<div class="bal-big" style="font-size:clamp(26px,2.6vw,36px)">' + fmt(val)
    + '<small> $FTR</small></div>'
    + '<div class="bal-delta' + (pnl >= 0 ? '' : ' down') + '" style="margin-bottom:16px">'
    + '<span>' + (pnl >= 0 ? '+' : '-') + fmt(Math.abs(pnl)) + ' unrealised</span></div>'
    + '<div class="b-row"><span>Shares held</span><b>' + h.shares.toLocaleString('en-US') + '</b></div>'
    + '<div class="b-row"><span>Average cost</span><b>' + h.avg.toFixed(2) + '</b></div>'
    + '<div class="b-row"><span>Share of supply</span><b>' + (h.shares / 10000000 * 100).toFixed(2) + '%</b></div>'
    + '<div class="b-row total"><span>In your club</span><b>'
    + (h.inClub && h.inClub !== 'SUB' ? h.inClub : 'Unassigned') + '</b></div>';
}
renderPos();
window.addEventListener('fantrade:statechange', renderPos);

bookRows('aBids', 'bid', 7);
bookRows('aAsks', 'ask', 7);
el('aSpread').textContent = 'Spread ' + (A.p * 0.0036).toFixed(2) + ' $FTR · '
  + (0.36).toFixed(2) + '% · mid ' + A.p.toFixed(2);

(function(){
  var out = [], t = Date.now();
  for(var i = 0; i < 9; i++){
    var up = Math.sin(i * 1.9) > 0;
    var p = A.p * (1 + (Math.sin(i * 3.1) * 0.004));
    var mins = i * 3 + 1;
    out.push('<div class="tr-row"><span style="color:' + (up ? 'var(--lime)' : 'var(--red)') + '">'
      + p.toFixed(2) + '</span><span style="text-align:center;color:var(--dim)">'
      + fmt(900 + Math.abs(Math.cos(i * 2.2)) * 7400) + '</span>'
      + '<span style="text-align:right;color:var(--faint)">' + mins + 'm ago</span></div>');
  }
  el('aTrades').innerHTML = out.join('');
})();
"""

page("asset.html", "Market — Fantrade", "".join(asset), ASSET_JS)

# ══════════════════════════════════════════════════════════════════
# TRADE — the terminal
# ══════════════════════════════════════════════════════════════════
trade = [T('<main><section class="app-head" style="padding-bottom:26px"><div class="wrap">'
           '<div data-reveal>@@</div>'
           '<div class="asset-head" style="margin-top:22px" data-reveal>'
           '<span class="coin" id="tCoin">@@</span>'
           '<div style="min-width:0"><div class="nm" id="tName">Bukayo Saka</div>'
           '<div class="sym"><span id="tSym">$Saka</span> / $FTR · spot</div></div>'
           '<div class="px"><div class="v" id="tPx">48.20</div>'
           '<div class="d" id="tDelta">+6.4% today</div></div>'
           '</div></div></section>',
           crumb("asset.html", "Market page"), ic("boot", "ic"))]

trade.append('<section style="padding:6px 0 130px"><div class="wrap"><div class="bento">')

# chart
trade.append('<div class="bezel c8" data-reveal><div class="core pad">'
             '<div class="rowhead"><div class="k-label">Last price</div>'
             '<div class="range" id="tRange" style="margin-left:auto">'
             '<button type="button" aria-pressed="true" data-r="1D">1D</button>'
             '<button type="button" aria-pressed="false" data-r="1W">1W</button>'
             '<button type="button" aria-pressed="false" data-r="1M">1M</button></div></div>'
             '<div class="bal-chart" id="tChart" style="height:210px"></div>'
             '<div class="book" style="margin-top:24px">'
             '<div class="side bid"><div class="h"><span>Bid $FTR</span><span>Shares</span></div>'
             '<div id="tBids"></div></div>'
             '<div class="side ask"><div class="h"><span>Ask $FTR</span><span>Shares</span></div>'
             '<div id="tAsks"></div></div></div>'
             '<div class="spread" id="tSpread">—</div></div></div>')

# ticket
trade.append(T('<div class="bezel c4" data-reveal><div class="core pad">'
               '<div class="sideseg" id="tSide">'
               '<button type="button" aria-pressed="true" data-s="buy">Buy</button>'
               '<button type="button" aria-pressed="false" data-s="sell">Sell</button></div>'
               '<div class="tabstrip" id="tType" style="margin-bottom:18px">'
               '<button type="button" aria-pressed="true" data-t="market">Market</button>'
               '<button type="button" aria-pressed="false" data-t="limit">Limit</button></div>'
               '<div class="tf" id="f-tLimit" hidden><label for="tLimit">Limit price ($FTR)</label>'
               '<div class="inp"><input id="tLimit" inputmode="decimal"></div>'
               '<div class="err">Enter a price above zero.</div></div>'
               '<div class="field"><label>Shares</label>'
               '<input id="tQty" value="1,000" inputmode="numeric"></div>'
               '<div class="quick"><button data-pc="25">25%</button><button data-pc="50">50%</button>'
               '<button data-pc="75">75%</button><button data-pc="100">Max</button></div>'
               '<div class="line"><span>Order value</span><b id="tSub">—</b></div>'
               '<div class="line"><span>Protocol fee (0.4%)</span><b id="tFee">—</b></div>'
               '<div class="line"><span id="tTotLabel">Total cost</span><b id="tTot">—</b></div>'
               '<div class="line"><span id="tAvailLabel">Available</span><b id="tAvail">—</b></div>'
               '@@'
               '<p style="font-size:11.5px;color:var(--faint);font-weight:300;margin-top:16px;line-height:1.6">'
               'Market orders fill against the book shown on the left. Settled shares land in your wallet '
               'immediately and become eligible for your club and for FanPlay.</p>'
               '</div></div>',
               btn("Place order", tag="button",
                   extra='id="tGo" style="width:100%;justify-content:space-between;margin-top:18px"')))

# open orders / history
trade.append('<div class="bezel c12" data-reveal><div class="core">'
             '<div style="padding:26px 24px 14px"><div class="tabstrip" id="tLedgerTabs" '
             'style="width:max-content;max-width:100%">'
             '<button type="button" aria-pressed="true" data-l="open">Open orders</button>'
             '<button type="button" aria-pressed="false" data-l="fills">Your fills</button>'
             '</div></div>'
             '<div id="tLedger"></div></div></div>')

trade.append('</div></div></section></main>')

TRADE_JS = PICK_JS + r"""
document.title = 'Trade ' + A.t + ' — Fantrade';
var el = function(id){ return document.getElementById(id); };
var side = 'buy', otype = 'market', view = 'open';

document.querySelector('.crumb').href = 'asset.html?a=' + encodeURIComponent(A.t);
el('tCoin').className = 'coin' + (A.c ? ' am' : '');
el('tCoin').innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-' + (A.c ? 'whistle' : 'boot')
  + '"/></svg>';
el('tName').textContent = A.n;
el('tSym').textContent = A.t;
el('tPx').textContent = A.p.toFixed(2);
el('tDelta').textContent = (A.d >= 0 ? '+' : '') + A.d.toFixed(1) + '% today';
el('tDelta').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('tLimit').value = A.p.toFixed(2);

var TSERIES = { '1D': series(34, A.d / 24, 2.4, 13), '1W': series(40, A.d / 8, 3.6, 29),
                '1M': series(46, A.d / 3, 5.4, 61) };
function tpaint(r){ drawArea(el('tChart'), TSERIES[r], A.d >= 0); }
document.querySelectorAll('#tRange button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#tRange button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true'); tpaint(b.dataset.r);
  });
});
tpaint('1D');
bookRows('tBids', 'bid', 9);
bookRows('tAsks', 'ask', 9);
el('tSpread').textContent = 'Spread ' + (A.p * 0.0036).toFixed(2) + ' $FTR · mid ' + A.p.toFixed(2);

function num(v){ return parseInt(String(v).replace(/[^0-9]/g, ''), 10) || 0; }
function price(){ return otype === 'limit' ? (parseFloat(el('tLimit').value) || A.p) : A.p; }

function calc(){
  var q = num(el('tQty').value), px = price(), sub = q * px, fee = sub * 0.004;
  var s = FT.getState(), h = held();
  el('tSub').textContent = fmt(sub) + ' $FTR';
  el('tFee').textContent = fmt(fee) + ' $FTR';
  el('tTotLabel').textContent = side === 'buy' ? 'Total cost' : 'You receive';
  el('tTot').textContent = fmt(side === 'buy' ? sub + fee : sub - fee) + ' $FTR';
  el('tAvailLabel').textContent = side === 'buy' ? 'Available $FTR' : 'Shares held';
  el('tAvail').textContent = side === 'buy'
    ? fmt(s.wallet.balance) + ' $FTR'
    : (h ? h.shares.toLocaleString('en-US') + ' ' + A.t : '0 ' + A.t);
  var go = el('tGo');
  go.childNodes[0].nodeValue = (side === 'buy' ? 'Buy ' : 'Sell ') + A.t;
  go.className = 'btn ' + (side === 'buy' ? 'btn-lime' : 'btn-red');
}
el('tQty').addEventListener('input', calc);
el('tLimit').addEventListener('input', calc);

document.querySelectorAll('#tSide button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#tSide button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true'); side = b.dataset.s; calc();
  });
});
document.querySelectorAll('#tType button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#tType button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true');
    otype = b.dataset.t;
    el('f-tLimit').hidden = otype !== 'limit';
    calc();
  });
});
document.querySelectorAll('[data-pc]').forEach(function(b){
  b.addEventListener('click', function(){
    var pc = +b.dataset.pc / 100, s = FT.getState(), h = held(), q;
    if(side === 'buy') q = Math.floor(s.wallet.balance * pc / (price() * 1.004));
    else q = Math.floor((h ? h.shares : 0) * pc);
    el('tQty').value = q.toLocaleString('en-US');
    calc();
  });
});

el('tGo').addEventListener('click', function(){
  var q = num(el('tQty').value);
  if(q < 1){ showToast('Enter how many shares to trade.', 'error'); return; }
  if(otype === 'limit' && !(parseFloat(el('tLimit').value) > 0)){
    document.getElementById('f-tLimit').classList.add('bad'); return;
  }
  if(otype === 'limit'){
    showToast('Limit order for ' + q.toLocaleString('en-US') + ' ' + A.t + ' at '
      + price().toFixed(2) + ' placed.', 'success');
    OPEN.unshift({ side: side, q: q, px: price(), t: 'Just now' });
    renderLedger();
    return;
  }
  try {
    var r = FT.executeTrade(side, A.t, A.n, q, A.p, A.c);
    showToast((side === 'buy' ? 'Bought ' : 'Sold ') + q.toLocaleString('en-US') + ' ' + A.t
      + ' for ' + r.total.toLocaleString('en-US') + ' $FTR.', 'success');
    calc(); renderLedger();
  } catch(e){ showToast(e.message, 'error'); }
});

var OPEN = [{ side:'buy', q:2000, px:A.p * 0.94, t:'Today, 09:12' },
            { side:'sell', q:1500, px:A.p * 1.08, t:'Yesterday, 18:40' }];
function renderLedger(){
  var box = el('tLedger'), s = FT.getState();
  var cols = 'grid-template-columns:90px 1fr 1fr 1fr 110px';
  if(view === 'open'){
    if(!OPEN.length){
      box.innerHTML = '<div class="empty-state"><svg class="ic-xl" aria-hidden="true">'
        + '<use href="#i-receipt"/></svg>No open orders on this market.</div>';
      return;
    }
    box.innerHTML = '<div class="dh" style="' + cols + '"><span>Side</span><span>Shares</span>'
      + '<span>Limit price</span><span>Placed</span><span style="text-align:right">Action</span></div>'
      + OPEN.map(function(o, i){
        return '<div class="dr" style="' + cols + '">'
          + '<div><span class="tag ' + (o.side === 'buy' ? 'lime' : 'red') + '">' + o.side + '</span></div>'
          + '<div class="num" style="font-size:13px">' + o.q.toLocaleString('en-US') + '</div>'
          + '<div class="num" style="font-size:13px">' + o.px.toFixed(2) + '</div>'
          + '<div style="color:var(--dim);font-size:12.5px">' + o.t + '</div>'
          + '<div style="text-align:right"><button class="tradebtn" data-cancel="' + i + '" '
          + 'style="width:auto;padding:7px 14px">Cancel</button></div></div>';
      }).join('');
    box.querySelectorAll('[data-cancel]').forEach(function(b){
      b.addEventListener('click', function(){
        OPEN.splice(+b.dataset.cancel, 1);
        renderLedger();
        showToast('Order cancelled. Nothing was charged.', 'info');
      });
    });
    return;
  }
  var fills = s.transactions.filter(function(t){
    return (t.type === 'BUY' || t.type === 'SELL') && t.asset === A.t;
  });
  if(!fills.length){
    box.innerHTML = '<div class="empty-state"><svg class="ic-xl" aria-hidden="true">'
      + '<use href="#i-candle"/></svg>No fills on ' + A.t + ' yet.</div>';
    return;
  }
  box.innerHTML = '<div class="dh" style="' + cols + '"><span>Side</span><span>Shares</span>'
    + '<span>Price</span><span>When</span><span style="text-align:right">$FTR</span></div>'
    + fills.map(function(t){
      var down = t.type === 'BUY';
      return '<div class="dr" style="' + cols + '">'
        + '<div><span class="tag ' + (down ? 'lime' : 'red') + '">' + t.type + '</span></div>'
        + '<div class="num" style="font-size:13px">' + t.shares.toLocaleString('en-US') + '</div>'
        + '<div class="num" style="font-size:13px">' + t.price.toFixed(2) + '</div>'
        + '<div style="color:var(--dim);font-size:12.5px">' + t.time + '</div>'
        + '<div class="pl ' + (down ? 'down' : 'up') + '" style="text-align:right">'
        + (down ? '-' : '+') + fmt(t.total) + '</div></div>';
    }).join('');
}
document.querySelectorAll('#tLedgerTabs button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#tLedgerTabs button').forEach(function(x){
      x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true'); view = b.dataset.l; renderLedger();
  });
});
calc(); renderLedger();
window.addEventListener('fantrade:statechange', function(){ calc(); renderLedger(); });
"""

page("trade.html", "Trade — Fantrade", "".join(trade), TRADE_JS)

print("built asset.html + trade.html")

# ══════════════════════════════════════════════════════════════════
# DIVISIONS — the tier structure behind the league table
# ══════════════════════════════════════════════════════════════════
IDX = [104, 109, 113, 118, 122, 129, 134, 138, 145, 148]


def idx_chart(vals, w=620, h=180):
    lo, hi = min(vals) - 6, max(vals) + 6
    rng = hi - lo
    pa, pb = [], []
    for i, v in enumerate(vals):
        x = i * (w / (len(vals) - 1))
        pa.append("%.1f,%.1f" % (x, h - ((v - lo) / rng) * h))
        pb.append("%.1f,%.1f" % (x, h - ((v * 0.86 - lo) / rng) * h))
    return ('<svg viewBox="0 0 %d %d" preserveAspectRatio="none">'
            '<defs><linearGradient id="dvg" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%%" stop-color="#C4F82A" stop-opacity=".22"/>'
            '<stop offset="100%%" stop-color="#C4F82A" stop-opacity="0"/></linearGradient></defs>'
            '<polygon points="0,%d %s %d,%d" fill="url(#dvg)"/>'
            '<polyline points="%s" fill="none" stroke="#4DA6FF" stroke-width="1.4" '
            'stroke-dasharray="4 4" opacity=".8"/>'
            '<polyline points="%s" fill="none" stroke="#C4F82A" stroke-width="1.8" stroke-linejoin="round"/>'
            '</svg>' % (w, h, h, " ".join(pa), w, h, " ".join(pb), " ".join(pa)))


dv = [T('<main><section class="app-head" style="padding-bottom:26px"><div class="wrap">'
        '<div data-reveal>@@</div>'
        '<span class="pill" style="margin-top:20px" data-reveal>@@ Competition structure</span>'
        '<h1 data-reveal>Divisions<br>&amp; promotion</h1>'
        '<p class="lede" data-reveal>Clubs move between tiers at the end of each four-week cycle on '
        'accumulated points. Value does not promote you — points do.</p>'
        '</div></section>',
        crumb("leaderboard.html", "Back to the table"), ic("layers", "ic"))]

dv.append('<section style="padding:6px 0 130px"><div class="wrap"><div class="bento">')

dv.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
            '<div class="k-label">The three tiers</div>'
            '<div class="div-card"><span class="dot" style="background:#C4F82A"></span>'
            '<div><b>Apex · Tier 1</b><span class="r">Ranks 1–150 worldwide. Your club is here.</span></div>'
            '<div class="pp"><em>50%</em><span>Prize pool</span></div></div>'
            '<div class="div-card"><span class="dot" style="background:#4DA6FF"></span>'
            '<div><b>Contender · Tier 2</b><span class="r">Ranks 151–500. Relegation zone below 450.</span></div>'
            '<div class="pp"><em>30%</em><span>Prize pool</span></div></div>'
            '<div class="div-card"><span class="dot" style="background:rgba(255,255,255,.34)"></span>'
            '<div><b>Challenger &amp; Rising Star</b><span class="r">Ranks 501+ and academy formations.</span></div>'
            '<div class="pp"><em>20%</em><span>Prize pool</span></div></div>'
            '<div class="b-row" style="margin-top:22px"><span>Cycle ends</span>'
            '<b>Gameweek 30 · 28 Sep</b></div>'
            '<div class="b-row"><span>Your standing</span><b style="color:var(--lime)">Safe in Apex</b></div>'
            '<div class="b-row total"><span>Points to the next tier up</span><b>—</b></div>'
            '<div style="margin-top:20px">@@</div>'
            '</div></div>',
            btn("Back to the table", "btn-glass", "leaderboard.html",
                extra='style="width:100%;justify-content:space-between"')))

dv.append(T('<div class="bezel c7" data-reveal><div class="core pad">'
            '<div class="rowhead"><div class="k-label">Syndicate portfolio index</div>'
            '<span class="tag lime" style="margin-left:auto">▲ 28.4% since GW24</span></div>'
            '<div style="height:180px">@@</div>'
            '<div class="chart-x" style="margin-top:12px"><span>GW24</span><span>GW25</span><span>GW26</span>'
            '<span>GW27</span><span>GW28</span></div>'
            '<div class="statgrid" style="margin-top:22px">'
            '<div class="mini"><div class="k">Mean club</div><div class="v">148.6K</div></div>'
            '<div class="mini"><div class="k">Median club</div><div class="v">92.4K</div></div>'
            '<div class="mini"><div class="k">New clubs</div><div class="v lime">+48</div></div>'
            '</div>'
            '<p style="font-size:11.5px;color:var(--faint);font-weight:300;margin-top:18px;line-height:1.6">'
            'Solid line is the index. Dashed line is the same basket without coach equities — the gap is what '
            'tactical synergy has been worth over the cycle.</p>'
            '</div></div>', idx_chart(IDX)))

dv.append(T('<div class="bezel c12" data-reveal><div class="core pad">'
            '<div class="k-label">How the table is built</div>'
            '<div class="statgrid" style="grid-template-columns:repeat(4,minmax(0,1fr));margin-top:6px">'
            '<div class="mini"><div class="k">01 · Raw performance</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:10px 0 0;line-height:1.6">'
            'Every eligible appearance by an asset you own scores against the published rules — goals, '
            'assists, clean sheets, duels, defensive actions.</p></div>'
            '<div class="mini"><div class="k">02 · Captain weighting</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:10px 0 0;line-height:1.6">'
            'The armband multiplies one player\'s return by 1.5x. Choosing it is the single biggest weekly '
            'decision most managers get wrong.</p></div>'
            '<div class="mini"><div class="k">03 · Squad synergy</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:10px 0 0;line-height:1.6">'
            'A full eleven in natural positions, teammate links and a coach whose real shape matches yours '
            'compound into the club multiplier.</p></div>'
            '<div class="mini"><div class="k">04 · Settlement</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:10px 0 0;line-height:1.6">'
            'Points convert to $FTR at the tier rate you staked at. Top-150 clubs are paid first, on the '
            'last final whistle of the window.</p></div></div>'
            '<div style="display:flex;gap:10px;margin-top:22px;flex-wrap:wrap">@@@@</div>'
            '</div></div>',
            btn("Read the scoring rules", "btn-glass", "how-it-works.html#rules"),
            btn("Improve your synergy", href="clubs.html")))

dv.append('</div></div></section></main>')

page("divisions.html", "Divisions — Fantrade", "".join(dv), "", """
.chart-x{display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:10px;
  color:var(--faint);margin-top:10px}
.div-card{border:1px solid var(--hair);background:rgba(255,255,255,.03);border-radius:18px;padding:20px;
  box-shadow:var(--inset);display:flex;gap:16px;align-items:flex-start;margin-bottom:10px}
.div-card .dot{width:9px;height:9px;border-radius:99px;flex:none;margin-top:6px}
.div-card b{display:block;font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 800;
  text-transform:uppercase;font-size:14px;margin-bottom:4px}
.div-card .r{font-size:11.5px;color:var(--faint);font-weight:300}
.div-card .pp{margin-left:auto;text-align:right;flex:none}
.div-card .pp em{font-style:normal;font-family:'JetBrains Mono',monospace;font-size:15px;color:var(--lime)}
.div-card .pp span{display:block;font-weight:600;font-size:8.5px;letter-spacing:.14em;color:var(--faint);
  text-transform:uppercase;margin-top:5px}
""")

print("built divisions.html")
