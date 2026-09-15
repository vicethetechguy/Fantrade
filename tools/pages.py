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

ex = [T('<main><section class="app-head" style="padding-bottom:14px"><div class="wrap">'
        '<span class="greet" data-reveal>Markets</span>'
        '<h1 data-reveal>Exchange</h1>'
        '<div class="searchbox" style="margin-top:16px;max-width:none" data-reveal>@@'
        '<input id="q" type="search" placeholder="Search a player, coach or ticker"></div>'
        '<div class="statbar" data-reveal>'
        '<div>@@ 24h volume <b>48.24M</b> $FTR</div>'
        '<div>@@ Listed assets <b>420</b></div>'
        '<div>@@ Top gainer <b id="topG">$Jackson</b></div>'
        '<div>@@ Your balance <b data-bind="balance">128,450</b></div>'
        '</div></div></section>',
        ic("search", "ic"), ic("candle", "ic"), ic("layers", "ic"), ic("bolt", "ic"), ic("coin", "ic"))]

ex.append('<section style="padding-top:8px"><div class="wrap"><div class="bento">')

ex.append('<div class="bezel c12" data-reveal><div class="core">'
          '<div style="padding:16px 16px 0"><div class="utabs" id="exSort">'
          '<button type="button" aria-pressed="true" data-s="all">All</button>'
          '<button type="button" aria-pressed="false" data-s="hot">Hot</button>'
          '<button type="button" aria-pressed="false" data-s="new">New</button>'
          '<button type="button" aria-pressed="false" data-s="gainers">Gainers</button>'
          '<button type="button" aria-pressed="false" data-s="losers">Losers</button>'
          '<button type="button" aria-pressed="false" data-s="volume">Volume</button>'
          '</div></div>'
          '<div style="padding:12px 16px 0"><div class="utabs sm" id="exKind" style="border-bottom:0">'
          '<button type="button" aria-pressed="true" data-f="all">All</button>'
          '<button type="button" aria-pressed="false" data-f="holdings">Holdings</button>'
          '<button type="button" aria-pressed="false" data-f="player">Players</button>'
          '<button type="button" aria-pressed="false" data-f="coach">Coaches</button>'
          '</div></div>'
          '<div class="mkhead"><span>Asset / Volume</span>'
          '<span style="text-align:right">Price $FTR</span>'
          '<span style="text-align:center">24h</span></div>'
          '<div id="mkt"></div>'
          '<div style="padding:12px 16px 20px;display:flex;align-items:center;gap:10px;flex-wrap:wrap">'
          '<span style="font-size:10.5px;color:var(--faint)" id="mktCount">—</span>'
          '</div>'
          '</div></div>')

ex.append('</div></div></section>')

# movers + coach index
ex.append('<section style="padding-top:6px"><div class="wrap"><div class="bento">')
ex.append(T('<div class="bezel c4" data-reveal><div class="core pad"><div class="k-label">@@ Top gainers · 24h</div>'
          '<div class="movers" id="gainers"></div></div></div>', ic("bolt", "ic-sm")))
ex.append(T('<div class="bezel c4" data-reveal><div class="core pad"><div class="k-label">@@ Fallers · 24h</div>'
          '<div class="movers" id="fallers"></div></div></div>', ic("pulse", "ic-sm")))
ex.append(T('<div class="bezel c4" data-reveal><div class="core pad"><div class="k-label">@@ Coach index</div>'
          '<div class="value-big">24.65 <small>$FTR</small></div>'
          '<div class="delta">▲ 2.1% · 186 coaches</div>'
          '<div style="margin-top:14px">@@</div>'
          '</div></div>', ic("whistle", "ic-sm"), '<div id="coachSpark"></div>'))
ex.append('</div></div></section>')
ex.append('</main>')

EX_JS = r"""
var kind = 'all', sort = 'all', q = '';
function fmt(n){ return n.toLocaleString('en-US'); }

function view(){
  var s = FT.getState();
  var list = ASSETS.map(function(a, i){ return [a, i]; }).filter(function(x){
    var a = x[0];
    if(kind === 'player' && a.c) return false;
    if(kind === 'coach' && !a.c) return false;
    if(kind === 'holdings' && !s.holdings[a.t]) return false;
    if(q && (a.t + ' ' + a.n).toLowerCase().indexOf(q) < 0) return false;
    return true;
  });
  if(sort === 'gainers') list.sort(function(a, b){ return b[0].d - a[0].d; });
  else if(sort === 'losers') list.sort(function(a, b){ return a[0].d - b[0].d; });
  else if(sort === 'volume' || sort === 'hot') list.sort(function(a, b){ return b[0].p - a[0].p; });
  else if(sort === 'new') list.reverse();
  return list;
}

function rows(){
  var s = FT.getState(), list = view();
  document.getElementById('mkt').innerHTML = list.map(function(x){
    var a = x[0], to = 'asset.html?a=' + encodeURIComponent(a.t);
    var h = s.holdings[a.t];
    return "<a class='mkrow' href='" + to + "' data-i='" + x[1] + "'>"
      + "<div class='pair'><span class='coin" + (a.c ? " am" : "") + "'>"
      + "<svg class='ic'><use href='#i-" + (a.c ? 'whistle' : 'boot') + "'/></svg></span>"
      + "<div style='min-width:0'><div class='sym'>" + a.t.replace('$', '')
      + "<em>/$FTR</em><span class='lev'>" + (a.c ? 'COACH' : 'SHARE') + "</span></div>"
      + "<div class='meta'>" + a.n + " · " + a.cap + (h ? " · you hold " + fmt(h.shares) : "")
      + "</div></div></div>"
      + "<div class='px'><span data-px>" + a.p.toFixed(2)
      + "</span><em>\u2248 \u00a3" + (a.p / 12.4).toFixed(2) + "</em></div>"
      + "<div><span class='pct" + (a.d >= 0 ? '' : ' down') + "' data-dx>"
      + (a.d >= 0 ? '+' : '') + a.d.toFixed(2) + "%</span></div></a>";
  }).join('') || "<div class='empty-state'><svg class='ic-xl' aria-hidden='true'><use href='#i-search'/></svg>"
    + "No assets match that search. Try a surname or a ticker like $Saka.</div>";
  document.getElementById('mktCount').textContent =
    list.length + ' of ' + ASSETS.length + ' assets · tap one for its market page';
}

document.querySelectorAll('#exKind button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#exKind button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true'); kind = b.dataset.f; rows();
  });
});
document.querySelectorAll('#exSort button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#exSort button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed','true'); sort = b.dataset.s; rows();
  });
});
var qi = document.getElementById('q');
if(qi) qi.addEventListener('input', function(){ q = qi.value.trim().toLowerCase(); rows(); });

function moverList(el, up){
  var list = ASSETS.slice().sort(function(a, b){ return up ? b.d - a.d : a.d - b.d; }).slice(0, 4);
  document.getElementById(el).innerHTML = list.map(function(a){
    return "<a class='arow' style='padding:9px 0' href='asset.html?a=" + encodeURIComponent(a.t) + "'>"
      + "<div class='who'><span class='coin" + (a.c ? " am" : "") + "'><svg class='ic'><use href='#i-"
      + (a.c ? 'whistle' : 'boot') + "'/></svg></span><div style='min-width:0'><div class='nm'>" + a.t
      + "</div><div class='qt'>" + a.n + "</div></div></div>"
      + "<div></div><div><div class='val'>" + a.p.toFixed(2) + "</div><div class='chg "
      + (a.d >= 0 ? 'up' : 'down') + "'>" + (a.d >= 0 ? '+' : '') + a.d.toFixed(1) + "%</div></div></a>";
  }).join('');
}
rows();
moverList('gainers', true);
moverList('fallers', false);
document.getElementById('topG').textContent =
  ASSETS.slice().sort(function(a, b){ return b.d - a.d; })[0].t;
var cs = document.getElementById('coachSpark');
if(cs) cs.innerHTML = spark(true, 240, 40);
liveTicks('.mkrow');
window.addEventListener('fantrade:statechange', rows);
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

ROUNDS = [("MD 27", "812", "18th", "w", "+6,200"), ("MD 26", "704", "41st", "w", "+4,100"),
          ("MD 25", "689", "63rd", "w", "+3,250"), ("MD 24", "512", "308th", "l", "-2,500"),
          ("MD 23", "548", "214th", "l", "-2,500")]

cl.append(T('<main><section style="padding-top:30px"><div class="wrap"><div class="bento">'
          '<div class="bezel c7" data-reveal><div class="core">'
          '<div style="padding:20px 22px 0"><div class="tabstrip" id="clTabs" role="tablist">'
          '<button type="button" role="tab" aria-pressed="true" data-p="lineups">Line-ups</button>'
          '<button type="button" role="tab" aria-pressed="false" data-p="position">League position</button>'
          '<button type="button" role="tab" aria-pressed="false" data-p="form">Form &amp; results</button>'
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

cl.append(T('<div class="bezel c12" data-reveal><div class="core pad">'
          '<div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">'
          '<span class="ibox">@@</span>'
          '<div style="min-width:0"><div style="font-family:Archivo;'
          'font-variation-settings:\'wdth\' 120,\'wght\' 800;text-transform:uppercase;font-size:18px">'
          'Rebuild the club</div>'
          '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:6px 0 0;line-height:1.6;'
          'max-width:60ch">Name, crest, coach, shape and every slot in the eleven — eight steps, and the '
          'shape rebuilds around what you own.</p></div>'
          '<span style="margin-left:auto">@@</span></div></div></div>',
          ic("formation", "ic-lg"),
          btn("Open the club builder", href="club-builder.html")))
cl.append('</div></div></section></main>')

CL_JS = PITCH_JS + r"""
document.querySelectorAll('#clTabs button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#clTabs button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed', 'true');
    document.querySelectorAll('[data-pane]').forEach(function(p){
      p.classList.toggle('on', p.dataset.pane === b.dataset.p);
    });
  });
});
(function(){
  var r = document.getElementById('clRung');
  if(r) r.textContent = '#' + FT.getState().club.rank;
})();

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
# CLUB BUILDER
# ══════════════════════════════════════════════════════════
# builder
bd = [T('<main><section class="app-head" style="padding-bottom:24px"><div class="wrap">'
        '<div data-reveal>@@</div>'
        '<span class="pill" style="margin-top:20px" data-reveal>@@ Club builder</span>'
        '<h1 data-reveal>Build it in<br>eight steps</h1>'
        '<p class="lede" data-reveal>Identity first, squad second. Every slot you fill checks your wallet '
        'before it accepts a name — change the formation and the shape rebuilds around the players you own.</p>'
        '</div></section>',
        crumb("clubs.html", "Back to the club"), ic("formation", "ic"))]
bd.append('<section style="padding:6px 0 130px"><div class="wrap">')
bd.append(T('<div class="bento"><div class="bezel c5" data-reveal><div class="core pad">'
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
bd.append('<div class="bezel c7" data-reveal><div class="core pitch" id="builderPitch"></div></div></div></div></section>')

bd.append('</main>')

page("club-builder.html", "Club builder — Fantrade", "".join(bd), CL_JS, CL_CSS, app=True)




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
          '<div class="statbar" data-reveal><div>@@ Window closes <b>Fri 18:30</b></div>'
          '<div>@@ Fixtures tracked <b>9 matches</b></div><div>@@ Your entries <b id="fpActiveCount">2 active</b></div></div>'
          '</div></header>', ic("bolt", "ic"), ic("clock", "ic"), ic("calendar", "ic"), ic("target", "ic")))

fp.append(T('<main><section style="padding-top:30px"><div class="wrap"><div class="bezel" data-reveal><div class="core">'
          '<div class="tabs" role="tablist" aria-label="FanPlay mode">'
          '<button class="tab" role="tab" id="tab-solo" aria-controls="pane" aria-selected="false" data-mode="solo">'
          '<span class="ibox">@@</span><div><b>Individual</b><span>One player</span></div></button>'
          '<button class="tab" role="tab" id="tab-club" aria-controls="pane" aria-selected="true" data-mode="club">'
          '<span class="ibox">@@</span><div><b>Dream Club</b><span>Whole club · +15%</span></div></button></div>', ic("boot", "ic-lg"), ic("crest", "ic-lg")))

fp.append(T('<div class="fp-body" id="pane" role="tabpanel" aria-labelledby="tab-club"><div class="fp-left">'
          '<div class="fp-sel"><span class="badge" id="selBadge">@@</span>'
          '<div><div class="nm" id="selName">Zero FC</div><p class="sub" id="selSub">4-3-3 · Coach $Arteta · XI + 4 bench</p></div>'
          '<div class="right">Ownership<br><span class="up">Verified</span></div></div>'
          '<div class="k-label">Select market</div><div class="markets" id="markets">', ic("crest", "ic")))
TIERS = [("Simple", 1, "Goals, assists and clean sheets.", 18),
         ("PRO", 1.4, "Adds key passes, duels won and expected goals.", 32),
         ("Elite", 2, "Full performance data, position-weighted.", 50),
         ("Killer", 3, "Elite scoring plus cards, misses and errors against you.", 68),
         ("Viynx Move", 4.5, "Scoring swings with live in-match movement.", 84),
         ("Viynx Max", 7, "Every event counts, at maximum weight.", 100)]
for name, m, note, risk in TIERS:
    fp.append(T('<button class="mkt"@@ data-m="@@" data-note="@@">@@</button>', ' aria-pressed="true"' if name == "Elite" else ' aria-pressed="false"', m, note, name))
fp.append('</div><p class="mkt-note" id="mktNote">Full performance data, position-weighted.</p>'
          '<div style="border-top:1px solid var(--hair);padding-top:20px">'
          '<div class="b-row"><span>Settlement window</span><b>MD 07 · Fri 18:30</b></div>'
          '<div class="b-row"><span>Fixtures tracked</span><b id="fixtures">9 matches · 4 leagues</b></div>'
          '<div class="b-row"><span>Entry stake</span><b>2,500 $FTR</b></div></div></div>')

fp.append('<div class="fp-right"><div class="k-label">Projected round</div><div class="calc">'
          '<div class="cr"><span id="baseLabel">Club base points</span><b id="basePts">100 FP</b></div>'
          '<div class="cr"><span>Market multiplier</span><b id="multPts">×2.0</b></div>'
          '<div class="cr boost" id="boostRow"><span>Club boost</span><b>+15%</b></div>'
          '<div class="cr" id="capRow"><span>Captain $Bruno ×1.5</span><b>in base</b></div>'
          '<div class="out"><div class="k">Projected Fantrade Points</div><div class="v" id="fpOut">230</div>'
          '<div class="n" id="fpNote">Club mode · Elite</div></div></div>'
          + btn("Activate entry", tag="button", extra='id="activateEntryBtn" style="margin-top:20px;width:100%;justify-content:space-between"') +
          '</div></div></div></div></div></section>')

# ── matchday board ────────────────────────────────────────────────
# (fid, home, home colour, home score, away, away colour, away score,
#  status, clock, your asset on the pitch)
MATCHDAY = [
    ("eng", "Premier League", "Matchweek 7", [
        ("m-ars", "Arsenal", "ARS", "#EF0107", "2", "Chelsea", "CHE", "#034694", "1", "live", "68'", "$Saka · 42 FP"),
        ("m-mci", "Man City", "MCI", "#6CABDD", "3", "Everton", "EVE", "#003399", "0", "live", "71'", "$Haaland · 58 FP"),
        ("m-mun", "Man United", "MUN", "#DA291C", "1", "Tottenham", "TOT", "#8f95a3", "1", "live", "54'", "$Bruno · 31 FP"),
        ("m-new", "Newcastle", "NEW", "#8f95a3", "–", "Brighton", "BHA", "#0057B8", "–", "soon", "19:30", ""),
    ]),
    ("esp", "La Liga", "Jornada 7", [
        ("m-rma", "Real Madrid", "RMA", "#FEBE10", "4", "Real Betis", "BET", "#00954C", "0", "ft", "FT", "$Vinicius · 44 FP"),
        ("m-bar", "Barcelona", "BAR", "#A50044", "–", "Sevilla", "SEV", "#D4021D", "–", "soon", "21:00", "$Pedri"),
    ]),
    ("ger", "Bundesliga", "Spieltag 6", [
        ("m-bay", "Bayern", "FCB", "#DC052D", "2", "RB Leipzig", "RBL", "#DD0741", "2", "ht", "HT", "$Musiala · 19 FP"),
    ]),
    ("ita", "Serie A", "Play-offs", [
        ("m-sud", "Sudtirol", "SUD", "#8f95a3", "1", "Bari", "BAR", "#C8102E", "1", "aet", "AET", ""),
        ("m-bar2", "Barnsley", "BAR", "#D2122E", "–", "Sheff Wednesday", "SHW", "#0057B8", "–", "soon", "20:30", ""),
    ]),
]

fp.append(T('<section id="board" style="padding-top:40px"><div class="wrap">'
            '<div class="rowhead" data-reveal style="margin-bottom:22px">'
            '<span class="ibox">@@</span>'
            '<div><div style="font-family:Archivo;font-variation-settings:\'wdth\' 120,\'wght\' 800;'
            'text-transform:uppercase;font-size:20px">Live board</div>'
            '<div class="sub-line">Your eleven, wherever they are playing this window</div></div></div>'
            '<div class="bento"><div class="bezel c8" data-reveal><div class="core">', ic("pulse", "ic-lg")))

# date strip
fp.append(T('<div style="padding:24px 22px 18px">'
            '<div class="datestrip">'
            '<button class="livetgl" type="button" id="liveOnly" aria-pressed="false">'
            '<span class="dot-live"></span>Live only</button>'
            '<div class="dates" id="dateStrip">'
            '<span class="nudge">@@</span>'
            '<button type="button" aria-pressed="false"><small>Sun</small><b>28 Sep</b></button>'
            '<button type="button" aria-pressed="true"><small>Today</small><b>29 Sep</b></button>'
            '<button type="button" aria-pressed="false"><small>Tue</small><b>30 Sep</b></button>'
            '<span class="nudge">@@</span></div>'
            '<button class="bell" type="button" id="calBtn" aria-label="Open the full calendar" '
            'style="border-radius:14px">@@</button>'
            '</div></div>',
            "‹", "›", ic("calendar", "ic")))

# featured match
fp.append(T('<div style="padding:0 22px">'
            '<div class="feat islive" id="featCard">'
            '<div class="feat-top"><button type="button" id="featHide">Hide</button>'
            '<div class="mid"><b>Emirates Stadium</b><span>Matchweek 7 · your biggest exposure</span></div>'
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
fp.append('<div id="boardList">')
for code, comp, sub, fixtures in MATCHDAY:
    fp.append(T('<div class="comp">@@<div><b>@@</b><span>@@</span></div>'
                '<a class="more" href="#board">All fixtures @@</a></div>',
                flag(code), comp, sub, ic("arrow", "ic-sm")))
    for fid, home, hsh, hc, hs, away, ash, ac, a_s, st, clock, mine in fixtures:
        hw = hs.isdigit() and a_s.isdigit() and int(hs) > int(a_s)
        aw = hs.isdigit() and a_s.isdigit() and int(a_s) > int(hs)
        fp.append(T('<div class="fixt@@" data-fid="@@" data-live="@@">'
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
fp.append('</div>')

fp.append('<div style="padding:16px 22px 26px;display:flex;align-items:center;gap:12px;flex-wrap:wrap">'
          '<span style="font-size:11.5px;color:var(--faint);font-weight:300" id="boardNote">'
          '9 fixtures · 4 with your assets</span></div>')

fp.append('</div></div>')

# side column — countdown + running total
fp.append('<div class="c4" style="display:flex;flex-direction:column;gap:16px">'
          '<div class="bezel" data-reveal><div class="core pad"><div class="k-label">Round closes in</div>'
          '<div class="countdown"><div class="cd"><b id="cdH">04</b><span>Hours</span></div>'
          '<div class="cd"><b id="cdM">12</b><span>Mins</span></div>'
          '<div class="cd"><b id="cdS">38</b><span>Secs</span></div></div>'
          '</div></div>'
          '<div class="bezel" data-reveal style="flex:1"><div class="core pad"><div class="k-label">Running total</div>'
          '<div class="value-big" id="runFP">175 <small>FP</small></div>'
          '<div class="delta">Club mode · Elite · +15%</div>'
          '<div style="margin-top:20px"><div class="b-row"><span>Starters scoring</span><b>7 of 11</b></div>'
          '<div class="b-row"><span>Subs activated</span><b>1</b></div>'
          '<div class="b-row"><span>Coach modifier</span><b>+3.0%</b></div>'
          '<div class="b-row total"><span>Followed fixtures</span><b id="favCount">1</b></div></div>'
          '<div class="k-label" style="margin-top:26px">Club form</div>'
          '<div class="form5" style="margin-bottom:12px">'
          '<i class="l">L</i><i class="l">L</i><i class="w">W</i><i class="w">W</i><i class="w">W</i></div>'
          '</div></div></div></div></div></section>')

fp.append('</main>')

FP_JS = r"""
var mode='club', mult=2, mktName='ELITE';
var tabs=document.querySelectorAll('.tab'), mkts=document.querySelectorAll('.mkt');
var CREST="<svg class='ic'><use href='#i-crest'/></svg>", BOOT="<svg class='ic'><use href='#i-boot'/></svg>";
function render(){
  var base=100, total=Math.round(base*(mode==='club'?1.15:1)*mult);
  document.getElementById('basePts').textContent=base+' FP';
  document.getElementById('multPts').textContent='×'+mult.toFixed(1);
  document.getElementById('fpOut').textContent=total.toLocaleString();
  document.getElementById('fpNote').textContent=(mode==='club'?'Club mode':'Individual mode')+' · '+mktName;
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
page("fanplay.html", "FanPlay — Fantrade", "".join(fp), FP_JS, FP_CSS, app=True)

print("built:", sorted(os.listdir(OUT)))
