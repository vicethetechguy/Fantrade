# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
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
    html = (head(title, css, "app" if app else "") + atmosphere() + nav(fname, app) +
            body + footer() + "<script src=\"public/fantrade-api.js\"></script><script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)


# ══════════════════════════════════════════════════════════
# 1. LANDING
# ══════════════════════════════════════════════════════════
LAND_CSS = """
.hero{padding:214px 0 0;text-align:center}
.hero h1{font-size:clamp(44px,9vw,116px);font-variation-settings:'wdth' 125,'wght' 900;margin-top:30px}
.hero h1 .lt{font-variation-settings:'wdth' 125,'wght' 200;color:#C3C9BE}
.hero .lede{margin:30px auto 40px;text-align:center}
.hero-cta{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.trust{display:flex;gap:10px;justify-content:center;margin-top:44px;flex-wrap:wrap}
.trust div{border:1px solid var(--hair);border-radius:999px;padding:10px 20px;background:rgba(255,255,255,.025);
  font-size:12px;color:var(--dim);box-shadow:var(--inset);display:flex;align-items:center;gap:10px}
.trust b{font-family:'JetBrains Mono',monospace;font-weight:400;color:var(--ink)}
.trust .ic{width:14px;height:14px;color:var(--lime)}
.console{margin-top:84px}
.console-bar{display:flex;align-items:center;gap:12px;padding:14px 20px;border-bottom:1px solid var(--hair);background:rgba(255,255,255,.02)}
.console-bar .tag{font-weight:600;font-size:10px;color:var(--faint);letter-spacing:.14em;text-transform:uppercase}
.console-bar .live{margin-left:auto;display:flex;align-items:center;gap:8px;font-weight:600;font-size:9.5px;color:var(--lime);letter-spacing:.16em}
.pulse{width:6px;height:6px;border-radius:50%;background:var(--lime);box-shadow:0 0 12px var(--lime);animation:pulse 2.4s var(--ease) infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.3;transform:scale(.8)}}
.console-body{display:grid;grid-template-columns:1.25fr 1fr;text-align:left}
.book{border-right:1px solid var(--hair)}
.bhead,.brow{display:grid;grid-template-columns:1.6fr 1fr .85fr 1fr;gap:12px;padding:13px 22px;align-items:center}
.bhead{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);border-bottom:1px solid var(--hair);text-transform:uppercase}
.brow{border-bottom:1px solid rgba(255,255,255,.045);transition:background .6s var(--ease)}
.brow:hover{background:rgba(255,255,255,.025)}
.panel{padding:24px 26px}
.panel-h{display:flex;align-items:center;gap:13px;margin-bottom:20px}
.panel-h .nm{font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 800;text-transform:uppercase;font-size:16px}
.panel-h .sub{font-weight:600;font-size:9.5px;color:var(--faint);letter-spacing:.14em;text-transform:uppercase}
.panel .btn{width:100%;justify-content:space-between;margin-top:20px}
.band{margin-top:130px;border-top:1px solid var(--hair);border-bottom:1px solid var(--hair);
  background:rgba(255,255,255,.018);padding:15px 0;overflow:hidden;white-space:nowrap}
.band-track{display:inline-flex;gap:44px;animation:slide 46s linear infinite;
  font-family:'JetBrains Mono',monospace;font-size:11.5px;color:var(--faint)}
.band-track b{color:var(--ink);font-weight:400}
@keyframes slide{to{transform:translateX(-50%)}}
.layer-n{font-weight:600;font-size:9.5px;letter-spacing:.2em;color:var(--faint);text-transform:uppercase}
.layer h3{font-size:34px;margin:18px 0 14px}
.layer p{color:var(--dim);font-size:14.5px;font-weight:300;margin:0;max-width:44ch}
.layer ul{list-style:none;padding:0;margin:24px 0 0;font-size:13px;color:var(--dim)}
.layer li{padding:11px 0;border-top:1px solid rgba(255,255,255,.055);display:flex;gap:12px;align-items:center}
.layer li .ic{width:15px;height:15px;color:var(--lime);opacity:.85}
.layer.amber h3{color:var(--amber)}
.layer.amber li .ic{color:var(--amber)}
.layer.lime h3{color:var(--lime)}
.layer .ibox{margin-bottom:22px}
.step .i{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--lime);text-transform:uppercase}
.step h4{font-size:20px;margin:14px 0 10px}
.step p{font-size:12.5px;font-weight:300;color:var(--dim);margin:0;line-height:1.6}
.step.end .i,.step.end h4{color:var(--amber)}
.cta-sec{padding:160px 0 140px;text-align:center}
.cta-sec h2{font-size:clamp(38px,8vw,96px);font-variation-settings:'wdth' 125,'wght' 900}
.cta-sec .lede{margin:28px auto 40px;text-align:center}
@media (max-width:1024px){.console-body{grid-template-columns:1fr}.book{border-right:0;border-bottom:1px solid var(--hair)}}
@media (max-width:768px){.hero{padding:128px 0 0}.hero h1{font-size:clamp(34px,10.5vw,56px)}
  .band{margin-top:88px}.console{margin-top:52px}.hero-cta{flex-direction:column;align-items:stretch}
  .hero-cta .btn{justify-content:space-between}.trust div{width:100%}
  .bhead,.brow{grid-template-columns:1.5fr 1fr .8fr;padding:12px 16px}
  .bhead span:last-child,.brow>div:last-child{display:none}
  .console-bar .tag{display:none}.cta-sec{padding:104px 0 92px}}
"""


def layer(n, title, body, items, cls="", icon="wallet"):
    lis = "".join('<li>%s%s</li>' % (ic("check", "ic"), t) for t in items)
    return (T('<div class="core pad layer @@"><span class="ibox @@">@@</span>'
            '<div class="layer-n">@@</div><h3>@@</h3><p>@@</p><ul>@@</ul></div>', cls, "am" if cls == "amber" else "", ic(icon, "ic-lg"), n, title, body, lis))


land = []
land.append('<header class="hero" id="top"><div class="wrap">')
land.append(T('<span class="pill" data-reveal>@@ A football ownership economy</span>', ic("ball", "ic")))
land.append('<h1 data-reveal>Own the game.<br><span class="lt">Build your club.</span><br>Play to earn.</h1>')
land.append('<p class="lede" data-reveal>Buy shares in the players and coaches you believe in. Assemble them into a '
            'club that is yours. Then put your football knowledge to work every matchday.</p>')
land.append('<div class="hero-cta" data-reveal>' + btn("Start trading", href="exchange.html") +
            btn("See a Dream Club", "btn-glass", "clubs.html") + '</div>')
land.append(T('<div class="trust" data-reveal><div>@@ <b>10,000,000</b> shares per asset</div>'
            '<div>@@ <b>2,140</b> players &amp; coaches</div><div>@@ Settled in <b>$FTR</b></div></div>', ic("supply", "ic"), ic("user", "ic"), ic("coin", "ic")))
land.append('</div><div class="wrap"><div class="bezel console" id="exchange" data-reveal><div class="core">')
land.append(T('<div class="console-bar">@@<span class="tag">Exchange · Matchday 07</span>'
            '<span class="live"><span class="pulse"></span>Market open</span></div>', ic("candle", "ic")))
land.append('<div class="console-body"><div class="book">'
            '<div class="bhead"><span>Asset</span><span>Price $FTR</span><span>24h</span><span>7d</span></div>'
            '<div id="book"></div></div>')
land.append(T('<div class="panel"><div class="panel-h"><span class="badge">@@</span>'
            '<div><div class="nm">$Saka</div><div class="sub">Bukayo Saka · Winger</div></div></div>'
            '<div class="line"><span>Total supply</span><b>10,000,000</b></div>'
            '<div class="line"><span>Held by fans</span><b>3,712,480</b></div>'
            '<div class="supply"><i style="width:37%"></i></div>'
            '<div class="k-label" style="margin:8px 0 16px">37.1% of supply in circulation</div>'
            '<div class="line"><span>Your holding</span><b>10,000 shares</b></div>'
            '<div class="line"><span>FanPlay eligible</span><b class="up">Yes</b></div>'
            '<div class="line"><span>In your club</span><b>ZERO FC · RW</b></div>@@</div>', ic("boot", "ic"), btn("Buy shares", href="exchange.html")))
land.append('</div></div></div></div></header>')
land.append('<div class="band" aria-hidden="true"><div class="band-track" id="band"></div></div><main>')

# layers
land.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
            '<span class="pill">@@ Three layers, one economy</span>'
            '<h2>Every asset you own<br>does three jobs</h2>'
            '<p class="lede">Most fantasy games end when the whistle goes. On Fantrade the same share is an investment, '
            'a squad member and a scoring position at once.</p></div>', ic("layers", "ic")))
land.append('<div class="bento"><div class="bezel c5" data-reveal>' +
            layer("Layer 01", "Own", "Buy fractional shares in players and coaches. Every asset is split into ten "
                  "million shares, so you can start with one or build a real position.",
                  ["Player shares — $Bruno, $Saka, $Jackson", "Coach shares — $Arteta, $Pep, $Maresca",
                   "Buy, sell, hold or swap at any time", "Swap fees settled in $FTR"], icon="wallet") +
            '</div><div class="bento c7" style="align-content:start">'
            '<div class="bezel c12" data-reveal>' +
            layer("Layer 02", "Build", "Turn your holdings into a club with a name, a badge, a stadium and a shape. "
                  "Your squad is your portfolio, arranged the way you see football.",
                  ["Pick a coach, a formation and a captain", "Eleven starters plus a working bench"],
                  cls="amber", icon="crest") +
            '</div><div class="bezel c12" data-reveal>' +
            layer("Layer 03", "Play", "Enter FanPlay with a single player or your whole club. Real match data settles "
                  "the round into Fans Point, then $FTR.",
                  ["Six market tiers, Simple to Viynx Max", "Club mode earns a configurable boost"],
                  cls="lime", icon="bolt") +
            '</div></div></div></div></section>')

# club teaser
land.append(T('<section id="clubs"><div class="wrap"><div class="sec-head" data-reveal>'
            '<span class="pill">@@ Dream Clubs</span><h2>A squad you<br>actually own</h2>'
            '<p class="lede">No loans, no drafting players out of thin air. A name only enters your teamsheet once the '
            'shares are in your wallet — which is exactly what makes the club worth something.</p></div>', ic("crest", "ic")))
land.append(T('<div class="bento"><div class="bezel c7" data-reveal><div class="core pitch" id="pitchMount"></div></div>'
            '<div class="c5" style="display:flex;flex-direction:column;gap:16px">'
            '<div class="bezel" data-reveal><div class="core pad"><div class="k-label">Club value</div>'
            '<div class="value-big">245,800 <small>$FTR</small></div>'
            '<div class="delta">▲ 12,400 this week · ▲ 145.8% since founding</div>'
            '<div style="margin-top:24px;border-top:1px solid var(--hair);padding-top:6px">'
            '<div class="b-row"><span>Starting XI</span><b>180,600</b></div>'
            '<div class="b-row"><span>Bench (4)</span><b>45,200</b></div>'
            '<div class="b-row"><span>Coach</span><b>20,000</b></div>'
            '<div class="b-row total"><span>Club value</span><b>245,800</b></div></div></div></div>'
            '<div class="mini-grid" data-reveal>'
            '<div class="mini"><div class="k">Club rank</div><div class="v">#124</div></div>'
            '<div class="mini"><div class="k">Club FP</div><div class="v lime">8,420</div></div>'
            '<div class="mini"><div class="k">Club boost</div><div class="v amber">+15%</div></div>'
            '<div class="mini"><div class="k">Win rate</div><div class="v">62%</div></div></div>'
            '<div class="bezel" data-reveal style="flex:1"><div class="core pad-sm">'
            '<div class="k-label">Chemistry · why Zero FC boosts +15%</div>'
            '<div class="b-row"><span>Base club mode</span><b>+10.0%</b></div>'
            '<div class="b-row"><span>Coach fits 4-3-3</span><b>+3.0%</b></div>'
            '<div class="b-row"><span>XI in natural positions</span><b>+2.0%</b></div>'
            '<div class="b-row"><span>Squad completeness</span><span>bench 4/5</span></div>'
            '<div style="margin-top:18px">@@</div></div></div></div></div></div></section>', btn("Open the club builder", "btn-glass btn-sm", "clubs.html")))

# loop
steps = [("01 / Buy", "Take a position", "Deposit, convert to $FTR and buy into the players and coaches you rate.", "c4", ""),
         ("02 / Own", "Hold the shares", "Ownership is the key that unlocks every other part of the platform.", "c3", ""),
         ("03 / Build", "Assemble the club", "Name it, badge it, pick a coach and a shape, fill the XI and the bench.", "c5", ""),
         ("04 / Play", "Enter a round", "Solo or club, choose your market tier, verify ownership and activate.", "c5", ""),
         ("05 / Earn", "Settle in $FTR", "Real match data converts performance into Fans Point.", "c3", ""),
         ("06 / Reinvest", "Grow the portfolio", "Buy the next player. Club value rises with the squad underneath it.", "c4", "end")]
land.append(T('<section id="loop"><div class="wrap"><div class="sec-head center" data-reveal>'
            '<span class="pill">@@ The Fantrade loop</span><h2>Buy, own, build,<br>play, earn, reinvest</h2></div>'
            '<div class="bento">', ic("swap", "ic")))
for i, t, d, c, e in steps:
    land.append(T('<div class="bezel tight @@" data-reveal><div class="core pad-sm step @@">'
                '<div class="i">@@</div><h4>@@</h4><p>@@</p></div></div>', c, e, i, t, d))
land.append('</div></div></section>')

# rules
rules = [("supply", "Ten million shares, fixed", "Every player and every coach is issued the same fixed supply. Price moves on demand, never on a quiet reprint.", "c6", ""),
         ("lock", "No borrowing, ever", "If a player isn't in your wallet he isn't on your teamsheet. Every lineup is validated before a round opens.", "c6", ""),
         ("whistle", "Coaches are real assets", "$Arteta trades like a player and works like a manager — his shares move on results and set your club modifier.", "c4", "am"),
         ("subs", "Substitutes that matter", "A starter who gets no minutes is replaced by an eligible sub under the rules you set. Depth is strategy.", "c4", ""),
         ("clock", "A deterministic window", "Rounds open and close on a published matchday clock, so everyone is scored on the same fixtures and the same data.", "c4", "")]
land.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
            '<span class="pill amber">@@ Rules of the house</span><h2>How Fantrade<br>keeps it honest</h2></div>'
            '<div class="bento halves">', ic("shield", "ic")))
for icon, t, d, c, am in rules:
    land.append(T('<div class="bezel tight @@" data-reveal><div class="core pad f">'
                '<span class="ibox @@">@@</span><h4>@@</h4><p>@@</p></div></div>', c, am, ic(icon, "ic-lg"), t, d))
land.append('</div></div></section>')

land.append('<section class="cta-sec"><div class="wrap"><h2 data-reveal>Your club is<br>waiting to<br>be built</h2>'
            '<p class="lede" data-reveal>Start with one share in one player. The rest of the squad is a decision you '
            'get to make every single week.</p><div class="hero-cta" data-reveal>' +
            btn("Create account") + btn("Browse the exchange", "btn-glass", "exchange.html") +
            '</div></div></section></main>')

PITCH_JS = r"""
var XI=[[['ST','$Haaland']],[['LW','$Vinicius'],['CAM','$Bruno',1],['RW','$Saka']],
        [['CM','$Rice'],['CM','$Odegaard']],
        [['LB','$Davies'],['CB','$VanDijk'],['CB','$Saliba'],['RB','$White']],[['GK','$Raya']]];
var BENCH=[['GK','$Alisson'],['DEF','$Gabriel'],['MID','$Pedri'],['MID','$Musiala']];
var ARM="<svg class='ic' aria-hidden='true'><use href='#i-armband'/></svg>";
function pitchHTML(){
  var h="<div class='pitch-head'><span class='crest'>ZFC</span><div><div class='name'>Zero FC</div>"+
    "<div class='meta'>4-3-3 · Emirates of the North · Est. 2026</div></div>"+
    "<div class='coach'><span class='badge coach'><svg class='ic' aria-hidden='true'><use href='#i-whistle'/></svg></span>"+
    "<div><b>$Arteta</b><span>Coach · owned</span></div></div></div>";
  XI.forEach(function(row){
    h+="<div class='line-row'>";
    row.forEach(function(p){
      h+="<div class='chip"+(p[2]?" cap":"")+"'><div class='pos'>"+p[0]+"</div><div class='nm'>"+p[1]+"</div>"+
         (p[2]?"<div class='arm'>"+ARM+"Captain ×1.5</div>":"")+"</div>";
    });
    h+="</div>";
  });
  h+="<div class='bench'><div class='k-label'>Bench · auto-subs if a starter doesn't play</div><div class='bench-row'>";
  BENCH.forEach(function(p){ h+="<div class='chip sm'><div class='pos'>"+p[0]+"</div><div class='nm'>"+p[1]+"</div></div>"; });
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
    (a.d>=0?'#C4F82A':'#FF5E5E')+"'>"+(a.d>=0?'+':'')+a.d.toFixed(1)+"%</em></span>"; }).join('');
  band.innerHTML=s+s;
}
"""
page("index.html", "Home — Fantrade", "".join(land), PITCH_JS, LAND_CSS)


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
.kc-banner{display:flex;align-items:center;justify-content:space-between;gap:14px;background:rgba(196,248,42,.06);border:1px solid rgba(196,248,42,.22);border-radius:10px;padding:10px 14px;margin-bottom:14px}
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
.kc-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);display:grid;place-items:center;flex:none;color:var(--lime);font-family:Archivo,sans-serif;font-size:11px;font-weight:800}
.kc-avatar.coach{color:var(--amber);border-color:rgba(255,106,31,.25);background:rgba(255,106,31,.08)}
.kc-pair-title{display:flex;align-items:center;gap:5px;font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:14.5px;line-height:1.1;color:var(--ink)}
.kc-pair-quote{font-size:11.5px;color:#767c82;font-weight:600}
.kc-tag{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;color:#767c82;background:rgba(255,255,255,.08);border-radius:4px;padding:1px 4px;margin-left:2px}
.kc-pair-sub{font-size:11.5px;color:#767c82;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kc-row-mid{text-align:right;padding-right:12px}
.kc-price-main{font-family:'JetBrains Mono',monospace;font-size:14.5px;font-weight:600;color:var(--ink);letter-spacing:-.01em}
.kc-price-sub{font-family:'JetBrains Mono',monospace;font-size:11px;color:#767c82;margin-top:2px}
.kc-row-right{display:flex;justify-content:flex-end}
.kc-pill{display:inline-flex;align-items:center;justify-content:center;min-width:76px;height:32px;border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:12.5px;font-weight:700;color:#0A0D03;background:var(--lime);box-sizing:border-box;padding:0 6px}
.kc-pill.down{background:#FF3B47;color:#fff}
"""

ex = [T('<main><div class="kc-ex-wrap">'
        '<!-- Top Search & Actions -->'
        '<div class="kc-top-bar">'
        '  <div class="kc-search-box">'
        '    @@'
        '    <input id="q" type="search" class="kc-search-input" placeholder="LSK" autocomplete="off">'
        '  </div>'
        '  <div class="kc-search-actions">'
        '    <button type="button" class="kc-action-btn" id="btnTrend" title="Trends">'
        '      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>'
        '    </button>'
        '    <a href="notifications.html" class="kc-action-btn" title="Alerts">'
        '      @@'
        '      <span class="dot"></span>'
        '    </a>'
        '  </div>'
        '</div>'
        '<!-- Primary Category Tabs -->'
        '<div class="kc-cat-tabs" id="kcCatTabs">'
        '  <button type="button" class="kc-cat-tab" data-cat="fav">Favorites</button>'
        '  <button type="button" class="kc-cat-tab on" data-cat="markets">All Shares</button>'
        '  <button type="button" class="kc-cat-tab" data-cat="alpha">Top Alpha 🔥</button>'
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
        '  <button type="button" class="kc-edit-btn" id="btnEdit" title="Customize list">'
        '    <svg class="ic-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>'
        '  </button>'
        '</div>'
        '<!-- Floating Widget Banner -->'
        '<div class="kc-banner" id="annBanner">'
        '  <div class="kc-banner-text">Matchday 05 Player Shares Live: Buy &amp; hold player shares to unlock your Dream Club.</div>'
        '  <div class="kc-banner-actions">'
        '    <button type="button" class="kc-banner-close" onclick="document.getElementById(\'annBanner\').style.display=\'none\'">✕</button>'
        '  </div>'
        '</div>'
        '<!-- Table Headers -->'
        '<div class="kc-th">'
        '  <span data-sort="pair">Player Share ⇅ / Volume ⇅</span>'
        '  <span data-sort="price" style="justify-content:flex-end">Price ($FTR) ⇅</span>'
        '  <span data-sort="change" style="justify-content:flex-end">24h Change ⇅</span>'
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
    var subPrice = a.club ? a.club : (a.p * 0.9997).toFixed(2) + ' FTR';
    var avatarLetter = sym.substring(0, 2).toUpperCase();

    return "<a class='kc-row' href='" + to + "'>"
      + "<div class='kc-row-left'>"
      + "  <div class='kc-avatar" + (a.c ? " coach" : "") + "'>" + avatarLetter + "</div>"
      + "  <div style='min-width:0'>"
      + "    <div class='kc-pair-title'>"
      + "      <span>" + sym + "</span>"
      + "      <span class='kc-pair-quote'>/" + quote + "</span>"
      + "      <span class='kc-tag'>" + (a.tag || (a.c ? 'COACH' : '10x')) + "</span>"
      + "    </div>"
      + "    <div class='kc-pair-sub'>" + a.n + " | " + (a.cap || a.vol || '39.24M') + "</div>"
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
.stepper button[aria-current="step"]{background:var(--lime);border-color:var(--lime);color:#0A0D03}
.stepper button:hover:not([aria-current="step"]){color:var(--ink);border-color:var(--hair-2)}
.forms{display:flex;gap:8px;flex-wrap:wrap}
.forms button{flex:1;min-width:92px;border:1px solid var(--hair);background:rgba(255,255,255,.03);color:var(--dim);
  border-radius:14px;padding:14px 0;font-family:'JetBrains Mono',monospace;font-size:14px;cursor:pointer;
  box-shadow:var(--inset);transition:all .6s var(--ease)}
.forms button[aria-pressed="true"]{background:var(--lime);border-color:var(--lime);color:#0A0D03}
.forms button:hover:not([aria-pressed="true"]){color:var(--ink);border-color:var(--hair-2)}
.swatches{display:flex;gap:8px;margin-top:12px}
.sw{width:34px;height:34px;border-radius:11px;border:1px solid var(--hair);cursor:pointer;box-shadow:var(--inset);
  transition:transform .6s var(--ease)}
.sw:hover,.sw[aria-pressed="true"]{transform:scale(1.08)}
.sw[aria-pressed="true"]{border-color:var(--ink)}
.lb{display:grid;grid-template-columns:52px 2fr 1fr 1fr 1fr;gap:14px;align-items:center;padding:15px 24px;
  border-bottom:1px solid rgba(255,255,255,.05);font-size:13px}
.lb.h{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;border-bottom:1px solid var(--hair)}
.lb .rank{font-family:'JetBrains Mono',monospace;color:var(--faint)}
.lb.you{background:rgba(196,248,42,.06)}
.lb .cn{display:flex;align-items:center;gap:12px}
.mini-crest{width:26px;height:29px;flex:none;clip-path:polygon(0 0,100% 0,100% 66%,50% 100%,0 66%)}
@media (max-width:768px){.lb{grid-template-columns:40px 1.6fr 1fr;padding:13px 16px}
 .lb>*:nth-child(n+4){display:none}}
"""

cl = ['<main><div class="kc-home-wrap" style="padding-top:12px;padding-bottom:84px">']
cl.append(T('<div class="kc-topbar">'
            '<a class="kc-icon-btn" href="dashboard.html" aria-label="Back to Home">@@</a>'
            '<div class="kc-top-title" id="clName">Zero FC</div>'
            '<a class="kc-icon-btn" href="club-builder.html?new=1" title="New Club" style="background:rgba(196,248,42,.1);border-color:rgba(196,248,42,.3);color:#C4F82A;font-weight:700;font-size:18px">+</a>'
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
var curColor='#C4F82A';

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
  curColor=c.color||'#C4F82A';

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
      curColor = s.style.background || '#C4F82A';
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
    "<defs><linearGradient id='vg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#C4F82A' stop-opacity='.35'/>"+
    "<stop offset='1' stop-color='#C4F82A' stop-opacity='0'/></linearGradient></defs>"+
    "<polygon points='0,"+h+" "+pts.join(' ')+" "+w+","+h+"' fill='url(#vg)'/>"+
    "<polyline points='"+pts.join(' ')+"' fill='none' stroke='#C4F82A' stroke-width='1.6' stroke-linejoin='round'/></svg>"+
    "<div class='b-row' style='margin-top:12px'><span>8 rounds ago</span><b>118,000</b></div>"+
    "<div class='b-row'><span>Now</span><b>245,800</b></div>";
}
"""
page("clubs.html", "Dream Clubs — Fantrade", "".join(cl), CL_JS, CL_CSS, app=True)

# ══════════════════════════════════════════════════════════
# CLUB BUILDER
# ══════════════════════════════════════════════════════════
# builder
bd = ['<main><div class="kc-home-wrap" style="padding-top:12px;padding-bottom:84px">']
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
          '<button class="sw" aria-pressed="true" style="background:linear-gradient(160deg,#C4F82A,#83b300)" aria-label="Lime"></button>'
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
# 4. FANPLAY
# ══════════════════════════════════════════════════════════
FP_CSS = """
.kc-home-wrap{max-width:680px;margin:0 auto;padding:12px 16px 84px}
.kc-fut-topbar{display:flex;align-items:center;justify-content:space-between;padding:8px 0 12px}
.kc-pair-btn{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);padding:6px 12px;border-radius:999px;cursor:pointer}
.kc-pair-btn:hover{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.14)}
.kc-pair-sym{font-weight:700;font-size:14.5px;color:#fff}
.kc-tag-perp{font-size:10px;padding:2px 6px;border-radius:4px;background:rgba(255,255,255,.08);color:#8E9AA8;font-weight:600}
.kc-tag-lev{font-size:10px;padding:2px 6px;border-radius:4px;background:rgba(196,248,42,.15);color:#C4F82A;font-weight:700}
.kc-delta-badge{font-family:'JetBrains Mono',monospace;font-size:11.5px;font-weight:600;padding:3px 8px;border-radius:6px;background:rgba(196,248,42,.12);color:#C4F82A}

.kc-fut-stats{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-radius:12px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);font-size:11px;color:#8E9AA8;margin-bottom:14px;overflow-x:auto;gap:12px}
.kc-stat-item{display:flex;flex-direction:column;gap:2px;white-space:nowrap}
.kc-stat-item b{color:#fff;font-family:'JetBrains Mono',monospace;font-weight:500}

.kc-fut-desk{display:grid;grid-template-columns:1fr 1.2fr;gap:12px;margin-bottom:16px}
@media (max-width:540px){.kc-fut-desk{grid-template-columns:1fr}}

.kc-book-col{display:flex;flex-direction:column;gap:3px;font-family:'JetBrains Mono',monospace;font-size:11px}
.kc-book-row{display:flex;justify-content:space-between;padding:3px 6px;border-radius:4px;position:relative;overflow:hidden}
.kc-book-row::after{content:"";position:absolute;top:0;bottom:0;right:0;pointer-events:none;border-radius:4px}
.kc-book-row.ask::after{background:rgba(255,94,94,.12);width:var(--w,40%)}
.kc-book-row.ask span:first-child{color:#FF5E5E}
.kc-book-row.bid::after{background:rgba(196,248,42,.12);width:var(--w,40%)}
.kc-book-row.bid span:first-child{color:#C4F82A}
.kc-last-px{display:flex;align-items:baseline;gap:6px;padding:8px 6px;margin:4px 0;border-top:1px solid rgba(255,255,255,.06);border-bottom:1px solid rgba(255,255,255,.06)}
.kc-last-px b{font-size:17px;color:#C4F82A;font-weight:700}
.kc-last-px span{font-size:10px;color:#8E9AA8}

.kc-trade-col{display:flex;flex-direction:column;gap:10px}
.kc-side-tgl{display:grid;grid-template-columns:1fr 1fr;gap:6px;padding:4px;border-radius:12px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07)}
.kc-side-btn{border:0;background:transparent;padding:8px 0;border-radius:8px;font-family:Archivo,sans-serif;font-weight:700;font-size:11.5px;text-transform:uppercase;cursor:pointer;color:#8E9AA8;transition:all .2s}
.kc-side-btn.buy.on{background:#C4F82A;color:#0A0D03}
.kc-side-btn.sell.on{background:#FF5E5E;color:#fff}

.kc-input-box{display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border-radius:10px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);font-size:12px}
.kc-input-box label{font-size:9.5px;color:#8E9AA8;font-weight:600;text-transform:uppercase}
.kc-input-box input{border:0;background:transparent;color:#fff;text-align:right;font-family:'JetBrains Mono',monospace;font-size:13.5px;outline:none;width:60%}

.kc-pct-chips{display:flex;gap:4px}
.kc-pct-chip{flex:1;padding:5px 0;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);color:#8E9AA8;border-radius:6px;font-size:9.5px;font-family:'JetBrains Mono',monospace;cursor:pointer;text-align:center;transition:all .2s}
.kc-pct-chip:hover{background:rgba(255,255,255,.08);color:#fff}

.kc-fut-cta{width:100%;padding:12px 0;border-radius:12px;border:0;font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:13px;letter-spacing:.04em;text-transform:uppercase;cursor:pointer;background:#C4F82A;color:#0A0D03;transition:all .2s}
.kc-fut-cta.sell{background:#FF5E5E;color:#fff}

.kc-fut-tabs{display:flex;gap:16px;border-bottom:1px solid rgba(255,255,255,.08);padding-bottom:4px;margin:20px 0 14px}
.kc-fut-tab{background:transparent;border:0;color:#8E9AA8;font-family:Montserrat,sans-serif;font-size:13px;font-weight:600;cursor:pointer;padding:6px 0;position:relative}
.kc-fut-tab.on{color:#fff}
.kc-fut-tab.on::after{content:"";position:absolute;left:0;right:0;bottom:-5px;height:2px;background:#C4F82A;border-radius:2px}

.kc-pos-card{padding:16px;border-radius:16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);margin-bottom:12px}
.kc-pos-head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}
.kc-pos-name{font-weight:700;font-size:14px;color:#fff;display:flex;align-items:center;gap:6px}
.kc-pos-pnl{text-align:right;font-family:'JetBrains Mono',monospace}
.kc-pos-pnl .v{font-size:14.5px;font-weight:700;color:#C4F82A}
.kc-pos-pnl .p{font-size:11px;color:#C4F82A}
.kc-pos-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;font-size:11px;color:#8E9AA8;margin-top:10px}
.kc-pos-grid b{display:block;color:#fff;font-family:'JetBrains Mono',monospace;margin-top:2px}

.tierrail{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.tiercard{display:flex;flex-direction:column;gap:6px;padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);color:#8E9AA8;cursor:pointer;text-align:left}
.tiercard[aria-pressed="true"]{border-color:#C4F82A;background:rgba(196,248,42,.08);color:#fff}
.tiercard .t{font-weight:700;font-size:11px;text-transform:uppercase}
.tiercard .x{font-family:'JetBrains Mono',monospace;font-size:16px;color:#C4F82A}
.tiercard .risk{height:3px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden;margin-top:4px}
.tiercard .risk i{display:block;height:100%;border-radius:99px;background:#C4F82A}

.countdown{display:flex;gap:8px;margin-top:14px}
.cd{flex:1;text-align:center;border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:10px 4px;background:rgba(255,255,255,.03)}
.cd b{display:block;font-family:'JetBrains Mono',monospace;font-size:18px;color:#fff}
.cd span{font-size:8px;letter-spacing:.12em;color:#8E9AA8;text-transform:uppercase}

.calc .cr{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:12px;color:#8E9AA8}
.calc .cr b{color:#fff;font-family:'JetBrains Mono',monospace}
.calc .out{padding:14px;border-radius:12px;background:rgba(196,248,42,.06);border:1px solid rgba(196,248,42,.2);margin-top:12px;text-align:center}
.calc .out .v{font-family:'JetBrains Mono',monospace;font-size:26px;color:#C4F82A;font-weight:700}
"""

fp = ['<main><div class="kc-home-wrap">']

# Topbar
fp.append(T('<div class="kc-fut-topbar">'
            '<div class="kc-pair-btn">'
            '<span class="kc-pair-sym">$SAKA/FTR</span>'
            '<span class="kc-tag-perp">Perp</span>'
            '<span class="kc-tag-lev">10x</span>'
            '</div>'
            '<div class="kc-delta-badge">+6.40%</div>'
            '<div style="display:flex;align-items:center;gap:8px">'
            '<a class="kc-icon-btn" href="asset.html?a=%24Saka" title="Candlestick Chart" style="width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;color:#8E9AA8;text-decoration:none">@@</a>'
            '<button class="bell" type="button" id="fpBell" aria-label="Matchday alerts" style="width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;color:#8E9AA8;cursor:pointer">@@<span class="dot" id="fpBellDot" hidden></span></button>'
            '</div>'
            '<span hidden id="fpActiveCount">2 active</span>'
            '</div>',
            ic("candle", "ic"), ic("bell", "ic")))

# Sub Stats Bar
fp.append('<div class="kc-fut-stats">'
          '<div class="kc-stat-item"><span>Mark</span><b>14.80</b></div>'
          '<div class="kc-stat-item"><span>Index</span><b>14.78</b></div>'
          '<div class="kc-stat-item"><span>24h High</span><b>15.20</b></div>'
          '<div class="kc-stat-item"><span>24h Low</span><b>13.90</b></div>'
          '<div class="kc-stat-item"><span>Funding / Countdown</span><b style="color:#C4F82A">0.0100% 03:42:15</b></div>'
          '</div>')

# Futures Desk (Order Book + Ticket)
fp.append('<div class="kc-fut-desk">'
          '<div class="kc-book-col">'
          '<div class="kc-book-row ask" style="--w:78%"><span>14.95</span><span style="color:#8E9AA8">4,200</span></div>'
          '<div class="kc-book-row ask" style="--w:62%"><span>14.90</span><span style="color:#8E9AA8">6,800</span></div>'
          '<div class="kc-book-row ask" style="--w:45%"><span>14.85</span><span style="color:#8E9AA8">12,500</span></div>'
          '<div class="kc-last-px"><b>14.80</b><span>≈ $1.19</span></div>'
          '<div class="kc-book-row bid" style="--w:55%"><span>14.75</span><span style="color:#8E9AA8">8,900</span></div>'
          '<div class="kc-book-row bid" style="--w:70%"><span>14.70</span><span style="color:#8E9AA8">14,200</span></div>'
          '<div class="kc-book-row bid" style="--w:85%"><span>14.65</span><span style="color:#8E9AA8">19,500</span></div>'
          '</div>'
          '<div class="kc-trade-col">'
          '<div class="kc-side-tgl" id="futSideTgl">'
          '<button class="kc-side-btn buy on" type="button" data-side="buy">Open Long</button>'
          '<button class="kc-side-btn sell" type="button" data-side="sell">Open Short</button>'
          '</div>'
          '<div class="kc-input-box"><label>Price</label><input id="futPx" value="14.80" inputmode="decimal"></div>'
          '<div class="kc-input-box"><label>Qty</label><input id="futQty" value="1,000" inputmode="numeric"></div>'
          '<div class="kc-pct-chips">'
          '<button class="kc-pct-chip" type="button" data-fpct="25">25%</button>'
          '<button class="kc-pct-chip" type="button" data-fpct="50">50%</button>'
          '<button class="kc-pct-chip" type="button" data-fpct="75">75%</button>'
          '<button class="kc-pct-chip" type="button" data-fpct="100">100%</button>'
          '</div>'
          '<div style="display:flex;justify-content:space-between;font-size:11px;color:#8E9AA8;margin-top:2px">'
          '<span>Cost: <b style="color:#fff" id="futCost">1,480 FTR</b></span>'
          '<span>Max: <b style="color:#C4F82A">86,790</b></span>'
          '</div>'
          '<button class="kc-fut-cta" id="futGoBtn" type="button">Open Long (Buy)</button>'
          '</div></div>')

# Lower Tabs: Positions / Orders / Matchday Fantasy
fp.append('<div class="kc-fut-tabs" id="futTabs">'
          '<button class="kc-fut-tab on" type="button" data-sec="pos">Positions (1)</button>'
          '<button class="kc-fut-tab" type="button" data-sec="orders">Open Orders (0)</button>'
          '<button class="kc-fut-tab" type="button" data-sec="fantasy">Matchday 07 Fantasy</button>'
          '</div>')

# Section: Positions
fp.append('<div id="secPos">'
          '<div class="kc-pos-card">'
          '<div class="kc-pos-head">'
          '<div><div class="kc-pos-name">$SAKA Perp <span class="kc-tag-lev">10x Long</span></div>'
          '<div style="font-size:11px;color:#8E9AA8;margin-top:3px">Isolated · Size: 10,000 shares</div></div>'
          '<div class="kc-pos-pnl"><div class="v">+1,420.00 FTR</div><div class="p">+28.40% ROE</div></div>'
          '</div>'
          '<div class="kc-pos-grid">'
          '<div><span>Entry Price</span><b>13.90</b></div>'
          '<div><span>Mark Price</span><b>14.80</b></div>'
          '<div><span>Liq. Price</span><b style="color:#FF5E5E">7.40</b></div>'
          '<div><span>Margin</span><b>5,000 FTR</b></div>'
          '<div><span>TP / SL</span><b>-- / --</b></div>'
          '<div style="display:flex;align-items:flex-end">'
          '<button type="button" onclick="showToast(\'Position closed at market price.\', \'success\')" style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);color:#fff;font-size:11px;cursor:pointer">Close</button>'
          '</div></div></div></div>')

# Section: Orders
fp.append('<div id="secOrders" style="display:none">'
          '<div style="padding:28px;text-align:center;color:#8E9AA8;font-size:13px">No open limit orders right now.</div>'
          '</div>')

# Section: Matchday 07 Fantasy (FanPlay)
fp.append('<div id="secFantasy" style="display:none">'
          '<div style="display:flex;flex-direction:column;gap:16px">'
          '<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden;padding:18px" data-reveal>'
          '<div class="fstep-h"><span class="n">1</span>Choose Play Mode</div>'
          '<div class="seg2" role="tablist" style="margin-bottom:14px">'
          '<button class="tab" role="tab" id="tab-solo" aria-selected="false" data-mode="solo" style="border-radius:12px;padding:12px">'
          '<span class="l" style="font-weight:700">Individual</span><span class="s" style="font-size:11px;color:#8E9AA8">One player</span></button>'
          '<button class="tab" role="tab" id="tab-club" aria-selected="true" data-mode="club" style="border-radius:12px;padding:12px">'
          '<span class="l" style="font-weight:700">Dream Club</span><span class="s" id="clubModeNote" style="font-size:11px;color:#8E9AA8">Whole club</span></button>'
          '</div>'
          '<div class="clubrail" id="fpClubs" style="margin-bottom:14px"></div>'
          '<div class="fp-sel" style="margin-bottom:12px"><span class="badge" id="selBadge"></span>'
          '<div style="min-width:0"><div class="nm" id="selName">Zero FC</div>'
          '<p class="sub" id="selSub">4-3-3 · Coach $Arteta</p></div>'
          '<div class="right">Ownership<span class="up" style="color:#C4F82A">Verified</span></div></div>'
          '<div class="line"><span>Fixtures tracked</span><b id="fixtures">9 matches · 4 leagues</b></div>'
          '<div class="line"><span>Entries live this round</span><b id="fpLive">—</b></div>'
          '</div>')

# Tiers Card
fp.append('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden;padding:18px" data-reveal>'
          '<div class="fstep-h"><span class="n">2</span>Select Market Tier</div>'
          '<div class="tierrail" id="markets">')

TIERS = [("Simple", 1, "Goals, assists and clean sheets.", 18),
         ("PRO", 1.4, "Adds key passes, duels won and expected goals.", 32),
         ("Elite", 2, "Full performance data, position-weighted.", 50),
         ("Killer", 3, "Elite scoring plus cards, misses and errors against you.", 68),
         ("Viynx Move", 4.5, "Scoring swings with live in-match movement.", 84),
         ("Viynx Max", 7, "Every event counts, at maximum weight.", 100)]

for name, m, note, risk in TIERS:
    fp.append(T('<button class="mkt tiercard"@@ data-m="@@" data-note="@@">'
                '<span class="t">@@</span><span class="x">×@@</span>'
                '<span class="risk"><i style="width:@@%"></i></span></button>',
                ' aria-pressed="true"' if name == "Elite" else ' aria-pressed="false"',
                m, note, name, ("%g" % m), risk))
fp.append('</div><p class="mkt-note" id="mktNote" style="margin-top:10px;font-size:12px;color:#8E9AA8">Full performance data, position-weighted.</p></div>')

# Stake & Output
fp.append(T('<div class="bezel" style="border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden;padding:18px" data-reveal>'
            '<div class="fstep-h"><span class="n">3</span>Stake &amp; Activate</div>'
            '<div class="field"><label>Amount</label>'
            '<input id="fpStake" value="2,500" inputmode="numeric"></div>'
            '<div class="quick"><button type="button" data-st="1000">1,000</button>'
            '<button type="button" data-st="2500">2,500</button>'
            '<button type="button" data-st="5000">5,000</button>'
            '<button type="button" class="maxbtn" id="fpMax">Max</button></div>'
            '<div class="line"><span>Available</span><b><span data-bind="balance">128,450</span> $FTR</b></div>'
            '<div class="line"><span>Weekly cap remaining</span><b id="fpCapLeft">—</b></div>'
            '<div class="capbar" style="margin:10px 0"><i id="fpCapBar" style="width:50%"></i></div>'
            '<div class="calc" style="margin-top:14px">'
            '<div class="cr"><span id="baseLabel">Club base points</span><b id="basePts">100 FP</b></div>'
            '<div class="cr"><span>Market multiplier</span><b id="multPts">×2.0</b></div>'
            '<div class="cr boost" id="boostRow"><span>Club boost</span><b style="color:var(--amber)">+15%</b></div>'
            '<div class="out"><div style="font-size:10px;text-transform:uppercase;color:#8E9AA8;letter-spacing:.12em">Projected Fans Point</div>'
            '<div class="v" id="fpOut">230</div>'
            '<div style="font-size:11px;color:#8E9AA8" id="fpNote">Club mode · Elite</div></div>'
            '</div>'
            '@@'
            '<a class="fp-boardlink" href="liveboard.html" style="margin-top:14px;display:flex;align-items:center;gap:8px;text-decoration:none;font-size:12px;color:#C4F82A">@@<span>Live Matchday Board</span><span style="margin-left:auto;color:#8E9AA8">9 fixtures @@</span></a>'
            '</div></div></div>',
            btn("Activate entry", tag="button",
                extra='id="activateEntryBtn" style="margin-top:16px;width:100%;justify-content:space-between"'),
            ic("pulse", "ic"), ic("arrow", "ic-sm")))

fp.append('</div></main>')


FP_JS = r"""
var mode='club', mult=2, mktName='ELITE';
var tabs=document.querySelectorAll('.tab'), mkts=document.querySelectorAll('.mkt');
var CREST="<svg class='ic'><use href='#i-crest'/></svg>", BOOT="<svg class='ic'><use href='#i-boot'/></svg>";
// which club this entry stakes — defaults to the one you last switched to
var pickedClub = FT.activeClubId();

function staked(id){
  return (FT.getState().fanplay.activeEntries || []).filter(function(e){ return e.clubId === id; })[0];
}
function renderClubs(){
  var rail=document.getElementById('fpClubs'), s=FT.getState();
  if(!rail) return;
  rail.hidden = mode!=='club';
  if(mode!=='club') return;
  rail.innerHTML=s.clubs.map(function(c){
    var live=staked(c.id);
    return '<button class="clubchip" type="button" data-club="'+c.id+'"'
      +(c.id===pickedClub?' aria-pressed="true"':' aria-pressed="false"')+'>'
      +'<span class="rc" style="background:linear-gradient(160deg,'+c.colors[0]+','
      +(c.colors[1]||c.colors[0])+')">'
      +c.name.split(/\s+/).map(function(w){ return w.charAt(0).toUpperCase(); }).join('').slice(0,3)+'</span>'
      +'<span class="cn">'+c.name+'</span>'
      +'<span class="cd">'+(live?'staked':'+'+(c.boost||0).toFixed(1)+'%')+'</span></button>';
  }).join('');
  rail.querySelectorAll('[data-club]').forEach(function(b){
    b.addEventListener('click',function(){
      pickedClub=b.dataset.club; renderClubs(); render();
    });
  });
}

function render(){
  var s=FT.getState();
  var club=mode==='club';
  var c=club?FT.getClub(pickedClub):null;
  var boost=club?(c.boost||0)/100:0;
  var base=100, total=Math.round(base*(1+boost)*mult);
  document.getElementById('basePts').textContent=base+' FP';
  document.getElementById('multPts').textContent='×'+mult.toFixed(1);
  document.getElementById('fpOut').textContent=total.toLocaleString();
  document.getElementById('fpNote').textContent=(club?c.name:'Individual mode')+' · '+mktName;
  var br=document.getElementById('boostRow');
  br.style.display=club?'flex':'none';
  br.querySelector('b').textContent='+'+(club?(c.boost||0).toFixed(1):'0.0')+'%';
  document.getElementById('capRow').style.display=club?'flex':'none';
  var cName=club?c.name:'$Bruno';
  var cForm=club?(c.formation||'4-3-3'):'';
  document.getElementById('selBadge').innerHTML=club?CREST:BOOT;
  document.getElementById('selName').textContent=cName;
  document.getElementById('selSub').textContent=club
    ? cForm+' · Coach '+(c.coach||'$Arteta')+' · '+(c.division||'Challenger')+' division'
    : 'Bruno Fernandes · 10,000 shares activated';
  var cmn=document.getElementById('clubModeNote');
  if(cmn) cmn.textContent=club
    ? c.name+' · +'+(c.boost||0).toFixed(1)+'%'
    : s.clubs.length+(s.clubs.length===1?' club':' clubs');
  document.getElementById('baseLabel').textContent=club?'Club base points':'Player base points';
  document.getElementById('fixtures').textContent=club?'9 matches · 4 leagues':'1 match · Man Utd v Spurs';
  var lv=document.getElementById('fpLive');
  if(lv){
    var n=(s.fanplay.activeEntries||[]).length;
    lv.textContent=n+(n===1?' entry':' entries');
  }
  var btn=document.getElementById('activateEntryBtn');
  if(btn){
    var done = club && staked(pickedClub);
    btn.innerHTML = done
      ? "Already staked <span class='cap'><svg class='ic'><use href='#i-check'/></svg></span>"
      : "Activate entry <span class='cap'><svg class='ic'><use href='#i-arrow'/></svg></span>";
    btn.classList.toggle('btn-glass', !!done);
    btn.classList.toggle('btn-lime', !done);
  }
}
tabs.forEach(function(t){ t.addEventListener('click',function(){
  tabs.forEach(function(x){ x.setAttribute('aria-selected','false'); });
  t.setAttribute('aria-selected','true'); mode=t.dataset.mode;
  document.getElementById('pane').setAttribute('aria-labelledby',t.id);
  renderClubs(); render(); }); });
mkts.forEach(function(m){ m.addEventListener('click',function(){
  mkts.forEach(function(x){ x.setAttribute('aria-pressed','false'); });
  m.setAttribute('aria-pressed','true'); mult=parseFloat(m.dataset.m);
  mktName=(m.querySelector('.t')||m).textContent.trim();
  document.getElementById('mktNote').textContent=m.dataset.note; render(); }); });
renderClubs(); render();

function syncFPEntriesCount(){
  var s=FT.getState();
  var el=document.getElementById('fpActiveCount');
  if(el) el.textContent=s.fanplay.activeEntries.length+' active';
  render();
}
syncFPEntriesCount();

var actBtn=document.getElementById('activateEntryBtn');
if(actBtn){
  actBtn.addEventListener('click',function(){
    var s=FT.getState();
    var club=mode==='club'?FT.getClub(pickedClub):null;
    var base=100;
    var total=Math.round(base*(club?1+(club.boost||0)/100:1)*mult);
    var target=club?club.name:'$Bruno';

    try{
      var stake=stakeAmount();
      if(stake<100){ showToast("The smallest stake is 100 $FTR.", "error"); return; }
      var entry=FT.activateFanPlayEntry({
        mode: mode==='club'?'Dream Club':'Individual',
        clubId: club?club.id:'',
        target: target,
        tier: mktName,
        mult: mult,
        stake: stake,
        projectedFP: total
      });
      syncFPEntriesCount();
      renderClubs();
      showToast("Entry activated for "+target+" in "+mktName+" tier · "
        +stake.toLocaleString('en-US')+" $FTR staked.", "success");
      actBtn.innerHTML="Entry active <span class='cap'><svg class='ic'><use href='#i-check'/></svg></span>";
      setTimeout(function(){
        actBtn.innerHTML="Activate another entry <span class='cap'><svg class='ic'><use href='#i-arrow'/></svg></span>";
      },3200);
    }catch(err){
      showToast(err.message, "error");
      if(err.message.indexOf("Insufficient")!==-1){
        setTimeout(function(){ showAccountModal(); }, 700);
      }
    }
  });
}
window.addEventListener('fantrade:statechange', function(){ renderClubs(); syncFPEntriesCount(); });

// ── stake field ─────────────────────────────────────────────────
function el(id){ return document.getElementById(id); }
function stakeAmount(){ return parseInt(String(el('fpStake').value).replace(/[^0-9]/g,''),10)||0; }
function capBar(){
  var s=FT.getState(), cap=s.prefs.stakeCap||5000, used=stakeAmount();
  var left=Math.max(0, cap-used);
  el('fpCapLeft').textContent=left.toLocaleString('en-US')+' of '+cap.toLocaleString('en-US')+' $FTR';
  el('fpCapBar').style.width=Math.min(100, used/cap*100).toFixed(0)+'%';
  el('fpCapBar').style.background=used>cap?'var(--red)':'var(--lime)';
}
el('fpStake').addEventListener('input',function(){
  var v=el('fpStake').value.replace(/[^0-9]/g,'');
  el('fpStake').value=v?(+v).toLocaleString('en-US'):'';
  capBar();
});
document.querySelectorAll('[data-st]').forEach(function(b){
  b.addEventListener('click',function(){
    el('fpStake').value=(+b.dataset.st).toLocaleString('en-US'); capBar();
  });
});
el('fpMax').addEventListener('click',function(){
  var s=FT.getState();
  el('fpStake').value=Math.min(s.wallet.balance, s.prefs.stakeCap||5000).toLocaleString('en-US');
  capBar();
});
capBar();
window.addEventListener('fantrade:statechange', capBar);

// ── round clock ─────────────────────────────────────────────────
var left=4*3600+12*60+38;
function pad(n){ return n<10?'0'+n:''+n; }
if(!reduce) setInterval(function(){
  if(left<=0) return; left--;
  el('fpH').textContent=pad(Math.floor(left/3600));
  el('fpM').textContent=pad(Math.floor(left%3600/60));
  el('fpS').textContent=pad(left%60);
},1000);

// ── matchday alerts, from the same feed the bell in the top bar reads ──
var KIND={settle:'Settlement', order:'Order', club:'Club', system:'Account'};
el('fpBell').addEventListener('click',function(){
  var s=FT.getState();
  var rows=(s.notifications||[]).filter(function(n){
    return n.kind==='settle'||n.kind==='club';
  }).slice(0,5);
  var html='<h3 class="ft-modal-title">Matchday alerts</h3>';
  if(!rows.length){
    html+='<div class="empty-state"><svg class="ic-xl" aria-hidden="true"><use href="#i-pulse"/></svg>'
      +'Nothing on the round yet.</div>';
  } else {
    html+='<div style="max-height:52vh;overflow:auto;margin-bottom:18px">'+rows.map(function(n){
      return '<div class="trow"><span class="coin'+(n.tone==='up'?' lime':'')+'">'
        +'<svg class="ic" aria-hidden="true"><use href="#i-'+n.icon+'"/></svg></span>'
        +'<div class="bd"><div class="t">'+n.title+(n.read?'':' <span class="tag lime">New</span>')+'</div>'
        +'<div class="d">'+KIND[n.kind]+' · '+n.time+'</div></div>'
        +(n.amt?'<div class="a" style="color:'+(n.tone==='down'?'var(--red)':'var(--lime)')+'">'+n.amt+'</div>':'')
        +'</div>';
    }).join('')+'</div>';
  }
  html+='<div style="display:flex;gap:10px;flex-wrap:wrap">'
    +'<a class="btn btn-lime" href="notifications.html" style="flex:1;justify-content:center">All activity</a>'
    +'<button class="btn btn-glass" id="fpBellRead" type="button" style="flex:1;justify-content:center">'
    +'Mark read</button></div>';
  openModal(html);
  var r=el('fpBellRead');
  if(r) r.addEventListener('click',function(){ FT.readAll(); closeModal(); paintBell(); });
});
function paintBell(){
  var n=FT.unread();
  el('fpBellDot').hidden = n===0;
  el('fpBell').setAttribute('aria-label', n ? n+' unread matchday alerts' : 'Matchday alerts');
}
paintBell();
window.addEventListener('fantrade:statechange', paintBell);

// Futures bottom tabs
document.querySelectorAll('#futTabs button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#futTabs button').forEach(function(x){ x.classList.remove('on'); });
    b.classList.add('on');
    var sec = b.dataset.sec;
    el('secPos').style.display = sec === 'pos' ? '' : 'none';
    el('secOrders').style.display = sec === 'orders' ? '' : 'none';
    el('secFantasy').style.display = sec === 'fantasy' ? '' : 'none';
  });
});

// Futures side toggle
var futSide = 'buy';
document.querySelectorAll('#futSideTgl button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#futSideTgl button').forEach(function(x){ x.classList.remove('on'); });
    b.classList.add('on');
    futSide = b.dataset.side;
    var btn = el('futGoBtn');
    if(futSide === 'buy'){
      btn.textContent = 'Open Long (Buy)';
      btn.className = 'kc-fut-cta';
    } else {
      btn.textContent = 'Open Short (Sell)';
      btn.className = 'kc-fut-cta sell';
    }
  });
});

// Futures percentage chips
document.querySelectorAll('[data-fpct]').forEach(function(b){
  b.addEventListener('click', function(){
    var pct = parseInt(b.dataset.fpct, 10);
    var px = parseFloat(el('futPx').value) || 14.80;
    var s = FT.getState();
    var available = s.wallet.balance || 128450;
    var marginToUse = (available * (pct / 100)) * 0.1;
    var qty = Math.floor((marginToUse * 10) / px);
    el('futQty').value = qty.toLocaleString('en-US');
    el('futCost').textContent = Math.round(qty * px * 0.1).toLocaleString('en-US') + ' FTR';
  });
});

// Futures order submit
el('futGoBtn').addEventListener('click', function(){
  var qty = parseInt(String(el('futQty').value).replace(/[^0-9]/g, ''), 10) || 0;
  if(qty <= 0){ showToast('Enter a valid order quantity.', 'error'); return; }
  showToast((futSide === 'buy' ? 'Long' : 'Short') + ' order for ' + qty.toLocaleString('en-US') + ' $SAKA placed at 10x leverage.', 'success');
});
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
.kc-home-wrap{max-width:680px;margin:0 auto;padding:12px 16px 84px}
.bezel.flat .datestrip{margin-bottom:4px}
"""

lb = ['<main><div class="kc-home-wrap" style="padding-top:12px;padding-bottom:84px">']

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
    el.style.color='#C4F82A'; setTimeout(function(){ el.style.color=''; },800); }
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
