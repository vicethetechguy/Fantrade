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
            "<script src=\"public/fantrade-api.js\"></script>" +
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
ASSET_CSS = """
/* KuCoin-style Asset Info & Candlestick Chart Page */
.kc-asset-wrap{max-width:680px;margin:0 auto;padding:10px 16px 84px}
.kc-asset-topbar{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:4px 0 10px;border-bottom:1px solid rgba(255,255,255,.05)}
.kc-top-left{display:flex;align-items:center;gap:10px}
.kc-icon-btn{width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);display:grid;place-items:center;color:var(--ink);cursor:pointer;text-decoration:none;transition:background .2s}
.kc-icon-btn:hover{background:rgba(255,255,255,.09)}
.kc-asset-title-box{text-align:left;margin-left:4px}
.kc-asset-pair-head{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:16px;line-height:1.1;color:var(--ink)}
.kc-asset-sub-head{font-size:11px;color:#767c82;margin-top:2px}
.kc-top-right{display:flex;align-items:center;gap:8px;margin-left:auto}
.kc-tool-ai{height:28px;padding:0 10px;border-radius:999px;background:rgba(196,248,42,.1);border:1px solid rgba(196,248,42,.3);color:var(--lime);font-family:Archivo,sans-serif;font-weight:700;font-size:11px;display:flex;align-items:center;gap:4px;cursor:pointer}

/* Main View Tabs */
.kc-asset-tabs{display:flex;align-items:center;gap:24px;border-bottom:1px solid rgba(255,255,255,.07);margin-bottom:12px}
.kc-asset-tab{background:transparent;border:0;outline:0;padding:10px 0 10px;font-family:Montserrat,sans-serif;font-size:14px;font-weight:500;color:#767c82;cursor:pointer;position:relative;transition:color .2s}
.kc-asset-tab:hover{color:var(--ink)}
.kc-asset-tab.on{color:var(--ink);font-weight:700}
.kc-asset-tab.on::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2.5px;background:var(--lime);border-radius:2px}

/* Price & 24h Summary Section */
.kc-price-sec{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:12px}
.kc-hero-px{font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:700;line-height:1;letter-spacing:-.02em;color:var(--lime)}
.kc-hero-sub{display:flex;align-items:center;gap:8px;font-family:'JetBrains Mono',monospace;font-size:12.5px;color:#767c82;margin-top:6px}
.kc-hero-delta{color:var(--lime);font-weight:600}
.kc-hero-delta.down{color:#FF3B47}
.kc-pop-badge{display:inline-flex;align-items:center;gap:5px;background:rgba(255,106,31,.1);border:1px solid rgba(255,106,31,.25);color:var(--amber);font-size:10.5px;font-weight:600;padding:3px 8px;border-radius:999px;margin-top:8px}

.kc-stats-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px 18px;min-width:170px;text-align:right}
.kc-stat-row{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:11px}
.kc-stat-row span{color:#767c82}
.kc-stat-row b{font-family:'JetBrains Mono',monospace;font-weight:600;color:var(--ink)}

/* News Ticker */
.kc-news{display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:8px;padding:7px 12px;margin-bottom:12px;font-size:11.5px;color:#8B918A}
.kc-news-txt{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kc-news-close{background:transparent;border:0;color:#767c82;cursor:pointer;padding:0 2px}

/* Timeframe Bar */
.kc-tf-bar{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px}
.kc-tf-lbl{font-size:12px;color:#767c82;font-weight:500;padding-right:4px}
.kc-tf-pills{display:flex;align-items:center;gap:14px;flex:1}
.kc-tf-pill{background:transparent;border:0;outline:0;font-family:Montserrat,sans-serif;font-size:12px;font-weight:500;color:#767c82;cursor:pointer;padding:3px 0}
.kc-tf-pill:hover{color:var(--ink)}
.kc-tf-pill.on{color:var(--ink);font-weight:700}
.kc-tf-tools{display:flex;align-items:center;gap:12px;color:#767c82}
.kc-tf-tool{background:transparent;border:0;color:inherit;cursor:pointer;padding:2px}

/* Chart Canvas */
.kc-chart-box{position:relative;background:rgba(10,11,12,.7);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:10px 4px 6px;margin-bottom:8px}
.kc-chart-svg{width:100%;height:260px;display:block}
.kc-chart-axis-x{display:flex;justify-content:space-between;padding:4px 10px 0;font-family:'JetBrains Mono',monospace;font-size:9.5px;color:#5A605B}

/* Technical Indicators Row */
.kc-ind-row{display:flex;align-items:center;gap:14px;padding:8px 0;margin-bottom:8px;overflow-x:auto;scrollbar-width:none}
.kc-ind-chip{background:transparent;border:0;outline:0;font-family:Montserrat,sans-serif;font-size:11px;font-weight:500;color:#686e74;cursor:pointer;padding:2px 0}
.kc-ind-chip:hover{color:var(--ink)}
.kc-ind-chip.on{color:var(--lime);font-weight:600}
.kc-ind-sep{color:rgba(255,255,255,.12);font-size:11px}

/* Lower Section Tabs */
.kc-low-tabs{display:flex;align-items:center;gap:20px;border-bottom:1px solid rgba(255,255,255,.07);margin-bottom:10px}
.kc-low-tab{background:transparent;border:0;outline:0;padding:8px 0;font-family:Montserrat,sans-serif;font-size:13px;font-weight:500;color:#767c82;cursor:pointer;position:relative}
.kc-low-tab:hover{color:var(--ink)}
.kc-low-tab.on{color:var(--ink);font-weight:700}
.kc-low-tab.on::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;background:var(--lime);border-radius:2px}

/* Order Book Pane */
.kc-pane{display:none}
.kc-pane.on{display:block}
.kc-book-row-head{display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:10.5px;color:#767c82;padding:0 2px 6px;border-bottom:1px solid rgba(255,255,255,.05)}
.kc-book-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:6px}
.kc-b-line{display:flex;justify-content:space-between;position:relative;height:21px;align-items:center;font-family:'JetBrains Mono',monospace;font-size:11px;padding:0 4px}
.kc-b-line .depth{position:absolute;top:0;bottom:0;right:0;pointer-events:none;opacity:.15;border-radius:2px}
.kc-b-line.bid span:first-child{color:var(--lime);font-weight:600}
.kc-b-line.bid .depth{background:var(--lime)}
.kc-b-line.ask span:first-child{color:#FF3B47;font-weight:600}
.kc-b-line.ask .depth{background:#FF3B47}
.kc-b-line span:last-child{color:var(--dim)}

/* Fixed Bottom Action Bar */
.kc-action-dock{position:fixed;left:50%;bottom:58px;transform:translateX(-50%);z-index:74;width:100%;max-width:680px;box-sizing:border-box;background:rgba(8,9,10,.95);backdrop-filter:blur(20px);border-top:1px solid rgba(255,255,255,.08);padding:8px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.kc-dock-tools{display:flex;align-items:center;gap:16px}
.kc-dock-tool{display:flex;flex-direction:column;align-items:center;gap:2px;text-decoration:none;color:#767c82;font-size:9.5px}
.kc-dock-tool:hover{color:var(--ink)}
.kc-dock-tool .ic{width:18px;height:18px}
.kc-dock-btns{display:flex;align-items:center;gap:10px;flex:1;max-width:320px}
.kc-btn-buy{flex:1;height:40px;background:var(--lime);color:#0A0D03;border-radius:8px;font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:14px;display:grid;place-items:center;text-decoration:none;text-transform:uppercase;letter-spacing:.02em}
.kc-btn-sell{flex:1;height:40px;background:#FF3B47;color:#fff;border-radius:8px;font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:14px;display:grid;place-items:center;text-decoration:none;text-transform:uppercase;letter-spacing:.02em}
"""

asset = [T('<main><div class="kc-asset-wrap">'
           '<!-- Top Navigation Bar -->'
           '<div class="kc-asset-topbar">'
           '  <div class="kc-top-left">'
           '    <a href="exchange.html" class="kc-icon-btn" title="Back">'
           '      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>'
           '    </a>'
           '    <button type="button" class="kc-icon-btn" title="Menu">'
           '      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/></svg>'
           '    </button>'
           '    <div class="kc-asset-title-box">'
           '      <div class="kc-asset-pair-head"><span id="aTitlePair">SOL/USDT</span></div>'
           '      <div class="kc-asset-sub-head" id="aTitleSub">Solana</div>'
           '    </div>'
           '  </div>'
           '  <div class="kc-top-right">'
           '    <button type="button" class="kc-tool-ai" title="AI Market Insight">✨ Ai</button>'
           '    <button type="button" class="kc-icon-btn" id="aAlertBtn" title="Alert">'
           '      @@'
           '    </button>'
           '    <button type="button" class="kc-icon-btn" id="aFav" title="Favorite">'
           '      @@'
           '    </button>'
           '  </div>'
           '</div>'
           '<!-- Primary Tabs -->'
           '<div class="kc-asset-tabs" id="aMainTabs">'
           '  <button type="button" class="kc-asset-tab on" data-tab="chart">Chart</button>'
           '  <button type="button" class="kc-asset-tab" data-tab="feed">Feed</button>'
           '  <button type="button" class="kc-asset-tab" data-tab="info">Coin Info</button>'
           '  <button type="button" class="kc-asset-tab" data-tab="recom">Recommendations</button>'
           '</div>'
           '<!-- Price & 24h Summary Section -->'
           '<div class="kc-price-sec">'
           '  <div>'
           '    <div class="kc-hero-px" id="aPx">102.64</div>'
           '    <div class="kc-hero-sub">'
           '      <span id="aSubUsd">≈$102.61</span>'
           '      <span class="kc-hero-delta" id="aDelta">+2.99%</span>'
           '    </div>'
           '    <div class="kc-pop-badge" id="aPopBadge">🔥 Top 16 by popularity</div>'
           '  </div>'
           '  <div class="kc-stats-grid">'
           '    <div class="kc-stat-row"><span>24h High</span><b id="sHigh">104.82</b></div>'
           '    <div class="kc-stat-row"><span>24h Low</span><b id="sLow">99.21</b></div>'
           '    <div class="kc-stat-row"><span>24h Vol (<span id="sVolBase">SOL</span>)</span><b id="sVolS">384.44K</b></div>'
           '    <div class="kc-stat-row"><span>24h Vol (<span id="sVolQuote">USDT</span>)</span><b id="sVol">39.24M</b></div>'
           '  </div>'
           '</div>'
           '<!-- News Ticker -->'
           '<div class="kc-news" id="newsTicker">'
           '  <span>📢</span>'
           '  <span class="kc-news-txt">Grayscale Launches Digital Asset Model Portfolios with Four Initial Strategies...</span>'
           '  <button type="button" class="kc-news-close" onclick="document.getElementById(\'newsTicker\').style.display=\'none\'">✕</button>'
           '</div>'
           '<!-- Timeframe Bar -->'
           '<div class="kc-tf-bar">'
           '  <span class="kc-tf-lbl">Time</span>'
           '  <div class="kc-tf-pills" id="aTf">'
           '    <button type="button" class="kc-tf-pill on" data-t="15m">15m</button>'
           '    <button type="button" class="kc-tf-pill" data-t="1h">1h</button>'
           '    <button type="button" class="kc-tf-pill" data-t="8h">8h</button>'
           '    <button type="button" class="kc-tf-pill" data-t="1D">1D</button>'
           '    <button type="button" class="kc-tf-pill" data-t="1W">More ▾</button>'
           '  </div>'
           '  <div class="kc-tf-tools">'
           '    <button type="button" class="kc-tf-tool" title="Settings">⚙</button>'
           '    <button type="button" class="kc-tf-tool" title="Full Chart">⛶</button>'
           '  </div>'
           '</div>'
           '<!-- Candlestick Chart Area -->'
           '<div class="kc-chart-box">'
           '  <div id="aChart" class="kc-chart-svg"></div>'
           '  <div class="kc-chart-axis-x" id="aCx">'
           '    <span>09-14 16:00</span><span>09-14 19:15</span><span>09-14 22:30</span><span>09-15 01:45</span>'
           '  </div>'
           '</div>'
           '<!-- Indicators -->'
           '<div class="kc-ind-row">'
           '  <button type="button" class="kc-ind-chip on">MA</button>'
           '  <button type="button" class="kc-ind-chip">EMA</button>'
           '  <button type="button" class="kc-ind-chip">BOLL</button>'
           '  <span class="kc-ind-sep">|</span>'
           '  <button type="button" class="kc-ind-chip on">VOL</button>'
           '  <button type="button" class="kc-ind-chip">MACD</button>'
           '  <button type="button" class="kc-ind-chip">RSI</button>'
           '  <button type="button" class="kc-ind-chip">KDJ</button>'
           '</div>'
           '<!-- Lower Panes -->'
           '<div class="kc-low-tabs" id="aPanes">'
           '  <button type="button" class="kc-low-tab on" data-p="book">Order Book</button>'
           '  <button type="button" class="kc-low-tab" data-p="trades">Trade History</button>'
           '  <button type="button" class="kc-low-tab" data-p="stats">Data Analysis</button>'
           '</div>'
           '<div class="kc-pane on" data-pane="book">'
           '  <div class="kc-book-row-head"><span>Bid Price (Buy)</span><span style="text-align:right">Ask Price (Sell)</span></div>'
           '  <div class="kc-book-grid">'
           '    <div id="aBids"></div>'
           '    <div id="aAsks"></div>'
           '  </div>'
           '</div>'
           '<div class="kc-pane" data-pane="trades">'
           '  <div class="tr-row" style="color:var(--faint);font-size:9.5px;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,.05)">'
           '    <span>Price</span><span style="text-align:center">Amount</span><span style="text-align:right">Time</span>'
           '  </div>'
           '  <div id="aTrades"></div>'
           '</div>'
           '<div class="kc-pane" data-pane="stats">'
           '  <div class="statgrid">'
           '    <div class="mini"><div class="k">Market Cap</div><div class="v" id="sCap">—</div></div>'
           '    <div class="mini"><div class="k">Held by Fans</div><div class="v lime" id="sHeld">—</div></div>'
           '    <div class="mini"><div class="k">Fixed Supply</div><div class="v">10.00M</div></div>'
           '    <div class="mini"><div class="k">52w High</div><div class="v" id="sYH">—</div></div>'
           '    <div class="mini"><div class="k">52w Low</div><div class="v" id="sYL">—</div></div>'
           '    <div class="mini"><div class="k">Popularity</div><div class="v">#16</div></div>'
           '  </div>'
           '</div>'
           '</div>'
           '<!-- Fixed Bottom Trading Bar -->'
           '<div class="kc-action-dock">'
           '  <div class="kc-dock-tools">'
           '    <a href="trade.html" class="kc-dock-tool">'
           '      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/></svg>'
           '      <span>Futures</span>'
           '    </a>'
           '    <a href="trade.html" class="kc-dock-tool">'
           '      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'
           '      <span>Grid</span>'
           '    </a>'
           '    <a href="trade.html" class="kc-dock-tool">'
           '      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/></svg>'
           '      <span>Margin</span>'
           '    </a>'
           '    <a href="exchange.html" class="kc-dock-tool">'
           '      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>'
           '      <span>Compare</span>'
           '    </a>'
           '  </div>'
           '  <div class="kc-dock-btns">'
           '    <a href="#" id="aBuy" class="kc-btn-buy">Buy</a>'
           '    <a href="#" id="aSell" class="kc-btn-sell">Sell</a>'
           '  </div>'
           '</div>'
           '</main>',
           ic("bell", "ic"),
           ic("star", "ic"))]

ASSET_JS = PICK_JS + r"""
function el(id){ return document.getElementById(id); }

var quote = A.q || (A.t.indexOf('$') === 0 ? 'FTR' : 'USDT');
var symClean = A.t.replace('$', '');

el('aTitlePair').textContent = symClean + '/' + quote;
el('aTitleSub').textContent = A.n;
el('sVolBase').textContent = symClean;
el('sVolQuote').textContent = quote;

var pxText = (A.p > 999 ? A.p.toLocaleString('en-US', {minimumFractionDigits: 1, maximumFractionDigits: 2}) : A.p.toFixed(A.p < 1 ? 4 : 2));
el('aPx').textContent = pxText;
el('aSubUsd').textContent = '≈$' + (A.p * 0.9997).toFixed(A.p < 1 ? 4 : 2);
var up = A.d >= 0;
el('aDelta').textContent = (up ? '+' : '') + A.d.toFixed(2) + '%';
el('aDelta').className = 'kc-hero-delta' + (up ? '' : ' down');

el('sHigh').textContent = (A.h || (A.p * 1.025)).toFixed(A.p < 1 ? 4 : 2);
el('sLow').textContent = (A.low || (A.p * 0.97)).toFixed(A.p < 1 ? 4 : 2);
el('sVolS').textContent = A.vol || '384.44K';
el('sVol').textContent = A.cap || '39.24M';

var capEl = el('sCap');
if(capEl) capEl.textContent = A.cap || '39.24M';
var heldEl = el('sHeld');
if(heldEl) heldEl.textContent = (A.p * 38400).toLocaleString('en-US', {maximumFractionDigits: 0});
var yhEl = el('sYH');
if(yhEl) yhEl.textContent = (A.p * 1.4).toFixed(2);
var ylEl = el('sYL');
if(ylEl) ylEl.textContent = (A.p * 0.65).toFixed(2);

el('aBuy').href = 'trade.html?a=' + encodeURIComponent(A.t) + '&side=buy';
el('aSell').href = 'trade.html?a=' + encodeURIComponent(A.t) + '&side=sell';

// Timeframe setup
var TF = {
  '15m': [32, 0.003, 14],
  '1h':  [36, 0.006, 28],
  '8h':  [40, 0.012, 42],
  '1D':  [45, 0.024, 60],
  '1W':  [48, 0.048, 90]
};
var LABELS = {
  '15m': ['09-14 16:00', '09-14 19:15', '09-14 22:30', '09-15 01:45'],
  '1h':  ['09-12 12:00', '09-13 00:00', '09-13 12:00', '09-14 00:00'],
  '8h':  ['09-08', '09-10', '09-12', '09-14'],
  '1D':  ['Aug 20', 'Aug 28', 'Sep 05', 'Sep 14'],
  '1W':  ['May 2026', 'Jun 2026', 'Jul 2026', 'Aug 2026']
};

function drawKucoinCandles(host, data){
  if(!host || !data || !data.length) return;
  var w = 680, h = 260, padR = 64, plot = h - 36;
  var hi = Math.max.apply(null, data.map(function(d){ return d.h; }));
  var lo = Math.min.apply(null, data.map(function(d){ return d.l; }));
  var rng = (hi - lo) || 1;
  hi += rng * 0.05; lo -= rng * 0.05; rng = hi - lo;
  var cw = (w - padR) / data.length, bw = Math.max(2, cw * 0.62);
  function y(v){ return plot - ((v - lo) / rng) * plot + 8; }

  var parts = [], grid = [];
  for(var g = 0; g <= 3; g++){
    var gv = lo + (rng / 3) * g, gy = y(gv);
    grid.push('<line x1="0" y1="' + gy.toFixed(1) + '" x2="' + (w - padR) + '" y2="' + gy.toFixed(1) + '" stroke="rgba(255,255,255,.05)" stroke-width="1"/>');
    grid.push('<text x="' + (w - padR + 6) + '" y="' + (gy + 3).toFixed(1) + '" fill="#5A605B" font-size="9.5" font-family="JetBrains Mono, monospace">' + gv.toFixed(gv < 1 ? 4 : 2) + '</text>');
  }

  var maxCandle = data[0], minCandle = data[0];
  data.forEach(function(d, i){
    if(d.h > maxCandle.h){ maxCandle = d; maxCandle._i = i; }
    if(d.l < minCandle.l){ minCandle = d; minCandle._i = i; }

    var x = i * cw + cw / 2, up = d.c >= d.o;
    var col = up ? '#C4F82A' : '#FF3B47';
    var top = y(Math.max(d.o, d.c)), bot = y(Math.min(d.o, d.c));
    parts.push('<line x1="' + x.toFixed(1) + '" y1="' + y(d.h).toFixed(1) + '" x2="' + x.toFixed(1) + '" y2="' + y(d.l).toFixed(1) + '" stroke="' + col + '" stroke-width="1.2"/>');
    parts.push('<rect x="' + (x - bw / 2).toFixed(1) + '" y="' + top.toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.max(1.5, bot - top).toFixed(1) + '" fill="' + col + '" rx="0.5"/>');
  });

  // High marker callout (104.82 ---)
  var hx = (maxCandle._i || 0) * cw + cw / 2, hy = y(maxCandle.h);
  parts.push('<line x1="' + Math.max(0, hx - 24) + '" y1="' + hy.toFixed(1) + '" x2="' + (hx + 24) + '" y2="' + hy.toFixed(1) + '" stroke="#8B918A" stroke-dasharray="2 2" stroke-width="1"/>');
  parts.push('<text x="' + (hx - 4) + '" y="' + (hy - 4).toFixed(1) + '" fill="#8B918A" font-size="9" text-anchor="end" font-family="JetBrains Mono, monospace">' + maxCandle.h.toFixed(maxCandle.h < 1 ? 4 : 2) + '</text>');

  // Low marker callout (101.21 ---)
  var lx = (minCandle._i || 0) * cw + cw / 2, ly = y(minCandle.l);
  parts.push('<line x1="' + Math.max(0, lx - 24) + '" y1="' + ly.toFixed(1) + '" x2="' + (lx + 24) + '" y2="' + ly.toFixed(1) + '" stroke="#8B918A" stroke-dasharray="2 2" stroke-width="1"/>');
  parts.push('<text x="' + (lx + 4) + '" y="' + (ly + 11).toFixed(1) + '" fill="#8B918A" font-size="9" font-family="JetBrains Mono, monospace">' + minCandle.l.toFixed(minCandle.l < 1 ? 4 : 2) + '</text>');

  // Current price line & right badge
  var last = data[data.length - 1];
  var cy = y(last.c);
  parts.push('<line x1="0" y1="' + cy.toFixed(1) + '" x2="' + (w - padR) + '" y2="' + cy.toFixed(1) + '" stroke="#8B918A" stroke-dasharray="2 2" stroke-width="1" opacity=".7"/>');
  parts.push('<rect x="' + (w - padR) + '" y="' + (cy - 12).toFixed(1) + '" width="62" height="24" rx="4" fill="#14171A" stroke="#32383e" stroke-width="1"/>');
  parts.push('<text x="' + (w - padR + 31) + '" y="' + (cy - 1).toFixed(1) + '" fill="#F4F6F1" font-size="9" font-weight="600" text-anchor="middle" font-family="JetBrains Mono, monospace">' + last.c.toFixed(last.c < 1 ? 4 : 2) + '</text>');
  parts.push('<text x="' + (w - padR + 31) + '" y="' + (cy + 9).toFixed(1) + '" fill="#767c82" font-size="7.5" text-anchor="middle" font-family="JetBrains Mono, monospace">06:37</text>');

  host.innerHTML = '<svg viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">' + grid.join('') + parts.join('') + '</svg>';
}

function tf(t){
  var cfg = TF[t] || TF['15m'];
  var data = candleData(cfg[0], A.p * 0.96, cfg[1], cfg[2]);
  var drift = A.p / data[data.length - 1].c;
  data.forEach(function(d){ d.o *= drift; d.h *= drift; d.l *= drift; d.c *= drift; });
  drawKucoinCandles(el('aChart'), data);
  el('aCx').innerHTML = (LABELS[t] || LABELS['15m']).map(function(l){ return '<span>' + l + '</span>'; }).join('');
}

document.querySelectorAll('#aTf button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#aTf button').forEach(function(x){ x.classList.remove('on'); });
    b.classList.add('on');
    tf(b.dataset.t);
  });
});
tf('15m');

// Main view tabs
document.querySelectorAll('#aMainTabs button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#aMainTabs button').forEach(function(x){ x.classList.remove('on'); });
    b.classList.add('on');
  });
});

// Lower panes
document.querySelectorAll('#aPanes button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#aPanes button').forEach(function(x){ x.classList.remove('on'); });
    b.classList.add('on');
    document.querySelectorAll('[data-pane]').forEach(function(p){
      p.classList.toggle('on', p.dataset.pane === b.dataset.p);
    });
  });
});

// Render Order book depth
function renderKucoinBook(){
  var px = A.p;
  var bids = [], asks = [];
  for(var i = 0; i < 6; i++){
    var bPx = px * (1 - (i + 1) * 0.0018);
    var bAmt = Math.round(1400 + Math.abs(Math.sin(i * 2.3)) * 8200);
    var bW = Math.min(95, 20 + i * 14);
    bids.push('<div class="kc-b-line bid">'
      + '<span>' + bPx.toFixed(bPx < 1 ? 4 : 2) + '</span>'
      + '<span>' + bAmt.toLocaleString('en-US') + '</span>'
      + '<div class="depth" style="width:' + bW + '%"></div></div>');

    var aPx = px * (1 + (i + 1) * 0.0018);
    var aAmt = Math.round(1200 + Math.abs(Math.cos(i * 1.9)) * 7500);
    var aW = Math.min(95, 25 + i * 12);
    asks.push('<div class="kc-b-line ask">'
      + '<span>' + aPx.toFixed(aPx < 1 ? 4 : 2) + '</span>'
      + '<span>' + aAmt.toLocaleString('en-US') + '</span>'
      + '<div class="depth" style="width:' + aW + '%"></div></div>');
  }
  el('aBids').innerHTML = bids.join('');
  el('aAsks').innerHTML = asks.join('');
}
renderKucoinBook();

// Trade history
(function(){
  var out = [];
  for(var i = 0; i < 10; i++){
    var up = Math.sin(i * 1.9) > 0;
    var p = A.p * (1 + (Math.sin(i * 3.1) * 0.003));
    out.push('<div class="tr-row" style="display:flex;justify-content:space-between;padding:5px 0;font-family:JetBrains Mono,monospace;font-size:11px">'
      + '<span style="color:' + (up ? 'var(--lime)' : '#FF3B47') + '">' + p.toFixed(p < 1 ? 4 : 2) + '</span>'
      + '<span style="color:var(--dim)">' + fmt(900 + Math.abs(Math.cos(i * 2.2)) * 7400) + '</span>'
      + '<span style="color:var(--faint)">' + (i * 2 + 1) + 'm ago</span></div>');
  }
  el('aTrades').innerHTML = out.join('');
})();

// Favorite button
var fav = el('aFav');
if(fav){
  fav.style.color = FT.isFav(A.t) ? 'var(--lime)' : '#767c82';
  fav.addEventListener('click', function(){
    var on = FT.toggleFav(A.t);
    fav.style.color = on ? 'var(--lime)' : '#767c82';
  });
}
"""

page("asset.html", "Market — Fantrade", "".join(asset), ASSET_JS, ASSET_CSS)

# ══════════════════════════════════════════════════════════════════
# TRADE — the terminal: bid, buy, sell, swap
# ══════════════════════════════════════════════════════════════════
TRADE_CSS = """
@media (max-width:640px){
  /* drop the "placed" column so side, size, price and the action stay on one row */
  #tLedger .dh,#tLedger .dr{grid-template-columns:52px 1fr 1fr 76px!important;gap:8px;padding:12px 0}
  #tLedger .dh>*:nth-child(4),#tLedger .dr>*:nth-child(4){display:none}
  #tLedger .dh>*:nth-child(5),#tLedger .dr>*:nth-child(5){text-align:right}
  #tLedger .dh{font-size:8px;letter-spacing:.12em}
}
#tLedger .dh,#tLedger .dr{padding-left:0;padding-right:0}
/* The terminal reads like a spot exchange: the book and the ticket side by
   side at every width, then the ledger under them. */
.tgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.16fr);gap:16px;align-items:start}
@media (min-width:1100px){.tgrid{grid-template-columns:minmax(0,360px) minmax(0,1fr);gap:34px}}
@media (max-width:420px){.tgrid{gap:10px}}

.pairhead{display:flex;align-items:center;gap:13px;flex-wrap:wrap}
.pairhead .coin{width:38px;height:38px}
.pairhead .coin .ic{width:18px;height:18px}
.pairhead .pr{font-family:Archivo;font-variation-settings:'wdth' 120,'wght' 800;text-transform:uppercase;
  font-size:clamp(17px,2.4vw,22px);line-height:1;white-space:nowrap}
.pairhead .pr em{font-style:normal;color:var(--faint)}
.pairhead .dlt{font-family:'JetBrains Mono',monospace;font-size:13px}
.pairhead .chip{margin-left:auto;display:flex;align-items:center;gap:8px;flex:none}
.pairhead .chip a{display:grid;place-items:center;width:34px;height:34px;border-radius:11px;
  border:1px solid var(--hair);background:rgba(255,255,255,.04);color:var(--dim);box-shadow:var(--inset);
  transition:all .5s var(--ease)}
.pairhead .chip a:hover{color:var(--lime);border-color:rgba(196,248,42,.4)}
.pairhead .chip .ic{width:16px;height:16px}

/* order book footer: tick size + depth split */
.bkfoot{display:flex;align-items:center;gap:8px;margin-top:12px}
.ticksel{display:flex;align-items:center;gap:8px;flex:1;min-width:0;border:1px solid var(--hair);
  border-radius:10px;background:rgba(255,255,255,.03);box-shadow:var(--inset);padding:6px 10px}
.ticksel select{flex:1;min-width:0;border:0;background:transparent;color:var(--ink);outline:none;
  cursor:pointer;font-family:'JetBrains Mono',monospace;font-size:11.5px}
.ticksel select option{background:#0A0B0C}
.ticksel .chev{flex:none}
.bkbtn{display:grid;place-items:center;width:36px;height:34px;flex:none;border-radius:10px;
  border:1px solid var(--hair);background:rgba(255,255,255,.04);color:var(--dim);box-shadow:var(--inset);
  transition:all .5s var(--ease)}
.bkbtn:hover{color:var(--lime);border-color:rgba(196,248,42,.4)}
.bkbtn .ic{width:15px;height:15px}
/* the ladder tints stay behind the numbers, not in front of them */
.book2 .b2row i{opacity:.72}
.book2 .last span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (max-width:420px){
  .book2 .bh{font-size:8px}
  .b2row{padding:4px 5px;font-size:10.5px}
  .book2 .last b{font-size:14px}
  .book2 .last span{font-size:9.5px}
  .bkfoot{gap:6px}
  .ticksel{padding:6px 8px}
  .ticksel select{font-size:10.5px}
}

/* buy / sell / swap */
.sideseg{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:4px;border-radius:14px;
  background:rgba(255,255,255,.035);border:1px solid var(--hair);box-shadow:var(--inset);margin-bottom:12px}
.sideseg button{border:0;background:transparent;color:var(--faint);border-radius:11px;padding:11px 0;
  cursor:pointer;font-family:Montserrat,sans-serif;font-weight:600;font-size:11px;letter-spacing:.12em;
  text-transform:uppercase;transition:all .45s var(--ease)}
.sideseg button:hover{color:var(--ink)}
.sideseg button[aria-pressed="true"]{background:rgba(196,248,42,.14);color:var(--lime);
  box-shadow:inset 0 0 0 1px rgba(196,248,42,.34)}
.sideseg button[data-m="sell"][aria-pressed="true"]{background:rgba(255,94,94,.14);color:var(--red);
  box-shadow:inset 0 0 0 1px rgba(255,94,94,.34)}
.sideseg button[data-m="swap"][aria-pressed="true"]{background:rgba(255,255,255,.09);color:var(--ink);
  box-shadow:inset 0 0 0 1px var(--hair-2)}

/* a field carries its label above the value, steppers on the right */
.tfield{display:flex;align-items:center;gap:10px;border:1px solid var(--hair);border-radius:12px;
  background:rgba(255,255,255,.03);box-shadow:var(--inset);padding:9px 4px 9px 13px;margin-bottom:8px}
.tfield .bd{flex:1;min-width:0}
.tfield .lbl{display:block;font-weight:600;font-size:8.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--faint);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tfield input{display:block;width:100%;border:0;background:transparent;color:var(--ink);outline:none;
  font-family:'JetBrains Mono',monospace;font-size:15px;padding:4px 0 0}
.tfield input::placeholder{color:var(--faint)}
.tfield input:read-only{color:var(--dim)}
.tfield .pm{flex:none;display:flex;align-items:stretch;align-self:stretch}
.tfield .pm button{width:34px;border:0;background:transparent;color:var(--dim);cursor:pointer;
  font-size:17px;line-height:1;transition:color .4s var(--ease)}
.tfield .pm button:first-child{border-right:1px solid var(--hair)}
.tfield .pm button:hover{color:var(--lime)}
.tfield[hidden]{display:none}

.tline{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:7px 0;font-size:11.5px;
  color:var(--faint)}
.tline b{font-family:'JetBrains Mono',monospace;font-weight:400;color:var(--ink);font-size:12px}
.tline .dash{border-bottom:1px dashed var(--hair-2);padding-bottom:1px}
.bigbtn{display:block;width:100%;border:0;border-radius:14px;padding:16px 0;margin-top:14px;cursor:pointer;
  font-family:Montserrat,sans-serif;font-weight:600;font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;
  background:var(--lime);color:#0A0D03;box-shadow:var(--inset),0 16px 38px -16px rgba(196,248,42,.75);
  transition:filter .4s var(--ease)}
.bigbtn:hover{filter:brightness(1.06)}
.bigbtn.sell{background:var(--red);color:#fff;box-shadow:var(--inset),0 16px 38px -16px rgba(255,94,94,.7)}
.bigbtn.neutral{background:rgba(255,255,255,.08);color:var(--ink);border:1px solid var(--hair-2);
  box-shadow:var(--inset)}

@media (max-width:420px){
  .tfield .lbl .unit{display:none}
  .tfield{padding:8px 2px 8px 10px}
  .tfield input{font-size:13.5px}
  .tfield .pm button{width:28px;font-size:15px}
  .sideseg button{font-size:9.5px;letter-spacing:.08em;padding:10px 0}
}
"""

trade = [T('<main><section class="app-head" style="padding:92px 0 14px"><div class="wrap">'
           '<a class="crumb" href="asset.html" id="tBack" aria-label="Market page">@@Market</a>'
           '<div class="pairhead" data-reveal style="margin-top:13px">'
           '<span class="coin" id="tCoin">@@</span>'
           '<div class="pr"><span id="tSym">$Saka</span><em>/$FTR</em></div>'
           '<div class="dlt" id="tDelta">+6.40%</div>'
           '<span class="chip"><a href="asset.html" id="tChart" aria-label="Open the chart">@@</a></span>'
           '</div></div></section>',
           ic("arrow", "ic"), ic("boot", "ic"), ic("market", "ic"))]

trade.append('<section style="padding:0 0 120px"><div class="wrap"><div class="tgrid">')

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

trade.append('</div></section></main>')

TRADE_JS = PICK_JS + r"""
document.title = 'Trade ' + A.t + ' — Fantrade';
var el = function(id){ return document.getElementById(id); };
var mode = param('side') === 'sell' ? 'sell' : 'buy', otype = 'limit', view = 'open';

el('tBack').href = 'asset.html?a=' + encodeURIComponent(A.t);
el('tCoin').className = 'coin' + (A.c ? ' am' : '');
el('tCoin').innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-' + (A.c ? 'whistle' : 'boot')
  + '"/></svg>';
el('tSym').textContent = A.t;
el('tQtyUnit').textContent = A.t;
el('tChart').href = 'asset.html?a=' + encodeURIComponent(A.t);
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
            '<stop offset="0%%" stop-color="#C4F82A" stop-opacity=".22"/>'
            '<stop offset="100%%" stop-color="#C4F82A" stop-opacity="0"/></linearGradient></defs>'
            '<polygon points="0,%d %s %d,%d" fill="url(#dvg)"/>'
            '<polyline points="%s" fill="none" stroke="#4DA6FF" stroke-width="1.4" '
            'stroke-dasharray="4 4" opacity=".8"/>'
            '<polyline points="%s" fill="none" stroke="#C4F82A" stroke-width="1.8" stroke-linejoin="round"/>'
            '</svg>' % (w, h, h, " ".join(pa), w, h, " ".join(pb), " ".join(pa)))


dv = [T('<main><section class="app-head" style="padding-bottom:26px"><div class="wrap">'
        '<div data-reveal>@@</div>'
        '<h1 data-reveal style="margin-top:20px">Divisions</h1>'
        '</div></section>',
        crumb("leaderboard.html", "Back to the table"))]

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
