# -*- coding: utf-8 -*-
"""Account + in-app surfaces: auth, onboarding, dashboard, portfolio,
leaderboard, notifications, settings. Same shell, same tokens as pages 1–6."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import head, atmosphere, nav, nav_min, footer, ic, JS_SHELL

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


def page(fname, title, body, js="", css="", app=True, chrome=True):
    """chrome=False renders the stripped auth shell (minimal nav, no footer)."""
    shell = nav(fname, app) if chrome else nav_min()
    tail = footer() if chrome else ""
    html = (head(title, css, "app" if (app and chrome) else "") + atmosphere() + shell + body + tail +
            "<script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)


def tf(label, name, typ="text", ph="", icon="", hint="", err="", extra="", link=""):
    lab = ('<div class="lrow"><label for="%s">%s</label><a href="#" data-forgot>%s</a></div>' % (name, label, link)
           if link else '<label for="%s">%s</label>' % (name, label))
    eye = ('<button class="eye" type="button" data-eye aria-label="Show password">Show</button>'
           if typ == "password" else "")
    return ('<div class="tf" id="f-%s"><%s<div class="inp">%s'
            '<input id="%s" name="%s" type="%s" placeholder="%s" %s>%s</div>%s%s</div>'
            % (name, lab[1:], ic(icon, "ic") if icon else "", name, name, typ, ph, extra, eye,
               '<div class="hint">%s</div>' % hint if hint else "",
               '<div class="err">%s</div>' % err if err else ""))


def sel(label, name, options, icon="", hint=""):
    opts = "".join('<option%s>%s</option>' % (' selected' if o.startswith("*") else '', o.lstrip("*")) for o in options)
    return ('<div class="tf" id="f-%s"><label for="%s">%s</label><div class="inp">%s'
            '<select id="%s" name="%s">%s</select>%s</div>%s</div>'
            % (name, name, label, ic(icon, "ic") if icon else "", name, name, opts,
               '<span class="chev"></span>', '<div class="hint">%s</div>' % hint if hint else ""))


def check(name, html, checked=False):
    return ('<label class="checkrow"><input type="checkbox" id="%s"%s><span class="box">%s</span>'
            '<span>%s</span></label>' % (name, ' checked' if checked else '', ic("check", "ic"), html))


COUNTRIES = ["*United Kingdom", "Nigeria", "Ireland", "Ghana", "Kenya", "South Africa",
             "Spain", "Germany", "France", "Italy", "Portugal", "Netherlands",
             "United States", "Canada", "Australia", "India", "Other"]

# ══════════════════════════════════════════════════════════════════
# Shared auth JS — validation, password meter, reveal toggles
# ══════════════════════════════════════════════════════════════════
AUTH_JS = r"""
function fld(id){ return document.getElementById(id); }
function wrap(id){ return document.getElementById('f-' + id); }
function bad(id, msg){
  var w = wrap(id); if(!w) return false;
  w.classList.add('bad'); w.classList.remove('ok');
  var e = w.querySelector('.err'); if(e && msg) e.textContent = msg;
  return false;
}
function good(id){
  var w = wrap(id); if(w){ w.classList.remove('bad'); w.classList.add('ok'); }
  return true;
}
function clearErr(id){ var w = wrap(id); if(w) w.classList.remove('bad'); }
function validEmail(v){ return /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test((v||'').trim()); }
function scorePw(v){
  var s = 0;
  if(!v) return 0;
  if(v.length >= 8) s++;
  if(v.length >= 12) s++;
  if(/[A-Z]/.test(v) && /[a-z]/.test(v)) s++;
  if(/[0-9]/.test(v) && /[^A-Za-z0-9]/.test(v)) s++;
  return s;
}
document.querySelectorAll('[data-eye]').forEach(function(b){
  b.addEventListener('click', function(){
    var i = b.parentNode.querySelector('input');
    var show = i.type === 'password';
    i.type = show ? 'text' : 'password';
    b.textContent = show ? 'Hide' : 'Show';
    b.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
  });
});
document.querySelectorAll('[data-forgot]').forEach(function(a){
  a.addEventListener('click', function(e){
    e.preventDefault();
    openModal('<h3 class="ft-modal-title">Reset your password</h3>'
      + '<p class="ft-modal-desc">Enter the email on your Fantrade account. We will send a single-use link that '
      + 'expires in 20 minutes. Your holdings and club stay locked while a reset is pending.</p>'
      + '<div class="tf" id="f-resetEmail"><label for="resetEmail">Email</label><div class="inp">'
      + '<input id="resetEmail" type="email" placeholder="you@example.com"></div>'
      + '<div class="err">Enter a valid email address.</div></div>'
      + '<button class="btn btn-lime" id="resetGo" type="button" style="width:100%;justify-content:space-between;margin-top:8px">'
      + 'Send reset link<span class="cap"><svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></span></button>');
    var go = document.getElementById('resetGo');
    if(go) go.addEventListener('click', function(){
      var v = document.getElementById('resetEmail').value;
      if(!validEmail(v)){ bad('resetEmail'); return; }
      closeModal();
      showToast('Reset link sent to ' + v.trim() + '.', 'success');
    });
  });
});
document.querySelectorAll('.oauth button').forEach(function(b){
  b.addEventListener('click', function(){
    showToast(b.dataset.provider + ' is not wired up in this prototype — use the email form.', 'info');
  });
});
"""

# ══════════════════════════════════════════════════════════════════
# SIGN IN
# ══════════════════════════════════════════════════════════════════
PROOF = [("shield", "Your shares never leave your wallet",
          "Ownership is validated on every club lock. Nothing is lent, shorted or synthesised behind you."),
         ("clock", "Settlement on the final whistle",
          "Rounds close on a published clock. Points convert to $FTR and land in the same balance you staked from."),
         ("rank", "One club, one league table",
          "Every Dream Club is ranked against the same 1,420 syndicates. No hidden lobbies, no private pools.")]


def brand_panel(pill, title, lede, rows=PROOF):
    out = [T('<div class="auth-brand"><div><span class="pill" data-reveal>@@ @@</span>'
             '<h1 data-reveal>@@</h1><p class="lede" data-reveal>@@</p><div class="proof" data-reveal>',
             ic("ball", "ic"), pill, title, lede)]
    for icon, t, d in rows:
        out.append(T('<div class="pr"><span class="ibox">@@</span><div><b>@@</b>@@</div></div>',
                     ic(icon, "ic"), t, d))
    out.append('</div></div></div>')
    return "".join(out)


si = [T('<main class="auth">@@<div class="auth-form"><div class="inner" data-reveal>',
        brand_panel("Manager access", "Back to<br>the desk",
                    "Your balance, your holdings and your teamsheet are exactly where you left them. "
                    "Gameweek 28 locks in three hours."))]
si.append('<h2>Sign in</h2><p class="auth-sub">Use the email on your Fantrade account. '
          'Sessions stay open for 30 days unless you sign out.</p>')
si.append('<form id="signinForm" novalidate>')
si.append(tf("Email", "email", "email", "you@example.com", "", "", "Enter a valid email address."))
si.append(tf("Password", "password", "password", "••••••••••", "lock", "",
             "Password must be at least 8 characters.", link="Forgot?"))
si.append(check("remember", "Keep me signed in on this device", True))
si.append('<button class="btn btn-lime" type="submit" style="width:100%;justify-content:space-between">'
          'Sign in' + ARROW + '</button>')
si.append('</form>')
si.append('<div class="splitline">Or continue with</div>')
si.append(T('<div class="oauth"><button type="button" data-provider="Passkey">@@ Passkey</button>'
            '<button type="button" data-provider="Google">@@ Google</button>'
            '<button type="button" data-provider="Wallet">@@ Wallet</button></div>',
            ic("shield", "ic"), ic("crest", "ic"), ic("wallet", "ic")))
si.append('<div class="demo-note">Prototype build — any valid email and an 8-character password will sign you in. '
          'Try <b>alex.morgan@fantrade.app</b> with <b>fantrade2026</b>.</div>')
si.append('<div class="auth-alt">New to Fantrade? <a href="signup.html">Create an account</a></div>')
si.append('</div></div></main>')

SIGNIN_JS = AUTH_JS + r"""
var sf = document.getElementById('signinForm');
if(sf) sf.addEventListener('submit', function(e){
  e.preventDefault();
  var em = fld('email').value, pw = fld('password').value;
  var ok = true;
  if(!validEmail(em)) ok = bad('email'); else good('email');
  if(!pw || pw.length < 8) ok = bad('password'); else good('password');
  if(!ok){ showToast('Check the highlighted fields and try again.', 'error'); return; }
  var name = FT.getState().auth.email === em.trim() ? null : em.trim().split('@')[0]
      .split(/[._-]+/).map(function(w){ return w.charAt(0).toUpperCase() + w.slice(1); }).join(' ');
  FT.signIn(em.trim(), name);
  showToast('Welcome back. Loading your desk…', 'success');
  setTimeout(function(){ window.location.href = 'dashboard.html'; }, 700);
});
['email','password'].forEach(function(id){
  var el = fld(id); if(el) el.addEventListener('input', function(){ clearErr(id); });
});
"""

page("signin.html", "Sign in — Fantrade", "".join(si), SIGNIN_JS, chrome=False)

# ══════════════════════════════════════════════════════════════════
# SIGN UP
# ══════════════════════════════════════════════════════════════════
SU_PROOF = [("coin", "Start with 50,000 $FTR",
             "Every new manager gets a prototype balance to buy their first shares with. No card, no deposit."),
            ("formation", "Build a club in eight steps",
             "Name it, pick a shape, fill eleven positions from assets you actually own, then put it on the pitch."),
            ("trophy", "Play your first matchday free",
             "Your opening FanPlay entry is covered. After that, stakes come out of the same wallet as everything else.")]

su = [T('<main class="auth">@@<div class="auth-form"><div class="inner" data-reveal>',
        brand_panel("Open an account", "Own your<br>first player",
                    "Three minutes to an account, a funded wallet and eleven names on a teamsheet.",
                    SU_PROOF))]
su.append('<h2>Create account</h2><p class="auth-sub">One account covers the exchange, your Dream Club '
          'and every FanPlay round.</p>')
su.append('<form id="signupForm" novalidate>')
su.append(tf("Full name", "name", "text", "Alex Morgan", "user", "", "Tell us what to call you."))
su.append(tf("Email", "email", "email", "you@example.com", "", "", "Enter a valid email address."))
su.append(tf("Password", "password", "password", "At least 8 characters", "lock", "",
             "Use 8 characters or more, with a number.",
             extra='autocomplete="new-password"'))
su.append('<div class="strength" id="pwMeter" aria-hidden="true"><i></i><i></i><i></i><i></i></div>'
          '<div class="hint" id="pwLabel" style="margin:9px 0 18px;color:var(--faint);font-size:11px">'
          'Strength — add length, mixed case and a symbol.</div>')
su.append(sel("Country of residence", "country", COUNTRIES, "flag",
              "Sets your tax export format and which leagues settle in your local window."))
su.append(check("terms", 'I accept the <a href="#">Terms</a> and <a href="#">Responsible play</a> policy, '
                         'and I am 18 or over.'))
su.append('<button class="btn btn-lime" type="submit" style="width:100%;justify-content:space-between">'
          'Create account' + ARROW + '</button>')
su.append('</form>')
su.append('<div class="splitline">Or continue with</div>')
su.append(T('<div class="oauth"><button type="button" data-provider="Passkey">@@ Passkey</button>'
            '<button type="button" data-provider="Google">@@ Google</button>'
            '<button type="button" data-provider="Wallet">@@ Wallet</button></div>',
            ic("shield", "ic"), ic("crest", "ic"), ic("wallet", "ic")))
su.append('<div class="auth-alt">Already have an account? <a href="signin.html">Sign in</a></div>')
su.append('</div></div></main>')

SIGNUP_JS = AUTH_JS + r"""
var pw = fld('password'), meter = document.getElementById('pwMeter'), plab = document.getElementById('pwLabel');
var WORDS = ['Too short', 'Weak — add length', 'Fair — add a number or symbol', 'Strong', 'Very strong'];
if(pw) pw.addEventListener('input', function(){
  var s = scorePw(pw.value);
  meter.querySelectorAll('i').forEach(function(b, i){
    b.className = i < s ? (s <= 1 ? 'low' : (s === 2 ? 'mid' : 'on')) : '';
  });
  plab.textContent = 'Strength — ' + WORDS[s].toLowerCase() + '.';
  clearErr('password');
});
var uf = document.getElementById('signupForm');
if(uf) uf.addEventListener('submit', function(e){
  e.preventDefault();
  var nm = fld('name').value.trim(), em = fld('email').value, p = fld('password').value;
  var ok = true;
  if(nm.length < 2) ok = bad('name'); else good('name');
  if(!validEmail(em)) ok = bad('email'); else good('email');
  if(scorePw(p) < 2) ok = bad('password'); else good('password');
  if(!fld('terms').checked){
    ok = false;
    showToast('You need to accept the terms before an account can be opened.', 'error');
  }
  if(!ok){ if(fld('terms').checked) showToast('Check the highlighted fields and try again.', 'error'); return; }
  FT.signUp({ name: nm, email: em.trim(), region: fld('country').value });
  showToast('Account created. Let us get you set up.', 'success');
  setTimeout(function(){ window.location.href = 'onboarding.html'; }, 700);
});
['name','email'].forEach(function(id){
  var el = fld(id); if(el) el.addEventListener('input', function(){ clearErr(id); });
});
"""

page("signup.html", "Create account — Fantrade", "".join(su), SIGNUP_JS, chrome=False)

print("built signin.html + signup.html")

# ══════════════════════════════════════════════════════════════════
# ONBOARDING — four steps from a fresh account to a fielded club
# ══════════════════════════════════════════════════════════════════
OB_CSS = """
.forms{display:flex;gap:8px;flex-wrap:wrap}
.forms button{flex:1;min-width:92px;border:1px solid var(--hair);background:rgba(255,255,255,.03);color:var(--dim);
  border-radius:14px;padding:14px 0;font-family:'JetBrains Mono',monospace;font-size:14px;cursor:pointer;
  box-shadow:var(--inset);transition:all .6s var(--ease)}
.forms button[aria-pressed="true"]{background:var(--lime);border-color:var(--lime);color:#0A0D03}
.forms button:hover:not([aria-pressed="true"]){color:var(--ink);border-color:var(--hair-2)}
.swatches{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}
.sw{width:36px;height:36px;border-radius:12px;border:1px solid var(--hair);cursor:pointer;box-shadow:var(--inset);
  transition:transform .6s var(--ease)}
.sw:hover,.sw[aria-pressed="true"]{transform:scale(1.08)}
.sw[aria-pressed="true"]{border-color:var(--ink)}
.grant{border:1px solid rgba(196,248,42,.3);border-radius:20px;padding:28px 24px;text-align:center;
  background:radial-gradient(ellipse at 50% 130%,rgba(196,248,42,.16),rgba(196,248,42,.03) 62%);
  box-shadow:var(--inset);margin-bottom:20px}
.grant .k{font-weight:600;font-size:9.5px;letter-spacing:.2em;color:#95ad44;text-transform:uppercase}
.grant .v{font-family:'JetBrains Mono',monospace;font-weight:200;font-size:clamp(34px,4.4vw,50px);
  color:var(--lime);line-height:1;margin:14px 0 10px;letter-spacing:-.035em}
.grant p{font-size:12.5px;color:var(--dim);font-weight:300;margin:0 auto;max-width:42ch;line-height:1.6}
.ob-h4{font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 800;text-transform:uppercase;
  font-size:19px;margin:0 0 8px}
.ob-p{font-size:13px;color:var(--dim);font-weight:300;margin:0 0 24px;line-height:1.6;max-width:56ch}
"""

STARTERS = [("$Saka", "Bukayo Saka", "RW · Arsenal", 48.20, False),
            ("$Bruno", "Bruno Fernandes", "CAM · Man United", 39.75, False),
            ("$Haaland", "Erling Haaland", "ST · Man City", 71.40, False),
            ("$Saliba", "William Saliba", "CB · Arsenal", 33.80, False),
            ("$Musiala", "Jamal Musiala", "CAM · Bayern", 46.70, False),
            ("$Arteta", "Mikel Arteta", "Coach · Arsenal", 22.05, True)]

STEPS = [("01", "Manager profile"), ("02", "Fund your wallet"),
         ("03", "First asset"), ("04", "Name your club")]

ob = [T('<main><section class="app-head" style="padding-bottom:0"><div class="wrap">'
        '<span hidden>@@</span>'
        '<h1 data-reveal>Set up<br>your desk</h1>'
        '<p class="lede" data-reveal>Four steps. At the end of them you own shares, you have a club with a name '
        'and a shape, and you are eligible for the next settlement window.</p>'
        '</div></section><section style="padding:44px 0 120px"><div class="wrap"><div class="bento">',
        ic("formation", "ic"))]

# ── wizard column ──
ob.append('<div class="bezel c8" data-reveal><div class="core pad"><div class="prog" id="obProg">')
for i, (n, l) in enumerate(STEPS):
    ob.append(T('<div class="st@@" data-step="@@"><div class="n">Step @@</div><div class="l">@@</div></div>',
                " on" if i == 0 else "", i, n, l))
ob.append('</div>')

# step 1
ob.append('<div class="step-pane on" data-pane="0">'
          '<h4 class="ob-h4">Who is managing?</h4>'
          '<p class="ob-p">Your handle is what the league table shows next to your club. '
          'It can be changed once per season.</p>')
ob.append(tf("Manager handle", "handle", "text", "@alex_trader", "user", "",
             "Handles are 3–20 characters, letters, numbers and underscores."))
ob.append('<div class="tf-row">')
ob.append(sel("Region", "region", COUNTRIES, "flag"))
ob.append(sel("Home league", "league", ["*Premier League", "La Liga", "Serie A", "Bundesliga",
                                        "Ligue 1", "Nigeria Premier Football League", "Eredivisie", "Primeira Liga"],
              "stadium"))
ob.append('</div>')
ob.append('<div class="hint" style="color:var(--faint);font-size:11px;margin-top:4px">'
          'Your home league sets the default settlement window and the fixtures shown first on your matchday board.</div>')
ob.append('</div>')

# step 2
ob.append(T('<div class="step-pane" data-pane="1">'
            '<h4 class="ob-h4">Fund your wallet</h4>'
            '<p class="ob-p">Everything on Fantrade settles in $FTR — share purchases, swap fees, matchday stakes '
            'and payouts. New managers start with a prototype grant.</p>'
            '<div class="grant"><div class="k">Opening grant</div><div class="v">50,000<span '
            'style="font-size:17px;color:var(--faint);letter-spacing:0"> $FTR</span></div>'
            '<p>Roughly £4,030 at today\'s rate. Enough for a starting eleven and your first Elite-tier entry.</p></div>'
            '@@'
            '<div class="k-label" style="margin-top:26px">Add more (optional)</div>'
            '<div class="field"><label>You pay</label><input id="obFiat" value="0" inputmode="numeric"></div>'
            '<div class="quick"><button data-f="100">£100</button><button data-f="250">£250</button>'
            '<button data-f="500">£500</button><button data-f="1000">£1,000</button></div>'
            '<div class="line"><span>Converted at 12.40 $FTR / £1, less 0.5% fee</span><b id="obConv">0 $FTR</b></div>'
            '</div>',
            btn("Claim 50,000 $FTR", tag="button",
                extra='id="obClaim" style="width:100%;justify-content:space-between"')))

# step 3
ob.append('<div class="step-pane" data-pane="2">'
          '<h4 class="ob-h4">Buy your first asset</h4>'
          '<p class="ob-p">Pick one to start with. Every asset has a fixed supply of 10,000,000 shares, so what you '
          'hold is a real fraction of that player or coach — not a card, not a copy.</p>'
          '<div class="picks" id="obPicks">')
for sym, nm, role, px, coach in STARTERS:
    ob.append(T('<button class="pick" type="button" data-sym="@@" data-nm="@@" data-px="@@" data-coach="@@">'
                '<span class="coin@@" style="margin-bottom:12px">@@</span>'
                '<div class="sym">@@</div><div class="nm">@@</div><div class="px">@@ <span '
                'style="font-size:10px;color:var(--faint)">$FTR</span></div></button>',
                sym, nm, px, "1" if coach else "0",
                " am" if coach else "", ic("whistle" if coach else "boot", "ic"),
                sym, role, "%.2f" % px))
ob.append('</div>')
ob.append('<div class="field" style="margin-top:18px"><label>Shares</label>'
          '<input id="obShares" value="1,000" inputmode="numeric"></div>'
          '<div class="quick"><button data-s="250">250</button><button data-s="500">500</button>'
          '<button data-s="1000">1,000</button><button data-s="2500">2,500</button></div>'
          '<div class="line"><span>Subtotal</span><b id="obSub">—</b></div>'
          '<div class="line"><span>Protocol fee (0.4%)</span><b id="obFee">—</b></div>'
          '<div class="line"><span>Total</span><b id="obTot">—</b></div>')
ob.append(btn("Buy shares", tag="button", extra='id="obBuy" style="width:100%;justify-content:space-between;margin-top:18px"'))
ob.append('</div>')

# step 4
ob.append('<div class="step-pane" data-pane="3">'
          '<h4 class="ob-h4">Name your club</h4>'
          '<p class="ob-p">Your Dream Club is the portfolio you field on a matchday. You can rebuild the eleven any '
          'time — the name and colours are what the league table remembers.</p>')
ob.append(tf("Club name", "clubName", "text", "Zero FC", "crest", "",
             "2–24 characters. This appears on the global leaderboard."))
ob.append('<div class="k-label" style="margin-top:22px">Starting formation</div>'
          '<div class="forms" id="obForms">'
          '<button type="button" aria-pressed="true">4-3-3</button>'
          '<button type="button" aria-pressed="false">4-4-2</button>'
          '<button type="button" aria-pressed="false">3-5-2</button>'
          '<button type="button" aria-pressed="false">4-2-3-1</button></div>')
ob.append('<div class="k-label" style="margin-top:24px">Club colour</div><div class="swatches" id="obSw">'
          '<button class="sw" type="button" aria-pressed="true" data-c="#C4F82A" data-n="Lime" '
          'style="background:linear-gradient(160deg,#C4F82A,#83b300)" aria-label="Lime"></button>'
          '<button class="sw" type="button" aria-pressed="false" data-c="#FF6A1F" data-n="Amber" '
          'style="background:linear-gradient(160deg,#FF6A1F,#b33f06)" aria-label="Amber"></button>'
          '<button class="sw" type="button" aria-pressed="false" data-c="#4DA6FF" data-n="Azure" '
          'style="background:linear-gradient(160deg,#4DA6FF,#0b5fae)" aria-label="Azure"></button>'
          '<button class="sw" type="button" aria-pressed="false" data-c="#FF5E8A" data-n="Rose" '
          'style="background:linear-gradient(160deg,#FF5E8A,#a81f45)" aria-label="Rose"></button>'
          '<button class="sw" type="button" aria-pressed="false" data-c="#F4F6F1" data-n="Chalk" '
          'style="background:linear-gradient(160deg,#F4F6F1,#8f938b)" aria-label="Chalk"></button></div>')
ob.append('</div>')

ob.append(T('<div class="wiz-foot">@@@@<span class="sp" id="obCount">Step 1 of 4</span></div>',
            btn("Back", "btn-glass", tag="button", extra='id="obBack" disabled style="opacity:.4"'),
            btn("Continue", tag="button", extra='id="obNext"')))
ob.append('</div></div>')

# ── summary column ──
ob.append(T('<div class="bezel c4" data-reveal><div class="core pad">'
            '<div class="k-label">Your setup so far</div>'
            '<div class="b-row"><span>Manager</span><b data-bind="name">Alex Morgan</b></div>'
            '<div class="b-row"><span>Handle</span><b id="sumHandle">—</b></div>'
            '<div class="b-row"><span>Region</span><b id="sumRegion">United Kingdom</b></div>'
            '<div class="b-row"><span>Wallet</span><b id="sumWallet">—</b></div>'
            '<div class="b-row"><span>First asset</span><b id="sumAsset">—</b></div>'
            '<div class="b-row"><span>Club</span><b id="sumClub">—</b></div>'
            '<div class="b-row total"><span>Ready for</span><b>Gameweek 28</b></div>'
            '<div class="k-label" style="margin-top:30px">What happens next</div>'
            '<div class="rowlink">@@ Fill the other ten positions</div>'
            '<div class="rowlink">@@ Slot a coach for the synergy bonus</div>'
            '<div class="rowlink">@@ Pick a market tier and stake</div>'
            '<div class="rowlink">@@ Settle on the final whistle</div>'
            '<p style="font-size:11.5px;color:var(--faint);font-weight:300;margin-top:22px;line-height:1.6">'
            'Nothing here is final. You can rebuild the club, sell the shares and change the handle from Settings '
            'at any point before a round locks.</p>'
            '</div></div>',
            ic("formation", "ic"), ic("whistle", "ic"), ic("bolt", "ic"), ic("timer", "ic")))

ob.append('</div></div></section></main>')

OB_JS = r"""
var step = 0, PANES = document.querySelectorAll('.step-pane'), STEPS_N = PANES.length;
var claimed = false, picked = null, addFtr = 0;
function el(id){ return document.getElementById(id); }
function wrap(id){ return document.getElementById('f-' + id); }
function render(){
  PANES.forEach(function(p, i){ p.classList.toggle('on', i === step); });
  document.querySelectorAll('#obProg .st').forEach(function(s, i){
    s.classList.toggle('on', i === step);
    s.classList.toggle('done', i < step);
  });
  el('obBack').disabled = step === 0;
  el('obBack').style.opacity = step === 0 ? '.4' : '1';
  el('obCount').textContent = 'Step ' + (step + 1) + ' of ' + STEPS_N;
  el('obNext').childNodes[0].nodeValue = step === STEPS_N - 1 ? 'Enter the arena' : 'Continue';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function sum(){
  var s = FT.getState();
  el('sumHandle').textContent = el('handle').value.trim() || '—';
  el('sumRegion').textContent = el('region').value;
  el('sumWallet').textContent = s.wallet.balance.toLocaleString('en-US') + ' $FTR';
  el('sumAsset').textContent = picked ? picked.sym : '—';
  el('sumClub').textContent = (el('clubName').value.trim() || '—') + ' · ' + formation;
}
// step 1
el('handle').addEventListener('input', sum);
el('region').addEventListener('change', sum);

// step 2 — grant + optional top-up
el('obClaim').addEventListener('click', function(){
  if(claimed){ showToast('The opening grant has already been claimed.', 'info'); return; }
  claimed = true;
  FT.depositFtr(50000);
  el('obClaim').style.opacity = '.5';
  el('obClaim').childNodes[0].nodeValue = 'Grant claimed';
  showToast('50,000 $FTR credited to your wallet.', 'success');
  sum();
});
function num(v){ return parseInt(String(v).replace(/[^0-9]/g, ''), 10) || 0; }
function convPreview(){
  var gbp = num(el('obFiat').value);
  addFtr = Math.round(gbp * 12.40 * 0.995);
  el('obConv').textContent = addFtr.toLocaleString('en-US') + ' $FTR';
}
el('obFiat').addEventListener('input', convPreview);
document.querySelectorAll('.quick button[data-f]').forEach(function(b){
  b.addEventListener('click', function(){
    el('obFiat').value = num(b.dataset.f).toLocaleString('en-US');
    convPreview();
  });
});

// step 3 — first asset
document.querySelectorAll('#obPicks .pick').forEach(function(p){
  p.addEventListener('click', function(){
    document.querySelectorAll('#obPicks .pick').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    p.setAttribute('aria-pressed', 'true');
    picked = { sym: p.dataset.sym, nm: p.dataset.nm, px: parseFloat(p.dataset.px), coach: p.dataset.coach === '1' };
    cost(); sum();
  });
});
function cost(){
  if(!picked){ el('obSub').textContent = el('obFee').textContent = el('obTot').textContent = '—'; return; }
  var sh = num(el('obShares').value), sub = sh * picked.px, fee = sub * 0.004;
  el('obSub').textContent = Math.round(sub).toLocaleString('en-US') + ' $FTR';
  el('obFee').textContent = Math.round(fee).toLocaleString('en-US') + ' $FTR';
  el('obTot').textContent = Math.round(sub + fee).toLocaleString('en-US') + ' $FTR';
}
el('obShares').addEventListener('input', cost);
document.querySelectorAll('.quick button[data-s]').forEach(function(b){
  b.addEventListener('click', function(){
    el('obShares').value = num(b.dataset.s).toLocaleString('en-US');
    cost();
  });
});
el('obBuy').addEventListener('click', function(){
  if(!picked){ showToast('Pick an asset first.', 'error'); return; }
  var sh = num(el('obShares').value);
  if(sh < 1){ showToast('Enter how many shares you want.', 'error'); return; }
  try {
    var r = FT.executeTrade('buy', picked.sym, picked.nm, sh, picked.px, picked.coach);
    showToast(sh.toLocaleString('en-US') + ' ' + picked.sym + ' bought for ' + r.total.toLocaleString('en-US') + ' $FTR.', 'success');
    sum();
  } catch(err){ showToast(err.message, 'error'); }
});

// step 4 — club identity
var formation = '4-3-3', colors = ['#C4F82A', '#83b300'], colorName = 'Lime';
document.querySelectorAll('#obForms button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#obForms button').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    formation = b.textContent.trim();
    sum();
  });
});
document.querySelectorAll('#obSw .sw').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#obSw .sw').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    colors = [b.dataset.c, b.dataset.c]; colorName = b.dataset.n;
  });
});
el('clubName').addEventListener('input', sum);

// navigation
function validateStep(){
  if(step === 0){
    var h = el('handle').value.trim().replace(/^@/, '');
    if(!/^[A-Za-z0-9_]{3,20}$/.test(h)){ wrap('handle').classList.add('bad'); return false; }
    wrap('handle').classList.remove('bad');
    return true;
  }
  if(step === 1){
    if(!claimed){ showToast('Claim the opening grant to continue.', 'error'); return false; }
    if(addFtr > 0){ FT.convertGbp(num(el('obFiat').value)); addFtr = 0; el('obFiat').value = '0'; convPreview(); }
    return true;
  }
  if(step === 2){
    if(!FT.getState().holdings[picked ? picked.sym : '']){
      showToast('Buy your first asset to continue — you can sell it later.', 'error');
      return false;
    }
    return true;
  }
  var cn = el('clubName').value.trim();
  if(cn.length < 2 || cn.length > 24){ wrap('clubName').classList.add('bad'); return false; }
  return true;
}
el('obBack').addEventListener('click', function(){ if(step > 0){ step--; render(); } });
el('obNext').addEventListener('click', function(){
  if(!validateStep()) return;
  if(step < STEPS_N - 1){ step++; render(); sum(); return; }
  FT.completeOnboarding({
    handle: '@' + el('handle').value.trim().replace(/^@/, ''),
    region: el('region').value,
    league: el('league').value,
    clubName: el('clubName').value.trim(),
    formation: formation,
    colors: colors,
    colorName: colorName
  });
  showToast('Setup complete. ' + el('clubName').value.trim() + ' is live.', 'success');
  setTimeout(function(){ window.location.href = 'dashboard.html'; }, 800);
});
el('handle').value = FT.getState().user.handle;
el('clubName').value = FT.getState().club.name;
render(); sum(); cost();
"""

page("onboarding.html", "Onboarding — Fantrade", "".join(ob), OB_JS, OB_CSS)
print("built onboarding.html")

# ══════════════════════════════════════════════════════════════════
# DASHBOARD — the signed-in home
# ══════════════════════════════════════════════════════════════════
DASH_CSS = """
.fx{display:grid;grid-template-columns:88px 1fr auto;gap:16px;align-items:center;padding:16px 24px;
  border-bottom:1px solid rgba(255,255,255,.05);transition:background .6s var(--ease)}
.fx:last-child{border-bottom:0}
.fx:hover{background:rgba(255,255,255,.022)}
.fx .code{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--faint);letter-spacing:.06em;
  border:1px solid var(--hair);border-radius:9px;padding:7px 0;text-align:center;background:rgba(255,255,255,.03)}
.fx .tie{font-size:14px;font-weight:500}
.fx .gr{font-size:11px;color:var(--faint);margin-top:6px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.fx .gr em{font-style:normal;font-family:'JetBrains Mono',monospace;color:var(--dim)}
.fx .fpv{text-align:right;font-family:'JetBrains Mono',monospace;font-size:15px;color:var(--lime);
  font-weight:300;white-space:nowrap}
.fx .fpv em{font-style:normal;font-family:Montserrat,sans-serif;font-weight:600;font-size:8.5px;
  letter-spacing:.16em;color:var(--faint);text-transform:uppercase;white-space:nowrap}
.mv{border-bottom:1px solid rgba(255,255,255,.045)}
.mv:last-child{border-bottom:0}
.mv:hover{background:transparent}
.crest-lg{width:52px;height:57px;flex:none;clip-path:polygon(0 0,100% 0,100% 66%,50% 100%,0 66%);
  display:grid;place-items:center;font-family:Archivo;font-variation-settings:'wdth' 100,'wght' 900;
  font-size:15px;color:#0A0D03;filter:drop-shadow(0 8px 18px rgba(196,248,42,.3))}
@media (max-width:768px){
  .fx{grid-template-columns:72px 1fr;gap:12px;padding:14px}
  .fx .fpv{text-align:left;grid-column:2}
  .mv{padding-left:0!important;padding-right:0!important}
}
"""

FIXTURES = [("ARS·CHE", "Arsenal vs Chelsea", "Emirates Stadium · Sat 17:30",
             [("$Saka", "RW"), ("$Saliba", "CB")], "140–210"),
            ("MCI·NEW", "Man City vs Newcastle", "Etihad Stadium · Sat 20:00",
             [("$Haaland", "ST")], "95–165"),
            ("MUN·EVE", "Man United vs Everton", "Old Trafford · Sun 14:00",
             [("$Bruno", "CAM · captain 1.5x")], "180–240"),
            ("RMA·ATM", "Real Madrid vs Atlético", "Santiago Bernabéu · Sun 21:00",
             [("$Vinicius", "LW")], "110–180")]

# (symbol, name, price, 24h %, index into the shared ASSETS ticker array in JS_SHELL)
MOVERS = [("$Jackson", "Nicolas Jackson", 14.85, 11.2, 8), ("$Saka", "Bukayo Saka", 48.20, 6.4, 0),
          ("$Musiala", "Jamal Musiala", 46.70, 5.1, 5), ("$Arteta", "Mikel Arteta", 22.05, 4.9, 9),
          ("$Haaland", "Erling Haaland", 71.40, -1.8, 1), ("$Pedri", "Pedri González", 41.15, -0.9, 6)]

da = [T('<main><section class="app-head"><div class="wrap"><div class="head-row">'
        '<div><h1 data-reveal>Evening, <span data-bind="first">Alex</span></h1></div>'
        '<div class="acts" data-reveal>@@@@</div></div>'
        '</div></section>',
        btn("Enter matchday", href="fanplay.html"),
        btn("Buy shares", "btn-glass", "exchange.html"))]

da.append('<section style="padding:10px 0 120px"><div class="wrap"><div class="bento">')

# net worth
da.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
            '<div class="k-label">Net worth</div>'
            '<div class="bal-big"><span data-bind="net">370,300</span><small> $FTR</small></div>'
            '<div class="bal-delta" id="dashDelta">@@<span>18.4% over 30 days</span>'
            '<em>+6,200 settled this week</em></div>'
            '<div class="bal-chart" id="dashChart"></div>'
            '<div class="range" id="dashRange" style="margin-bottom:22px">'
            '<button type="button" aria-pressed="false" data-r="1W">1W</button>'
            '<button type="button" aria-pressed="true" data-r="1M">1M</button>'
            '<button type="button" aria-pressed="false" data-r="3M">3M</button>'
            '<button type="button" aria-pressed="false" data-r="All">All</button></div>'
            '<div class="alloc" id="dashAlloc"><i style="width:66%;background:linear-gradient(90deg,#8fbe00,#C4F82A)"></i>'
            '<i style="width:25%;background:#4DA6FF"></i>'
            '<i style="width:9%;background:rgba(255,255,255,.34)"></i></div>'
            '<div class="b-row"><span>@@ Held in shares (mark to market)</span><b data-bind="assets">245,800</b></div>'
            '<div class="b-row"><span>@@ Liquid $FTR</span><b data-bind="balance">128,450</b></div>'
            '<div class="b-row"><span>@@ Locked in entries</span><b data-bind="locked">5,000</b></div>'
            '<div class="b-row total"><span>Season payouts received</span><b data-bind="earned">19,640</b></div>'
            '<div style="display:flex;gap:10px;margin-top:22px;flex-wrap:wrap">@@@@</div>'
            '</div></div>',
            ic("arrow", "ic"),
            '<i style="display:inline-block;width:8px;height:8px;border-radius:3px;background:#C4F82A;margin-right:9px"></i>',
            '<i style="display:inline-block;width:8px;height:8px;border-radius:3px;background:#4DA6FF;margin-right:9px"></i>',
            '<i style="display:inline-block;width:8px;height:8px;border-radius:3px;background:rgba(255,255,255,.34);margin-right:9px"></i>',
            btn("Portfolio & ledger", href="portfolio.html", extra='style="flex:1;justify-content:space-between"'),
            btn("Open wallet", "btn-glass", "ftr.html", extra='style="flex:1;justify-content:space-between"')))

# club card
da.append(T('<div class="bezel c4" data-reveal><div class="core pad">'
            '<div class="k-label">Your Dream Club</div>'
            '<div style="display:flex;align-items:center;gap:16px;margin-bottom:6px">'
            '<div class="crest-lg" id="dashCrest" style="background:linear-gradient(160deg,#C4F82A,#83b300)">ZF</div>'
            '<div><div style="font-family:Archivo;font-variation-settings:\'wdth\' 125,\'wght\' 900;'
            'text-transform:uppercase;font-size:23px;line-height:1" data-bind="club">Zero FC</div>'
            '<div class="sub-line" style="letter-spacing:.14em;text-transform:uppercase">'
            '<span data-bind="formation">4-3-3</span> · Apex division</div></div></div>'
            '<div class="mini-grid" style="margin-top:22px">'
            '<div class="mini"><div class="k">Global rank</div><div class="v lime" data-bind="rank">#124</div></div>'
            '<div class="mini"><div class="k">Season FP</div><div class="v" data-bind="fp">8,420</div></div>'
            '<div class="mini"><div class="k">Club valuation</div><div class="v" data-bind="clubvalue">245,800</div></div>'
            '<div class="mini"><div class="k">Multiplier</div><div class="v amber" data-bind="boost">15.0%</div></div>'
            '</div>'
            '<div class="rowlink" style="margin-top:22px">@@ 11 of 11 starters owned<b>Verified</b></div>'
            '<div class="rowlink">@@ 6 of 6 bench slots filled<b>Verified</b></div>'
            '<div class="rowlink">@@ Coach matches your shape<b style="color:var(--amber)">+5.0%</b></div>'
            '<div style="margin-top:22px">@@</div>'
            '</div></div>',
            ic("check", "ic"), ic("subs", "ic"), ic("whistle", "ic"),
            btn("Open club", "btn-glass", "clubs.html", extra='style="width:100%;justify-content:space-between"')))

# countdown
da.append(T('<div class="bezel c3" data-reveal><div class="core pad">'
            '<div class="k-label">Gameweek 28 locks in</div>'
            '<div class="clock" id="lockClock">'
            '<div class="u"><b id="cdH">03</b><span>Hrs</span></div>'
            '<div class="u"><b id="cdM">14</b><span>Min</span></div>'
            '<div class="u"><b id="cdS">22</b><span>Sec</span></div></div>'
            '<div class="k-label" style="margin-top:26px">Last round</div>'
            '<div class="b-row"><span>Matchday 27 finish</span><b>18th / 1,420</b></div>'
            '<div class="b-row"><span>Points scored</span><b>812 FP</b></div>'
            '<div class="b-row total"><span>Returned</span><b style="color:var(--lime)">+6,200 $FTR</b></div>'
            '<div style="margin-top:22px">@@</div>'
            '</div></div>',
            btn("Enter FanPlay", href="fanplay.html", extra='style="width:100%;justify-content:space-between"')))

# matchday board
da.append(T('<div class="bezel c7" data-reveal><div class="core">'
            '<div style="padding:30px 24px 20px;display:flex;align-items:center;gap:14px;flex-wrap:wrap">'
            '<span class="ibox">@@</span><div><div style="font-family:Archivo;'
            'font-variation-settings:\'wdth\' 120,\'wght\' 800;text-transform:uppercase;font-size:17px">'
            'Matchday board</div><div class="sub-line">Gameweek 28</div></div>'
            '<span class="tag lime" style="margin-left:auto">@@ 4 fixtures live</span></div>',
            ic("calendar", "ic-lg"), ic("pulse", "ic")))
for code, tie, meta, assets, fp in FIXTURES:
    chips = "".join('<em>%s</em><span style="color:var(--faint)">%s</span>' % (s, r) for s, r in assets)
    da.append(T('<div class="fx"><div class="code">@@</div>'
                '<div><div class="tie">@@</div><div class="gr">@@</div>'
                '<div class="gr" style="margin-top:4px;color:var(--faint)">@@</div></div>'
                '<div class="fpv">@@ <em>Expected FP</em></div></div>',
                code, tie, chips, meta, fp))
da.append(T('<div style="padding:20px 24px 28px;display:flex;gap:12px;align-items:center;flex-wrap:wrap">'
            '<span style="font-size:11.5px;color:var(--faint);font-weight:300;white-space:nowrap">'
            'Projected club total 450–780 FP</span>'
            '<span style="margin-left:auto">@@</span></div>'
            '</div></div>',
            btn("See scoring rules", "btn-glass", "how-it-works.html#rules",
                extra='style="padding:7px 7px 7px 18px;font-size:11px"')))

# movers
da.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
            '<div style="display:flex;align-items:center;gap:12px;margin-bottom:18px">'
            '<div class="k-label" style="margin:0">Today\'s movers</div>'
            '<a href="exchange.html" style="margin-left:auto;font-size:11px;color:var(--lime)">Open exchange</a></div>'))
for sym, nm, px, d, idx in MOVERS:
    coach = sym == "$Arteta"
    da.append(T('<div class="arow mv" data-i="@@" style="padding-left:0;padding-right:0">'
                '<div class="who"><span class="coin@@">@@</span>'
                '<div style="min-width:0"><div class="nm">@@</div><div class="qt">@@</div></div></div>'
                '<div data-spark="@@"></div>'
                '<div><div class="val" data-px>@@</div>'
                '<div class="chg @@" data-dx>@@</div></div></div>',
                idx, " am" if coach else "", ic("whistle" if coach else "boot", "ic"),
                sym, nm, "1" if d >= 0 else "0", "%.2f" % px,
                "up" if d >= 0 else "down", ("+" if d >= 0 else "") + "%.1f%%" % d))
da.append(T('<div style="margin-top:20px">@@</div></div></div>',
            btn("All 420 markets", "btn-glass", "exchange.html",
                extra='style="width:100%;justify-content:space-between"')))

# quick actions
da.append(T('<div class="c12" data-reveal><div class="qa">'
            '<a href="exchange.html"><span class="ibox">@@</span><div><b>Trade</b>'
            '<span>420 markets</span></div></a>'
            '<a href="clubs.html"><span class="ibox">@@</span><div><b>Rebalance XI</b>'
            '<span>4-3-3 · locked Sat 17:30</span></div></a>'
            '<a href="fanplay.html"><span class="ibox am">@@</span><div><b>Stake a round</b>'
            '<span>Gameweek 28 open</span></div></a>'
            '<a href="leaderboard.html"><span class="ibox">@@</span><div><b>League table</b>'
            '<span>#124 of 1,420</span></div></a>'
            '</div></div>',
            ic("candle", "ic-lg"), ic("formation", "ic-lg"), ic("bolt", "ic-lg"), ic("rank", "ic-lg")))

# activity + entries
da.append(T('<div class="bezel c7" data-reveal><div class="core">'
            '<div style="padding:30px 24px 18px;display:flex;align-items:center;gap:12px">'
            '<div class="k-label" style="margin:0">Recent activity</div>'
            '<a href="notifications.html" style="margin-left:auto;font-size:11px;color:var(--lime)">'
            'All activity (<span data-unread>3</span> unread)</a></div>'
            '<div class="dt" id="dashLedger"></div></div></div>'))

da.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
            '<div class="k-label">Active entries</div>'
            '<div id="dashEntries"></div>'
            '<div class="k-label" style="margin-top:28px">Responsible play</div>'
            '<div class="b-row"><span>Weekly stake cap</span><b id="dashCap">5,000 $FTR</b></div>'
            '<div class="b-row"><span>Staked this week</span><b>2,500 $FTR</b></div>'
            '<div class="supply"><i style="width:50%"></i></div>'
            '<div style="margin-top:18px">@@</div>'
            '</div></div>',
            btn("Manage limits", "btn-glass", "settings-play.html",
                extra='style="width:100%;justify-content:space-between"')))

da.append('</div></div></section></main>')

DASH_JS = r"""
// greeting by local hour
(function(){
  var h = new Date().getHours();
  var word = h < 12 ? 'Morning' : (h < 18 ? 'Afternoon' : 'Evening');
  var head = document.querySelector('.app-head h1');
  if(head) head.innerHTML = word + ', <span data-bind="first">Manager</span>';
  FT.syncUI();
})();

// club crest takes the saved club colour
(function(){
  var s = FT.getState(), c = document.getElementById('dashCrest');
  if(!c) return;
  c.style.background = 'linear-gradient(160deg,' + s.club.colors[0] + ',' + (s.club.colors[1] || s.club.colors[0]) + ')';
  c.style.color = s.club.colorName === 'Chalk' ? '#0A0D03' : '#0A0D03';
  c.textContent = s.club.name.split(/\s+/).map(function(w){ return w.charAt(0).toUpperCase(); }).join('').slice(0, 3);
})();

// sparklines on the movers list
document.querySelectorAll('[data-spark]').forEach(function(d){
  d.innerHTML = spark(d.dataset.spark === '1', 88, 26);
});
liveTicks('.mv');

// net-worth chart, same component as the wallet
var DSERIES = { '1W': series(28, 0.4, 3.0, 19), '1M': series(36, 1.1, 4.8, 53),
                '3M': series(44, 1.7, 6.4, 83), 'All': series(52, 2.4, 8.6, 127) };
var DDELTA = { '1W': '4.2% this week', '1M': '18.4% over 30 days',
               '3M': '41.7% this quarter', 'All': '212.5% all time' };
function dpaint(r){
  drawArea(document.getElementById('dashChart'), DSERIES[r], true);
  document.querySelector('#dashDelta span').textContent = DDELTA[r];
}
document.querySelectorAll('#dashRange button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#dashRange button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
    b.setAttribute('aria-pressed', 'true');
    dpaint(b.dataset.r);
  });
});
dpaint('1M');

// countdown to the gameweek lock
(function(){
  var end = Date.now() + (3 * 3600 + 14 * 60 + 22) * 1000;
  function pad(n){ return (n < 10 ? '0' : '') + n; }
  function tick(){
    var d = Math.max(0, end - Date.now()), t = Math.floor(d / 1000);
    var e = document.getElementById('cdH'); if(!e) return;
    e.textContent = pad(Math.floor(t / 3600));
    document.getElementById('cdM').textContent = pad(Math.floor(t / 60) % 60);
    document.getElementById('cdS').textContent = pad(t % 60);
  }
  tick(); setInterval(tick, 1000);
})();

// allocation bar reflects the real split
function renderAlloc(){
  var s = FT.getState(), bar = document.getElementById('dashAlloc');
  if(!bar) return;
  var held = FT.holdingsValue(), liq = s.wallet.balance, lock = s.wallet.locked;
  var tot = held + liq + lock || 1, b = bar.querySelectorAll('i');
  b[0].style.width = (held / tot * 100).toFixed(1) + '%';
  b[1].style.width = (liq / tot * 100).toFixed(1) + '%';
  b[2].style.width = (lock / tot * 100).toFixed(1) + '%';
}
renderAlloc();
window.addEventListener('fantrade:statechange', renderAlloc);

// ledger + entries render from state
var TONE = { BUY:'lime', SELL:'red', STAKE:'amber', PAYOUT:'lime', CONVERT:'', DEPOSIT:'lime' };
var TICON = { BUY:'candle', SELL:'candle', STAKE:'bolt', PAYOUT:'trophy', CONVERT:'swap', DEPOSIT:'coin' };
function renderLedger(){
  var s = FT.getState(), box = document.getElementById('dashLedger');
  if(!box) return;
  var rows = s.transactions.slice(0, 6).map(function(t){
    var sign = (t.type === 'BUY' || t.type === 'STAKE') ? '-' : '+';
    return '<div class="dr" style="grid-template-columns:120px 1fr 130px">'
      + '<div><span class="tag ' + (TONE[t.type] || '') + '"><svg class="ic" aria-hidden="true"><use href="#i-'
      + (TICON[t.type] || 'receipt') + '"/></svg>' + t.type + '</span></div>'
      + '<div><div style="font-size:13px">' + t.asset + '</div><div class="sub-line">' + t.time + '</div></div>'
      + '<div class="pl ' + (sign === '+' ? 'up' : 'down') + '" style="text-align:right">' + sign
      + Math.round(t.total).toLocaleString('en-US') + '</div></div>';
  }).join('');
  box.innerHTML = '<div class="dh" style="grid-template-columns:120px 1fr 130px"><span>Event</span>'
    + '<span>Detail</span><span style="text-align:right">$FTR</span></div>' + rows;
}
function renderEntries(){
  var s = FT.getState(), box = document.getElementById('dashEntries');
  if(!box) return;
  if(!s.fanplay.activeEntries.length){
    box.innerHTML = '<div class="empty-state" style="padding:32px 0">'
      + '<svg class="ic-xl" aria-hidden="true"><use href="#i-bolt"/></svg>'
      + 'No live entries. Stake the club before the lock to score this window.</div>';
    return;
  }
  box.innerHTML = s.fanplay.activeEntries.map(function(e){
    return '<div style="border:1px solid var(--hair);background:rgba(255,255,255,.03);border-radius:16px;'
      + 'padding:16px 18px;margin-bottom:10px;box-shadow:var(--inset)">'
      + '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">'
      + '<span class="tag ' + (e.mode === 'Dream Club' ? 'lime' : '') + '">' + e.mode + '</span>'
      + '<span class="tag amber">' + e.tier + ' · ' + e.mult.toFixed(1) + 'x</span>'
      + '<span style="margin-left:auto;font-family:\'JetBrains Mono\',monospace;font-size:13px">'
      + e.stake.toLocaleString('en-US') + ' $FTR</span></div>'
      + '<div class="b-row" style="border:0;padding:10px 0 0"><span>' + e.target + '</span><b>'
      + e.projectedFP + ' FP projected</b></div>'
      + '<div class="sub-line">' + e.status + '</div></div>';
  }).join('');
}
function renderCap(){
  var c = document.getElementById('dashCap');
  if(c) c.textContent = FT.getState().prefs.stakeCap.toLocaleString('en-US') + ' $FTR';
}
renderLedger(); renderEntries(); renderCap();
window.addEventListener('fantrade:statechange', function(){ renderLedger(); renderEntries(); renderCap(); });
"""

page("dashboard.html", "Home — Fantrade", "".join(da), DASH_JS, DASH_CSS)
print("built dashboard.html")

# ══════════════════════════════════════════════════════════════════
# PORTFOLIO & LEDGER
# ══════════════════════════════════════════════════════════════════
PF_CSS = """
.hcols{grid-template-columns:1.7fr .8fr .85fr .8fr .9fr 1.05fr 1.15fr 86px}
.lcols{grid-template-columns:132px 1.6fr .9fr 1fr 104px}
.chart-x{display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:10px;
  color:var(--faint);margin-top:10px}
.seg-sm{display:flex;gap:4px;padding:4px;border-radius:999px;background:rgba(255,255,255,.035);
  border:1px solid var(--hair);box-shadow:var(--inset)}
.seg-sm button{border:0;background:transparent;color:var(--dim);border-radius:999px;padding:7px 15px;cursor:pointer;
  font-weight:600;font-size:10px;letter-spacing:.1em;text-transform:uppercase;transition:all .5s var(--ease)}
.seg-sm button[aria-pressed="true"]{background:var(--lime);color:#0A0D03}
.seg-sm button:hover:not([aria-pressed="true"]){color:var(--ink)}
.hashm{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--faint)}
@media (max-width:1024px){
  .hcols{grid-template-columns:1.6fr .8fr .9fr 1fr 1.1fr 86px}
  .hcols>*:nth-child(3),.hcols>*:nth-child(4){display:none}
}
@media (max-width:640px){
  .pfhead{flex-wrap:wrap}
  .pfhead .seg-sm{margin-left:0!important;width:100%;justify-content:space-between}
  .pfhead .seg-sm button{flex:1}
}
@media (max-width:768px){
  .hcols{grid-template-columns:1.5fr 1fr 86px}
  .hcols>*:nth-child(2),.hcols>*:nth-child(3),.hcols>*:nth-child(4),.hcols>*:nth-child(5),
  .hcols>*:nth-child(7){display:none}
  .lcols{grid-template-columns:104px 1fr 100px}
  .lcols>*:nth-child(3),.lcols>*:nth-child(5){display:none}
}
"""

pf = [T('<main><section class="app-head"><div class="wrap"><div class="head-row">'
        '<div><h1 data-reveal>Portfolio</h1></div>'
        '<div class="acts" data-reveal>@@@@</div></div>'
        '</div></section>',
        btn("Export CSV", "btn-glass", tag="button", extra='id="pfExport"'),
        btn("Rebalance squad", href="clubs.html"))]

pf.append('<section style="padding:10px 0 120px"><div class="wrap"><div class="bento">')

# value + chart
pf.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
            '<div class="pfhead" style="display:flex;align-items:flex-start;gap:14px">'
            '<div style="min-width:0"><div class="k-label">Total portfolio value</div>'
            '<div class="bal-big" style="font-size:clamp(28px,2.9vw,44px)">'
            '<span data-bind="net">370,300</span><small style="white-space:nowrap"> $FTR</small></div>'
            '<div class="bal-delta" id="pfDelta">@@<span>18.4% over 30 days</span></div></div>'
            '<div class="range" style="margin-left:auto;flex:none" id="pfRange">'
            '<button type="button" aria-pressed="true" data-r="30D">30D</button>'
            '<button type="button" aria-pressed="false" data-r="90D">90D</button>'
            '<button type="button" aria-pressed="false" data-r="All">All</button></div></div>'
            '<div class="bal-chart" id="pfChart"></div>'
            '<div class="chart-x" id="pfAxis"><span>Aug 15</span><span>Aug 29</span><span>Sep 07</span>'
            '<span>Today</span></div>'
            '<div class="b-row" style="margin-top:18px"><span>Unrealised P&amp;L</span>'
            '<b class="pl up" id="pfPnl">+0</b></div>'
            '<div class="b-row"><span>Realised this season</span><b class="pl up">+48,920</b></div>'
            '<div class="b-row total"><span>Effective yield (24 gameweeks)</span>'
            '<b style="color:var(--lime)">39.2% APR</b></div>'
            '</div></div>', ic("arrow", "ic")))

# allocation
pf.append(T('<div class="bezel c4" data-reveal><div class="core pad">'
            '<div class="k-label">Capital allocation</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:0 0 4px;line-height:1.6">'
            'How your balance is split between locked club assets, liquid reserves and speculative positions '
            'you have not assigned to a club.</p>'
            '<div class="alloc" id="pfAlloc">'
            '<i style="width:66%;background:linear-gradient(90deg,#8fbe00,#C4F82A)"></i>'
            '<i style="width:25%;background:#4DA6FF"></i>'
            '<i style="width:9%;background:rgba(255,255,255,.34)"></i></div>'
            '<div class="b-row"><span>@@Fielded in your Dream Club</span><b id="pfFielded">—</b></div>'
            '<div class="b-row"><span>@@Liquid &amp; staking reserves</span><b data-bind="balance">128,450</b></div>'
            '<div class="b-row"><span>@@Unassigned / speculative</span><b id="pfSpec">—</b></div>'
            '<div class="b-row total"><span>Total</span><b data-bind="net">370,300</b></div>'
            '<div class="mini-grid" style="margin-top:22px">'
            '<div class="mini"><div class="k">Player shares</div><div class="v" id="pfNPlayers">3</div></div>'
            '<div class="mini"><div class="k">Coach equities</div><div class="v amber" id="pfNCoaches">1</div></div>'
            '<div class="mini"><div class="k">Assigned to club</div><div class="v lime" id="pfNField">11</div></div>'
            '<div class="mini"><div class="k">Total positions</div><div class="v" id="pfNTotal">18</div></div>'
            '</div></div></div>',
            '<i style="display:inline-block;width:8px;height:8px;border-radius:3px;background:#C4F82A;margin-right:9px"></i>',
            '<i style="display:inline-block;width:8px;height:8px;border-radius:3px;background:#4DA6FF;margin-right:9px"></i>',
            '<i style="display:inline-block;width:8px;height:8px;border-radius:3px;background:rgba(255,255,255,.34);margin-right:9px"></i>'))

# syndicate card
pf.append(T('<div class="bezel c3" data-reveal><div class="core pad">'
            '<div class="k-label">Club syndicate</div>'
            '<div style="font-family:Archivo;font-variation-settings:\'wdth\' 125,\'wght\' 900;'
            'text-transform:uppercase;font-size:24px;line-height:1" data-bind="club">Zero FC</div>'
            '<div class="sub-line" style="letter-spacing:.14em;text-transform:uppercase;margin-bottom:20px">'
            'Apex division · Tier 1</div>'
            '<div class="b-row"><span>Head coach</span><b style="color:var(--amber)">$Arteta</b></div>'
            '<div class="b-row"><span>Squad captain</span><b>$Bruno · 1.5x</b></div>'
            '<div class="b-row"><span>Club valuation</span><b data-bind="clubvalue">245,800</b></div>'
            '<div class="b-row"><span>Global rank</span><b data-bind="rank">#124</b></div>'
            '<div class="b-row total"><span>Locked until</span><b>Sat 17:30</b></div>'
            '<div class="k-label" style="margin-top:26px">Ownership proof</div>'
            '<div class="rowlink">@@ 13 of 13 assets verified<b style="color:var(--lime)">Valid</b></div>'
            '<div class="rowlink">@@ Zero borrowed positions<b style="color:var(--lime)">Valid</b></div>'
            '<p style="font-size:11.5px;color:var(--faint);font-weight:300;margin-top:16px;line-height:1.6">'
            'Ownership is re-checked when a round locks. A club that cannot prove its eleven does not score.</p>'
            '<div style="margin-top:18px">@@</div>'
            '</div></div>',
            ic("shield", "ic"), ic("check", "ic"),
            btn("Inspect the pitch", "btn-glass", "clubs.html",
                extra='style="width:100%;justify-content:space-between"')))

# holdings
pf.append(T('<div class="bezel c12" data-reveal><div class="core">'
            '<div style="padding:30px 24px 18px;display:flex;align-items:center;gap:14px;flex-wrap:wrap">'
            '<div><div style="font-family:Archivo;font-variation-settings:\'wdth\' 120,\'wght\' 800;'
            'text-transform:uppercase;font-size:19px">Share holdings &amp; equities</div>'
            '<div class="sub-line" id="pfCount">Loading your positions…</div></div>'
            '<div class="markets" style="margin-left:auto" id="pfFilter">'
            '<button class="mkt" type="button" aria-pressed="true" data-f="all">All holdings</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-f="player">Player shares</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-f="coach">Coach equities</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-f="club">Fielded</button>'
            '</div></div>'
            '<div class="dt"><div class="dh hcols"><span>Asset &amp; ticker</span><span>Shares</span>'
            '<span>Avg cost</span><span>Price</span><span>24h</span><span>Unrealised</span>'
            '<span>Allocation</span><span></span></div><div id="pfRows"></div></div>'
            '</div></div>'))

# ledger
pf.append(T('<div class="bezel c7" data-reveal><div class="core">'
            '<div style="padding:30px 24px 18px;display:flex;align-items:center;gap:12px;flex-wrap:wrap">'
            '<div><div style="font-family:Archivo;font-variation-settings:\'wdth\' 120,\'wght\' 800;'
            'text-transform:uppercase;font-size:19px">Settlement ledger</div>'
            '<div class="sub-line">Every balance movement, oldest at the bottom</div></div>'
            '<span class="tag lime" style="margin-left:auto">@@ All verified</span></div>'
            '<div class="dt"><div class="dh lcols"><span>Event</span><span>Detail</span>'
            '<span>Reference</span><span style="text-align:right">$FTR</span><span style="text-align:right">Audit</span>'
            '</div><div id="pfLedger"></div></div>'
            '<div style="padding:20px 24px 28px;font-size:11.5px;color:var(--faint);font-weight:300;line-height:1.6">'
            'References are prototype identifiers. In production each settlement is anchored to a signed '
            'match-telemetry record you can verify independently.</div>'
            '</div></div>', ic("check", "ic")))

# yield
pf.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
            '<div class="k-label">FanPlay yield</div>'
            '<div class="value-big" style="color:var(--lime)">+48,920<small> $FTR</small></div>'
            '<div class="delta">Across 24 settled gameweeks · 39.2% APR equivalent</div>'
            '<div class="b-row" style="margin-top:20px"><span>Best round</span><b>MD 21 · +9,400</b></div>'
            '<div class="b-row"><span>Worst round</span><b class="pl down">MD 14 · -2,500</b></div>'
            '<div class="b-row"><span>Rounds settled in profit</span><b>17 of 24</b></div>'
            '<div class="b-row total"><span>Unclaimed batch</span>'
            '<b style="color:var(--lime)" id="pfUnclaimed">5,000 $FTR</b></div>'
            '<div style="margin-top:20px">@@</div>'
            '<div class="k-label" style="margin-top:30px">Tax &amp; records</div>'
            '<div class="rowlink">@@ Gains summary, this tax year<b>Ready</b></div>'
            '<div class="rowlink">@@ Full transaction export (CSV)<b>Ready</b></div>'
            '<p style="font-size:11.5px;color:var(--faint);font-weight:300;margin-top:16px;line-height:1.6">'
            'Fantrade does not give tax advice. Exports are provided so you or your accountant can do the work '
            'properly.</p>'
            '</div></div>',
            btn("Claim 5,000 $FTR", tag="button",
                extra='id="pfClaim" style="width:100%;justify-content:space-between"'),
            ic("scales", "ic"), ic("receipt", "ic")))

pf.append('</div></div></section></main>')

PF_JS = r"""
var ROLE = { RW:'Right winger', CAM:'Attacking mid', ST:'Striker', CB:'Centre back', COACH:'Head coach',
             SUB:'Tactical bench', LW:'Left winger', CM:'Centre mid', GK:'Goalkeeper' };
var MOVE = { '$Saka':6.4, '$Haaland':-1.8, '$Bruno':4.2, '$Arteta':14.2, '$Vinicius':1.9,
             '$Bellingham':3.7, '$Musiala':5.1, '$Pedri':-0.9, '$Saliba':2.7, '$Jackson':11.2,
             '$Pep':2.8, '$Maresca':7.4 };
var filter = 'all';

function money(n){ return Math.round(n).toLocaleString('en-US'); }

function renderHoldings(){
  var s = FT.getState(), box = document.getElementById('pfRows');
  if(!box) return;
  var keys = Object.keys(s.holdings), rows = [], shown = 0, pnlTotal = 0;
  var fielded = 0, spec = 0, np = 0, nc = 0, nf = 0;

  keys.forEach(function(k){
    var h = s.holdings[k];
    var val = h.shares * h.p, cost = h.shares * h.avg, pnl = val - cost;
    var inClub = h.inClub && h.inClub !== 'SUB';
    pnlTotal += pnl;
    if(inClub){ fielded += val; nf++; } else { spec += val; }
    if(h.c) nc++; else np++;

    var pass = filter === 'all'
      || (filter === 'player' && !h.c)
      || (filter === 'coach' && h.c)
      || (filter === 'club' && inClub);
    if(!pass) return;
    shown++;

    var d = MOVE[k] === undefined ? 0 : MOVE[k];
    rows.push('<div class="dr hcols">'
      + '<div class="asset"><span class="coin' + (h.c ? ' am' : '') + '">'
      + '<svg class="ic" aria-hidden="true"><use href="#i-' + (h.c ? 'whistle' : 'boot') + '"/></svg></span>'
      + '<div style="min-width:0"><div class="t-sym">' + k + '</div><div class="t-nm">' + h.n + '</div></div></div>'
      + '<div class="num" style="font-size:13px">' + h.shares.toLocaleString('en-US') + '</div>'
      + '<div class="num" style="font-size:13px;color:var(--dim)">' + h.avg.toFixed(2) + '</div>'
      + '<div class="num" style="font-size:13px">' + h.p.toFixed(2) + '</div>'
      + '<div class="tick ' + (d >= 0 ? 'up' : 'down') + '" style="font-size:12px">'
      + (d >= 0 ? '+' : '') + d.toFixed(1) + '%</div>'
      + '<div><div class="pl ' + (pnl >= 0 ? 'up' : 'down') + '">' + (pnl >= 0 ? '+' : '-')
      + money(Math.abs(pnl)) + '</div><div class="sub-line">' + money(val) + ' $FTR held</div></div>'
      + '<div><span class="tag ' + (inClub ? 'lime' : (h.c ? 'amber' : '')) + '">'
      + (inClub ? (h.inClub === 'COACH' ? 'Head coach' : 'Starting XI') : 'Unassigned') + '</span>'
      + '<div class="sub-line">' + (ROLE[h.inClub] || 'Reserve') + '</div></div>'
      + '<div><a class="tradebtn" href="exchange.html" style="display:block;text-align:center;'
      + 'text-decoration:none;line-height:1.6">Trade</a></div></div>');
  });

  box.innerHTML = rows.join('') || '<div class="empty-state">'
    + '<svg class="ic-xl" aria-hidden="true"><use href="#i-supply"/></svg>'
    + 'Nothing in this view yet. Buy shares on the exchange and they will appear here.</div>';

  document.getElementById('pfCount').textContent =
    shown + ' of ' + keys.length + ' holdings shown · ' + np + ' player, ' + nc + ' coach';
  var pnlEl = document.getElementById('pfPnl');
  pnlEl.textContent = (pnlTotal >= 0 ? '+' : '-') + money(Math.abs(pnlTotal));
  pnlEl.className = 'pl ' + (pnlTotal >= 0 ? 'up' : 'down');
  document.getElementById('pfFielded').textContent = money(fielded);
  document.getElementById('pfSpec').textContent = money(spec);
  document.getElementById('pfNPlayers').textContent = np;
  document.getElementById('pfNCoaches').textContent = nc;
  document.getElementById('pfNField').textContent = nf;
  document.getElementById('pfNTotal').textContent = keys.length;

  var bar = document.getElementById('pfAlloc').querySelectorAll('i');
  var liq = s.wallet.balance + s.wallet.locked, tot = fielded + spec + liq || 1;
  bar[0].style.width = (fielded / tot * 100).toFixed(1) + '%';
  bar[1].style.width = (liq / tot * 100).toFixed(1) + '%';
  bar[2].style.width = (spec / tot * 100).toFixed(1) + '%';
}

document.querySelectorAll('#pfFilter .mkt').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#pfFilter .mkt').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    filter = b.dataset.f;
    renderHoldings();
  });
});

var LTONE = { BUY:'', SELL:'amber', STAKE:'amber', PAYOUT:'lime', CONVERT:'', DEPOSIT:'lime' };
var LICON = { BUY:'candle', SELL:'candle', STAKE:'bolt', PAYOUT:'trophy', CONVERT:'swap', DEPOSIT:'coin' };
function ref(i){
  var seed = 'a3f91c7b4e20d68f5c1ab9e374';
  return '0x' + seed.slice(i % 12, (i % 12) + 4) + '…' + seed.slice(-4 - (i % 6), -(i % 6) || undefined);
}
function renderLedger(){
  var s = FT.getState(), box = document.getElementById('pfLedger');
  if(!box) return;
  box.innerHTML = s.transactions.map(function(t, i){
    var neg = (t.type === 'BUY' || t.type === 'STAKE');
    return '<div class="dr lcols">'
      + '<div><span class="tag ' + (LTONE[t.type] || '') + '">'
      + '<svg class="ic" aria-hidden="true"><use href="#i-' + (LICON[t.type] || 'receipt') + '"/></svg>'
      + t.type + '</span></div>'
      + '<div><div style="font-size:13px">' + t.asset + '</div>'
      + '<div class="sub-line">' + (t.shares > 1 ? t.shares.toLocaleString('en-US') + ' units @ '
        + t.price.toFixed(2) + ' · ' : '') + t.time + '</div></div>'
      + '<div class="hashm">' + ref(i) + '</div>'
      + '<div class="pl ' + (neg ? 'down' : 'up') + '" style="text-align:right">'
      + (neg ? '-' : '+') + money(t.total) + '</div>'
      + '<div style="text-align:right"><span class="tag lime">'
      + '<svg class="ic" aria-hidden="true"><use href="#i-check"/></svg>OK</span></div></div>';
  }).join('');
}

// claim the pending yield batch
var claimed = false;
var cb = document.getElementById('pfClaim');
if(cb) cb.addEventListener('click', function(){
  if(claimed){ showToast('That batch has already been claimed.', 'info'); return; }
  claimed = true;
  FT.depositFtr(5000);
  document.getElementById('pfUnclaimed').textContent = '0 $FTR';
  cb.style.opacity = '.5';
  cb.childNodes[0].nodeValue = 'Batch claimed';
  showToast('5,000 $FTR of settled yield claimed.', 'success');
});

// CSV export
var xb = document.getElementById('pfExport');
if(xb) xb.addEventListener('click', function(){
  var s = FT.getState();
  var lines = [['Type', 'Asset', 'Units', 'Price ($FTR)', 'Total ($FTR)', 'When'].join(',')];
  s.transactions.forEach(function(t){
    lines.push([t.type, t.asset.replace(/,/g, ' '), t.shares, t.price, t.total, t.time.replace(/,/g, '')].join(','));
  });
  lines.push('');
  lines.push(['Holding', 'Shares', 'Avg cost', 'Price', 'Value'].join(','));
  Object.keys(s.holdings).forEach(function(k){
    var h = s.holdings[k];
    lines.push([k, h.shares, h.avg.toFixed(2), h.p.toFixed(2), Math.round(h.shares * h.p)].join(','));
  });
  var blob = new Blob([lines.join('\n')], { type: 'text/csv' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'fantrade-ledger.csv';
  document.body.appendChild(a); a.click(); a.remove();
  showToast('Ledger exported as fantrade-ledger.csv.', 'success');
});

var PSERIES = { '30D': series(36, 1.1, 4.8, 53), '90D': series(46, 1.8, 6.6, 89),
                'All': series(56, 2.5, 9.2, 131) };
var PDELTA = { '30D': '18.4% over 30 days', '90D': '44.1% over 90 days', 'All': '212.5% all time' };
var PAXIS = { '30D': ['Aug 15','Aug 29','Sep 07','Today'],
              '90D': ['Jun 16','Jul 15','Aug 14','Today'],
              'All': ['GW 01','GW 10','GW 19','GW 28'] };
function ppaint(r){
  drawArea(document.getElementById('pfChart'), PSERIES[r], true);
  document.querySelector('#pfDelta span').textContent = PDELTA[r];
  document.getElementById('pfAxis').innerHTML = PAXIS[r].map(function(l){ return '<span>' + l + '</span>'; }).join('');
}
document.querySelectorAll('#pfRange button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#pfRange button').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    ppaint(b.dataset.r);
  });
});
ppaint('30D');

renderHoldings(); renderLedger();
window.addEventListener('fantrade:statechange', function(){ renderHoldings(); renderLedger(); });
"""

page("portfolio.html", "Portfolio — Fantrade", "".join(pf), PF_JS, PF_CSS)
print("built portfolio.html")

# ══════════════════════════════════════════════════════════════════
# LEADERBOARD — global Dream Club standings
# ══════════════════════════════════════════════════════════════════
LB_CSS = """
.scols{grid-template-columns:54px 2fr 1.15fr 1.5fr .8fr .9fr 1fr 92px}
.club-cell{display:flex;align-items:center;gap:13px;min-width:0}
.mcrest{width:34px;height:38px;flex:none;clip-path:polygon(0 0,100% 0,100% 66%,50% 100%,0 66%);
  display:grid;place-items:center;font-family:Archivo;font-variation-settings:'wdth' 100,'wght' 900;
  font-size:11px;color:#0A0D03}
.club-cell .cn{font-size:13.5px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.div-card{border:1px solid var(--hair);background:rgba(255,255,255,.03);border-radius:18px;padding:20px;
  box-shadow:var(--inset);display:flex;gap:16px;align-items:flex-start;margin-bottom:10px}
.div-card:last-child{margin-bottom:0}
.div-card .dot{width:9px;height:9px;border-radius:99px;flex:none;margin-top:6px}
.div-card b{display:block;font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 800;
  text-transform:uppercase;font-size:14px;margin-bottom:4px}
.div-card .r{font-size:11.5px;color:var(--faint);font-weight:300}
.div-card .pp{margin-left:auto;text-align:right;flex:none}
.div-card .pp em{font-style:normal;font-family:'JetBrains Mono',monospace;font-size:15px;color:var(--lime)}
.div-card .pp span{display:block;font-weight:600;font-size:8.5px;letter-spacing:.14em;color:var(--faint);
  text-transform:uppercase;margin-top:5px}
.idx{position:relative;height:170px;margin-top:20px}
.idx svg{width:100%;height:100%;display:block;overflow:visible}
@media (max-width:1024px){
  .scols{grid-template-columns:48px 1.8fr 1.1fr .8fr 1fr 88px}
  .scols>*:nth-child(4),.scols>*:nth-child(6){display:none}
}
@media (max-width:768px){
  .scols{grid-template-columns:38px 1.5fr 1fr}
  .scols>*:nth-child(4),.scols>*:nth-child(5),.scols>*:nth-child(6),
  .scols>*:nth-child(7),.scols>*:nth-child(8){display:none}
}
"""

# rank, club, manager, holders, value, delta%, core XI, coach + shape, boost, FP, yield, division
BOARD = [
    (1, "Apex Titans FC", "@CryptoKlopp", 48, 612400, 7.2, ["Mbappé 98", "Haaland 97", "Vinícius 95"],
     "$Pep · 4-3-3 Tiki-taka", 18.5, 14890, 34200, "apex", "#C4F82A"),
    (2, "Galactico Syndicate", "@SatoshiZidane", 32, 540100, 5.6, ["Bellingham 96", "Kane 95", "Rodri 94"],
     "$DonCarlo · 4-3-1-2 Fluid", 17.0, 13920, 29800, "apex", "#F4F6F1"),
    (3, "Arsenal Web3 FC", "@GoonerDAO", 112, 495200, 6.9, ["Saka 95", "Ødegaard 94", "Saliba 93"],
     "$Arteta · 4-3-3 Inverted", 16.5, 13450, 27100, "apex", "#FF5E8A"),
    (4, "Bavarian Meta XI", "@KaiserWeb3", 19, 462800, 2.5, ["Musiala 94", "Sané 91", "Kimmich 93"],
     "$Alonso · 3-4-2-1 Dominance", 14.0, 12890, 23500, "apex", "#4DA6FF"),
    (5, "Lombardia Capital", "@MilanoWhale", 61, 420500, -0.9, ["Lautaro 93", "Barella 92", "Bastoni 91"],
     "$Inzaghi · 3-5-2 Direct", 13.5, 12110, 21200, "apex", "#FF6A1F"),
    (6, "Anfield Collective", "@KopLedger", 88, 398400, 3.1, ["Salah 94", "Van Dijk 92", "Szoboszlai 89"],
     "$Slot · 4-3-3 High press", 13.0, 11740, 19900, "apex", "#FF5E5E"),
    (7, "Seleção Futures", "@SambaStake", 27, 371900, 4.4, ["Vinícius 95", "Rodrygo 90", "Éder 88"],
     "$Dorival · 4-2-3-1 Counter", 12.5, 11020, 18300, "apex", "#C4F82A"),
    (124, "Zero FC", "You · single-owner", 1, 245800, 7.9, ["Bruno 90", "Saka 95", "Haaland 97"],
     "$Arteta · 4-3-3 High press", 15.0, 8420, 18400, "apex", "#C4F82A"),
    (151, "Rioja Rising", "@TempranilloFC", 12, 198200, 1.4, ["Yamal 92", "Pedri 91", "Cubarsí 87"],
     "$Flick · 4-3-3 Youth", 11.0, 7180, 9400, "contender", "#FF6A1F"),
    (188, "Naija Nine", "@LagosLedger", 34, 176500, 9.8, ["Osimhen 91", "Lookman 88", "Iwobi 84"],
     "$Peseiro · 4-4-2 Wide", 10.5, 6640, 8800, "contender", "#4DA6FF"),
    (214, "Porto Alegre XI", "@GauchoGains", 8, 154300, -2.2, ["Diogo 89", "Vitinha 88", "Pepê 85"],
     "$Amorim · 3-4-3 Press", 9.5, 6020, 7100, "contender", "#F4F6F1"),
    (503, "Academy Origins", "@FirstTeamFund", 5, 84600, 12.6, ["Yıldız 84", "Endrick 83", "Zaïre 82"],
     "$Motta · 4-2-3-1 Raw", 7.0, 3910, 3200, "challenger", "#FF5E8A"),
    (612, "Sunday League Ltd", "@ParkPitchDAO", 3, 61200, 5.5, ["Elanga 81", "Mainoo 83", "Hato 80"],
     "$Dyche · 4-4-2 Honest", 6.5, 3140, 2400, "challenger", "#C4F82A"),
]

IDX = [104, 109, 113, 118, 122, 129, 134, 138, 145, 148]


def idx_chart(vals, w=620, h=170):
    lo, hi = min(vals) - 6, max(vals) + 6
    rng = hi - lo
    pa, pb = [], []
    for i, v in enumerate(vals):
        x = i * (w / (len(vals) - 1))
        pa.append("%.1f,%.1f" % (x, h - ((v - lo) / rng) * h))
        pb.append("%.1f,%.1f" % (x, h - ((v * 0.86 - lo) / rng) * h))
    return ('<svg viewBox="0 0 %d %d" preserveAspectRatio="none">'
            '<defs><linearGradient id="lbg" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%%" stop-color="#C4F82A" stop-opacity=".22"/>'
            '<stop offset="100%%" stop-color="#C4F82A" stop-opacity="0"/></linearGradient></defs>'
            '<polygon points="0,%d %s %d,%d" fill="url(#lbg)"/>'
            '<polyline points="%s" fill="none" stroke="#4DA6FF" stroke-width="1.4" stroke-dasharray="4 4" opacity=".8"/>'
            '<polyline points="%s" fill="none" stroke="#C4F82A" stroke-width="1.8" stroke-linejoin="round"/>'
            '</svg>' % (w, h, h, " ".join(pa), w, h, " ".join(pb), " ".join(pa)))


lb = [T('<main><section class="app-head"><div class="wrap"><div class="head-row">'
        '<div><h1 data-reveal>Standings</h1></div>'
        '<div class="acts" data-reveal>@@@@</div></div>'
        '</div></section>',
        btn("Rebalance your XI", href="clubs.html"),
        btn("Enter this round", "btn-glass", "fanplay.html"))]

lb.append('<section style="padding:10px 0 120px"><div class="wrap"><div class="bento">')

# your rank, as a strip
lb.append(T('<div class="bezel flat c12" data-reveal><div class="core pad-sm">'
            '<div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">'
            '<div class="crest-lg" id="lbCrest" style="background:linear-gradient(160deg,#C4F82A,#83b300)">ZF</div>'
            '<div style="min-width:0"><div style="font-family:Archivo;'
            'font-variation-settings:\'wdth\' 125,\'wght\' 900;text-transform:uppercase;font-size:21px;'
            'line-height:1" data-bind="club">Zero FC</div>'
            '<div class="sub-line" style="letter-spacing:.14em;text-transform:uppercase">'
            'Apex division · <span data-bind="handle">@alex_trader</span></div></div>'
            '<div style="display:flex;gap:28px;flex-wrap:wrap;margin-left:auto;align-items:center">'
            '<div><div class="k-label" style="margin:0 0 6px">Rank</div>'
            '<div class="num" style="font-size:22px;color:var(--lime)" data-bind="rank">#124</div></div>'
            '<div><div class="k-label" style="margin:0 0 6px">Season FP</div>'
            '<div class="num" style="font-size:22px" data-bind="fp">8,420</div></div>'
            '<div><div class="k-label" style="margin:0 0 6px">Form</div>'
            '<div class="form5"><i class="l">L</i><i class="l">L</i><i class="w">W</i><i class="w">W</i>'
            '<i class="w">W</i></div></div>'
            '<span>@@</span></div></div></div></div>',
            btn("Division structure", "btn-glass", "divisions.html")))

# standings
lb.append(T('<div class="bezel flat c12 flat-sep" data-reveal><div class="core">'
            '<div style="padding:0 0 18px;display:flex;align-items:center;gap:14px;flex-wrap:wrap">'
            '<div><div style="font-family:Archivo;font-variation-settings:\'wdth\' 120,\'wght\' 800;'
            'text-transform:uppercase;font-size:19px">Gameweek 28 table</div>'
            '<div class="sub-line" id="lbCount">13 of 1,420 clubs</div></div>'
            '<div class="markets" style="margin-left:auto" id="lbFilter">'
            '<button class="mkt" type="button" aria-pressed="true" data-d="all">All divisions</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-d="apex">Apex</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-d="contender">Contender</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-d="challenger">Challenger</button>'
            '</div></div>'
            '<div class="rail" style="padding:0 0 16px;margin:0">'
            '<div class="searchbox">@@<input id="lbSearch" placeholder="Search club or manager handle" '
            'aria-label="Search clubs"></div>'
            '<div class="seg-sm" id="lbSort"><button type="button" aria-pressed="true" data-s="rank">By rank</button>'
            '<button type="button" aria-pressed="false" data-s="value">By value</button>'
            '<button type="button" aria-pressed="false" data-s="yield">By yield</button></div></div>'
            '<div class="dt"><div class="dh scols"><span>Rank</span><span>Club &amp; manager</span>'
            '<span>Club value</span><span>Core XI &amp; tactical head</span><span>Boost</span>'
            '<span>Total FP</span><span>Est. yield</span><span></span></div>'
            '<div id="lbRows"></div></div>'
            '</div></div>', ic("search", "ic")))

lb.append('</div></div></section></main>')

LB_ROWS = ",".join(
    "{r:%d,c:%s,m:%s,h:%d,v:%d,d:%s,xi:%s,co:%s,b:%s,fp:%d,y:%d,dv:%s,cl:%s,you:%s}" % (
        r, repr(c).replace("'", '"'), repr(m).replace("'", '"'), h, v, d,
        "[" + ",".join(repr(x).replace("'", '"') for x in xi) + "]",
        repr(co).replace("'", '"'), b, fp, y, repr(dv).replace("'", '"'),
        repr(col).replace("'", '"'), "true" if c == "Zero FC" else "false")
    for r, c, m, h, v, d, xi, co, b, fp, y, dv, col in BOARD)

LB_JS = ("var BOARD=[" + LB_ROWS + "];") + r"""
var div = 'all', sort = 'rank', q = '';

(function(){
  var s = FT.getState(), c = document.getElementById('lbCrest');
  if(c){
    c.style.background = 'linear-gradient(160deg,' + s.club.colors[0] + ',' + (s.club.colors[1] || s.club.colors[0]) + ')';
    c.textContent = s.club.name.split(/\s+/).map(function(w){ return w.charAt(0).toUpperCase(); }).join('').slice(0, 3);
  }
  // your own row tracks the club you actually saved
  BOARD.forEach(function(b){
    if(b.you){ b.c = s.club.name; b.r = s.club.rank; b.fp = s.club.fp; b.v = s.club.value;
      b.b = s.club.boost; b.cl = s.club.colors[0];
      b.co = '$' + s.club.coach.replace('$', '') + ' · ' + s.club.formation + ' High press'; }
  });
})();

function money(n){ return n.toLocaleString('en-US'); }
function initials(n){ return n.split(/\s+/).map(function(w){ return w.charAt(0).toUpperCase(); }).join('').slice(0, 3); }

function renderBoard(){
  var rows = BOARD.filter(function(b){
    if(div !== 'all' && b.dv !== div) return false;
    if(q && (b.c + ' ' + b.m).toLowerCase().indexOf(q) === -1) return false;
    return true;
  });
  rows.sort(function(a, b){
    if(sort === 'value') return b.v - a.v;
    if(sort === 'yield') return b.y - a.y;
    return a.r - b.r;
  });
  document.getElementById('lbRows').innerHTML = rows.map(function(b){
    return '<div class="dr scols' + (b.you ? ' you' : '') + '">'
      + '<div class="rk' + (b.r <= 3 ? ' top' : '') + '">#' + b.r + '</div>'
      + '<div class="club-cell"><span class="mcrest" style="background:linear-gradient(160deg,' + b.cl
      + ',rgba(0,0,0,.45))">' + initials(b.c) + '</span><div style="min-width:0"><div class="cn">' + b.c
      + (b.you ? ' <span class="tag lime" style="margin-left:6px">You</span>' : '') + '</div>'
      + '<div class="sub-line">' + b.m + (b.h > 1 ? ' · ' + b.h + ' fractional holders' : '') + '</div></div></div>'
      + '<div><div class="num" style="font-size:13px">' + money(b.v) + '</div>'
      + '<div class="pl ' + (b.d >= 0 ? 'up' : 'down') + '" style="font-size:11px">'
      + (b.d >= 0 ? '+' : '') + b.d.toFixed(1) + '%</div></div>'
      + '<div><div class="xi">' + b.xi.map(function(x){ return '<i>' + x + '</i>'; }).join('') + '</div>'
      + '<div class="sub-line">' + b.co + '</div></div>'
      + '<div><span class="tag ' + (b.b >= 15 ? 'lime' : '') + '">+' + b.b.toFixed(1) + '%</span></div>'
      + '<div class="num" style="font-size:13px">' + money(b.fp) + ' <span style="color:var(--faint);'
      + 'font-size:10px">FP</span></div>'
      + '<div class="pl up">+' + money(b.y) + '</div>'
      + '<div>' + (b.you
        ? '<a class="tradebtn" href="clubs.html" style="display:block;text-align:center;text-decoration:none;'
          + 'line-height:1.6;background:var(--lime);border-color:var(--lime);color:#0A0D03">Rebalance</a>'
        : '<button class="tradebtn" type="button" data-inspect="' + b.c + '">Inspect</button>') + '</div>'
      + '</div>';
  }).join('') || '<div class="empty-state"><svg class="ic-xl" aria-hidden="true"><use href="#i-search"/></svg>'
      + 'No clubs match that search.</div>';

  document.getElementById('lbCount').textContent =
    rows.length + ' of 1,420 clubs';

  document.querySelectorAll('[data-inspect]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var b = BOARD.filter(function(x){ return x.c === btn.dataset.inspect; })[0];
      if(!b) return;
      openModal('<h3 class="ft-modal-title">' + b.c + '</h3>'
        + '<p class="ft-modal-desc">' + b.m + ' · ' + b.co + '</p>'
        + '<div class="ft-modal-card">'
        + '<div class="m-row"><span>Global rank</span><b>#' + b.r + '</b></div>'
        + '<div class="m-row"><span>Club value</span><b>' + money(b.v) + ' $FTR</b></div>'
        + '<div class="m-row"><span>Squad multiplier</span><b>+' + b.b.toFixed(1) + '%</b></div>'
        + '<div class="m-row"><span>Fractional holders</span><b>' + b.h + '</b></div>'
        + '<div class="m-row total"><span>Total Fantrade Points</span><b>' + money(b.fp) + ' FP</b></div>'
        + '</div>'
        + '<div class="k-label">Core eleven</div><div class="ft-modal-card"><div class="xi">'
        + b.xi.map(function(x){ return '<i>' + x + '</i>'; }).join('') + '</div></div>'
        + '<p style="font-size:11.5px;color:var(--faint);font-weight:300;line-height:1.6;margin:0">'
        + 'Full teamsheets unlock after the window settles. Until then only the core three are public.</p>');
    });
  });
}

document.querySelectorAll('#lbFilter .mkt').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#lbFilter .mkt').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    div = b.dataset.d; renderBoard();
  });
});
document.querySelectorAll('#lbSort button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#lbSort button').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    sort = b.dataset.s; renderBoard();
  });
});
var sb = document.getElementById('lbSearch');
if(sb) sb.addEventListener('input', function(){ q = sb.value.trim().toLowerCase(); renderBoard(); });

renderBoard();
window.addEventListener('fantrade:statechange', renderBoard);
"""

page("leaderboard.html", "Leaderboard — Fantrade", "".join(lb), LB_JS, LB_CSS + PF_CSS)
print("built leaderboard.html")

# ══════════════════════════════════════════════════════════════════
# NOTIFICATIONS — activity feed
# ══════════════════════════════════════════════════════════════════
NT_CSS = """
.fd .ibox{flex:none}
.fd .ibox .ic{width:17px;height:17px}
.quiet{display:flex;gap:10px;align-items:center;margin-top:10px}
.quiet .tf{flex:1;margin:0}
"""

nt = [T('<main><section class="app-head"><div class="wrap"><div class="head-row">'
        '<div><h1 data-reveal>Activity</h1></div>'
        '<div class="acts" data-reveal>@@@@</div></div></div></section>',
        btn("Mark all read", "btn-glass", tag="button", extra='id="ntRead"'),
        btn("Notification settings", href="settings-alerts.html"))]

nt.append('<section style="padding:10px 0 120px"><div class="wrap"><div class="bento">')

nt.append(T('<div class="bezel c8" data-reveal><div class="core">'
            '<div style="padding:26px 24px 16px"><div class="markets" id="ntFilter">'
            '<button class="mkt" type="button" aria-pressed="true" data-k="all">Everything</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-k="settle">Settlements</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-k="order">Orders</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-k="club">Club</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-k="system">Account</button>'
            '</div></div><div id="ntFeed"></div>'
            '<div style="padding:22px 24px 28px;text-align:center">'
            '<span style="font-size:11.5px;color:var(--faint);font-weight:300">'
            'Activity older than 90 days is available in your ledger export.</span></div>'
            '</div></div>'))

nt.append(T('<div class="bezel c4" data-reveal><div class="core pad">'
            '<div class="k-label">Needs you before the lock</div>'
            '<div class="warn" style="margin:0 0 24px">@@<p>W. Saliba is a late fitness test. Auto-sub will '
            'field Gabriel if he is withdrawn — turn auto-sub off in Settings if you would rather take the zero.</p>'
            '</div>'
            '<div class="k-label">What you get told about</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:0 0 8px;line-height:1.6">'
            'Toggle a channel off and Fantrade stops sending it — the event still lands in your ledger.</p>'
            '<div class="sw-row"><div><div class="t">Round settlements</div>'
            '<div class="d">Results, points and payouts when a window closes.</div></div>'
            '<button class="tgl" type="button" data-pref="settleAlerts" aria-pressed="true"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Order fills</div>'
            '<div class="d">Market and limit orders that execute on the book.</div></div>'
            '<button class="tgl" type="button" data-pref="orderFills" aria-pressed="true"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Club &amp; teamsheet risk</div>'
            '<div class="d">Injuries, late fitness tests and auto-sub decisions.</div></div>'
            '<button class="tgl" type="button" data-pref="clubAlerts" aria-pressed="true"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Price moves on your holdings</div>'
            '<div class="d">Alerts when an asset you own moves more than 8% in a session.</div></div>'
            '<button class="tgl" type="button" data-pref="priceMoves" aria-pressed="false"><i></i></button></div>'
            '<div class="k-label" style="margin-top:26px">This week</div>'
            '<div class="b-row"><span>Events recorded</span><b id="ntTotal">8</b></div>'
            '<div class="b-row"><span>Unread</span><b class="pl up" data-unread>3</b></div>'
            '<div class="b-row total"><span>Net balance movement</span>'
            '<b style="color:var(--lime)">+6,620 $FTR</b></div>'
            '<div style="margin-top:22px">@@</div>'
            '</div></div>',
            ic("flag", "ic"),
            btn("All settings", "btn-glass", "settings.html",
                extra='style="width:100%;justify-content:space-between"')))

nt.append('</div></div></section></main>')

NT_JS = r"""
var kind = 'all';
function renderFeed(){
  var s = FT.getState(), box = document.getElementById('ntFeed');
  if(!box) return;
  var list = s.notifications.filter(function(n){ return kind === 'all' || n.kind === kind; });
  if(!list.length){
    box.innerHTML = '<div class="empty-state"><svg class="ic-xl" aria-hidden="true"><use href="#i-pulse"/></svg>'
      + 'Nothing in this view. Quiet is usually good.</div>';
    return;
  }
  var out = [], day = null;
  list.forEach(function(n){
    if(n.day !== day){ day = n.day; out.push('<div class="daysep">' + day + '</div>'); }
    out.push('<div class="fd' + (n.read ? '' : ' unread') + '" data-id="' + n.id + '" role="button" tabindex="0">'
      + '<span class="ibox' + (n.kind === 'club' ? ' am' : '') + '">'
      + '<svg class="ic" aria-hidden="true"><use href="#i-' + n.icon + '"/></svg></span>'
      + '<div class="bd"><div class="tt">' + n.title + '</div><div class="ms">' + n.msg + '</div>'
      + '<div class="tm">' + n.time + '</div></div>'
      + (n.amt ? '<div class="amt ' + (n.tone === 'up' ? 'up' : (n.tone === 'down' ? 'down' : ''))
        + '" style="color:' + (n.tone === 'up' ? 'var(--lime)' : (n.tone === 'down' ? 'var(--red)' : 'var(--faint)'))
        + '">' + n.amt + '</div>' : '')
      + '</div>');
  });
  box.innerHTML = out.join('');
  document.getElementById('ntTotal').textContent = s.notifications.length;

  box.querySelectorAll('.fd').forEach(function(row){
    function open(){
      FT.readOne(row.dataset.id);
      row.classList.remove('unread');
    }
    row.addEventListener('click', open);
    row.addEventListener('keydown', function(e){ if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); open(); } });
  });
}
document.querySelectorAll('#ntFilter .mkt').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#ntFilter .mkt').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    kind = b.dataset.k; renderFeed();
  });
});
var rb = document.getElementById('ntRead');
if(rb) rb.addEventListener('click', function(){
  if(!FT.unread()){ showToast('Everything is already read.', 'info'); return; }
  FT.readAll();
  renderFeed();
  showToast('All activity marked as read.', 'success');
});
renderFeed();
"""

page("notifications.html", "Notifications — Fantrade", "".join(nt), NT_JS, NT_CSS)
print("built notifications.html")

# ══════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════
ST_CSS = """
.sec-card{scroll-margin-top:130px}
.sec-title{display:flex;align-items:center;gap:14px;margin-bottom:20px}
.sec-title h3{font-family:Archivo;font-variation-settings:'wdth' 120,'wght' 800;text-transform:uppercase;
  font-size:19px;margin:0}
.sec-title p{font-size:12px;color:var(--faint);font-weight:300;margin:5px 0 0;line-height:1.5}
.sess{display:flex;align-items:center;gap:14px;padding:15px 0;border-bottom:1px solid rgba(255,255,255,.05)}
.sess:last-child{border-bottom:0}
.sess .t{font-size:13px}
.sess .d{font-size:11px;color:var(--faint);margin-top:4px}
.sess .kill{margin-left:auto;border:1px solid var(--hair);background:rgba(255,255,255,.04);color:var(--dim);
  border-radius:999px;padding:7px 15px;font-weight:600;font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;
  cursor:pointer;transition:all .5s var(--ease)}
.sess .kill:hover{border-color:rgba(255,94,94,.5);color:#ff9a9a}
"""

SETNAV = [("profile", "user", "Manager profile"), ("club", "crest", "Club identity"),
          ("security", "shield", "Security"), ("alerts", "pulse", "Notifications"),
          ("wallet", "wallet", "Wallet & payouts"), ("play", "scales", "Responsible play"),
          ("data", "receipt", "Data & account")]

SECTIONS = {}

SECTIONS["profile"] = T('<div class="bezel flat sec-card" data-reveal><div class="core pad">'
            '<div class="sec-title"><span class="ibox">@@</span><div><h3>Manager profile</h3>'
            '<p>Shown next to your club everywhere it appears publicly.</p></div></div>'
            '<div class="tf-row">@@@@</div>@@'
            '<div class="tf-row">@@@@</div>'
            '<div style="display:flex;gap:10px;margin-top:8px;flex-wrap:wrap">@@</div>'
            '</div></div>',
            ic("user", "ic-lg"),
            tf("Display name", "stName", "text", "Alex Morgan", "user"),
            tf("Manager handle", "stHandle", "text", "@alex_trader", "", "",
               "3–20 characters, letters, numbers and underscores."),
            tf("Email", "stEmail", "email", "you@example.com", "", "Used for settlement receipts and sign-in."),
            sel("Region", "stRegion", COUNTRIES, "flag"),
            sel("Home league", "stLeague", ["*Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
                                            "Nigeria Premier Football League", "Eredivisie", "Primeira Liga"],
                "stadium"),
            btn("Save profile", tag="button", extra='id="stSaveProfile"'))

# club identity
SECTIONS["club"] = T('<div class="bezel flat sec-card" data-reveal><div class="core pad">'
            '<div class="sec-title"><span class="ibox">@@</span><div><h3>Club identity</h3>'
            '<p>The name, shape and colours your Dream Club carries on the league table.</p></div></div>'
            '@@'
            '<div class="k-label" style="margin-top:20px">Default formation</div>'
            '<div class="forms" id="stForms">'
            '<button type="button" aria-pressed="true">4-3-3</button>'
            '<button type="button" aria-pressed="false">4-4-2</button>'
            '<button type="button" aria-pressed="false">3-5-2</button>'
            '<button type="button" aria-pressed="false">4-2-3-1</button></div>'
            '<div class="k-label" style="margin-top:24px">Club colour</div><div class="swatches" id="stSw">'
            '<button class="sw" type="button" aria-pressed="true" data-c="#C4F82A" data-n="Lime" '
            'style="background:linear-gradient(160deg,#C4F82A,#83b300)" aria-label="Lime"></button>'
            '<button class="sw" type="button" aria-pressed="false" data-c="#FF6A1F" data-n="Amber" '
            'style="background:linear-gradient(160deg,#FF6A1F,#b33f06)" aria-label="Amber"></button>'
            '<button class="sw" type="button" aria-pressed="false" data-c="#4DA6FF" data-n="Azure" '
            'style="background:linear-gradient(160deg,#4DA6FF,#0b5fae)" aria-label="Azure"></button>'
            '<button class="sw" type="button" aria-pressed="false" data-c="#FF5E8A" data-n="Rose" '
            'style="background:linear-gradient(160deg,#FF5E8A,#a81f45)" aria-label="Rose"></button>'
            '<button class="sw" type="button" aria-pressed="false" data-c="#F4F6F1" data-n="Chalk" '
            'style="background:linear-gradient(160deg,#F4F6F1,#8f938b)" aria-label="Chalk"></button></div>'
            '<div class="sw-row" style="margin-top:20px"><div><div class="t">Automatic substitutions</div>'
            '<div class="d">If a starter does not play, field the highest-ranked eligible bench asset instead. '
            'Turning this off means an absent starter simply scores nothing.</div></div>'
            '<button class="tgl" type="button" data-pref="autoSub" aria-pressed="true"><i></i></button></div>'
            '<div style="display:flex;gap:10px;margin-top:18px;flex-wrap:wrap">@@@@</div>'
            '</div></div>',
            ic("crest", "ic-lg"),
            tf("Club name", "stClub", "text", "Zero FC", "crest", "", "2–24 characters."),
            btn("Save club identity", tag="button", extra='id="stSaveClub"'),
            btn("Open the club builder", "btn-glass", "clubs.html"))

# security
SECTIONS["security"] = T('<div class="bezel flat sec-card" data-reveal><div class="core pad">'
            '<div class="sec-title"><span class="ibox">@@</span><div><h3>Security</h3>'
            '<p>Your assets are only as safe as the way you get into the account.</p></div></div>'
            '@@@@@@'
            '<div style="display:flex;gap:10px;margin:4px 0 8px;flex-wrap:wrap">@@</div>'
            '<div class="sw-row"><div><div class="t">Two-factor authentication</div>'
            '<div class="d">Require a code from your authenticator app on every new sign-in and before '
            'any withdrawal.</div></div>'
            '<button class="tgl" type="button" data-pref="twoFactor" aria-pressed="false"><i></i></button></div>'
            '<div class="warn" id="tfaWarn">@@<p>Two-factor is off. Anyone with your password can move '
            '$FTR out of this wallet and rebuild your club.</p></div>'
            '<div class="k-label" style="margin-top:26px">Active sessions</div>'
            '<div class="sess"><span class="ibox sm">@@</span><div><div class="t">Chrome · London, UK</div>'
            '<div class="d">This device · active now</div></div>'
            '<span class="tag lime" style="margin-left:auto">Current</span></div>'
            '<div class="sess"><span class="ibox sm plain">@@</span><div><div class="t">Safari · iPhone 15</div>'
            '<div class="d">Lagos, NG · last seen 2 days ago</div></div>'
            '<button class="kill" type="button" data-kill>Revoke</button></div>'
            '<div class="sess"><span class="ibox sm plain">@@</span><div><div class="t">Firefox · Manchester, UK</div>'
            '<div class="d">Last seen 11 days ago</div></div>'
            '<button class="kill" type="button" data-kill>Revoke</button></div>'
            '</div></div>',
            ic("shield", "ic-lg"),
            tf("Current password", "stPwOld", "password", "••••••••••", "lock"),
            tf("New password", "stPwNew", "password", "At least 8 characters", "lock", "",
               "Use 8 characters or more, with a number."),
            tf("Confirm new password", "stPwConf", "password", "Repeat it", "lock", "",
               "The two passwords do not match."),
            btn("Update password", tag="button", extra='id="stSavePw"'),
            ic("flag", "ic"),
            ic("shield", "ic-sm"), ic("user", "ic-sm"), ic("user", "ic-sm"))

# notifications
SECTIONS["alerts"] = T('<div class="bezel flat sec-card" data-reveal><div class="core pad">'
            '<div class="sec-title"><span class="ibox">@@</span><div><h3>Notifications</h3>'
            '<p>What Fantrade sends you, and when it stays quiet.</p></div></div>'
            '<div class="sw-row"><div><div class="t">Round settlements</div>'
            '<div class="d">Results, points scored and payouts when a window closes.</div></div>'
            '<button class="tgl" type="button" data-pref="settleAlerts"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Order fills</div>'
            '<div class="d">Market and limit orders that execute on the book.</div></div>'
            '<button class="tgl" type="button" data-pref="orderFills"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Club &amp; teamsheet risk</div>'
            '<div class="d">Injuries, late fitness tests and auto-sub decisions before a lock.</div></div>'
            '<button class="tgl" type="button" data-pref="clubAlerts"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Price moves on your holdings</div>'
            '<div class="d">When an asset you own moves more than 8% in a session.</div></div>'
            '<button class="tgl" type="button" data-pref="priceMoves"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Weekly digest</div>'
            '<div class="d">One email on Monday: club performance, portfolio movement, next fixtures.</div></div>'
            '<button class="tgl" type="button" data-pref="digest"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Product and marketing email</div>'
            '<div class="d">New features, market tiers and competitions. Off by default.</div></div>'
            '<button class="tgl" type="button" data-pref="marketing"><i></i></button></div>'
            '</div></div>', ic("pulse", "ic-lg"))

# wallet
SECTIONS["wallet"] = T('<div class="bezel flat sec-card" data-reveal><div class="core pad">'
            '<div class="sec-title"><span class="ibox">@@</span><div><h3>Wallet &amp; payouts</h3>'
            '<p>Where settled $FTR goes when you take it off the platform.</p></div></div>'
            '<div class="mini-grid" style="grid-template-columns:repeat(3,1fr)">'
            '<div class="mini"><div class="k">Available</div><div class="v lime"><span data-bind="balance">'
            '128,450</span></div></div>'
            '<div class="mini"><div class="k">Locked</div><div class="v"><span data-bind="locked">5,000</span></div></div>'
            '<div class="mini"><div class="k">Season payouts</div><div class="v"><span data-bind="earned">'
            '19,640</span></div></div></div>'
            '<div class="tf-row" style="margin-top:20px">@@@@</div>@@'
            '<div class="b-row"><span>Withdrawal fee</span><b>0.5% · minimum 50 $FTR</b></div>'
            '<div class="b-row"><span>Settlement window</span><b>1–2 working days</b></div>'
            '<div class="b-row total"><span>Verification status</span>'
            '<b style="color:var(--lime)">Verified</b></div>'
            '<div style="display:flex;gap:10px;margin-top:18px;flex-wrap:wrap">@@@@</div>'
            '</div></div>',
            ic("wallet", "ic-lg"),
            sel("Payout currency", "stCur", ["*GBP · £", "NGN · ₦", "EUR · €", "USD · $"], "coin"),
            sel("Payout method", "stMethod", ["*Bank transfer", "Card refund", "On-chain wallet"], "bank"),
            tf("Payout account", "stAcct", "text", "Sort code and account number", "", "",
               "Prototype build — no real payout details are stored."),
            btn("Save payout details", tag="button", extra='id="stSavePayout"'),
            btn("Open your wallet", "btn-glass", "ftr.html"))

# responsible play
SECTIONS["play"] = T('<div class="bezel flat sec-card" data-reveal><div class="core pad">'
            '<div class="sec-title"><span class="ibox am">@@</span><div><h3>Responsible play</h3>'
            '<p>Limits you set now are enforced at entry. Raising one takes 24 hours; lowering one is immediate.</p>'
            '</div></div>'
            '<div class="tf-row">@@@@</div>'
            '<div class="line"><span>Staked this week</span><b>2,500 $FTR</b></div>'
            '<div class="supply"><i id="stCapBar" style="width:50%"></i></div>'
            '<div style="display:flex;gap:10px;margin:18px 0 8px;flex-wrap:wrap">@@</div>'
            '<div class="sw-row"><div><div class="t">Take a break</div>'
            '<div class="d">Suspend new entries and purchases for a fixed period. Your holdings and club stay '
            'exactly as they are, and settled rounds still pay out.</div></div>'
            '<button class="btn btn-glass btn-sm" type="button" id="stBreak">Set a break@@</button></div>'
            '<p style="font-size:11.5px;color:var(--faint);font-weight:300;margin-top:16px;line-height:1.6">'
            'If matchday staking has stopped being fun, that is a good reason to stop. '
            'Support organisations are listed in the Responsible play policy.</p>'
            '</div></div>',
            ic("scales", "ic-lg"),
            tf("Weekly stake cap ($FTR)", "stCap", "text", "5,000", "lock", "",
               "Enter a number between 100 and 100,000."),
            sel("Deposit limit", "stDep", ["*No limit", "£250 per month", "£500 per month", "£1,000 per month"],
                "coin"),
            btn("Save limits", tag="button", extra='id="stSaveLimits"'),
            ARROW)

# data & account
SECTIONS["data"] = T('<div class="bezel flat sec-card" data-reveal><div class="core pad">'
            '<div class="sec-title"><span class="ibox">@@</span><div><h3>Data &amp; account</h3>'
            '<p>Take your records with you, or close the account entirely.</p></div></div>'
            '<div class="rowlink">@@ Full ledger export (CSV)<b><a href="portfolio.html" '
            'style="color:var(--lime)">Download</a></b></div>'
            '<div class="rowlink">@@ Gains summary for this tax year<b><a href="portfolio.html" '
            'style="color:var(--lime)">Download</a></b></div>'
            '<div class="rowlink">@@ Account data request (GDPR)<b><a href="#" id="stGdpr" '
            'style="color:var(--lime)">Request</a></b></div>'
            '<div class="danger-zone" style="margin-top:26px">'
            '<div style="font-family:Archivo;font-variation-settings:\'wdth\' 118,\'wght\' 800;'
            'text-transform:uppercase;font-size:14px;color:#ff9a9a;margin-bottom:8px">Danger zone</div>'
            '<p style="font-size:12.5px;color:var(--dim);font-weight:300;margin:0 0 18px;line-height:1.6">'
            'Resetting returns this prototype to its opening state — wallet, holdings, club and activity. '
            'Closing an account sells every position at market and pays the balance out.</p>'
            '<div style="display:flex;gap:10px;flex-wrap:wrap">@@@@</div></div>'
            '</div></div>',
            ic("receipt", "ic-lg"), ic("receipt", "ic"), ic("scales", "ic"), ic("shield", "ic"),
            btn("Reset prototype data", "btn-glass", tag="button", extra='id="stReset"'),
            btn("Close account", "btn-red", tag="button", extra='id="stClose"'))

ST_JS = r"""
// One script serves every settings screen, so nothing here assumes a field is
// present — each section has its own page now.
function el(id){ return document.getElementById(id); }
function wrap(id){ return document.getElementById('f-' + id); }
function num(v){ return parseInt(String(v).replace(/[^0-9]/g, ''), 10) || 0; }
function set(id, v){ var e = el(id); if(e) e.value = v; }
function on(id, ev, fn){ var e = el(id); if(e) e.addEventListener(ev, fn); }

// hydrate from state
(function(){
  var s = FT.getState();
  set('stName', s.user.name);
  set('stHandle', s.user.handle);
  set('stEmail', s.auth.email);
  set('stClub', s.club.name);
  set('stCap', s.prefs.stakeCap.toLocaleString('en-US'));
  [['stRegion', s.user.region], ['stLeague', s.user.league]].forEach(function(p){
    var sel = el(p[0]);
    if(!sel) return;
    for(var i = 0; i < sel.options.length; i++){ if(sel.options[i].text === p[1]) sel.selectedIndex = i; }
  });
  document.querySelectorAll('#stForms button').forEach(function(b){
    b.setAttribute('aria-pressed', b.textContent.trim() === s.club.formation ? 'true' : 'false');
  });
  document.querySelectorAll('#stSw .sw').forEach(function(b){
    b.setAttribute('aria-pressed', b.dataset.n === s.club.colorName ? 'true' : 'false');
  });
  capBar();
})();

function capBar(){
  var f = el('stCap'), bar = el('stCapBar');
  if(!f || !bar) return;
  var cap = num(f.value) || 1;
  if(bar) bar.style.width = Math.min(100, 2500 / cap * 100).toFixed(0) + '%';
}
on('stCap', 'input', capBar);

var formation = FT.getState().club.formation;
var colors = FT.getState().club.colors.slice();
var colorName = FT.getState().club.colorName;
document.querySelectorAll('#stForms button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#stForms button').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    formation = b.textContent.trim();
  });
});
document.querySelectorAll('#stSw .sw').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#stSw .sw').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    colors = [b.dataset.c, b.dataset.c]; colorName = b.dataset.n;
  });
});

on('stSaveProfile', 'click', function(){
  var nm = el('stName').value.trim();
  var h = el('stHandle').value.trim().replace(/^@/, '');
  var em = el('stEmail').value.trim();
  if(nm.length < 2){ wrap('stName').classList.add('bad'); showToast('Give us a display name.', 'error'); return; }
  if(!/^[A-Za-z0-9_]{3,20}$/.test(h)){ wrap('stHandle').classList.add('bad'); return; }
  if(!/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(em)){ wrap('stEmail').classList.add('bad');
    showToast('That email does not look right.', 'error'); return; }
  wrap('stName').classList.remove('bad'); wrap('stHandle').classList.remove('bad');
  wrap('stEmail').classList.remove('bad');
  FT.updateProfile({ name: nm, handle: '@' + h, region: el('stRegion').value, league: el('stLeague').value });
  var s = FT.getState(); s.auth.email = em; FT.save(); FT.syncUI();
  showToast('Profile saved.', 'success');
});

on('stSaveClub', 'click', function(){
  var cn = el('stClub').value.trim();
  if(cn.length < 2 || cn.length > 24){ wrap('stClub').classList.add('bad');
    showToast('Club names are 2–24 characters.', 'error'); return; }
  wrap('stClub').classList.remove('bad');
  FT.saveClub({ name: cn, formation: formation, colors: colors, colorName: colorName });
  showToast(cn + ' updated — ' + formation + ', ' + colorName + '.', 'success');
});

on('stSavePw', 'click', function(){
  var o = el('stPwOld').value, n = el('stPwNew').value, c = el('stPwConf').value;
  if(!o){ wrap('stPwOld').classList.add('bad'); showToast('Enter your current password.', 'error'); return; }
  if(n.length < 8){ wrap('stPwNew').classList.add('bad'); return; }
  if(n !== c){ wrap('stPwConf').classList.add('bad'); return; }
  ['stPwOld', 'stPwNew', 'stPwConf'].forEach(function(i){ wrap(i).classList.remove('bad'); });
  el('stPwOld').value = el('stPwNew').value = el('stPwConf').value = '';
  showToast('Password updated. Other sessions were signed out.', 'success');
});

on('stSavePayout', 'click', function(){
  showToast('Payout details saved for ' + el('stCur').value.split(' ')[0] + ' via '
    + el('stMethod').value.toLowerCase() + '.', 'success');
});

on('stSaveLimits', 'click', function(){
  var cap = num(el('stCap').value);
  if(cap < 100 || cap > 100000){ wrap('stCap').classList.add('bad'); return; }
  wrap('stCap').classList.remove('bad');
  FT.setPref('stakeCap', cap);
  el('stCap').value = cap.toLocaleString('en-US');
  capBar();
  showToast('Weekly stake cap set to ' + cap.toLocaleString('en-US') + ' $FTR.', 'success');
});

on('stBreak', 'click', function(){
  openModal('<h3 class="ft-modal-title">Take a break</h3>'
    + '<p class="ft-modal-desc">New entries and purchases are blocked for the period you choose. Holdings stay '
    + 'where they are, settled rounds still pay out, and the block cannot be lifted early.</p>'
    + '<div class="ft-modal-card"><div class="m-row"><span>24 hours</span><b>Cooling off</b></div>'
    + '<div class="m-row"><span>7 days</span><b>Short break</b></div>'
    + '<div class="m-row"><span>30 days</span><b>Extended break</b></div>'
    + '<div class="m-row total"><span>6 months</span><b>Self-exclusion</b></div></div>'
    + '<p style="font-size:11.5px;color:var(--faint);font-weight:300;line-height:1.6;margin:0">'
    + 'Prototype build — no break is actually applied. In production this is irreversible for the chosen period.</p>');
});

document.querySelectorAll('[data-kill]').forEach(function(b){
  b.addEventListener('click', function(){
    b.closest('.sess').style.opacity = '.4';
    b.textContent = 'Revoked';
    b.disabled = true;
    showToast('Session revoked. That device will have to sign in again.', 'success');
  });
});

on('stGdpr', 'click', function(e){
  e.preventDefault();
  showToast('Data request logged. A copy is emailed within 30 days.', 'info');
});

on('stReset', 'click', function(){
  openModal('<h3 class="ft-modal-title">Reset prototype data?</h3>'
    + '<p class="ft-modal-desc">Your wallet, holdings, club, activity and limits all return to the opening '
    + 'state. This cannot be undone.</p>'
    + '<div style="display:flex;gap:10px;flex-wrap:wrap">'
    + '<button class="btn btn-red" id="rstYes" type="button" style="flex:1;justify-content:center">Reset everything</button>'
    + '<button class="btn btn-glass" id="rstNo" type="button" style="flex:1;justify-content:center">Keep my data</button></div>');
  el('rstNo').addEventListener('click', closeModal);
  el('rstYes').addEventListener('click', function(){
    FT.resetState(); closeModal();
    showToast('Prototype reset to defaults.', 'info');
    setTimeout(function(){ location.reload(); }, 700);
  });
});

on('stClose', 'click', function(){
  openModal('<h3 class="ft-modal-title">Close your account</h3>'
    + '<p class="ft-modal-desc">Every position is sold at the market price shown on the exchange, open entries '
    + 'settle normally, and the remaining balance is paid to your verified payout account. Your club is removed '
    + 'from the league table at the end of the current cycle.</p>'
    + '<div class="ft-modal-card"><div class="m-row"><span>Positions to liquidate</span><b id="clHold">—</b></div>'
    + '<div class="m-row"><span>Balance to pay out</span><b id="clBal">—</b></div>'
    + '<div class="m-row total"><span>Open entries</span><b id="clEnt">—</b></div></div>'
    + '<p style="font-size:11.5px;color:var(--faint);font-weight:300;line-height:1.6;margin:0 0 18px">'
    + 'Prototype build — nothing is closed. Use “Reset prototype data” to start over.</p>'
    + '<button class="btn btn-glass" id="clNo" type="button" style="width:100%;justify-content:center">'
    + 'Keep my account</button>');
  var s = FT.getState();
  el('clHold').textContent = Object.keys(s.holdings).length + ' holdings';
  el('clBal').textContent = (s.wallet.balance + s.wallet.locked).toLocaleString('en-US') + ' $FTR';
  el('clEnt').textContent = s.fanplay.activeEntries.length;
  el('clNo').addEventListener('click', closeModal);
});

// the two-factor warning only stands while two-factor is off
(function(){
  var w = el('tfaWarn'), t = document.querySelector('.tgl[data-pref="twoFactor"]');
  if(!w || !t) return;
  function sync(){ w.hidden = t.getAttribute('aria-pressed') === 'true'; }
  t.addEventListener('click', function(){ setTimeout(sync, 0); });
  sync();
})();

"""

def hub(rows):
    out = []
    for href, icon, title, desc, bind, suffix in rows:
        val = ('<span class="val" data-bind="%s">—</span>' % bind) if bind else ""
        if val and suffix:
            val = val[:-7] + '</span><span class="val" style="display:inline">%s</span>' % suffix
            val = ('<span class="val"><span data-bind="%s">—</span>%s</span>' % (bind, suffix))
        out.append(T('<a href="@@"><span class="ibox">@@</span><div class="bd"><b>@@</b><p>@@</p>@@</div>'
                     '<span class="go">@@</span></a>', href, ic(icon, "ic-lg"), title, desc, val,
                     ic("arrow", "ic")))
    return '<div class="hub">%s</div>' % "".join(out)


SET_PAGES = [("profile", "settings-profile.html", "Manager profile", "user"),
             ("club", "settings-club.html", "Club identity", "crest"),
             ("security", "settings-security.html", "Security", "shield"),
             ("alerts", "settings-alerts.html", "Notifications", "pulse"),
             ("wallet", "settings-wallet.html", "Wallet & payouts", "wallet"),
             ("play", "settings-play.html", "Responsible play", "scales"),
             ("data", "settings-data.html", "Data & account", "receipt")]

# Once a section owns a page, the card's own title block is saying it twice.
_SECTITLE = re.compile(r'<div class="sec-title">.*?</div></div>', re.S)


def _blurb(frag):
    m = re.search(r'<div class="sec-title">.*?<p>(.*?)</p>', frag, re.S)
    return m.group(1) if m else ""


for _key, _fname, _label, _icon in SET_PAGES:
    _frag = SECTIONS[_key]
    _body = ('<main><section class="app-head" style="padding:92px 0 12px"><div class="wrap">'
             '<a class="crumb" href="settings.html" aria-label="Back to settings">%s Settings</a>'
             '<h1 data-reveal style="margin-top:14px">%s</h1>'
             '</div></section>'
             '<section style="padding:0 0 120px"><div class="wrap">%s</div></section></main>'
             % (ic("arrow", "ic"), _label, _SECTITLE.sub("", _frag)))
    page(_fname, _label + " — Fantrade", _body, ST_JS, ST_CSS + OB_CSS)

sx = ['<main><section class="app-head"><div class="wrap">'
      '<h1 data-reveal>Settings</h1>'
      '</div></section>']
sx.append('<section style="padding:10px 0 130px"><div class="wrap"><div class="bento">')
sx.append(T('<div class="c12 hub-sec" data-reveal>@@</div>',
            hub([(_fname, _icon, _label, _blurb(SECTIONS[_key]), "", "")
                 for _key, _fname, _label, _icon in SET_PAGES])))
sx.append(T('<div class="c12" data-reveal style="margin-top:8px">@@</div>',
            btn("Sign out", "btn-glass", tag="button",
                extra='data-signout style="justify-content:space-between;min-width:220px"')))
sx.append('</div></div></section></main>')
page("settings.html", "Settings — Fantrade", "".join(sx), "", ST_CSS + OB_CSS)
print("built settings.html + 7 section pages")

# ══════════════════════════════════════════════════════════════════
# ACCOUNT — the hub behind the fifth tab
# ══════════════════════════════════════════════════════════════════
AC_CSS = """
.hub-sec{margin-bottom:12px}
.hub-sec .k-label{margin-bottom:12px}
"""

HUB_MONEY = [
    ("ftr.html", "wallet", "$FTR wallet",
     "Balance, send, receive, swap and buy. Your receive QR lives here.", "balance", " $FTR"),
    ("portfolio.html", "receipt", "Portfolio &amp; ledger",
     "Every share you hold, unrealised P&amp;L and the full settlement audit trail.", "net", " $FTR net"),
]
HUB_CLUB = [
    ("clubs.html", "crest", "Dream Club",
     "Your eleven, the bench, the coach and the club builder.", "club", ""),
    ("leaderboard.html", "rank", "League table",
     "Where the club sits against 1,420 syndicates this cycle.", "rank", " worldwide"),
]
HUB_ACCT = [
    ("notifications.html", "pulse", "Notifications",
     "Settlements, order fills, teamsheet risk and account events.", "", ""),
    ("settings.html", "scales", "Settings",
     "Profile, club identity, security, payouts and responsible play.", "", ""),
]


ac = [T('<main><section class="app-head"><div class="wrap">'
        '<h1 data-reveal>Account</h1>'
        '</div></section>')]

ac.append('<section style="padding:10px 0 130px"><div class="wrap"><div class="bento">')

# identity
ac.append(T('<div class="bezel c12" data-reveal><div class="core pad">'
            '<div class="idcard">'
            '<span class="avatar"><span data-bind="initials">AM</span></span>'
            '<div style="min-width:0">'
            '<div style="font-family:Archivo;font-variation-settings:\'wdth\' 125,\'wght\' 900;'
            'text-transform:uppercase;font-size:26px;line-height:1" data-bind="name">Alex Morgan</div>'
            '<div class="sub-line" style="font-family:\'JetBrains Mono\',monospace;color:var(--lime);'
            'font-size:12px;margin-top:7px"><span data-bind="handle">@alex_trader</span></div>'
            '<div class="sub-line" style="letter-spacing:.14em;text-transform:uppercase;margin-top:7px">'
            'Apex division · manager since Sep 2026</div></div>'
            '<div style="margin-left:auto;display:flex;gap:10px;flex-wrap:wrap">@@@@</div>'
            '</div>'
            '<div class="statbar" style="margin-top:26px">'
            '<div>@@ Available <b data-bind="balance">128,450</b> $FTR</div>'
            '<div>@@ Net worth <b data-bind="net">370,300</b></div>'
            '<div>@@ Club <b data-bind="club">Zero FC</b></div>'
            '<div>@@ Rank <b data-bind="rank">#124</b></div>'
            '</div></div></div>',
            btn("Edit profile", "btn-glass", "settings-profile.html"),
            btn("Open wallet", href="ftr.html"),
            ic("coin", "ic"), ic("chart", "ic"), ic("crest", "ic"), ic("rank", "ic")))

ac.append(T('<div class="c12 hub-sec" data-reveal><div class="k-label">Money</div>@@</div>', hub(HUB_MONEY)))
ac.append(T('<div class="c12 hub-sec" data-reveal><div class="k-label">Club</div>@@</div>', hub(HUB_CLUB)))
ac.append(T('<div class="c12 hub-sec" data-reveal><div class="k-label">Account</div>@@</div>', hub(HUB_ACCT)))

# quick controls
ac.append(T('<div class="bezel c7" data-reveal><div class="core pad">'
            '<div class="k-label">Quick controls</div>'
            '<div class="sw-row"><div><div class="t">Round settlement alerts</div>'
            '<div class="d">Results, points and payouts the moment a window closes.</div></div>'
            '<button class="tgl" type="button" data-pref="settleAlerts"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Club &amp; teamsheet risk</div>'
            '<div class="d">Injuries and late fitness tests before a lock.</div></div>'
            '<button class="tgl" type="button" data-pref="clubAlerts"><i></i></button></div>'
            '<div class="sw-row"><div><div class="t">Automatic substitutions</div>'
            '<div class="d">Field the best eligible bench asset when a starter does not play.</div></div>'
            '<button class="tgl" type="button" data-pref="autoSub"><i></i></button></div>'
            '<div class="b-row" style="margin-top:18px"><span>Weekly stake cap</span>'
            '<b id="acCap">5,000 $FTR</b></div>'
            '<div class="b-row"><span>Two-factor authentication</span><b id="acTfa">Off</b></div>'
            '<div style="display:flex;gap:10px;margin-top:20px;flex-wrap:wrap">@@@@</div>'
            '</div></div>',
            btn("All settings", "btn-glass", "settings.html",
                extra='style="flex:1;justify-content:space-between"'),
            btn("Responsible play", "btn-glass", "settings-play.html",
                extra='style="flex:1;justify-content:space-between"')))

# activity + session
ac.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
            '<div style="display:flex;align-items:center;gap:12px">'
            '<div class="k-label" style="margin:0">Latest activity</div>'
            '<a href="notifications.html" style="margin-left:auto;font-size:11px;color:var(--lime)">'
            'See all (<span data-unread>3</span>)</a></div>'
            '<div id="acFeed" style="margin-top:14px"></div>'
            '<div class="k-label" style="margin-top:26px">Session</div>'
            '<div class="rowlink">@@ Signed in as<b data-bind="email">you@example.com</b></div>'
            '<div class="rowlink">@@ This device<b>Chrome · London</b></div>'
            '<div style="margin-top:20px">@@</div>'
            '</div></div>',
            ic("user", "ic"), ic("shield", "ic"),
            btn("Sign out", "btn-glass", tag="button",
                extra='data-signout style="width:100%;justify-content:space-between"')))

ac.append('</div></div></section></main>')

AC_JS = r"""
(function(){
  var s = FT.getState();
  document.querySelectorAll('[data-bind="initials"]').forEach(function(el){ el.textContent = FT.initials(); });
  var cap = document.getElementById('acCap');
  if(cap) cap.textContent = s.prefs.stakeCap.toLocaleString('en-US') + ' $FTR';
  var tfa = document.getElementById('acTfa');
  if(tfa){
    tfa.textContent = s.prefs.twoFactor ? 'On' : 'Off';
    tfa.style.color = s.prefs.twoFactor ? 'var(--lime)' : 'var(--amber)';
  }
})();

function renderAcFeed(){
  var s = FT.getState(), box = document.getElementById('acFeed');
  if(!box) return;
  var list = s.notifications.slice(0, 3);
  box.innerHTML = list.map(function(n){
    return '<div class="rowlink" style="align-items:flex-start;gap:12px">'
      + '<span class="ibox sm' + (n.kind === 'club' ? ' am' : '') + '" style="margin-top:2px">'
      + '<svg class="ic-sm" aria-hidden="true"><use href="#i-' + n.icon + '"/></svg></span>'
      + '<span style="min-width:0;flex:1"><span style="display:block;font-size:12.5px;color:var(--ink)">'
      + n.title + '</span><span class="sub-line">' + n.time + '</span></span>'
      + (n.amt ? '<b style="color:' + (n.tone === 'up' ? 'var(--lime)' : 'var(--red)') + '">'
        + n.amt.replace(' $FTR', '') + '</b>' : '') + '</div>';
  }).join('');
}
renderAcFeed();
window.addEventListener('fantrade:statechange', renderAcFeed);
"""

page("account.html", "Account — Fantrade", "".join(ac), AC_JS, AC_CSS)
print("built account.html")
