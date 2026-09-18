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
    """chrome=False renders the stripped auth shell (minimal nav)."""
    shell = nav(fname, app) if chrome else nav_min()
    html = (head(title, css, "app" if (app and chrome) else "") + atmosphere() + shell + body +
            "<script src=\"public/fantrade-api.js\"></script><script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
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
  border-radius:14px;padding:14px 0;font-family:'Montserrat', sans-serif;font-size:14px;cursor:pointer;
  box-shadow:var(--inset);transition:all .6s var(--ease)}
.forms button[aria-pressed="true"]{background:var(--lime);border-color:var(--lime);color:#fff}
.forms button:hover:not([aria-pressed="true"]){color:var(--ink);border-color:var(--hair-2)}
.swatches{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}
.sw{width:36px;height:36px;border-radius:12px;border:1px solid var(--hair);cursor:pointer;box-shadow:var(--inset);
  transition:transform .6s var(--ease)}
.sw:hover,.sw[aria-pressed="true"]{transform:scale(1.08)}
.sw[aria-pressed="true"]{border-color:var(--ink)}
.grant{border:1px solid rgba(24,0,173,.3);border-radius:20px;padding:28px 24px;text-align:center;
  background:radial-gradient(ellipse at 50% 130%,rgba(24,0,173,.16),rgba(24,0,173,.03) 62%);
  box-shadow:var(--inset);margin-bottom:20px}
.grant .k{font-weight:600;font-size:9.5px;letter-spacing:.2em;color:#95ad44;text-transform:uppercase}
.grant .v{font-family:'Montserrat', sans-serif;font-weight:200;font-size:clamp(34px,4.4vw,50px);
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
          '<button class="sw" type="button" aria-pressed="true" data-c="#1800ad" data-n="Indigo" '
          'style="background:linear-gradient(160deg,#1800ad,#0f0075)" aria-label="Indigo"></button>'
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
var formation = '4-3-3', colors = ['#1800ad', '#0f0075'], colorName = 'Indigo';
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
/* Dashboard / Home Page Styles */
.kc-home-wrap{max-width:680px;margin:0 auto;padding:4px 16px 88px}

/* Search bar */
.kc-home-searchbar-wrap{display:flex;align-items:center;gap:10px;margin-bottom:16px}
.kc-home-search-box{flex:1;display:flex;align-items:center;gap:10px;height:44px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);border-radius:999px;padding:0 16px;transition:border-color .2s,background .2s}
.kc-home-search-box:focus-within{border-color:var(--lime);background:rgba(255,255,255,.08)}
.kc-home-search-box svg{color:#767c82;flex-shrink:0}
.kc-home-search-box input{flex:1;background:transparent;border:0;outline:0;color:var(--ink);font-family:Montserrat,sans-serif;font-size:13px}
.kc-home-search-box input::placeholder{color:#767c82}
.kc-home-scan-btn{width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:grid;place-items:center;color:var(--ink);flex-shrink:0;text-decoration:none;transition:background .2s,border-color .2s}
.kc-home-scan-btn:hover{background:rgba(255,255,255,.1);border-color:var(--lime);color:var(--lime)}

/* Hero Portfolio Card */
.kc-home-bal-card{background:linear-gradient(135deg,rgba(24,0,173,.09) 0%,rgba(10,12,14,.92) 55%,rgba(255,255,255,.02) 100%);border:1px solid rgba(24,0,173,.22);border-radius:20px;padding:20px 22px;margin-bottom:16px;box-shadow:0 14px 34px rgba(0,0,0,.45)}
.kc-bal-header{display:flex;align-items:center;gap:8px;font-size:12px;color:#8E9AA8}
.kc-eye-btn{background:transparent;border:0;color:inherit;cursor:pointer;display:grid;place-items:center;padding:2px;transition:color .2s}
.kc-eye-btn:hover{color:var(--lime)}
.kc-bal-delta-tag{margin-left:auto;background:rgba(24,0,173,.15);color:var(--lime);font-size:10.5px;font-weight:700;padding:3px 9px;border-radius:999px;font-family:'Montserrat', sans-serif}
.kc-bal-val{font-family:'Montserrat', sans-serif;font-size:34px;font-weight:700;letter-spacing:-.02em;color:var(--ink);margin:8px 0 2px}
.kc-bal-val small{font-size:16px;color:var(--lime);font-weight:600}
.kc-bal-sub{font-size:12px;color:#767c82;font-family:'Montserrat', sans-serif}

/* Quick Action Circles */
.kc-bal-actions{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:18px;padding-top:16px;border-top:1px solid rgba(255,255,255,.06)}
.kc-act-circle{display:flex;flex-direction:column;align-items:center;gap:6px;text-decoration:none;color:var(--ink);transition:transform .2s}
.kc-act-circle:hover{transform:translateY(-2px)}
.kc-act-circle:hover .kc-act-ico{background:rgba(24,0,173,.2);border-color:var(--lime);color:var(--lime)}
.kc-act-ico{width:46px;height:46px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:grid;place-items:center;color:var(--ink);transition:all .2s}
.kc-act-circle span{font-size:11.5px;font-weight:500;color:#8E9AA8}

/* Gameweek Ticker */
.kc-news{display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:10px 14px;margin-bottom:18px;font-size:12px;color:#8B918A}
.kc-live-dot{width:7px;height:7px;border-radius:50%;background:var(--lime);box-shadow:0 0 8px var(--lime);flex-shrink:0;animation:kcPulse 2s infinite}
@keyframes kcPulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.3)}}
.kc-news-txt{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kc-news-txt b{font-family:'Montserrat', sans-serif;color:var(--lime)}
.kc-news-close{background:transparent;border:0;color:#767c82;cursor:pointer;font-size:14px}

/* Hot Trending Cards Strip - Horizontal Swipe & Scroll */
.kc-hot-strip{display:flex;align-items:stretch;gap:10px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;padding:2px 2px 8px;margin-bottom:20px}
.kc-hot-strip::-webkit-scrollbar{display:none}
.kc-hot-card{flex:0 0 142px;width:142px;min-width:142px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:14px;padding:12px 14px;text-decoration:none;color:inherit;transition:border-color .2s,transform .2s;box-sizing:border-box}
.kc-hot-card:hover{border-color:rgba(24,0,173,.3);transform:translateY(-2px)}
.kc-hot-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}
.kc-hot-ticker{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;font-size:13px;color:var(--ink)}
.kc-hot-badge{font-family:'Montserrat', sans-serif;font-size:10px;font-weight:700;padding:1px 5px;border-radius:4px}
.kc-hot-badge.up{background:rgba(24,0,173,.15);color:var(--lime)}
.kc-hot-badge.down{background:rgba(255,94,94,.15);color:#FF5E5E}
.kc-hot-name{font-size:10.5px;color:#767c82;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:6px}
.kc-hot-price{font-family:'Montserrat', sans-serif;font-size:14px;font-weight:700;color:var(--ink)}
.kc-hot-price small{font-size:10px;color:var(--lime);font-weight:500}

/* Category Tabs */
.kc-cat-tabs{display:flex;align-items:center;gap:18px;border-bottom:1px solid rgba(255,255,255,.07);overflow-x:auto;scrollbar-width:none;margin-bottom:12px}
.kc-cat-tabs::-webkit-scrollbar{display:none}
.kc-cat-tab{background:transparent;border:0;outline:0;padding:8px 0 10px;font-family:Montserrat,sans-serif;font-size:14px;font-weight:500;color:#767c82;cursor:pointer;white-space:nowrap;position:relative;transition:color .2s}
.kc-cat-tab:hover{color:var(--ink)}
.kc-cat-tab.on{color:var(--ink);font-weight:700}
.kc-cat-tab.on::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2.5px;background:var(--lime);border-radius:2px}

/* Market Watchlist Rows */
.kc-home-rows{display:flex;flex-direction:column;gap:4px}
.kc-row{display:grid;grid-template-columns:1fr 110px 92px;align-items:center;padding:12px 10px;border-radius:12px;border-bottom:1px solid rgba(255,255,255,.04);text-decoration:none;color:inherit;transition:background .2s ease}
.kc-row:hover{background:rgba(255,255,255,.03)}
.kc-row-left{display:flex;align-items:center;gap:12px;min-width:0}
.kc-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);display:grid;place-items:center;flex:none;color:var(--lime);font-family:Archivo,sans-serif;font-size:11px;font-weight:800;overflow:hidden}
.kc-avatar .player-photo{width:100%;height:100%;object-fit:cover;object-position:50% 18%;display:block}
.kc-avatar.coach{color:var(--amber);border-color:rgba(255,106,31,.25);background:rgba(255,106,31,.08)}
.kc-pair-title{display:flex;align-items:center;gap:5px;font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 800;font-size:14px;line-height:1.1;color:var(--ink)}
.kc-pair-quote{font-size:11.5px;color:#767c82;font-weight:600}
.kc-tag{font-family:'Montserrat', sans-serif;font-size:9px;font-weight:600;color:#767c82;background:rgba(255,255,255,.08);border-radius:4px;padding:1px 4px;margin-left:2px}
.kc-tag.coach-tag{color:var(--amber);background:rgba(255,106,31,.12)}
.kc-pair-sub{font-size:11.5px;color:#767c82;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kc-row-mid{text-align:right;padding-right:12px}
.kc-price-main{font-family:'Montserrat', sans-serif;font-size:14px;font-weight:600;color:var(--ink);letter-spacing:-.01em}
.kc-price-sub{font-family:'Montserrat', sans-serif;font-size:11px;color:#767c82;margin-top:2px}
.kc-row-right{display:flex;justify-content:flex-end}
.kc-pill{display:inline-flex;align-items:center;justify-content:center;min-width:76px;height:32px;border-radius:6px;font-family:'Montserrat', sans-serif;font-size:12px;font-weight:700;color:#fff;background:var(--lime);box-sizing:border-box;padding:0 6px}
.kc-pill.down{background:#FF5E5E;color:#fff}

/* Dream club card */
.kc-ref-card{display:flex;align-items:center;justify-content:space-between;gap:16px;background:linear-gradient(135deg,rgba(255,255,255,.04) 0%,rgba(255,255,255,.02) 100%);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:16px 20px;text-decoration:none;transition:border-color .2s,transform .2s}
.kc-ref-card:hover{border-color:rgba(24,0,173,.3);transform:translateY(-1px)}
.kc-ref-left{flex:1}
.kc-ref-title{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 700;font-size:15px;color:var(--ink);margin-bottom:4px}
.kc-ref-sub{font-size:12px;color:#767c82}
.kc-ref-icon-box{width:52px;height:52px;flex-shrink:0;border-radius:14px;overflow:hidden;background:rgba(255,255,255,.05);display:grid;place-items:center}
"""

da = [T('<main><div class="kc-home-wrap">'
        '<!-- Search & Discovery Bar -->'
        '<div class="kc-home-searchbar-wrap">'
        '  <div class="kc-home-search-box">'
        '    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>'
        '    <input type="text" id="homeSearchInput" placeholder="Search football player shares, clubs, coaches..." autocomplete="off">'
        '  </div>'
        '  <a href="receive.html" class="kc-home-scan-btn" title="QR Scanner">'
        '    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 8V5a1 1 0 0 1 1-1h3M4 16v3a1 1 0 0 0 1 1h3M16 4h3a1 1 0 0 1 1 1v3M16 20h3a1 1 0 0 0 1-1v-3"/></svg>'
        '  </a>'
        '</div>'

        '<!-- Total Equity Hero Card -->'
        '<div class="kc-home-bal-card">'
        '  <div class="kc-bal-header">'
        '    <span>Total Portfolio Equity ($FTR)</span>'
        '    <button type="button" class="kc-eye-btn" id="balEyeBtn" aria-label="Toggle balance visibility">'
        '      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>'
        '    </button>'
        '    <span class="kc-bal-delta-tag" id="dashDelta">+18.4% +6,200</span>'
        '  </div>'
        '  <div class="kc-bal-val">'
        '    <span id="homeBalVal" data-bind="net">370,300</span> <small>$FTR</small>'
        '  </div>'
        '  <div class="kc-bal-sub" id="homeBalSub">≈ $37,030.00 USD</div>'
        '  <div class="kc-bal-actions">'
        '    <a href="buy.html" class="kc-act-circle">'
        '      <div class="kc-act-ico"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12l7 7 7-7"/></svg></div>'
        '      <span>Deposit</span>'
        '    </a>'
        '    <a href="send.html" class="kc-act-circle">'
        '      <div class="kc-act-ico"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></div>'
        '      <span>Transfer</span>'
        '    </a>'
        '    <a href="fanplay.html" class="kc-act-circle">'
        '      <div class="kc-act-ico"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="14.83" y1="9.17" x2="19.07" y2="4.93"/><line x1="4.93" y1="19.07" x2="9.17" y2="14.83"/></svg></div>'
        '      <span>FanPlay</span>'
        '    </a>'
        '    <a href="clubs.html" class="kc-act-circle">'
        '      <div class="kc-act-ico"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg></div>'
        '      <span>Clubs</span>'
        '    </a>'
        '  </div>'
        '</div>'

        '<!-- Gameweek Live Pulse Ticker -->'
        '<div class="kc-news">'
        '  <span class="kc-live-dot"></span>'
        '  <div class="kc-news-txt">Gameweek 28 locks in <b id="cdH">03</b>h <b id="cdM">14</b>m <b id="cdS">22</b>s · Arsenal vs Chelsea Sat 17:30 · <b>1.25M $FTR</b> pool</div>'
        '  <button type="button" class="kc-news-close" onclick="this.parentElement.style.display=\'none\'">✕</button>'
        '</div>'

        '<!-- Trending Spotlight Strip (Horizontal Scroll: 8 cards) -->'
        '<div class="kc-hot-strip">'
        '  <a href="asset.html?a=%24Saka" class="kc-hot-card">'
        '    <div class="kc-hot-top">'
        '      <span class="kc-hot-ticker">$Saka</span>'
        '      <span class="kc-hot-badge up">+6.4%</span>'
        '    </div>'
        '    <div class="kc-hot-name">Bukayo Saka · Arsenal</div>'
        '    <div class="kc-hot-price">48.20 <small>FTR</small></div>'
        '  </a>'
        '  <a href="asset.html?a=%24Haaland" class="kc-hot-card">'
        '    <div class="kc-hot-top">'
        '      <span class="kc-hot-ticker">$Haaland</span>'
        '      <span class="kc-hot-badge down">-1.8%</span>'
        '    </div>'
        '    <div class="kc-hot-name">Erling Haaland · Man City</div>'
        '    <div class="kc-hot-price">71.40 <small>FTR</small></div>'
        '  </a>'
        '  <a href="asset.html?a=%24Palmer" class="kc-hot-card">'
        '    <div class="kc-hot-top">'
        '      <span class="kc-hot-ticker">$Palmer</span>'
        '      <span class="kc-hot-badge up">+8.2%</span>'
        '    </div>'
        '    <div class="kc-hot-name">Cole Palmer · Chelsea</div>'
        '    <div class="kc-hot-price">52.80 <small>FTR</small></div>'
        '  </a>'
        '  <a href="asset.html?a=%24Mbappe" class="kc-hot-card">'
        '    <div class="kc-hot-top">'
        '      <span class="kc-hot-ticker">$Mbappe</span>'
        '      <span class="kc-hot-badge up">+4.8%</span>'
        '    </div>'
        '    <div class="kc-hot-name">Kylian Mbappé · Real Madrid</div>'
        '    <div class="kc-hot-price">78.50 <small>FTR</small></div>'
        '  </a>'
        '  <a href="asset.html?a=%24Yamal" class="kc-hot-card">'
        '    <div class="kc-hot-top">'
        '      <span class="kc-hot-ticker">$Yamal</span>'
        '      <span class="kc-hot-badge up">+9.4%</span>'
        '    </div>'
        '    <div class="kc-hot-name">Lamine Yamal · Barcelona</div>'
        '    <div class="kc-hot-price">66.20 <small>FTR</small></div>'
        '  </a>'
        '  <a href="asset.html?a=%24Bellingham" class="kc-hot-card">'
        '    <div class="kc-hot-top">'
        '      <span class="kc-hot-ticker">$Bellingham</span>'
        '      <span class="kc-hot-badge up">+3.3%</span>'
        '    </div>'
        '    <div class="kc-hot-name">Jude Bellingham · Real Madrid</div>'
        '    <div class="kc-hot-price">58.90 <small>FTR</small></div>'
        '  </a>'
        '  <a href="asset.html?a=%24Vinicius" class="kc-hot-card">'
        '    <div class="kc-hot-top">'
        '      <span class="kc-hot-ticker">$Vinicius</span>'
        '      <span class="kc-hot-badge up">+0.7%</span>'
        '    </div>'
        '    <div class="kc-hot-name">Vinícius Jr · Real Madrid</div>'
        '    <div class="kc-hot-price">63.10 <small>FTR</small></div>'
        '  </a>'
        '  <a href="asset.html?a=%24Musiala" class="kc-hot-card">'
        '    <div class="kc-hot-top">'
        '      <span class="kc-hot-ticker">$Musiala</span>'
        '      <span class="kc-hot-badge up">+5.1%</span>'
        '    </div>'
        '    <div class="kc-hot-name">Jamal Musiala · Bayern</div>'
        '    <div class="kc-hot-price">46.70 <small>FTR</small></div>'
        '  </a>'
        '</div>'

        '<!-- Player Shares Watchlist Section -->'
        '<div class="kc-group">'
        '  <div style="display:flex;align-items:center;justify-content:space-between;margin:0 0 10px 4px">'
        '    <div style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 115,\'wght\' 800;font-size:14px;color:var(--ink);letter-spacing:-.01em">PLAYER SHARES WATCHLIST</div>'
        '    <a href="exchange.html" style="font-size:11.5px;color:var(--lime);font-weight:600;display:flex;align-items:center;gap:3px">All 18 shares ›</a>'
        '  </div>'
        '  <div class="kc-cat-tabs" id="homeTabs" style="margin-bottom:10px">'
        '    <button type="button" class="kc-cat-tab on" data-f="hot">Hot 🔥</button>'
        '    <button type="button" class="kc-cat-tab" data-f="gainers">Top Gainers</button>'
        '    <button type="button" class="kc-cat-tab" data-f="forwards">Forwards</button>'
        '    <button type="button" class="kc-cat-tab" data-f="midfielders">Midfielders</button>'
        '    <button type="button" class="kc-cat-tab" data-f="coaches">Coaches</button>'
        '  </div>'
        '  <div id="homeMarketRows" class="kc-home-rows"></div>'
        '</div>'

        '<!-- Dream Club Card -->'
        '<a href="clubs.html" class="kc-ref-card" style="margin-top:18px">'
        '  <div class="kc-ref-left">'
        '    <div class="kc-ref-title">Dream Club: Zero FC · #124</div>'
        '    <div class="kc-ref-sub">Gameweek 28: 11 of 11 starters owned · +15.0% boost</div>'
        '  </div>'
        '  <div class="kc-ref-icon-box">'
        '    <div style="font-family:Archivo;font-weight:900;color:var(--lime);font-size:18px">ZF</div>'
        '  </div>'
        '</a>'

        '</div></main>')]

DASH_JS = r"""
(function(){
  // Countdown to Gameweek 28 lock
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

  // Toggle balance visibility
  var eye = document.getElementById('balEyeBtn');
  var bVal = document.getElementById('homeBalVal');
  var bSub = document.getElementById('homeBalSub');
  var hidden = localStorage.getItem('ft_hide_bal') === 'true';
  function updateBalVis(){
    if(!bVal) return;
    if(hidden){
      bVal.textContent = '******';
      if(bSub) bSub.textContent = '≈ $*** USD';
    } else {
      var s = FT.getState();
      var net = FT.holdingsValue() + s.wallet.balance + s.wallet.locked;
      bVal.textContent = net.toLocaleString('en-US');
      if(bSub) bSub.textContent = '≈ $' + (net * 0.1).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' USD';
    }
  }
  if(eye){
    eye.addEventListener('click', function(){
      hidden = !hidden;
      localStorage.setItem('ft_hide_bal', hidden ? 'true' : 'false');
      updateBalVis();
    });
  }
  updateBalVis();
  window.addEventListener('fantrade:statechange', updateBalVis);

  // Render market rows matching exchange style strictly with football player & coach shares
  var homeFilter = 'hot';
  var searchKeyword = '';

  var searchEl = document.getElementById('homeSearchInput');
  if(searchEl){
    searchEl.addEventListener('input', function(){
      searchKeyword = searchEl.value.trim().toLowerCase();
      renderHomeRows();
    });
  }

  function renderHomeRows(){
    var box = document.getElementById('homeMarketRows');
    if(!box) return;
    var list = ASSETS.slice();
    if(searchKeyword){
      list = list.filter(function(a){
        return a.t.toLowerCase().indexOf(searchKeyword) >= 0 ||
               a.n.toLowerCase().indexOf(searchKeyword) >= 0 ||
               (a.club && a.club.toLowerCase().indexOf(searchKeyword) >= 0);
      });
    } else {
      if(homeFilter === 'hot') list = list.filter(function(a){ return ['$Saka','$Haaland','$Mbappe','$Yamal','$Palmer','$Arteta'].indexOf(a.t) >= 0; });
      else if(homeFilter === 'gainers') list = list.slice().sort(function(a,b){ return b.d - a.d; }).slice(0, 7);
      else if(homeFilter === 'forwards') list = list.filter(function(a){ return a.pos === 'FWD'; });
      else if(homeFilter === 'midfielders') list = list.filter(function(a){ return a.pos === 'MID'; });
      else if(homeFilter === 'coaches') list = list.filter(function(a){ return a.c || a.pos === 'MGR'; });
    }

    if(!list.length){
      box.innerHTML = '<div style="text-align:center;padding:32px 16px;color:#767c82;font-size:12px">No player shares match your search.</div>';
      return;
    }

    box.innerHTML = list.map(function(a){
      var up = a.d >= 0;
      var to = 'asset.html?a=' + encodeURIComponent(a.t);
      var sym = a.t.replace('$', '');
      var quote = a.q || 'FTR';
      var posTag = a.pos || (a.c ? 'MGR' : 'FWD');
      var clubName = a.club || (a.c ? 'Premier League Manager' : 'Premier League');
      return "<a class='kc-row' href='" + to + "'>"
        + "<div class='kc-row-left'>"
        + "  <div class='kc-avatar" + (a.c ? " coach" : "") + "'>" + playerPhoto(a.t,a.n) + "</div>"
        + "  <div style='min-width:0'>"
        + "    <div class='kc-pair-title'>"
        + "      <span>" + sym + "</span>"
        + "      <span class='kc-pair-quote'>/" + quote + "</span>"
        + "      <span class='kc-tag" + (a.c ? " coach-tag" : "") + "'>" + posTag + "</span>"
        + "    </div>"
        + "    <div class='kc-pair-sub'>" + a.n + " · " + clubName + "</div>"
        + "  </div>"
        + "</div>"
        + "<div class='kc-row-mid'>"
        + "  <div class='kc-price-main'>" + (a.p > 999 ? a.p.toLocaleString('en-US', {minimumFractionDigits: 1, maximumFractionDigits: 2}) : a.p.toFixed(2)) + " <span style='font-size:10px;color:#767c82'>FTR</span></div>"
        + "  <div class='kc-price-sub'>≈ $" + (a.p * 0.1).toFixed(2) + " USD</div>"
        + "</div>"
        + "<div class='kc-row-right'>"
        + "  <div class='kc-pill" + (up ? "" : " down") + "'>" + (up ? "+" : "") + a.d.toFixed(2) + "%</div>"
        + "</div>"
        + "</a>";
    }).join('');
  }

  document.querySelectorAll('#homeTabs button').forEach(function(b){
    b.addEventListener('click', function(){
      document.querySelectorAll('#homeTabs button').forEach(function(x){ x.classList.remove('on'); });
      b.classList.add('on');
      homeFilter = b.dataset.f;
      renderHomeRows();
    });
  });
  renderHomeRows();
})();
"""

page("dashboard.html", "Home — Fantrade", "".join(da), DASH_JS, DASH_CSS)
print("built dashboard.html")

# ══════════════════════════════════════════════════════════════════
# PORTFOLIO & LEDGER
# ══════════════════════════════════════════════════════════════════
PF_CSS = """
.hcols{grid-template-columns:1.7fr .8fr .85fr .8fr .9fr 1.05fr 1.15fr 86px}
.lcols{grid-template-columns:132px 1.6fr .9fr 1fr 104px}
.chart-x{display:flex;justify-content:space-between;font-family:'Montserrat', sans-serif;font-size:10px;
  color:var(--faint);margin-top:10px}
.seg-sm{display:flex;gap:4px;padding:4px;border-radius:999px;background:rgba(255,255,255,.035);
  border:1px solid var(--hair);box-shadow:var(--inset)}
.seg-sm button{border:0;background:transparent;color:var(--dim);border-radius:999px;padding:7px 15px;cursor:pointer;
  font-weight:600;font-size:10px;letter-spacing:.1em;text-transform:uppercase;transition:all .5s var(--ease)}
.seg-sm button[aria-pressed="true"]{background:var(--lime);color:#fff}
.seg-sm button:hover:not([aria-pressed="true"]){color:var(--ink)}
.hashm{font-family:'Montserrat', sans-serif;font-size:11px;color:var(--faint)}
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

pf = [T('<main><div class="kc-home-wrap">'
        '<div class="kc-p-topbar">'
        '  <a href="account.html" class="kc-p-back" title="Back to Account">'
        '    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>'
        '  </a>'
        '  <div style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:18px;color:var(--ink)">Portfolio &amp; Ledger</div>'
        '  <button type="button" class="kc-p-action-btn" id="pfExport" title="Export CSV">'
        '    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'
        '  </button>'
        '</div>'
        '<div class="bento">')]

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
            '<i style="width:66%;background:linear-gradient(90deg,#0f0075,#1800ad)"></i>'
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
            '<i style="display:inline-block;width:8px;height:8px;border-radius:3px;background:#1800ad;margin-right:9px"></i>',
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
pf.append(T('<div class="bezel c12" data-reveal><div class="core mobile-flat">'
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
pf.append(T('<div class="bezel c7" data-reveal><div class="core mobile-flat">'
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

pf.append('</div></div></main>')

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
  font-size:11px;color:#fff}
.club-cell .cn{font-size:13.5px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.div-card{border:1px solid var(--hair);background:rgba(255,255,255,.03);border-radius:18px;padding:20px;
  box-shadow:var(--inset);display:flex;gap:16px;align-items:flex-start;margin-bottom:10px}
.div-card:last-child{margin-bottom:0}
.div-card .dot{width:9px;height:9px;border-radius:99px;flex:none;margin-top:6px}
.div-card b{display:block;font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 800;
  text-transform:uppercase;font-size:14px;margin-bottom:4px}
.div-card .r{font-size:11.5px;color:var(--faint);font-weight:300}
.div-card .pp{margin-left:auto;text-align:right;flex:none}
.div-card .pp em{font-style:normal;font-family:'Montserrat', sans-serif;font-size:15px;color:var(--lime)}
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
    (1, "Apex Titans FC", "@TacticalKlopp", 48, 612400, 7.2, ["Mbappé 98", "Haaland 97", "Vinícius 95"],
     "$Pep · 4-3-3 Tiki-taka", 18.5, 14890, 34200, "apex", "#1800ad"),
    (2, "Galactico Syndicate", "@ZidaneTactics", 32, 540100, 5.6, ["Bellingham 96", "Kane 95", "Rodri 94"],
     "$DonCarlo · 4-3-1-2 Fluid", 17.0, 13920, 29800, "apex", "#F4F6F1"),
    (3, "Arsenal Elite FC", "@GoonerBoss", 112, 495200, 6.9, ["Saka 95", "Ødegaard 94", "Saliba 93"],
     "$Arteta · 4-3-3 Inverted", 16.5, 13450, 27100, "apex", "#FF5E8A"),
    (4, "Bavarian Meta XI", "@KaiserTactics", 19, 462800, 2.5, ["Musiala 94", "Sané 91", "Kimmich 93"],
     "$Alonso · 3-4-2-1 Dominance", 14.0, 12890, 23500, "apex", "#4DA6FF"),
    (5, "Lombardia Capital", "@MilanoWhale", 61, 420500, -0.9, ["Lautaro 93", "Barella 92", "Bastoni 91"],
     "$Inzaghi · 3-5-2 Direct", 13.5, 12110, 21200, "apex", "#FF6A1F"),
    (6, "Anfield Collective", "@KopLedger", 88, 398400, 3.1, ["Salah 94", "Van Dijk 92", "Szoboszlai 89"],
     "$Slot · 4-3-3 High press", 13.0, 11740, 19900, "apex", "#FF5E5E"),
    (7, "Seleção Futures", "@SambaStake", 27, 371900, 4.4, ["Vinícius 95", "Rodrygo 90", "Éder 88"],
     "$Dorival · 4-2-3-1 Counter", 12.5, 11020, 18300, "apex", "#1800ad"),
    (124, "Zero FC", "You · single-owner", 1, 245800, 7.9, ["Bruno 90", "Saka 95", "Haaland 97"],
     "$Arteta · 4-3-3 High press", 15.0, 8420, 18400, "apex", "#1800ad"),
    (151, "Rioja Rising", "@TempranilloFC", 12, 198200, 1.4, ["Yamal 92", "Pedri 91", "Cubarsí 87"],
     "$Flick · 4-3-3 Youth", 11.0, 7180, 9400, "contender", "#FF6A1F"),
    (188, "Naija Nine", "@LagosLedger", 34, 176500, 9.8, ["Osimhen 91", "Lookman 88", "Iwobi 84"],
     "$Peseiro · 4-4-2 Wide", 10.5, 6640, 8800, "contender", "#4DA6FF"),
    (214, "Porto Alegre XI", "@GauchoGains", 8, 154300, -2.2, ["Diogo 89", "Vitinha 88", "Pepê 85"],
     "$Amorim · 3-4-3 Press", 9.5, 6020, 7100, "contender", "#F4F6F1"),
    (503, "Academy Origins", "@FirstTeamFund", 5, 84600, 12.6, ["Yıldız 84", "Endrick 83", "Zaïre 82"],
     "$Motta · 4-2-3-1 Raw", 7.0, 3910, 3200, "challenger", "#FF5E8A"),
    (612, "Sunday League Ltd", "@ParkPitchDAO", 3, 61200, 5.5, ["Elanga 81", "Mainoo 83", "Hato 80"],
     "$Dyche · 4-4-2 Honest", 6.5, 3140, 2400, "challenger", "#1800ad"),
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
            '<stop offset="0%%" stop-color="#1800ad" stop-opacity=".22"/>'
            '<stop offset="100%%" stop-color="#1800ad" stop-opacity="0"/></linearGradient></defs>'
            '<polygon points="0,%d %s %d,%d" fill="url(#lbg)"/>'
            '<polyline points="%s" fill="none" stroke="#4DA6FF" stroke-width="1.4" stroke-dasharray="4 4" opacity=".8"/>'
            '<polyline points="%s" fill="none" stroke="#1800ad" stroke-width="1.8" stroke-linejoin="round"/>'
            '</svg>' % (w, h, h, " ".join(pa), w, h, " ".join(pb), " ".join(pa)))


lb = [T('<main><div class="kc-home-wrap">'
        '<div class="kc-p-topbar">'
        '  <div class="kc-p-title-group">'
        '    <a href="dashboard.html" class="kc-p-back" title="Back to Home">'
        '      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>'
        '    </a>'
        '    <div style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:18px;color:var(--ink);white-space:nowrap">League Standings</div>'
        '  </div>'
        '  <a href="divisions.html" class="kc-p-action-btn" title="Divisions">'
        '    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
        '  </a>'
        '</div>'
        '<div class="bento">')]

# your rank, as a strip
lb.append(T('<div class="bezel flat c12" data-reveal><div class="core pad-sm">'
            '<div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">'
            '<div class="crest-lg" id="lbCrest" style="background:linear-gradient(160deg,#1800ad,#0f0075)">ZF</div>'
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

lb.append('</div></div></main>')

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
          + 'line-height:1.6;background:var(--lime);border-color:var(--lime);color:#fff">Rebalance</a>'
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
        + '<div class="m-row total"><span>Total Fans Point</span><b>' + money(b.fp) + ' FP</b></div>'
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
.nt-filter-head{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:18px 18px 12px}
.nt-filter-head .markets{flex:1;min-width:0;overflow-x:auto;flex-wrap:nowrap;scrollbar-width:none}
.nt-read{border:0;background:transparent;color:var(--lime);font:600 10px Montserrat,sans-serif;white-space:nowrap;cursor:pointer;padding:7px 4px}
@media(max-width:560px){.nt-filter-head{align-items:flex-start;flex-direction:column}.nt-read{align-self:flex-end}}
"""

nt = [T('<main><div class="kc-home-wrap">'
        '<div class="kc-p-topbar">'
        '  <a href="dashboard.html" class="kc-p-back" title="Back to Home">'
        '    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>'
        '  </a>'
        '  <div style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:18px;color:var(--ink)">Notifications</div>'
        '  <a href="settings-alerts.html" class="kc-p-action-btn" title="Notification settings" aria-label="Notification settings">'
        '    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.9"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.05.05a2 2 0 1 1-2.83 2.83l-.05-.05a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21a2 2 0 1 1-4 0v-.07a1.7 1.7 0 0 0-1.03-1.56 1.7 1.7 0 0 0-1.88.34l-.05.05a2 2 0 1 1-2.83-2.83l.05-.05A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.03H3a2 2 0 1 1 0-4h.04A1.7 1.7 0 0 0 4.6 8.94a1.7 1.7 0 0 0-.34-1.88l-.05-.05a2 2 0 1 1 2.83-2.83l.05.05a1.7 1.7 0 0 0 1.88.34A1.7 1.7 0 0 0 10 3.01V3a2 2 0 1 1 4 0v.01a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.05-.05a2 2 0 1 1 2.83 2.83l-.05.05a1.7 1.7 0 0 0-.34 1.88 1.7 1.7 0 0 0 1.56 1.03H21a2 2 0 1 1 0 4h-.04A1.7 1.7 0 0 0 19.4 15z"/></svg>'
        '  </a>'
        '</div>'
        '<div class="bento">')]

nt.append(T('<div class="bezel c12" data-reveal><div class="core mobile-flat">'
            '<div class="nt-filter-head"><div class="markets" id="ntFilter">'
            '<button class="mkt" type="button" aria-pressed="true" data-k="all">Everything</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-k="settle">Settlements</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-k="order">Orders</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-k="club">Club</button>'
            '<button class="mkt" type="button" aria-pressed="false" data-k="system">Account</button>'
            '</div><button type="button" class="nt-read" id="ntRead">Mark all read · <span id="ntTotal">8</span></button></div><div id="ntFeed"></div>'
            '<div style="padding:22px 24px 28px;text-align:center">'
            '<span style="font-size:11.5px;color:var(--faint);font-weight:300">'
            'Activity older than 90 days is available in your ledger export.</span></div>'
            '</div></div>'))

nt.append('</div></div></main>')

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
  var total = document.getElementById('ntTotal');
  if(total) total.textContent = s.notifications.length;

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
.kc-settings-wrap{width:min(820px,100%);margin:0 auto;padding:6px 16px 110px;box-sizing:border-box}
.settings-head{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:6px 0 18px}
.settings-head-copy{min-width:0;text-align:center}
.settings-head-copy h1{font:800 19px Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;margin:0;color:var(--ink)}
.settings-head-copy p{font-size:10.5px;color:var(--faint);margin:3px 0 0}
.settings-nav{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:7px;margin:0 0 14px}
.settings-nav a{min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding:11px 5px;border:1px solid rgba(255,255,255,.065);border-radius:12px;background:rgba(255,255,255,.025);color:var(--faint);text-decoration:none;text-align:center;font-size:9px;line-height:1.2;transition:.2s ease}
.settings-nav a .ic{width:16px;height:16px}
.settings-nav a:hover{color:var(--ink);border-color:rgba(255,255,255,.14);background:rgba(255,255,255,.045)}
.settings-nav a.on{color:#0a0d03;background:var(--lime);border-color:var(--lime);box-shadow:var(--shadow-action)}
.settings-hero{padding:3px 2px 14px}
.settings-hero h2{margin:0 0 5px;font:800 17px Archivo,sans-serif!important;text-transform:none!important}
.settings-hero p{margin:0;color:var(--faint);font-size:11.5px}
.settings-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.settings-card{display:flex;align-items:center;gap:13px;padding:16px;border:1px solid rgba(255,255,255,.07);border-radius:15px;background:rgba(10,12,14,.7);color:var(--ink);text-decoration:none;box-shadow:var(--shadow-card);transition:.2s ease}
.settings-card:hover{transform:translateY(-2px);border-color:rgba(24,0,173,.22)}
.settings-card .bd{min-width:0;flex:1}.settings-card b{display:block;font-size:13px}.settings-card p{font-size:10.5px;line-height:1.45;color:var(--faint);margin:4px 0 0}
.settings-card>.ic{width:14px;height:14px;color:var(--faint)}
.sec-card>.core{background:linear-gradient(145deg,rgba(16,19,18,.92),rgba(8,10,10,.96))}
@media(max-width:680px){
  .kc-settings-wrap{padding-left:12px;padding-right:12px}
  .settings-nav{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:2px}
  .settings-nav a{flex:0 0 82px;scroll-snap-align:start}
  .settings-grid{grid-template-columns:1fr}
  .sec-title{align-items:flex-start}.sec-title p{max-width:36ch}
}
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
            '<button class="sw" type="button" aria-pressed="true" data-c="#1800ad" data-n="Indigo" '
            'style="background:linear-gradient(160deg,#1800ad,#0f0075)" aria-label="Indigo"></button>'
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


AC_CSS = """
/* KuCoin Mobile Profile Page Design (Screenshot 3 Match) */
.kc-profile-wrap{max-width:560px;margin:0 auto;padding:8px 16px 110px}
.kc-p-topbar{display:flex;align-items:center;justify-content:space-between;padding:6px 0 16px}
.kc-p-back{width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);display:grid;place-items:center;color:var(--ink);cursor:pointer;text-decoration:none;transition:background .2s}
.kc-p-back:hover{background:rgba(255,255,255,.09)}
.kc-p-actions{display:flex;align-items:center;gap:10px}
.kc-p-action-btn{width:38px;height:38px;border-radius:50%;background:transparent;border:0;color:var(--ink);display:grid;place-items:center;cursor:pointer;transition:background .2s;text-decoration:none}
.kc-p-action-btn:hover{background:rgba(255,255,255,.06)}

/* Hero Avatar & Identity */
.kc-p-hero{display:flex;flex-direction:column;align-items:center;text-align:center;padding:6px 0 20px}
.kc-p-avatar-box{position:relative;width:88px;height:88px;margin-bottom:12px}
.kc-p-avatar-img{width:100%;height:100%;border-radius:50%;object-fit:cover;border:2.5px solid var(--lime);box-shadow:0 0 24px rgba(24,0,173,.2)}
.kc-p-name-row{display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:5px}
.kc-p-username{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;font-size:22px;letter-spacing:-.01em;color:var(--ink)}
.kc-p-edit-btn{background:transparent;border:0;color:#767c82;cursor:pointer;display:grid;place-items:center;padding:2px;transition:color .15s}
.kc-p-edit-btn:hover{color:var(--lime)}
.kc-p-uid-row{display:flex;align-items:center;justify-content:center;gap:6px;font-family:'Montserrat', sans-serif;font-size:12px;color:#767c82;margin-bottom:14px}
.kc-p-copy-btn{background:transparent;border:0;color:inherit;cursor:pointer;display:grid;place-items:center;padding:2px;transition:color .15s}
.kc-p-copy-btn:hover{color:var(--lime)}

/* Status Pills */
.kc-p-pills{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap}
.kc-p-pill{display:inline-flex;align-items:center;gap:5px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:999px;padding:5px 13px;font-size:11.5px;color:#8E9AA8;text-decoration:none;cursor:pointer;transition:border-color .2s,background .2s}
.kc-p-pill:hover{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.16);color:var(--ink)}
.kc-p-pill.safeguard{color:var(--lime);border-color:rgba(24,0,173,.25);background:rgba(24,0,173,.06)}
.kc-p-pill .chev{font-size:11px;opacity:.7;margin-left:2px}

/* Referral Banner Card */
.kc-ref-card{display:flex;align-items:center;justify-content:space-between;gap:16px;background:linear-gradient(135deg,rgba(255,255,255,.04) 0%,rgba(255,255,255,.02) 100%);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:16px 20px;margin:18px 0 24px;text-decoration:none;cursor:pointer;transition:border-color .2s,transform .2s}
.kc-ref-card:hover{border-color:rgba(24,0,173,.3);transform:translateY(-1px)}
.kc-ref-left{flex:1}
.kc-ref-title{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 115,'wght' 700;font-size:16px;color:var(--ink);margin-bottom:4px}
.kc-ref-sub{font-size:12px;color:#767c82}
.kc-ref-icon-box{width:56px;height:56px;flex-shrink:0;border-radius:14px;overflow:hidden;background:rgba(255,255,255,.05);display:grid;place-items:center}
.kc-ref-icon-box img{width:100%;height:100%;object-fit:cover}

/* Grouped Lists */
.kc-group{margin-bottom:22px}
.kc-group-title{font-size:11.5px;font-weight:600;color:#767c82;text-transform:none;letter-spacing:.02em;margin:0 0 8px 4px}
.kc-group-box{background:rgba(10,12,14,.6);border:1px solid rgba(255,255,255,.06);border-radius:14px;overflow:hidden}
.kc-item-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.04);text-decoration:none;color:var(--ink);cursor:pointer;transition:background .15s;background:transparent;border-left:0;border-right:0;border-top:0;width:100%;box-sizing:border-box;font-family:inherit}
.kc-item-row:last-child{border-bottom:0}
.kc-item-row:hover{background:rgba(255,255,255,.025)}
.kc-item-left{display:flex;align-items:center;gap:14px;flex:1;min-width:0;text-align:left}
.kc-item-ico{width:22px;height:22px;display:grid;place-items:center;color:#8E9AA8;flex-shrink:0}
.kc-item-text-wrap{min-width:0}
.kc-item-title{font-size:14px;font-weight:500;color:var(--ink)}
.kc-item-desc{font-size:11px;color:#767c82;margin-top:2px}
.kc-item-right{display:flex;align-items:center;gap:8px;font-size:12px;color:#767c82;flex-shrink:0}
.kc-badge-k1{display:inline-flex;align-items:center;gap:4px;color:#8E9AA8;font-size:11.5px}
.kc-badge-k1 .k1-tag{background:rgba(24,0,173,.15);color:var(--lime);font-size:9.5px;font-weight:700;padding:1px 5px;border-radius:4px}
.kc-chevron{color:#555c63}

/* Toggle Switch */
.kc-switch{position:relative;width:40px;height:22px;background:rgba(255,255,255,.14);border-radius:999px;border:0;cursor:pointer;transition:background .2s;padding:2px}
.kc-switch.on{background:var(--lime)}
.kc-switch i{display:block;width:18px;height:18px;background:#fff;border-radius:50%;transition:transform .2s;box-shadow:0 1px 3px rgba(0,0,0,.3)}
.kc-switch.on i{transform:translateX(18px);background:#000}

/* Toast */
.kc-toast{position:fixed;top:28px;left:50%;transform:translateX(-50%) translateY(-20px);background:rgba(18,20,23,.95);border:1px solid var(--lime);color:var(--ink);padding:10px 20px;border-radius:999px;font-size:12px;font-family:Montserrat,sans-serif;font-weight:600;display:flex;align-items:center;gap:8px;box-shadow:0 8px 30px rgba(0,0,0,.6);opacity:0;pointer-events:none;transition:all .25s ease;z-index:999}
.kc-toast.show{opacity:1;transform:translateX(-50%) translateY(0);pointer-events:auto}
"""

ac = [T('<main><div class="kc-profile-wrap">'
        '<!-- Top Navigation Bar -->'
        '<div class="kc-p-topbar">'
        '  <a href="dashboard.html" class="kc-p-back" id="kcBackBtn" title="Back" onclick="if(window.history.length>1){window.history.back();return false;}">'
        '    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>'
        '  </a>'
        '  <div style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:17px;color:var(--ink);letter-spacing:.02em">PROFILE</div>'
        '  <div class="kc-p-actions">'
        '    <a href="notifications.html" class="kc-p-action-btn" title="Support &amp; Notifications">'
        '      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>'
        '    </a>'
        '    <a href="receive.html" class="kc-p-action-btn" title="Scan">'
        '      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 8V5a1 1 0 0 1 1-1h3M4 16v3a1 1 0 0 0 1 1h3M16 4h3a1 1 0 0 1 1 1v3M16 20h3a1 1 0 0 0 1-1v-3"/></svg>'
        '    </a>'
        '    <button type="button" class="kc-p-action-btn" id="kcSwitchProfileBtn" title="Add / Switch Profile">'
        '      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>'
        '    </button>'
        '  </div>'
        '</div>'

        '<!-- Hero Avatar & Identity -->'
        '<div class="kc-p-hero">'
        '  <div class="kc-p-avatar-box">'
        '    <img src="assets/astronaut_avatar.jpg" alt="Avatar" class="kc-p-avatar-img">'
        '  </div>'
        '  <div class="kc-p-name-row">'
        '    <span class="kc-p-username" id="kcUsername">Viceonchain</span>'
        '    <button type="button" class="kc-p-edit-btn" id="kcEditNameBtn" title="Edit username">'
        '      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>'
        '    </button>'
        '  </div>'
        '  <div class="kc-p-uid-row">'
        '    <span>UID: <span id="kcUid">242423082</span></span>'
        '    <button type="button" class="kc-p-copy-btn" id="kcCopyUidBtn" title="Copy UID">'
        '      <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
        '    </button>'
        '  </div>'
        '  <div class="kc-p-pills">'
        '    <button type="button" class="kc-p-pill" id="kcVipPill">'
        '      <span style="font-size:10.5px;border-radius:50%;width:14px;height:14px;display:inline-grid;place-items:center;border:1px solid currentColor">V</span>'
        '      <span>VIP 0</span>'
        '      <span class="chev">›</span>'
        '    </button>'
        '    <button type="button" class="kc-p-pill safeguard" id="kcSafeguardPill">'
        '      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>'
        '      <span>Safeguard</span>'
        '      <span class="chev">›</span>'
        '    </button>'
        '    <button type="button" class="kc-p-pill" id="kcVerifiedPill">'
        '      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
        '      <span>Verified</span>'
        '      <span class="chev">›</span>'
        '    </button>'
        '  </div>'
        '</div>'

        '<!-- Referral Program Banner Card -->'
        '<div class="kc-ref-card" id="kcReferralCard" role="button" tabindex="0">'
        '  <div class="kc-ref-left">'
        '    <div class="kc-ref-title">Referral Program</div>'
        '    <div class="kc-ref-sub">Refer friends to earn a 35% commission</div>'
        '  </div>'
        '  <div class="kc-ref-icon-box">'
        '    <img src="assets/referral_icon.jpg" alt="Referral">'
        '  </div>'
        '</div>'

        '<!-- Section: Account -->'
        '<div class="kc-group">'
        '  <div class="kc-group-title">Account</div>'
        '  <div class="kc-group-box">'
        '    <div class="kc-item-row" id="kcLoyaltyRow" role="button" tabindex="0">'
        '      <div class="kc-item-left">'
        '        <div class="kc-item-ico"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 9H4a2 2 0 0 1-2-2V5h4M18 9h2a2 2 0 0 0 2-2V5h-4M6 5h12v6a6 6 0 0 1-12 0V5z"/><line x1="12" y1="17" x2="12" y2="21"/><line x1="8" y1="21" x2="16" y2="21"/></svg></div>'
        '        <div class="kc-item-text-wrap"><div class="kc-item-title">$FTR Loyalty Level</div></div>'
        '      </div>'
        '      <div class="kc-item-right">'
        '        <span class="kc-badge-k1"><span class="k1-tag">F1</span> To be Unlocked</span>'
        '        <svg class="kc-chevron" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>'
        '      </div>'
        '    </div>'
        '    <div class="kc-item-row" id="kcFeesVipRow" role="button" tabindex="0">'
        '      <div class="kc-item-left">'
        '        <div class="kc-item-ico"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg></div>'
        '        <div class="kc-item-text-wrap"><div class="kc-item-title">Fees &amp; VIP</div></div>'
        '      </div>'
        '      <div class="kc-item-right">'
        '        <span>VIP 0</span>'
        '        <svg class="kc-chevron" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>'
        '      </div>'
        '    </div>'
        '    <div class="kc-item-row">'
        '      <div class="kc-item-left">'
        '        <div class="kc-item-ico"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M12 6v12M2 12a2 2 0 0 0 2-2V8M22 12a2 2 0 0 1-2-2V8"/></svg></div>'
        '        <div class="kc-item-text-wrap">'
        '          <div class="kc-item-title">Pay Fees with $FTR</div>'
        '          <div class="kc-item-desc">20% off on trading fees</div>'
        '        </div>'
        '      </div>'
        '      <div class="kc-item-right">'
        '        <button type="button" class="kc-switch on" id="kcFeeSwitch" aria-label="Toggle pay fees with $FTR"><i></i></button>'
        '      </div>'
        '    </div>'
        '    <a href="portfolio.html" class="kc-item-row">'
        '      <div class="kc-item-left">'
        '        <div class="kc-item-ico"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>'
        '        <div class="kc-item-text-wrap"><div class="kc-item-title">Trade History &amp; Ledger</div></div>'
        '      </div>'
        '      <div class="kc-item-right">'
        '        <svg class="kc-chevron" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>'
        '      </div>'
        '    </a>'
        '  </div>'
        '</div>'

        '<!-- Section: Security & System -->'
        '<div class="kc-group">'
        '  <div class="kc-group-title">Security &amp; System</div>'
        '  <div class="kc-group-box">'
        '    <a href="settings-security.html" class="kc-item-row">'
        '      <div class="kc-item-left">'
        '        <div class="kc-item-ico"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div>'
        '        <div class="kc-item-text-wrap"><div class="kc-item-title">Security Settings</div></div>'
        '      </div>'
        '      <div class="kc-item-right">'
        '        <span>Change password</span>'
        '        <svg class="kc-chevron" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>'
        '      </div>'
        '    </a>'
        '    <a href="settings.html" class="kc-item-row">'
        '      <div class="kc-item-left">'
        '        <div class="kc-item-ico"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></div>'
        '        <div class="kc-item-text-wrap"><div class="kc-item-title">Profile &amp; App Settings</div><div class="kc-item-desc">Profile, club, alerts, wallet and play limits</div></div>'
        '      </div>'
        '      <div class="kc-item-right">'
        '        <span>7 sections</span>'
        '        <svg class="kc-chevron" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>'
        '      </div>'
        '    </a>'
        '  </div>'
        '</div>'

        '<!-- Section: Rewards -->'
        '<div class="kc-group">'
        '  <div class="kc-group-title">Rewards</div>'
        '  <div class="kc-group-box">'
        '    <a href="fanplay.html" class="kc-item-row">'
        '      <div class="kc-item-left">'
        '        <div class="kc-item-ico"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/></svg></div>'
        '        <div class="kc-item-text-wrap"><div class="kc-item-title">Rewards Hub &amp; Matchday Pool</div></div>'
        '      </div>'
        '      <div class="kc-item-right">'
        '        <svg class="kc-chevron" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>'
        '      </div>'
        '    </a>'
        '  </div>'
        '</div>'

        '<!-- Sign Out Row -->'
        '<div style="margin-top:20px;text-align:center">'
        '  <button type="button" class="btn btn-glass" id="kcSignOutBtn" style="width:100%;justify-content:center;padding:12px;border-radius:12px;font-size:13px;color:#FF5E5E;border-color:rgba(255,94,94,.2)">'
        '    Sign Out'
        '  </button>'
        '</div>'

        '<!-- Feedback Toast -->'
        '<div id="kcToast" class="kc-toast">'
        '  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--lime)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
        '  <span id="kcToastText">UID copied to clipboard</span>'
        '</div>'

        '</div></main>')]

AC_JS = r"""
(function(){
  function showToast(txt){
    var t = document.getElementById('kcToast');
    var s = document.getElementById('kcToastText');
    if(!t) return;
    if(s) s.textContent = txt;
    t.classList.add('show');
    clearTimeout(t._timer);
    t._timer = setTimeout(function(){ t.classList.remove('show'); }, 2200);
  }

  // Copy UID
  var copyBtn = document.getElementById('kcCopyUidBtn');
  if(copyBtn){
    copyBtn.addEventListener('click', function(){
      var uid = document.getElementById('kcUid').textContent.trim();
      navigator.clipboard.writeText(uid).then(function(){
        showToast('UID ' + uid + ' copied to clipboard');
      }).catch(function(){
        showToast('UID: ' + uid);
      });
    });
  }

  // Edit username
  var editBtn = document.getElementById('kcEditNameBtn');
  var nameEl = document.getElementById('kcUsername');
  var storedName = localStorage.getItem('ft_username') || 'Viceonchain';
  if(nameEl) nameEl.textContent = storedName;

  if(editBtn && nameEl){
    editBtn.addEventListener('click', function(){
      var next = prompt('Enter display name:', nameEl.textContent);
      if(next && next.trim()){
        nameEl.textContent = next.trim();
        localStorage.setItem('ft_username', next.trim());
        showToast('Username updated to ' + next.trim());
      }
    });
  }

  // Toggle switch for fee discount
  var sw = document.getElementById('kcFeeSwitch');
  if(sw){
    var isOn = localStorage.getItem('ft_fee_discount') !== 'false';
    if(isOn) sw.classList.add('on');
    else sw.classList.remove('on');

    sw.addEventListener('click', function(){
      var now = sw.classList.toggle('on');
      localStorage.setItem('ft_fee_discount', now ? 'true' : 'false');
      showToast(now ? '20% fee discount enabled' : 'Fee discount disabled');
    });
  }

  // Interactive Modals for VIP, Safeguard, Verified, Referral, Loyalty, Security, Preferences
  function modal(title, bodyHtml){
    openModal('<h3 class="ft-modal-title">' + title + '</h3>'
      + '<div style="margin-top:12px;font-size:13px;color:var(--dim);line-height:1.6">' + bodyHtml + '</div>'
      + '<button class="btn btn-lime" onclick="closeModal()" type="button" style="width:100%;justify-content:center;margin-top:20px">Done</button>');
  }

  function on(id, fn){
    var el = document.getElementById(id);
    if(el) el.addEventListener('click', fn);
  }

  on('kcVipPill', function(){
    modal('VIP 0 Tier Benefits',
      '<div class="ft-modal-card">'
      + '<div class="m-row"><span>Maker Fee</span><b>0.100%</b></div>'
      + '<div class="m-row"><span>Taker Fee</span><b>0.100%</b></div>'
      + '<div class="m-row"><span>Fee with $FTR (20% off)</span><b style="color:var(--lime)">0.080%</b></div>'
      + '<div class="m-row total"><span>30-Day Share Volume</span><b>0 / 100,000 $FTR</b></div>'
      + '</div><p style="font-size:11.5px;color:#767c82;margin-top:10px">Reach 100,000 $FTR 30-day trading volume to unlock VIP 1 fee tier (0.07% / 0.09%).</p>');
  });

  on('kcFeesVipRow', function(){
    var p = document.getElementById('kcVipPill');
    if(p) p.click();
  });

  on('kcSafeguardPill', function(){
    modal('Account Safeguard',
      '<div class="ft-modal-card">'
      + '<div class="m-row"><span>Login 2FA</span><b style="color:var(--lime)">Enabled (App Authenticator)</b></div>'
      + '<div class="m-row"><span>Anti-Phishing Code</span><b style="color:var(--lime)">Active</b></div>'
      + '<div class="m-row"><span>Device Whitelist</span><b style="color:var(--lime)">Chrome Windows (London)</b></div>'
      + '<div class="m-row total"><span>Withdrawal Delay</span><b>0 seconds (Instant)</b></div>'
      + '</div>');
  });

  on('kcVerifiedPill', function(){
    modal('Identity Verification',
      '<div class="ft-modal-card">'
      + '<div class="m-row"><span>Status</span><b style="color:var(--lime)">Tier 2 Verified (Complete)</b></div>'
      + '<div class="m-row"><span>Daily Payout Limit</span><b>1,000,000 $FTR</b></div>'
      + '<div class="m-row"><span>FanPlay Entry Cap</span><b>Unlimited</b></div>'
      + '<div class="m-row total"><span>Jurisdiction</span><b>United Kingdom</b></div>'
      + '</div>');
  });

  on('kcReferralCard', function(){
    modal('Referral Program',
      '<p>Invite friends to trade player shares and play Matchdays on Fantrade. You earn <b>35% of all trading fees</b> they generate.</p>'
      + '<div class="tf" style="margin-top:14px"><label>Your Referral Link</label><div class="inp">'
      + '<input type="text" id="refLinkInput" value="https://fantrade.app/ref/vice2424" readonly>'
      + '</div></div>'
      + '<button class="btn btn-glass" id="copyRefLinkBtn" type="button" style="width:100%;justify-content:center;margin-top:6px">Copy Link</button>'
      + '<div class="ft-modal-card" style="margin-top:14px">'
      + '<div class="m-row"><span>Friends Invited</span><b>12 managers</b></div>'
      + '<div class="m-row total"><span>Total Commission Earned</span><b style="color:var(--lime)">14,820 $FTR</b></div>'
      + '</div>');
    var cb = document.getElementById('copyRefLinkBtn');
    if(cb){
      cb.addEventListener('click', function(){
        navigator.clipboard.writeText('https://fantrade.app/ref/vice2424').then(function(){
          showToast('Referral link copied to clipboard!');
        });
      });
    }
  });

  on('kcLoyaltyRow', function(){
    modal('$FTR Loyalty Level',
      '<div class="ft-modal-card">'
      + '<div class="m-row"><span>Current Status</span><b>F1 Member</b></div>'
      + '<div class="m-row"><span>$FTR Balance Staked</span><b style="color:var(--lime)">128,450 $FTR</b></div>'
      + '<div class="m-row"><span>Matchday Dividend Boost</span><b>+5.0%</b></div>'
      + '<div class="m-row total"><span>Next Tier (F2)</span><b>250,000 $FTR (+10% Boost)</b></div>'
      + '</div>');
  });

  on('kcSecurityRow', function(){
    modal('Security Settings',
      '<div class="ft-modal-card">'
      + '<div class="m-row"><span>Password</span><b>Last changed 14 days ago</b></div>'
      + '<div class="m-row"><span>Two-Factor Auth</span><b style="color:var(--lime)">Active</b></div>'
      + '<div class="m-row"><span>Active Sessions</span><b>1 device online</b></div>'
      + '<div class="m-row total"><span>Biometric Passkey</span><b style="color:var(--lime)">Supported</b></div>'
      + '</div>');
  });

  on('kcPreferencesRow', function(){
    modal('App Preferences',
      '<div class="ft-modal-card">'
      + '<div class="m-row"><span>Display Currency</span><b>USD ($) / $FTR</b></div>'
      + '<div class="m-row"><span>App Language</span><b>English (UK)</b></div>'
      + '<div class="m-row"><span>Theme</span><b style="color:var(--lime)">Dark Void (Default)</b></div>'
      + '<div class="m-row total"><span>Haptic Feedback</span><b style="color:var(--lime)">On</b></div>'
      + '</div>');
  });

  on('kcSwitchProfileBtn', function(){
    modal('Switch Profile',
      '<div class="ft-modal-card">'
      + '<div class="m-row" style="background:rgba(24,0,173,.08)"><span>Viceonchain (Active)</span><b style="color:var(--lime)">Primary Manager</b></div>'
      + '<div class="m-row"><span>NorthBank_Scout</span><b>Secondary Scout</b></div>'
      + '</div>'
      + '<p style="font-size:11.5px;color:#767c82;margin-top:10px">You can manage multiple football identities or club divisions under one wallet.</p>');
  });

  on('kcSignOutBtn', function(){
    showToast('Signed out of session. Redirecting to sign in...');
    setTimeout(function(){ window.location.href = 'signin.html'; }, 900);
  });
})();
"""

page("account.html", "Profile — Fantrade", "".join(ac), AC_JS, AC_CSS)
print("built account.html")

# Profile settings now use focused pages instead of redirects or one long screen.
SETTINGS_COPY = {
    "profile": ("Manager profile", "Control the identity shown with your club and activity."),
    "club": ("Club identity", "Set your club name, formation, colour and substitution rules."),
    "security": ("Security", "Manage your password, two-factor protection and active sessions."),
    "alerts": ("Notification settings", "Choose which match, market and account updates Fantrade sends."),
    "wallet": ("Wallet & payouts", "Review balances and choose where settled funds are paid."),
    "play": ("Responsible play", "Set clear limits and take a break whenever you need one."),
    "data": ("Data & account", "Export your information, reset the prototype or close the account."),
}

def settings_nav(active=""):
    links = []
    for key, icon_name, label in SETNAV:
        links.append('<a href="settings-%s.html" class="%s">%s<span>%s</span></a>' %
                     (key, "on" if key == active else "", ic(icon_name, "ic"), label))
    return '<nav class="settings-nav" aria-label="Profile settings">%s</nav>' % "".join(links)

def settings_top(title, subtitle):
    return ('<div class="settings-head">'
            '<a href="account.html" class="kc-p-back" title="Back to profile">'
            '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg></a>'
            '<div class="settings-head-copy"><h1>%s</h1><p>%s</p></div>'
            '<a href="notifications.html" class="kc-p-action-btn" title="Notifications">%s</a>'
            '</div>') % (title, subtitle, ic("pulse", "ic"))

settings_cards = []
for key, icon_name, label in SETNAV:
    title, desc = SETTINGS_COPY[key]
    settings_cards.append('<a class="settings-card" href="settings-%s.html"><span class="ibox">%s</span>'
                          '<div class="bd"><b>%s</b><p>%s</p></div>%s</a>' %
                          (key, ic(icon_name, "ic-lg"), title, desc, ic("arrow", "ic")))

settings_index = ('<main><div class="kc-settings-wrap">' +
                  settings_top("Profile settings", "Everything personal, in one place") +
                  '<div class="settings-hero"><h2>Choose what to update</h2><p>Changes save to your Fantrade profile and follow you across devices.</p></div>' +
                  '<div class="settings-grid">' + "".join(settings_cards) + '</div></div></main>')
page("settings.html", "Profile settings — Fantrade", settings_index, ST_JS, ST_CSS)
print("built settings.html")

for key, _icon_name, _label in SETNAV:
    title, desc = SETTINGS_COPY[key]
    body = ('<main><div class="kc-settings-wrap">' + settings_top(title, desc) +
            settings_nav(key) + SECTIONS[key] + '</div></main>')
    page("settings-%s.html" % key, "%s — Fantrade" % title, body, ST_JS, ST_CSS)
    print("built settings-%s.html" % key)

REDIRECT_TO_WALLET = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=ftr.html"><title>Redirecting to Wallet...</title><script>window.location.replace('ftr.html');</script></head><body style="background:#050505;color:#F4F6F1;font-family:sans-serif;display:grid;place-items:center;height:100vh;margin:0"><div style="text-align:center"><p style="color:#8E9AA8">Redirecting to your Wallet...</p><a href="ftr.html" style="color:#1800ad;font-weight:600">Click here if not redirected</a></div></body></html>"""

with open(os.path.join(OUT, "wallet.html"), "w", encoding="utf-8") as f:
    f.write(REDIRECT_TO_WALLET)
print("built wallet.html redirect -> ftr.html")
