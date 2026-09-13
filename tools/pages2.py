# -*- coding: utf-8 -*-
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


def page(fname, title, body, js="", css=""):
    html = (head(title, css) + atmosphere() + nav(title.split(" — ")[0]) +
            body + footer() + "<script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
    open(os.path.join(OUT, fname), "w", encoding="utf-8").write(html)


# ══════════════════════════════════════════════════════════
# $FTR
# ══════════════════════════════════════════════════════════
FTR_CSS = """
.balance{font-family:'JetBrains Mono',monospace;font-weight:200;font-size:clamp(46px,6vw,74px);
  letter-spacing:-.045em;line-height:1;margin:14px 0 10px}
.balance small{font-size:18px;color:var(--faint);letter-spacing:0;font-weight:300}
.split{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:26px}
.split div{border:1px solid var(--hair);border-radius:16px;padding:18px;background:rgba(255,255,255,.03);box-shadow:var(--inset)}
.split .k{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase}
.split .v{font-family:'JetBrains Mono',monospace;font-size:20px;margin-top:8px;font-weight:300}
.conv{display:flex;align-items:center;gap:12px;margin:6px 0 4px}
.conv .eq{color:var(--faint);font-size:13px}
.tx{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:14px;padding:15px 24px;
  border-bottom:1px solid rgba(255,255,255,.05);font-size:13px;align-items:center}
.tx.h{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;border-bottom:1px solid var(--hair)}
.tx .w{display:flex;align-items:center;gap:11px}
.dist{display:flex;align-items:center;gap:26px;flex-wrap:wrap}
.dist .key{display:flex;flex-direction:column;gap:12px;flex:1;min-width:180px}
.dist .kr{display:flex;align-items:center;gap:11px;font-size:13px;color:var(--dim)}
.dist .kr i{width:10px;height:10px;border-radius:3px;display:block;flex:none}
.dist .kr b{margin-left:auto;font-family:'JetBrains Mono',monospace;color:var(--ink);font-weight:400}
@media (max-width:768px){.split{grid-template-columns:1fr}
 .tx{grid-template-columns:1.4fr 1fr;padding:13px 16px}.tx>*:nth-child(n+3){display:none}}
"""

f = []
f.append(T('<header class="phead"><div class="wrap">'
           '<span class="pill" data-reveal>@@ The platform currency</span><h1 data-reveal>$FTR</h1>'
           '<p class="lede" data-reveal>One balance funds everything. You buy shares with $FTR, pay swap fees in $FTR, '
           'stake FanPlay entries in $FTR, and every settled round pays back into the same wallet.</p>'
           '<div class="statbar" data-reveal><div>@@ Your balance <b>128,450 $FTR</b></div>'
           '<div>@@ Locked in entries <b>5,000</b></div><div>@@ Earned this season <b>19,640</b></div></div>'
           '</div></header>',
           ic("coin", "ic"), ic("wallet", "ic"), ic("lock", "ic"), ic("trophy", "ic")))

f.append('<main><section style="padding-top:30px"><div class="wrap"><div class="bento">')
f.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
           '<div class="k-label">Available balance</div>'
           '<div class="balance">128,450<small> $FTR</small></div>'
           '<div class="delta">▲ 6,200 this week from settled rounds</div>'
           '<div class="split"><div><div class="k">Locked in entries</div><div class="v">5,000</div></div>'
           '<div><div class="k">Held in assets</div><div class="v">402,610</div></div></div>'
           '<div style="display:flex;gap:10px;margin-top:22px;flex-wrap:wrap">@@@@</div></div></div>',
           btn("Deposit", extra='style="flex:1;justify-content:space-between"'),
           btn("Withdraw", "btn-glass", extra='style="flex:1;justify-content:space-between"')))

f.append(T('<div class="bezel c4" data-reveal><div class="core pad">'
           '<div class="k-label">Convert</div>'
           '<div class="field"><label>You pay</label><input id="fiat" value="1,000" inputmode="numeric"></div>'
           '<div class="conv">@@<span class="eq">1 GBP = 12.40 $FTR · rate held for 30s</span></div>'
           '<div class="field"><label>You receive</label><input id="ftr" value="12,400" readonly></div>'
           '<div class="quick"><button data-f="100">£100</button><button data-f="500">£500</button>'
           '<button data-f="1000">£1,000</button><button data-f="5000">£5,000</button></div>'
           '<div class="line"><span>Conversion fee (0.5%)</span><b id="cFee">62</b></div>'
           '<div class="line"><span>Credited</span><b id="cNet">12,338 $FTR</b></div>'
           '@@</div></div>',
           ic("swap", "ic"), btn("Convert to $FTR", tag="button",
                                 extra='style="margin-top:18px;width:100%;justify-content:space-between"')))

f.append(T('<div class="bezel c3" data-reveal><div class="core pad">'
           '<div class="k-label">Circulating supply</div>'
           '<div class="dist" style="margin-top:10px">'
           '<svg viewBox="0 0 42 42" style="width:120px;height:120px;flex:none">'
           '<circle cx="21" cy="21" r="15.9" fill="none" stroke="rgba(255,255,255,.07)" stroke-width="5"/>'
           '<circle cx="21" cy="21" r="15.9" fill="none" stroke="#C4F82A" stroke-width="5" '
           'stroke-dasharray="46 54" stroke-dashoffset="25" transform="rotate(-90 21 21)"/>'
           '<circle cx="21" cy="21" r="15.9" fill="none" stroke="#FF6A1F" stroke-width="5" '
           'stroke-dasharray="28 72" stroke-dashoffset="79" transform="rotate(-90 21 21)"/>'
           '<circle cx="21" cy="21" r="15.9" fill="none" stroke="rgba(255,255,255,.28)" stroke-width="5" '
           'stroke-dasharray="14 86" stroke-dashoffset="51" transform="rotate(-90 21 21)"/></svg></div>'
           '<div class="key" style="margin-top:22px">'
           '<div class="kr"><i style="background:#C4F82A"></i>Held by fans<b>46%</b></div>'
           '<div class="kr"><i style="background:#FF6A1F"></i>Staked in rounds<b>28%</b></div>'
           '<div class="kr"><i style="background:rgba(255,255,255,.28)"></i>Rewards pool<b>14%</b></div>'
           '<div class="kr"><i style="background:rgba(255,255,255,.08)"></i>Treasury<b>12%</b></div></div>'
           '</div></div>'))
f.append('</div></div></section>')

# utility
f.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
           '<span class="pill">@@ What it does</span><h2>One currency,<br>four jobs</h2>'
           '<p class="lede">$FTR is not a separate speculation. It is the settlement layer that makes ownership, '
           'trading and matchday scoring work as one system.</p></div><div class="bento">', ic("layers", "ic")))
for icon, t, d, c, am in [("candle", "Buys shares", "Every order on the exchange clears in $FTR, including partial fills and limit orders.", "c6", ""),
                          ("swap", "Pays swap fees", "Swapping one asset for another settles the difference and the fee in $FTR, never in shares.", "c6", ""),
                          ("bolt", "Stakes FanPlay entries", "Entering a round locks a stake for the settlement window. Unsettled stakes stay visible in your balance.", "c4", "am"),
                          ("trophy", "Pays out rounds", "Fantrade Points convert to $FTR at settlement and land back in the same wallet.", "c4", ""),
                          ("lock", "Never leaves your control", "Locked balances are shown separately and release the moment a window closes.", "c4", "")]:
    f.append(T('<div class="bezel tight @@" data-reveal><div class="core pad f"><span class="ibox @@">@@</span>'
               '<h4>@@</h4><p>@@</p></div></div>', c, am, ic(icon, "ic-lg"), t, d))
f.append('</div></div></section>')

# ledger
TX = [("Matchday 06 settlement", "Club · Elite", "+312 FP", "+3,744"),
      ("Bought 10,000 $Saka", "Exchange", "—", "−483,928"),
      ("Matchday 05 settlement", "Individual · PRO", "+140 FP", "+1,680"),
      ("Swap $Pedri → $Musiala", "Swap fee", "—", "−184"),
      ("Deposit", "Convert GBP", "—", "+12,338"),
      ("Matchday 04 settlement", "Club · Elite", "+286 FP", "+3,432")]
f.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
           '<span class="pill">@@ Ledger</span><h2>Every movement,<br>in one place</h2></div>'
           '<div class="bezel" data-reveal><div class="core">'
           '<div class="tx h"><span>Activity</span><span>Type</span><span>Points</span><span>$FTR</span></div>',
           ic("receipt", "ic")))
for what, kind, fp, amt in TX:
    cls = "up" if amt.startswith("+") else "down"
    icon = "trophy" if "settlement" in what else ("swap" if "Swap" in what else ("wallet" if "Deposit" in what else "candle"))
    f.append(T('<div class="tx"><span class="w">@@@@</span><span style="color:var(--dim);font-size:12.5px">@@</span>'
               '<span class="num" style="font-size:12.5px;color:var(--dim)">@@</span>'
               '<span class="num @@">@@</span></div>', ic(icon, "ic-sm"), what, kind, fp, cls, amt))
f.append('</div></div></div></section></main>')

FTR_JS = r"""
var fi=document.getElementById('fiat'), fo=document.getElementById('ftr');
function conv(){
  var v=parseInt((fi.value||'0').replace(/[^0-9]/g,''),10)||0;
  var gross=v*12.4, fee=gross*0.005;
  fo.value=Math.round(gross).toLocaleString('en-US');
  document.getElementById('cFee').textContent=Math.round(fee).toLocaleString('en-US');
  document.getElementById('cNet').textContent=Math.round(gross-fee).toLocaleString('en-US')+' $FTR';
}
if(fi){
  fi.addEventListener('input',function(){
    var v=fi.value.replace(/[^0-9]/g,''); fi.value=v?(+v).toLocaleString('en-US'):''; conv();
  });
  document.querySelectorAll('[data-f]').forEach(function(b){
    b.addEventListener('click',function(){ fi.value=(+b.dataset.f).toLocaleString('en-US'); conv(); });
  });
  conv();
}
"""
page("ftr.html", "$FTR — Fantrade", "".join(f), FTR_JS, FTR_CSS)


# ══════════════════════════════════════════════════════════
# HOW IT WORKS
# ══════════════════════════════════════════════════════════
HIW_CSS = """
.walk{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:center;margin-bottom:16px}
.walk.flip .art{order:-1}
.walk .body{padding:44px 40px}
.walk .n{font-family:Archivo;font-variation-settings:'wdth' 125,'wght' 900;font-size:clamp(52px,7vw,86px);
  color:transparent;-webkit-text-stroke:1px rgba(196,248,42,.5);line-height:.85}
.walk h3{font-size:clamp(26px,3.4vw,38px);margin:18px 0 14px}
.walk p{color:var(--dim);font-weight:300;font-size:14.5px;max-width:46ch;margin:0}
.walk ul{list-style:none;padding:0;margin:22px 0 0;font-size:13px;color:var(--dim)}
.walk li{padding:10px 0;border-top:1px solid rgba(255,255,255,.055);display:flex;gap:12px;align-items:center}
.walk li .ic{color:var(--lime);width:15px;height:15px}
.art{min-height:280px;display:grid;place-items:center;position:relative;overflow:hidden;
  background:radial-gradient(ellipse at 50% 40%,rgba(196,248,42,.10),transparent 62%)}
.art .glyph{width:104px;height:104px;color:var(--lime);opacity:.9;fill:currentColor;
  filter:drop-shadow(0 18px 40px rgba(196,248,42,.28))}
.art.am{background:radial-gradient(ellipse at 50% 40%,rgba(255,106,31,.10),transparent 62%)}
.art.am .glyph{color:var(--amber);filter:drop-shadow(0 18px 40px rgba(255,106,31,.26))}
.art .ring{position:absolute;border:1px solid rgba(255,255,255,.06);border-radius:50%}
.art .r1{width:180px;height:180px}.art .r2{width:250px;height:250px}.art .r3{width:320px;height:320px}
.cmp{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:14px;padding:16px 26px;
  border-bottom:1px solid rgba(255,255,255,.05);font-size:13.5px;align-items:center}
.cmp.h{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;border-bottom:1px solid var(--hair)}
.cmp .y{color:var(--lime);display:flex;align-items:center;gap:8px}
.cmp .n{color:var(--faint);display:flex;align-items:center;gap:8px}
.cmp .ic{width:15px;height:15px}
details{border-bottom:1px solid rgba(255,255,255,.06)}
details summary{list-style:none;cursor:pointer;padding:22px 0;display:flex;align-items:center;gap:16px;
  font-family:Archivo;font-variation-settings:'wdth' 115,'wght' 700;text-transform:uppercase;font-size:15px}
details summary::-webkit-details-marker{display:none}
details summary .pm{margin-left:auto;width:28px;height:28px;border-radius:999px;border:1px solid var(--hair);
  display:grid;place-items:center;color:var(--dim);transition:transform .7s var(--ease),background .6s var(--ease)}
details[open] summary .pm{transform:rotate(45deg);background:var(--lime);color:#0A0D03;border-color:var(--lime)}
details p{color:var(--dim);font-weight:300;font-size:14px;max-width:62ch;padding:0 0 22px}
.tl{display:flex;gap:0;margin-top:10px;flex-wrap:wrap}
.tl div{flex:1;min-width:150px;padding:22px 20px;border-left:1px solid var(--hair);position:relative}
.tl div:first-child{border-left:0}
.tl .k{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase}
.tl .v{font-family:'JetBrains Mono',monospace;font-size:16px;margin-top:10px}
.tl .d{font-size:12.5px;color:var(--dim);font-weight:300;margin-top:8px;line-height:1.5}
@media (max-width:900px){.walk{grid-template-columns:1fr}.walk.flip .art{order:0}.art{min-height:200px}
 .walk .body{padding:30px 26px}.cmp{grid-template-columns:1.2fr .8fr .8fr;padding:14px 18px}}
"""

WALK = [
    ("01", "ball", "Fund your balance", "Deposit and convert to $FTR. That single balance is what you trade with, "
     "stake with and get paid into — there is no second currency to manage.",
     ["Convert at the rate shown, fee included", "Balance splits into available and locked"], False),
    ("02", "candle", "Buy players and coaches", "Every asset carries a fixed ten million shares. Buy one share or a "
     "hundred thousand — you own a real slice of that player's Fantrade market.",
     ["Players and coaches trade on the same book", "0.4% fee on both sides, always shown first"], False),
    ("03", "crest", "Build your Dream Club", "Name it, badge it, pick a coach and a shape. Every slot checks your "
     "wallet before it accepts a player, so the squad is genuinely yours.",
     ["1 coach, 11 starters, a working bench", "Change the formation and the shape rebuilds"], True),
    ("04", "bolt", "Enter a round", "Play a single player or send the whole club. Pick a market tier and the "
     "projected points update before you commit anything.",
     ["Six tiers from Simple to Viynx Max", "Club mode earns a configurable boost"], False),
    ("05", "clock", "The window settles", "Real fixtures do the scoring. When the matchday clock closes, every "
     "eligible performance is collected and converted into Fantrade Points.",
     ["Your players can be in different matches", "Bench subs in under your own rules"], False),
    ("06", "trophy", "Get paid, then reinvest", "Points convert to $FTR and land back in your wallet. Most managers "
     "put it straight back into the next player.",
     ["Club value moves with the squad underneath", "Rankings update at the end of every round"], True),
]

h = []
h.append(T('<header class="phead"><div class="wrap">'
           '<span class="pill" data-reveal>@@ The whole loop</span><h1 data-reveal>How Fantrade<br>works</h1>'
           '<p class="lede" data-reveal>Six steps, one balance, and a rule that holds all of it together: you can only '
           'play what you actually own.</p><div style="margin-top:34px" data-reveal>@@</div></div></header>',
           ic("swap", "ic"), btn("Start with the exchange", href="exchange.html")))

h.append('<main><section style="padding-top:20px"><div class="wrap">')
for n, icon, t, d, items, am in WALK:
    lis = "".join(T("<li>@@@@</li>", ic("check", "ic"), x) for x in items)
    art = T('<div class="bezel" data-reveal><div class="core art @@"><span class="ring r1"></span>'
            '<span class="ring r2"></span><span class="ring r3"></span>'
            '<svg class="glyph" aria-hidden="true"><use href="#i-@@"/></svg></div></div>',
            "am" if am else "", icon)
    body = T('<div class="bezel" data-reveal><div class="core body"><div class="n">@@</div>'
             '<h3>@@</h3><p>@@</p><ul>@@</ul></div></div>', n, t, d, lis)
    h.append(T('<div class="walk @@">@@@@</div>', "flip" if am else "", body, art))
h.append('</div></section>')

# settlement timeline
h.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
           '<span class="pill">@@ Settlement</span><h2>One clock,<br>not one fixture</h2>'
           '<p class="lede">A round is a window, not a match. It opens, it locks, the fixtures play out, and everyone '
           'is scored on the same data at the same moment.</p></div>'
           '<div class="bezel" data-reveal><div class="core"><div class="tl">'
           '<div><div class="k">Opens</div><div class="v">Mon 09:00</div><div class="d">Entries accepted. Lineups, '
           'captain and market tier can be changed freely.</div></div>'
           '<div><div class="k">Locks</div><div class="v">Fri 18:30</div><div class="d">No further changes. Ownership '
           'is verified once and frozen for the round.</div></div>'
           '<div><div class="k">Plays out</div><div class="v">Fri–Sun</div><div class="d">Eligible performances are '
           'collected across every tracked fixture.</div></div>'
           '<div><div class="k">Settles</div><div class="v">Mon 02:00</div><div class="d">Points convert to $FTR. '
           'Stakes release, rankings update.</div></div></div></div></div></div></section>', ic("clock", "ic")))

# comparison
CMP = [("Requires ownership", 1, 1), ("Number of assets scored", "1", "up to 16"),
       ("Coach modifier applies", 0, 1), ("Chemistry boost available", 0, 1),
       ("Captain multiplier", 0, 1), ("Bench auto-substitution", 0, 1),
       ("Simplest to enter", 1, 0)]
h.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
           '<span class="pill amber">@@ Choosing a mode</span><h2>Individual<br>or club</h2></div>'
           '<div class="bezel" data-reveal><div class="core">'
           '<div class="cmp h"><span></span><span>Individual</span><span>Dream Club</span></div>', ic("scales", "ic")))
for label, a, b in CMP:
    def cell(v):
        if v == 1: return T('<span class="y">@@Yes</span>', ic("check", "ic"))
        if v == 0: return T('<span class="n">@@No</span>', ic("cross", "ic"))
        return '<span class="num" style="font-size:13px">%s</span>' % v
    h.append(T('<div class="cmp"><span>@@</span>@@@@</div>', label, cell(a), cell(b)))
h.append('</div></div></div></section>')

# faq
FAQ = [("Do I need all eleven players in the same match?",
        "No. Your club scores wherever its players are playing. Fantrade collects eligible performances across every "
        "tracked fixture in the window and settles them together on one clock."),
       ("What happens if a starter doesn't play?",
        "An eligible bench player is substituted in automatically, under the rules you configured when you built the "
        "club. That is why a full bench is worth more than four names and a gap."),
       ("Can I put a player I don't own in my club?",
        "No. Ownership is validated when you add a player and again when the round locks. If the shares aren't in your "
        "wallet, the name doesn't enter the teamsheet."),
       ("How is club value calculated?",
        "The current market value of your starting eleven, plus your bench, plus your coach. It moves whenever the "
        "underlying assets move, which is why the club itself becomes something worth building."),
       ("What does the coach actually do?",
        "For now the coach provides a club modifier rather than his own scoring engine. A coach whose real shape "
        "matches your formation contributes his full bonus."),
       ("Are Dream Clubs tradable?",
        "Not at launch. A club is a portfolio and a FanPlay identity. Club-to-club competition and rankings come first.")]
h.append(T('<section><div class="wrap"><div class="sec-head" data-reveal>'
           '<span class="pill">@@ Questions</span><h2>Before you<br>start</h2></div>'
           '<div class="bezel" data-reveal><div class="core" style="padding:10px 34px 20px">', ic("list", "ic") if False else ic("check", "ic")))
for q, a in FAQ:
    h.append(T('<details><summary>@@<span class="pm">@@</span></summary><p>@@</p></details>',
               q, ic("cross", "ic-sm"), a))
h.append('</div></div></div></section>')

h.append(T('<section style="padding-top:60px"><div class="wrap" style="text-align:center">'
           '<h2 data-reveal>Ready to own<br>your first player?</h2>'
           '<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:34px" data-reveal>'
           '@@@@</div></div></section></main>',
           btn("Browse the exchange", href="exchange.html"),
           btn("See a Dream Club", "btn-glass", "clubs.html")))

page("how-it-works.html", "How it works — Fantrade", "".join(h), "", HIW_CSS)
print("built ftr.html + how-it-works.html")
