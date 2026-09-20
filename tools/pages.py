# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app_design import apply_design, intro
from common import head, atmosphere, nav, footer, ic, flag, JS_SHELL

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.makedirs(OUT, exist_ok=True)

def T(tpl, *args):
    """Template with @@ placeholders — avoids %-escaping every literal percent in HTML."""
    out = tpl
    for a in args:
        out = out.replace("@@", str(a), 1)
    return out

ARROW = '<span class="cap">' + ic("arrow", "ic") + '</span>'


def crumb(href, label):
    return '<a class="crumb" href="%s">%s%s</a>' % (href, ic("arrow", "ic"), label)


def btn(label, cls="btn-lime", href="#", tag="a", extra=""):
    o = '<%s class="btn %s" %s %s>%s%s</%s>' % (
        tag, cls, ('href="%s"' % href) if tag == "a" else "", extra, label, ARROW, tag)
    return o


def page(fname, title, body, js="", css="", app=False):
    tail = footer() if fname == "index.html" else ""
    html = (head(title, css, "app" if app else "") + atmosphere() + nav(fname, app) +
            body + tail + "<script src=\"public/fantrade-api.js\"></script><script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
    html = apply_design(fname, html)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)


# ══════════════════════════════════════════════════════════
# 1. LANDING
# ══════════════════════════════════════════════════════════
from landing import build_landing


PITCH_JS = r"""
var XI=[[['ST','$Haaland']],[['LW','$Vinicius'],['CAM','$Bruno',1],['RW','$Saka']],
        [['CM','$Rice'],['CM','$Odegaard']],
        [['LB','$Davies'],['CB','$VanDijk'],['CB','$Saliba'],['RB','$White']],[['GK','$Raya']]];
var BENCH=[['GK','$Alisson'],['DEF','$Gabriel'],['MID','$Pedri'],['MID','$Musiala']];
var ARM="<svg class='ic' aria-hidden='true'><use href='#i-armband'/></svg>";
function pitchHTML(){
  var h="<div class='pitch-head'><span class='crest'>ZFC</span><div><div class='name'>Zero FC</div>"+
    "<div class='meta'>4-3-3 · Emirates of the North · Est. 2026</div></div>"+
    "<div class='coach'><span class='player-face'>"+playerPhoto('$Arteta','Mikel Arteta')+"</span>"+
    "<div><b>$Arteta</b><span>Coach · owned</span></div></div></div>";
  XI.forEach(function(row){
    h+="<div class='line-row'>";
    row.forEach(function(p){
      h+="<div class='chip"+(p[2]?" cap":"")+"'><div class='pos'>"+p[0]+"</div><span class='player-face'>"+playerPhoto(p[1],p[1])+"</span><div class='nm'>"+p[1]+"</div>"+
         (p[2]?"<div class='arm'>"+ARM+"Captain ×1.5</div>":"")+"</div>";
    });
    h+="</div>";
  });
  h+="<div class='bench'><div class='k-label'>Bench · auto-subs if a starter doesn't play</div><div class='bench-row'>";
  BENCH.forEach(function(p){ h+="<div class='chip sm'><div class='pos'>"+p[0]+"</div><span class='player-face'>"+playerPhoto(p[1],p[1])+"</span><div class='nm'>"+p[1]+"</div></div>"; });
  h+="<button class='chip sm empty' id='addSub' aria-expanded='false'><div class='pos'>Sub 5</div><div class='nm'>+ Add</div></button></div>"+
     "<div class='own-alert' id='ownAlert' role='status'><div><p>You hold <strong>0</strong> of 10,000,000 <strong>$Mbapp\u00e9</strong> shares.</p>"+
     "<p style='color:var(--dim);font-size:12px;font-weight:300;margin-top:4px'>Buy shares to unlock him for Zero FC. Players can't be borrowed.</p></div>"+
     "<a class='btn btn-lime btn-sm' href='exchange.html'>Buy $Mbapp\u00e9<span class='cap'><svg class='ic'><use href='#i-arrow'/></svg></span></a></div></div>";
  return h;
}
var pm=document.getElementById('pitchMount');
if(pm){ pm.innerHTML=pitchHTML();
  var add=document.getElementById('addSub'), al=document.getElementById('ownAlert');
  add.addEventListener('click',function(){ var o=al.classList.toggle('show'); add.setAttribute('aria-expanded',o?'true':'false'); });
}
var book=document.getElementById('book');
if(book){
  book.innerHTML=ASSETS.slice(0,7).map(function(a,i){
    return "<div class='brow' data-i='"+i+"'><div class='asset'><span class='badge"+(a.c?" coach":"")+"'>"+
      "<svg class='ic'><use href='#i-"+(a.c?'whistle':'boot')+"'/></svg></span><div><div class='t-sym'>"+a.t+
      "</div><div class='t-nm'>"+a.n+"</div></div></div><div class='tick' data-px>"+a.p.toFixed(2)+
      "</div><div class='tick "+(a.d>=0?'up':'down')+"' data-dx>"+(a.d>=0?'+':'')+a.d.toFixed(1)+"%</div><div>"+
      spark(a.d>=0,94,26)+"</div></div>";
  }).join('');
  liveTicks('.brow');
}
var band=document.getElementById('band');
if(band){
  var s=ASSETS.map(function(a){ return "<span><b>"+a.t+"</b> "+a.p.toFixed(2)+" <em style='font-style:normal;color:"+
    (a.d>=0?'#1800ad':'#FF5E5E')+"'>"+(a.d>=0?'+':'')+a.d.toFixed(1)+"%</em></span>"; }).join('');
  band.innerHTML=s+s;
}
"""
build_landing()


# ══════════════════════════════════════════════════════════
# 2. EXCHANGE
# ══════════════════════════════════════════════════════════
EX_CSS = """
/* KuCoin-style Markets / Exchange Page */
.kc-ex-wrap{max-width:680px;margin:0 auto;padding:12px 16px 84px}
.kc-top-bar{display:flex;align-items:center;gap:12px;margin-bottom:12px}
.kc-search-box{flex:1;display:flex;align-items:center;gap:10px;height:42px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);border-radius:999px;padding:0 14px;box-sizing:border-box}
.kc-search-box .ic{color:#767c82;width:18px;height:18px;flex:none}
.kc-search-input{flex:1;background:transparent;border:0;outline:0;color:var(--ink);font-family:Montserrat,sans-serif;font-size:13.5px}
.kc-search-input::placeholder{color:#686e74}
.kc-search-actions{display:flex;align-items:center;gap:10px;flex:none}
.kc-action-btn{width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);display:grid;place-items:center;color:var(--ink);cursor:pointer;position:relative;text-decoration:none}
.kc-action-btn:hover{background:rgba(255,255,255,.08)}
.kc-action-btn .dot{position:absolute;top:6px;right:6px;width:7px;height:7px;border-radius:50%;background:#FF3B47}

/* Category Tabs */
.kc-cat-tabs{display:flex;align-items:center;gap:22px;border-bottom:1px solid rgba(255,255,255,.07);overflow-x:auto;scrollbar-width:none;margin-bottom:12px}
.kc-cat-tabs::-webkit-scrollbar{display:none}
.kc-cat-tab{background:transparent;border:0;outline:0;padding:8px 0 10px;font-family:Montserrat,sans-serif;font-size:15px;font-weight:500;color:#767c82;cursor:pointer;white-space:nowrap;position:relative;transition:color .2s}
.kc-cat-tab:hover{color:var(--ink)}
.kc-cat-tab.on{color:var(--ink);font-weight:700}
.kc-cat-tab.on::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2.5px;background:var(--lime);border-radius:2px}

/* Sub-filter Bar */
.kc-sub-bar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}
.kc-sub-tabs{display:flex;align-items:center;gap:18px;overflow-x:auto;scrollbar-width:none}
.kc-sub-tabs::-webkit-scrollbar{display:none}
.kc-sub-tab{background:transparent;border:0;outline:0;font-family:Montserrat,sans-serif;font-size:13px;font-weight:500;color:#767c82;cursor:pointer;white-space:nowrap;padding:4px 0;transition:color .2s}
.kc-sub-tab:hover{color:var(--ink)}
.kc-sub-tab.on{color:var(--ink);font-weight:700}
.kc-edit-btn{background:transparent;border:0;color:#767c82;cursor:pointer;padding:4px;display:grid;place-items:center;transition:color .2s}
.kc-edit-btn:hover{color:var(--ink)}

/* Announcement Banner */
.kc-banner{display:flex;align-items:center;justify-content:space-between;gap:14px;background:rgba(24,0,173,.06);border:1px solid rgba(24,0,173,.22);border-radius:10px;padding:10px 14px;margin-bottom:14px}
.kc-banner-text{font-size:12px;line-height:1.45;color:var(--lime);flex:1}
.kc-banner-actions{display:flex;align-items:center;gap:10px;flex:none}
.kc-banner-set{background:transparent;border:1px solid var(--lime);color:var(--lime);border-radius:999px;padding:4px 14px;font-size:11.5px;font-weight:600;cursor:pointer;font-family:Montserrat,sans-serif}
.kc-banner-close{background:transparent;border:0;color:var(--lime);font-size:16px;cursor:pointer;padding:0 4px;line-height:1}

/* Table Header */
.kc-th{display:grid;grid-template-columns:1fr 110px 92px;align-items:center;padding:8px 0;font-size:11px;color:#767c82;border-bottom:1px solid rgba(255,255,255,.05);margin-bottom:4px}
.kc-th span{display:inline-flex;align-items:center;gap:3px;cursor:pointer;user-select:none}
.kc-th span:hover{color:var(--ink)}

/* Market Rows */
.kc-row{display:grid;grid-template-columns:1fr 110px 92px;align-items:center;padding:13px 0;border-bottom:1px solid rgba(255,255,255,.04);text-decoration:none;color:inherit;transition:background .2s ease}
.kc-row:hover{background:rgba(255,255,255,.025)}
.kc-row-left{display:flex;align-items:center;gap:12px;min-width:0}
.kc-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);display:grid;place-items:center;flex:none;color:var(--lime);font-family:Archivo,sans-serif;font-size:11px;font-weight:800;overflow:hidden}
.kc-avatar .player-photo{width:100%;height:100%;object-fit:cover;object-position:50% 18%;display:block}
.kc-avatar.coach{color:var(--amber);border-color:rgba(255,106,31,.25);background:rgba(255,106,31,.08)}
.kc-pair-title{display:flex;align-items:center;gap:5px;font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:14.5px;line-height:1.1;color:var(--ink)}
.kc-pair-quote{font-size:11.5px;color:#767c82;font-weight:600}
.kc-tag{font-family:'Montserrat', sans-serif;font-size:9px;font-weight:600;color:#767c82;background:rgba(255,255,255,.08);border-radius:4px;padding:1px 4px;margin-left:2px}
.kc-pair-sub{font-size:11.5px;color:#767c82;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kc-row-mid{text-align:right;padding-right:12px}
.kc-price-main{font-family:'Montserrat', sans-serif;font-size:14.5px;font-weight:600;color:var(--ink);letter-spacing:-.01em}
.kc-price-sub{font-family:'Montserrat', sans-serif;font-size:11px;color:#767c82;margin-top:2px}
.kc-row-right{display:flex;justify-content:flex-end}
.kc-pill{display:inline-flex;align-items:center;justify-content:center;min-width:76px;height:32px;border-radius:6px;font-family:'Montserrat', sans-serif;font-size:12.5px;font-weight:700;color:#fff;background:var(--lime);box-sizing:border-box;padding:0 6px}
.kc-pill.down{background:#FF3B47;color:#fff}
"""

ex = [T('<main><div class="kc-ex-wrap">' + intro('Exchange', 'Find the players you believe in.') +
        '<!-- Top Search & Actions -->'
        '<div class="kc-top-bar">'
        '  <div class="kc-search-box">'
        '    @@'
        '    <input id="q" type="search" class="kc-search-input" placeholder="Search players, clubs or coaches" aria-label="Search player shares" autocomplete="off">'
        '  </div>'
        '</div>'
        '<!-- Primary Category Tabs -->'
        '<div class="kc-cat-tabs" id="kcCatTabs">'
        '  <button type="button" class="kc-cat-tab" data-cat="fav">Favorites</button>'
        '  <button type="button" class="kc-cat-tab on" data-cat="markets">All shares</button>'
        '  <button type="button" class="kc-cat-tab" data-cat="alpha">Trending</button>'
        '  <button type="button" class="kc-cat-tab" data-cat="fwd">Forwards</button>'
        '  <button type="button" class="kc-cat-tab" data-cat="mid">Midfielders</button>'
        '  <button type="button" class="kc-cat-tab" data-cat="coaches">Coaches</button>'
        '</div>'
        '<!-- Sub-filter Row -->'
        '<div class="kc-sub-bar">'
        '  <div class="kc-sub-tabs" id="kcSubTabs">'
        '    <button type="button" class="kc-sub-tab on" data-sub="all">All</button>'
        '    <button type="button" class="kc-sub-tab" data-sub="holdings">Holdings</button>'
        '    <button type="button" class="kc-sub-tab" data-sub="epl">Premier League</button>'
        '    <button type="button" class="kc-sub-tab" data-sub="laliga">La Liga</button>'
        '    <button type="button" class="kc-sub-tab" data-sub="gainers">Top Gainers</button>'
        '  </div>'
        '</div>'
        '<!-- Table Headers -->'
        '<div class="kc-th">'
        '  <span data-sort="pair">Player ⇅</span>'
        '  <span data-sort="price" style="justify-content:flex-end">Price ($FTR) ⇅</span>'
        '  <span data-sort="change" style="justify-content:flex-end">24h ⇅</span>'
        '</div>'
        '<!-- Market List -->'
        '<div id="mktList"></div>'
        '<div style="padding:14px 0 0;font-size:11px;color:#767c82;text-align:center" id="mktCount">—</div>'
        '</div></main>',
        ic("search", "ic"),
        ic("bell", "ic"))]

EX_JS = r"""
var cat = 'markets', sub = 'all', sortCol = '', sortAsc = false, q = '';
var favs = JSON.parse(localStorage.getItem('ft_favorites') || '["$Saka","$Haaland","$Mbappe","$Yamal"]');

function fmt(n){ return n.toLocaleString('en-US'); }

function getFilteredList(){
  var s = FT.getState();
  var list = ASSETS.filter(function(a){
    // Search filter
    if(q && (a.t + ' ' + a.n).toLowerCase().indexOf(q) < 0) return false;

    // Category filter
    if(cat === 'fav' && favs.indexOf(a.t) < 0) return false;
    if(cat === 'alpha' && (a.d < 3.0 && !a.c)) return false;
    if(cat === 'fwd' && a.pos !== 'FWD') return false;
    if(cat === 'mid' && a.pos !== 'MID') return false;
    if(cat === 'coaches' && !a.c) return false;

    // Sub-tab filter
    if(sub === 'holdings' && !s.holdings[a.t]) return false;
    if(sub === 'epl' && (a.club || '').indexOf('Arsenal') < 0 && (a.club || '').indexOf('Manchester') < 0 && (a.club || '').indexOf('Chelsea') < 0) return false;
    if(sub === 'laliga' && (a.club || '').indexOf('Madrid') < 0 && (a.club || '').indexOf('Barcelona') < 0) return false;
    if(sub === 'gainers' && a.d <= 2.0) return false;

    return true;
  });

  if(sortCol === 'pair'){
    list.sort(function(a, b){ return sortAsc ? a.t.localeCompare(b.t) : b.t.localeCompare(a.t); });
  } else if(sortCol === 'price'){
    list.sort(function(a, b){ return sortAsc ? a.p - b.p : b.p - a.p; });
  } else if(sortCol === 'change'){
    list.sort(function(a, b){ return sortAsc ? a.d - b.d : b.d - a.d; });
  }

  return list;
}

function renderMarketRows(){
  var list = getFilteredList();
  var host = document.getElementById('mktList');
  if(!list.length){
    host.innerHTML = '<div style="padding:48px 0;text-align:center;color:#767c82;font-size:13px">'
      + 'No player shares match your search or filter.</div>';
    document.getElementById('mktCount').textContent = '0 shares';
    return;
  }

  host.innerHTML = list.map(function(a){
    var to = 'asset.html?a=' + encodeURIComponent(a.t);
    var quote = a.q || 'FTR';
    var sym = a.t.replace('$', '');
    var up = a.d >= 0;
    var subPrice = (a.p * 0.1).toFixed(2) + ' USD';

    return "<a class='kc-row' href='" + to + "'>"
      + "<div class='kc-row-left'>"
      + "  <div class='kc-avatar" + (a.c ? " coach" : "") + "'>" + playerPhoto(a.t,a.n) + "</div>"
      + "  <div style='min-width:0'>"
      + "    <div class='kc-pair-title'>"
      + "      <span>" + sym + "</span>"
      + "      <span class='kc-pair-quote'>/" + quote + "</span>"
      + "      <span class='kc-tag'>" + (a.tag || (a.c ? 'COACH' : '10x')) + "</span>"
      + "    </div>"
      + "    <div class='kc-pair-sub'>" + a.n + " · " + (a.club || (a.c ? 'Coach' : 'Player')) + "</div>"
      + "  </div>"
      + "</div>"
      + "<div class='kc-row-mid'>"
      + "  <div class='kc-price-main'>" + (a.p > 999 ? a.p.toLocaleString('en-US', {minimumFractionDigits: 1, maximumFractionDigits: 2}) : a.p.toFixed(a.p < 1 ? 4 : 2)) + "</div>"
      + "  <div class='kc-price-sub'>$" + subPrice + "</div>"
      + "</div>"
      + "<div class='kc-row-right'>"
      + "  <div class='kc-pill" + (up ? "" : " down") + "'>" + (up ? "+" : "") + a.d.toFixed(2) + "%</div>"
      + "</div>"
      + "</a>";
  }).join('');

  document.getElementById('mktCount').textContent = list.length + ' of ' + ASSETS.length + ' assets';
}

// Category Tabs
document.querySelectorAll('#kcCatTabs button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#kcCatTabs button').forEach(function(x){ x.classList.remove('on'); });
    b.classList.add('on');
    cat = b.dataset.cat;
    renderMarketRows();
  });
});

// Sub-filter Tabs
document.querySelectorAll('#kcSubTabs button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#kcSubTabs button').forEach(function(x){ x.classList.remove('on'); });
    b.classList.add('on');
    sub = b.dataset.sub;
    renderMarketRows();
  });
});

// Search input
var qi = document.getElementById('q');
if(qi){
  qi.addEventListener('input', function(){
    q = qi.value.trim().toLowerCase();
    renderMarketRows();
  });
}

// Sorting headers
document.querySelectorAll('.kc-th span').forEach(function(el){
  el.addEventListener('click', function(){
    var col = el.dataset.sort;
    if(sortCol === col) sortAsc = !sortAsc;
    else { sortCol = col; sortAsc = false; }
    renderMarketRows();
  });
});

renderMarketRows();
window.addEventListener('fantrade:statechange', renderMarketRows);
"""

page("exchange.html", "Exchange — Fantrade", "".join(ex), EX_JS, EX_CSS, app=True)


# ══════════════════════════════════════════════════════════
# 3. DREAM CLUBS
# ══════════════════════════════════════════════════════════
CL_CSS = """
.kc-home-wrap{max-width:680px;margin:0 auto;padding:12px 16px 84px}
.kc-topbar{display:flex;align-items:center;justify-content:space-between;padding:8px 0 16px}
.kc-top-title{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;font-size:17px;letter-spacing:-.01em;text-transform:uppercase}
.kc-icon-btn{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;color:#8E9AA8;cursor:pointer;transition:all .2s ease;text-decoration:none}
.kc-icon-btn:hover{color:#fff;background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.15)}
.kc-icon-btn .ic{width:18px;height:18px}
.stepper{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:24px}
.stepper button{border:1px solid var(--hair);background:rgba(255,255,255,.03);color:var(--dim);border-radius:999px;
  padding:9px 16px;font-weight:600;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;
  box-shadow:var(--inset);display:flex;align-items:center;gap:9px;transition:all .6s var(--ease)}
.stepper button .ic{width:14px;height:14px}
.stepper button[aria-current="step"]{background:var(--lime);border-color:var(--lime);color:#fff}
.stepper button:hover:not([aria-current="step"]){color:var(--ink);border-color:var(--hair-2)}
.forms{display:flex;gap:8px;flex-wrap:wrap}
.forms button{flex:1;min-width:92px;border:1px solid var(--hair);background:rgba(255,255,255,.03);color:var(--dim);
  border-radius:14px;padding:14px 0;font-family:'Montserrat', sans-serif;font-size:14px;cursor:pointer;
  box-shadow:var(--inset);transition:all .6s var(--ease)}
.forms button[aria-pressed="true"]{background:var(--lime);border-color:var(--lime);color:#fff}
.forms button:hover:not([aria-pressed="true"]){color:var(--ink);border-color:var(--hair-2)}
.swatches{display:flex;gap:8px;margin-top:12px}
.sw{width:34px;height:34px;border-radius:11px;border:1px solid var(--hair);cursor:pointer;box-shadow:var(--inset);
  transition:transform .6s var(--ease)}
.sw:hover,.sw[aria-pressed="true"]{transform:scale(1.08)}
.sw[aria-pressed="true"]{border-color:var(--ink)}
.lb{display:grid;grid-template-columns:52px 2fr 1fr 1fr 1fr;gap:14px;align-items:center;padding:15px 24px;
  border-bottom:1px solid rgba(255,255,255,.05);font-size:13px}
.lb.h{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;border-bottom:1px solid var(--hair)}
.lb .rank{font-family:'Montserrat', sans-serif;color:var(--faint)}
.lb.you{background:rgba(24,0,173,.06)}
.lb .cn{display:flex;align-items:center;gap:12px}
.mini-crest{width:26px;height:29px;flex:none;clip-path:polygon(0 0,100% 0,100% 66%,50% 100%,0 66%)}
@media (max-width:768px){.lb{grid-template-columns:40px 1.6fr 1fr;padding:13px 16px}
 .lb>*:nth-child(n+4){display:none}}
"""

cl = ['<main><div class="kc-home-wrap" style="padding-top:0;padding-bottom:84px">']
cl.append(T('<div class="kc-topbar">'
            '<a class="kc-icon-btn" href="dashboard.html" aria-label="Back to Home">@@</a>'
            '<div class="kc-top-title" id="clName">Zero FC</div>'
            '<a class="kc-icon-btn" href="club-builder.html?new=1" title="New Club" style="background:rgba(24,0,173,.1);border-color:rgba(24,0,173,.3);color:#1800ad;font-weight:700;font-size:18px">+</a>'
            '</div>', ic("arrow", "ic")))
cl.append('<div class="clubrail" id="clubRail" style="margin-bottom:16px" data-reveal></div>')

ROUNDS = [("MD 27", "812", "18th", "w", "+6,200"), ("MD 26", "704", "41st", "w", "+4,100"),
          ("MD 25", "689", "63rd", "w", "+3,250"), ("MD 24", "512", "308th", "l", "-2,500"),
          ("MD 23", "548", "214th", "l", "-2,500")]

cl.append(T('<div style="display:flex;flex-direction:column;gap:16px">'
          '<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core">'
          '<div style="padding:16px 18px 0"><div class="tabstrip" id="clTabs" role="tablist">'
          '<button type="button" role="tab" aria-pressed="true" data-p="lineups">Line-ups</button>'
          '<button type="button" role="tab" aria-pressed="false" data-p="position">Position</button>'
          '<button type="button" role="tab" aria-pressed="false" data-p="form">Form</button>'
          '</div></div>'
          '<div class="pane on" data-pane="lineups"><div class="pitch" id="pitchMount"></div></div>'

          # ── league position, live ──
          '<div class="pane" data-pane="position"><div class="pad">'
          '<div style="display:flex;align-items:center;gap:12px;margin-bottom:22px;flex-wrap:wrap">'
          '<div class="k-label" style="margin:0">League position — live</div>'
          '<span class="listening" style="margin-left:auto"><i></i>Updating</span></div>'
          '<div class="gauge">'
          '<div class="gside"><div class="gbar"><i style="height:60%"></i></div>'
          '<div class="pc">60%</div><div class="lb">Zero FC form</div></div>'
          '<div class="ladder">'
          '<div class="rung">#122</div><div class="rung">#123</div>'
          '<div class="rung you" id="clRung">#124</div><div class="rung">#125</div></div>'
          '<div class="gside"><div class="gbar rival"><i style="height:20%"></i></div>'
          '<div class="pc">20%</div><div class="lb">Sextante FC</div></div>'
          '</div>'
          '<div style="display:flex;gap:26px;margin-top:28px;flex-wrap:wrap">'
          '<div><div class="k-label">Zero FC · you</div>'
          '<div class="form5"><i class="l">L</i><i class="l">L</i><i class="w">W</i><i class="w">W</i>'
          '<i class="w">W</i></div></div>'
          '<div style="margin-left:auto"><div class="k-label">#123 · Sextante FC</div>'
          '<div class="form5"><i class="w">W</i><i class="l">L</i><i class="d">D</i><i class="l">L</i>'
          '<i class="l">L</i></div></div></div>'
          '<div style="margin-top:26px;border-top:1px solid var(--hair);padding-top:6px">'
          '<div class="b-row"><span>Points behind #123</span><b>140 FP</b></div>'
          '<div class="b-row"><span>Points clear of #125</span><b>96 FP</b></div>'
          '<div class="b-row"><span>Apex promotion cutoff</span><b>Top 150</b></div>'
          '<div class="b-row total"><span>Projected finish</span>'
          '<b style="color:var(--lime)">#118 · safe</b></div></div>'
          '</div></div>'

          # ── form and results ──
          '<div class="pane" data-pane="form"><div class="pad" style="padding-bottom:20px">'
          '<div class="k-label">Last five settled rounds</div></div>'
          '<div class="dt"><div class="dh" style="grid-template-columns:78px 1fr 90px 92px 46px">'
          '<span>Round</span><span>Points</span><span>Finish</span>'
          '<span style="text-align:right">Settled</span><span style="text-align:right">R</span></div>'
          + "".join(T('<div class="dr" style="grid-template-columns:78px 1fr 90px 92px 46px">'
                      '<div class="num" style="font-size:13px">@@</div>'
                      '<div><div class="num" style="font-size:13px">@@ FP</div>'
                      '<div class="sub-line">Elite tier · Dream Club mode</div></div>'
                      '<div style="color:var(--dim);font-size:12.5px">@@ / 1,420</div>'
                      '<div class="pl @@" style="text-align:right">@@</div>'
                      '<div style="text-align:right"><span class="form5" style="justify-content:flex-end">'
                      '<i class="@@">@@</i></span></div></div>',
                      md, pts, fin, "up" if res == "w" else "down", ftr, res, res.upper())
                    for md, pts, fin, res, ftr in ROUNDS) +
          '</div>'
          '<div class="pad" style="padding-top:22px">'
          '<div class="mini-grid" style="grid-template-columns:repeat(3,1fr)">'
          '<div class="mini"><div class="k">Rounds won</div><div class="v lime">3 of 5</div></div>'
          '<div class="mini"><div class="k">Best finish</div><div class="v">18th</div></div>'
          '<div class="mini"><div class="k">Net this cycle</div><div class="v amber">+8,550</div></div>'
          '</div></div></div>'

          '</div></div>'
          '<div style="display:flex;flex-direction:column;gap:16px">'
          '<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad"><div class="k-label">Club value</div>'
          '<div class="value-big"><span id="clValue">245,800</span> <small>$FTR</small></div>'
          '<div class="delta" id="clMeta">Apex division · +15.0% boost</div>'
          '<div style="margin-top:22px;border-top:1px solid var(--hair);padding-top:6px">'
          '<div class="b-row"><span>Starting XI</span><b>180,600</b></div>'
          '<div class="b-row"><span>Bench (4)</span><b>45,200</b></div>'
          '<div class="b-row"><span>Coach $Arteta</span><b>20,000</b></div>'
          '<div class="b-row total"><span>Club value</span><b>245,800</b></div></div>'
          '<div style="margin-top:18px">@@</div></div></div>'
          '<div class="mini-grid" data-reveal>'
          '<div class="mini"><div class="k">Last round</div><div class="v lime">312</div></div>'
          '<div class="mini"><div class="k">Season FP</div><div class="v" id="clFp">8,420</div></div>'
          '<div class="mini"><div class="k">Win rate</div><div class="v">62%</div></div>'
          '<div class="mini"><div class="k">$FTR earned</div><div class="v amber">19,640</div></div></div>'
          '<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad-sm">'
          '<div class="k-label">Club value · last 8 rounds</div><div id="valChart"></div></div></div>'
          '</div>', btn("Enter this club in FanPlay", "btn-lime btn-sm", "fanplay.html")))

cl.append(T('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad">'
          '<div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">'
          '<span class="ibox">@@</span>'
          '<div style="min-width:0"><div style="font-family:Archivo;'
          'font-variation-settings:\'wdth\' 120,\'wght\' 800;text-transform:uppercase;font-size:18px">'
          'Your clubs</div>'
          '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:6px 0 0;line-height:1.6;'
          'max-width:60ch" id="clCount">—</p></div>'
          '<span style="margin-left:auto;display:flex;gap:10px;flex-wrap:wrap">@@@@</span></div></div></div>',
          ic("formation", "ic-lg"),
          btn("Edit this club", "btn-glass", "club-builder.html"),
          btn("New club", href="club-builder.html?new=1")))

cl.append('</div></div></main>')


CL_JS = PITCH_JS + r"""
// ── the clubs you own, as a rail you can switch from ──────────────
function crestFor(c){
  return '<span class="rc" style="background:linear-gradient(160deg,' + c.colors[0] + ','
    + (c.colors[1] || c.colors[0]) + ')">'
    + c.name.split(/\s+/).map(function(w){ return w.charAt(0).toUpperCase(); }).join('').slice(0,3)
    + '</span>';
}
function renderRail(){
  var rail = document.getElementById('clubRail');
  if(!rail) return;
  var s = FT.getState();
  rail.innerHTML = s.clubs.map(function(c){
    return '<button class="clubchip" type="button" data-club="' + c.id + '"'
      + (c.id === s.activeClub ? ' aria-pressed="true"' : ' aria-pressed="false"') + '>'
      + crestFor(c) + '<span class="cn">' + c.name + '</span>'
      + '<span class="cd">' + (c.division || 'Challenger') + ' · #' + c.rank + '</span></button>';
  }).join('')
    + '<a class="clubchip add" href="club-builder.html?new=1">'
    + '<span class="rc plus">+</span><span class="cn">New club</span>'
    + '<span class="cd">Build another</span></a>';
  rail.querySelectorAll('[data-club]').forEach(function(b){
    b.addEventListener('click', function(){
      if(b.getAttribute('aria-pressed') === 'true') return;
      try {
        var c = FT.switchClub(b.dataset.club);
        showToast('Switched to ' + c.name + '.', 'success');
      } catch(e){ showToast(e.message, 'error'); }
    });
  });
}
function renderClubHead(){
  var s = FT.getState(), c = s.club;
  var set = function(id, v){ var e = document.getElementById(id); if(e) e.textContent = v; };
  set('clName', c.name);
  set('clValue', (c.value || 0).toLocaleString('en-US'));
  set('clFp', (c.fp || 0).toLocaleString('en-US'));
  set('clMeta', (c.division || 'Challenger') + ' division · +' + (c.boost || 0).toFixed(1) + '% boost');
  set('clRung', '#' + c.rank);
  set('clCount', s.clubs.length + (s.clubs.length === 1 ? ' club' : ' clubs')
    + ' · staking ' + c.name + ' this round');
  renderRail();
}
renderClubHead();
window.addEventListener('fantrade:statechange', renderClubHead);

document.querySelectorAll('#clTabs button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#clTabs button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed', 'true');
    document.querySelectorAll('[data-pane]').forEach(function(p){
      p.classList.toggle('on', p.dataset.pane === b.dataset.p);
    });
  });
});


var FORMS={
 '4-3-3':[[['ST','$Haaland']],[['LW','$Vinicius'],['CAM','$Bruno',1],['RW','$Saka']],
          [['CM','$Rice'],['CM','$Odegaard']],
          [['LB','$Davies'],['CB','$VanDijk'],['CB','$Saliba'],['RB','$White']],[['GK','$Raya']]],
 '4-4-2':[[['ST','$Haaland'],['ST','$Jackson']],
          [['LM','$Vinicius'],['CM','$Rice'],['CM','$Bruno',1],['RM','$Saka']],
          [['LB','$Davies'],['CB','$VanDijk'],['CB','$Saliba'],['RB','$White']],[['GK','$Raya']]],
 '3-5-2':[[['ST','$Haaland'],['ST','$Vinicius']],
          [['LWB','$Davies'],['CM','$Rice'],['CM','$Odegaard'],['CAM','$Bruno',1],['RWB','$Saka']],
          [['CB','$VanDijk'],['CB','$Saliba'],['CB','$Gabriel']],[['GK','$Raya']]],
 '4-2-3-1':[[['ST','$Haaland']],[['LW','$Vinicius'],['CAM','$Bruno',1],['RW','$Saka']],
          [['DM','$Rice'],['DM','$Odegaard']],
          [['LB','$Davies'],['CB','$VanDijk'],['CB','$Saliba'],['RB','$White']],[['GK','$Raya']]]
};
var bp=document.getElementById('builderPitch');
var curShape='4-3-3';
var curColor='#1800ad';

function renderBuilder(shape){
  curShape=shape;
  XI=FORMS[shape] || FORMS['4-3-3'];
  var s=FT.getState();
  var cName=s.club.name||'Zero FC';
  var cStad=s.club.stadium||'Emirates of the North';
  var html=pitchHTML().replace('Zero FC', cName).replace('4-3-3 · Emirates of the North', shape+' · '+cStad);
  bp.innerHTML=html;
  var cr=bp.querySelector('.crest');
  if(cr) cr.style.background='linear-gradient(160deg,'+curColor+',rgba(0,0,0,.4))';
  var add=bp.querySelector('#addSub'), al=bp.querySelector('#ownAlert');
  if(add) add.addEventListener('click',function(){ var o=al.classList.toggle('show'); add.setAttribute('aria-expanded',o?'true':'false'); });
}

var NEWCLUB = /[?&]new=1/.test(window.location.search);

function syncClubUI(){
  var s=FT.getState();
  var c=s.club;
  curShape=c.formation||'4-3-3';
  curColor=c.color||'#1800ad';

  // building a second club starts from a blank name, not the one you already own
  var ni=document.getElementById('clubNameInput');
  if(ni && !NEWCLUB) ni.value=c.name;
  var si=document.getElementById('clubStadiumInput');
  if(si && !NEWCLUB) si.value=c.stadium;

  if(!NEWCLUB) document.querySelectorAll('h1').forEach(function(h){
    if(h.textContent.indexOf('Zero')!==-1 || h.textContent.indexOf(c.name)!==-1){
      h.textContent=c.name;
    }
  });

  document.querySelectorAll('.pitch-head').forEach(function(ph){
    var nm=ph.querySelector('.name');
    if(nm) nm.textContent=c.name;
    var mt=ph.querySelector('.meta');
    if(mt) mt.textContent=curShape+' · '+c.stadium+' · Est. 2026';
    var cr=ph.querySelector('.crest');
    if(cr) cr.style.background='linear-gradient(160deg,'+curColor+',rgba(0,0,0,.4))';
  });

  var myRow=document.getElementById('myClubLbRow');
  if(myRow){
    var cn=myRow.querySelector('.cn');
    if(cn){
      cn.innerHTML='<span class="mini-crest" style="background:linear-gradient(160deg,'+curColor+',rgba(0,0,0,.4))"></span>'+c.name;
    }
  }

  // update active buttons in formation
  document.querySelectorAll('#forms button').forEach(function(b){
    b.setAttribute('aria-pressed', b.textContent.trim()===curShape ? 'true' : 'false');
  });
}

if(bp){
  var savedClub=FT.getState().club;
  if(savedClub && savedClub.formation) curShape=savedClub.formation;
  if(savedClub && savedClub.color) curColor=savedClub.color;

  renderBuilder(curShape);
  syncClubUI();

  document.querySelectorAll('#forms button').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('#forms button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
      b.setAttribute('aria-pressed','true');
      renderBuilder(b.textContent.trim());
    });
  });
  document.querySelectorAll('.sw').forEach(function(s){
    s.addEventListener('click',function(){
      document.querySelectorAll('.sw').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
      s.setAttribute('aria-pressed','true');
      var c=getComputedStyle(s).backgroundImage;
      curColor = s.style.background || '#1800ad';
      [bp.querySelector('.crest'), document.querySelector('#pitchMount .crest')].forEach(function(cr){
        if(cr) cr.style.backgroundImage=c;
      });
      var myRow=document.getElementById('myClubLbRow');
      if(myRow){
        var mc=myRow.querySelector('.mini-crest');
        if(mc) mc.style.backgroundImage=c;
      }
    });
  });
  document.querySelectorAll('#stepper button').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('#stepper button').forEach(function(x){ x.removeAttribute('aria-current'); });
      b.setAttribute('aria-current','step');
    });
  });

  var scb=document.getElementById('saveClubBtn');
  if(scb){
    scb.addEventListener('click',function(){
      var isNew = /[?&]new=1/.test(window.location.search);
      var name=(document.getElementById('clubNameInput').value||'').trim();
      var stadium=(document.getElementById('clubStadiumInput').value||'Unnamed ground').trim();
      if(name.length<2){ showToast("Give the club a name first.", "error"); return; }
      try {
        if(isNew){
          FT.createClub({ name: name, stadium: stadium, formation: curShape, color: curColor });
          showToast(name+" created and selected.", "success");
          setTimeout(function(){ window.location.href='clubs.html'; }, 900);
        } else {
          FT.saveClub({ name: name, stadium: stadium, formation: curShape, color: curColor });
          showToast(name+" ("+curShape+") saved.", "success");
        }
        syncClubUI();
      } catch(err){ showToast(err.message, "error"); }
    });
  }
}
var vc=document.getElementById('valChart');
if(vc){
  var vals=[118,132,141,160,179,196,233,245.8], w=340, h=110, max=260;
  var pts=vals.map(function(v,i){ return (i*(w/(vals.length-1))).toFixed(1)+','+(h-(v/max)*h).toFixed(1); });
  vc.innerHTML="<svg viewBox='0 0 "+w+" "+h+"' preserveAspectRatio='none' style='width:100%;height:110px;display:block'>"+
    "<defs><linearGradient id='vg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#1800ad' stop-opacity='.35'/>"+
    "<stop offset='1' stop-color='#1800ad' stop-opacity='0'/></linearGradient></defs>"+
    "<polygon points='0,"+h+" "+pts.join(' ')+" "+w+","+h+"' fill='url(#vg)'/>"+
    "<polyline points='"+pts.join(' ')+"' fill='none' stroke='#1800ad' stroke-width='1.6' stroke-linejoin='round'/></svg>"+
    "<div class='b-row' style='margin-top:12px'><span>8 rounds ago</span><b>118,000</b></div>"+
    "<div class='b-row'><span>Now</span><b>245,800</b></div>";
}
"""
page("clubs.html", "Dream Clubs — Fantrade", "".join(cl), CL_JS, CL_CSS, app=True)

# ══════════════════════════════════════════════════════════
# CLUB BUILDER
# ══════════════════════════════════════════════════════════
# builder
bd = ['<main><div class="kc-home-wrap" style="padding-top:0;padding-bottom:84px">']
bd.append(T('<div class="kc-topbar">'
            '<a class="kc-icon-btn" href="clubs.html" aria-label="Back to Clubs">@@</a>'
            '<div class="kc-top-title">Club Builder</div>'
            '<div style="width:36px"></div>'
            '</div>', ic("arrow", "ic")))
bd.append('<div style="display:flex;flex-direction:column;gap:16px">')
bd.append(T('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad">'
          '<div class="stepper" id="stepper">'
          '<button aria-current="step">@@ 1 Name</button><button>@@ 2 Identity</button>'
          '<button>@@ 3 Coach</button><button>@@ 4 Shape</button><button>@@ 5 XI</button>'
          '<button>@@ 6 Bench</button><button>@@ 7 Review</button><button>@@ 8 Save</button></div>'
          '<div class="field"><label>Club name</label><input id="clubNameInput" value="Zero FC" style="text-align:right"></div>'
          '<div class="field"><label>Stadium</label><input id="clubStadiumInput" value="Emirates of the North" style="text-align:right;font-size:13px"></div>'
          '<div class="k-label" style="margin-top:20px">Club colours</div>'
          '<div class="swatches">'
          '<button class="sw" aria-pressed="true" style="background:linear-gradient(160deg,#1800ad,#0f0075)" aria-label="Indigo"></button>'
          '<button class="sw" style="background:linear-gradient(160deg,#FF6A1F,#a83c00)" aria-label="Amber"></button>'
          '<button class="sw" style="background:linear-gradient(160deg,#4DA3FF,#0a4d99)" aria-label="Blue"></button>'
          '<button class="sw" style="background:linear-gradient(160deg,#E8E8E8,#8a8a8a)" aria-label="Silver"></button>'
          '<button class="sw" style="background:linear-gradient(160deg,#B14DFF,#5c1799)" aria-label="Violet"></button></div>'
          '<div class="k-label" style="margin-top:26px">Formation</div>'
          '<div class="forms" id="forms"><button aria-pressed="true">4-3-3</button><button>4-4-2</button>'
          '<button>3-5-2</button><button>4-2-3-1</button></div>'
          '<div class="line" style="margin-top:24px"><span>Ownership check</span><b class="up">15 of 16 owned</b></div>'
          '<div class="line"><span>Projected boost</span><b>+15.0%</b></div>'
          '@@</div></div>', ic("crest", "ic"), ic("swatch", "ic"), ic("whistle", "ic"), ic("formation", "ic"),
                              ic("pitch", "ic"), ic("subs", "ic"), ic("check", "ic"), ic("shield", "ic"),
                              btn("Save club", tag="button", extra='id="saveClubBtn" style="margin-top:20px;width:100%;justify-content:space-between"')))
bd.append('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pitch" id="builderPitch"></div></div>')
bd.append('</div></div></main>')

page("club-builder.html", "Club builder — Fantrade", "".join(bd), CL_JS, CL_CSS, app=True)




# ══════════════════════════════════════════════════════════
# 4. FANPLAY ENGINE (PROMPT 4)
# ══════════════════════════════════════════════════════════
FP_CSS = """
.kc-home-wrap{max-width:760px;margin:0 auto;padding:12px 16px 94px}
.fp-topbar{display:flex;align-items:center;justify-content:space-between;padding:8px 0 16px;border-bottom:1px solid rgba(255,255,255,.06)}
.fp-title-box{display:flex;align-items:center;gap:12px}
.fp-title-box h2{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 900;font-size:18px;margin:0;color:#fff;text-transform:uppercase}
.fp-title-box span{font-size:11px;color:#8E9AA8}

/* Metric Chips Dashboard (§80) */
.fp-metrics-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:16px 0 20px}
@media (max-width:640px){.fp-metrics-grid{grid-template-columns:repeat(2,1fr)}}
.fp-metric-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:12px 14px;display:flex;flex-direction:column;gap:4px}
.fp-metric-lbl{font-size:10px;font-weight:600;color:#8E9AA8;text-transform:uppercase;letter-spacing:.08em}
.fp-metric-val{font-family:'Montserrat',sans-serif;font-size:18px;font-weight:700;color:#fff}
.fp-metric-val.lime{color:var(--lime)}
.fp-metric-val.amber{color:var(--amber)}

/* Navigation View Switcher */
.fp-view-nav{display:flex;gap:10px;background:rgba(255,255,255,.03);padding:4px;border-radius:12px;border:1px solid rgba(255,255,255,.06);margin-bottom:20px}
.fp-view-btn{flex:1;padding:9px 0;background:transparent;border:0;color:#8E9AA8;border-radius:8px;font-family:Montserrat,sans-serif;font-size:12.5px;font-weight:600;cursor:pointer;transition:all .2s;text-align:center}
.fp-view-btn.on{background:rgba(255,255,255,.09);color:#fff;box-shadow:0 2px 8px rgba(0,0,0,.4)}

/* Step Indicator Bar */
.fp-step-bar{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;position:relative}
.fp-step-dot{display:flex;flex-direction:column;align-items:center;gap:6px;z-index:2;cursor:pointer}
.fp-step-circle{width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);color:#8E9AA8;display:grid;place-items:center;font-weight:700;font-size:12px;transition:all .2s}
.fp-step-dot.active .fp-step-circle{background:var(--lime);border-color:var(--lime);color:#fff;box-shadow:0 0 16px rgba(24,0,173,.4)}
.fp-step-dot.completed .fp-step-circle{background:rgba(24,0,173,.15);border-color:var(--lime);color:var(--lime)}
.fp-step-label{font-size:10px;color:#8E9AA8;font-weight:600;text-transform:uppercase}
.fp-step-dot.active .fp-step-label{color:#fff}

/* Step Container Card */
.fp-panel{background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);border-radius:20px;padding:24px;margin-bottom:20px}
.fp-panel-title{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:18px;color:#fff;margin:0 0 6px;text-transform:uppercase}
.fp-panel-sub{font-size:13px;color:#8E9AA8;margin:0 0 18px}

/* Asset Selection Grid */
.fp-asset-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.fp-asset-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:14px;cursor:pointer;transition:all .2s;text-align:left}
.fp-asset-card:hover{border-color:rgba(24,0,173,.4);background:rgba(255,255,255,.05)}
.fp-asset-card.selected{border-color:var(--lime);background:rgba(24,0,173,.08);box-shadow:0 0 18px rgba(24,0,173,.15)}
.fp-asset-sym{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;font-size:16px;color:#fff}
.fp-asset-name{font-size:11.5px;color:#8E9AA8;margin-top:2px}
.fp-asset-avail{margin-top:10px;font-size:11px;color:#1800ad;font-weight:600}

/* Match Selection Grid */
.fp-match-grid{display:flex;flex-direction:column;gap:10px}
.fp-match-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:16px;cursor:pointer;transition:all .2s}
.fp-match-card:hover{border-color:rgba(24,0,173,.4)}
.fp-match-card.selected{border-color:var(--lime);background:rgba(24,0,173,.08)}
.fp-match-comp{font-size:10.5px;font-weight:700;color:var(--amber);text-transform:uppercase;letter-spacing:.06em}
.fp-match-teams{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:17px;color:#fff;margin:6px 0}
.fp-match-meta{font-size:11.5px;color:#8E9AA8;display:flex;align-items:center;gap:12px}

/* Market Tiers Grid (§10, §11, §12) */
.fp-market-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
@media (max-width:600px){.fp-market-grid{grid-template-columns:1fr}}
.fp-market-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:16px;cursor:pointer;transition:all .2s;display:flex;flex-direction:column;gap:8px}
.fp-market-card:hover{border-color:rgba(24,0,173,.3)}
.fp-market-card.selected{border-color:var(--lime);background:rgba(24,0,173,.08)}
.fp-market-name{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;font-size:15px;color:#fff;text-transform:uppercase}
.fp-market-limit{font-size:10.5px;color:var(--lime);font-weight:700}
.fp-market-desc{font-size:12px;color:#8E9AA8;line-height:1.5;flex:1}

/* Prediction Option Cards (§13, §49) */
.fp-opt-grid{display:flex;flex-direction:column;gap:10px}
.fp-opt-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:14px 16px;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:16px;transition:all .2s}
.fp-opt-card:hover{border-color:rgba(24,0,173,.3)}
.fp-opt-card.selected{border-color:var(--lime);background:rgba(24,0,173,.07)}
.fp-opt-left{display:flex;align-items:center;gap:14px}
.fp-opt-check{width:22px;height:22px;border-radius:6px;border:1.5px solid rgba(255,255,255,.2);display:grid;place-items:center;color:#fff;font-weight:800;font-size:12px;transition:all .2s}
.fp-opt-card.selected .fp-opt-check{background:var(--lime);border-color:var(--lime)}
.fp-opt-label{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 700;font-size:14px;color:#fff}
.fp-opt-meta{font-size:11px;color:#8E9AA8;margin-top:2px;display:flex;gap:8px}
.fp-opt-right{display:flex;gap:12px;text-align:right}
.fp-opt-suc{font-family:'Montserrat',sans-serif;font-size:13px;font-weight:700;color:var(--lime)}
.fp-opt-fail{font-family:'Montserrat',sans-serif;font-size:13px;font-weight:700;color:#FF5E5E}

/* Stake & Review Cards (§50, §51, §52) */
.fp-stake-box{display:flex;flex-direction:column;gap:12px}
.fp-stake-input-wrap{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.1);border-radius:12px}
.fp-stake-input{border:0;background:transparent;color:#fff;font-family:'Montserrat',sans-serif;font-size:22px;font-weight:700;outline:none;width:60%}
.fp-stake-chips{display:flex;gap:8px}
.fp-stake-chip{flex:1;padding:8px 0;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);color:#8E9AA8;border-radius:8px;font-size:11.5px;cursor:pointer;text-align:center;font-weight:600}
.fp-stake-chip:hover{background:rgba(255,255,255,.09);color:#fff}
.fp-breakdown{display:flex;flex-direction:column;gap:8px;padding:14px;background:rgba(255,255,255,.02);border-radius:12px;font-size:12.5px;color:#8E9AA8}
.fp-breakdown-row{display:flex;justify-content:space-between;align-items:center}
.fp-breakdown-row b{color:#fff;font-family:'Montserrat',sans-serif}
.fp-risk-box{padding:12px 14px;border-radius:12px;background:rgba(255,106,31,.08);border:1px solid rgba(255,106,31,.2);color:#FF9D66;font-size:11.5px;line-height:1.5;margin-top:14px}

/* Action Buttons */
.fp-nav-btns{display:flex;gap:12px;margin-top:20px}
.fp-btn-back{flex:1;padding:14px 0;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);color:#fff;border-radius:12px;font-family:Archivo,sans-serif;font-weight:700;font-size:13px;text-transform:uppercase;cursor:pointer;text-align:center}
.fp-btn-next{flex:2;padding:14px 0;background:var(--lime);border:0;color:#fff;border-radius:12px;font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:13.5px;text-transform:uppercase;cursor:pointer;text-align:center;box-shadow:0 0 20px rgba(24,0,173,.3)}
"""

fp = ['<main><div class="kc-home-wrap fanplay-layout">', intro('FanPlay', 'Your players. Your predictions. Your matchday.', '<a class="app-text-link" href="liveboard.html">Live board</a>')]

# 4 Key Metrics Dashboard Chips (§80)
fp.append('<div class="fp-metrics-grid">'
          '<div class="fp-metric-card"><span class="fp-metric-lbl">Locked Shares</span><span class="fp-metric-val lime" id="mLockedShares">0</span></div>'
          '<div class="fp-metric-card"><span class="fp-metric-lbl">Active Positions</span><span class="fp-metric-val" id="mActiveCount">0</span></div>'
          '<div class="fp-metric-card"><span class="fp-metric-lbl">Provisional FP</span><span class="fp-metric-val lime" id="mProvFP">0 FP</span></div>'
          '<div class="fp-metric-card"><span class="fp-metric-lbl">Settled Earnings</span><span class="fp-metric-val amber" id="mSettledFTR">0.00 $FTR</span></div>'
          '</div>')

# Tab Switcher: Wizard vs Active vs History
fp.append('<div class="fp-view-nav">'
          '<button type="button" class="fp-view-btn on" id="vbtnWizard" onclick="window.switchFPView(\'wizard\')">New entry</button>'
          '<button type="button" class="fp-view-btn" id="vbtnActive" onclick="window.switchFPView(\'active\')">Active (<span id="tabActiveCount">0</span>)</button>'
          '<button type="button" class="fp-view-btn" id="vbtnHistory" onclick="window.switchFPView(\'history\')">History</button>'
          '</div>')

# ══════════════════════════════════════════════════════════
# VIEW 1: 7-STEP WIZARD (§48)
# ══════════════════════════════════════════════════════════
fp.append('<div id="fpViewWizard">'
          '<!-- Step Indicator -->'
          '<div class="fp-step-bar">'
          '<div class="fp-step-dot active" id="sdot1" onclick="window.goToStep(1)"><div class="fp-step-circle">1</div><span class="fp-step-label">Asset</span></div>'
          '<div class="fp-step-dot" id="sdot2" onclick="window.goToStep(2)"><div class="fp-step-circle">2</div><span class="fp-step-label">Match</span></div>'
          '<div class="fp-step-dot" id="sdot3" onclick="window.goToStep(3)"><div class="fp-step-circle">3</div><span class="fp-step-label">Market</span></div>'
          '<div class="fp-step-dot" id="sdot4" onclick="window.goToStep(4)"><div class="fp-step-circle">4</div><span class="fp-step-label">Picks</span></div>'
          '<div class="fp-step-dot" id="sdot5" onclick="window.goToStep(5)"><div class="fp-step-circle">5</div><span class="fp-step-label">Stake</span></div>'
          '<div class="fp-step-dot" id="sdot6" onclick="window.goToStep(6)"><div class="fp-step-circle">6</div><span class="fp-step-label">Review</span></div>'
          '<div class="fp-step-dot" id="sdot7"><div class="fp-step-circle">7</div><span class="fp-step-label">Done</span></div>'
          '</div>')

# Step 1: Choose Asset
fp.append('<div class="fp-panel" id="stepBox1">'
          '<div class="fp-panel-title">Choose your player.</div>'
          '<div class="fp-panel-sub">Choose a player or coach you own. Only available shares can be entered.</div>'
          '<div class="fp-asset-grid" id="stepAssetGrid"></div>'
          '<div class="fp-nav-btns"><button type="button" class="fp-btn-next" onclick="window.goToStep(2)">Next: Choose Match →</button></div>'
          '</div>')

# Step 2: Choose Match
fp.append('<div class="fp-panel" id="stepBox2" style="display:none">'
          '<div class="fp-panel-title">Pick a match.</div>'
          '<div class="fp-panel-sub">Choose an upcoming fixture before entries close.</div>'
          '<div class="fp-match-grid" id="stepMatchGrid"></div>'
          '<div class="fp-nav-btns">'
          '<button type="button" class="fp-btn-back" onclick="window.goToStep(1)">← Back</button>'
          '<button type="button" class="fp-btn-next" onclick="window.goToStep(3)">Next: Choose Market →</button>'
          '</div></div>')

# Choose how you want to play. (§10, §11, §12)
fp.append('<div class="fp-panel" id="stepBox3" style="display:none">'
          '<div class="fp-panel-title">Choose how you want to play.</div>'
          '<div class="fp-panel-sub">Compare the number of predictions and potential gains or losses for each tier.</div>'
          '<div class="fp-market-grid" id="stepMarketGrid"></div>'
          '<div class="fp-nav-btns">'
          '<button type="button" class="fp-btn-back" onclick="window.goToStep(2)">← Back</button>'
          '<button type="button" class="fp-btn-next" onclick="window.goToStep(4)">Next: Select Predictions →</button>'
          '</div></div>')

# Step 4: Choose Predictions (§13, §14, §15, §16, §17, §49)
fp.append('<div class="fp-panel" id="stepBox4" style="display:none">'
          '<div class="fp-panel-title">Make your predictions.</div>'
          '<div class="fp-panel-sub" id="stepPicksSub">Choose the predictions for your tier. We’ll help you avoid conflicting picks.</div>'
          '<div class="fp-opt-grid" id="stepOptGrid"></div>'
          '<div class="fp-nav-btns">'
          '<button type="button" class="fp-btn-back" onclick="window.goToStep(3)">← Back</button>'
          '<button type="button" class="fp-btn-next" onclick="window.goToStep(5)">Next: Choose Shares →</button>'
          '</div></div>')

# Step 5: Choose Stake (§5, §6, §50)
fp.append('<div class="fp-panel" id="stepBox5" style="display:none">'
          '<div class="fp-panel-title">Choose your shares.</div>'
          '<div class="fp-panel-sub">You stake player shares, NOT $FTR directly. Staked shares are locked until final match settlement.</div>'
          '<div class="fp-stake-box">'
          '<div class="fp-stake-input-wrap">'
          '<label style="font-size:11px;color:#8E9AA8;text-transform:uppercase;font-weight:700">Shares Stake</label>'
          '<input type="number" id="stakeInput" value="100" min="1" oninput="window.updateStakeCalculations()">'
          '</div>'
          '<div class="fp-stake-chips">'
          '<button type="button" class="fp-stake-chip" onclick="window.setStakePct(0.25)">25%</button>'
          '<button type="button" class="fp-stake-chip" onclick="window.setStakePct(0.50)">50%</button>'
          '<button type="button" class="fp-stake-chip" onclick="window.setStakePct(0.75)">75%</button>'
          '<button type="button" class="fp-stake-chip" onclick="window.setStakePct(1.00)">100%</button>'
          '</div>'
          '<div class="fp-breakdown">'
          '<div class="fp-breakdown-row"><span>Total Owned Shares</span><b id="sOwned">500</b></div>'
          '<div class="fp-breakdown-row"><span>Currently Locked</span><b id="sLocked">0</b></div>'
          '<div class="fp-breakdown-row"><span>Available to Stake</span><b id="sAvail" style="color:var(--lime)">500</b></div>'
          '<div class="fp-breakdown-row" style="border-top:1px solid rgba(255,255,255,.06);padding-top:8px"><span>Remaining After Lock</span><b id="sRemain">400</b></div>'
          '</div>'
          '</div>'
          '<div class="fp-nav-btns">'
          '<button type="button" class="fp-btn-back" onclick="window.goToStep(4)">← Back</button>'
          '<button type="button" class="fp-btn-next" onclick="window.goToStep(6)">Review Position →</button>'
          '</div></div>')

# Step 6: Review & Risk Disclosure (§51, §52)
fp.append('<div class="fp-panel" id="stepBox6" style="display:none">'
          '<div class="fp-panel-title">Review your entry.</div>'
          '<div class="fp-panel-sub">Verify your exact potential FP range and $FTR settlement range before locking shares.</div>'
          '<div class="fp-breakdown" id="reviewBreakdown"></div>'
          '<div class="fp-risk-box">'
          '⚠️ <b>FanPlay Risk Disclosure:</b> Staked shares are locked and cannot be sold on the Exchange until the match reaches final settlement. Incorrect predictions generate negative Fans Point (FP), which will debit your $FTR ledger balance upon settlement at 1,000 FP = 1 $FTR. Final settlement uses official authoritative matchday data.'
          '</div>'
          '<div class="fp-nav-btns">'
          '<button type="button" class="fp-btn-back" onclick="window.goToStep(5)">← Back</button>'
          '<button type="button" class="fp-btn-next" id="btnActivate" onclick="window.submitActivation()">Lock Shares &amp; Activate FanPlay</button>'
          '</div></div>')

# Step 7: Activated Success Receipt
fp.append('<div class="fp-panel" id="stepBox7" style="display:none;text-align:center;padding:40px 20px">'
          '<div style="font-size:48px;margin-bottom:12px">🎉</div>'
          '<div class="fp-panel-title" style="color:var(--lime)">FanPlay Position Activated!</div>'
          '<div class="fp-panel-sub" id="step7Msg">Your shares are reserved until the match settles.</div>'
          '<div style="display:flex;gap:12px;justify-content:center;margin-top:24px">'
          '<button type="button" class="fp-btn-next" style="flex:none;padding:12px 28px" onclick="window.switchFPView(\'active\')">View Active Positions</button>'
          '<button type="button" class="fp-btn-back" style="flex:none;padding:12px 28px" onclick="window.resetWizard()">Create Another</button>'
          '</div></div>'
          '</div>')

# ══════════════════════════════════════════════════════════
# VIEW 2: ACTIVE & LIVE POSITIONS (§29, §45, §46)
# ══════════════════════════════════════════════════════════
fp.append('<div id="fpViewActive" style="display:none">'
          '<div id="activeList" style="display:flex;flex-direction:column;gap:14px"></div>'
          '</div>')

# ══════════════════════════════════════════════════════════
# VIEW 3: SETTLED HISTORY (§45, §46, §81)
# ══════════════════════════════════════════════════════════
fp.append('<div id="fpViewHistory" style="display:none">'
          '<div id="historyList" style="display:flex;flex-direction:column;gap:14px"></div>'
          '</div>')

fp.append('</div></main>')

FP_JS = r"""
var curView = 'wizard';
var curStep = 1;
var eligibleAssets = [];
var matchesList = [];
var marketsList = [];
var optionsList = [];
var userFanPlays = [];

var selAsset = null;
var selMatch = null;
var selMarket = null;
var selOptionIds = [];
var stakeShares = 100;

function switchFPView(v){
  curView = v;
  document.getElementById('vbtnWizard').classList.toggle('on', v==='wizard');
  document.getElementById('vbtnActive').classList.toggle('on', v==='active');
  document.getElementById('vbtnHistory').classList.toggle('on', v==='history');
  document.getElementById('fpViewWizard').style.display = v==='wizard' ? '' : 'none';
  document.getElementById('fpViewActive').style.display = v==='active' ? '' : 'none';
  document.getElementById('fpViewHistory').style.display = v==='history' ? '' : 'none';
  if(v==='active' || v==='history'){
    loadUserFanPlays();
  }
}
window.switchFPView = switchFPView;

function resetWizard(){
  curStep = 1;
  selAsset = null;
  selMatch = null;
  selMarket = null;
  selOptionIds = [];
  stakeShares = 100;
  updateStepUI();
  switchFPView('wizard');
  loadInitialData();
}
window.resetWizard = resetWizard;

function goToStep(s){
  if(s > curStep){
    if(curStep === 1 && !selAsset){ showToast('Select an asset to continue.', 'error'); return; }
    if(curStep === 2 && !selMatch){ showToast('Select a match fixture to continue.', 'error'); return; }
    if(curStep === 3 && !selMarket){ showToast('Select a market tier to continue.', 'error'); return; }
    if(curStep === 4){
      if(selOptionIds.length === 0){ showToast('Select at least 1 prediction option.', 'error'); return; }
      if(selMarket && selOptionIds.length > selMarket.maxSelections){
        showToast('Maximum ' + selMarket.maxSelections + ' selections allowed in ' + selMarket.name + '.', 'error');
        return;
      }
    }
    if(curStep === 5){
      var avail = selAsset ? (selAsset.availableQuantity || 0) : 0;
      if(stakeShares <= 0){ showToast('Enter a valid share stake.', 'error'); return; }
      if(stakeShares > avail){ showToast('Insufficient available shares. You have ' + avail + '.', 'error'); return; }
      renderReview();
    }
  }
  curStep = s;
  updateStepUI();
  if(s === 4) loadOptions();
  if(s === 5) updateStakeCalculations();
}
window.goToStep = goToStep;

function updateStepUI(){
  for(var i=1; i<=7; i++){
    var dot = document.getElementById('sdot' + i);
    var box = document.getElementById('stepBox' + i);
    if(dot){
      dot.classList.toggle('active', i === curStep);
      dot.classList.toggle('completed', i < curStep);
    }
    if(box){
      box.style.display = i === curStep ? '' : 'none';
    }
  }
}

function loadInitialData(){
  document.getElementById('stepAssetGrid').innerHTML = '<p class="fp-load-state" role="status">Loading your available shares…</p>';
  // 1. Assets
  if(window.FantradeAPI && FantradeAPI.getFanPlayEligibleAssets){
    FantradeAPI.getFanPlayEligibleAssets().then(function(res){
      if(res.success && res.data){
        eligibleAssets = res.data;
        renderAssetGrid();
      }
    }).catch(function(e){
      document.getElementById('stepAssetGrid').innerHTML = '<div class="fp-load-state" role="status"><p>Your shares could not be loaded. Please try again.</p><button class="app-primary" type="button" onclick="window.resetWizard()">Try again</button></div>';
    });
  }

  // 2. Matches
  if(window.FantradeAPI && FantradeAPI.getFanPlayMatches){
    FantradeAPI.getFanPlayMatches().then(function(res){
      if(res.success && res.data){
        matchesList = res.data;
        renderMatchGrid();
      }
    }).catch(function(e){ console.warn('Matches load error:', e); });
  }

  // 3. Markets
  if(window.FantradeAPI && FantradeAPI.getFanPlayMarkets){
    FantradeAPI.getFanPlayMarkets().then(function(res){
      if(res.success && res.data){
        marketsList = res.data;
        renderMarketGrid();
      }
    }).catch(function(e){ console.warn('Markets load error:', e); });
  }

  loadUserFanPlays();
}

document.querySelectorAll('#stepAssetGrid,#stepMatchGrid,#stepMarketGrid,#stepOptGrid').forEach(function(grid){
  grid.addEventListener('keydown', function(event){
    if((event.key === 'Enter' || event.key === ' ') && event.target.matches('[role="button"]')){
      event.preventDefault();event.target.click();
    }
  });
});
function renderAssetGrid(){
  var container = document.getElementById('stepAssetGrid');
  if(!container) return;
  if(eligibleAssets.length === 0){
    container.innerHTML = '<div style="grid-column:1/-1;padding:24px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:12px">No available shares yet. <a class="app-text-link" href="exchange.html">Explore the exchange</a> to choose your first player.</div>';
    return;
  }
  container.innerHTML = eligibleAssets.map(function(a){
    var isSel = selAsset && selAsset.id === a.id;
    return '<div role="button" tabindex="0" class="fp-asset-card' + (isSel ? ' selected' : '') + '" onclick="window.selectAsset(\'' + a.id + '\')">'
      + playerPhoto(a.symbol, a.name, 'fp-player-photo')
      + '<div class="fp-asset-sym">' + a.symbol + '</div>'
      + '<div class="fp-asset-name">' + a.name + ' · ' + (a.team || 'Pro') + '</div>'
      + '<div class="fp-asset-avail">Available: <b>' + (a.availableQuantity || 0).toLocaleString() + '</b> shares</div>'
      + '</div>';
  }).join('');
}

function selectAsset(id){
  selAsset = eligibleAssets.find(function(a){ return a.id === id; });
  renderAssetGrid();
  goToStep(2);
}
window.selectAsset = selectAsset;

function renderMatchGrid(){
  var container = document.getElementById('stepMatchGrid');
  if(!container) return;
  if(matchesList.length === 0){
    container.innerHTML = '<div style="padding:24px;text-align:center;color:#8E9AA8">No fixtures scheduled currently.</div>';
    return;
  }
  container.innerHTML = matchesList.map(function(m){
    var isSel = selMatch && selMatch.id === m.id;
    var dt = new Date(m.scheduledAt).toLocaleDateString(undefined, { weekday:'short', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' });
    return '<div role="button" tabindex="0" class="fp-match-card' + (isSel ? ' selected' : '') + '" onclick="window.selectMatch(\'' + m.id + '\')">'
      + '<div class="fp-match-comp">' + m.competition + ' · Matchweek ' + (m.matchweek || 1) + '</div>'
      + '<div class="fp-match-teams">' + m.homeTeam + ' vs ' + m.awayTeam + '</div>'
      + '<div class="fp-match-meta"><span>📅 ' + dt + '</span><span style="color:var(--lime)">Status: ' + m.status + '</span></div>'
      + '</div>';
  }).join('');
}

function selectMatch(id){
  selMatch = matchesList.find(function(m){ return m.id === id; });
  renderMatchGrid();
  goToStep(3);
}
window.selectMatch = selectMatch;

function renderMarketGrid(){
  var container = document.getElementById('stepMarketGrid');
  if(!container) return;
  container.innerHTML = marketsList.map(function(m){
    var isSel = selMarket && selMarket.id === m.id;
    return '<div role="button" tabindex="0" class="fp-market-card' + (isSel ? ' selected' : '') + '" onclick="window.selectMarket(\'' + m.id + '\')">'
      + '<div class="fp-market-name">' + m.name + '</div>'
      + '<div class="fp-market-limit">Max ' + m.maxSelections + ' ' + (m.maxSelections === 1 ? 'Selection' : 'Selections') + '</div>'
      + '<div class="fp-market-desc">' + (m.description || 'Configurable performance predictions.') + '</div>'

      + '</div>';
  }).join('');
}

function selectMarket(id){
  selMarket = marketsList.find(function(m){ return m.id === id; });
  renderMarketGrid();
  selOptionIds = [];
  goToStep(4);
}
window.selectMarket = selectMarket;

function loadOptions(){
  if(!selAsset || !selMatch || !selMarket) return;
  var sub = document.getElementById('stepPicksSub');
  if(sub){
    sub.textContent = selMarket.name + ' Tier: Select up to ' + selMarket.maxSelections + ' predictions for ' + selAsset.symbol + ' in ' + selMatch.homeTeam + ' vs ' + selMatch.awayTeam + '.';
  }
  if(window.FantradeAPI && FantradeAPI.getFanPlayOptions){
    FantradeAPI.getFanPlayOptions(selAsset.id, selMatch.id, selMarket.id).then(function(res){
      if(res.success && res.data){
        optionsList = res.data;
        renderOptionsGrid();
      }
    }).catch(function(e){ console.warn('Options load error:', e); });
  }
}

function renderOptionsGrid(){
  var container = document.getElementById('stepOptGrid');
  if(!container) return;
  if(optionsList.length === 0){
    container.innerHTML = '<div style="padding:24px;text-align:center;color:#8E9AA8">No prediction options published yet for this fixture and asset.</div>';
    return;
  }
  container.innerHTML = optionsList.map(function(opt){
    var isSel = selOptionIds.indexOf(opt.id) !== -1;
    return '<div role="button" tabindex="0" class="fp-opt-card' + (isSel ? ' selected' : '') + '" onclick="window.toggleOption(\'' + opt.id + '\')">'
      + '<div class="fp-opt-left">'
      + '  <div class="fp-opt-check">' + (isSel ? '✓' : '') + '</div>'
      + '  <div>'
      + '    <div class="fp-opt-label">' + opt.label + '</div>'
      + '    <div class="fp-opt-meta"><span>Category: ' + opt.category + '</span><span>•</span><span>Difficulty: ' + opt.difficulty + '</span>' + (opt.optionGroup ? '<span>• Group: ' + opt.optionGroup + '</span>' : '') + '</div>'
      + '  </div>'
      + '</div>'
      + '<div class="fp-opt-right">'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Success</div><div class="fp-opt-suc">+' + opt.successFP + ' FP</div></div>'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Failure</div><div class="fp-opt-fail">' + opt.failureFP + ' FP</div></div>'
      + '</div>'
      + '</div>';
  }).join('');
}

function toggleOption(id){
  var idx = selOptionIds.indexOf(id);
  var opt = optionsList.find(function(o){ return o.id === id; });
  if(idx !== -1){
    selOptionIds.splice(idx, 1);
  } else {
    // 1. Max selections check
    if(selMarket && selOptionIds.length >= selMarket.maxSelections){
      showToast('Maximum ' + selMarket.maxSelections + ' selections reached for ' + selMarket.name + '.', 'error');
      return;
    }
    // 2. Option group exclusivity check
    if(opt && opt.optionGroup){
      var groupMatch = selOptionIds.map(function(oid){ return optionsList.find(function(o){ return o.id === oid; }); })
        .find(function(o){ return o && o.optionGroup === opt.optionGroup; });
      if(groupMatch){
        showToast('Only one selection allowed from group "' + opt.optionGroup + '". Deselect ' + groupMatch.label + ' first.', 'error');
        return;
      }
    }
    selOptionIds.push(id);
  }
  renderOptionsGrid();
}
window.toggleOption = toggleOption;

function setStakePct(pct){
  if(!selAsset) return;
  var avail = selAsset.availableQuantity || 0;
  stakeShares = Math.max(1, Math.floor(avail * pct));
  var inp = document.getElementById('stakeInput');
  if(inp) inp.value = stakeShares;
  updateStakeCalculations();
}
window.setStakePct = setStakePct;

function updateStakeCalculations(){
  var inp = document.getElementById('stakeInput');
  if(inp){
    stakeShares = parseInt(inp.value, 10) || 0;
  }
  var owned = selAsset ? (selAsset.totalQuantity || 0) : 0;
  var locked = selAsset ? (selAsset.lockedQuantity || 0) : 0;
  var avail = selAsset ? (selAsset.availableQuantity || 0) : 0;
  var remain = Math.max(0, avail - stakeShares);

  if(document.getElementById('sOwned')) document.getElementById('sOwned').textContent = owned.toLocaleString();
  if(document.getElementById('sLocked')) document.getElementById('sLocked').textContent = locked.toLocaleString();
  if(document.getElementById('sAvail')) document.getElementById('sAvail').textContent = avail.toLocaleString();
  if(document.getElementById('sRemain')) document.getElementById('sRemain').textContent = remain.toLocaleString();
}
window.updateStakeCalculations = updateStakeCalculations;

function renderReview(){
  var container = document.getElementById('reviewBreakdown');
  if(!container || !selAsset || !selMatch || !selMarket) return;
  var selectedOpts = selOptionIds.map(function(id){ return optionsList.find(function(o){ return o.id === id; }); }).filter(Boolean);

  var maxSucFP = selectedOpts.reduce(function(acc, o){ return acc + (o.successFP * stakeShares); }, 0);
  var maxFailFP = selectedOpts.reduce(function(acc, o){ return acc + (o.failureFP * stakeShares); }, 0);

  var maxSucFTR = (maxSucFP / 1000).toFixed(2);
  var maxFailFTR = (maxFailFP / 1000).toFixed(2);

  container.innerHTML = '<div class="fp-breakdown-row"><span>Player / Coach Asset</span><b>' + selAsset.symbol + ' (' + selAsset.name + ')</b></div>'
    + '<div class="fp-breakdown-row"><span>Fixture</span><b>' + selMatch.homeTeam + ' vs ' + selMatch.awayTeam + '</b></div>'
    + '<div class="fp-breakdown-row"><span>Market Tier</span><b>' + selMarket.name + '</b></div>'
    + '<div class="fp-breakdown-row"><span>Staked Player Shares</span><b style="color:var(--lime)">' + stakeShares.toLocaleString() + ' shares locked</b></div>'
    + '<div class="fp-breakdown-row" style="border-top:1px solid rgba(255,255,255,.06);padding-top:8px"><span>Selected Predictions</span><b>' + selectedOpts.length + ' options</b></div>'
    + selectedOpts.map(function(o){
        return '<div style="display:flex;justify-content:space-between;font-size:11.5px;color:#CAD2C5;padding-left:10px">• ' + o.label + ' <span style="color:var(--lime)">+' + o.successFP + '</span> / <span style="color:#FF5E5E">' + o.failureFP + ' FP</span></div>';
      }).join('')
    + '<div class="fp-breakdown-row" style="border-top:1px solid rgba(255,255,255,.06);padding-top:8px"><span>Potential Fans Point (FP) Range</span><b>' + maxFailFP.toLocaleString() + ' FP to +' + maxSucFP.toLocaleString() + ' FP</b></div>'
    + '<div class="fp-breakdown-row"><span>Potential $FTR Settlement (1,000 FP = 1 $FTR)</span><b style="color:var(--amber)">' + (maxFailFTR > 0 ? '+' : '') + maxFailFTR + ' $FTR to +' + maxSucFTR + ' $FTR</b></div>';
}

function submitActivation(){
  var btn = document.getElementById('btnActivate');
  if(btn) { btn.disabled = true; btn.textContent = 'Locking Shares & Activating...'; }

  var idempotencyKey = 'fp_act_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);

  var payload = {
    type: 'INDIVIDUAL',
    assetId: selAsset.id,
    matchId: selMatch.id,
    marketId: selMarket.id,
    stakedShares: stakeShares,
    selectedOptionIds: selOptionIds,
    idempotencyKey: idempotencyKey
  };

  if(window.FantradeAPI && FantradeAPI.activateFanPlay){
    FantradeAPI.activateFanPlay(payload).then(function(res){
      if(res.success && res.data){
        showToast('FanPlay position successfully activated! Shares locked.', 'success');
        document.getElementById('step7Msg').textContent = 'Successfully locked ' + stakeShares.toLocaleString() + ' ' + selAsset.symbol + ' shares. ID: ' + res.data.id;
        goToStep(7);
        loadUserFanPlays();
      } else {
        showToast(res.error || 'Activation failed', 'error');
        if(btn){ btn.disabled = false; btn.textContent = 'Lock Shares & Activate FanPlay'; }
      }
    }).catch(function(err){
      showToast(err.message || 'Activation network error', 'error');
      if(btn){ btn.disabled = false; btn.textContent = 'Lock Shares & Activate FanPlay'; }
    });
  }
}
window.submitActivation = submitActivation;

function loadUserFanPlays(){
  if(window.FantradeAPI && FantradeAPI.getFanPlays){
    FantradeAPI.getFanPlays().then(function(res){
      if(res.success && res.data){
        userFanPlays = res.data;
        updateDashboardMetrics();
        renderActiveList();
        renderHistoryList();
      }
    }).catch(function(e){ console.warn('Load fanplays error:', e); });
  }
}

function updateDashboardMetrics(){
  var active = userFanPlays.filter(function(fp){ return fp.status === 'ACTIVE' || fp.status === 'LIVE' || fp.status === 'PENDING_SETTLEMENT'; });
  var settled = userFanPlays.filter(function(fp){ return fp.status === 'SETTLED'; });

  var totalLocked = active.reduce(function(acc, fp){ return acc + (fp.stakedShares || 0); }, 0);
  var provFP = active.reduce(function(acc, fp){ return acc + (fp.totalFP || 0); }, 0);
  var settledFTR = settled.reduce(function(acc, fp){ return acc + (fp.ftrSettlement || 0); }, 0);

  if(document.getElementById('mLockedShares')) document.getElementById('mLockedShares').textContent = totalLocked.toLocaleString();
  if(document.getElementById('mActiveCount')) document.getElementById('mActiveCount').textContent = active.length;
  if(document.getElementById('tabActiveCount')) document.getElementById('tabActiveCount').textContent = active.length;
  if(document.getElementById('mProvFP')) document.getElementById('mProvFP').textContent = (provFP >= 0 ? '+' : '') + provFP.toLocaleString() + ' FP';
  if(document.getElementById('mSettledFTR')) document.getElementById('mSettledFTR').textContent = (settledFTR >= 0 ? '+' : '') + settledFTR.toFixed(2) + ' $FTR';
}

function renderActiveList(){
  var container = document.getElementById('activeList');
  if(!container) return;
  var active = userFanPlays.filter(function(fp){ return fp.status === 'ACTIVE' || fp.status === 'LIVE' || fp.status === 'PENDING_SETTLEMENT'; });
  if(active.length === 0){
    container.innerHTML = '<div style="padding:40px 20px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:14px">'
      + '<div style="font-size:32px;margin-bottom:8px">⚽</div>'
      + '<div style="font-weight:700;color:#fff;margin-bottom:4px">No Active Positions</div>'
      + '<div style="font-size:12px;margin-bottom:16px">You currently have no shares locked in active matchday FanPlays.</div>'
      + '<button type="button" class="fp-btn-next" style="padding:10px 20px;font-size:12px" onclick="switchFPView(\'wizard\')">Create New Position</button>'
      + '</div>';
    return;
  }
  container.innerHTML = active.map(function(fp){
    var assetSym = fp.asset ? fp.asset.symbol : '$ASSET';
    var matchName = fp.match ? (fp.match.homeTeam + ' vs ' + fp.match.awayTeam) : 'Matchday Fixture';
    var tierName = fp.market ? fp.market.name : 'FanPlay';
    var canSettle = fp.match && (fp.match.status === 'FINISHED' || fp.match.status === 'FINAL');
    var canCancel = fp.status === 'ACTIVE' && fp.match && (fp.match.status === 'SCHEDULED');

    return '<div class="fp-panel" style="padding:18px;margin-bottom:12px">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
      + '  <div>'
      + '    <span style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:17px;color:#fff">' + assetSym + '</span>'
      + '    <span style="font-size:12px;color:#8E9AA8;margin-left:8px">' + matchName + '</span>'
      + '  </div>'
      + '  <span style="font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;background:rgba(24,0,173,.12);color:var(--lime)">' + fp.status + '</span>'
      + '</div>'
      + '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;background:rgba(255,255,255,.02);padding:10px;border-radius:10px;margin-bottom:12px">'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Market Tier</div><b style="font-size:12px;color:#fff">' + tierName + '</b></div>'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Locked Shares</div><b style="font-size:12px;color:var(--lime)">' + (fp.stakedShares || 0).toLocaleString() + '</b></div>'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Live Prov. FP</div><b style="font-size:12px;color:var(--amber)">' + (fp.totalFP || 0).toLocaleString() + ' FP</b></div>'
      + '</div>'
      + '<div style="display:flex;flex-direction:column;gap:4px;margin-bottom:12px">'
      + (fp.selections || []).map(function(s){
          return '<div style="display:flex;justify-content:space-between;font-size:12px;color:#CAD2C5">'
            + '<span>' + s.optionLabel + '</span>'
            + '<span style="font-weight:600;' + (s.evaluationResult === 'SUCCESS' ? 'color:var(--lime)' : s.evaluationResult === 'FAILURE' ? 'color:#FF5E5E' : 'color:#8E9AA8') + '">' + (s.evaluationResult || 'PENDING') + '</span>'
            + '</div>';
        }).join('')
      + '</div>'
      + '<div style="display:flex;gap:10px;justify-content:flex-end">'
      + (canCancel ? '<button type="button" class="fp-btn-back" style="padding:6px 14px;font-size:11px" onclick="window.cancelFanPlay(\'' + fp.id + '\')">Cancel Position</button>' : '')
      + (canSettle ? '<button type="button" class="fp-btn-next" style="padding:6px 14px;font-size:11px" onclick="window.settleFanPlay(\'' + fp.id + '\')">Execute Final Settlement</button>' : '')
      + '</div>'
      + '</div>';
  }).join('');
}

function renderHistoryList(){
  var container = document.getElementById('historyList');
  if(!container) return;
  var settled = userFanPlays.filter(function(fp){ return fp.status === 'SETTLED' || fp.status === 'CANCELLED' || fp.status === 'VOID'; });
  if(settled.length === 0){
    container.innerHTML = '<div style="padding:40px 20px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:14px">'
      + '<div style="font-weight:700;color:#fff;margin-bottom:4px">No History</div>'
      + '<div style="font-size:12px">Settled matchday positions and $FTR ledger payouts will appear here.</div>'
      + '</div>';
    return;
  }
  container.innerHTML = settled.map(function(fp){
    var assetSym = fp.asset ? fp.asset.symbol : '$ASSET';
    var matchName = fp.match ? (fp.match.homeTeam + ' vs ' + fp.match.awayTeam) : 'Matchday Fixture';
    var isWin = (fp.ftrSettlement || 0) >= 0;
    var dt = new Date(fp.settledAt || fp.createdAt).toLocaleDateString();

    return '<div class="fp-panel" style="padding:18px;margin-bottom:12px">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
      + '  <div>'
      + '    <span style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:17px;color:#fff">' + assetSym + '</span>'
      + '    <span style="font-size:12px;color:#8E9AA8;margin-left:8px">' + matchName + ' · ' + dt + '</span>'
      + '  </div>'
      + '  <span style="font-size:14px;font-weight:800;color:' + (isWin ? 'var(--lime)' : '#FF5E5E') + '">'
      + (isWin ? '+' : '') + (fp.ftrSettlement || 0).toFixed(2) + ' $FTR'
      + '  </span>'
      + '</div>'
      + '<div style="display:flex;gap:14px;font-size:11.5px;color:#8E9AA8;margin-bottom:12px">'
      + '  <span>Staked: <b>' + (fp.stakedShares || 0).toLocaleString() + ' shares</b> (Unlocked ✓)</span>'
      + '  <span>Total FP: <b style="color:#fff">' + (fp.totalFP || 0).toLocaleString() + ' FP</b></span>'
      + '  <span>Status: <b>' + fp.status + '</b></span>'
      + '</div>'
      + '<div style="display:flex;flex-direction:column;gap:6px;border-top:1px solid rgba(255,255,255,.05);padding-top:10px">'
      + (fp.selections || []).map(function(s){
          var res = s.evaluationResult;
          var resColor = res === 'SUCCESS' ? 'var(--lime)' : res === 'FAILURE' ? '#FF5E5E' : '#8E9AA8';
          return '<div style="display:flex;justify-content:space-between;align-items:center;font-size:12px">'
            + '<div><span style="color:#CAD2C5">• ' + s.optionLabel + '</span>'
            + (s.evaluationReason ? '<div style="font-size:10.5px;color:#8E9AA8;padding-left:12px">' + s.evaluationReason + '</div>' : '')
            + '</div>'
            + '<div style="text-align:right">'
            + '<span style="font-weight:700;color:' + resColor + '">' + (res || 'N/A') + '</span> '
            + '<span style="color:#8E9AA8;font-size:11px">(' + (s.optionFP > 0 ? '+' : '') + s.optionFP + ' FP)</span>'
            + '</div>'
            + '</div>';
        }).join('')
      + '</div>'
      + '</div>';
  }).join('');
}

function cancelFanPlay(id){
  if(!confirm('Are you sure you want to cancel this FanPlay position and unlock your shares?')) return;
  if(window.FantradeAPI && FantradeAPI.cancelFanPlay){
    FantradeAPI.cancelFanPlay(id).then(function(res){
      if(res.success){
        showToast('FanPlay position cancelled. Shares unlocked.', 'success');
        loadUserFanPlays();
      } else {
        showToast(res.error || 'Failed to cancel', 'error');
      }
    }).catch(function(e){ showToast(e.message, 'error'); });
  }
}
window.cancelFanPlay = cancelFanPlay;

function settleFanPlay(id){
  if(window.FantradeAPI && FantradeAPI.settleFanPlay){
    FantradeAPI.settleFanPlay(id).then(function(res){
      if(res.success){
        showToast('Final match settlement complete! Shares unlocked and ledger updated.', 'success');
        loadUserFanPlays();
      } else {
        showToast(res.error || 'Settlement failed', 'error');
      }
    }).catch(function(e){ showToast(e.message, 'error'); });
  }
}
window.settleFanPlay = settleFanPlay;

// Expose handlers to global window scope for inline HTML onclick attributes
window.switchFPView = switchFPView;
window.resetWizard = resetWizard;
window.goToStep = goToStep;
window.selectAsset = selectAsset;
window.selectMatch = selectMatch;
window.selectMarket = selectMarket;
window.toggleOption = toggleOption;
window.setStakePct = setStakePct;
window.updateStakeCalculations = updateStakeCalculations;
window.submitActivation = submitActivation;
window.cancelFanPlay = cancelFanPlay;
window.settleFanPlay = settleFanPlay;

// Initial load
loadInitialData();
setInterval(loadUserFanPlays, 15000);
window.addEventListener('fantrade:statechange', loadUserFanPlays);
"""
page("fanplay.html", "FanPlay — Fantrade", "".join(fp), FP_JS, FP_CSS, app=True)


# ══════════════════════════════════════════════════════════
# 4b. LIVE BOARD — its own screen, nothing boxed
# ══════════════════════════════════════════════════════════
# ── matchday board ────────────────────────────────────────────────
# (fid, home, home code, home colour, home score, away, away code,
#  away colour, away score, status, clock, your asset on the pitch)
MATCHDAY = [
    ("eng", "Premier League", "Matchweek 7", [
        ("m-ars", "Arsenal", "ARS", "#EF0107", "2", "Chelsea", "CHE", "#034694", "1", "live", "68'", "$Saka · 42 FP"),
        ("m-mci", "Man City", "MCI", "#6CABDD", "3", "Everton", "EVE", "#003399", "0", "live", "71'", "$Haaland · 58 FP"),
        ("m-mun", "Man United", "MUN", "#DA291C", "1", "Tottenham", "TOT", "#8f95a3", "1", "live", "54'", "$Bruno · 31 FP"),
        ("m-new", "Newcastle", "NEW", "#8f95a3", "\u2013", "Brighton", "BHA", "#0057B8", "\u2013", "soon", "19:30", ""),
    ]),
    ("esp", "La Liga", "Jornada 7", [
        ("m-rma", "Real Madrid", "RMA", "#FEBE10", "4", "Real Betis", "BET", "#00954C", "0", "ft", "FT", "$Vinicius · 44 FP"),
        ("m-bar", "Barcelona", "BAR", "#A50044", "\u2013", "Sevilla", "SEV", "#D4021D", "\u2013", "soon", "21:00", "$Pedri"),
    ]),
    ("ger", "Bundesliga", "Spieltag 6", [
        ("m-bay", "Bayern", "FCB", "#DC052D", "2", "RB Leipzig", "RBL", "#DD0741", "2", "ht", "HT", "$Musiala · 19 FP"),
    ]),
    ("ita", "Serie A", "Play-offs", [
        ("m-sud", "Sudtirol", "SUD", "#8f95a3", "1", "Bari", "BAR", "#C8102E", "1", "aet", "AET", ""),
        ("m-bar2", "Barnsley", "BAR", "#D2122E", "\u2013", "Sheff Wednesday", "SHW", "#0057B8", "\u2013", "soon", "20:30", ""),
    ]),
]

LB_CSS = FP_CSS + """
.kc-home-wrap{max-width:680px;margin:0 auto;padding:0 16px 84px}
.bezel.flat .datestrip{margin-bottom:4px}
"""

lb = ['<main><div class="kc-home-wrap" style="padding-top:0;padding-bottom:84px">']

# Topbar
lb.append(T('<div class="kc-topbar" style="display:flex;align-items:center;justify-content:space-between;padding:8px 0 16px">'
            '<a class="kc-icon-btn" href="fanplay.html" aria-label="Back to FanPlay" style="width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;color:#8E9AA8;text-decoration:none">@@</a>'
            '<div style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:17px;text-transform:uppercase">Matchday Live Board</div>'
            '<button class="bell" type="button" id="calBtn" aria-label="Calendar" style="width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;color:#8E9AA8;cursor:pointer">@@</button>'
            '</div>',
            ic("arrow", "ic"), ic("calendar", "ic")))

lb.append('<div style="display:flex;flex-direction:column;gap:16px">')

# date strip card
lb.append(T('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden;padding:14px" data-reveal>'
            '<div class="datestrip" style="margin-bottom:0">'
            '<button class="livetgl" type="button" id="liveOnly" aria-pressed="false">'
            '<span class="dot-live"></span>Live only</button>'
            '<div class="dateline">'
            '<div class="dates" id="dateStrip">'
            '<span class="nudge">@@</span>'
            '<button type="button" aria-pressed="false"><small>Sun</small><b>28 Sep</b></button>'
            '<button type="button" aria-pressed="true"><small>Today</small><b>29 Sep</b></button>'
            '<button type="button" aria-pressed="false"><small>Tue</small><b>30 Sep</b></button>'
            '<span class="nudge">@@</span></div>'
            '</div></div></div>',
            "‹", "›"))

# featured match
lb.append(T('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal>'
            '<div class="feat islive" id="featCard" style="border:0">'
            '<div class="feat-top"><button type="button" id="featHide">Hide</button>'
            '<div class="mid"><b>Emirates Stadium</b><span>Matchweek 7</span></div>'
            '<a href="#board" style="color:var(--faint)">Match</a></div>'
            '<div class="feat-mid">'
            '<div class="side"><span class="tcrest" style="background:linear-gradient(160deg,#EF0107,#8d0104)">ARS</span>'
            '<div class="nm">Arsenal</div><div class="ha">@@ Home</div></div>'
            '<div class="sc" id="featScore">2 : 1</div>'
            '<div class="side"><span class="tcrest" style="background:linear-gradient(160deg,#034694,#02295a)">CHE</span>'
            '<div class="nm">Chelsea</div><div class="ha">Away</div></div></div>'
            '<span class="minute live" id="featMin">68&rsquo;</span></div></div>',
            ic("stadium", "ic")))

# competition groups
lb.append('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad">'
          '<div id="boardList">')
for code, comp, sub, fixtures in MATCHDAY:
    lb.append(T('<div class="comp" style="padding:14px 10px 8px">@@<div><b>@@</b><span>@@</span></div>'
                '<a class="more" href="#board">All @@</a></div>',
                flag(code), comp, sub, ic("arrow", "ic-sm")))
    for fid, home, hsh, hc, hs, away, ash, ac, a_s, st, clock, mine in fixtures:
        hw = hs.isdigit() and a_s.isdigit() and int(hs) > int(a_s)
        aw = hs.isdigit() and a_s.isdigit() and int(a_s) > int(hs)
        lb.append(T('<div class="fixt@@" data-fid="@@" data-live="@@" style="margin:0 0 8px">'
                    '<div class="stat">@@</div>'
                    '<div class="teams">'
                    '<div class="tm@@"><span class="tcrest sm" style="background:@@">@@</span>'
                    '<span class="n">@@</span>@@<span class="g">@@</span></div>'
                    '<div class="tm@@"><span class="tcrest sm" style="background:@@">@@</span>'
                    '<span class="n">@@</span><span class="g">@@</span></div></div>'
                    '<button class="star" type="button" data-fav="@@" aria-pressed="false" '
                    'aria-label="Follow this fixture">@@</button></div>',
                    " live" if st in ("live", "ht") else "", fid, "1" if st in ("live", "ht") else "0",
                    ("<b>%s</b>" % clock) if st in ("live", "ht", "aet") else clock,
                    "" if hw or not (hw or aw) else " dim", hc, hsh, home,
                    ('<span class="mine">%s</span>' % mine) if mine else "", hs,
                    "" if aw or not (hw or aw) else " dim", ac, ash, away, a_s,
                    fid, ic("star", "ic")))
lb.append('</div>')

lb.append('<div style="padding:12px 0 6px;display:flex;align-items:center;gap:12px;flex-wrap:wrap">'
          '<span style="font-size:11.5px;color:var(--faint);font-weight:300" id="boardNote">'
          '9 fixtures · 4 with your assets</span></div>')
lb.append('</div></div>')

# side cards — countdown + running total
lb.append('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad"><div class="k-label">Round closes in</div>'
          '<div class="countdown"><div class="cd"><b id="cdH">04</b><span>Hours</span></div>'
          '<div class="cd"><b id="cdM">12</b><span>Mins</span></div>'
          '<div class="cd"><b id="cdS">38</b><span>Secs</span></div></div>'
          '</div></div>'
          '<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden" data-reveal><div class="core pad"><div class="k-label">Running total</div>'
          '<div class="value-big" id="runFP">175 <small>FP</small></div>'
          '<div class="delta">Club mode · Elite · +15%</div>'
          '<div style="margin-top:20px"><div class="b-row"><span>Starters scoring</span><b>7 of 11</b></div>'
          '<div class="b-row"><span>Subs activated</span><b>1</b></div>'
          '<div class="b-row"><span>Coach modifier</span><b>+3.0%</b></div>'
          '<div class="b-row total"><span>Followed fixtures</span><b id="favCount">1</b></div></div>'
          '<div class="k-label" style="margin-top:26px">Club form</div>'
          '<div class="form5" style="margin-bottom:12px">'
          '<i class="l">L</i><i class="l">L</i><i class="w">W</i><i class="w">W</i><i class="w">W</i></div>'
          '</div></div>')

lb.append('</div></div></main>')


LIVE_JS = r"""
var left=4*3600+12*60+38;
function pad(n){ return n<10?'0'+n:''+n; }
if(!reduce) setInterval(function(){
  if(left<=0) return; left--;
  document.getElementById('cdH').textContent=pad(Math.floor(left/3600));
  document.getElementById('cdM').textContent=pad(Math.floor(left%3600/60));
  document.getElementById('cdS').textContent=pad(left%60);
},1000);
var run=175;
if(!reduce) setInterval(function(){
  if(Math.random()<.45){ run+=Math.round(Math.random()*4)+1;
    var el=document.getElementById('runFP');
    el.innerHTML=run+" <small>FP</small>";
    el.style.color='#1800ad'; setTimeout(function(){ el.style.color=''; },800); }
},2600);

// ══ matchday board ══════════════════════════════════════════════
function $(id){ return document.getElementById(id); }

// follow / unfollow a fixture — persists to FT state
function paintStars(){
  var n = 0;
  document.querySelectorAll('.star[data-fav]').forEach(function(b){
    var on = FT.isFav(b.dataset.fav);
    b.setAttribute('aria-pressed', on ? 'true' : 'false');
    b.setAttribute('aria-label', (on ? 'Stop following ' : 'Follow ') + 'this fixture');
    if(on) n++;
  });
  if($('favCount')) $('favCount').textContent = n;
}
document.querySelectorAll('.star[data-fav]').forEach(function(b){
  b.addEventListener('click', function(){
    var added = FT.toggleFav(b.dataset.fav);
    paintStars();
    showToast(added ? 'Following this fixture — you will be told when it settles.'
                    : 'Stopped following that fixture.', added ? 'success' : 'info');
  });
});
paintStars();
window.addEventListener('fantrade:statechange', paintStars);

// live-only filter
var liveOnly = false;
function filterBoard(){
  var shown = 0;
  document.querySelectorAll('.fixt').forEach(function(r){
    var keep = !liveOnly || r.dataset.live === '1';
    r.style.display = keep ? '' : 'none';
    if(keep) shown++;
  });
  document.querySelectorAll('.comp').forEach(function(c){
    var any = false, n = c.nextElementSibling;
    while(n && n.classList.contains('fixt')){
      if(n.style.display !== 'none') any = true;
      n = n.nextElementSibling;
    }
    c.style.display = any ? '' : 'none';
  });
  $('boardNote').textContent = liveOnly
    ? shown + ' fixtures in play right now'
    : '9 fixtures tracked this window · 4 of them carry your assets';
}
$('liveOnly').addEventListener('click', function(){
  liveOnly = !liveOnly;
  $('liveOnly').setAttribute('aria-pressed', liveOnly ? 'true' : 'false');
  filterBoard();
});

// date strip
document.querySelectorAll('#dateStrip button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#dateStrip button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed', 'true');
    var day = b.querySelector('small').textContent;
    if(day === 'Today'){ filterBoard(); return; }
    showToast(day + ' has no settled Fantrade window yet — the board shows today.', 'info');
  });
});

$('calBtn').addEventListener('click', function(){
  openModal('<h3 class="ft-modal-title">Settlement calendar</h3>'
    + '<p class="ft-modal-desc">Rounds run on a fixed weekly clock. Entries lock at the window and settle on the '
    + 'last final whistle inside it.</p>'
    + '<div class="ft-modal-card">'
    + '<div class="m-row"><span>Matchday 07</span><b style="color:var(--live)">In play · closes Fri 18:30</b></div>'
    + '<div class="m-row"><span>Matchday 08</span><b>Opens Sat 09:00</b></div>'
    + '<div class="m-row"><span>Matchday 09</span><b>Opens 12 Oct</b></div>'
    + '<div class="m-row total"><span>Cycle ends</span><b>Matchday 10 · 19 Oct</b></div></div>'
    + '<p style="font-size:11.5px;color:var(--faint);font-weight:300;line-height:1.6;margin:0">'
    + 'Prototype build — the board shows a fixed set of fixtures.</p>');
});

// hide the featured card
$('featHide').addEventListener('click', function(){
  var c = $('featCard');
  var hidden = c.dataset.hidden === '1';
  c.dataset.hidden = hidden ? '0' : '1';
  c.querySelector('.feat-mid').style.display = hidden ? '' : 'none';
  c.querySelector('.minute').style.display = hidden ? '' : 'none';
  c.style.paddingBottom = hidden ? '' : '20px';
  $('featHide').textContent = hidden ? 'Hide' : 'Show';
});

// the featured minute ticks with the round
(function(){
  if(reduce) return;
  var min = 68, hs = 2, as = 1;
  setInterval(function(){
    if(min >= 90){ $('featMin').textContent = "90'+" + (min - 89); }
    else { min++; $('featMin').textContent = min + "\u2019"; }
    if(min < 90 && Math.random() < 0.08){
      Math.random() < 0.6 ? hs++ : as++;
      $('featScore').textContent = hs + ' : ' + as;
      showToast('Goal at the Emirates — ' + hs + ':' + as + '.', 'info');
    }
  }, 5000);
})();
"""
page("liveboard.html", "Live board — Fantrade", "".join(lb), LIVE_JS, LB_CSS, app=True)


print("built:", sorted(os.listdir(OUT)))
