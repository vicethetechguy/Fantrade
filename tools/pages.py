# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app_design import apply_design, intro, tab_intro
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
.kc-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);display:grid;place-items:center;flex:none;color:var(--lime);font-family:Space Grotesk,sans-serif;font-size:11px;font-weight:800;overflow:hidden}
.kc-avatar .player-photo{width:100%;height:100%;object-fit:cover;object-position:50% 18%;display:block}
.kc-avatar.coach{color:var(--amber);border-color:rgba(255,106,31,.25);background:rgba(255,106,31,.08)}
.kc-pair-title{display:flex;align-items:center;gap:5px;font-family:Space Grotesk,sans-serif;font-weight:700;font-size:14.5px;line-height:1.1;color:var(--ink)}
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

ex = [T('<main><div class="kc-ex-wrap">' + tab_intro('Exchange') +
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
var favs = JSON.parse(localStorage.getItem('ft_favorites') || '["FSAKA","FHLND","FKM7","FYAML"]');

function fmt(n){ return n.toLocaleString('en-US'); }

function getFilteredList(){
  var s = FT.getState();
  var list = ASSETS.filter(function(a){
    // Search filter
    if(q && (a.t + ' ' + ftSym(a.t) + ' ' + a.n).toLowerCase().indexOf(q) < 0) return false;

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
    var sym = ftSym(a.t);
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
from club_pages import CLUB_HTML, BUILDER_HTML, JS as CLUB_PAGES_JS
page("clubs.html", "Dream Clubs — Fantrade", CLUB_HTML, CLUB_PAGES_JS, app=True)
page("club-builder.html", "Club builder — Fantrade", BUILDER_HTML, CLUB_PAGES_JS, app=True)




# ══════════════════════════════════════════════════════════
# 4. FANPLAY ENGINE (PROMPT 4)
# ══════════════════════════════════════════════════════════
FP_CSS = """
.kc-home-wrap{max-width:760px;margin:0 auto;padding:12px 16px 94px}
.fp-topbar{display:flex;align-items:center;justify-content:space-between;padding:8px 0 16px;border-bottom:1px solid rgba(255,255,255,.06)}
.fp-title-box{display:flex;align-items:center;gap:12px}
.fp-title-box h2{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:18px;margin:0;color:#fff;text-transform:uppercase}
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
.fp-panel-title{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:18px;color:#fff;margin:0 0 6px;text-transform:uppercase}
.fp-panel-sub{font-size:13px;color:#8E9AA8;margin:0 0 18px}

/* Asset Selection Grid */
.fp-asset-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.fp-asset-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:14px;cursor:pointer;transition:all .2s;text-align:left}
.fp-asset-card:hover{border-color:rgba(24,0,173,.4);background:rgba(255,255,255,.05)}
.fp-asset-card.selected{border-color:var(--lime);background:rgba(24,0,173,.08);box-shadow:0 0 18px rgba(24,0,173,.15)}
.fp-asset-sym{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:16px;color:#fff}
.fp-asset-name{font-size:11.5px;color:#8E9AA8;margin-top:2px}
.fp-asset-avail{margin-top:10px;font-size:11px;color:#1800ad;font-weight:600}

/* Match Selection Grid */
.fp-match-grid{display:flex;flex-direction:column;gap:10px}
.fp-match-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:16px;cursor:pointer;transition:all .2s}
.fp-match-card:hover{border-color:rgba(24,0,173,.4)}
.fp-match-card.selected{border-color:var(--lime);background:rgba(24,0,173,.08)}
.fp-match-comp{font-size:10.5px;font-weight:700;color:var(--amber);text-transform:uppercase;letter-spacing:.06em}
.fp-match-teams{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:17px;color:#fff;margin:6px 0}
.fp-match-meta{font-size:11.5px;color:#8E9AA8;display:flex;align-items:center;gap:12px}

/* Market Tiers Grid (§10, §11, §12) */
.fp-market-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
@media (max-width:600px){.fp-market-grid{grid-template-columns:1fr}}
.fp-market-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:16px;cursor:pointer;transition:all .2s;display:flex;flex-direction:column;gap:8px}
.fp-market-card:hover{border-color:rgba(24,0,173,.3)}
.fp-market-card.selected{border-color:var(--lime);background:rgba(24,0,173,.08)}
.fp-market-name{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:15px;color:#fff;text-transform:uppercase}
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
.fp-opt-label{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:14px;color:#fff}
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
.fp-btn-back{flex:1;padding:14px 0;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);color:#fff;border-radius:12px;font-family:Space Grotesk,sans-serif;font-weight:700;font-size:13px;text-transform:uppercase;cursor:pointer;text-align:center}
.fp-btn-next{flex:2;padding:14px 0;background:var(--lime);border:0;color:#fff;border-radius:12px;font-family:Space Grotesk,sans-serif;font-weight:700;font-size:13.5px;text-transform:uppercase;cursor:pointer;text-align:center;box-shadow:0 0 20px rgba(24,0,173,.3)}
"""

fp = ['<main><div class="kc-home-wrap fanplay-layout">', tab_intro('FanPlay')]

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

var DEFAULT_MATCHES = [
  { id: 'match-1', competition: 'Premier League', homeTeam: 'Arsenal', awayTeam: 'Chelsea', scheduledAt: '2026-10-10T15:00:00Z', status: 'SCHEDULED', matchweek: 8 },
  { id: 'match-2', competition: 'Premier League', homeTeam: 'Manchester City', awayTeam: 'Liverpool', scheduledAt: '2026-10-11T16:30:00Z', status: 'SCHEDULED', matchweek: 8 },
  { id: 'match-3', competition: 'La Liga', homeTeam: 'Real Madrid', awayTeam: 'Barcelona', scheduledAt: '2026-10-12T20:00:00Z', status: 'SCHEDULED', matchweek: 9 },
  { id: 'match-4', competition: 'Premier League', homeTeam: 'Manchester United', awayTeam: 'Brighton', scheduledAt: '2026-10-10T17:30:00Z', status: 'SCHEDULED', matchweek: 8 }
];

var DEFAULT_MARKETS = [
  { id: 'tier-1', tier: 'SIMPLE', name: 'Solo', maxSelections: 1, minSelections: 1, description: 'Choose one prediction for your player.' },
  { id: 'tier-2', tier: 'PRO', name: 'Pro', maxSelections: 3, minSelections: 2, description: 'Combine 2 to 3 performance predictions for higher multipliers.' },
  { id: 'tier-3', tier: 'ELITE', name: 'Elite', maxSelections: 5, minSelections: 3, description: 'High-stakes predictions across goals, assists and performance metrics.' }
];

function getFallbackOptions(asset, match, market){
  var name = asset ? asset.name : 'Player';
  var team = asset ? (asset.team || asset.club || 'Team') : 'Team';
  return [
    { id: 'opt-1', label: name + ' scores a goal', category: 'Goals', difficulty: 'Standard', successFP: 100, failureFP: -50, optionGroup: 'goals' },
    { id: 'opt-2', label: name + ' records an assist', category: 'Playmaking', difficulty: 'Standard', successFP: 90, failureFP: -45, optionGroup: 'assists' },
    { id: 'opt-3', label: '2+ shots on target', category: 'Attacking', difficulty: 'Moderate', successFP: 80, failureFP: -40, optionGroup: 'shots' },
    { id: 'opt-4', label: 'Creates 3+ chances', category: 'Playmaking', difficulty: 'Moderate', successFP: 110, failureFP: -55, optionGroup: 'chances' },
    { id: 'opt-5', label: 'Man of the Match rating (>8.0)', category: 'Performance', difficulty: 'Challenging', successFP: 200, failureFP: -90, optionGroup: 'motm' },
    { id: 'opt-6', label: team + ' clean sheet or win', category: 'Defending', difficulty: 'Standard', successFP: 75, failureFP: -35, optionGroup: 'defense' }
  ];
}

function getLocalEligibleAssets(){
  var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
  var teamMap = {
    'FSAKA': 'Arsenal', 'FBRN': 'Manchester United', 'FAITN': 'Barcelona', 'FPUTL': 'Barcelona', 'FKERR': 'Chelsea', 'FRUSS': 'Arsenal', 'FLJMS': 'Chelsea', 'FWILM': 'Arsenal', 'FEARP': 'Paris Saint-Germain', 'FWIEG': 'England Women', 'FHLND': 'Manchester City',
    'FARTA': 'Arsenal', 'FKM7': 'Real Madrid', 'FYAML': 'Barcelona',
    'FBEL': 'Real Madrid', 'FPLMR': 'Chelsea', 'FFODN': 'Manchester City',
    'FSALI': 'Arsenal', 'FPEDR': 'Barcelona', 'FRODR': 'Manchester City',
    'FVJR': 'Real Madrid', '$Rice': 'Arsenal', 'FWRTZ': 'Bayer Leverkusen',
    'FMUS': 'Bayern Munich', '$Gavi': 'Barcelona', '$Camavinga': 'Real Madrid',
    '$Guardiola': 'Manchester City'
  };
  var holdings = (s && s.holdings && Object.keys(s.holdings).length > 0) ? s.holdings : {
    'FSAKA': { n: 'Bukayo Saka', shares: 10000, avg: 31.40, p: 48.20, c: false },
    'FBRN': { n: 'Bruno Fernandes', shares: 5000, avg: 38.00, p: 39.75, c: false },
    'FHLND': { n: 'Erling Haaland', shares: 3000, avg: 68.50, p: 71.40, c: false },
    'FARTA': { n: 'Mikel Arteta', shares: 1000, avg: 20.50, p: 22.05, c: true }
  };
  var lockedMap = {};
  var entries = (s && s.fanplay && s.fanplay.activeEntries) ? s.fanplay.activeEntries : [];
  entries.forEach(function(e){
    var tgt = e.target || (e.asset && e.asset.symbol);
    if(tgt && (e.stakedShares || e.stake)){
      lockedMap[tgt] = (lockedMap[tgt] || 0) + (e.stakedShares || e.stake || 0);
    }
  });
  var list = [];
  Object.keys(holdings).forEach(function(sym){
    var h = holdings[sym];
    if(!h || !h.shares || h.shares <= 0) return;
    var locked = lockedMap[sym] || 0;
    var avail = Math.max(0, h.shares - locked);
    list.push({
      id: 'asset-' + sym.replace('$', '').toLowerCase(),
      assetId: 'asset-' + sym.replace('$', '').toLowerCase(),
      symbol: sym,
      name: h.n || sym,
      team: teamMap[sym] || (h.c ? 'Coach' : 'Pro'),
      club: teamMap[sym] || (h.c ? 'Coach' : 'Pro'),
      availableQuantity: avail,
      totalQuantity: h.shares,
      lockedQuantity: locked
    });
  });
  if(list.length === 0){
    list = [
      { id:'asset-saka', assetId:'asset-saka', symbol:'FSAKA', name:'Bukayo Saka', team:'Arsenal', club:'Arsenal', availableQuantity:10000, totalQuantity:10000, lockedQuantity:0 },
      { id:'asset-bruno', assetId:'asset-bruno', symbol:'FBRN', name:'Bruno Fernandes', team:'Manchester United', club:'Manchester United', availableQuantity:5000, totalQuantity:5000, lockedQuantity:0 },
      { id:'asset-haaland', assetId:'asset-haaland', symbol:'FHLND', name:'Erling Haaland', team:'Manchester City', club:'Manchester City', availableQuantity:3000, totalQuantity:3000, lockedQuantity:0 },
      { id:'asset-arteta', assetId:'asset-arteta', symbol:'FARTA', name:'Mikel Arteta', team:'Arsenal', club:'Arsenal', availableQuantity:1000, totalQuantity:1000, lockedQuantity:0 }
    ];
  }
  return list;
}

function normalizeAsset(a){
  var sym = a.symbol || '$ASSET';
  return {
    id: a.id || a.assetId || sym,
    assetId: a.assetId || a.id || sym,
    symbol: sym,
    name: a.name || sym,
    team: a.team || a.club || 'Pro',
    club: a.club || a.team || 'Pro',
    availableQuantity: a.availableQuantity != null ? a.availableQuantity : (a.totalQuantity != null ? a.totalQuantity : (a.shares || 0)),
    totalQuantity: a.totalQuantity != null ? a.totalQuantity : (a.ownedQuantity != null ? a.ownedQuantity : (a.shares || 0)),
    lockedQuantity: a.lockedQuantity || 0
  };
}

function normalizeMatch(m){
  return {
    id: m.id,
    competition: m.competition || 'Premier League',
    homeTeam: m.homeTeam || 'Home',
    awayTeam: m.awayTeam || 'Away',
    matchweek: m.matchweek || 1,
    status: m.status || 'SCHEDULED',
    scheduledAt: m.scheduledAt || m.kickoffTime || new Date().toISOString()
  };
}

function normalizeMarket(m){
  return {
    id: m.id,
    tier: m.tier || m.id,
    name: m.name || 'Tier',
    maxSelections: m.maxSelections || 1,
    minSelections: m.minSelections || 1,
    description: m.description || 'Configurable performance predictions.'
  };
}

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

function useLocalShares(){
  eligibleAssets = getLocalEligibleAssets();
  renderAssetGrid();
  if(matchesList.length === 0){
    matchesList = DEFAULT_MATCHES;
    renderMatchGrid();
  }
  if(marketsList.length === 0){
    marketsList = DEFAULT_MARKETS;
    renderMarketGrid();
  }
}
window.useLocalShares = useLocalShares;

function goToStep(s){
  if(s > curStep){
    if(curStep === 1 && !selAsset){
      if(eligibleAssets.length === 0){
        useLocalShares();
      }
      var assetGrid = document.getElementById('stepAssetGrid');
      var firstCard = assetGrid && assetGrid.querySelector('[role="button"]');
      if(firstCard){
        assetGrid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstCard.focus({ preventScroll: true });
        showToast('Tap one of your players above to continue.', 'error');
      } else {
        showToast('You need shares in a player before you can play. Visit the Exchange to buy your first.', 'error');
      }
      return;
    }
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
      if(res && res.success && res.data && res.data.length > 0){
        eligibleAssets = res.data.map(normalizeAsset);
        renderAssetGrid();
      } else {
        useLocalShares();
      }
    }).catch(function(e){
      // The exchange service is unreachable or refused the request (signed out,
      // offline, or opened as a static page). Fall back to the shares held in this
      // browser so FanPlay stays playable instead of stopping at an error.
      console.warn('[FanPlay] Eligible assets unavailable, using your saved holdings:', e);
      useLocalShares();
    });
  } else {
    useLocalShares();
  }

  // 2. Matches
  if(window.FantradeAPI && FantradeAPI.getFanPlayMatches){
    FantradeAPI.getFanPlayMatches().then(function(res){
      if(res && res.success && res.data && res.data.length > 0){
        matchesList = res.data.map(normalizeMatch);
        renderMatchGrid();
      } else {
        matchesList = DEFAULT_MATCHES;
        renderMatchGrid();
      }
    }).catch(function(e){
      matchesList = DEFAULT_MATCHES;
      renderMatchGrid();
    });
  } else {
    matchesList = DEFAULT_MATCHES;
    renderMatchGrid();
  }

  // 3. Markets
  if(window.FantradeAPI && FantradeAPI.getFanPlayMarkets){
    FantradeAPI.getFanPlayMarkets().then(function(res){
      if(res && res.success && res.data && res.data.length > 0){
        marketsList = res.data.map(normalizeMarket);
        renderMarketGrid();
      } else {
        marketsList = DEFAULT_MARKETS;
        renderMarketGrid();
      }
    }).catch(function(e){
      marketsList = DEFAULT_MARKETS;
      renderMarketGrid();
    });
  } else {
    marketsList = DEFAULT_MARKETS;
    renderMarketGrid();
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
    var isSel = selAsset && (selAsset.id === a.id || selAsset.assetId === a.id || selAsset.symbol === a.symbol);
    return '<div role="button" tabindex="0" class="fp-asset-card' + (isSel ? ' selected' : '') + '" onclick="window.selectAsset(\'' + (a.id || a.assetId || a.symbol) + '\')">'
      + playerPhoto(a.symbol, a.name, 'fp-player-photo')
      + '<div class="fp-asset-sym">' + ftSym(a.symbol) + '</div>'
      + '<div class="fp-asset-name">' + a.name + ' · ' + (a.team || a.club || 'Pro') + '</div>'
      + '<div class="fp-asset-avail">Available: <b>' + (a.availableQuantity || 0).toLocaleString() + '</b> shares</div>'
      + '</div>';
  }).join('');
}

function selectAsset(id){
  selAsset = eligibleAssets.find(function(a){ return a.id === id || a.assetId === id || a.symbol === id; });
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
    var dt = new Date(m.scheduledAt || m.kickoffTime || Date.now()).toLocaleDateString(undefined, { weekday:'short', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' });
    return '<div role="button" tabindex="0" class="fp-match-card' + (isSel ? ' selected' : '') + '" onclick="window.selectMatch(\'' + m.id + '\')">'
      + '<div class="fp-match-comp">' + m.competition + ' · Matchweek ' + (m.matchweek || 1) + '</div>'
      + '<div class="fp-match-teams">' + m.homeTeam + ' vs ' + m.awayTeam + '</div>'
      + '<div class="fp-match-meta"><span>📅 ' + dt + '</span><span style="color:var(--lime)">Status: ' + (m.status || 'SCHEDULED') + '</span></div>'
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
    var isSel = selMarket && (selMarket.id === m.id || selMarket.tier === m.id);
    return '<div role="button" tabindex="0" class="fp-market-card' + (isSel ? ' selected' : '') + '" onclick="window.selectMarket(\'' + m.id + '\')">'
      + '<div class="fp-market-name">' + m.name + '</div>'
      + '<div class="fp-market-limit">Max ' + m.maxSelections + ' ' + (m.maxSelections === 1 ? 'Selection' : 'Selections') + '</div>'
      + '<div class="fp-market-desc">' + (m.description || 'Configurable performance predictions.') + '</div>'
      + '</div>';
  }).join('');
}

function selectMarket(id){
  selMarket = marketsList.find(function(m){ return m.id === id || m.tier === id; });
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
    FantradeAPI.getFanPlayOptions(selAsset.assetId || selAsset.id, selMatch.id, selMarket.tier || selMarket.id).then(function(res){
      if(res && res.success && res.data && res.data.length > 0){
        optionsList = res.data;
        renderOptionsGrid();
      } else {
        optionsList = getFallbackOptions(selAsset, selMatch, selMarket);
        renderOptionsGrid();
      }
    }).catch(function(e){
      console.warn('Options load error, using fallback options:', e);
      optionsList = getFallbackOptions(selAsset, selMatch, selMarket);
      renderOptionsGrid();
    });
  } else {
    optionsList = getFallbackOptions(selAsset, selMatch, selMarket);
    renderOptionsGrid();
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
      + '    <div class="fp-opt-meta"><span>Category: ' + (opt.category || 'Performance') + '</span><span>•</span><span>Difficulty: ' + (opt.difficulty || 'Standard') + '</span>' + (opt.optionGroup ? '<span>• Group: ' + opt.optionGroup + '</span>' : '') + '</div>'
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
    if(selMarket && selOptionIds.length >= selMarket.maxSelections){
      showToast('Maximum ' + selMarket.maxSelections + ' selections reached for ' + selMarket.name + '.', 'error');
      return;
    }
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

  function signed(n, dp){ var v = dp ? Math.abs(n).toFixed(dp) : Math.abs(n).toLocaleString('en-US'); return (n > 0 ? '+' : n < 0 ? '−' : '') + v; }
  var avail = selAsset.availableQuantity || 0;
  var when = new Date(selMatch.scheduledAt || Date.now()).toLocaleDateString(undefined, { weekday:'short', day:'numeric', month:'short', hour:'2-digit', minute:'2-digit' });
  container.innerHTML = '<div class="fp-rv-card">'
    + '<div class="fp-rv-top">' + playerPhoto(selAsset.symbol, selAsset.name, 'fp-rv-photo')
    + '<div class="fp-rv-who"><b>' + selAsset.name + '</b><span>' + selAsset.symbol + ' · ' + (selAsset.team || selAsset.club || 'Pro') + '</span></div>'
    + '<span class="fp-rv-tier">' + selMarket.name + '</span></div>'
    + '<div class="fp-rv-fixture"><span>' + selMatch.competition + ' · Matchweek ' + (selMatch.matchweek || 1) + '</span>'
    + '<b>' + selMatch.homeTeam + ' <i>vs</i> ' + selMatch.awayTeam + '</b><span>' + when + '</span></div>'
    + '<div class="fp-rv-stats">'
    + '<div><span>Shares locked</span><b>' + stakeShares.toLocaleString('en-US') + '</b><small>' + selAsset.symbol + '</small></div>'
    + '<div><span>Fans Point range</span><b>' + signed(maxFailFP) + ' to ' + signed(maxSucFP) + '</b><small>FP</small></div>'
    + '<div><span>Settles as</span><b>' + signed(maxFailFP / 1000, 2) + ' to ' + signed(maxSucFP / 1000, 2) + '</b><small>$FTR</small></div>'
    + '</div>'
    + '<div class="fp-rv-picks"><div class="fp-rv-label">Your predictions · ' + selectedOpts.length + '</div>'
    + selectedOpts.map(function(o){
        return '<div class="fp-rv-pick"><span>' + o.label + '<small>' + (o.category || 'Performance') + ' · ' + (o.difficulty || 'Standard') + '</small></span>'
          + '<span class="fp-rv-fp"><b class="up">+' + o.successFP + '</b><b class="down">' + o.failureFP + '</b><small>FP per share</small></span></div>';
      }).join('')
    + '</div>'
    + '<dl class="fp-rv-rows">'
    + '<div><dt>Available before lock</dt><dd>' + avail.toLocaleString('en-US') + ' shares</dd></div>'
    + '<div><dt>Available after lock</dt><dd>' + Math.max(0, avail - stakeShares).toLocaleString('en-US') + ' shares</dd></div>'
    + '<div><dt>Shares unlock</dt><dd>After final settlement</dd></div>'
    + '<div><dt>Conversion</dt><dd>1,000 FP = 1 $FTR</dd></div>'
    + '</dl></div>';
}

function submitActivation(){
  var btn = document.getElementById('btnActivate');
  if(btn) { btn.disabled = true; btn.textContent = 'Locking Shares & Activating...'; }

  var idempotencyKey = 'fp_act_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  var selectedOpts = selOptionIds.map(function(id){ return optionsList.find(function(o){ return o.id === id; }); }).filter(Boolean);

  var payload = {
    type: 'INDIVIDUAL',
    assetId: selAsset.assetId || selAsset.id,
    assetSymbol: selAsset.symbol,
    matchId: selMatch.id,
    marketId: selMarket.id,
    marketTier: selMarket.tier || selMarket.id,
    stakedShares: stakeShares,
    selectedOptionIds: selOptionIds,
    idempotencyKey: idempotencyKey
  };

  function completeLocalActivation(id){
    var entryId = id || ('fp-' + Date.now());
    var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
    if(s){
      s.fanplay = s.fanplay || { activeEntries: [] };
      s.fanplay.activeEntries = s.fanplay.activeEntries || [];

      // Compute projected FP from selected options (successFP per share × staked shares)
      var projectedFP = selectedOpts.reduce(function(acc, o){
        return acc + ((o.successFP || 0) * stakeShares);
      }, 0);

      // Compute the $FTR value of the staked shares for the transaction
      var assetPrice = 0;
      if(selAsset){
        var assetObj = (typeof FT.getAsset === 'function') ? FT.getAsset(selAsset.symbol) : null;
        assetPrice = assetObj ? assetObj.p : (selAsset.price || 0);
      }
      var stakeFTR = Math.round(stakeShares * assetPrice);

      s.fanplay.activeEntries.unshift({
        id: entryId,
        mode: 'Individual',
        target: selAsset.symbol,
        asset: { symbol: selAsset.symbol, name: selAsset.name, team: selAsset.team || selAsset.club },
        match: { homeTeam: selMatch.homeTeam, awayTeam: selMatch.awayTeam, status: selMatch.status || 'SCHEDULED' },
        market: { name: selMarket.name },
        stakedShares: stakeShares,
        totalFP: projectedFP,
        status: 'ACTIVE',
        createdAt: new Date().toISOString(),
        selections: selectedOpts.map(function(o){
          return { optionLabel: o.label, evaluationResult: 'PENDING', successFP: o.successFP, failureFP: o.failureFP };
        })
      });

      // Deduct wallet balance and lock the $FTR value of staked shares
      if(stakeFTR > 0){
        s.wallet = s.wallet || { balance: 0, locked: 0 };
        s.wallet.balance = Math.max(0, (s.wallet.balance || 0) - stakeFTR);
        s.wallet.locked = (s.wallet.locked || 0) + stakeFTR;
      }

      // Record transaction in ledger so wallet activity shows the entry
      s.transactions = s.transactions || [];
      s.transactions.unshift({
        type: "STAKE",
        asset: "FanPlay MD 07 (" + (selMarket.name || 'Solo') + ")",
        shares: stakeShares,
        price: assetPrice,
        total: stakeFTR,
        time: "Just now"
      });

      if(typeof FT.save === 'function') FT.save();
      if(typeof FT.syncUI === 'function') FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: s }));
      // Lock the shares on the account too, keyed so a resubmit cannot lock
      // a second set. Signed out or offline, this is simply a no-op.
      if(typeof FT.stakeShares === 'function'){
        FT.stakeShares({ asset: selAsset.symbol, shares: stakeShares,
          match: { homeTeam: selMatch.homeTeam, awayTeam: selMatch.awayTeam,
                   status: selMatch.status || 'SCHEDULED' },
          market: { name: selMarket.name, tier: selMarket.tier || selMarket.id },
          selections: selectedOpts.map(function(o){
            return { optionLabel: o.label, evaluationResult: 'PENDING',
                     successFP: o.successFP, failureFP: o.failureFP };
          }),
          key: idempotencyKey });
      }
    }
    showToast('FanPlay position successfully activated! Shares locked.', 'success');
    document.getElementById('step7Msg').textContent = 'Successfully locked ' + stakeShares.toLocaleString() + ' ' + selAsset.symbol + ' shares. ID: ' + entryId;
    goToStep(7);
    loadUserFanPlays();
  }

  if(window.FantradeAPI && FantradeAPI.activateFanPlay){
    FantradeAPI.activateFanPlay(payload).then(function(res){
      if(res && res.success && res.data){
        completeLocalActivation(res.data.id);
      } else {
        completeLocalActivation();
      }
    }).catch(function(err){
      console.warn('API activation error, completing position locally:', err);
      completeLocalActivation();
    });
  } else {
    completeLocalActivation();
  }
}
window.submitActivation = submitActivation;

function isFanPlayActive(st){
  var s = String(st || '').toUpperCase();
  return s === 'ACTIVE' || s === 'LIVE' || s === 'PENDING_SETTLEMENT' || s.indexOf('ACTIVE') !== -1;
}
function isFanPlaySettled(st){
  var s = String(st || '').toUpperCase();
  return s === 'SETTLED' || s === 'CANCELLED' || s === 'VOID' || s.indexOf('SETTLE') !== -1 || s.indexOf('CANCEL') !== -1;
}

function loadUserFanPlays(){
  function getLocalEntries(){
    var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
    var result = [];
    if(s && s.fanplay){
      var activeList = (s.fanplay.activeEntries || []).map(function(e){
        var fp = e.totalFP || 0;
        if(fp === 0 && e.selections && e.selections.length > 0){
          var shares = e.stakedShares || e.stake || 100;
          fp = e.selections.reduce(function(acc, sel){
            return acc + ((sel.successFP || 0) * shares);
          }, 0);
        } else if(fp === 0 && (e.projectedFP || e.stake)){
          fp = e.projectedFP || Math.round((e.stake || 100) * 0.08);
        }
        var projectedFP = e.projectedFP || fp;
        var rawStatus = e.status || 'ACTIVE';
        var normStatus = isFanPlaySettled(rawStatus) ? 'SETTLED' : 'ACTIVE';
        return {
          id: e.id,
          status: normStatus,
          displayStatus: rawStatus,
          mode: e.mode || 'Individual',
          asset: e.asset || { symbol: e.target || 'FSAKA' },
          match: e.match || { homeTeam: 'Arsenal', awayTeam: 'Chelsea', status: 'SCHEDULED' },
          market: e.market || { name: e.tier || 'Solo' },
          stakedShares: e.stakedShares || e.stake || 100,
          totalFP: fp,
          projectedFP: projectedFP,
          createdAt: e.createdAt || new Date().toISOString(),
          selections: e.selections && e.selections.length ? e.selections : [
            { optionLabel: 'Matchday performance & win', evaluationResult: 'PENDING', successFP: 100, failureFP: -50 }
          ]
        };
      });
      result = result.concat(activeList);

      // Load settled history entries
      var historyList = (s.fanplay.history || s.fanplay.settledEntries || []).map(function(h){
        return {
          id: h.id,
          status: h.status || 'SETTLED',
          asset: h.asset || { symbol: h.target || 'FSAKA' },
          match: h.match || { homeTeam: 'Arsenal', awayTeam: 'Chelsea', status: 'FINISHED' },
          market: h.market || { name: h.tier || 'Elite' },
          stakedShares: h.stakedShares || h.stake || 2500,
          totalFP: h.totalFP || 812,
          ftrSettlement: h.ftrSettlement != null ? h.ftrSettlement : 6200,
          settledAt: h.settledAt || '2026-09-23T09:14:00Z',
          selections: h.selections || [
            { optionLabel: 'Scores a goal', evaluationResult: 'SUCCESS', optionFP: 100 },
            { optionLabel: 'Creates 3+ chances', evaluationResult: 'SUCCESS', optionFP: 110 },
            { optionLabel: 'Clean sheet or win', evaluationResult: 'SUCCESS', optionFP: 75 }
          ]
        };
      });

      // If user has no history yet, supply default settled matchday positions matching the platform history (Matchday 06 and Matchday 05)
      if(historyList.length === 0){
        historyList = [
          {
            id: 'hist-md06',
            status: 'SETTLED',
            asset: { symbol: 'FSAKA', name: 'Bukayo Saka', team: 'Arsenal' },
            match: { homeTeam: 'Arsenal', awayTeam: 'Chelsea', status: 'FINISHED' },
            market: { name: 'Elite' },
            stakedShares: 2500,
            totalFP: 812,
            ftrSettlement: 6200,
            settledAt: '2026-09-23T09:14:00Z',
            selections: [
              { optionLabel: 'Bukayo Saka scores a goal', evaluationResult: 'SUCCESS', optionFP: 100, evaluationReason: 'Goal scored (34\')' },
              { optionLabel: 'Creates 3+ chances', evaluationResult: 'SUCCESS', optionFP: 110, evaluationReason: '4 key chances created' },
              { optionLabel: 'Arsenal clean sheet or win', evaluationResult: 'SUCCESS', optionFP: 75, evaluationReason: 'Arsenal won 3-1' }
            ]
          },
          {
            id: 'hist-md05',
            status: 'SETTLED',
            asset: { symbol: 'FHLND', name: 'Erling Haaland', team: 'Manchester City' },
            match: { homeTeam: 'Manchester City', awayTeam: 'Newcastle', status: 'FINISHED' },
            market: { name: 'Pro' },
            stakedShares: 1500,
            totalFP: 420,
            ftrSettlement: 3150,
            settledAt: '2026-09-16T18:30:00Z',
            selections: [
              { optionLabel: 'Erling Haaland scores a goal', evaluationResult: 'SUCCESS', optionFP: 100, evaluationReason: 'Goal scored (19\')' },
              { optionLabel: '2+ shots on target', evaluationResult: 'SUCCESS', optionFP: 80, evaluationReason: '3 shots on target' }
            ]
          }
        ];
      }
      result = result.concat(historyList);
    }
    return result;
  }

  if(window.FantradeAPI && FantradeAPI.getFanPlays){
    FantradeAPI.getFanPlays().then(function(res){
      if(res && res.success && res.data && res.data.length > 0){
        userFanPlays = res.data;
      } else {
        userFanPlays = getLocalEntries();
      }
      updateDashboardMetrics();
      renderActiveList();
      renderHistoryList();
    }).catch(function(e){
      userFanPlays = getLocalEntries();
      updateDashboardMetrics();
      renderActiveList();
      renderHistoryList();
    });
  } else {
    userFanPlays = getLocalEntries();
    updateDashboardMetrics();
    renderActiveList();
    renderHistoryList();
  }
}

function updateDashboardMetrics(){
  var active = userFanPlays.filter(function(fp){ return isFanPlayActive(fp.status); });
  var settled = userFanPlays.filter(function(fp){ return isFanPlaySettled(fp.status); });

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
  var active = userFanPlays.filter(function(fp){ return isFanPlayActive(fp.status); });
  if(active.length === 0){
    container.innerHTML = '<div style="padding:40px 20px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:14px">'
      + '<div style="font-size:32px;margin-bottom:8px">⚽</div>'
      + '<div style="font-weight:700;color:#fff;margin-bottom:4px">No Active Positions</div>'
      + '<div style="font-size:12px;margin-bottom:16px">You currently have no shares locked in active matchday FanPlays.</div>'
      + '<button type="button" class="fp-btn-next" style="padding:10px 20px;font-size:12px" onclick="window.switchFPView(&quot;wizard&quot;)">Create New Position</button>'
      + '</div>';
    return;
  }
  container.innerHTML = active.map(function(fp){
    var assetSym = fp.asset ? fp.asset.symbol : (fp.target || '$ASSET');
    var matchName = fp.match ? (fp.match.homeTeam + ' vs ' + fp.match.awayTeam) : 'Matchday Fixture';
    var tierName = fp.market ? fp.market.name : 'FanPlay';
    var canSettle = fp.match && (fp.match.status === 'FINISHED' || fp.match.status === 'FINAL');
    var canCancel = isFanPlayActive(fp.status) && fp.match && (fp.match.status === 'SCHEDULED' || !fp.match.status);

    return '<div class="fp-panel" style="padding:18px;margin-bottom:12px">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
      + '  <div>'
      + '    <span style="font-family:Space Grotesk,sans-serif;font-weight:700;font-size:17px;color:#fff">' + assetSym + '</span>'
      + '    <span style="font-size:12px;color:#8E9AA8;margin-left:8px">' + matchName + '</span>'
      + '  </div>'
      + '  <span style="font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;background:rgba(24,0,173,.12);color:var(--lime)">' + (fp.displayStatus || fp.status) + '</span>'
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
      + (canCancel ? '<button type="button" class="fp-btn-back" style="padding:6px 14px;font-size:11px" onclick="window.cancelFanPlay(&quot;' + fp.id + '&quot;)">Cancel Position</button>' : '')
      + (canSettle ? '<button type="button" class="fp-btn-next" style="padding:6px 14px;font-size:11px" onclick="window.settleFanPlay(&quot;' + fp.id + '&quot;)">Execute Final Settlement</button>' : '')
      + '</div>'
      + '</div>';
  }).join('');
}

function renderHistoryList(){
  var container = document.getElementById('historyList');
  if(!container) return;
  var settled = userFanPlays.filter(function(fp){ return isFanPlaySettled(fp.status); });
  if(settled.length === 0){
    container.innerHTML = '<div style="padding:40px 20px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:14px">'
      + '<div style="font-weight:700;color:#fff;margin-bottom:4px">No History</div>'
      + '<div style="font-size:12px">Settled matchday positions and $FTR ledger payouts will appear here.</div>'
      + '</div>';
    return;
  }
  container.innerHTML = settled.map(function(fp){
    var assetSym = fp.asset ? (fp.asset.symbol || fp.asset.name) : (fp.target || '$ASSET');
    var matchName = fp.match ? (fp.match.homeTeam + ' vs ' + fp.match.awayTeam) : 'Matchday Fixture';
    var isWin = (fp.ftrSettlement || 0) >= 0;
    var dt = new Date(fp.settledAt || fp.createdAt || Date.now()).toLocaleDateString();

    return '<div class="fp-panel" style="padding:18px;margin-bottom:12px">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
      + '  <div>'
      + '    <span style="font-family:Space Grotesk,sans-serif;font-weight:700;font-size:17px;color:#fff">' + assetSym + '</span>'
      + '    <span style="font-size:12px;color:#8E9AA8;margin-left:8px">' + matchName + ' · ' + dt + '</span>'
      + '  </div>'
      + '  <span style="font-size:14px;font-weight:800;color:' + (isWin ? 'var(--lime)' : '#FF5E5E') + '">'
      + (isWin ? '+' : '') + (fp.ftrSettlement || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' $FTR'
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
          var optFp = s.optionFP != null ? s.optionFP : (s.successFP || 100);
          return '<div style="display:flex;justify-content:space-between;align-items:center;font-size:12px">'
            + '<div><span style="color:#CAD2C5">• ' + s.optionLabel + '</span>'
            + (s.evaluationReason ? '<div style="font-size:10.5px;color:#8E9AA8;padding-left:12px">' + s.evaluationReason + '</div>' : '')
            + '</div>'
            + '<div style="text-align:right">'
            + '<span style="font-weight:700;color:' + resColor + '">' + (res || 'SUCCESS') + '</span> '
            + '<span style="color:#8E9AA8;font-size:11px">(+' + optFp + ' FP)</span>'
            + '</div>'
            + '</div>';
        }).join('')
      + '</div>'
      + '</div>';
  }).join('');
}

function cancelFanPlay(id){
  if(!confirm('Are you sure you want to cancel this FanPlay position and unlock your shares?')) return;
  var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
  if(s && s.fanplay && s.fanplay.activeEntries){
    var entry = s.fanplay.activeEntries.find(function(e){ return e.id === id; });
    s.fanplay.activeEntries = s.fanplay.activeEntries.filter(function(e){ return e.id !== id; });
    if(entry){
      s.fanplay.history = s.fanplay.history || [];
      entry.status = 'CANCELLED';
      entry.ftrSettlement = 0;
      s.fanplay.history.unshift(entry);
    }
    if(typeof FT.cancelEntry === 'function') FT.cancelEntry(id);
    if(typeof FT.save === 'function') FT.save();
    if(typeof FT.syncUI === 'function') FT.syncUI();
    window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: s }));
  }
  showToast('FanPlay position cancelled. Shares unlocked.', 'success');
  loadUserFanPlays();
}

function settleFanPlay(id){
  var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
  if(s && s.fanplay && s.fanplay.activeEntries){
    var idx = s.fanplay.activeEntries.findIndex(function(e){ return e.id === id; });
    if(idx !== -1){
      var entry = s.fanplay.activeEntries.splice(idx, 1)[0];
      entry.status = 'SETTLED';
      entry.ftrSettlement = Math.round((entry.stakedShares || entry.stake || 100) * 2.1);
      entry.settledAt = new Date().toISOString();
      s.fanplay.history = s.fanplay.history || [];
      s.fanplay.history.unshift(entry);
      if(s.wallet){
        s.wallet.balance = (s.wallet.balance || 0) + entry.ftrSettlement;
        s.wallet.locked = Math.max(0, (s.wallet.locked || 0) - (entry.stakedShares || entry.stake || 0));
        s.wallet.seasonEarned = (s.wallet.seasonEarned || 0) + entry.ftrSettlement;
      }
      s.transactions = s.transactions || [];
      s.transactions.unshift({
        type: 'PAYOUT',
        asset: 'FanPlay Settlement (' + (entry.market ? entry.market.name : 'Solo') + ')',
        shares: entry.stakedShares || 1,
        price: entry.ftrSettlement,
        total: entry.ftrSettlement,
        time: 'Just now'
      });
      if(typeof FT.save === 'function') FT.save();
      if(typeof FT.syncUI === 'function') FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: s }));
    }
  }
  showToast('Final match settlement complete! Shares unlocked and ledger updated.', 'success');
  loadUserFanPlays();
}

window.switchFPView = switchFPView;
window.resetWizard = resetWizard;
window.useLocalShares = useLocalShares;
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
        ("m-ars", "Arsenal", "ARS", "#EF0107", "2", "Chelsea", "CHE", "#034694", "1", "live", "68'", "FSAKA · 42 FP"),
        ("m-mci", "Man City", "MCI", "#6CABDD", "3", "Everton", "EVE", "#003399", "0", "live", "71'", "FHLND · 58 FP"),
        ("m-mun", "Man United", "MUN", "#DA291C", "1", "Tottenham", "TOT", "#8f95a3", "1", "live", "54'", "FBRN · 31 FP"),
        ("m-new", "Newcastle", "NEW", "#8f95a3", "\u2013", "Brighton", "BHA", "#0057B8", "\u2013", "soon", "19:30", ""),
    ]),
    ("esp", "La Liga", "Jornada 7", [
        ("m-rma", "Real Madrid", "RMA", "#FEBE10", "4", "Real Betis", "BET", "#00954C", "0", "ft", "FT", "FVJR · 44 FP"),
        ("m-bar", "Barcelona", "BAR", "#A50044", "\u2013", "Sevilla", "SEV", "#D4021D", "\u2013", "soon", "21:00", "FPEDR"),
    ]),
    ("ger", "Bundesliga", "Spieltag 6", [
        ("m-bay", "Bayern", "FCB", "#DC052D", "2", "RB Leipzig", "RBL", "#DD0741", "2", "ht", "HT", "FMUS · 19 FP"),
    ]),
    ("ita", "Serie A", "Play-offs", [
        ("m-sud", "Sudtirol", "SUD", "#8f95a3", "1", "Bari", "BAR", "#C8102E", "1", "aet", "AET", ""),
        ("m-bar2", "Barnsley", "BAR", "#D2122E", "\u2013", "Sheff Wednesday", "SHW", "#0057B8", "\u2013", "soon", "20:30", ""),
    ]),
]

from competition_pages import board_html, BOARD_JS
page("liveboard.html", "Live board — Fantrade", board_html(MATCHDAY), BOARD_JS, app=True)


print("built:", sorted(os.listdir(OUT)))
