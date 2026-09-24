# -*- coding: utf-8 -*-
"""Drill-down screens: one asset's market page, the trade terminal, the club
builder and the division structure. Each one is a destination reached from a
list, never a section stacked onto it."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import head, atmosphere, nav, footer, ic, JS_SHELL
from app_design import apply_design, intro

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
    html = (head(title, css, "app" if app else "") + atmosphere() + nav(fname, app) + body +
            "<script src=\"public/fantrade-api.js\"></script>" +
            "<script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
    html = apply_design(fname, html)
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
var SYM = ftSym(param('a') || 'FSAKA');
var A = ASSETS.filter(function(x){ return x.t.toLowerCase() === SYM.toLowerCase() || ftSym(x.t).toLowerCase() === SYM.toLowerCase(); })[0] || ASSETS[0];
function fmt(n){ return Math.round(n).toLocaleString('en-US'); }
function money(n){ return pxFmt(n); }
function held(){ return FT.getState().holdings[A.t] || null; }

// Order book, built deterministically around the last price so the same
// asset always shows the same depth. Asks render top-down (worst first),
// bids top-down (best first), the way a real book reads.
var TICK = 1;
function book2(box, side, count, onPick){
  var rows = [], px = A.p, total = 0;
  for(var i = 0; i < count; i++){
    var step = (i + 1) * (px * 0.0016) * TICK;
    var p = side === 'bid' ? px - step : px + step;
    var size = Math.round(3100 + Math.abs(Math.sin((i + 1) * 2.7)) * 41000);
    total += size;
    rows.push({ p: p, s: size, t: total });
  }
  var max = rows[rows.length - 1].t;
  if(side === 'ask') rows.reverse();
  var host = document.getElementById(box);
  host.innerHTML = rows.map(function(r){
    return '<div class="b2row ' + side + '" data-px="' + pxFix(r.p) + '">'
      + '<i style="width:' + (r.t / max * 100).toFixed(0) + '%"></i>'
      + '<span>' + pxFix(r.p) + '</span><span>' + fmt(r.s) + '</span></div>';
  }).join('');
  if(onPick) host.querySelectorAll('.b2row').forEach(function(el){
    el.tabIndex = 0;
    el.setAttribute('role', 'button');
    el.setAttribute('aria-label', 'Set limit price to ' + el.dataset.px + ' FTR');
    el.addEventListener('click', function(){ onPick(parseFloat(el.dataset.px)); });
    el.addEventListener('keydown', function(event){
      if(event.key === 'Enter' || event.key === ' '){event.preventDefault();onPick(parseFloat(el.dataset.px));}
    });
  });
}
"""

# ══════════════════════════════════════════════════════════════════
# ASSET — one player or coach's market page (Screenshot 2 Match)
# ══════════════════════════════════════════════════════════════════
from asset_page import HTML as ASSET_HTML, JS as ASSET_JS

page("asset.html", "Player shares — Fantrade", ASSET_HTML, ASSET_JS)

# ══════════════════════════════════════════════════════════════════
# TRADE — the terminal: bid, buy, sell, swap
# ══════════════════════════════════════════════════════════════════
TRADE_CSS = """
/* KuCoin-style Mobile Player Share Trading Terminal */
.kc-trade-wrap{max-width:680px;margin:0 auto;padding:8px 16px 110px}
.kc-trade-topbar{display:flex;align-items:center;justify-content:space-between;padding:6px 0 14px;border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:12px}
.kc-trade-top-left{display:flex;align-items:center;gap:10px}
.kc-trade-pair-title{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:18px;display:flex;align-items:center;gap:6px;color:var(--ink)}
.kc-trade-pair-title .kc-quote{font-size:13px;color:#767c82;font-weight:600}
.kc-trade-tag{background:rgba(255,255,255,.08);color:#8E9AA8;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px}
.kc-trade-delta{font-family:'Montserrat', sans-serif;font-size:12px;font-weight:600;color:var(--lime);margin-left:4px}
.kc-trade-delta.down{color:#FF3B47}
.kc-trade-top-right{display:flex;align-items:center;gap:8px}

@media (max-width:640px){
  #tLedger .dh,#tLedger .dr{grid-template-columns:52px 1fr 1fr 76px!important;gap:8px;padding:12px 0}
  #tLedger .dh>*:nth-child(4),#tLedger .dr>*:nth-child(4){display:none}
  #tLedger .dh>*:nth-child(5),#tLedger .dr>*:nth-child(5){text-align:right}
  #tLedger .dh{font-size:8px;letter-spacing:.12em}
}
#tLedger .dh,#tLedger .dr{padding-left:0;padding-right:0}
.tgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.16fr);gap:16px;align-items:start}
@media (max-width:480px){.tgrid{grid-template-columns:1fr 1.15fr;gap:10px}}

/* order book footer: tick size + depth split */
.bkfoot{display:flex;align-items:center;gap:8px;margin-top:10px}
.ticksel{display:flex;align-items:center;gap:8px;flex:1;min-width:0;border:1px solid rgba(255,255,255,.08);
  border-radius:8px;background:rgba(255,255,255,.03);box-shadow:var(--inset);padding:5px 8px}
.ticksel select{flex:1;min-width:0;border:0;background:transparent;color:var(--ink);outline:none;
  cursor:pointer;font-family:'Montserrat', sans-serif;font-size:11px}
.ticksel select option{background:#0A0B0C}
.ticksel .chev{flex:none}
.bkbtn{display:grid;place-items:center;width:32px;height:32px;flex:none;border-radius:8px;
  border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.04);color:#767c82;transition:all .2s}
.bkbtn:hover{color:var(--lime);border-color:rgba(24,0,173,.4)}
.bkbtn .ic{width:14px;height:14px}
.book2 .b2row i{opacity:.72}
.book2 .last span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (max-width:420px){
  .book2 .bh{font-size:8px}
  .b2row{padding:3px 4px;font-size:10px}
  .book2 .last b{font-size:13px}
  .book2 .last span{font-size:9px}
  .bkfoot{gap:6px}
  .ticksel{padding:5px 6px}
  .ticksel select{font-size:10px}
}

/* buy / sell / swap pills */
.sideseg{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:3px;border-radius:10px;
  background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);margin-bottom:12px}
.sideseg button{border:0;background:transparent;color:#767c82;border-radius:8px;padding:9px 0;
  cursor:pointer;font-family:Montserrat,sans-serif;font-weight:700;font-size:11.5px;letter-spacing:.04em;
  text-transform:uppercase;transition:all .2s}
.sideseg button:hover{color:var(--ink)}
.sideseg button[aria-pressed="true"]{background:var(--lime);color:#fff;font-weight:800}
.sideseg button[data-m="sell"][aria-pressed="true"]{background:#FF3B47;color:#fff}
.sideseg button[data-m="swap"][aria-pressed="true"]{background:rgba(255,255,255,.12);color:var(--ink)}

/* Fields */
.tfield{display:flex;align-items:center;gap:8px;border:1px solid rgba(255,255,255,.08);border-radius:10px;
  background:rgba(255,255,255,.03);padding:8px 4px 8px 12px;margin-bottom:8px}
.tfield .bd{flex:1;min-width:0}
.tfield .lbl{display:block;font-weight:600;font-size:8.5px;letter-spacing:.12em;text-transform:uppercase;
  color:#767c82;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tfield input{display:block;width:100%;border:0;background:transparent;color:var(--ink);outline:none;
  font-family:'Montserrat', sans-serif;font-size:14px;padding:3px 0 0}
.tfield input::placeholder{color:#5A605B}
.tfield input:read-only{color:#8B918A}
.tfield .pm{flex:none;display:flex;align-items:stretch;align-self:stretch}
.tfield .pm button{width:30px;border:0;background:transparent;color:#767c82;cursor:pointer;
  font-size:16px;line-height:1;transition:color .2s}
.tfield .pm button:first-child{border-right:1px solid rgba(255,255,255,.08)}
.tfield .pm button:hover{color:var(--lime)}
.tfield[hidden]{display:none}

.tline{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:6px 0;font-size:11.5px;color:#767c82}
.tline b{font-family:'Montserrat', sans-serif;font-weight:500;color:var(--ink);font-size:12px}
.bigbtn{display:block;width:100%;border:0;border-radius:10px;padding:14px 0;margin-top:12px;cursor:pointer;
  font-family:Space Grotesk,sans-serif;font-weight:700;font-size:13.5px;letter-spacing:.04em;text-transform:uppercase;
  background:var(--lime);color:#fff;transition:filter .2s}
.bigbtn:hover{filter:brightness(1.08)}
.bigbtn.sell{background:#FF3B47;color:#fff}
.bigbtn.neutral{background:rgba(255,255,255,.08);color:var(--ink);border:1px solid rgba(255,255,255,.14)}
"""

trade = [T('<main><div class="kc-trade-wrap trade-page">' + '<a href="exchange.html" id="tBack" class="back-btn" aria-label="Back to player details">Back</a>' + intro('Trade shares', 'Choose your player. Make your next move.') +
           '<!-- Top Navigation Bar -->'
           '<div class="kc-trade-topbar">'
           '  <div class="kc-trade-top-left">'
           '    <span id="tPortrait" class="trade-portrait"></span><div class="trade-player"><p id="tPlayerName"></p><div class="kc-trade-pair-title">'
           '      <span id="tSym">FSAKA</span><span class="kc-quote">/FTR</span>'
           '      <span class="kc-trade-delta" id="tDelta">+6.40%</span>'
           '    </div></div>'
           '  </div>'
           '  <div class="kc-trade-top-right">'
           '    <a href="asset.html" id="tChart" class="kc-icon-btn" title="Candlestick Chart">'
           '      View chart'
           '    </a>'
           '  </div>'
           '</div>'
           '<div class="tgrid">')]

# ── the book ──
trade.append(T('<details class="trade-depth" id="tradeDepth"><summary>Market depth</summary><p class="trade-help">Preview orders. Select a price to use it in your limit order.</p>'
               '<div class="book2"><div class="bh"><span>Price $FTR</span><span>Shares</span></div>'
               '<div id="tAsks"></div>'
               '<div class="last"><b id="tLast">—</b><span id="tLastSub">last traded</span></div>'
               '<div id="tBids"></div>'
               '<div class="depthbar"><i id="tdBid" style="width:58%;background:var(--lime)"></i>'
               '<i id="tdAsk" style="width:42%;background:var(--red)"></i></div>'
               '<div class="depthkey"><span style="color:var(--lime)" id="tdBidK">B 58%</span>'
               '<span style="color:var(--red)" id="tdAskK">42% S</span></div></div>'
               '<div class="bkfoot"><span class="ticksel">'
               '<select id="tTick" aria-label="Price grouping">'
               '<option value="1">0.01</option><option value="5">0.05</option>'
               '<option value="10">0.10</option><option value="50">0.50</option></select>'
               '<span class="chev"></span></span>'
               '<a class="bkbtn" href="#tLedger" id="tJump" aria-label="Jump to your orders">@@</a></div>'
               '</details>', ic("receipt", "ic")))

# ── the ticket ──
trade.append(T('<div class="trade-ticket">'
               '<div class="sideseg" id="tMode">'
               '<button type="button" aria-pressed="true" data-m="buy">Buy</button>'
               '<button type="button" aria-pressed="false" data-m="sell">Sell</button>'
               '<button type="button" aria-pressed="false" data-m="swap">Swap</button>'
               '</div>'

               # buy / sell ticket
               '<div class="pane on" data-pane="order">'
               '<label class="trade-field-label" for="tTypeBtn" id="tTypeLabel">Order type</label><div class="otype" id="tTypeWrap">'
               '<select id="tType" hidden tabindex="-1" aria-hidden="true" aria-describedby="tradeTypeHelp"><option value="limit">Limit</option>'
               '<option value="market">Market</option>'
               '</select>'
               '<button type="button" class="trade-pick-card" id="tTypeBtn" aria-haspopup="dialog" aria-labelledby="tTypeLabel tTypeBtn"></button></div><p class="trade-help" id="tradeTypeHelp"></p>'

               '<div class="tfield" id="tStopWrap" hidden><div class="bd">'
               '<label class="lbl" for="tStop">Stop price · FTR</label><input id="tStop" inputmode="decimal"></div>'
               '<span class="pm"><button type="button" data-step="-1" data-for="tStop" '
               'aria-label="Lower the stop">&minus;</button>'
               '<button type="button" data-step="1" data-for="tStop" aria-label="Raise the stop">+</button>'
               '</span></div>'

               '<div class="tfield" id="tLimitWrap"><div class="bd">'
               '<label class="lbl" for="tLimit">Price per share · FTR</label><input id="tLimit" inputmode="decimal"></div>'
               '<span class="pm"><button type="button" data-step="-1" data-for="tLimit" '
               'aria-label="Lower the price">&minus;</button>'
               '<button type="button" data-step="1" data-for="tLimit" aria-label="Raise the price">+</button>'
               '</span></div>'

               '<div class="tfield"><div class="bd">'
               '<label class="lbl" for="tQty">Shares<span class="unit"> · <span id="tQtyUnit">FSAKA</span></span></label>'
               '<input id="tQty" inputmode="numeric" placeholder="Enter quantity" value=""></div>'
               '<span class="pm"><button type="button" data-step="-1" data-for="tQty" '
               'aria-label="Fewer shares">&minus;</button>'
               '<button type="button" data-step="1" data-for="tQty" aria-label="More shares">+</button>'
               '</span></div>'

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

               '<div class="tfield" style="margin-top:20px"><div class="bd">'
               '<label class="lbl" for="tAmt">Order value · FTR</label><input id="tAmt" readonly></div></div>'

               '<div class="tline"><span>Fee (0.4%)</span><b id="tFee">—</b></div>'
               '<div class="tline"><span id="tTotLabel">Total cost</span><b id="tTot">—</b></div>'
               '<div class="tline"><span id="tAvailLabel">Avail.</span><b id="tAvail">—</b></div>'
               '<div class="tline"><span class="dash" id="tMaxLabel">Max buy</span><b id="tMax">—</b></div>'
               '<button class="bigbtn" type="button" id="tGo">Buy FSAKA</button>'
               '</div>'

               # swap
               '<div class="pane" data-pane="swap">'
               '<div class="tf" id="f-swFrom"><label for="swFromBtn" id="swFromLabel">From</label>'
               '<select id="swFrom" hidden tabindex="-1" aria-hidden="true"></select><button type="button" class="swap-pick trade-swap-pick" id="swFromBtn" data-trade-pick="from" aria-haspopup="dialog" aria-labelledby="swFromLabel swFromBtn"></button>'
               '<div class="hint" id="swHold">—</div></div>'
               '<div class="tfield"><div class="bd"><label class="lbl" for="swQty">Shares to swap</label>'
               '<input id="swQty" inputmode="numeric" placeholder="Enter quantity" value=""></div>'
               '<span class="pm"><button type="button" data-step="-1" data-for="swQty" '
               'aria-label="Fewer shares">&minus;</button>'
               '<button type="button" data-step="1" data-for="swQty" aria-label="More shares">+</button>'
               '</span></div>'
               '<div class="tf" style="margin-top:12px"><label for="swToBtn" id="swToLabel">To</label>'
               '<select id="swTo" hidden tabindex="-1" aria-hidden="true"></select><button type="button" class="swap-pick trade-swap-pick" id="swToBtn" data-trade-pick="to" aria-haspopup="dialog" aria-labelledby="swToLabel swToBtn"></button></div>'
               '<div class="tline"><span>You give</span><b id="swGive">—</b></div>'
               '<div class="tline"><span>Fee (0.4%)</span><b id="swFee">—</b></div>'
               '<div class="tline"><span>You receive</span><b id="swGet">—</b></div>'
               '<div class="tline"><span>Dust back to wallet</span><b id="swDust">—</b></div>'
               '<button class="bigbtn neutral" type="button" id="swGo">Swap assets</button>'
               '</div>'
               '</div>',
               ic("candle", "ic"), ic("swap", "ic"), ic("target", "ic")))

trade.append('</div>')

# ── open orders / your fills / assets ──
trade.append('<div class="flat-sep" data-reveal>'
             '<div class="utabs" id="tLedgerTabs">'
             '<button type="button" aria-pressed="true" data-l="open">Open orders '
             '<span id="tcOpen">(0)</span></button>'
             '<button type="button" aria-pressed="false" data-l="fills">Your fills '
             '<span id="tcFills">(0)</span></button>'
             '<button type="button" aria-pressed="false" data-l="assets">Assets '
             '<span id="tcAssets">(0)</span></button>'
             '</div><div id="tLedger"></div></div>')

trade.append('''</div>
<dialog id="tradeOptionPicker" class="asset-picker" aria-labelledby="tradeOptionPickerTitle">
<div class="asset-picker-heading"><h2 id="tradeOptionPickerTitle">Choose order type.</h2><button type="button" id="tradeOptionPickerClose" aria-label="Close order type picker">''' + ic("cross", "ic") + '''</button></div>
<p id="tradeOptionStatus" class="asset-search-status" role="status"></p><div id="tradeOptionResults" class="asset-search-results"></div></dialog>
<dialog id="tradeAssetPicker" class="asset-picker" aria-labelledby="tradeAssetPickerTitle">
<div class="asset-picker-heading"><h2 id="tradeAssetPickerTitle">Choose shares.</h2><button type="button" id="tradeAssetPickerClose" aria-label="Close share picker">''' + ic("cross", "ic") + '''</button></div>
<label for="tradeAssetSearch">Search players, coaches or clubs</label><input id="tradeAssetSearch" type="search" placeholder="Try Saka or Arsenal" autocomplete="off">
<p id="tradeAssetStatus" class="asset-search-status" role="status"></p><div id="tradeAssetResults" class="asset-search-results"></div></dialog>
</main>''')

TRADE_JS = PICK_JS + r"""
document.title = 'Trade ' + ftSym(A.t) + ' Activity Shares — Fantrade';
var el = function(id){ return document.getElementById(id); };
var mode = param('side') === 'sell' ? 'sell' : 'buy', otype = 'limit', view = 'open';
function safeText(v){var span=document.createElement('span');span.textContent=String(v == null ? '' : v);return span.innerHTML.replace(/"/g,'&quot;');}

if(el('tBack')) el('tBack').href = 'asset.html?a=' + encodeURIComponent(A.t);
if(el('tCoin')){
  el('tCoin').className = 'coin' + (A.c ? ' am' : '');
  el('tCoin').innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-' + (A.c ? 'whistle' : 'boot') + '"/></svg>';
}
if(el('tSym')) el('tSym').textContent = ftSym(A.t);
el('tPortrait').innerHTML = playerPhoto(A.t,A.n);
el('tPlayerName').textContent = A.n;
var tradeDesktop = window.matchMedia('(min-width: 901px)');
el('tradeDepth').open = tradeDesktop.matches;
tradeDesktop.addEventListener('change',function(event){el('tradeDepth').open=event.matches;});
if(el('tQtyUnit')) el('tQtyUnit').textContent = ftSym(A.t);
if(el('tChart')) el('tChart').href = 'asset.html?a=' + encodeURIComponent(A.t);
el('tDelta').textContent = (A.d >= 0 ? '+' : '') + A.d.toFixed(2) + '%';
el('tDelta').classList.toggle('down', A.d < 0);
el('tDelta').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('tLimit').value = pxFix(A.p);
el('tStop').value = pxFix(A.p * 0.96);

function drawBook(){
  book2('tAsks', 'ask', 8, function(px){ el('tLimit').value = pxFix(px); calc(); });
  book2('tBids', 'bid', 8, function(px){ el('tLimit').value = pxFix(px); calc(); });
}
drawBook();
el('tTick').addEventListener('change', function(){
  TICK = parseFloat(el('tTick').value) || 1;
  drawBook();
});
el('tLast').textContent = pxFmt(A.p);
el('tLast').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('tLastSub').textContent = '≈ ' + usdFmt(A.p);
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
    t.value = isQty ? Math.round(v).toLocaleString('en-US') : pxFix(v);
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
  el('tAvailLabel').textContent = 'Available';
  el('tAvail').textContent = mode === 'buy'
    ? fmt(s.wallet.balance) + ' $FTR'
    : (h ? h.shares.toLocaleString('en-US') + ' ' + A.t : '0 ' + A.t);
  el('tMaxLabel').textContent = mode === 'buy' ? 'Max buy' : 'Max sell';
  el('tMax').textContent = mode === 'buy'
    ? Math.floor(s.wallet.balance / (px * 1.004)).toLocaleString('en-US') + ' ' + A.t
    : (h ? h.shares.toLocaleString('en-US') + ' ' + A.t : '0 ' + A.t);
  var go = el('tGo');
  var verb = mode === 'buy' ? 'Buy ' : 'Sell ';
  go.textContent = verb + A.t;
  go.className = 'bigbtn' + (mode === 'buy' ? '' : ' sell');
  el('tradeTypeHelp').textContent = otype === 'market'
    ? 'Trade at the available market price. The final price may vary.'
    : 'Choose your price per share. Limit orders on this preview are kept for this visit only.';
}

var ORDER_TYPES = {
  limit: { n:'Limit', sub:'Choose your price and rest the order on the book.' },
  market: { n:'Market', sub:'Trade at the best available market price.' }
};
function orderTypeCard(value){
  var item = ORDER_TYPES[value] || ORDER_TYPES.limit;
  return '<span class="wallet-currency-dot"><svg class="ic" aria-hidden="true"><use href="#i-candle"/></svg></span><span class="swap-pick-text"><b>'+safeText(item.n)+'</b><small>'+safeText(item.sub)+'</small></span><svg class="ic swap-pick-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
}
function syncOrderTypeCard(){ el('tTypeBtn').innerHTML = orderTypeCard(el('tType').value); }
var tradeOptionPicker = el('tradeOptionPicker');
function orderTypeRows(){
  var current = el('tType').value, keys = Object.keys(ORDER_TYPES);
  el('tradeOptionStatus').textContent = 'Choose how this order should execute.';
  el('tradeOptionResults').innerHTML = keys.map(function(key){
    var item = ORDER_TYPES[key];
    return '<button type="button" class="asset-search-row" data-order-type="'+key+'"'+(key===current?' aria-current="true"':'')+'><span class="wallet-currency-dot"><svg class="ic" aria-hidden="true"><use href="#i-candle"/></svg></span><span><b>'+safeText(item.n)+'</b><small>'+safeText(item.sub)+'</small></span><span class="asset-search-price">'+safeText(item.n)+'</span></button>';
  }).join('');
}
function openOrderTypePicker(){orderTypeRows();tradeOptionPicker.showModal();document.body.classList.add('asset-picker-open');}

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
  syncOrderTypeCard();
  calc();
});
el('tTypeBtn').addEventListener('click', openOrderTypePicker);
el('tradeOptionResults').addEventListener('click', function(event){
  var row = event.target.closest('[data-order-type]'); if(!row) return;
  el('tType').value = row.dataset.orderType;
  el('tType').dispatchEvent(new Event('change'));
  tradeOptionPicker.close();
});
el('tradeOptionPickerClose').addEventListener('click', function(){ tradeOptionPicker.close(); });
tradeOptionPicker.addEventListener('close', function(){ document.body.classList.remove('asset-picker-open'); el('tTypeBtn').focus(); });
tradeOptionPicker.addEventListener('click', function(event){
  var r = tradeOptionPicker.getBoundingClientRect();
  if(event.target === tradeOptionPicker && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) tradeOptionPicker.close();
});
['tQty','tLimit','tStop'].forEach(function(id){
  el(id).addEventListener('input', calc);
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
    + ' at ' + pxFmt(price()) + ' is on the book.', 'success');
});

// ── swap ──
var PRICES = {};
function clubOfTrade(k){var a=ASSETS.filter(function(x){return x.t===k;})[0];return a&&a.club?a.club:(PRICES[k+':coach']?'Coach':'');}
function swapPickCard(k,sub){
  if(!k || !PRICES[k+':name']) return '<span class="swap-pick-empty">Choose shares</span><svg class="ic swap-pick-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
  return playerPhoto(k,PRICES[k+':name'])+'<span class="swap-pick-text"><b>'+safeText(PRICES[k+':name'])+'</b><small>'+safeText(sub)+'</small></span><svg class="ic swap-pick-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
}
function syncTradeSwapPicks(){
  var s=FT.getState(),fk=el('swFrom').value,tk=el('swTo').value,h=s.holdings[fk];
  el('swFromBtn').innerHTML=h?swapPickCard(fk,ftSym(fk)+' · '+h.shares.toLocaleString('en-US')+' shares available'):'<span class="swap-pick-empty">No shares held yet</span>';
  el('swFromBtn').disabled=!h;
  el('swToBtn').innerHTML=swapPickCard(tk,ftSym(tk)+' · '+(PRICES[tk]?money(PRICES[tk])+' FTR per share':''));
}
function fillSwap(){
  var s = FT.getState(), from = el('swFrom'), to = el('swTo');
  var held_ = Object.keys(s.holdings), all = {};
  ASSETS.forEach(function(x){ all[x.t] = x.p; PRICES[x.t] = x.p;
    PRICES[x.t + ':name'] = x.n; PRICES[x.t + ':coach'] = x.c; });
  held_.forEach(function(k){ all[k] = s.holdings[k].p; PRICES[k] = s.holdings[k].p;
    PRICES[k + ':name'] = s.holdings[k].n; });
  var kf = from.value, kt = to.value;
  from.innerHTML = held_.map(function(k){
    return '<option value="' + k + '">' + ftSym(k) + ' · ' + s.holdings[k].shares.toLocaleString('en-US')
      + ' shares</option>';
  }).join('') || '<option value="">Nothing held yet</option>';
  to.innerHTML = Object.keys(all).map(function(k){
    return '<option value="' + k + '">' + ftSym(k) + ' · ' + pxFmt(all[k]) + ' $FTR</option>';
  }).join('');
  if(kf && s.holdings[kf]) from.value = kf;
  if(kt && all[kt]) to.value = kt;
  else if(to.value === from.value && to.options.length > 1) to.selectedIndex = 1;
  swapCalc();
}
function swapCalc(){
  var s = FT.getState(), fk = el('swFrom').value, tk = el('swTo').value, h = s.holdings[fk];
  syncTradeSwapPicks();
  if(!h){ ['swGive','swFee','swGet','swDust'].forEach(function(i){ el(i).textContent = '—'; });
    el('swHold').textContent = 'Buy something on the exchange first.'; return; }
  el('swHold').textContent = 'You hold ' + h.shares.toLocaleString('en-US') + ' at ' + pxFmt(h.p) + ' $FTR.';
  var q = Math.min(Math.round(num(el('swQty').value)), h.shares);
  var gross = q * h.p, fee = gross * 0.004, net = gross - fee;
  var tp = PRICES[tk] || 0, got = tp ? Math.floor(net / tp) : 0;
  el('swGive').textContent = q.toLocaleString('en-US') + ' ' + ftSym(fk) + ' · ' + fmt(gross) + ' $FTR';
  el('swFee').textContent = fmt(fee) + ' $FTR';
  el('swGet').textContent = got.toLocaleString('en-US') + ' ' + ftSym(tk);
  el('swDust').textContent = fmt(Math.max(0, net - got * tp)) + ' $FTR';
}
['swQty'].forEach(function(i){ el(i).addEventListener('input', swapCalc); });
['swFrom','swTo'].forEach(function(i){ el(i).addEventListener('change', swapCalc); });
var tradeAssetPicker=el('tradeAssetPicker'),tradePickMode='from';
function tradeAssetRows(){
  var s=FT.getState(),q=el('tradeAssetSearch').value.trim().toLowerCase(),rows;
  if(tradePickMode==='from') rows=Object.keys(s.holdings).filter(function(k){return s.holdings[k].shares>0;}).map(function(k){var h=s.holdings[k];return {t:k,n:h.n,sub:ftSym(k)+(clubOfTrade(k)?' · '+clubOfTrade(k):''),v:h.shares.toLocaleString('en-US'),u:'shares'};});
  else {var from=el('swFrom').value;rows=ASSETS.map(function(a){return a.t;}).concat(Object.keys(s.holdings)).filter(function(k,i,a){return a.indexOf(k)===i&&k!==from&&PRICES[k];}).map(function(k){return {t:k,n:PRICES[k+':name'],sub:ftSym(k)+(clubOfTrade(k)?' · '+clubOfTrade(k):''),v:money(PRICES[k]),u:'FTR'};});}
  rows=rows.filter(function(r){return (r.n+' '+r.sub).toLowerCase().indexOf(q)>-1;});
  var current=el(tradePickMode==='from'?'swFrom':'swTo').value;
  el('tradeAssetStatus').textContent=rows.length?rows.length+(tradePickMode==='from'?' holdings':' shares'):'No matches. Try another name or club.';
  el('tradeAssetResults').innerHTML=rows.map(function(r){return '<button type="button" class="asset-search-row" data-sym="'+safeText(r.t)+'"'+(r.t===current?' aria-current="true"':'')+'>'+playerPhoto(r.t,r.n)
    +'<span><b>'+safeText(r.n)+'</b><small>'+safeText(r.sub)+'</small></span><span class="asset-search-price">'+safeText(r.v)+'<small>'+safeText(r.u)+'</small></span></button>';}).join('');
}
function openTradeAssetPicker(which){tradePickMode=which;el('tradeAssetPickerTitle').textContent=which==='from'?'Choose shares to swap.':'Choose what to receive.';el('tradeAssetSearch').value='';tradeAssetRows();tradeAssetPicker.showModal();document.body.classList.add('asset-picker-open');el('tradeAssetSearch').focus();}
document.querySelectorAll('[data-trade-pick]').forEach(function(button){button.addEventListener('click',function(){openTradeAssetPicker(button.dataset.tradePick);});});
el('tradeAssetSearch').addEventListener('input',tradeAssetRows);
el('tradeAssetResults').addEventListener('click',function(event){var row=event.target.closest('[data-sym]');if(!row)return;var sel=el(tradePickMode==='from'?'swFrom':'swTo');sel.value=row.dataset.sym;if(tradePickMode==='from'&&el('swTo').value===sel.value){var alt=Array.prototype.slice.call(el('swTo').options).map(function(o){return o.value;}).filter(function(v){return v!==sel.value;})[0];if(alt)el('swTo').value=alt;}sel.dispatchEvent(new Event('change'));tradeAssetPicker.close();});
el('tradeAssetPickerClose').addEventListener('click',function(){tradeAssetPicker.close();});
tradeAssetPicker.addEventListener('close',function(){document.body.classList.remove('asset-picker-open');el(tradePickMode==='from'?'swFromBtn':'swToBtn').focus();});
tradeAssetPicker.addEventListener('click',function(event){var r=tradeAssetPicker.getBoundingClientRect();if(event.target===tradeAssetPicker&&(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom))tradeAssetPicker.close();});
el('swGo').addEventListener('click', function(){
  var fk = el('swFrom').value, tk = el('swTo').value;
  if(!fk){ showToast('Nothing to swap yet.', 'error'); return; }
  if(fk === tk){ showToast('Pick two different assets.', 'error'); return; }
  try {
    var r = FT.swapAssets(fk, tk, Math.round(num(el('swQty').value)), PRICES);
    showToast(r.spent.toLocaleString('en-US') + ' ' + ftSym(fk) + ' swapped for '
      + r.received.toLocaleString('en-US') + ' ' + ftSym(tk) + '.', 'success');
  } catch(e){ showToast(e.message, 'error'); }
});

// ── ledger ──
var OPEN = [{ side:'buy', q:2000, px:A.p * 0.94, t:'Today, 09:12', type:'limit' },
            { side:'sell', q:1500, px:A.p * 1.08, t:'Yesterday, 18:40', type:'limit' }];
function renderLedger(){
  var box = el('tLedger'), s = FT.getState();
  if(el('tcOpen')) counts();
  var cols = 'grid-template-columns:62px 1fr 1fr 1.3fr 82px';
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
          + '<div class="num" style="font-size:12px">' + pxFmt(o.px) + '</div>'
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
        + playerPhoto(k,h.n) + '</span>'
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
        + '<div class="num" style="font-size:12px">' + pxFmt(t.price) + '</div>'
        + '<div style="color:var(--dim);font-size:11px">' + t.time + '</div>'
        + '<div class="pl ' + (down ? 'down' : 'up') + '" style="text-align:right">'
        + (down ? '-' : '+') + fmt(t.total) + '</div></div>';
    }).join('');
}
function counts(){
  var s = FT.getState();
  el('tcOpen').textContent = '(' + OPEN.length + ')';
  el('tcFills').textContent = '(' + s.transactions.filter(function(t){
    return (t.type === 'BUY' || t.type === 'SELL') && t.asset === A.t; }).length + ')';
  el('tcAssets').textContent = '(' + Object.keys(s.holdings).length + ')';
}
document.querySelectorAll('#tLedgerTabs button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#tLedgerTabs button').forEach(function(x){
      x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true'); view = b.dataset.l; renderLedger();
  });
});

if(mode === 'sell') document.querySelector('#tMode button[data-m="sell"]').click();
syncOrderTypeCard(); paintSlider(0); calc(); fillSwap(); renderLedger(); counts();
window.addEventListener('fantrade:statechange', function(){
  calc(); fillSwap(); renderLedger(); counts();
});
"""

page("trade.html", "Trade — Fantrade", "".join(trade), TRADE_JS, TRADE_CSS)

print("built asset.html + trade.html")

# ══════════════════════════════════════════════════════════════════
# DIVISIONS — the tier structure behind the league table
# ══════════════════════════════════════════════════════════════════
from competition_pages import DIVISIONS_HTML, DIVISIONS_JS
page("divisions.html", "Divisions — Fantrade", DIVISIONS_HTML, DIVISIONS_JS)
