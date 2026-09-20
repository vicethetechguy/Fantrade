# -*- coding: utf-8 -*-
"""Drill-down screens: one asset's market page, the trade terminal, the club
builder and the division structure. Each one is a destination reached from a
list, never a section stacked onto it."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import head, atmosphere, nav, footer, ic, JS_SHELL
from app_design import apply_design

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
var SYM = param('a') || '$Saka';
var A = ASSETS.filter(function(x){ return x.t.toLowerCase() === SYM.toLowerCase(); })[0] || ASSETS[0];
function fmt(n){ return Math.round(n).toLocaleString('en-US'); }
function money(n){ return n.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}); }
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
.kc-trade-pair-title{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;font-size:18px;display:flex;align-items:center;gap:6px;color:var(--ink)}
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
  font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:13.5px;letter-spacing:.04em;text-transform:uppercase;
  background:var(--lime);color:#fff;transition:filter .2s}
.bigbtn:hover{filter:brightness(1.08)}
.bigbtn.sell{background:#FF3B47;color:#fff}
.bigbtn.neutral{background:rgba(255,255,255,.08);color:var(--ink);border:1px solid rgba(255,255,255,.14)}
"""

trade = [T('<main><div class="kc-trade-wrap">'
           '<!-- Top Navigation Bar -->'
           '<div class="kc-trade-topbar">'
           '  <div class="kc-trade-top-left">'
           '    <a href="exchange.html" class="kc-p-back" title="Back to Markets">'
           '      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>'
           '    </a>'
           '    <div class="kc-trade-pair-title">'
           '      <span id="tSym">$Saka</span><span class="kc-quote">/FTR</span>'
           '      <span class="kc-trade-tag">10x</span>'
           '      <span class="kc-trade-delta" id="tDelta">+6.40%</span>'
           '    </div>'
           '  </div>'
           '  <div class="kc-trade-top-right">'
           '    <a href="asset.html" id="tChart" class="kc-icon-btn" title="Candlestick Chart">'
           '      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
           '    </a>'
           '    <button type="button" class="kc-icon-btn" title="Options">'
           '      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>'
           '    </button>'
           '  </div>'
           '</div>'
           '<div class="tgrid">')]

# ── the book ──
trade.append(T('<div data-reveal>'
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
               '</div>', ic("receipt", "ic")))

# ── the ticket ──
trade.append(T('<div data-reveal>'
               '<div class="sideseg" id="tMode">'
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

               '<div class="tfield" id="tStopWrap" hidden><div class="bd">'
               '<span class="lbl">Stop ($FTR)</span><input id="tStop" inputmode="decimal"></div>'
               '<span class="pm"><button type="button" data-step="-1" data-for="tStop" '
               'aria-label="Lower the stop">&minus;</button>'
               '<button type="button" data-step="1" data-for="tStop" aria-label="Raise the stop">+</button>'
               '</span></div>'

               '<div class="tfield" id="tLimitWrap"><div class="bd">'
               '<span class="lbl">Limit ($FTR)</span><input id="tLimit" inputmode="decimal"></div>'
               '<span class="pm"><button type="button" data-step="-1" data-for="tLimit" '
               'aria-label="Lower the price">&minus;</button>'
               '<button type="button" data-step="1" data-for="tLimit" aria-label="Raise the price">+</button>'
               '</span></div>'

               '<div class="tfield"><div class="bd">'
               '<span class="lbl">Quantity<span class="unit"> (<span id="tQtyUnit">$Saka</span>)</span></span>'
               '<input id="tQty" inputmode="numeric" value="1,000"></div>'
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
               '<span class="lbl">Amount ($FTR)</span><input id="tAmt" readonly></div></div>'

               '<div class="tline"><span>Fee (0.4%)</span><b id="tFee">—</b></div>'
               '<div class="tline"><span id="tTotLabel">Total cost</span><b id="tTot">—</b></div>'
               '<div class="tline"><span id="tAvailLabel">Avail.</span><b id="tAvail">—</b></div>'
               '<div class="tline"><span class="dash" id="tMaxLabel">Max buy</span><b id="tMax">—</b></div>'
               '<button class="bigbtn" type="button" id="tGo">Buy $Saka</button>'
               '</div>'

               # swap
               '<div class="pane" data-pane="swap">'
               '<div class="tf" id="f-swFrom"><label for="swFrom">From</label><div class="inp">@@'
               '<select id="swFrom"></select><span class="chev"></span></div>'
               '<div class="hint" id="swHold">—</div></div>'
               '<div class="tfield"><div class="bd"><span class="lbl">Shares</span>'
               '<input id="swQty" inputmode="numeric" value="500"></div>'
               '<span class="pm"><button type="button" data-step="-1" data-for="swQty" '
               'aria-label="Fewer shares">&minus;</button>'
               '<button type="button" data-step="1" data-for="swQty" aria-label="More shares">+</button>'
               '</span></div>'
               '<div class="tf" style="margin-top:12px"><label for="swTo">To</label><div class="inp">@@'
               '<select id="swTo"></select><span class="chev"></span></div></div>'
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

trade.append('</div></div></main>')

TRADE_JS = PICK_JS + r"""
document.title = 'Trade ' + A.t + ' — Fantrade';
var el = function(id){ return document.getElementById(id); };
var mode = param('side') === 'sell' ? 'sell' : 'buy', otype = 'limit', view = 'open';

if(el('tBack')) el('tBack').href = 'asset.html?a=' + encodeURIComponent(A.t);
if(el('tCoin')){
  el('tCoin').className = 'coin' + (A.c ? ' am' : '');
  el('tCoin').innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-' + (A.c ? 'whistle' : 'boot') + '"/></svg>';
}
if(el('tSym')) el('tSym').textContent = A.t;
if(el('tQtyUnit')) el('tQtyUnit').textContent = A.t;
if(el('tChart')) el('tChart').href = 'asset.html?a=' + encodeURIComponent(A.t);
el('tDelta').textContent = (A.d >= 0 ? '+' : '') + A.d.toFixed(2) + '%';
el('tDelta').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('tLimit').value = A.p.toFixed(2);
el('tStop').value = (A.p * 0.96).toFixed(2);

function drawBook(){
  book2('tAsks', 'ask', 8, function(px){ el('tLimit').value = px.toFixed(2); calc(); });
  book2('tBids', 'bid', 8, function(px){ el('tLimit').value = px.toFixed(2); calc(); });
}
drawBook();
el('tTick').addEventListener('change', function(){
  TICK = parseFloat(el('tTick').value) || 1;
  drawBook();
});
el('tLast').textContent = A.p.toFixed(2);
el('tLast').style.color = A.d >= 0 ? 'var(--lime)' : 'var(--red)';
el('tLastSub').textContent = '≈ £' + (A.p / 12.4).toFixed(2);
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
  el('tAvailLabel').textContent = 'Avail.';
  el('tAvail').textContent = mode === 'buy'
    ? fmt(s.wallet.balance) + ' $FTR'
    : (h ? h.shares.toLocaleString('en-US') + ' ' + A.t : '0 ' + A.t);
  el('tMaxLabel').textContent = mode === 'buy' ? 'Max buy' : 'Max sell';
  el('tMax').textContent = mode === 'buy'
    ? Math.floor(s.wallet.balance / (px * 1.004)).toLocaleString('en-US') + ' ' + A.t
    : (h ? h.shares.toLocaleString('en-US') + ' ' + A.t : '0 ' + A.t);
  var go = el('tGo');
  var verb = otype === 'market' ? (mode === 'buy' ? 'Buy ' : 'Sell ')
    : (mode === 'buy' ? 'Bid for ' : 'Ask for ');
  go.textContent = verb + A.t;
  go.className = 'bigbtn' + (mode === 'buy' ? '' : ' sell');
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
paintSlider(0); calc(); fillSwap(); renderLedger(); counts();
window.addEventListener('fantrade:statechange', function(){
  calc(); fillSwap(); renderLedger(); counts();
});
"""

page("trade.html", "Trade — Fantrade", "".join(trade), TRADE_JS, TRADE_CSS)

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
            '<stop offset="0%%" stop-color="#1800ad" stop-opacity=".22"/>'
            '<stop offset="100%%" stop-color="#1800ad" stop-opacity="0"/></linearGradient></defs>'
            '<polygon points="0,%d %s %d,%d" fill="url(#dvg)"/>'
            '<polyline points="%s" fill="none" stroke="#4DA6FF" stroke-width="1.4" '
            'stroke-dasharray="4 4" opacity=".8"/>'
            '<polyline points="%s" fill="none" stroke="#1800ad" stroke-width="1.8" stroke-linejoin="round"/>'
            '</svg>' % (w, h, h, " ".join(pa), w, h, " ".join(pb), " ".join(pa)))


dv = ['<main><div class="kc-home-wrap" style="padding-top:0;padding-bottom:84px">']

# Top Bar
dv.append(T('<div class="kc-topbar" style="display:flex;align-items:center;justify-content:space-between;padding:8px 0 16px">'
            '<a class="kc-icon-btn" href="leaderboard.html" aria-label="Back to Leaderboard" style="width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;color:#8E9AA8;text-decoration:none">@@</a>'
            '<div style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:17px;text-transform:uppercase">Divisions &amp; Tiers</div>'
            '<div style="width:36px"></div>'
            '</div>',
            ic("arrow", "ic")))

# Content Stack
dv.append('<div style="display:flex;flex-direction:column;gap:16px">')

dv.append(T('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad">'
            '<div class="k-label">The three tiers</div>'
            '<div class="div-card"><span class="dot" style="background:#1800ad"></span>'
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

dv.append(T('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad">'
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

dv.append(T('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad">'
            '<div class="k-label">How the table is built</div>'
            '<div class="statgrid" style="grid-template-columns:repeat(2,minmax(0,1fr));margin-top:6px;gap:12px">'
            '<div class="mini"><div class="k">01 · Raw performance</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:10px 0 0;line-height:1.6">'
            'Every appearance scores goals, assists, clean sheets, duels, and defensive actions.</p></div>'
            '<div class="mini"><div class="k">02 · Captain weighting</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:10px 0 0;line-height:1.6">'
            'The armband multiplies return by 1.5x on your chosen key asset.</p></div>'
            '<div class="mini"><div class="k">03 · Squad synergy</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:10px 0 0;line-height:1.6">'
            'Teammate links and coach shape synergy compound into the club multiplier.</p></div>'
            '<div class="mini"><div class="k">04 · Settlement</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:10px 0 0;line-height:1.6">'
            'Points convert to $FTR. Top-150 clubs are settled first on final whistle.</p></div></div>'
            '<div style="display:flex;gap:10px;margin-top:22px;flex-wrap:wrap">@@@@</div>'
            '</div></div>',
            btn("Read the scoring rules", "btn-glass", "how-it-works.html#rules"),
            btn("Improve your synergy", href="clubs.html")))

dv.append('</div></div></main>')

page("divisions.html", "Divisions — Fantrade", "".join(dv), "", """
.kc-home-wrap{max-width:680px;margin:0 auto;padding:12px 16px 84px}
.chart-x{display:flex;justify-content:space-between;font-family:'Montserrat', sans-serif;font-size:10px;
  color:var(--faint);margin-top:10px}
.div-card{border:1px solid var(--hair);background:rgba(255,255,255,.03);border-radius:18px;padding:20px;
  box-shadow:var(--inset);display:flex;gap:16px;align-items:flex-start;margin-bottom:10px}
.div-card .dot{width:9px;height:9px;border-radius:99px;flex:none;margin-top:6px}
.div-card b{display:block;font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 800;
  text-transform:uppercase;font-size:14px;margin-bottom:4px}
.div-card .r{font-size:11.5px;color:var(--faint);font-weight:300}
.div-card .pp{margin-left:auto;text-align:right;flex:none}
.div-card .pp em{font-style:normal;font-family:'Montserrat', sans-serif;font-size:15px;color:var(--lime)}
.div-card .pp span{display:block;font-weight:600;font-size:8.5px;letter-spacing:.14em;color:var(--faint);
  text-transform:uppercase;margin-top:5px}
""", app=True)


print("built divisions.html")
