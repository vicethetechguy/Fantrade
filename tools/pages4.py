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
    html = (head(title, css, "app" if app else "") + atmosphere() + nav(fname, app) + body + footer() +
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

// Order book, built deterministically around the last price so the same
// asset always shows the same depth. Asks render top-down (worst first),
// bids top-down (best first), the way a real book reads.
function book2(box, side, count, onPick){
  var rows = [], px = A.p, total = 0;
  for(var i = 0; i < count; i++){
    var step = (i + 1) * (px * 0.0016);
    var p = side === 'bid' ? px - step : px + step;
    var size = Math.round(3100 + Math.abs(Math.sin((i + 1) * 2.7)) * 41000);
    total += size;
    rows.push({ p: p, s: size, t: total });
  }
  var max = rows[rows.length - 1].t;
  if(side === 'ask') rows.reverse();
  var host = document.getElementById(box);
  host.innerHTML = rows.map(function(r){
    return '<div class="b2row ' + side + '" data-px="' + r.p.toFixed(2) + '">'
      + '<i style="width:' + (r.t / max * 100).toFixed(0) + '%"></i>'
      + '<span>' + r.p.toFixed(2) + '</span><span>' + fmt(r.s) + '</span></div>';
  }).join('');
  if(onPick) host.querySelectorAll('.b2row').forEach(function(el){
    el.addEventListener('click', function(){ onPick(parseFloat(el.dataset.px)); });
  });
}
"""

# ══════════════════════════════════════════════════════════════════
# ASSET — one player or coach's market page
# ══════════════════════════════════════════════════════════════════
asset = [T('<main><section class="app-head" style="padding:92px 0 10px"><div class="wrap">'
           '<div class="asset-head" data-reveal>'
           '<a class="crumb" href="exchange.html" aria-label="All markets">@@</a>'
           '<span class="coin" id="aCoin">@@</span>'
           '<div style="min-width:0"><div class="nm" id="aName">Bukayo Saka</div>'
           '<div class="sym"><span id="aSym">$Saka</span> · <span id="aRole">Player</span></div></div>'
           '<span style="margin-left:auto;display:flex;gap:8px">'
           '<button class="bell" type="button" id="aFav" aria-pressed="false" '
           'aria-label="Add to favourites" style="border-radius:11px">@@</button></span>'
           '</div></div></section>',
           ic("arrow", "ic"), ic("boot", "ic"), ic("star", "ic"))]

asset.append('<section style="padding:0 0 120px"><div class="wrap">')

# ── price header + candles ──
asset.append('<div class="bezel" data-reveal><div class="core pad">'
             '<div style="display:flex;gap:22px;flex-wrap:wrap;align-items:flex-start">'
             '<div><div class="bal-big" id="aPx" style="margin:0;color:var(--lime)">48.20</div>'
             '<div class="bal-delta" id="aDelta" style="margin-top:7px"><span>+6.4% today</span>'
             '<em id="aGbp">≈ £3.89</em></div></div>'
             '<div class="statgrid" style="margin-left:auto;grid-template-columns:repeat(2,minmax(0,1fr));'
             'gap:6px 22px;min-width:240px">'
             '<div class="b-row" style="padding:3px 0"><span>24h high</span><b id="sHigh">—</b></div>'
             '<div class="b-row" style="padding:3px 0"><span>24h low</span><b id="sLow">—</b></div>'
             '<div class="b-row" style="padding:3px 0"><span>24h vol (shares)</span><b id="sVolS">—</b></div>'
             '<div class="b-row" style="padding:3px 0"><span>24h vol ($FTR)</span><b id="sVol">—</b></div>'
             '</div></div>'
             '<div class="utabs sm" id="aTf" style="margin-top:16px;border-bottom:0;gap:18px">'
             '<button type="button" aria-pressed="false" data-t="15m">15m</button>'
             '<button type="button" aria-pressed="true" data-t="1h">1h</button>'
             '<button type="button" aria-pressed="false" data-t="8h">8h</button>'
             '<button type="button" aria-pressed="false" data-t="1D">1D</button>'
             '<button type="button" aria-pressed="false" data-t="1W">1W</button></div>'
             '<div class="ohlc" id="aOhlc" style="margin-top:10px"></div>'
             '<div class="candles" id="aChart"></div>'
             '<div class="cx" id="aCx"></div>'
             '<div class="stickybar"><a class="buy" id="aBuy" href="#">Buy</a>'
             '<a class="sell" id="aSell" href="#">Sell</a></div>'
             '</div></div>')

# ── book / trades / stats ──
asset.append('<div class="bezel" style="margin-top:10px" data-reveal><div class="core">'
             '<div style="padding:16px 16px 0"><div class="utabs" id="aPanes">'
             '<button type="button" aria-pressed="true" data-p="book">Order book</button>'
             '<button type="button" aria-pressed="false" data-p="trades">Trade history</button>'
             '<button type="button" aria-pressed="false" data-p="stats">Coin info</button>'
             '<button type="button" aria-pressed="false" data-p="pos">Your position</button>'
             '</div></div>'
             '<div class="pad">'
             '<div class="pane on" data-pane="book">'
             '<div class="book2"><div class="bh"><span>Price $FTR</span><span>Shares</span></div>'
             '<div id="aAsks"></div>'
             '<div class="last"><b id="aLast">—</b><span id="aLastSub">last traded</span></div>'
             '<div id="aBids"></div>'
             '<div class="depthbar"><i id="dBid" style="width:58%;background:var(--lime)"></i>'
             '<i id="dAsk" style="width:42%;background:var(--red)"></i></div>'
             '<div class="depthkey"><span style="color:var(--lime)" id="dBidK">B 58%</span>'
             '<span style="color:var(--red)" id="dAskK">42% S</span></div></div></div>'
             '<div class="pane" data-pane="trades">'
             '<div class="tr-row" style="color:var(--faint);font-size:8.5px;letter-spacing:.13em;'
             'text-transform:uppercase;border-bottom:1px solid var(--hair);padding-bottom:8px">'
             '<span>Price</span><span style="text-align:center">Shares</span>'
             '<span style="text-align:right">Time</span></div><div id="aTrades"></div></div>'
             '<div class="pane" data-pane="stats">'
             '<div class="statgrid">'
             '<div class="mini"><div class="k">Market cap</div><div class="v" id="sCap">—</div></div>'
             '<div class="mini"><div class="k">Held by fans</div><div class="v lime" id="sHeld">—</div></div>'
             '<div class="mini"><div class="k">Fixed supply</div><div class="v">10.00M</div></div>'
             '<div class="mini"><div class="k">52w high</div><div class="v" id="sYH">—</div></div>'
             '<div class="mini"><div class="k">52w low</div><div class="v" id="sYL">—</div></div>'
             '<div class="mini"><div class="k">Holders</div><div class="v" id="sHolders">—</div></div>'
             '</div>'
             '<div class="b-row" style="margin-top:14px"><span>Season FP contributed</span>'
             '<b id="aFp">—</b></div>'
             '<div class="b-row"><span>Tactical perk</span><b id="aPerk">—</b></div>'
             '<div class="b-row"><span>Eligible for</span><b>Club XI · FanPlay</b></div>'
             '<div class="b-row total"><span>Form, last five</span>'
             '<b><span class="form5" style="justify-content:flex-end"><i class="w">W</i><i class="w">W</i>'
             '<i class="d">D</i><i class="l">L</i><i class="w">W</i></span></b></div></div>'
             '<div class="pane" data-pane="pos"><div id="aPos"></div></div>'
             '</div></div></div>')

asset.append('</div></section></main>')

ASSET_JS = PICK_JS + r"""
document.title = A.t + ' — Fantrade';
var el = function(id){ return document.getElementById(id); };
el('aCoin').className = 'coin' + (A.c ? ' am' : '');
el('aCoin').innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-' + (A.c ? 'whistle' : 'boot')
  + '"/></svg>';
el('aName').textContent = A.n;
el('aSym').textContent = A.t;
el('aRole').textContent = A.c ? 'Coach equity' : 'Player share';
el('aPx').textContent = A.p.toFixed(2);
el('aPx').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('aDelta').className = 'bal-delta' + (A.d >= 0 ? '' : ' down');
el('aDelta').querySelector('span').textContent = (A.d >= 0 ? '+' : '') + A.d.toFixed(2) + '% today';
el('aGbp').textContent = '≈ £' + (A.p / 12.4).toFixed(2);
['aBuy','aSell'].forEach(function(i, n){
  el(i).href = 'trade.html?a=' + encodeURIComponent(A.t) + '&side=' + (n ? 'sell' : 'buy');
});

el('sHigh').textContent = (A.p * 1.021).toFixed(2);
el('sLow').textContent = (A.p * 0.968).toFixed(2);
el('sVolS').textContent = fmt(384440);
el('sVol').textContent = A.cap;
el('sCap').textContent = A.cap;
el('sHeld').textContent = A.h.toFixed(1) + '%';
el('sYH').textContent = (A.p * 1.34).toFixed(2);
el('sYL').textContent = (A.p * 0.58).toFixed(2);
el('sHolders').textContent = fmt(Math.round(A.h * 1840));
el('aFp').textContent = A.c ? 'Team outcomes' : fmt(A.p * 18) + ' FP';
el('aPerk').textContent = A.c ? '+5.0% tactical synergy' : '+9% key pass weighting';

// ── candles ──
var TF = { '15m': [46, 0.010, 7], '1h': [46, 0.018, 23], '8h': [46, 0.030, 51],
           '1D': [46, 0.046, 89], '1W': [46, 0.072, 131] };
var LABELS = { '15m': ['16:00','19:15','22:30','01:45'], '1h': ['09-12','09-13','09-14','09-15'],
               '8h': ['Aug 28','Sep 03','Sep 09','Sep 15'], '1D': ['Jun','Jul','Aug','Sep'],
               '1W': ['Q4 25','Q1 26','Q2 26','Q3 26'] };
function tf(t){
  var cfg = TF[t], data = candleData(cfg[0], A.p * 0.94, cfg[1], cfg[2]);
  // land the series on the live price so the header and the chart agree
  var drift = A.p / data[data.length - 1].c;
  data.forEach(function(d){ d.o *= drift; d.h *= drift; d.l *= drift; d.c *= drift; });
  var last = drawCandles(el('aChart'), data);
  el('aCx').innerHTML = LABELS[t].map(function(l){ return '<span>' + l + '</span>'; }).join('');
  el('aOhlc').innerHTML = ['O', 'H', 'L', 'C'].map(function(k, i){
    var v = [last.o, last.h, last.l, last.c][i];
    return '<span>' + k + '<b style="color:' + (last.c >= last.o ? 'var(--lime)' : 'var(--red)') + '">'
      + v.toFixed(2) + '</b></span>';
  }).join('') + '<span>Vol<b>' + fmt(384440) + '</b></span>';
}
document.querySelectorAll('#aTf button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#aTf button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true'); tf(b.dataset.t);
  });
});
tf('1h');

// ── panes ──
document.querySelectorAll('#aPanes button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#aPanes button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true');
    document.querySelectorAll('[data-pane]').forEach(function(p){
      p.classList.toggle('on', p.dataset.pane === b.dataset.p);
    });
  });
});

book2('aAsks', 'ask', 7);
book2('aBids', 'bid', 7);
el('aLast').textContent = A.p.toFixed(2);
el('aLast').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('aLastSub').textContent = '≈ £' + (A.p / 12.4).toFixed(2) + ' · last traded';
(function(){
  var bidPct = Math.round(48 + A.d);
  bidPct = Math.max(12, Math.min(88, bidPct));
  el('dBid').style.width = bidPct + '%';
  el('dAsk').style.width = (100 - bidPct) + '%';
  el('dBidK').textContent = 'B ' + bidPct + '%';
  el('dAskK').textContent = (100 - bidPct) + '% S';
})();

(function(){
  var out = [];
  for(var i = 0; i < 12; i++){
    var up = Math.sin(i * 1.9) > 0;
    var p = A.p * (1 + (Math.sin(i * 3.1) * 0.004));
    out.push('<div class="tr-row"><span style="color:' + (up ? 'var(--lime)' : 'var(--red)') + '">'
      + p.toFixed(2) + '</span><span style="text-align:center;color:var(--dim)">'
      + fmt(900 + Math.abs(Math.cos(i * 2.2)) * 7400) + '</span>'
      + '<span style="text-align:right;color:var(--faint)">' + (i * 3 + 1) + 'm ago</span></div>');
  }
  el('aTrades').innerHTML = out.join('');
})();

function renderPos(){
  var h = held(), box = el('aPos');
  if(!h){
    box.innerHTML = '<div class="empty-state">'
      + '<svg class="ic-xl" aria-hidden="true"><use href="#i-supply"/></svg>'
      + 'You do not hold ' + A.t + ' yet. Buy some to field it in your club.</div>';
    return;
  }
  var val = h.shares * h.p, cost = h.shares * h.avg, pnl = val - cost;
  box.innerHTML = '<div class="bal-big" style="font-size:24px">' + fmt(val) + '<small> $FTR</small></div>'
    + '<div class="bal-delta' + (pnl >= 0 ? '' : ' down') + '" style="margin-bottom:12px">'
    + '<span>' + (pnl >= 0 ? '+' : '-') + fmt(Math.abs(pnl)) + ' unrealised</span></div>'
    + '<div class="b-row"><span>Shares held</span><b>' + h.shares.toLocaleString('en-US') + '</b></div>'
    + '<div class="b-row"><span>Average cost</span><b>' + h.avg.toFixed(2) + '</b></div>'
    + '<div class="b-row"><span>Share of supply</span><b>' + (h.shares / 10000000 * 100).toFixed(2) + '%</b></div>'
    + '<div class="b-row total"><span>In your club</span><b>'
    + (h.inClub && h.inClub !== 'SUB' ? h.inClub : 'Unassigned') + '</b></div>';
}
renderPos();
window.addEventListener('fantrade:statechange', renderPos);

var fav = el('aFav');
fav.setAttribute('aria-pressed', FT.isFav(A.t) ? 'true' : 'false');
fav.style.color = FT.isFav(A.t) ? 'var(--lime)' : '';
fav.addEventListener('click', function(){
  var on = FT.toggleFav(A.t);
  fav.setAttribute('aria-pressed', on ? 'true' : 'false');
  fav.style.color = on ? 'var(--lime)' : '';
  showToast(on ? A.t + ' added to favourites.' : A.t + ' removed from favourites.',
    on ? 'success' : 'info');
});
"""

page("asset.html", "Market — Fantrade", "".join(asset), ASSET_JS)

# ══════════════════════════════════════════════════════════════════
# TRADE — the terminal: bid, buy, sell, swap
# ══════════════════════════════════════════════════════════════════
trade = [T('<main><section class="app-head" style="padding:92px 0 10px"><div class="wrap">'
           '<div class="asset-head" data-reveal>'
           '<a class="crumb" href="asset.html" id="tBack" aria-label="Market page">@@</a>'
           '<span class="coin" id="tCoin">@@</span>'
           '<div style="min-width:0"><div class="nm" id="tName" style="font-size:clamp(17px,2vw,22px)">'
           'Bukayo Saka</div>'
           '<div class="sym"><span id="tSym">$Saka</span> / $FTR</div></div>'
           '<div style="margin-left:auto;text-align:right">'
           '<div class="num" id="tPx" style="font-size:18px">48.20</div>'
           '<div class="num" id="tDelta" style="font-size:11px;margin-top:4px">+6.40%</div></div>'
           '</div></div></section>',
           ic("arrow", "ic"), ic("boot", "ic"))]

trade.append('<section style="padding:0 0 120px"><div class="wrap"><div class="bento">')

# ── book ──
trade.append('<div class="bezel c5" data-reveal><div class="core pad">'
             '<div class="book2"><div class="bh"><span>Price $FTR</span><span>Shares</span></div>'
             '<div id="tAsks"></div>'
             '<div class="last"><b id="tLast">—</b><span id="tLastSub">last traded</span></div>'
             '<div id="tBids"></div>'
             '<div class="depthbar"><i id="tdBid" style="width:58%;background:var(--lime)"></i>'
             '<i id="tdAsk" style="width:42%;background:var(--red)"></i></div>'
             '<div class="depthkey"><span style="color:var(--lime)" id="tdBidK">B 58%</span>'
             '<span style="color:var(--red)" id="tdAskK">42% S</span></div></div>'
             '<p style="font-size:10.5px;color:var(--faint);font-weight:300;margin:14px 0 0;line-height:1.55">'
             'Tap any row to load that price into the ticket. A limit order that does not fill immediately '
             'rests on the book as your bid or ask until it does.</p>'
             '</div></div>')

# ── ticket ──
trade.append(T('<div class="bezel c7" data-reveal><div class="core pad">'
               '<div class="utabs" id="tMode" style="margin-bottom:16px">'
               '<button type="button" aria-pressed="true" data-m="buy">Buy</button>'
               '<button type="button" aria-pressed="false" data-m="sell">Sell</button>'
               '<button type="button" aria-pressed="false" data-m="swap">Swap</button>'
               '</div>'

               # buy / sell ticket
               '<div class="pane on" data-pane="order">'
               '<button class="otype" type="button" id="tTypeWrap">@@'
               '<select id="tType"><option value="limit">Limit</option>'
               '<option value="market">Market</option>'
               '<option value="stop">Stop-limit</option></select>'
               '<span class="chev"></span></button>'
               '<div class="stp" id="tStopWrap" hidden><span class="lbl">Stop ($FTR)</span>'
               '<button type="button" data-step="-1" data-for="tStop" aria-label="Lower">&minus;</button>'
               '<input id="tStop" inputmode="decimal">'
               '<button type="button" data-step="1" data-for="tStop" aria-label="Raise">+</button></div>'
               '<div class="stp" id="tLimitWrap"><span class="lbl">Limit ($FTR)</span>'
               '<button type="button" data-step="-1" data-for="tLimit" aria-label="Lower">&minus;</button>'
               '<input id="tLimit" inputmode="decimal">'
               '<button type="button" data-step="1" data-for="tLimit" aria-label="Raise">+</button></div>'
               '<div class="stp"><span class="lbl">Shares</span>'
               '<button type="button" data-step="-1" data-for="tQty" aria-label="Fewer">&minus;</button>'
               '<input id="tQty" inputmode="numeric" value="1,000">'
               '<button type="button" data-step="1" data-for="tQty" aria-label="More">+</button></div>'
               '<div class="slider" id="tSlider">'
               '<span class="track"></span><span class="fill" id="tFill"></span>'
               '<span class="notch" style="left:0"></span><span class="notch" style="left:25%"></span>'
               '<span class="notch" style="left:50%"></span><span class="notch" style="left:75%"></span>'
               '<span class="notch" style="left:100%"></span>'
               '<span class="knob" id="tKnob" style="left:0"></span>'
               '<input type="range" id="tRange" min="0" max="100" step="1" value="0" '
               'aria-label="Percentage of balance">'
               '<span class="pcts"><span>0%</span><span>25%</span><span>50%</span><span>75%</span>'
               '<span>100%</span></span></div>'
               '<div class="stp" style="margin-top:18px"><span class="lbl">Order value</span>'
               '<input id="tAmt" readonly></div>'
               '<div class="line"><span>Protocol fee (0.4%)</span><b id="tFee">—</b></div>'
               '<div class="line"><span id="tTotLabel">Total cost</span><b id="tTot">—</b></div>'
               '<div class="line"><span id="tAvailLabel">Available</span><b id="tAvail">—</b></div>'
               '@@'
               '<p style="font-size:10.5px;color:var(--faint);font-weight:300;margin-top:12px;line-height:1.55" '
               'id="tHint">A limit buy below the market rests as your bid until someone sells into it.</p>'
               '</div>'

               # swap
               '<div class="pane" data-pane="swap">'
               '<div class="tf" id="f-swFrom"><label for="swFrom">From</label><div class="inp">@@'
               '<select id="swFrom"></select><span class="chev"></span></div>'
               '<div class="hint" id="swHold">—</div></div>'
               '<div class="stp"><span class="lbl">Shares</span>'
               '<button type="button" data-step="-1" data-for="swQty" aria-label="Fewer">&minus;</button>'
               '<input id="swQty" inputmode="numeric" value="500">'
               '<button type="button" data-step="1" data-for="swQty" aria-label="More">+</button></div>'
               '<div class="tf" style="margin-top:12px"><label for="swTo">To</label><div class="inp">@@'
               '<select id="swTo"></select><span class="chev"></span></div></div>'
               '<div class="line"><span>You give</span><b id="swGive">—</b></div>'
               '<div class="line"><span>Swap fee (0.4%)</span><b id="swFee">—</b></div>'
               '<div class="line"><span>You receive</span><b id="swGet">—</b></div>'
               '<div class="line"><span>Dust back to wallet</span><b id="swDust">—</b></div>'
               '@@'
               '<p style="font-size:10.5px;color:var(--faint);font-weight:300;margin-top:12px;line-height:1.55">'
               'A swap sells one asset and buys the other in a single settlement, so you are never '
               'uncovered between the two legs.</p>'
               '</div>'
               '</div></div>',
               ic("candle", "ic"),
               btn("Place order", tag="button",
                   extra='id="tGo" style="width:100%;justify-content:space-between;margin-top:14px"'),
               ic("swap", "ic"), ic("target", "ic"),
               btn("Swap assets", tag="button",
                   extra='id="swGo" style="width:100%;justify-content:space-between;margin-top:14px"')))

# ── open orders / fills ──
trade.append('<div class="bezel c12" data-reveal><div class="core">'
             '<div style="padding:16px 16px 0"><div class="utabs" id="tLedgerTabs">'
             '<button type="button" aria-pressed="true" data-l="open">Open orders</button>'
             '<button type="button" aria-pressed="false" data-l="fills">Your fills</button>'
             '<button type="button" aria-pressed="false" data-l="assets">Assets</button>'
             '</div></div><div id="tLedger"></div></div></div>')

trade.append('</div></div></section></main>')

TRADE_JS = PICK_JS + r"""
document.title = 'Trade ' + A.t + ' — Fantrade';
var el = function(id){ return document.getElementById(id); };
var mode = param('side') === 'sell' ? 'sell' : 'buy', otype = 'limit', view = 'open';

el('tBack').href = 'asset.html?a=' + encodeURIComponent(A.t);
el('tCoin').className = 'coin' + (A.c ? ' am' : '');
el('tCoin').innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-' + (A.c ? 'whistle' : 'boot')
  + '"/></svg>';
el('tName').textContent = A.n;
el('tSym').textContent = A.t;
el('tPx').textContent = A.p.toFixed(2);
el('tDelta').textContent = (A.d >= 0 ? '+' : '') + A.d.toFixed(2) + '%';
el('tDelta').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('tPx').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('tLimit').value = A.p.toFixed(2);
el('tStop').value = (A.p * 0.96).toFixed(2);

book2('tAsks', 'ask', 8, function(px){ el('tLimit').value = px.toFixed(2); calc(); });
book2('tBids', 'bid', 8, function(px){ el('tLimit').value = px.toFixed(2); calc(); });
el('tLast').textContent = A.p.toFixed(2);
el('tLast').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('tLastSub').textContent = '≈ £' + (A.p / 12.4).toFixed(2) + ' · last traded';
(function(){
  var b = Math.max(12, Math.min(88, Math.round(48 + A.d)));
  el('tdBid').style.width = b + '%'; el('tdAsk').style.width = (100 - b) + '%';
  el('tdBidK').textContent = 'B ' + b + '%'; el('tdAskK').textContent = (100 - b) + '% S';
})();

function num(v){ return parseFloat(String(v).replace(/[^0-9.]/g, '')) || 0; }
function qty(){ return Math.round(num(el('tQty').value)); }
function price(){ return otype === 'market' ? A.p : (num(el('tLimit').value) || A.p); }

// ── steppers ──
document.querySelectorAll('[data-step]').forEach(function(b){
  b.addEventListener('click', function(){
    var t = el(b.dataset.for), dir = +b.dataset.step;
    var isQty = /Qty/.test(b.dataset.for);
    var step = isQty ? 100 : Math.max(0.01, A.p * 0.001);
    var v = num(t.value) + dir * step;
    v = Math.max(isQty ? 0 : 0.01, v);
    t.value = isQty ? Math.round(v).toLocaleString('en-US') : v.toFixed(2);
    isQty ? (calc(), swapCalc()) : calc();
  });
});

// ── percentage slider ──
var rng = el('tRange');
function paintSlider(pc){
  el('tFill').style.width = pc + '%';
  el('tKnob').style.left = pc + '%';
  document.querySelectorAll('#tSlider .notch').forEach(function(n){
    n.classList.toggle('on', parseFloat(n.style.left) <= pc);
  });
}
rng.addEventListener('input', function(){
  var pc = +rng.value, s = FT.getState(), h = held(), q;
  if(mode === 'buy') q = Math.floor(s.wallet.balance * (pc / 100) / (price() * 1.004));
  else q = Math.floor((h ? h.shares : 0) * (pc / 100));
  el('tQty').value = q.toLocaleString('en-US');
  paintSlider(pc); calc();
});

function calc(){
  var q = qty(), px = price(), sub = q * px, fee = sub * 0.004;
  var s = FT.getState(), h = held();
  el('tAmt').value = fmt(sub) + ' $FTR';
  el('tFee').textContent = fmt(fee) + ' $FTR';
  el('tTotLabel').textContent = mode === 'buy' ? 'Total cost' : 'You receive';
  el('tTot').textContent = fmt(mode === 'buy' ? sub + fee : sub - fee) + ' $FTR';
  el('tAvailLabel').textContent = mode === 'buy' ? 'Available $FTR' : 'Shares held';
  el('tAvail').textContent = mode === 'buy'
    ? fmt(s.wallet.balance) + ' $FTR'
    : (h ? h.shares.toLocaleString('en-US') + ' ' + A.t : '0 ' + A.t);
  var go = el('tGo');
  var verb = otype === 'market' ? (mode === 'buy' ? 'Buy ' : 'Sell ')
    : (mode === 'buy' ? 'Place bid for ' : 'Place ask for ');
  go.childNodes[0].nodeValue = verb + A.t;
  go.className = 'btn ' + (mode === 'buy' ? 'btn-lime' : 'btn-red');
  el('tHint').textContent = otype === 'market'
    ? 'A market order fills straight from the book at the best available price.'
    : (mode === 'buy'
       ? 'A limit buy below the market rests as your bid until someone sells into it.'
       : 'A limit sell above the market rests as your ask until someone buys it.');
}

document.querySelectorAll('#tMode button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#tMode button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true');
    var m = b.dataset.m;
    document.querySelectorAll('[data-pane]').forEach(function(p){
      p.classList.toggle('on', p.dataset.pane === (m === 'swap' ? 'swap' : 'order'));
    });
    if(m !== 'swap'){ mode = m; rng.value = 0; paintSlider(0); calc(); }
  });
});
el('tType').addEventListener('change', function(){
  otype = el('tType').value;
  el('tLimitWrap').hidden = otype === 'market';
  el('tStopWrap').hidden = otype !== 'stop';
  calc();
});

el('tGo').addEventListener('click', function(){
  var q = qty();
  if(q < 1){ showToast('Enter how many shares to trade.', 'error'); return; }
  if(otype !== 'market' && !(price() > 0)){ showToast('Enter a valid price.', 'error'); return; }
  if(otype === 'market'){
    try {
      var r = FT.executeTrade(mode, A.t, A.n, q, A.p, A.c);
      showToast((mode === 'buy' ? 'Bought ' : 'Sold ') + q.toLocaleString('en-US') + ' ' + A.t
        + ' for ' + r.total.toLocaleString('en-US') + ' $FTR.', 'success');
      rng.value = 0; paintSlider(0); calc(); renderLedger();
    } catch(e){ showToast(e.message, 'error'); }
    return;
  }
  OPEN.unshift({ side: mode, q: q, px: price(), t: 'Just now', type: otype });
  renderLedger();
  showToast((mode === 'buy' ? 'Bid' : 'Ask') + ' for ' + q.toLocaleString('en-US') + ' ' + A.t
    + ' at ' + price().toFixed(2) + ' is on the book.', 'success');
});

// ── swap ──
var PRICES = {};
function fillSwap(){
  var s = FT.getState(), from = el('swFrom'), to = el('swTo');
  var held_ = Object.keys(s.holdings), all = {};
  ASSETS.forEach(function(x){ all[x.t] = x.p; PRICES[x.t] = x.p;
    PRICES[x.t + ':name'] = x.n; PRICES[x.t + ':coach'] = x.c; });
  held_.forEach(function(k){ all[k] = s.holdings[k].p; PRICES[k] = s.holdings[k].p;
    PRICES[k + ':name'] = s.holdings[k].n; });
  var kf = from.value, kt = to.value;
  from.innerHTML = held_.map(function(k){
    return '<option value="' + k + '">' + k + ' · ' + s.holdings[k].shares.toLocaleString('en-US')
      + ' shares</option>';
  }).join('') || '<option value="">Nothing held yet</option>';
  to.innerHTML = Object.keys(all).map(function(k){
    return '<option value="' + k + '">' + k + ' · ' + all[k].toFixed(2) + ' $FTR</option>';
  }).join('');
  if(kf && s.holdings[kf]) from.value = kf;
  if(kt && all[kt]) to.value = kt;
  else if(to.value === from.value && to.options.length > 1) to.selectedIndex = 1;
  swapCalc();
}
function swapCalc(){
  var s = FT.getState(), fk = el('swFrom').value, tk = el('swTo').value, h = s.holdings[fk];
  if(!h){ ['swGive','swFee','swGet','swDust'].forEach(function(i){ el(i).textContent = '—'; });
    el('swHold').textContent = 'Buy something on the exchange first.'; return; }
  el('swHold').textContent = 'You hold ' + h.shares.toLocaleString('en-US') + ' at ' + h.p.toFixed(2) + ' $FTR.';
  var q = Math.min(Math.round(num(el('swQty').value)), h.shares);
  var gross = q * h.p, fee = gross * 0.004, net = gross - fee;
  var tp = PRICES[tk] || 0, got = tp ? Math.floor(net / tp) : 0;
  el('swGive').textContent = q.toLocaleString('en-US') + ' ' + fk + ' · ' + fmt(gross) + ' $FTR';
  el('swFee').textContent = fmt(fee) + ' $FTR';
  el('swGet').textContent = got.toLocaleString('en-US') + ' ' + tk;
  el('swDust').textContent = fmt(Math.max(0, net - got * tp)) + ' $FTR';
}
['swQty'].forEach(function(i){ el(i).addEventListener('input', swapCalc); });
['swFrom','swTo'].forEach(function(i){ el(i).addEventListener('change', swapCalc); });
el('swGo').addEventListener('click', function(){
  var fk = el('swFrom').value, tk = el('swTo').value;
  if(!fk){ showToast('Nothing to swap yet.', 'error'); return; }
  if(fk === tk){ showToast('Pick two different assets.', 'error'); return; }
  try {
    var r = FT.swapAssets(fk, tk, Math.round(num(el('swQty').value)), PRICES);
    showToast(r.spent.toLocaleString('en-US') + ' ' + fk + ' swapped for '
      + r.received.toLocaleString('en-US') + ' ' + tk + '.', 'success');
  } catch(e){ showToast(e.message, 'error'); }
});

// ── ledger ──
var OPEN = [{ side:'buy', q:2000, px:A.p * 0.94, t:'Today, 09:12', type:'limit' },
            { side:'sell', q:1500, px:A.p * 1.08, t:'Yesterday, 18:40', type:'limit' }];
function renderLedger(){
  var box = el('tLedger'), s = FT.getState();
  var cols = 'grid-template-columns:82px 1fr 1fr 1fr 96px';
  if(view === 'open'){
    if(!OPEN.length){
      box.innerHTML = '<div class="empty-state"><svg class="ic-xl" aria-hidden="true">'
        + '<use href="#i-receipt"/></svg>No resting bids or asks on this market.</div>';
      return;
    }
    box.innerHTML = '<div class="dh" style="' + cols + '"><span>Side</span><span>Shares</span>'
      + '<span>Price</span><span>Placed</span><span style="text-align:right">Action</span></div>'
      + OPEN.map(function(o, i){
        return '<div class="dr" style="' + cols + '">'
          + '<div><span class="tag ' + (o.side === 'buy' ? 'lime' : 'red') + '">'
          + (o.side === 'buy' ? 'bid' : 'ask') + '</span></div>'
          + '<div class="num" style="font-size:12px">' + o.q.toLocaleString('en-US') + '</div>'
          + '<div class="num" style="font-size:12px">' + o.px.toFixed(2) + '</div>'
          + '<div style="color:var(--dim);font-size:11px">' + o.t + '</div>'
          + '<div style="text-align:right"><button class="tradebtn" data-cancel="' + i + '" '
          + 'style="width:auto;padding:5px 12px">Cancel</button></div></div>';
      }).join('');
    box.querySelectorAll('[data-cancel]').forEach(function(b){
      b.addEventListener('click', function(){
        OPEN.splice(+b.dataset.cancel, 1); renderLedger();
        showToast('Order cancelled. Nothing was charged.', 'info');
      });
    });
    return;
  }
  if(view === 'assets'){
    var keys = Object.keys(s.holdings);
    if(!keys.length){
      box.innerHTML = '<div class="empty-state"><svg class="ic-xl" aria-hidden="true">'
        + '<use href="#i-supply"/></svg>No holdings yet.</div>';
      return;
    }
    box.innerHTML = keys.map(function(k){
      var h = s.holdings[k];
      return '<a class="arow" href="asset.html?a=' + encodeURIComponent(k) + '">'
        + '<div class="who"><span class="coin' + (h.c ? ' am' : '') + '">'
        + '<svg class="ic"><use href="#i-' + (h.c ? 'whistle' : 'boot') + '"/></svg></span>'
        + '<div style="min-width:0"><div class="nm">' + k + '</div><div class="qt">' + h.n + '</div></div></div>'
        + '<div></div><div><div class="val">' + fmt(h.shares * h.p) + '</div>'
        + '<div class="chg">' + h.shares.toLocaleString('en-US') + ' shares</div></div></a>';
    }).join('');
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
        + '<div class="num" style="font-size:12px">' + t.shares.toLocaleString('en-US') + '</div>'
        + '<div class="num" style="font-size:12px">' + t.price.toFixed(2) + '</div>'
        + '<div style="color:var(--dim);font-size:11px">' + t.time + '</div>'
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

if(mode === 'sell') document.querySelector('#tMode button[data-m="sell"]').click();
paintSlider(0); calc(); fillSwap(); renderLedger();
window.addEventListener('fantrade:statechange', function(){ calc(); fillSwap(); renderLedger(); });
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
