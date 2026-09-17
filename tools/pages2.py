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
# $FTR ASSETS OVERVIEW (KUCOIN / MOBILE CRYPTO STYLE)
# ══════════════════════════════════════════════════════════
FTR_CSS = """
.kc-assets-wrap{max-width:680px;margin:0 auto;padding:12px 16px 84px}
.kc-topbar{display:flex;align-items:center;justify-content:space-between;padding:8px 0 16px}
.kc-top-title{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;font-size:17px;letter-spacing:-.01em;text-transform:uppercase}
.kc-icon-btn{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;color:#8E9AA8;cursor:pointer;transition:all .2s ease;text-decoration:none}
.kc-icon-btn:hover{color:#fff;background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.15)}
.kc-icon-btn .ic{width:18px;height:18px}

.kc-assets-card{background:linear-gradient(135deg,#0E1114 0%,#08090A 100%);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:22px;box-shadow:0 12px 32px rgba(0,0,0,.6);margin-bottom:18px;position:relative;overflow:hidden}
.kc-assets-card::before{content:"";position:absolute;top:-60px;right:-60px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,rgba(196,248,42,.12),transparent 70%);pointer-events:none}
.kc-card-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
.kc-card-lbl{font-size:11px;font-weight:600;letter-spacing:.12em;color:#8E9AA8;text-transform:uppercase;display:flex;align-items:center;gap:6px}
.kc-eye-btn{background:transparent;border:0;color:#8E9AA8;cursor:pointer;padding:2px;display:flex;align-items:center;transition:color .2s}
.kc-eye-btn:hover{color:#fff}
.kc-card-bal{font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:700;letter-spacing:-.02em;color:#FFFFFF;margin:4px 0 6px;line-height:1.1;display:flex;align-items:baseline;gap:6px}
.kc-card-bal small{font-size:16px;color:#C4F82A;font-weight:500}
.kc-card-sub{display:flex;align-items:center;gap:10px;font-size:12.5px;color:#8E9AA8}
.kc-pnl-pill{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;padding:2px 8px;border-radius:6px;background:rgba(196,248,42,.12);color:#C4F82A;border:1px solid rgba(196,248,42,.25)}

.kc-actions-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,.06)}
.kc-act-btn{display:flex;flex-direction:column;align-items:center;gap:8px;text-decoration:none;color:#C3C9BE;cursor:pointer;transition:transform .2s ease}
.kc-act-btn:hover{transform:translateY(-2px);color:#fff}
.kc-act-icon{width:44px;height:44px;border-radius:14px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);display:flex;align-items:center;justify-content:center;color:#C4F82A;transition:all .2s ease}
.kc-act-btn:hover .kc-act-icon{background:rgba(196,248,42,.15);border-color:rgba(196,248,42,.4)}
.kc-act-lbl{font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase}

.kc-alloc-card{background:#0A0B0C;border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:16px;margin-bottom:18px}
.kc-alloc-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;font-size:11.5px;font-weight:600;letter-spacing:.08em;color:#8E9AA8;text-transform:uppercase}
.kc-alloc-bar{height:6px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden;display:flex;margin-bottom:12px}
.kc-alloc-bar-seg{height:100%;transition:width .4s ease}
.kc-alloc-legend{display:flex;justify-content:space-between;gap:8px;font-size:11px;color:#8E9AA8;flex-wrap:wrap}
.kc-leg-item{display:flex;align-items:center;gap:6px}
.kc-leg-dot{width:8px;height:8px;border-radius:50%}
.kc-leg-item b{color:#fff;font-family:'JetBrains Mono',monospace;font-weight:500}

.kc-tabs{display:flex;gap:12px;border-bottom:1px solid rgba(255,255,255,.07);margin-bottom:12px;padding-bottom:2px}
.kc-tab-btn{background:transparent;border:0;color:#8E9AA8;font-family:Montserrat,sans-serif;font-size:13px;font-weight:600;padding:8px 4px;cursor:pointer;position:relative;transition:color .2s}
.kc-tab-btn.on{color:#fff}
.kc-tab-btn.on::after{content:"";position:absolute;left:0;right:0;bottom:-3px;height:2px;background:#C4F82A;border-radius:2px}

.kc-holdings-list{display:flex;flex-direction:column;gap:4px}
.kc-asset-row{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-radius:14px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);text-decoration:none;transition:all .2s ease}
.kc-asset-row:hover{background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.09)}
.kc-asset-left{display:flex;align-items:center;gap:12px}
.kc-asset-icon{width:38px;height:38px;border-radius:12px;background:rgba(196,248,42,.1);border:1px solid rgba(196,248,42,.25);display:flex;align-items:center;justify-content:center;color:#C4F82A}
.kc-asset-icon.coach{background:rgba(255,106,31,.1);border-color:rgba(255,106,31,.25);color:var(--amber)}
.kc-asset-name{font-weight:700;font-size:13.5px;color:#fff}
.kc-asset-sub{font-size:11px;color:#8E9AA8;margin-top:2px}
.kc-asset-right{text-align:right}
.kc-asset-val{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#fff}
.kc-asset-chg{font-family:'JetBrains Mono',monospace;font-size:11px;margin-top:2px}
.kc-asset-chg.up{color:#C4F82A}
.kc-asset-chg.down{color:#FF5E5E}
"""

WALLET_ASSETS = [("$Saka", "Bukayo Saka", "boot", "", 6.4, 0),
                 ("$Haaland", "Erling Haaland", "boot", "", -1.8, 1),
                 ("$Bruno", "Bruno Fernandes", "boot", "", 4.2, 2),
                 ("$Arteta", "Mikel Arteta", "whistle", "am", 14.2, 9)]

f = ['<main><div class="kc-assets-wrap">']

# Sleek Mobile Topbar
f.append(T('<div class="kc-topbar">'
           '<a class="kc-icon-btn" href="dashboard.html" aria-label="Back to Home">@@</a>'
           '<div class="kc-top-title">Wallet &amp; Assets</div>'
           '<a class="kc-icon-btn" href="activity.html" aria-label="Transaction Ledger" title="Transaction Ledger">@@</a>'
           '</div>',
           ic("arrow", "ic"), ic("receipt", "ic")))

# Total Assets Card
f.append(T('<div class="kc-assets-card">'
           '<div class="kc-card-top">'
           '<div class="kc-card-lbl">Total Equity Value ($FTR)'
           '<button type="button" class="kc-eye-btn" id="walEyeBtn" title="Toggle balance visibility">'
           '<svg class="ic" id="walEyeIcon"><use href="#i-eye"/></svg></button></div>'
           '<div class="kc-pnl-pill" id="walDelta">+2.35% (+2,940)</div>'
           '</div>'
           '<div class="kc-card-bal"><span id="walBal">128,450.00</span><small>$FTR</small></div>'
           '<div class="kc-card-sub"><span id="walGbp">≈ $10,358.80 USD</span> · <span style="color:#C4F82A">Protected</span></div>'
           '<div class="kc-actions-grid">'
           '<a class="kc-act-btn" href="buy.html"><div class="kc-act-icon">@@</div><span class="kc-act-lbl">Deposit</span></a>'
           '<a class="kc-act-btn" href="send.html"><div class="kc-act-icon">@@</div><span class="kc-act-lbl">Withdraw</span></a>'
           '<a class="kc-act-btn" href="send.html"><div class="kc-act-icon">@@</div><span class="kc-act-lbl">Transfer</span></a>'
           '<a class="kc-act-btn" href="swap.html"><div class="kc-act-icon">@@</div><span class="kc-act-lbl">Convert</span></a>'
           '</div></div>',
           ic("coin", "ic"), ic("send", "ic"), ic("arrow", "ic"), ic("swap", "ic")))

# Allocation Progress Bar Card
f.append('<div class="kc-alloc-card">'
         '<div class="kc-alloc-head"><span>Portfolio Allocation</span><span id="walPosCount">4 Positions</span></div>'
         '<div class="kc-alloc-bar">'
         '<div class="kc-alloc-bar-seg" style="width:62%;background:#C4F82A" title="Liquid FTR"></div>'
         '<div class="kc-alloc-bar-seg" style="width:28%;background:#4DA3FF" title="Player Shares"></div>'
         '<div class="kc-alloc-bar-seg" style="width:10%;background:#FF6A1F" title="Locked in Entries"></div>'
         '</div>'
         '<div class="kc-alloc-legend">'
         '<div class="kc-leg-item"><div class="kc-leg-dot" style="background:#C4F82A"></div>Liquid <b id="walLiquidAmt">128,450 FTR</b></div>'
         '<div class="kc-leg-item"><div class="kc-leg-dot" style="background:#4DA3FF"></div>Shares <b id="walSharesAmt">58,240 FTR</b></div>'
         '<div class="kc-leg-item"><div class="kc-leg-dot" style="background:#FF6A1F"></div>Locked <b id="walLockedAmt">10,000 FTR</b></div>'
         '</div></div>')

# Tabs: Holdings / Staking / History
f.append('<div class="kc-tabs">'
         '<button class="kc-tab-btn on" type="button" data-tab="holdings">Holdings</button>'
         '<button class="kc-tab-btn" type="button" data-tab="staking" onclick="window.location.href=\'fanplay.html\'">Staking &amp; Futures</button>'
         '<button class="kc-tab-btn" type="button" data-tab="history" onclick="window.location.href=\'activity.html\'">Ledger</button>'
         '</div>')

# Assets List
f.append('<div class="kc-holdings-list" id="walAssets"></div>')

f.append('</div></main>')

FTR_JS = ("var WASSETS=" + repr([{"t": t, "n": n, "i": i, "c": c, "d": d, "s": s}
                                 for t, n, i, c, d, s in WALLET_ASSETS]).replace("'", '"') + ";") + r"""
function el(id){ return document.getElementById(id); }
function money(n){ return Math.round(n).toLocaleString('en-US'); }

var hidden = false;
var eyeBtn = el('walEyeBtn');
if(eyeBtn){
  eyeBtn.addEventListener('click', function(){
    hidden = !hidden;
    syncWallet();
  });
}

function renderAssets(){
  var s = FT.getState(), box = el('walAssets');
  if(!box) return;
  var rows = [];

  // Liquid FTR Row
  rows.push('<div class="kc-asset-row">'
    + '<div class="kc-asset-left">'
    + '<div class="kc-asset-icon"><svg class="ic" aria-hidden="true"><use href="#i-coin"/></svg></div>'
    + '<div><div class="kc-asset-name">$FTR</div><div class="kc-asset-sub">Fantrade Token · Liquid</div></div>'
    + '</div>'
    + '<div class="kc-asset-right">'
    + '<div class="kc-asset-val">' + (hidden ? '••••••' : money(s.wallet.balance) + ' FTR') + '</div>'
    + '<div class="kc-asset-chg up">+2.35% (24h)</div>'
    + '</div></div>');

  // Player Holdings
  var totalSharesVal = 0;
  Object.keys(s.holdings).forEach(function(k){
    var h = s.holdings[k];
    var val = h.shares * (h.p || h.avg || 10);
    totalSharesVal += val;
    var meta = WASSETS.filter(function(a){ return a.t === k; })[0]
      || { i: h.c ? 'whistle' : 'boot', c: h.c ? 'coach' : '', d: 0, s: 0 };
    var up = meta.d >= 0;

    rows.push('<a class="kc-asset-row" href="asset.html?a=' + encodeURIComponent(k) + '">'
      + '<div class="kc-asset-left">'
      + '<div class="kc-asset-icon ' + (meta.c || '') + '"><svg class="ic" aria-hidden="true"><use href="#i-' + meta.i + '"/></svg></div>'
      + '<div><div class="kc-asset-name">' + k + ' <span style="font-weight:400;color:#8E9AA8;font-size:12px">' + h.n + '</span></div>'
      + '<div class="kc-asset-sub">' + (hidden ? '••••' : h.shares.toLocaleString('en-US') + ' shares') + '</div></div>'
      + '</div>'
      + '<div class="kc-asset-right">'
      + '<div class="kc-asset-val">' + (hidden ? '••••••' : money(val) + ' FTR') + '</div>'
      + '<div class="kc-asset-chg ' + (up ? 'up' : 'down') + '">' + (up ? '+' : '') + meta.d.toFixed(2) + '%</div>'
      + '</div></a>');
  });

  box.innerHTML = rows.join('');
  if(el('walPosCount')) el('walPosCount').textContent = (Object.keys(s.holdings).length + 1) + ' Assets';
  if(el('walSharesAmt')) el('walSharesAmt').textContent = (hidden ? '••••' : money(totalSharesVal) + ' FTR');
  if(el('walLockedAmt')) el('walLockedAmt').textContent = (hidden ? '••••' : money(s.wallet.locked || 0) + ' FTR');
  if(el('walLiquidAmt')) el('walLiquidAmt').textContent = (hidden ? '••••' : money(s.wallet.balance) + ' FTR');
}

function syncWallet(){
  var s = FT.getState();
  var bal = s.wallet.balance || 0;
  if(el('walBal')){
    el('walBal').textContent = hidden ? '••••••' : bal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  if(el('walGbp')){
    el('walGbp').textContent = hidden ? '≈ $•••••• USD' : '≈ $' + (bal * 0.0806).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' USD';
  }
  renderAssets();
}

syncWallet();
window.addEventListener('fantrade:statechange', syncWallet);
"""
page("ftr.html", "Wallet & Assets — Fantrade", "".join(f), FTR_JS, FTR_CSS, app=True)
page("wallet.html", "Wallet & Assets — Fantrade", "".join(f), FTR_JS, FTR_CSS, app=True)



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
