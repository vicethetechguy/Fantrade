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


def page(fname, title, body, js="", css="", app=False):
    html = (head(title, css, "app" if app else "") + atmosphere() + nav(fname, app) +
            body + footer() + "<script src=\"public/fantrade-api.js\"></script><script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
    open(os.path.join(OUT, fname), "w", encoding="utf-8").write(html)


# ══════════════════════════════════════════════════════════
# $FTR WALLET
# ══════════════════════════════════════════════════════════
FTR_CSS = """
.wcard{max-width:none}
"""

# label, icon, coin tone, sparkline direction
WALLET_ASSETS = [("$Saka", "Bukayo Saka", "boot", "", 6.4, 0),
                 ("$Haaland", "Erling Haaland", "boot", "", -1.8, 1),
                 ("$Bruno", "Bruno Fernandes", "boot", "", 4.2, 2),
                 ("$Arteta", "Mikel Arteta", "whistle", "am", 14.2, 9)]

# The wallet is a card and a list of what you own. Send, receive, swap, buy
# and the ledger are destinations, not panels stacked underneath it.
f = ['<main><section style="padding:118px 0 70px"><div class="wrap"><div class="bento">']

f.append(T('<div class="c5" data-reveal><div class="wcard">'
           '<span class="tag-id">FTR-012</span>'
           '<div class="k">Total balance</div>'
           '<div class="amt" id="walBal">128,450<small> $FTR</small></div>'
           '<div class="sub" id="walDelta">@@<span>2.35% today</span>'
           '<span style="color:rgba(10,13,3,.5)">·</span><span id="walGbp">≈ £10,358</span></div>'
           '<div class="wacts">'
           '<a href="send.html">@@<span>Send</span></a>'
           '<a href="receive.html">@@<span>Receive</span></a>'
           '<a href="swap.html">@@<span>Swap</span></a>'
           '<a href="buy.html">@@<span>Buy</span></a>'
           '</div></div></div>',
           ic("arrow", "ic"), ic("send", "ic"), ic("receive", "ic"),
           ic("swap", "ic"), ic("coin", "ic")))

f.append(T('<div class="bezel c7" data-reveal><div class="core">'
           '<div style="padding:24px 24px 12px;display:flex;align-items:center;gap:14px;flex-wrap:wrap">'
           '<div><div style="font-family:Archivo;font-variation-settings:\'wdth\' 120,\'wght\' 800;'
           'text-transform:uppercase;font-size:19px">My assets</div>'
           '<div class="sub-line" id="walCount">Loading…</div></div>'
           '<a class="seeall" href="activity.html">Activity @@</a></div>'
           '<div id="walAssets"></div></div></div>', ic("arrow", "ic-sm")))

f.append('</div></div></section></main>')

FTR_JS = ("var WASSETS=" + repr([{"t": t, "n": n, "i": i, "c": c, "d": d, "s": s}
                                 for t, n, i, c, d, s in WALLET_ASSETS]).replace("'", '"') + ";") + r"""
function el(id){ return document.getElementById(id); }
function money(n){ return Math.round(n).toLocaleString('en-US'); }

function renderAssets(){
  var s = FT.getState(), box = el('walAssets');
  var rows = ['<div class="arow"><div class="who"><span class="coin lime">'
    + '<svg class="ic" aria-hidden="true"><use href="#i-coin"/></svg></span>'
    + '<div style="min-width:0"><div class="nm">$FTR</div><div class="qt">Liquid balance</div></div></div>'
    + '<div data-spark="1"></div>'
    + '<div><div class="val">' + money(s.wallet.balance) + '</div>'
    + '<div class="chg up">+2.35%</div></div></div>'];

  Object.keys(s.holdings).forEach(function(k){
    var h = s.holdings[k];
    var meta = WASSETS.filter(function(a){ return a.t === k; })[0]
      || { i: h.c ? 'whistle' : 'boot', c: h.c ? 'am' : '', d: 0, s: 0 };
    var up = meta.d >= 0;
    rows.push('<a class="arow" href="asset.html?a=' + encodeURIComponent(k) + '">'
      + '<div class="who"><span class="coin ' + (meta.c || '') + '">'
      + '<svg class="ic" aria-hidden="true"><use href="#i-' + meta.i + '"/></svg></span>'
      + '<div style="min-width:0"><div class="nm">' + h.n + '</div>'
      + '<div class="qt">' + h.shares.toLocaleString('en-US') + ' ' + k + '</div></div></div>'
      + '<div data-spark="' + (up ? 1 : 0) + '"></div>'
      + '<div><div class="val">' + money(h.shares * h.p) + '</div>'
      + '<div class="chg ' + (up ? 'up' : 'down') + '">'
      + (up ? '+' : '') + meta.d.toFixed(2) + '%</div></div></a>');
  });

  box.innerHTML = rows.join('');
  el('walCount').textContent = Object.keys(s.holdings).length + ' positions · '
    + money(FT.holdingsValue()) + ' $FTR at market';
  box.querySelectorAll('[data-spark]').forEach(function(d){
    d.innerHTML = spark(d.dataset.spark === '1', 88, 26);
  });
}

function syncWallet(){
  var s = FT.getState();
  el('walBal').innerHTML = s.wallet.balance.toLocaleString('en-US') + '<small> $FTR</small>';
  el('walGbp').textContent = '≈ £' + Math.round(s.wallet.balance / 12.4).toLocaleString('en-US');
  renderAssets();
}
syncWallet();
window.addEventListener('fantrade:statechange', syncWallet);
"""
page("ftr.html", "$FTR — Fantrade", "".join(f), FTR_JS, FTR_CSS, app=True)


# ══════════════════════════════════════════════════════════
# HOW IT WORKS
# ══════════════════════════════════════════════════════════
HIW_CSS = """
.tier{height:100%}
.tier .top{display:flex;align-items:center;gap:14px;margin-bottom:16px}
.tier h4{font-size:19px}
.tier .x{margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:20px;color:var(--lime)}
.tier p{font-size:13px;font-weight:300;color:var(--dim);margin:0 0 16px}
.risk{height:4px;border-radius:99px;background:rgba(255,255,255,.07);overflow:hidden}
.risk i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#C4F82A,#FF6A1F)}
.risk-k{display:flex;justify-content:space-between;font-weight:600;font-size:9px;letter-spacing:.14em;
  color:var(--faint);margin-top:10px;text-transform:uppercase}
.rule{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:14px;padding:14px 24px;
  border-bottom:1px solid rgba(255,255,255,.05);font-size:13px}
.rule.h{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;
  border-bottom:1px solid var(--hair)}
.rule .num{color:var(--ink)}
@media (max-width:768px){
  .rule{grid-template-columns:1.4fr 1fr!important;padding:12px 14px!important}
  .rule>*:nth-child(n+3){display:none!important}
}
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
     "eligible performance is collected and converted into Fans Point.",
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

# ── rehomed from the in-app pages ──────────────────────────────
h.append(T('<section id="mechanics"><div class="wrap"><div class="sec-head" data-reveal>'
           '<span class="pill">@@ Order mechanics</span><h2>How a trade<br>settles here</h2>'
           '<p class="lede">Every order on the exchange clears the same way, whether it is your first '
           'fifty shares or a full squad rebuild.</p></div><div class="bento">', ic("swap", "ic")))
for icon, t, d in [("wallet", "Fund in $FTR",
                    "Deposit, convert to $FTR, and your balance is ready to trade against any listed asset."),
                   ("candle", "Buy at market",
                    "Orders fill against the live book. Fees are 0.4% on both sides and are always shown "
                    "before you confirm."),
                   ("shield", "Ownership recorded",
                    "Settled shares land in your wallet immediately and become eligible for FanPlay and "
                    "club selection.")]:
    h.append(T('<div class="bezel tight c4" data-reveal><div class="core pad f"><span class="ibox">@@</span>'
               '<h4>@@</h4><p>@@</p></div></div>', ic(icon, "ic-lg"), t, d))
h.append('</div></div></section>')

TIERS = [("Simple", 1, "Lowest variance. Goals, assists and clean sheets only — a good place to learn how "
          "settlement works.", 18, "target"),
         ("PRO", 1.4, "Adds key passes, duels won and expected goals to the scoring set.", 32, "chart"),
         ("Elite", 2, "Full performance data with position-weighted scoring. The standard matchday market.",
          50, "shield"),
         ("Killer", 3, "High multiplier, punishing downside. Cards, misses and errors all count against you.",
          68, "bolt"),
         ("Viynx Move", 4.5, "Momentum market. Scoring swings with live in-match movement across the whole "
          "round.", 84, "pulse"),
         ("Viynx Max", 7, "Maximum exposure. The largest payouts on Fantrade and the shortest odds of "
          "reaching them.", 100, "trophy")]
h.append(T('<section id="tiers"><div class="wrap"><div class="sec-head" data-reveal>'
           '<span class="pill">@@ Market tiers</span><h2>Six ways to<br>take the round</h2>'
           '<p class="lede">Every tier scores the same match from a different data set. Higher tiers pay '
           'more because they count more of what can go wrong.</p></div><div class="bento">',
           ic("candle", "ic")))
for name, m, note, risk, icon in TIERS:
    h.append(T('<div class="bezel tight c4" data-reveal><div class="core pad tier">'
               '<div class="top"><span class="ibox @@">@@</span><h4>@@</h4><span class="x">×@@</span></div>'
               '<p>@@</p><div class="risk"><i style="width:@@%"></i></div>'
               '<div class="risk-k"><span>Variance</span><span>@@</span></div></div></div>',
               "am" if risk > 60 else "", ic(icon, "ic-lg"), name, ("%g" % m), note, risk,
               "Low" if risk < 40 else ("Medium" if risk < 70 else "High")))
h.append('</div></div></section>')

RULES = [("Goal", "6", "4", "9"), ("Assist", "4", "3", "6"), ("Clean sheet", "5", "1", "7"),
         ("Key pass", "—", "1", "2"), ("Duel won", "—", "0.5", "1"), ("Yellow card", "−1", "−1", "−3"),
         ("Big chance missed", "—", "−2", "−4")]
h.append(T('<section id="rules"><div class="wrap"><div class="sec-head" data-reveal>'
           '<span class="pill amber">@@ Scoring</span><h2>What counts,<br>and for how much</h2>'
           '<p class="lede">Values shown for an outfield player. Goalkeepers and defenders carry their own '
           'weighting, and the coach scores on team outcomes rather than individual events.</p></div>'
           '<div class="bezel" data-reveal><div class="core">'
           '<div class="rule h"><span>Event</span><span>Simple</span><span>Elite</span>'
           '<span>Viynx Max</span></div>', ic("check", "ic")))
for ev, a, b, c in RULES:
    h.append(T('<div class="rule"><span>@@</span><span class="num">@@</span><span class="num">@@</span>'
               '<span class="num">@@</span></div>', ev, a, b, c))
h.append('</div></div></div></section>')

h.append(T('<section id="chem"><div class="wrap"><div class="sec-head" data-reveal>'
           '<span class="pill amber">@@ Club chemistry</span><h2>Why one squad<br>boosts harder</h2>'
           '<p class="lede">Two managers can own the same eleven players and score differently. Chemistry '
           'rewards the club that is actually coherent, not just expensive.</p></div><div class="bento">',
           ic("target", "ic")))
for icon, t, d, c, am in [("whistle", "Coach compatibility",
                           "A coach whose real-world shape matches your formation contributes his full "
                           "modifier. Mismatch it and the bonus shrinks.", "c4", "am"),
                          ("pitch", "Natural positions",
                           "Players scored in the role they actually play carry full weight. A winger at "
                           "left-back will cost you.", "c4", ""),
                          ("subs", "Squad completeness",
                           "A full bench is worth more than four names and a gap, because it guarantees "
                           "cover on matchday.", "c4", ""),
                          ("flag", "Players actually starting",
                           "Chemistry reads real team news. A squad of confirmed starters outperforms a "
                           "squad of big names on the bench.", "c6", ""),
                          ("clock", "Club consistency",
                           "Clubs that hold their shape across rounds build a consistency bonus. Constant "
                           "teardowns reset it.", "c6", "")]:
    h.append(T('<div class="bezel tight @@" data-reveal><div class="core pad f"><span class="ibox @@">@@</span>'
               '<h4>@@</h4><p>@@</p></div></div>', c, am, ic(icon, "ic-lg"), t, d))
h.append('</div></div></section>')

h.append(T('<section style="padding-top:60px"><div class="wrap" style="text-align:center">'
           '<h2 data-reveal>Ready to own<br>your first player?</h2>'
           '<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:34px" data-reveal>'
           '@@@@</div></div></section></main>',
           btn("Browse the exchange", href="exchange.html"),
           btn("See a Dream Club", "btn-glass", "clubs.html")))

page("how-it-works.html", "How it works — Fantrade", "".join(h), "", HIW_CSS)
print("built ftr.html + how-it-works.html")
