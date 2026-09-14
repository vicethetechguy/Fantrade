# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import head, atmosphere, nav, footer, ic, JS_SHELL

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.makedirs(OUT, exist_ok=True)

def T(tpl, *args):
    """Template with @@ placeholders — avoids %-escaping every literal percent in HTML."""
    out = tpl
    for a in args:
        out = out.replace("@@", str(a), 1)
    return out

ARROW = '<span class="cap">' + ic("arrow", "ic") + '</span>'


def btn(label, cls="btn-lime", href="#", tag="a", extra=""):
    o = '<%s class="btn %s" %s %s>%s%s</%s>' % (
        tag, cls, ('href="%s"' % href) if tag == "a" else "", extra, label, ARROW, tag)
    return o


def page(fname, title, body, js="", css="", app=False):
    html = (head(title, css) + atmosphere() + nav(title.split(" — ")[0] if " — " in title else "", app) +
            body + footer() + "<script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
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
                  "the round into Fantrade Points, then $FTR.",
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
         ("05 / Earn", "Settle in $FTR", "Real match data converts performance into Fantrade Points.", "c3", ""),
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
.ticket .line:last-of-type{border-bottom:0}
.movers{display:flex;flex-direction:column;gap:2px}
.mv{display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.05)}
.mv:last-child{border-bottom:0}
.mv .r{margin-left:auto;text-align:right}
.mv .r .p{font-family:'JetBrains Mono',monospace;font-size:13px}
.mv .r .d{font-family:'JetBrains Mono',monospace;font-size:11px}
.ringwrap{display:flex;align-items:center;gap:20px;margin:6px 0 18px}
.ring{width:96px;height:96px;flex:none}
.chartbox{padding:24px 26px 10px}
.legend{display:flex;gap:18px;flex-wrap:wrap;padding:0 26px 22px;font-size:11.5px;color:var(--faint)}
.legend span{display:flex;align-items:center;gap:8px}
.legend i{width:16px;height:2px;border-radius:2px;display:block}
"""

ex = []
ex.append(T('<header class="phead"><div class="wrap">'
          '<span class="pill" data-reveal>@@ Live market</span>'
          '<h1 data-reveal>Exchange</h1>'
          '<p class="lede" data-reveal>Every player and every coach carries a fixed supply of ten million shares. '
          'Price is set by what fans are willing to pay for the football underneath it.</p>'
          '<div class="statbar" data-reveal>'
          '<div>@@ 24h volume <b>4.28M $FTR</b></div>'
          '<div>@@ Listed assets <b>2,140</b></div>'
          '<div>@@ Top mover <b>$Jackson +11.2%</b></div>'
          '<div>@@ Next settlement <b>Fri 18:30</b></div></div></div></header>', ic("candle", "ic"), ic("chart", "ic"), ic("layers", "ic"), ic("bolt", "ic"), ic("clock", "ic")))

ex.append('<main><section style="padding-top:40px"><div class="wrap">')
ex.append(T('<div class="rail" data-reveal><div class="seg" id="seg">'
          '<button aria-pressed="true" data-f="all">@@ All</button>'
          '<button aria-pressed="false" data-f="player">@@ Players</button>'
          '<button aria-pressed="false" data-f="coach">@@ Coaches</button></div>'
          '<div class="searchbox">@@<input id="q" type="search" placeholder="Search a player or coach"></div>'
          '<div class="seg"><button aria-pressed="false">@@ Filters</button></div></div>', ic("layers", "ic"), ic("boot", "ic"), ic("whistle", "ic"), ic("search", "ic"), ic("filter", "ic")))

ex.append('<div class="bento"><div class="bezel c8" data-reveal><div class="core">'
          '<div class="mhead"><span>Asset</span><span>Price $FTR</span><span>24h</span><span>Valuation</span>'
          '<span>Supply held</span><span></span></div><div id="mkt"></div></div></div>')

# trade ticket
ex.append('<div class="c4" style="display:flex;flex-direction:column;gap:16px">'
          '<div class="bezel" data-reveal><div class="core pad ticket">'
          '<div style="display:flex;align-items:center;gap:13px;margin-bottom:20px">'
          '<span class="badge">%s</span><div><div style="font-family:Archivo;font-variation-settings:\'wdth\' 118,\'wght\' 800;'
          'text-transform:uppercase;font-size:17px" id="tkSym">$Saka</div>'
          '<div class="k-label" style="margin:4px 0 0" id="tkName">Bukayo Saka · Arsenal</div></div>'
          '<div style="margin-left:auto;text-align:right"><div class="num" style="font-size:18px" id="tkPx">48.20</div>'
          '<div class="num up" style="font-size:11px" id="tkD">+6.4%%</div></div></div>'
          '<div class="seg" style="width:100%%;margin-bottom:16px"><button style="flex:1;justify-content:center" '
          'aria-pressed="true" data-side="buy">Buy</button><button style="flex:1;justify-content:center" '
          'aria-pressed="false" data-side="sell">Sell</button></div>'
          '<div class="field"><label>Shares</label><input id="qty" value="10,000" inputmode="numeric"></div>'
          '<div class="quick"><button data-q="1000">1K</button><button data-q="10000">10K</button>'
          '<button data-q="50000">50K</button><button data-q="100000">100K</button></div>'
          '<div class="line"><span>Price per share</span><b id="sumPx">48.20 $FTR</b></div>'
          '<div class="line"><span>Subtotal</span><b id="sumSub">482,000</b></div>'
          '<div class="line"><span>Exchange fee (0.4%%)</span><b id="sumFee">1,928</b></div>'
          '<div class="line"><span>Total</span><b id="sumTot">483,928 $FTR</b></div>'
          '%s</div></div>' % (ic("boot", "ic"), btn("Review order", tag="button", extra='id="reviewOrderBtn" style="margin-top:20px;width:100%;justify-content:space-between"')))

ex.append('<div class="bezel" data-reveal><div class="core pad-sm">'
          '<div class="k-label">Supply</div><div class="ringwrap">'
          '<svg class="ring" viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="6"/>'
          '<circle id="spRing" cx="50" cy="50" r="42" fill="none" stroke="#C4F82A" stroke-width="6" stroke-linecap="round" '
          'stroke-dasharray="264" stroke-dashoffset="166" transform="rotate(-90 50 50)"/></svg>'
          '<div><div class="num" style="font-size:24px" id="spHeld">3,712,480</div>'
          '<div class="k-label" style="margin:6px 0 0">Held by fans</div>'
          '<div class="num" style="font-size:13px;color:var(--dim);margin-top:10px" id="spPct">37.1% of 10,000,000</div></div></div>'
          '<div class="b-row"><span>Your holding</span><b id="spYourHolding">10,000</b></div>'
          '<div class="b-row"><span>Average entry</span><b id="spAvgEntry">31.40</b></div>'
          '<div class="b-row"><span>Unrealised</span><b class="up" id="spUnrealised">+168,000</b></div>'
          '<div class="b-row"><span>In your club</span><b id="spInClub">ZERO FC · RW</b></div></div></div></div></div>')
ex.append('</div></section>')

# movers + coach index
ex.append('<section style="padding-top:20px"><div class="wrap"><div class="bento">')
ex.append(T('<div class="bezel c4" data-reveal><div class="core pad"><div class="k-label">@@ Top gainers · 24h</div>'
          '<div class="movers" id="gainers"></div></div></div>', ic("bolt", "ic-sm")))
ex.append(T('<div class="bezel c4" data-reveal><div class="core pad"><div class="k-label">@@ Fallers · 24h</div>'
          '<div class="movers" id="fallers"></div></div></div>', ic("pulse", "ic-sm")))
ex.append(T('<div class="bezel c4" data-reveal><div class="core pad"><div class="k-label">@@ Coach index</div>'
          '<div class="value-big">24.65 <small>$FTR</small></div>'
          '<div class="delta">▲ 2.1% · weighted across 186 listed coaches</div>'
          '<div style="margin-top:20px">@@</div>'
          '<p style="font-size:13px;font-weight:300;color:var(--dim);margin-top:18px">Coaches move on results, not '
          'minutes. A win, a clean sheet or a tactical turnaround feeds the index — and your club modifier.</p>'
          '</div></div>', ic("whistle", "ic-sm"), '<div id="coachSpark"></div>'))
ex.append('</div></div></section>')

# how trading works
ex.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
          '<span class="pill">@@ Order mechanics</span><h2>How a trade<br>settles here</h2></div>'
          '<div class="bento">', ic("swap", "ic")))
for icon, t, d, c in [("wallet", "Fund in $FTR", "Deposit, convert to $FTR, and your balance is ready to trade against any listed asset.", "c4"),
                      ("candle", "Buy at market", "Orders fill against the live book. Fees are 0.4% on both sides and are always shown before you confirm.", "c4"),
                      ("shield", "Ownership recorded", "Settled shares land in your wallet immediately and become eligible for FanPlay and club selection.", "c4")]:
    ex.append(T('<div class="bezel tight @@" data-reveal><div class="core pad f"><span class="ibox">@@</span>'
              '<h4>@@</h4><p>@@</p></div></div>', c, ic(icon, "ic-lg"), t, d))
ex.append('</div></div></section></main>')

EX_JS = r"""
var filter='all', q='', side='buy', sel=0;
function fmt(n){ return n.toLocaleString('en-US'); }
function rows(){
  var list=ASSETS.map(function(a,i){ return [a,i]; }).filter(function(x){
    var a=x[0];
    if(filter==='player'&&a.c) return false;
    if(filter==='coach'&&!a.c) return false;
    if(q && (a.t+' '+a.n).toLowerCase().indexOf(q)<0) return false;
    return true;
  });
  document.getElementById('mkt').innerHTML = list.map(function(x){
    var a=x[0], i=x[1];
    return "<div class='mrow"+(i===sel?" sel":"")+"' data-i='"+i+"'><div class='asset'><span class='badge"+(a.c?" coach":"")+
      "'><svg class='ic'><use href='#i-"+(a.c?'whistle':'boot')+"'/></svg></span><div><div class='t-sym'>"+a.t+
      "</div><div class='t-nm'>"+a.n+"</div></div></div><div class='tick' data-px>"+a.p.toFixed(2)+
      "</div><div class='tick "+(a.d>=0?'up':'down')+"' data-dx>"+(a.d>=0?'+':'')+a.d.toFixed(1)+"%</div>"+
      "<div class='num' style='font-size:12.5px;color:var(--dim)'>"+a.cap+" $FTR</div>"+
      "<div class='num' style='font-size:12.5px;color:var(--dim)'>"+a.h.toFixed(1)+"%</div>"+
      "<div><button class='tradebtn' data-trade='"+i+"'>Trade</button></div></div>";
  }).join('') || "<div style='padding:40px 24px;color:var(--dim);font-size:14px'>No assets match that search. Try a surname or a ticker like $Saka.</div>";
  document.querySelectorAll('[data-trade]').forEach(function(b){
    b.addEventListener('click',function(e){
      e.stopPropagation();
      sel=+b.dataset.trade;
      loadTicket();
      rows();
      if(window.innerWidth <= 768){
        var tk=document.querySelector('.ticket');
        if(tk) tk.scrollIntoView({ behavior:'smooth', block:'start' });
      }
    });
  });
  document.querySelectorAll('.mrow').forEach(function(row){
    row.addEventListener('click',function(e){
      if(e.target.closest('[data-trade]')) return;
      sel=+row.dataset.i;
      loadTicket();
      rows();
      if(window.innerWidth <= 768){
        var tk=document.querySelector('.ticket');
        if(tk) tk.scrollIntoView({ behavior:'smooth', block:'start' });
      }
    });
  });
}
function loadTicket(){
  var a=ASSETS[sel];
  document.getElementById('tkSym').textContent=a.t;
  document.getElementById('tkName').textContent=a.n+(a.c?' · Coach':' · Player');
  document.getElementById('tkPx').textContent=a.p.toFixed(2);
  var d=document.getElementById('tkD');
  d.textContent=(a.d>=0?'+':'')+a.d.toFixed(1)+'%'; d.className='num '+(a.d>=0?'up':'down');
  calc();
}
function calc(){
  var a=ASSETS[sel];
  var qty=parseInt((document.getElementById('qty').value||'0').replace(/[^0-9]/g,''),10)||0;
  var sub=qty*a.p, fee=sub*0.004;
  document.getElementById('sumPx').textContent=a.p.toFixed(2)+' $FTR';
  document.getElementById('sumSub').textContent=fmt(Math.round(sub));
  document.getElementById('sumFee').textContent=fmt(Math.round(fee));
  document.getElementById('sumTot').textContent=fmt(Math.round(side==='buy'?sub+fee:sub-fee))+' $FTR';
}
var qty=document.getElementById('qty');
if(qty){
  qty.addEventListener('input',function(){
    var v=qty.value.replace(/[^0-9]/g,''); qty.value=v?(+v).toLocaleString('en-US'):''; calc();
  });
  document.querySelectorAll('[data-q]').forEach(function(b){
    b.addEventListener('click',function(){ qty.value=(+b.dataset.q).toLocaleString('en-US'); calc(); });
  });
  document.querySelectorAll('[data-side]').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('[data-side]').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
      b.setAttribute('aria-pressed','true'); side=b.dataset.side; calc();
    });
  });
}
document.querySelectorAll('#seg button').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('#seg button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true'); filter=b.dataset.f; rows();
  });
});
var qi=document.getElementById('q');
if(qi) qi.addEventListener('input',function(){ q=qi.value.toLowerCase().trim(); rows(); });

function moverRow(a){
  return "<div class='mv'><span class='badge'><svg class='ic'><use href='#i-"+(a.c?'whistle':'boot')+"'/></svg></span>"+
    "<div><div class='t-sym'>"+a.t+"</div><div class='t-nm'>"+a.n+"</div></div>"+
    "<div class='r'><div class='p'>"+a.p.toFixed(2)+"</div><div class='d "+(a.d>=0?'up':'down')+"'>"+
    (a.d>=0?'+':'')+a.d.toFixed(1)+"%</div></div></div>";
}
var sorted=ASSETS.slice().sort(function(x,y){ return y.d-x.d; });
var g=document.getElementById('gainers'), f=document.getElementById('fallers');
if(g) g.innerHTML=sorted.slice(0,4).map(moverRow).join('');
if(f) f.innerHTML=sorted.slice(-3).reverse().map(moverRow).join('');
var cs=document.getElementById('coachSpark');
if(cs) cs.innerHTML=spark(true,320,64).replace("class='spark'","class='spark' style='height:64px'");

function updateSupplyCard(){
  var a=ASSETS[sel];
  if(!a) return;
  var s=FT.getState();
  var h=s.holdings[a.t];
  var heldFans=Math.round(10000000*(a.h/100));
  var dashoffset=Math.round(264*(1-a.h/100));

  var elHeld=document.getElementById('spHeld');
  if(elHeld) elHeld.textContent=fmt(heldFans);

  var elRing=document.getElementById('spRing');
  if(elRing) elRing.setAttribute('stroke-dashoffset', dashoffset);

  var elPct=document.getElementById('spPct');
  if(elPct) elPct.textContent=a.h.toFixed(1)+'% of 10,000,000';

  var elYour=document.getElementById('spYourHolding');
  if(elYour) elYour.textContent=h?fmt(h.shares)+' shares':'0 shares';

  var elAvg=document.getElementById('spAvgEntry');
  if(elAvg) elAvg.textContent=h?h.avg.toFixed(2):'—';

  var elUn=document.getElementById('spUnrealised');
  if(elUn){
    if(h && h.shares>0){
      var diff=(a.p-h.avg)*h.shares;
      elUn.textContent=(diff>=0?'+':'')+fmt(Math.round(diff));
      elUn.className='up '+(diff>=0?'up':'down');
    } else {
      elUn.textContent='—';
      elUn.className='num';
    }
  }

  var elClub=document.getElementById('spInClub');
  if(elClub){
    if(h && h.inClub){
      elClub.textContent=s.club.name+' · '+h.inClub;
    } else {
      elClub.textContent=a.c?'Not appointed':'Not in active XI';
    }
  }
}

var ro=document.getElementById('reviewOrderBtn');
if(ro){
  ro.addEventListener('click',function(){
    var a=ASSETS[sel];
    var qtyVal=parseInt((document.getElementById('qty').value||'0').replace(/[^0-9]/g,''),10)||0;
    if(qtyVal<=0){
      showToast("Please enter a valid share quantity greater than 0.", "error");
      return;
    }
    var sub=qtyVal*a.p, fee=sub*0.004;
    var tot=Math.round(side==='buy'?sub+fee:sub-fee);
    var s=FT.getState();
    var curH=s.holdings[a.t];

    var modalHtml='' +
      '<h3 class="ft-modal-title">Confirm '+(side==='buy'?'Buy Order':'Sell Order')+'</h3>' +
      '<p class="ft-modal-desc">Review execution details against the live Fantrade order book.</p>' +
      '<div class="ft-modal-card">' +
        '<div class="m-row"><span>Action</span><b style="color:'+(side==='buy'?'var(--lime)':'var(--amber)')+'">'+side.toUpperCase()+'</b></div>' +
        '<div class="m-row"><span>Asset</span><b>'+a.t+' ('+a.n+')</b></div>' +
        '<div class="m-row"><span>Quantity</span><b>'+fmt(qtyVal)+' shares</b></div>' +
        '<div class="m-row"><span>Price per Share</span><b>'+a.p.toFixed(2)+' $FTR</b></div>' +
        '<div class="m-row"><span>Subtotal</span><b>'+fmt(Math.round(sub))+' $FTR</b></div>' +
        '<div class="m-row"><span>Exchange Fee (0.4%)</span><b>'+fmt(Math.round(fee))+' $FTR</b></div>' +
        '<div class="m-row total"><span>Total '+(side==='buy'?'Cost':'Payout')+'</span><b style="color:'+(side==='buy'?'var(--lime)':'var(--amber)')+'">'+fmt(tot)+' $FTR</b></div>' +
      '</div>' +
      '<div class="ft-modal-card">' +
        '<div class="m-row"><span>Your Available Balance</span><b>'+fmt(s.wallet.balance)+' $FTR</b></div>' +
        '<div class="m-row"><span>Balance After Order</span><b style="color:'+(side==='buy'&&s.wallet.balance<tot?'var(--red)':'var(--ink)')+'">' +
          (side==='buy'?fmt(s.wallet.balance-tot):fmt(s.wallet.balance+tot))+' $FTR</b></div>' +
        '<div class="m-row"><span>Current Position</span><b>'+(curH?fmt(curH.shares):'0')+' shares</b></div>' +
      '</div>' +
      '<div style="display:flex;gap:10px;margin-top:20px">' +
        '<button class="btn btn-lime" id="confirmTradeBtn" type="button" style="flex:1;justify-content:center">Execute '+side.toUpperCase()+'</button>' +
        '<button class="btn btn-glass" id="cancelTradeBtn" type="button" style="flex:1;justify-content:center">Cancel</button>' +
      '</div>';

    openModal(modalHtml);

    var cancelBtn=document.getElementById('cancelTradeBtn');
    if(cancelBtn) cancelBtn.addEventListener('click', closeModal);

    var confBtn=document.getElementById('confirmTradeBtn');
    if(confBtn) confBtn.addEventListener('click',function(){
      try{
        var res=FT.executeTrade(side, a.t, a.n, qtyVal, a.p, a.c);
        showToast("Trade executed! "+(side==='buy'?'Bought ':'Sold ')+fmt(qtyVal)+" "+a.t+" shares.", "success");
        closeModal();
        updateSupplyCard();
        calc();
      }catch(err){
        showToast(err.message, "error");
      }
    });
  });
}

window.addEventListener('fantrade:statechange',function(){
  updateSupplyCard();
});

var origLoadTicket=loadTicket;
loadTicket=function(){
  origLoadTicket();
  updateSupplyCard();
};

rows(); loadTicket(); liveTicks('.mrow');
"""
page("exchange.html", "Exchange — Fantrade", "".join(ex), EX_JS, EX_CSS, app=True)


# ══════════════════════════════════════════════════════════
# 3. DREAM CLUBS
# ══════════════════════════════════════════════════════════
CL_CSS = """
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

cl = []
cl.append(T('<header class="phead"><div class="wrap">'
          '<span class="pill" data-reveal>@@ Dream Clubs</span><h1 data-reveal>Zero FC</h1>'
          '<p class="lede" data-reveal>Your club is a portfolio wearing a badge. Everything in the squad is owned '
          'outright, and its value moves with the market underneath it.</p>'
          '<div class="statbar" data-reveal><div>@@ Club value <b>245,800 $FTR</b></div>'
          '<div>@@ Rank <b>#124 of 48,206</b></div><div>@@ Club FP <b>8,420</b></div>'
          '<div>@@ Boost <b>+15%</b></div></div></div></header>', ic("crest", "ic"), ic("coin", "ic"), ic("trophy", "ic"), ic("bolt", "ic"), ic("target", "ic")))

cl.append(T('<main><section style="padding-top:30px"><div class="wrap"><div class="bento">'
          '<div class="bezel c7" data-reveal><div class="core pitch" id="pitchMount"></div></div>'
          '<div class="c5" style="display:flex;flex-direction:column;gap:16px">'
          '<div class="bezel" data-reveal><div class="core pad"><div class="k-label">Club value</div>'
          '<div class="value-big">245,800 <small>$FTR</small></div>'
          '<div class="delta">▲ 12,400 this week</div>'
          '<div style="margin-top:22px;border-top:1px solid var(--hair);padding-top:6px">'
          '<div class="b-row"><span>Starting XI</span><b>180,600</b></div>'
          '<div class="b-row"><span>Bench (4)</span><b>45,200</b></div>'
          '<div class="b-row"><span>Coach $Arteta</span><b>20,000</b></div>'
          '<div class="b-row total"><span>Club value</span><b>245,800</b></div></div>'
          '<div style="margin-top:18px">@@</div></div></div>'
          '<div class="mini-grid" data-reveal>'
          '<div class="mini"><div class="k">Last round</div><div class="v lime">312</div></div>'
          '<div class="mini"><div class="k">Season FP</div><div class="v">8,420</div></div>'
          '<div class="mini"><div class="k">Win rate</div><div class="v">62%</div></div>'
          '<div class="mini"><div class="k">$FTR earned</div><div class="v amber">19,640</div></div></div>'
          '<div class="bezel" data-reveal style="flex:1"><div class="core pad-sm">'
          '<div class="k-label">Club value · last 8 rounds</div><div id="valChart"></div></div></div>'
          '</div></div></div></section>', btn("Enter this club in FanPlay", "btn-lime btn-sm", "fanplay.html")))

# builder
cl.append(T('<section id="builder"><div class="wrap"><div class="sec-head" data-reveal>'
          '<span class="pill">@@ Club builder</span><h2>Build it in<br>eight steps</h2>'
          '<p class="lede">Identity first, squad second. Every slot you fill checks your wallet before it accepts a '
          'name — change the formation and the shape rebuilds around the players you own.</p></div>', ic("formation", "ic")))
cl.append(T('<div class="bento"><div class="bezel c5" data-reveal><div class="core pad">'
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
cl.append('<div class="bezel c7" data-reveal><div class="core pitch" id="builderPitch"></div></div></div></div></section>')

# chemistry
cl.append(T('<section id="chem"><div class="wrap"><div class="sec-head" data-reveal>'
          '<span class="pill amber">@@ Club chemistry</span><h2>Why one squad<br>boosts harder</h2>'
          '<p class="lede">Two managers can own the same eleven players and score differently. Chemistry rewards the '
          'club that is actually coherent, not just expensive.</p></div><div class="bento">', ic("target", "ic")))
for icon, t, d, c, am in [("whistle", "Coach compatibility", "A coach whose real-world shape matches your formation contributes his full modifier. Mismatch it and the bonus shrinks.", "c4", "am"),
                          ("pitch", "Natural positions", "Players scored in the role they actually play carry full weight. A winger at left-back will cost you.", "c4", ""),
                          ("subs", "Squad completeness", "A full bench is worth more than four names and a gap, because it guarantees cover on matchday.", "c4", ""),
                          ("flag", "Players actually starting", "Chemistry reads real team news. A squad of confirmed starters outperforms a squad of big names on the bench.", "c6", ""),
                          ("clock", "Club consistency", "Clubs that hold their shape across rounds build a consistency bonus. Constant teardowns reset it.", "c6", "")]:
    cl.append(T('<div class="bezel tight @@" data-reveal><div class="core pad f"><span class="ibox @@">@@</span>'
              '<h4>@@</h4><p>@@</p></div></div>', c, am, ic(icon, "ic-lg"), t, d))
cl.append('</div></div></section>')

# leaderboard
LB = [("1", "Vanguard XI", "#C4F82A", "612,400", "14,980", "+19%"),
      ("2", "Casa Blanca FC", "#E8E8E8", "588,100", "14,220", "+18%"),
      ("3", "Northside Union", "#4DA3FF", "540,750", "13,640", "+17%"),
      ("4", "Estádio Nove", "#FF6A1F", "498,300", "12,905", "+16%"),
      ("124", "Zero FC", "#C4F82A", "245,800", "8,420", "+15%")]
cl.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
          '<span class="pill">@@ Club table</span><h2>Where your club<br>sits this season</h2></div>'
          '<div class="bezel" data-reveal><div class="core">'
          '<div class="lb h"><span>Rank</span><span>Club</span><span>Club value</span><span>Season FP</span><span>Boost</span></div>', ic("trophy", "ic")))
for r, n, col, v, fp, b in LB:
    cl.append(T('<div class="lb@@"@@><span class="rank">@@</span><span class="cn">'
              '<span class="mini-crest" style="background:linear-gradient(160deg,@@,rgba(0,0,0,.4))"></span>@@</span>'
              '<span class="num">@@</span><span class="num">@@</span><span class="num up">@@</span></div>',
              " you" if n == "Zero FC" else "", ' id="myClubLbRow"' if n == "Zero FC" else "", r, col, n, v, fp, b))
cl.append('</div></div></div></section></main>')

CL_JS = PITCH_JS + r"""
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

function syncClubUI(){
  var s=FT.getState();
  var c=s.club;
  curShape=c.formation||'4-3-3';
  curColor=c.color||'#C4F82A';

  var ni=document.getElementById('clubNameInput');
  if(ni) ni.value=c.name;
  var si=document.getElementById('clubStadiumInput');
  if(si) si.value=c.stadium;

  document.querySelectorAll('h1').forEach(function(h){
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
      var name=(document.getElementById('clubNameInput').value||'Zero FC').trim();
      var stadium=(document.getElementById('clubStadiumInput').value||'Emirates of the North').trim();

      FT.saveClub({
        name: name,
        stadium: stadium,
        formation: curShape,
        color: curColor,
        boost: 15.0
      });

      syncClubUI();
      showToast("Club '"+name+"' ("+curShape+") saved successfully!", "success");
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
# 4. FANPLAY
# ══════════════════════════════════════════════════════════
FP_CSS = """
.fp-body{display:grid;grid-template-columns:1fr 1fr}
.fp-left{padding:38px 34px;border-right:1px solid var(--hair)}
.fp-right{padding:38px 34px;background:rgba(255,255,255,.018)}
.fp-sel{display:flex;align-items:center;gap:16px;border:1px solid var(--hair);border-radius:20px;padding:18px 20px;
  margin-bottom:28px;background:rgba(255,255,255,.03);box-shadow:var(--inset)}
.fp-sel .nm{font-family:Archivo;font-variation-settings:'wdth' 120,'wght' 800;text-transform:uppercase;font-size:18px}
.fp-sel .sub{font-weight:600;font-size:9.5px;color:var(--faint);margin:5px 0 0;letter-spacing:.14em;text-transform:uppercase}
.fp-sel .right{margin-left:auto;text-align:right;font-weight:600;font-size:9px;color:var(--faint);letter-spacing:.14em;text-transform:uppercase}
.mkt-note{margin-top:22px;font-size:13.5px;font-weight:300;color:var(--dim);min-height:46px}
.calc .cr{display:flex;justify-content:space-between;padding:13px 0;border-bottom:1px solid rgba(255,255,255,.055);font-size:12.5px;color:var(--dim)}
.calc .cr b{color:var(--ink);font-weight:400;font-family:'JetBrains Mono',monospace}
.calc .cr.boost b{color:var(--amber)}
.tier{height:100%}
.tier .top{display:flex;align-items:center;gap:14px;margin-bottom:16px}
.tier h4{font-size:19px}
.tier .x{margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:20px;color:var(--lime)}
.tier p{font-size:13px;font-weight:300;color:var(--dim);margin:0 0 16px}
.risk{height:4px;border-radius:99px;background:rgba(255,255,255,.07);overflow:hidden}
.risk i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#C4F82A,#FF6A1F)}
.risk-k{display:flex;justify-content:space-between;font-weight:600;font-size:9px;letter-spacing:.14em;color:var(--faint);margin-top:10px;text-transform:uppercase}
.fx{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:14px;align-items:center;padding:16px 24px;border-bottom:1px solid rgba(255,255,255,.05)}
.fx.h{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;border-bottom:1px solid var(--hair)}
.fx .team{display:flex;align-items:center;gap:11px;font-size:13px}
.fx .st{font-weight:600;font-size:9px;letter-spacing:.12em;padding:5px 11px;border-radius:999px;text-transform:uppercase;display:inline-block}
.st.live{background:rgba(196,248,42,.12);color:var(--lime);border:1px solid rgba(196,248,42,.3)}
.st.ft{background:rgba(255,255,255,.05);color:var(--dim);border:1px solid var(--hair)}
.st.soon{background:rgba(255,106,31,.1);color:var(--amber);border:1px solid rgba(255,106,31,.26)}
.rule{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:14px;padding:14px 24px;border-bottom:1px solid rgba(255,255,255,.05);font-size:13px}
.rule.h{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;border-bottom:1px solid var(--hair)}
.rule .num{color:var(--ink)}
.countdown{display:flex;gap:10px;margin-top:18px}
.cd{flex:1;text-align:center;border:1px solid var(--hair);border-radius:14px;padding:14px 6px;background:rgba(255,255,255,.03);box-shadow:var(--inset)}
.cd b{display:block;font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:300}
.cd span{font-weight:600;font-size:8.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase}
@media (max-width:1024px){.fp-body{grid-template-columns:1fr}.fp-left{border-right:0;border-bottom:1px solid var(--hair)}}
@media (max-width:768px){
  .fp-body{display:flex!important;flex-direction:column!important;width:100%!important;max-width:100%!important;min-width:0!important;box-sizing:border-box!important}
  .fp-left,.fp-right{width:100%!important;max-width:100%!important;min-width:0!important;padding:22px 16px!important;box-sizing:border-box!important}
  .fp-left{border-right:0!important;border-bottom:1px solid var(--hair)!important}
  .fx,.rule{grid-template-columns:1.4fr 1fr!important;padding:12px 14px!important;width:100%!important;box-sizing:border-box!important}
  .fx>*:nth-child(n+3),.rule>*:nth-child(n+3){display:none!important}
}
"""

fp = []
fp.append(T('<header class="phead"><div class="wrap">'
          '<span class="pill" data-reveal>@@ Matchday 07 · open</span><h1 data-reveal>FanPlay</h1>'
          '<p class="lede" data-reveal>Put what you own to work. Activate a single player or send your whole club out, '
          'pick how much risk you want, and let the real fixtures settle it.</p>'
          '<div class="statbar" data-reveal><div>@@ Window closes <b>Fri 18:30</b></div>'
          '<div>@@ Fixtures tracked <b>9 matches</b></div><div>@@ Your entries <b id="fpActiveCount">2 active</b></div></div>'
          '</div></header>', ic("bolt", "ic"), ic("clock", "ic"), ic("calendar", "ic"), ic("target", "ic")))

fp.append(T('<main><section style="padding-top:30px"><div class="wrap"><div class="bezel" data-reveal><div class="core">'
          '<div class="tabs" role="tablist" aria-label="FanPlay mode">'
          '<button class="tab" role="tab" id="tab-solo" aria-controls="pane" aria-selected="false" data-mode="solo">'
          '<span class="ibox">@@</span><div><b>Individual</b><span>Play one player you own</span></div></button>'
          '<button class="tab" role="tab" id="tab-club" aria-controls="pane" aria-selected="true" data-mode="club">'
          '<span class="ibox">@@</span><div><b>Dream Club</b><span>Play your whole club for a boost</span></div></button></div>', ic("boot", "ic-lg"), ic("crest", "ic-lg")))

fp.append(T('<div class="fp-body" id="pane" role="tabpanel" aria-labelledby="tab-club"><div class="fp-left">'
          '<div class="fp-sel"><span class="badge" id="selBadge">@@</span>'
          '<div><div class="nm" id="selName">Zero FC</div><p class="sub" id="selSub">4-3-3 · Coach $Arteta · XI + 4 bench</p></div>'
          '<div class="right">Ownership<br><span class="up">Verified</span></div></div>'
          '<div class="k-label">Select market</div><div class="markets" id="markets">', ic("crest", "ic")))
TIERS = [("Simple", 1, "Lowest variance. Goals, assists and clean sheets only — a good place to learn how settlement works.", 18),
         ("PRO", 1.4, "Adds key passes, duels won and expected goals to the scoring set.", 32),
         ("Elite", 2, "Full performance data with position-weighted scoring. The standard matchday market.", 50),
         ("Killer", 3, "High multiplier, punishing downside. Cards, misses and errors all count against you.", 68),
         ("Viynx Move", 4.5, "Momentum market. Scoring swings with live in-match movement across the whole round.", 84),
         ("Viynx Max", 7, "Maximum exposure. The largest payouts on Fantrade and the shortest odds of reaching them.", 100)]
for name, m, note, risk in TIERS:
    fp.append(T('<button class="mkt"@@ data-m="@@" data-note="@@">@@</button>', ' aria-pressed="true"' if name == "Elite" else ' aria-pressed="false"', m, note, name))
fp.append('</div><p class="mkt-note" id="mktNote">Full performance data with position-weighted scoring. The standard '
          'matchday market.</p><div style="border-top:1px solid var(--hair);padding-top:20px">'
          '<div class="b-row"><span>Settlement window</span><b>MD 07 · Fri 18:30</b></div>'
          '<div class="b-row"><span>Fixtures tracked</span><b id="fixtures">9 matches · 4 leagues</b></div>'
          '<div class="b-row"><span>Entry stake</span><b>2,500 $FTR</b></div></div></div>')

fp.append('<div class="fp-right"><div class="k-label">Projected round</div><div class="calc">'
          '<div class="cr"><span id="baseLabel">Club base points</span><b id="basePts">100 FP</b></div>'
          '<div class="cr"><span>Market multiplier</span><b id="multPts">×2.0</b></div>'
          '<div class="cr boost" id="boostRow"><span>Club boost — chemistry + coach</span><b>+15%</b></div>'
          '<div class="cr" id="capRow"><span>Captain $Bruno ×1.5</span><b>in base</b></div>'
          '<div class="out"><div class="k">Projected Fantrade Points</div><div class="v" id="fpOut">230</div>'
          '<div class="n" id="fpNote">Club mode · Elite · paid in $FTR at settlement</div></div></div>'
          + btn("Activate entry", tag="button", extra='id="activateEntryBtn" style="margin-top:20px;width:100%;justify-content:space-between"') +
          '<p style="font-size:13px;font-weight:300;color:var(--dim);margin-top:20px">Your club scores wherever its '
          'players are playing. The round closes on one clock, not one fixture.</p></div></div></div></div></div></section>')

# tiers
fp.append(T('<section id="tiers"><div class="wrap"><div class="sec-head" data-reveal>'
          '<span class="pill">@@ Market tiers</span><h2>Six ways to<br>take the round</h2>'
          '<p class="lede">Every tier scores the same match from a different data set. Higher tiers pay more because '
          'they count more of what can go wrong.</p></div><div class="bento">', ic("candle", "ic")))
icons = ["target", "chart", "shield", "bolt", "pulse", "trophy"]
spans = ["c4", "c4", "c4", "c4", "c4", "c4"]
for (name, m, note, risk), icon, c in zip(TIERS, icons, spans):
    fp.append(T('<div class="bezel tight @@" data-reveal><div class="core pad tier">'
              '<div class="top"><span class="ibox @@">@@</span><h4>@@</h4><span class="x">×@@</span></div>'
              '<p>@@</p><div class="risk"><i style="width:%d%"></i></div>'
              '<div class="risk-k"><span>Variance</span><span>@@</span></div></div></div>', c, "am" if risk > 60 else "", ic(icon, "ic-lg"), name, ("%g" % m), note, risk,
                 "Low" if risk < 40 else ("Medium" if risk < 70 else "High")))
fp.append('</div></div></section>')

# live board
FX = [("Arsenal v Chelsea", "live", "68'", "$Saka 42 FP"),
      ("Man Utd v Spurs", "live", "54'", "$Bruno 31 FP"),
      ("Man City v Everton", "live", "71'", "$Haaland 58 FP"),
      ("Real Madrid v Betis", "ft", "FT", "$Vinicius 44 FP"),
      ("Bayern v Leipzig", "soon", "19:30", "$Musiala —"),
      ("Barcelona v Sevilla", "soon", "21:00", "$Pedri —")]
fp.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
          '<span class="pill">@@ Live board</span><h2>Your club is alive<br>across nine matches</h2>'
          '<p class="lede">Fantrade does not require your eleven to be in the same fixture. Points accrue wherever your '
          'players are on the pitch, and the window settles them together.</p></div>'
          '<div class="bento"><div class="bezel c8" data-reveal><div class="core">'
          '<div class="fx h"><span>Fixture</span><span>Status</span><span>Contribution</span></div>', ic("pulse", "ic")))
for fixture, st, clock, contrib in FX:
    fp.append(T('<div class="fx"><span class="team">@@@@</span><span><span class="st @@">@@</span></span>'
              '<span class="num" style="font-size:12.5px;color:var(--dim)">@@</span></div>', ic("pitch", "ic-sm"), fixture, st, clock, contrib))
fp.append('</div></div><div class="c4" style="display:flex;flex-direction:column;gap:16px">'
          '<div class="bezel" data-reveal><div class="core pad"><div class="k-label">Round closes in</div>'
          '<div class="countdown"><div class="cd"><b id="cdH">04</b><span>Hours</span></div>'
          '<div class="cd"><b id="cdM">12</b><span>Mins</span></div><div class="cd"><b id="cdS">38</b><span>Secs</span></div></div>'
          '<p style="font-size:13px;font-weight:300;color:var(--dim);margin-top:18px">Entries lock at the window. '
          'Lineups, captain and market tier are fixed from that moment.</p></div></div>'
          '<div class="bezel" data-reveal style="flex:1"><div class="core pad"><div class="k-label">Running total</div>'
          '<div class="value-big" id="runFP">175 <small>FP</small></div>'
          '<div class="delta">Club mode · Elite · +15% boost applied at settlement</div>'
          '<div style="margin-top:20px"><div class="b-row"><span>Starters scoring</span><b>7 of 11</b></div>'
          '<div class="b-row"><span>Subs activated</span><b>1</b></div>'
          '<div class="b-row"><span>Coach modifier</span><b>+3.0%</b></div></div></div></div></div></div></div></section>')

# scoring rules
RULES = [("Goal", "6", "4", "9"), ("Assist", "4", "3", "6"), ("Clean sheet", "5", "1", "7"),
         ("Key pass", "—", "1", "2"), ("Duel won", "—", "0.5", "1"), ("Yellow card", "−1", "−1", "−3"),
         ("Big chance missed", "—", "−2", "−4")]
fp.append(T('<section id="rules"><div class="wrap"><div class="sec-head" data-reveal>'
          '<span class="pill amber">@@ Scoring</span><h2>What counts,<br>and for how much</h2>'
          '<p class="lede">Values shown for an outfield player. Goalkeepers and defenders carry their own weighting, '
          'and the coach scores on team outcomes rather than individual events.</p></div>'
          '<div class="bezel" data-reveal><div class="core">'
          '<div class="rule h"><span>Event</span><span>Simple</span><span>Elite</span><span>Viynx Max</span></div>', ic("check", "ic")))
for ev, a, b, c in RULES:
    fp.append(T('<div class="rule"><span>@@</span><span class="num">@@</span><span class="num">@@</span>'
              '<span class="num">@@</span></div>', ev, a, b, c))
fp.append('</div></div></div></section></main>')

FP_JS = r"""
var mode='club', mult=2, mktName='ELITE';
var tabs=document.querySelectorAll('.tab'), mkts=document.querySelectorAll('.mkt');
var CREST="<svg class='ic'><use href='#i-crest'/></svg>", BOOT="<svg class='ic'><use href='#i-boot'/></svg>";
function render(){
  var base=100, total=Math.round(base*(mode==='club'?1.15:1)*mult);
  document.getElementById('basePts').textContent=base+' FP';
  document.getElementById('multPts').textContent='×'+mult.toFixed(1);
  document.getElementById('fpOut').textContent=total.toLocaleString();
  document.getElementById('fpNote').textContent=(mode==='club'?'Club mode':'Individual mode')+' · '+mktName+' · paid in $FTR at settlement';
  document.getElementById('boostRow').style.display=mode==='club'?'flex':'none';
  document.getElementById('capRow').style.display=mode==='club'?'flex':'none';
  var club=mode==='club';
  var s=FT.getState();
  var cName=s.club.name||'Zero FC';
  var cForm=s.club.formation||'4-3-3';
  document.getElementById('selBadge').innerHTML=club?CREST:BOOT;
  document.getElementById('selName').textContent=club?cName:'$Bruno';
  document.getElementById('selSub').textContent=club?cForm+' · Coach $Arteta · XI + 4 bench':'Bruno Fernandes · 10,000 shares activated';
  document.getElementById('baseLabel').textContent=club?'Club base points':'Player base points';
  document.getElementById('fixtures').textContent=club?'9 matches · 4 leagues':'1 match · Man Utd v Spurs';
}
tabs.forEach(function(t){ t.addEventListener('click',function(){
  tabs.forEach(function(x){ x.setAttribute('aria-selected','false'); });
  t.setAttribute('aria-selected','true'); mode=t.dataset.mode;
  document.getElementById('pane').setAttribute('aria-labelledby',t.id); render(); }); });
mkts.forEach(function(m){ m.addEventListener('click',function(){
  mkts.forEach(function(x){ x.setAttribute('aria-pressed','false'); });
  m.setAttribute('aria-pressed','true'); mult=parseFloat(m.dataset.m); mktName=m.textContent.trim();
  document.getElementById('mktNote').textContent=m.dataset.note; render(); }); });
render();

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
    var base=100;
    var total=Math.round(base*(mode==='club'?1.15:1)*mult);
    var target=mode==='club'?s.club.name:'$Bruno';

    try{
      var entry=FT.activateFanPlayEntry({
        mode: mode,
        target: target,
        tier: mktName,
        mult: mult,
        stake: 2500,
        projectedFP: total
      });
      syncFPEntriesCount();
      showToast("Entry activated for "+target+" in "+mktName+" tier! 2,500 $FTR staked.", "success");
      actBtn.innerHTML="Entry Active · 2,500 $FTR Staked <span class='cap'><svg class='ic'><use href='#i-check'/></svg></span>";
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
window.addEventListener('fantrade:statechange', syncFPEntriesCount);

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
"""
page("fanplay.html", "FanPlay — Fantrade", "".join(fp), FP_JS, FP_CSS, app=True)

print("built:", sorted(os.listdir(OUT)))
