# -*- coding: utf-8 -*-
"""Account + in-app surfaces: auth, onboarding, dashboard, portfolio,
leaderboard, notifications, settings. Same shell, same tokens as pages 1–6."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from app_design import apply_design, intro, tab_intro
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
    html = apply_design(fname, html)
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
      + '<button class="auth-submit" id="resetGo" type="button" style="margin-top:8px">Send reset link</button>');
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


AUTH_PAGE_CSS = """
/* Sign in and sign up share the onboarding look: black canvas, lowercase
   wordmark, one centred column, filled fields and an indigo pill action. */
body{background:#050505;--dim:#b9bcb7;--faint:#979c96;--ink:#f4f6f1;--lime:#1800ad}
.orb,.grain{display:none}
.nav-min{top:0;min-height:76px;padding:16px 32px;padding-top:calc(16px + env(safe-area-inset-top));background:#050505}
.nav-min .logo{font-family:Space Grotesk,system-ui,sans-serif;font-size:25px;text-transform:lowercase;letter-spacing:-.03em}
.nav-min .brand-logo-img{width:28px;height:28px}
.nav-min a.back{min-height:44px;font-family:Montserrat,system-ui,sans-serif;letter-spacing:0;text-transform:none;font-size:12px;color:var(--dim)}
.auth-page{width:min(460px,100%);margin:auto;padding:128px 24px 64px}
.auth-intro{text-align:center;margin-bottom:36px}
.auth-intro h1{font-family:Space Grotesk,system-ui,sans-serif;font-size:clamp(28px,4.2vw,42px);font-weight:700;line-height:1.08;text-transform:none;letter-spacing:-.035em;margin:0}
.auth-intro p{font-size:14px;color:var(--dim);line-height:1.6;margin:14px auto 0;max-width:36ch}
.tf{margin-bottom:20px}
.tf label{font-size:13px;text-transform:none;letter-spacing:0;color:var(--dim);font-weight:500;margin-bottom:8px}
.tf .lrow{align-items:center;margin-bottom:8px}
.tf .lrow label{margin:0}
.tf .lrow a,.checkrow a,.auth-alt a{display:inline-flex;align-items:center;justify-content:center;min-height:30px;padding:5px 14px;border:0;border-radius:999px;background:#1800ad;color:#fff;font-size:13px;font-weight:600;text-decoration:none;white-space:nowrap;cursor:pointer;transition:background .2s}
.tf .lrow a:hover,.checkrow a:hover,.auth-alt a:hover{background:#3311cc;color:#fff}
.tf .inp{border:0;background:#121411;box-shadow:none;border-radius:14px;padding:0 16px;min-height:54px}
.tf .inp:focus-within{outline:none;background:#121411}
.tf .inp>.ic{color:#858c82}
.tf input,.tf select{font-size:16px;min-height:52px;font-weight:400;border:0!important;outline:none!important;background:transparent!important;box-shadow:none!important}
.tf input:focus,.tf select:focus,.tf input:focus-visible,.tf select:focus-visible{outline:none!important;border:0!important;box-shadow:none!important}
.tf input::placeholder{color:#858c82}
.tf .eye{min-height:44px;min-width:44px;font-size:12px;letter-spacing:0;text-transform:none;color:var(--dim);font-family:Montserrat,system-ui,sans-serif}
.tf .eye:hover{color:var(--ink)}
.tf .hint{font-size:12px;color:var(--dim);font-weight:400;margin-top:8px}
.tf .err{font-size:12px}
.tf.bad .inp{outline:none!important;border:0!important;box-shadow:none!important;background:#121411}
.tf.ok .inp{border:0!important;outline:none!important;box-shadow:none!important}
.strength{margin-top:-8px}
.strength i{height:4px;background:#1d201c}
#pwLabel{font-size:12px!important;line-height:1.5;margin:8px 0 22px!important;color:var(--dim)!important}
.checkrow{font-size:13px;font-weight:400;color:var(--dim);gap:12px;margin:4px 0 24px;line-height:1.6}
.checkrow .box{width:22px;height:22px;border-radius:7px;border:0;background:#121411;box-shadow:none}
.auth-submit{display:flex;align-items:center;justify-content:center;gap:12px;width:100%;min-height:52px;border:0;border-radius:999px;padding:14px 24px;background:var(--lime);color:#fff;font:600 14px Montserrat,system-ui,sans-serif;cursor:pointer;transition:background .2s}
.auth-submit:hover{background:#3311cc}
.auth-submit:focus-visible{outline:none}
.splitline{margin:28px 0 16px;font-size:12px;font-weight:500;letter-spacing:0;text-transform:none;color:var(--dim)}
.splitline::before,.splitline::after{background:#1d201c}
.oauth{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.oauth button{min-height:48px;padding:10px 8px;gap:8px;border:0;border-radius:999px;background:#121411;color:var(--ink);font:500 13px Montserrat,system-ui,sans-serif;box-shadow:none}
.oauth button:hover{background:#1a1d19;color:#fff;border:0}
.oauth button .ic{color:var(--dim)}
.demo-note{margin-top:24px;padding:0;border:0;background:none;font-size:12px;font-weight:400;color:var(--dim);line-height:1.7;text-align:center;overflow-wrap:anywhere}
.demo-note b{color:var(--ink);font-weight:500;font-family:Montserrat,system-ui,sans-serif}
.auth-alt{margin-top:20px;font-size:13px;color:var(--dim);line-height:1.6}
.ft-modal-title{font-family:Space Grotesk,system-ui,sans-serif;font-weight:700;font-size:24px;text-transform:none;letter-spacing:-.025em}
.ft-modal-desc{color:var(--dim);line-height:1.6}
@media (max-width:600px){
  .nav-min{min-height:68px;padding:12px 20px;padding-top:calc(12px + env(safe-area-inset-top))}
  .nav-min .logo{font-size:23px}
  .nav-min a.back{min-width:44px;justify-content:center}
  .nav-min a.back .ic{width:18px;height:18px}
  .auth-page{padding:100px 20px 40px;padding-bottom:calc(40px + env(safe-area-inset-bottom))}
  .auth-intro{text-align:left;margin-bottom:28px}
  .auth-intro h1{font-size:30px}
  .auth-intro p{font-size:13px;margin-left:0}
  .oauth button{font-size:12px;gap:6px;padding:10px 4px}
  .demo-note,.auth-alt{text-align:left}
}
"""

SIGNUP_PAGE_CSS = AUTH_PAGE_CSS

# ══════════════════════════════════════════════════════════════════
# SIGN IN
# ══════════════════════════════════════════════════════════════════
si = ['<main class="auth-page"><header class="auth-intro"><h1>Welcome back.</h1>'
      '<p>Sign in to your players, your club and your next matchday.</p></header>']
si.append('<form id="signinForm" novalidate>')
si.append(tf("Email", "email", "email", "you@example.com", "", "", "Enter a valid email address.", extra='autocomplete="email" inputmode="email" autocapitalize="none"'))
si.append(tf("Password", "password", "password", "••••••••••", "lock", "",
             "Password must be at least 8 characters.", extra='autocomplete="current-password"', link="Forgot?"))
si.append(check("remember", "Keep me signed in on this device", True))
si.append('<button class="auth-submit" type="submit">Sign in</button>')
si.append('</form>')
si.append('<div class="splitline">Or continue with</div>')
si.append(T('<div class="oauth"><button type="button" data-provider="Passkey">@@ Passkey</button>'
            '<button type="button" data-provider="Google">@@ Google</button>'
            '<button type="button" data-provider="Wallet">@@ Wallet</button></div>',
            ic("shield", "ic"), ic("crest", "ic"), ic("wallet", "ic")))
si.append('<div class="demo-note">Prototype build — accounts are real, balances are play money. '
          'No account yet? <b>Create one</b> below; if the server is out of reach, '
          'you are signed in on this device so you can still look around.</div>')
si.append('<div class="auth-alt">New to Fantrade? <a href="signup.html">Create an account</a></div>')
si.append('</main>')

SIGNIN_JS = AUTH_JS + r"""
var AFTER_SIGNIN = ['account','activity','asset','buy','club-builder','clubs',
  'dashboard','divisions','exchange','fanplay','ftr','liveboard','notifications',
  'onboarding','receive','send','settings','settings-alerts',
  'settings-club','settings-data','settings-play','settings-profile',
  'settings-security','settings-wallet','swap','trade','wallet','withdraw'];
function nextPage(){
  try{
    var raw = (new URLSearchParams(window.location.search)).get('next') || '';
    raw = raw.split('/').pop().split('?')[0].replace(/\.html$/i, '').toLowerCase();
    return AFTER_SIGNIN.indexOf(raw) === -1 ? null : raw + '.html';
  }catch(e){ return null; }
}
window.nextPage = nextPage;
if(nextPage() && window.FTDB){
  FTDB.ready().then(function(){ if(FTDB.signedIn()) window.location.replace(nextPage()); });
}
var sf = document.getElementById('signinForm');
if(sf) sf.addEventListener('submit', function(e){
  e.preventDefault();
  var em = fld('email').value, pw = fld('password').value;
  var ok = true;
  if(!validEmail(em)) ok = bad('email'); else good('email');
  if(!pw || pw.length < 8) ok = bad('password', 'Password must be at least 8 characters.'); else good('password');
  if(!ok){ showToast('Check the highlighted fields and try again.', 'error'); return; }
  var name = FT.getState().auth.email === em.trim() ? null : em.trim().split('@')[0]
      .split(/[._-]+/).map(function(w){ return w.charAt(0).toUpperCase() + w.slice(1); }).join(' ');
  var btn = sf.querySelector('.auth-submit'), label = btn ? btn.textContent : '';
  function busy(on){ if(!btn) return; btn.disabled = on; btn.textContent = on ? 'Signing in\u2026' : label; }
  function go(href){ setTimeout(function(){ window.location.href = href; }, 700); }

  /* No account server within reach \u2014 the prototype still runs from this
     browser, so the desk opens rather than the door closing. */
  function localOnly(reason){
    console.warn('[Fantrade] Signing in from this browser only:', reason);
    FT.signIn(em.trim(), name);
    showToast('Signed in on this device. Your account could not be reached, so this session is local.', 'info');
    go(nextPage() || 'dashboard.html');
  }

  busy(true);
  if(!window.FTDB){ localOnly('no database bridge on the page'); return; }
  FTDB.signIn(em.trim(), pw).then(function(){
    FT.signIn(em.trim(), name);
    return FT.syncCloud();
  }).then(function(){
    showToast('Welcome back. Loading your desk…', 'success');
    go(FT.getState().auth.onboarded ? (nextPage() || 'dashboard.html') : 'onboarding.html');
  }).catch(function(error){
    var msg = (error && error.message) || 'Sign in failed.';
    if(/reach the server|Failed to fetch|NetworkError/i.test(msg)){ localOnly(msg); return; }
    busy(false);
    bad('password', msg);
    showToast(msg, 'error');
  });
});
['email','password'].forEach(function(id){
  var el = fld(id); if(el) el.addEventListener('input', function(){ clearErr(id); });
});
"""

page("signin.html", "Sign in — Fantrade", "".join(si), SIGNIN_JS, css=AUTH_PAGE_CSS, chrome=False)

# ══════════════════════════════════════════════════════════════════
# SIGN UP
# ══════════════════════════════════════════════════════════════════
su = ['<main class="auth-page"><header class="auth-intro"><h1>Create your account.</h1>'
      '<p>One account for the exchange, your Dream Club and every FanPlay round.</p></header>']
su.append('<form id="signupForm" novalidate>')
su.append(tf("Full name", "name", "text", "Alex Morgan", "user", "", "Tell us what to call you.", extra='autocomplete="name"'))
su.append(tf("Email", "email", "email", "you@example.com", "", "", "Enter a valid email address.", extra='autocomplete="email" inputmode="email" autocapitalize="none"'))
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
su.append('<button class="auth-submit" type="submit">Create account</button>')
su.append('</form>')
su.append('<div class="splitline">Or continue with</div>')
su.append(T('<div class="oauth"><button type="button" data-provider="Passkey">@@ Passkey</button>'
            '<button type="button" data-provider="Google">@@ Google</button>'
            '<button type="button" data-provider="Wallet">@@ Wallet</button></div>',
            ic("shield", "ic"), ic("crest", "ic"), ic("wallet", "ic")))
su.append('<div class="auth-alt">Already have an account? <a href="signin.html">Sign in</a></div>')
su.append('</main>')

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
  var region = fld('country').value;
  var btn = uf.querySelector('.auth-submit'), label = btn ? btn.textContent : '';
  function busy(on){ if(!btn) return; btn.disabled = on; btn.textContent = on ? 'Creating account…' : label; }
  function go(href){ setTimeout(function(){ window.location.href = href; }, 900); }

  /* No account server within reach — the account is kept in this browser so
     the prototype can still be walked through end to end. */
  function localOnly(reason){
    console.warn('[Fantrade] Creating this account in the browser only:', reason);
    FT.signUp({ name: nm, email: em.trim(), region: region });
    showToast('Account created on this device. It could not be saved to your Fantrade account.', 'info');
    go('onboarding.html');
  }

  busy(true);
  if(!window.FTDB){ localOnly('no database bridge on the page'); return; }
  FTDB.signUp(em.trim(), p, { display_name: nm, region: region }).then(function(res){
    FT.signUp({ name: nm, email: em.trim(), region: region });
    if(res && res.needsConfirmation){
      showToast('Check your inbox to confirm ' + em.trim() + ', then sign in.', 'success');
      go('signin.html');
      return null;
    }
    return FT.syncCloud().then(function(){
      showToast('Account created. Let us get you set up.', 'success');
      go('onboarding.html');
    });
  }).catch(function(error){
    var msg = (error && error.message) || 'That account could not be created.';
    if(/reach the server|Failed to fetch|NetworkError/i.test(msg)){ localOnly(msg); return; }
    busy(false);
    bad('email', msg);
    showToast(msg, 'error');
  });
});
['name','email'].forEach(function(id){
  var el = fld(id); if(el) el.addEventListener('input', function(){ clearErr(id); });
});
"""

page("signup.html", "Create account — Fantrade", "".join(su), SIGNUP_JS, css=SIGNUP_PAGE_CSS, chrome=False)

print("built signin.html + signup.html")

# ══════════════════════════════════════════════════════════════════
# ONBOARDING — four steps from a fresh account to a fielded club
# ══════════════════════════════════════════════════════════════════
OB_CSS = """
body{background:#050505;--dim:#b9bcb7;--faint:#979c96;--ink:#f4f6f1;--lime:#1800ad}
.orb,.grain{display:none}
.nav-min{top:0;min-height:76px;padding:16px 32px;background:#050505}
.nav-min .logo{font-family:Space Grotesk,system-ui,sans-serif;font-size:25px;text-transform:lowercase;letter-spacing:-.03em}
.nav-min .brand-logo-img{width:28px;height:28px}
.nav-min a.back{min-height:44px;font-family:Montserrat,system-ui,sans-serif;letter-spacing:0;text-transform:none;font-size:12px}
.onboarding{width:min(660px,100%);margin:auto;padding:116px 24px 64px}
.ob-intro{text-align:center;margin-bottom:36px}
.ob-intro h1{font-size:clamp(28px,4.2vw,42px);font-weight:700;line-height:1.08;text-transform:none;letter-spacing:-.035em}
.ob-intro p{font-size:14px;color:var(--dim);margin:14px 0 0}
.ob-progress{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:32px}
.ob-progress p{margin:0;font-size:12px;color:var(--dim)}
.prog{gap:8px;margin:0;flex-wrap:nowrap}
.prog .st{border:0;padding:0;min-width:0;flex:none;width:8px;height:8px;border-radius:50%;background:#353735;opacity:1}
.prog .st.on{background:var(--lime);width:24px;border-radius:10px}
.prog .st.done{background:#b9bcb7}
.ob-h4{font-family:Space Grotesk,system-ui,sans-serif;font-weight:700;font-size:28px;text-transform:none;letter-spacing:-.025em;line-height:1.15;margin:0 0 10px}
.ob-p{font-size:14px;color:var(--dim);line-height:1.6;margin:0 0 28px}
.grant{display:flex;align-items:center;justify-content:space-between;gap:20px;margin:0 0 26px;padding:0;background:none;border:0;box-shadow:none}
.grant .k{font-size:12px;color:var(--dim)}
.grant .v{font-size:26px;font-weight:600;color:var(--ink);letter-spacing:-.04em;white-space:nowrap}
.grant .v span{font-size:12px;color:var(--dim);letter-spacing:0}
.picks{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-bottom:28px}
.pick{position:relative;display:flex;flex-direction:column;align-items:center;text-align:center;border:0;background:none;padding:16px 8px;border-radius:18px;box-shadow:none;transition:background .2s}
.pick:hover{background:#111310;transform:none}
.pick[aria-pressed="true"]{background:#17112f}
.pick[aria-pressed="true"]::after{content:'✓';position:absolute;right:12px;top:12px;color:#fff;background:var(--lime);width:20px;height:20px;border-radius:50%;font-size:12px}
.pick img{width:52px;height:52px;object-fit:cover;object-position:center 20%;border-radius:50%;margin-bottom:10px}
.pick .sym{font-size:14px;font-weight:600}
.pick .nm{font-size:11px;line-height:1.5}
.pick .px{font-size:13px;font-weight:500;margin-top:8px}.pick .px small{font-size:10px;color:var(--dim)}
.field{border:0;box-shadow:none;background:#121411;border-radius:14px;min-height:56px;padding:12px 16px}
.field label{text-transform:none;letter-spacing:0;font-size:13px;color:var(--dim)}
.field input{font-size:16px;min-height:32px;width:45%;border:0!important;outline:none!important;background:transparent!important;color:var(--ink)!important;box-shadow:none!important;-webkit-appearance:none;text-align:right}
.field:focus-within,.tf .inp:focus-within{outline:none!important;border:0!important;box-shadow:none!important}
.quick{gap:8px;margin:12px 0 24px}
.quick button{border:0;background:#121411;min-height:44px;font-size:12px}
.line{border:0;padding:5px 0;font-size:13px}.line b{color:var(--ink);font-weight:500}
.order-total{font-size:16px;margin-top:8px}
.ob-primary{display:flex;align-items:center;justify-content:center;gap:12px;width:100%;min-height:52px;border:0;border-radius:999px;padding:14px 24px;background:var(--lime);color:#fff;font:600 14px Montserrat,system-ui,sans-serif;cursor:pointer}
.ob-primary:hover{background:#3311cc}.ob-primary:disabled{opacity:.6;cursor:wait}
#obBuy{margin-top:24px}
.wiz-foot{margin-top:28px;display:flex;flex-wrap:nowrap;gap:16px}
.ob-back{border:0;background:none;color:var(--dim);padding:12px 8px;min-height:48px;font:500 13px Montserrat,system-ui,sans-serif;cursor:pointer}
.tf{margin-bottom:24px}.tf label,.k-label{font-size:13px;text-transform:none;letter-spacing:0;color:var(--dim);font-weight:500}
.tf .inp{border:0;background:#121411;box-shadow:none;border-radius:14px;padding:12px 16px;min-height:54px}
.tf input,.tf select{font-size:16px;min-height:28px}.tf input::placeholder{color:#858c82}
.tf-row{gap:16px}.tf .err{font-size:12px}.tf.bad .inp{outline:none!important;border:0!important;box-shadow:none!important}.tf.ok .inp{outline:none!important;border:0!important;box-shadow:none!important}
.forms{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:12px 0 28px}
.forms button{border:0;border-radius:12px;min-height:48px;background:#121411;color:var(--dim);font:500 14px Montserrat,system-ui,sans-serif;cursor:pointer}
.forms button[aria-pressed="true"]{background:var(--lime);color:#fff}
.swatches{display:flex;gap:12px;margin-top:12px}.sw{width:44px;height:44px;border:0;border-radius:50%;cursor:pointer}
.sw[aria-pressed="true"]{outline:2px solid #fff;outline-offset:4px}
.ob-summary{margin:24px 0 28px;display:grid;grid-template-columns:1fr 1fr;gap:24px}
.ob-summary div{min-width:0}.ob-summary dt{font-size:12px;color:var(--dim);margin-bottom:6px}.ob-summary dd{margin:0;font-size:15px;overflow-wrap:anywhere}.ob-summary .formation{display:block;white-space:nowrap;font-size:12px;color:var(--dim);margin-top:4px}
.ob-next-note{font-size:13px;color:var(--dim);line-height:1.7;margin:24px 0 0}
.ob-success{width:56px;height:56px;border-radius:50%;display:grid;place-items:center;background:var(--lime);color:white;margin-bottom:24px}.ob-success .ic{width:26px;height:26px}
@media(max-width:600px){
 .nav-min{min-height:68px;padding:12px 20px}.nav-min .logo{font-size:23px}.nav-min a.back{min-width:44px;justify-content:center}
 .onboarding{padding:100px 20px 40px;padding-bottom:calc(40px + env(safe-area-inset-bottom))}
 .ob-intro{text-align:left;margin-bottom:28px}.ob-intro h1{font-size:30px}.ob-intro p{font-size:13px;max-width:30ch}
 .ob-progress{margin-bottom:28px}.ob-h4{font-size:25px}.ob-p{font-size:13px;margin-bottom:24px}
 .picks{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}.pick{padding:12px 6px}.pick img{width:44px;height:44px}
 .grant{gap:12px}.grant .v{font-size:24px}.grant .k{max-width:110px;line-height:1.5}
 .forms{grid-template-columns:repeat(2,1fr)}.tf-row{grid-template-columns:1fr;gap:0}
}
"""

STARTERS = [("FSAKA", "Bukayo Saka", "Arsenal · Forward", 48.20, False),
            ("FBRN", "Bruno Fernandes", "Man United · Midfielder", 39.75, False),
            ("FHLND", "Erling Haaland", "Man City · Forward", 71.40, False),
            ("FSALI", "William Saliba", "Arsenal · Defender", 33.80, False),
            ("FMUS", "Jamal Musiala", "Bayern · Midfielder", 46.70, False),
            ("FARTA", "Mikel Arteta", "Arsenal · Coach", 22.05, True)]
STEPS = [("01", "Your first shares"), ("02", "Your profile"), ("03", "Your club"), ("04", "Ready to play")]
ob = ['<main class="onboarding"><header class="ob-intro"><h1>Make the game yours.</h1>'
      '<p>A few quick steps to your first shares and your own Dream Club.</p></header>'
      '<div class="ob-progress"><p id="obCount" aria-live="polite">Step 1 of 4 · Your first shares</p>'
      '<div class="prog" id="obProg" aria-hidden="true">']
for i, (n, label) in enumerate(STEPS):
    ob.append('<span class="st%s" data-step="%s"></span>' % (' on' if i == 0 else '', i))
ob.append('</div></div><div class="step-pane on" data-pane="0">'
          '<h2 class="ob-h4" tabindex="-1">Start with a player you believe in.</h2>'
          '<p class="ob-p">Choose your first shares using your demo balance. You can explore more players after setup.</p>'
          '<div class="grant"><div class="k">Your demo balance</div><div class="v"><b id="obBalance">50,000</b> <span>$FTR</span></div></div>'
          '<div class="picks" id="obPicks" role="group" aria-label="Choose your first player">')
STARTER_IMG_MAP = {
    'FSAKA': 'saka', 'FBRN': 'bruno', 'FHLND': 'haaland',
    'FSALI': 'saliba', 'FMUS': 'musiala', 'FARTA': 'arteta',
    'FAITN': 'bonmati', 'FPUTL': 'putellas', 'FKERR': 'kerr',
    'FRUSS': 'russo', 'FLJMS': 'james', 'FWILM': 'williamson',
    'FEARP': 'earps', 'FWIEG': 'wiegman'
}
for sym, nm, role, px, coach in STARTERS:
    img_slug = STARTER_IMG_MAP.get(sym, sym[1:].lower())
    ob.append(f'<button class="pick" type="button" data-sym="{sym}" data-nm="{nm}" data-px="{px}" data-coach="{int(coach)}" aria-pressed="false">'
              f'<img src="assets/players/{img_slug}.webp" alt="" width="52" height="52">'
              f'<span class="sym">{nm}</span><span class="nm">{role}</span><span class="px">{px:.2f} <small>$FTR / share</small></span></button>')
ob.append('</div><div class="field"><label for="obShares">Shares to buy</label><input id="obShares" value="500" inputmode="numeric"></div>'
          '<div class="quick"><button type="button" data-s="100">100</button><button type="button" data-s="250">250</button>'
          '<button type="button" data-s="500">500</button><button type="button" data-s="1000">1,000</button></div>'
          '<div class="line"><span>Shares</span><b id="obSub">—</b></div>'
          '<div class="line"><span>Fee (0.4%)</span><b id="obFee">—</b></div>'
          '<div class="line order-total"><span>Total</span><b id="obTot">—</b></div>'
          '<button type="button" class="ob-primary" id="obBuy">Buy shares &amp; continue</button></div>')
ob.append('<div class="step-pane" data-pane="1"><h2 class="ob-h4" tabindex="-1">What should we call you?</h2>'
          '<p class="ob-p">Your manager handle appears beside your club on the leaderboard.</p>')
ob.append(tf('Manager handle','handle','text','@your_name','user','', 'Use 3–20 letters, numbers or underscores.', extra='autocomplete="nickname" autocapitalize="none"'))
ob.append('<div class="tf-row">'+sel('Region','region',COUNTRIES,'flag')+sel('Home league','league',["*Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Nigeria Premier Football League", "Eredivisie", "Primeira Liga"],'stadium')+'</div>'
          '<p class="ob-next-note">We’ll use your home league to show the fixtures that matter to you first.</p></div>')
ob.append('<div class="step-pane" data-pane="2"><h2 class="ob-h4" tabindex="-1">Give your club an identity.</h2>'
          '<p class="ob-p">Pick a name, formation and colour. You can refine your squad after setup.</p>')
ob.append(tf('Club name','clubName','text','Your Dream Club','crest','','Choose a name between 2 and 24 characters.',extra='maxlength="24"'))
ob.append('<div class="k-label" id="formationLabel">Starting formation</div><div class="forms" id="obForms" role="group" aria-labelledby="formationLabel">')
for form in ['4-3-3','4-4-2','3-5-2','4-2-3-1']:
    ob.append(f'<button type="button" aria-pressed="{str(form == "4-3-3").lower()}">{form}</button>')
ob.append('</div><div class="k-label" id="colourLabel">Club colour</div><div class="swatches" id="obSw" role="group" aria-labelledby="colourLabel">')
for color,name in [('#1800ad','Indigo'),('#FF6A1F','Amber'),('#4DA6FF','Azure'),('#FF5E8A','Rose'),('#F4F6F1','Chalk')]:
    ob.append(f'<button class="sw" type="button" aria-pressed="{str(name == "Indigo").lower()}" data-c="{color}" data-n="{name}" style="background:{color}" aria-label="{name}"></button>')
ob.append('</div></div><div class="step-pane" data-pane="3"><div class="ob-success">'+ic('check','ic')+'</div>'
          '<h2 class="ob-h4" tabindex="-1">Your club starts here.</h2><p class="ob-p">Your first shares are in place. Here’s your setup.</p>'
          '<dl class="ob-summary"><div><dt>Manager</dt><dd data-bind="name">Alex Morgan</dd></div>'
          '<div><dt>Handle</dt><dd id="sumHandle">—</dd></div><div><dt>Region</dt><dd id="sumRegion">—</dd></div>'
          '<div><dt>Available balance</dt><dd id="sumWallet">—</dd></div><div><dt>First shares</dt><dd id="sumAsset">—</dd></div>'
          '<div><dt>Club &amp; formation</dt><dd><span id="sumClub">—</span><span class="formation" id="sumFormation">4-3-3</span></dd></div></dl>'
          '<p class="ob-next-note">Next, fill your lineup from the players you own and explore FanPlay. Your dashboard will guide you through it.</p></div>'
          '<div class="wiz-foot"><button class="ob-back" id="obBack" type="button" hidden>Back</button>'
          '<button class="ob-primary" id="obNext" type="button" hidden>Continue</button></div></main>')

OB_JS = r"""
// The back link became a pill button; missing it used to throw here and stop
// the rest of onboarding from ever running.
var backBtn = document.querySelector('.nav-min .back-btn, .nav-min .back');
if(backBtn) backBtn.setAttribute('aria-label', 'Back to Fantrade');
var step = 0, PANES = document.querySelectorAll('.step-pane'), STEPS_N = PANES.length;
var picked = null;
function el(id){ return document.getElementById(id); }
function wrap(id){ return document.getElementById('f-' + id); }
function num(v){ return parseInt(String(v).replace(/[^0-9]/g, ''), 10) || 0; }

// Ensure 50,000 $FTR grant is present
(function(){
  var s = FT.getState();
  if(s.wallet.balance < 50000){
    FT.depositFtr(50000);
  }
})();

function render(){
  PANES.forEach(function(p, i){ p.classList.toggle('on', i === step); });
  document.querySelectorAll('#obProg .st').forEach(function(s, i){
    s.classList.toggle('on', i === step);
    s.classList.toggle('done', i < step);
  });
  el('obBack').disabled = step === 0;
  el('obBack').style.opacity = step === 0 ? '.4' : '1';
  el('obCount').textContent = 'Step ' + (step + 1) + ' of ' + STEPS_N + ' · ' + ['Your first shares','Your profile','Your club','Ready to play'][step];
  el('obBack').hidden = step === 0;
  el('obNext').hidden = step === 0;
  el('obNext').childNodes[0].nodeValue = step === STEPS_N - 1 ? 'Go to my dashboard' : 'Continue';
  window.scrollTo({ top: 0, behavior: reduce ? 'instant' : 'smooth' });
  if(step > 0) PANES[step].querySelector('.ob-h4').focus({preventScroll:true});
}
function sum(){
  var s = FT.getState();
  el('sumHandle').textContent = el('handle').value.trim() || '—';
  el('sumRegion').textContent = el('region').value;
  el('sumWallet').textContent = s.wallet.balance.toLocaleString('en-US') + ' $FTR';
  el('obBalance').textContent = s.wallet.balance.toLocaleString('en-US');
  el('sumAsset').textContent = picked ? picked.sym : '—';
  el('sumClub').textContent = el('clubName').value.trim() || '—';
  el('sumFormation').textContent = formation;
}

// step 1 — first asset
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
  if(!picked){
    var firstPick = document.querySelector('#obPicks .pick');
    if(firstPick) firstPick.click();
  }
  var sh = num(el('obShares').value);
  if(sh < 1){ showToast('Enter how many shares you want.', 'error'); return; }
  el('obBuy').disabled = true;
  try {
    var r = FT.executeTrade('buy', picked.sym, picked.nm, sh, picked.px, picked.coach);
    showToast('🎉 ' + sh.toLocaleString('en-US') + ' ' + picked.sym + ' shares purchased! You are officially an owner.', 'success');
    sum();
    setTimeout(function(){
      if(step === 0){ step = 1; render(); sum(); }
      el('obBuy').disabled = false;
    }, 600);
  } catch(err){ el('obBuy').disabled = false; showToast(err.message, 'error'); }
});

// step 2 — manager profile
el('handle').addEventListener('input', sum);
el('region').addEventListener('change', sum);

// step 3 — club identity
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
    if(!picked || !FT.getState().holdings[picked.sym]){
      showToast('Select a player and click "Buy Shares" to start your portfolio.', 'error');
      return false;
    }
    return true;
  }
  if(step === 1){
    var h = el('handle').value.trim().replace(/^@/, '');
    if(!/^[A-Za-z0-9_]{3,20}$/.test(h)){ wrap('handle').classList.add('bad'); return false; }
    wrap('handle').classList.remove('bad');
    return true;
  }
  if(step === 2){
    var cn = el('clubName').value.trim();
    if(cn.length < 2 || cn.length > 24){ wrap('clubName').classList.add('bad'); return false; }
    wrap('clubName').classList.remove('bad');
    return true;
  }
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
render(); sum(); var firstP = document.querySelector("#obPicks .pick"); if(firstP) firstP.click();
"""

page("onboarding.html", "Onboarding — Fantrade", "".join(ob), OB_JS, OB_CSS, chrome=False)
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
.kc-home-search-box:focus-within{border-color:transparent;background:rgba(255,255,255,.08);outline:none}
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
/* Launch & Claim — built from the same parts as the scrolling home cards
   (24px radius, 26px padding, a light source top-right, no border line), but
   filled with the brand blue so it reads as the one thing on the page that
   asks you to act. */
.home-claim-card{margin-top:20px;padding:26px;border-radius:24px;border:0;color:#fff;
  background:radial-gradient(120% 78% at 100% 0%,rgba(255,255,255,.18),transparent 58%),var(--lime);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.16),0 20px 44px rgba(24,0,173,.34);
  display:grid;grid-template-columns:minmax(0,1fr);gap:18px;min-height:388px;align-content:start}
.home-claim-head{display:grid;gap:10px}
.home-claim-top{display:flex;align-items:center;gap:10px}
/* The mark sits straight on the blue with nothing behind it, in white:
   brightness(0) takes the logo to solid black, invert(1) turns that white. */
.home-claim-mark{width:34px;height:34px;object-fit:contain;flex-shrink:0;filter:brightness(0) invert(1)}
.home-claim-eyebrow{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;
  color:rgba(255,255,255,.72)}
.home-claim-card h2{font-size:25px!important;margin:0 0 8px;color:#fff;letter-spacing:-.022em}
.home-claim-card p{margin:0;color:rgba(255,255,255,.76);font-size:13.5px;line-height:1.65}
.home-claim-search{display:flex;align-items:center;gap:10px;margin:0;padding:6px 6px 6px 16px;
  border-radius:999px;background:rgba(0,0,0,.26);transition:box-shadow .15s ease}
.home-claim-search:focus-within{box-shadow:0 0 0 2px rgba(255,255,255,.6)}
.home-claim-search .ic{width:18px;height:18px;flex-shrink:0;color:rgba(255,255,255,.72)}
.home-claim-search input{flex:1;min-width:0;height:40px;border:0;outline:0;background:transparent;
  color:#fff;font:inherit;font-size:14px;padding:0}
.home-claim-search input::placeholder{color:rgba(255,255,255,.62)}
.home-claim-search input::-webkit-search-cancel-button{-webkit-appearance:none;appearance:none;display:none}
.home-claim-search button{flex-shrink:0;min-height:40px;padding:0 18px;border:0;border-radius:999px;
  background:#fff;color:var(--lime);font:inherit;font-size:13px;font-weight:700;cursor:pointer}
/* Results only change when the manager searches, so the card never grows or
   shrinks on its own while the page loads. */
.home-claim-results{display:grid;gap:10px;align-content:start}
.home-claim-hint p{margin:0 0 12px;font-size:12.5px;color:rgba(255,255,255,.72)}
.home-claim-chips{display:flex;flex-wrap:wrap;gap:8px}
.home-claim-chips button{border:0;border-radius:999px;padding:9px 14px;background:rgba(0,0,0,.26);
  color:#fff;font:inherit;font-size:12.5px;font-weight:600;cursor:pointer;transition:background .15s ease}
.home-claim-chips button:hover{background:rgba(0,0,0,.42)}
.home-claim-empty{display:grid;gap:6px;padding:16px 18px;border-radius:16px;background:rgba(0,0,0,.26)}
.home-claim-empty b{font-family:Space Grotesk,sans-serif;font-size:14.5px;letter-spacing:-.01em}
.home-claim-empty span{font-size:12.5px;line-height:1.6;color:rgba(255,255,255,.72)}
/* The rows sit in a well rather than behind a border, the way the stats block
   does on the scrolling cards. */
.home-claim-row{display:grid;grid-template-columns:44px minmax(0,1fr) auto;align-items:center;gap:13px;
  padding:12px 14px;border:0;border-radius:16px;background:rgba(0,0,0,.26);color:#fff;text-decoration:none;
  text-align:left;width:100%;box-sizing:border-box;font:inherit;cursor:pointer;transition:background .2s ease,transform .2s ease}
.home-claim-who{min-width:0}
.home-claim-row:hover{background:rgba(0,0,0,.4);transform:translateY(-1px)}
.home-claim-row .player-photo{width:44px;height:44px;border-radius:50%;object-fit:cover;
  object-position:50% 18%;background:rgba(0,0,0,.4);border:0}
.home-claim-row b{display:block;font-family:Space Grotesk,sans-serif;font-weight:700;font-size:14.5px;
  letter-spacing:-.015em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.home-claim-row small{display:flex;align-items:center;gap:7px;margin-top:4px;
  color:rgba(255,255,255,.66);font-size:11.5px;line-height:1.3;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
/* The F-ticker is a market symbol, so it gets a symbol's treatment. */
.home-claim-row small i{font-style:normal;font-family:Space Grotesk,sans-serif;font-weight:700;
  font-size:10.5px;letter-spacing:.04em;color:#fff;background:rgba(255,255,255,.16);
  border-radius:6px;padding:2px 6px;flex-shrink:0}
/* The money line: dollars first, because that is the figure people know. */
.home-claim-val{display:block;margin-top:5px;font-size:11.5px;line-height:1.45;color:rgba(255,255,255,.74)}
.home-claim-val strong{color:#fff;font-weight:700}
/* White on blue: the pill has to out-contrast the card it sits on. */
.home-claim-action{display:grid;place-items:center;min-height:36px;min-width:64px;box-sizing:border-box;
  padding:7px 15px;border-radius:999px;background:#fff;color:var(--lime);font-size:12px;
  font-weight:700;letter-spacing:.01em;white-space:nowrap}
.home-claim-row.is-listed .home-claim-action{background:rgba(255,255,255,.16);color:#fff}
@media(max-width:600px){
  .home-claim-card{padding:22px}
  .home-claim-row{gap:11px;padding:11px 12px}
  .home-claim-action{min-height:34px;min-width:0;padding:8px 13px}
  .home-claim-search button{padding:0 14px}
}
/* Scrolling cards */
.home-card-soon{display:inline-flex;align-items:center;margin:0 0 16px;padding:6px 12px;border-radius:999px;
  background:rgba(255,106,31,.14);color:var(--amber);font-size:11px;font-weight:700;letter-spacing:.07em;
  text-transform:uppercase}
body.app.calm .home-card-stats dd{overflow-wrap:anywhere}
body.app.calm .home-card .app-primary[aria-pressed="true"]{background:rgba(255,255,255,.1)}

/* The claim sheet is built exactly like "Switch player" on a player's page:
   a native dialog on the same surface, radius, padding, heading and round
   close button, with the same raised fill for everything inside it. */
body.claim-open{overflow:hidden}
.claim-modal-dialog{position:fixed;inset:0;box-sizing:border-box;width:min(560px,calc(100% - 32px));
  max-height:min(720px,calc(100dvh - 48px));margin:auto;border:0;border-radius:28px;padding:28px;
  background:#121411;color:var(--ink);box-shadow:0 24px 80px #0008;overflow-y:auto;overscroll-behavior:contain;
  scrollbar-width:none}
.claim-modal-dialog::-webkit-scrollbar{display:none}
.claim-modal-dialog::backdrop{background:#000b;backdrop-filter:blur(6px)}
.claim-modal-dialog[open]{animation:kcPop .22s cubic-bezier(.16,1,.3,1)}
@keyframes kcPop{from{opacity:0;transform:scale(.97) translateY(8px)}to{opacity:1;transform:none}}
.claim-picker-heading{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:24px}
.claim-picker-heading h2{font-size:25px;margin:0}
.claim-picker-heading button{display:grid;place-items:center;border:0;background:#242821;color:#fff;
  border-radius:50%;width:44px;height:44px;flex:none;cursor:pointer}
.claim-picker-heading .ic{width:18px;height:18px}
/* The player sits in a row like the picker's chosen result. */
.claim-modal-head{display:flex;align-items:center;gap:14px;padding:14px;border-radius:14px;background:#242821;margin-bottom:12px}
.claim-modal-head .player-photo{width:44px;height:44px;border-radius:50%;object-fit:cover;object-position:50% 18%;flex:none;border:0}
.claim-modal-head > div:last-child{min-width:0}
.claim-modal-title{margin:0;font-family:Montserrat,sans-serif;font-weight:600;font-size:14px;letter-spacing:0;overflow-wrap:anywhere}
.claim-modal-sub{font-size:11px;color:var(--dim);margin-top:4px;overflow-wrap:anywhere}
.claim-modal-sub b{color:#fff;font-weight:600}
.claim-about{margin:0 0 22px;padding:0 4px;font-size:12.5px;line-height:1.65;color:var(--dim)}
.claim-about[hidden]{display:none}
.claim-modal-dialog .claim-step:first-of-type{margin-top:22px}
.claim-section-lbl{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;
  color:var(--faint);margin:0 0 10px}
.claim-step{margin-bottom:18px}

/* Allocation: the choice is what share of 10,000,000 you take, so each option
   shows that share rather than making you read it off a number. */
.claim-opt-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.claim-opt-btn{position:relative;border:0;border-radius:18px;padding:14px 13px 13px;
  background:#242821;color:#fff;text-align:left;cursor:pointer;font:inherit;
  display:grid;gap:7px;align-content:start;transition:background .18s ease,transform .18s ease}
.claim-opt-btn:hover:not(.on){background:#2d3229;transform:translateY(-1px)}
.claim-opt-btn.on{background:var(--lime);box-shadow:0 10px 26px rgba(24,0,173,.42)}
.claim-opt-lvl{display:flex;align-items:baseline;gap:7px}
.claim-opt-lvl b{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:14px;letter-spacing:-.01em}
.claim-opt-pct{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:26px;line-height:1;
  letter-spacing:-.035em}
.claim-opt-btn small{display:block;font-size:11px;color:rgba(255,255,255,.62);line-height:1.45}
.claim-opt-btn.on small{color:rgba(255,255,255,.82)}
.claim-opt-fee{font-size:11.5px;font-weight:600;color:var(--dim)}
.claim-opt-btn.on .claim-opt-fee{color:#fff}

/* Where the 10,000,000 goes. One bar beats three numbers. */
.claim-split{margin-top:10px;padding:14px 16px;border-radius:14px;background:#242821}
.claim-split-bar{display:flex;height:10px;border-radius:999px;overflow:hidden;gap:2px;margin-bottom:12px}
.claim-split-bar i{display:block;transition:flex-basis .25s ease}
.claim-split-bar i.cs-ft{background:#a596ed}
.claim-split-bar i.cs-you{background:var(--lime);box-shadow:inset 0 0 0 1px rgba(255,255,255,.22)}
.claim-split-bar i.cs-mkt{background:rgba(255,255,255,.14)}
.claim-split-keys{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.claim-split-key{display:grid;gap:3px}
.claim-split-key span{display:flex;align-items:center;gap:6px;font-size:10.5px;color:var(--faint);
  text-transform:uppercase;letter-spacing:.05em}
.claim-split-key span::before{content:'';width:8px;height:8px;border-radius:3px;flex-shrink:0}
.claim-split-key.cs-ft span::before{background:#a596ed}
.claim-split-key.cs-you span::before{background:var(--lime);box-shadow:inset 0 0 0 1px rgba(255,255,255,.3)}
.claim-split-key.cs-mkt span::before{background:rgba(255,255,255,.2)}
.claim-split-key b{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:12.5px;
  color:#fff;letter-spacing:-.01em;white-space:nowrap}

/* Vesting */
.claim-vest-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.claim-vest-btn{border:0;border-radius:14px;padding:13px 8px;background:#242821;
  color:#fff;text-align:center;cursor:pointer;font:inherit;transition:background .18s ease,transform .18s ease}
.claim-vest-btn:hover:not(.on){background:#2d3229;transform:translateY(-1px)}
.claim-vest-btn.on{background:var(--lime);box-shadow:0 8px 20px rgba(24,0,173,.38)}
.claim-vest-btn b{display:block;font-family:Space Grotesk,sans-serif;font-weight:700;font-size:14px;
  letter-spacing:-.01em}
.claim-vest-btn small{display:block;font-size:10.5px;color:rgba(255,255,255,.58);margin-top:3px}
.claim-vest-btn.on small{color:rgba(255,255,255,.8)}

/* The terms, as three readable facts rather than a paragraph of bold text. */
.claim-terms{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px}
.claim-term{background:#242821;border-radius:14px;padding:12px 11px;display:grid;gap:3px}
.claim-term dt{font-size:10.5px;color:var(--faint);text-transform:uppercase;letter-spacing:.05em}
.claim-term dd{margin:0;font-family:Space Grotesk,sans-serif;font-weight:700;font-size:14px;
  color:#fff;letter-spacing:-.01em}
.claim-term dd small{display:block;font-family:Montserrat,sans-serif;font-weight:400;font-size:10.5px;
  color:var(--dim);margin-top:2px;letter-spacing:0}

/* What you pay */
.claim-fee-breakdown{margin-top:10px;background:#242821;border:0;border-radius:14px;
  padding:16px 18px;display:grid;gap:9px;font-size:12.5px}
.claim-fee-row{display:flex;justify-content:space-between;align-items:baseline;gap:12px;color:var(--dim)}
.claim-fee-row b{color:#fff;font-weight:600}
.claim-fee-row.burn span:last-child{color:#a596ed}
.claim-fee-row.total{margin-top:3px;padding-top:11px;border-top:1px solid rgba(255,255,255,.09);
  color:#fff;font-size:13px}
.claim-fee-row.total span:last-child{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:19px;
  letter-spacing:-.02em}
.claim-opt-fee i{display:block;font-style:normal;font-weight:500;font-size:10.5px;opacity:.72;margin-top:2px}
.claim-fee-row b small,.claim-fee-row span small{font-size:11px;color:var(--faint);font-weight:500}
.claim-fee-row.usd{justify-content:flex-end;margin-top:-5px;font-size:12px;color:var(--dim)}
.claim-fee-row.bal{margin-top:2px}
.claim-short{margin:14px 0 0;padding:12px 14px;border-radius:14px;background:rgba(255,106,31,.12);
  color:#ffc7a6;font-size:12.5px;line-height:1.55}
.claim-short[hidden]{display:none}
.claim-short b{color:#fff}
.claim-short a{color:#fff;font-weight:700;margin-left:4px}
.claim-submit-btn{margin-top:18px;width:100%;min-height:50px;border-radius:999px;background:var(--lime);
  border:0;color:#fff;font-family:Space Grotesk,sans-serif;font-weight:700;font-size:14.5px;
  letter-spacing:-.01em;cursor:pointer;display:grid;place-items:center;
  transition:transform .18s ease,filter .18s ease;box-shadow:0 12px 28px rgba(24,0,173,.44)}
.claim-submit-btn:hover:not([disabled]){transform:translateY(-1px);filter:brightness(1.12)}
.claim-submit-btn[disabled]{opacity:.45;cursor:not-allowed;box-shadow:none}
@media(max-width:420px){
  .claim-modal-dialog{padding:20px 16px}
  .claim-picker-heading h2{font-size:22px}
  .claim-opt-btn{padding:13px 11px 12px}
  .claim-opt-pct{font-size:23px}
  .claim-opt-btn small{font-size:10.5px}
  .claim-opt-fee{font-size:11px}
  .claim-split-key span{font-size:9.5px}
  .claim-term{padding:11px 9px}
  .claim-term dt{font-size:9.5px}
  .claim-term dd{font-size:13px}
}

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
.kc-hot-ticker{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:13px;color:var(--ink)}
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
.kc-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);display:grid;place-items:center;flex:none;color:var(--lime);font-family:Space Grotesk,sans-serif;font-size:11px;font-weight:800;overflow:hidden}
.kc-avatar .player-photo{width:100%;height:100%;object-fit:cover;object-position:50% 18%;display:block}
.kc-avatar.coach{color:var(--amber);border-color:rgba(255,106,31,.25);background:rgba(255,106,31,.08)}
.kc-pair-title{display:flex;align-items:center;gap:5px;font-family:Space Grotesk,sans-serif;font-weight:700;font-size:14px;line-height:1.1;color:var(--ink)}
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
.kc-ref-title{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:15px;color:var(--ink);margin-bottom:4px}
.kc-ref-sub{font-size:12px;color:#767c82}
.kc-ref-icon-box{width:52px;height:52px;flex-shrink:0;border-radius:14px;overflow:hidden;background:rgba(255,255,255,.05);display:grid;place-items:center}
"""

# Launch & Claim: the search and its starting suggestions are written into the
# page, so the card is its full size from first paint and never reflows.
CLAIM_SUGGEST = ['Lionel Messi', 'Khadija Shaw', 'Victor Osimhen', 'Rasheedat Ajibade', 'Bukayo Saka']
CLAIM_SEARCH_HTML = (
    '<form class="home-claim-search" id="homeClaimForm" role="search" autocomplete="off">' + ic('search', 'ic')
    + '<input type="search" id="homeClaimInput" placeholder="Search any footballer" '
      'aria-label="Search footballers" autocomplete="off"><button type="submit">Search</button></form>'
    + '<div class="home-claim-results" id="homeClaimResults" aria-live="polite">'
    + '<div class="home-claim-hint"><p>Try one of these, or any name you like.</p><div class="home-claim-chips">'
    + ''.join('<button type="button" data-q="%s">%s</button>' % (n, n) for n in CLAIM_SUGGEST)
    + '</div></div></div>')

da = ['<main><div class="kc-home-wrap home-layout">', tab_intro('Home'),
      '<section class="kc-home-bal-card" aria-label="Total value"><div class="kc-bal-header">Total value'
      '<button type="button" class="kc-eye-btn" id="balEyeBtn" aria-label="Toggle balance visibility">'+'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="fill:none"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>'+'</button></div>'
      '<div class="kc-bal-val"><span id="homeBalVal" data-bind="net">—</span> <small>$FTR</small></div>'
      '<div class="kc-bal-sub" id="homeBalSub">—</div>',
      '<div class="home-claim-card" aria-labelledby="homeClaimTitle"><div class="home-claim-head">'
      '<div class="home-claim-top">'
      '<img class="home-claim-mark" src="assets/fantrade-logo.png" alt="" width="34" height="34">'
      '<span class="home-claim-eyebrow">Open to claim</span></div>'
        '<div><h2 id="homeClaimTitle">Launch &amp; Claim Activity Shares</h2>'
        '<p>Search any footballer. If they already trade, see what a share costs. If nobody has claimed '
        'them yet, take 5% or 10% of their shares and launch them on the Exchange.</p></div></div>',
      CLAIM_SEARCH_HTML + '</div>'
      '<dialog class="claim-modal-dialog" id="claimModalBackdrop" aria-labelledby="claimPickerTitle">'
      '<div class="claim-picker-heading"><h2 id="claimPickerTitle">Claim this player.</h2>'
      '<button type="button" id="claimModalClose" aria-label="Close">' + ic('cross', 'ic') + '</button></div>'
      '<div class="claim-modal-head"><div id="claimModalPhoto"></div><div><h3 class="claim-modal-title" id="claimModalTitle"></h3>'
      '<div class="claim-modal-sub" id="claimModalSub"></div></div></div>'
      '<p class="claim-about" id="claimAbout" hidden></p>'
      '<div class="claim-step"><div class="claim-section-lbl">1 &middot; Your allocation</div>'
      '<div class="claim-opt-grid">'
      '<button type="button" class="claim-opt-btn on" data-level="1">'
      '<span class="claim-opt-lvl"><b>Level 1</b></span>'
      '<span class="claim-opt-pct">5%</span>'
      '<small>500,000 shares</small>'
      '<span class="claim-opt-fee" id="claimOpt1Fee">&mdash;</span></button>'
      '<button type="button" class="claim-opt-btn" data-level="2">'
      '<span class="claim-opt-lvl"><b>Level 2</b></span>'
      '<span class="claim-opt-pct">10%</span>'
      '<small>1,000,000 shares</small>'
      '<span class="claim-opt-fee" id="claimOpt2Fee">&mdash;</span></button>'
      '</div>'
      '<div class="claim-split"><div class="claim-split-bar" aria-hidden="true">'
      '<i class="cs-ft" style="flex-basis:10%"></i><i class="cs-you" id="claimSplitYou" style="flex-basis:5%"></i>'
      '<i class="cs-mkt" id="claimSplitMkt" style="flex-basis:85%"></i></div>'
      '<div class="claim-split-keys">'
      '<div class="claim-split-key cs-ft"><span>Fantrade</span><b>1,000,000</b></div>'
      '<div class="claim-split-key cs-you"><span>You</span><b id="claimSplitYouTxt">500,000</b></div>'
      '<div class="claim-split-key cs-mkt"><span>Market</span><b id="claimSplitMktTxt">8,500,000</b></div>'
      '</div></div></div>'
      '<div class="claim-step"><div class="claim-section-lbl">2 &middot; Vesting period</div>'
      '<div class="claim-vest-grid">'
      '<button type="button" class="claim-vest-btn on" data-years="1"><b>1 year</b><small>12 months</small></button>'
      '<button type="button" class="claim-vest-btn" data-years="2"><b>2 years</b><small>24 months</small></button>'
      '<button type="button" class="claim-vest-btn" data-years="3"><b>3 years</b><small>36 months</small></button>'
      '</div>'
      '<dl class="claim-terms">'
      '<div class="claim-term"><dt>Fee share</dt><dd>30%<small>of trading fees</small></dd></div>'
      '<div class="claim-term"><dt>Daily limit</dt><dd><span id="claimDailyLimitTxt">5,000</span><small>shares a day</small></dd></div>'
      '<div class="claim-term"><dt>Lister FP</dt><dd><span id="claimFpTxt">+5,000</span><small>pre-airdrop</small></dd></div>'
      '</dl></div>'
      '<div class="claim-section-lbl">3 &middot; What you pay</div>'
      '<div class="claim-fee-breakdown">'
      '<div class="claim-fee-row"><span>Reference price</span><b id="claimPriceTxt">&mdash;</b></div>'
      '<div class="claim-fee-row"><span>Shares you take</span><b id="claimSharesTxt">500,000</b></div>'
      '<div class="claim-fee-row burn"><span>Of which burned (2%)</span><span id="claimBurnTxt">&mdash;</span></div>'
      '<div class="claim-fee-row total"><span>You pay</span><span id="claimTotalTxt">&mdash;</span></div>'
      '<div class="claim-fee-row usd"><span id="claimUsdTxt"></span></div>'
      '<div class="claim-fee-row bal"><span>Your balance</span><b id="claimBalTxt">&mdash;</b></div>'
      '</div>'
      '<p class="claim-short" id="claimShort" hidden>You need <b id="claimShortAmt"></b> more to claim at this level.'
      '<a href="buy.html">Add funds</a></p>'
      '<button type="button" class="claim-submit-btn" id="claimSubmitBtn">Pay &amp; launch</button>'
      '</dialog></section>']
HOME_CARDS = [
    # (badge html, title, copy, stats [(label, value html)], cta label, href or "action:<name>", icon)
    ("", "Follow every fixture live.",
     "Scores, your players' involvement and FP as it lands, across every league you play in.",
     [("Leagues", "4"), ("Fixtures today", "9")],
     "Open live board", "liveboard.html", "arrow"),
    ("", "Bring your mates. Share their fees.",
     "Send friends your invite link. When they trade and play, you earn 35% of the trading fees they pay, for as long as they stay.",
     [("Your invite code", '<span data-home="reflink">&mdash;</span>'), ("Your share", "35% of fees")],
     "Copy invite link", "action:copy-ref", "copy"),
    ('<span class="home-card-soon">Coming soon</span>', "Fantrade Fan Day, London.",
     "Our first day in real life: matchday on a big screen, the season's top Dream Club managers on stage, "
     "and a room full of people who trade the same players you do.",
     [("Where", "London"), ("When", "Spring 2027")],
     "Notify me", "action:irl-notify", "bell"),
]

def home_card(i, card):
    badge, title, copy, stats, cta, target, icon = card
    stat_html = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (k, v) for k, v in stats)
    if target.startswith('action:'):
        act = target[len('action:'):]
        pressed = ' aria-pressed="false"' if act == 'irl-notify' else ''
        cta_html = ('<button type="button" class="app-primary" data-home-action="%s"%s><span>%s</span> %s</button>'
                    % (act, pressed, cta, ic(icon, 'ic')))
    else:
        cta_html = '<a class="app-primary" href="%s">%s %s</a>' % (target, cta, ic(icon, 'ic'))
    return ('<article class="home-card" id="homeCard%d" aria-roledescription="slide" aria-label="%d of %d: %s">%s'
            '<h2>%s</h2><p>%s</p><dl class="home-card-stats">%s</dl>%s</article>'
            % (i, i + 1, len(HOME_CARDS), title.rstrip('.'), badge, title, copy, stat_html, cta_html))

da.append('<section class="home-next" aria-roledescription="carousel" aria-label="Things to do">'
          '<div class="home-cards" id="homeCards" tabindex="0">' + ''.join(home_card(i, c) for i, c in enumerate(HOME_CARDS)) + '</div>'
          '<div class="home-cards-nav"><div class="home-dots" id="homeDots">'
          + ''.join('<button type="button" aria-label="Show card %d"%s></button>' % (i + 1, ' aria-current="true"' if i == 0 else '') for i in range(len(HOME_CARDS)))
          + '</div><div class="home-arrows"><button type="button" id="homePrev" aria-label="Previous card">' + ic('arrow', 'ic') + '</button>'
          '<button type="button" id="homeNext" aria-label="Next card">' + ic('arrow', 'ic') + '</button></div></div></section>'
          '<section class="home-market"><div class="app-section-head"><h2>Players to watch</h2><a href="exchange.html">View exchange</a></div>'
          '<div class="kc-cat-tabs" id="homeTabs"><button class="kc-cat-tab on" type="button" data-f="hot">Trending</button>'
          '<button class="kc-cat-tab" type="button" data-f="gainers">Top gainers</button>'
          '<button class="kc-cat-tab" type="button" data-f="forwards">Forwards</button>'
          '<button class="kc-cat-tab" type="button" data-f="midfielders">Midfielders</button>'
          '<button class="kc-cat-tab" type="button" data-f="coaches">Coaches</button></div>'
          '<div id="homeMarketRows" class="kc-home-rows"></div></section>'
          '<a class="home-club" href="clubs.html">'+ic('formation','ic')+'<div><b>Your Dream Club</b>'
          '<small>Build your lineup from the players you own.</small></div><span style="margin-left:auto">→</span></a></div></main>')

DASH_JS = r"""
/* Home cards: native scroll-snap for the swipe, smooth scrollTo for dots and arrows. */
(function(){
  var track = document.getElementById('homeCards'); if(!track) return;
  var cards = [].slice.call(track.children), dots = [].slice.call(document.querySelectorAll('#homeDots button'));
  function current(){ var best = 0, dist = Infinity, left = track.getBoundingClientRect().left;
    cards.forEach(function(c, i){ var d = Math.abs(c.getBoundingClientRect().left - left); if(d < dist){ dist = d; best = i; } }); return best; }
  function go(i){ i = Math.max(0, Math.min(cards.length - 1, i));
    track.scrollTo({ left: cards[i].offsetLeft - cards[0].offsetLeft, behavior: 'smooth' }); }
  function sync(){ var i = current(); dots.forEach(function(d, k){ if(k === i) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current'); });
    document.getElementById('homePrev').disabled = i === 0; document.getElementById('homeNext').disabled = i === cards.length - 1; }
  var t; track.addEventListener('scroll', function(){ clearTimeout(t); t = setTimeout(sync, 60); }, { passive: true });
  dots.forEach(function(d, k){ d.addEventListener('click', function(){ go(k); }); });
  document.getElementById('homePrev').addEventListener('click', function(){ go(current() - 1); });
  document.getElementById('homeNext').addEventListener('click', function(){ go(current() + 1); });
  track.addEventListener('keydown', function(e){ if(e.key === 'ArrowRight'){ e.preventDefault(); go(current() + 1); } if(e.key === 'ArrowLeft'){ e.preventDefault(); go(current() - 1); } });
  function entries(){ var n = (FT.getState().fanplay.activeEntries || []).length; document.querySelectorAll('[data-home="entries"]').forEach(function(el){ el.textContent = n; }); }
  entries(); window.addEventListener('fantrade:statechange', entries); sync();
})();

/* Launch & Claim, search first. Nothing here loads or redraws on its own:
   the suggestions are in the page from the start and results change only
   when the manager searches, so the card never jumps while the page loads. */
(function(){
  var form = document.getElementById('homeClaimForm'), input = document.getElementById('homeClaimInput');
  var box = document.getElementById('homeClaimResults');
  var modal = document.getElementById('claimModalBackdrop'), closeBtn = document.getElementById('claimModalClose');
  var submitBtn = document.getElementById('claimSubmitBtn');
  if(!form || !input || !box) return;
  var hint = box.innerHTML, active = null, level = 1, years = 1, cloudRows = null, askedCloud = false;

  function esc(v){ var n = document.createElement('span'); n.textContent = v == null ? '' : String(v); return n.innerHTML; }
  function fold(s){ return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function num(n){ return Math.round(Number(n) || 0).toLocaleString('en-US'); }
  function compact(n){ n = Number(n) || 0; return n >= 1e6 ? (Math.round(n / 1e4) / 100).toLocaleString('en-US') + 'M' : num(n); }
  function usd(ftr){
    var d = (Number(ftr) || 0) * FTR_USD;
    if(d >= 1e6) return '$' + compact(d);
    if(d >= 100) return '$' + num(d);
    return '$' + d.toFixed(d < 1 ? 3 : 2);
  }

  /* Cleared players come from the database when signed in, otherwise from
     the catalogue built into the page. Anyone already on the market is
     shown as trading, never as claimable. */
  function eligible(){ return (cloudRows && cloudRows.length) ? cloudRows : ELIGIBLE; }
  function askCloud(){
    if(askedCloud || !(window.FTDB && FTDB.signedIn && FTDB.signedIn() && FTDB.listings)) return;
    askedCloud = true;
    FTDB.listings().then(function(rows){
      if(!rows || !rows.length) return;
      cloudRows = rows.filter(function(r){ return !r.claimed; }).map(function(r){
        var t = ftSym(r.ticker || r.asset_id), local = ELIGIBLE.filter(function(e){ return e.t === t; })[0] || {};
        return { t: t, n: r.name || local.n, p: Number(r.price) || local.p, v: Number(r.valuation_usd) || local.v, pos: r.position || local.pos || (r.kind === 'COACH' ? 'MGR' : 'FWD'),
                 club: r.club || local.club, lg: r.league || local.lg, w: r.gender ? (r.gender === 'W' ? 1 : 0) : local.w,
                 aka: r.known_as || local.aka, about: r.about || local.about, country: r.country || local.country, listingId: r.id,
                 _photo: r.photo_url };
      }).filter(function(e){ return e.p > 0; });
      cloudRows.forEach(function(e){
        if(e._photo && typeof PLAYER_PROFILES !== 'undefined') PLAYER_PROFILES[e.t] = Object.assign(PLAYER_PROFILES[e.t] || {}, { photo: e._photo });
      });
      if(input.value.trim()) search(input.value);
    }).catch(function(){});
  }
  function catalogue(){
    var out = ASSETS.map(function(a){ return { a: a, listed: true }; });
    eligible().forEach(function(e){ if(!FT.isLaunched(e.t)) out.push({ a: e, listed: false }); });
    return out;
  }
  function score(r, f){
    var name = fold(r.a.n);
    if(name.indexOf(f) === 0) return 0;
    if(name.split(/\s+/).some(function(w){ return w.indexOf(f) === 0; })) return 1;
    return 2;
  }
  function row(r){
    var a = r.a;
    var meta = '<small><i>' + esc(a.t) + '</i>' + esc(a.club || '') + '</small>';
    if(r.listed){
      return '<a class="home-claim-row is-listed" href="asset.html?a=' + encodeURIComponent(a.t) + '">' + playerPhoto(a.t, a.n)
        + '<span class="home-claim-who"><b>' + esc(a.n) + '</b>' + meta
        + '<span class="home-claim-val"><strong>' + usd(a.p) + '</strong> a share &middot; ' + pxFmt(a.p) + ' $FTR</span></span>'
        + '<span class="home-claim-action">Buy</span></a>';
    }
    var q = FT.claimQuote(a, 1);
    return '<button type="button" class="home-claim-row" data-claim="' + esc(a.t) + '">' + playerPhoto(a.t, a.n)
      + '<span class="home-claim-who"><b>' + esc(a.n) + '</b>' + meta
      + '<span class="home-claim-val">Open to claim. 5% costs <strong>' + usd(q.cost) + '</strong> &middot; ' + compact(q.cost) + ' $FTR</span></span>'
      + '<span class="home-claim-action">Claim</span></button>';
  }
  function search(raw){
    var f = fold(raw).trim();
    if(!f){ box.innerHTML = hint; return; }
    askCloud();
    var words = f.split(/\s+/);
    var hits = catalogue().filter(function(r){
      var hay = fold([r.a.n, r.a.aka, r.a.t, r.a.club].join(' '));
      return words.every(function(w){ return hay.indexOf(w) > -1; });
    }).sort(function(x, y){ return score(x, f) - score(y, f); }).slice(0, 4);
    if(!hits.length){
      box.innerHTML = '<div class="home-claim-empty"><b>No cleared player matches &ldquo;' + esc(raw.trim()) + '&rdquo;.</b>'
        + '<span>Fantrade adds footballers to the claim list as it approves them. Check the spelling, or try a surname.</span></div>';
      return;
    }
    box.innerHTML = hits.map(row).join('');
  }

  input.addEventListener('input', function(){ search(input.value); });
  form.addEventListener('submit', function(e){ e.preventDefault(); search(input.value); });
  box.addEventListener('click', function(e){
    var chip = e.target.closest('[data-q]');
    if(chip){ input.value = chip.dataset.q; search(input.value); input.focus(); return; }
    var claim = e.target.closest('[data-claim]');
    if(claim){ var t = claim.dataset.claim; open(eligible().filter(function(x){ return x.t === t; })[0]); }
  });

  // <main> is its own stacking context, so the dialog lives on <body>.
  if(modal && modal.parentNode !== document.body) document.body.appendChild(modal);
  function set(id, html){ var el = document.getElementById(id); if(el) el.innerHTML = html; }
  function bar(id, count){ var el = document.getElementById(id); if(el) el.style.flexBasis = (count / 10000000 * 100) + '%'; }
  function refresh(){
    if(!active) return;
    var q = FT.claimQuote(active, level), q1 = FT.claimQuote(active, 1), q2 = FT.claimQuote(active, 2);
    var market = 10000000 - 1000000 - q.shares;
    set('claimOpt1Fee', compact(q1.cost) + ' $FTR<i>&asymp; ' + usd(q1.cost) + '</i>');
    set('claimOpt2Fee', compact(q2.cost) + ' $FTR<i>&asymp; ' + usd(q2.cost) + '</i>');
    set('claimSplitYouTxt', num(q.shares)); set('claimSplitMktTxt', num(market));
    bar('claimSplitYou', q.shares); bar('claimSplitMkt', market);
    set('claimDailyLimitTxt', num(q.shares * 0.01));
    set('claimFpTxt', '+' + num(q.shares / 100));
    set('claimPriceTxt', pxFmt(active.p) + ' $FTR <small>(' + usd(active.p) + ')</small>');
    set('claimSharesTxt', num(q.shares) + ' <small>(' + q.percent + '%)</small>');
    set('claimBurnTxt', num(q.burn) + ' $FTR');
    set('claimTotalTxt', num(q.cost) + ' $FTR');
    set('claimUsdTxt', '&asymp; ' + usd(q.cost));
    set('claimBalTxt', num(q.balance) + ' $FTR');
    set('claimShortAmt', num(q.short) + ' $FTR');
    var short = document.getElementById('claimShort'); if(short) short.hidden = q.short <= 0;
    if(submitBtn){
      submitBtn.disabled = q.short > 0;
      submitBtn.textContent = q.short > 0 ? 'Not enough $FTR for this level' : 'Pay ' + compact(q.cost) + ' $FTR & launch ' + active.t;
    }
  }
  function pick(sel, attr, value){
    modal.querySelectorAll(sel).forEach(function(b){ b.classList.toggle('on', Number(b.dataset[attr]) === value); });
  }
  function open(a){
    if(!a || !modal) return;
    active = a; level = 1; years = 1;
    set('claimModalTitle', esc(a.n));
    var prof = (typeof PLAYER_PROFILES !== 'undefined' && PLAYER_PROFILES[a.t]) || {};
    var about = a.about || prof.about || '', country = a.country || prof.country || '';
    set('claimModalSub', '<b>' + esc(a.t) + '</b> &middot; ' + esc([a.club, country].filter(Boolean).join(' · ')) + ' &middot; 10,000,000 Activity Shares');
    set('claimModalPhoto', playerPhoto(a.t, a.n));
    var ab = document.getElementById('claimAbout'); if(ab){ ab.textContent = about; ab.hidden = !about; }
    pick('.claim-opt-btn', 'level', 1); pick('.claim-vest-btn', 'years', 1);
    refresh();
    if(modal.showModal){ if(!modal.open) modal.showModal(); } else modal.setAttribute('open', '');
    document.body.classList.add('claim-open');
    modal.scrollTop = 0;
  }
  function close(){ if(modal && modal.open){ if(modal.close) modal.close(); else modal.removeAttribute('open'); } document.body.classList.remove('claim-open'); active = null; }
  if(closeBtn) closeBtn.addEventListener('click', close);
  if(modal){
    // Like the player picker: a click outside the sheet closes it; Escape
    // closes it natively and lands here through the close event.
    modal.addEventListener('click', function(e){
      if(e.target !== modal) return;
      var r = modal.getBoundingClientRect();
      if(e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) close();
    });
    modal.addEventListener('close', function(){ document.body.classList.remove('claim-open'); active = null; });
    modal.querySelectorAll('.claim-opt-btn').forEach(function(b){
      b.addEventListener('click', function(){ level = Number(b.dataset.level) || 1; pick('.claim-opt-btn', 'level', level); refresh(); });
    });
    modal.querySelectorAll('.claim-vest-btn').forEach(function(b){
      b.addEventListener('click', function(){ years = Number(b.dataset.years) || 1; pick('.claim-vest-btn', 'years', years); refresh(); });
    });
  }
  window.addEventListener('fantrade:statechange', function(){ if(active) refresh(); });

  if(submitBtn) submitBtn.addEventListener('click', function(){
    if(!active || submitBtn.disabled) return;
    var a = active, lv = level, yr = years;
    submitBtn.disabled = true; submitBtn.textContent = 'Launching ' + a.t + '…';
    var db = window.FTDB && FTDB.signedIn && FTDB.signedIn() && FTDB.claim;
    var run = db
      ? FTDB.claim(a.listingId || ('lst-' + a.t), lv, yr).then(function(){
          var res = FT.launchPlayer(a, lv, yr, { settled: true });
          return FT.syncCloud ? FT.syncCloud().then(function(){ return res; }, function(){ return res; }) : res;
        }, function(err){
          // A database without the claim function yet: carry on locally.
          if(/function|schema cache|could not find/i.test(String(err && err.message))) return FT.launchPlayer(a, lv, yr);
          throw err;
        })
      : new Promise(function(ok){ ok(FT.launchPlayer(a, lv, yr)); });
    run.then(function(res){
      close();
      input.value = a.n; search(a.n);
      showToast(esc(a.n) + ' is live. You hold ' + num(res.shares) + ' ' + a.t + ' shares, vesting over ' + yr + (yr === 1 ? ' year.' : ' years.'));
    }).catch(function(err){
      refresh();
      showToast(esc((err && err.message) || 'The claim did not go through.'), 'error');
    });
  });
})();

/* The scrolling cards' own buttons: copy the invite link, and remember a
   "notify me" for the Fan Day on this device. */
(function(){
  var handle = String((FT.getState().user || {}).handle || '').replace(/^@/, '') || 'manager';
  var link = 'https://fantrade.app/ref/' + encodeURIComponent(handle);
  document.querySelectorAll('[data-home="reflink"]').forEach(function(el){ el.textContent = handle; });
  function copied(){ showToast('Invite link copied'); }
  document.querySelectorAll('[data-home-action="copy-ref"]').forEach(function(b){
    b.addEventListener('click', function(){
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(link).then(copied, fallback);
      } else fallback();
      function fallback(){
        var t = document.createElement('textarea'); t.value = link; t.setAttribute('readonly', '');
        t.style.position = 'fixed'; t.style.opacity = '0'; document.body.appendChild(t); t.select();
        try { document.execCommand('copy'); copied(); } catch(e){ showToast('Your link: ' + link); }
        t.remove();
      }
    });
  });
  var KEY = 'ft_irl_notify';
  function isOn(){ try { return localStorage.getItem(KEY) === '1'; } catch(e){ return false; } }
  function paint(b){
    var on = isOn();
    b.setAttribute('aria-pressed', on ? 'true' : 'false');
    var label = b.querySelector('span'); if(label) label.textContent = on ? "You're on the list" : 'Notify me';
  }
  document.querySelectorAll('[data-home-action="irl-notify"]').forEach(function(b){
    paint(b);
    b.addEventListener('click', function(){
      var on = !isOn();
      try { localStorage.setItem(KEY, on ? '1' : '0'); } catch(e){}
      paint(b);
      showToast(on ? "We'll tell you when Fan Day tickets open." : 'Fan Day reminder turned off.');
    });
  });
})();

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
      if(bSub) bSub.textContent = '≈ $' + (net * FTR_USD).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' USD';
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
      if(homeFilter === 'hot') list = list.filter(function(a){ return ['FSAKA','FAITN','FHLND','FKERR','FKM7','FYAML','FRUSS','FPLMR','FLJMS','FWIEG','FARTA'].indexOf(a.t) >= 0; });
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
        + "  <div class='kc-price-main'>" + pxFmt(a.p) + " <span style='font-size:10px;color:#767c82'>FTR</span></div>"
        + "  <div class='kc-price-sub'>≈ " + usdFmt(a.p) + " USD</div>"
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

# ══════════════════════════════════════════════════════════════════
# LEADERBOARD — global Dream Club standings
# ══════════════════════════════════════════════════════════════════
LB_CSS = """
.scols{grid-template-columns:54px 2fr 1.15fr 1.5fr .8fr .9fr 1fr 92px}
.club-cell{display:flex;align-items:center;gap:13px;min-width:0}
.mcrest{width:34px;height:38px;flex:none;clip-path:polygon(0 0,100% 0,100% 66%,50% 100%,0 66%);
  display:grid;place-items:center;font-family:Space Grotesk;font-weight:700;
  font-size:11px;color:#fff}
.club-cell .cn{font-size:13.5px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.div-card{border:1px solid var(--hair);background:rgba(255,255,255,.03);border-radius:18px;padding:20px;
  box-shadow:var(--inset);display:flex;gap:16px;align-items:flex-start;margin-bottom:10px}
.div-card:last-child{margin-bottom:0}
.div-card .dot{width:9px;height:9px;border-radius:99px;flex:none;margin-top:6px}
.div-card b{display:block;font-family:Space Grotesk;font-weight:700;
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
     "FPEP · 4-3-3 Tiki-taka", 18.5, 14890, 34200, "apex", "#1800ad"),
    (2, "Galactico Syndicate", "@ZidaneTactics", 32, 540100, 5.6, ["Bellingham 96", "Kane 95", "Rodri 94"],
     "$DonCarlo · 4-3-1-2 Fluid", 17.0, 13920, 29800, "apex", "#F4F6F1"),
    (3, "Arsenal Elite FC", "@GoonerBoss", 112, 495200, 6.9, ["Saka 95", "Ødegaard 94", "Saliba 93"],
     "FARTA · 4-3-3 Inverted", 16.5, 13450, 27100, "apex", "#FF5E8A"),
    (4, "Bavarian Meta XI", "@KaiserTactics", 19, 462800, 2.5, ["Musiala 94", "Sané 91", "Kimmich 93"],
     "$Alonso · 3-4-2-1 Dominance", 14.0, 12890, 23500, "apex", "#4DA6FF"),
    (5, "Lombardia Capital", "@MilanoWhale", 61, 420500, -0.9, ["Lautaro 93", "Barella 92", "Bastoni 91"],
     "$Inzaghi · 3-5-2 Direct", 13.5, 12110, 21200, "apex", "#FF6A1F"),
    (6, "Anfield Collective", "@KopLedger", 88, 398400, 3.1, ["Salah 94", "Van Dijk 92", "Szoboszlai 89"],
     "$Slot · 4-3-3 High press", 13.0, 11740, 19900, "apex", "#FF5E5E"),
    (7, "Seleção Futures", "@SambaStake", 27, 371900, 4.4, ["Vinícius 95", "Rodrygo 90", "Éder 88"],
     "$Dorival · 4-2-3-1 Counter", 12.5, 11020, 18300, "apex", "#1800ad"),
    (124, "Zero FC", "You · single-owner", 1, 245800, 7.9, ["Bruno 90", "Saka 95", "Haaland 97"],
     "FARTA · 4-3-3 High press", 15.0, 8420, 18400, "apex", "#1800ad"),
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
        '    <div style="font-family:Space Grotesk,sans-serif;font-weight:700;font-size:18px;color:var(--ink);white-space:nowrap">League Standings</div>'
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
            '<div style="min-width:0"><div style="font-family:Space Grotesk;'
            'font-weight:700;text-transform:uppercase;font-size:21px;'
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
            '<div><div style="font-family:Space Grotesk;font-weight:700;'
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

# Rebuilt social leaderboard.  The earlier table data remains the source of
# truth, while this presentation follows the compact mobile ranking reference.
LB2_CSS = """
.lb2-wrap{width:100%;max-width:680px;margin:0 auto;padding:0 20px 118px;box-sizing:border-box}
.lb2-tabs{display:grid;grid-template-columns:1fr 1fr;border-bottom:1px solid var(--hair);margin-bottom:26px}
.lb2-tabs button{position:relative;border:0;background:transparent;color:var(--faint);padding:13px 8px 16px;font-size:17px;font-weight:600;cursor:pointer}
.lb2-tabs button.on{color:#fff}.lb2-tabs button.on::after{content:"";position:absolute;left:26%;right:26%;bottom:-1px;height:3px;border-radius:4px;background:var(--lime)}
.lb2-tabs em{font-style:normal;font-size:11px;color:var(--faint);margin-left:4px}
.lb2-section-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:13px}
.lb2-section-head h2{font-size:21px!important;font-weight:600!important}.lb2-section-head h2 span{font-size:10px;color:#fff;background:rgba(24,0,173,.34);border-radius:5px;padding:3px 6px;vertical-align:3px;margin-left:5px}
.lb2-section-head a{color:var(--dim);font-size:13px}
.lb2-clubs{display:flex;gap:10px;overflow-x:auto;scrollbar-width:none;margin:0 -20px 22px;padding:0 20px 2px}.lb2-clans::-webkit-scrollbar{display:none}
.lb2-club{flex:0 0 182px;background:var(--panel);border:1px solid var(--hair);border-radius:17px;padding:14px;text-decoration:none;color:#fff;cursor:pointer;transition:transform .2s,border-color .2s,background .2s;text-align:left;border:1px solid rgba(255,255,255,.08)}
.lb2-club:hover{border-color:rgba(24,0,173,.5);transform:translateY(-2px);background:rgba(255,255,255,.05)}
.lb2-club-top{display:flex;align-items:center;gap:11px}.lb2-club-mark{width:48px;height:48px;border-radius:13px;background:#fff;display:grid;place-items:center;overflow:hidden;color:#090713;font-weight:800}.lb2-club-mark img{width:100%;height:100%;object-fit:cover}
.lb2-club b{display:block;font-size:14px;margin-top:10px}.lb2-club small{display:block;color:var(--faint);font-size:10.5px;margin-top:5px}.lb2-club strong{display:block;color:var(--positive);font-size:13px;margin-top:10px}
.lb2-filter{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:8px 0 16px}
.lb2-select{border:1px solid var(--hair);background:var(--panel-2);color:#fff;border-radius:13px;padding:9px 14px;font-weight:600}
.lb2-ranges{display:flex;align-items:center;gap:5px}.lb2-ranges button{border:0;background:transparent;color:var(--faint);border-radius:9px;padding:8px 10px;font-weight:600;cursor:pointer}.lb2-ranges button.on{background:var(--panel-2);color:#fff}
.lb2-me{display:grid;grid-template-columns:52px 1fr auto;gap:12px;align-items:center;background:var(--panel);border:1px solid var(--hair);border-radius:17px;padding:14px;margin-bottom:15px}
.lb2-me-logo{width:48px;height:48px;border-radius:50%;background:#46f58c;padding:10px;object-fit:contain}.lb2-me span{display:block;color:var(--dim);font-size:12px}.lb2-me b{display:block;color:var(--lime);font-size:20px;margin-top:1px}.lb2-me-value{text-align:right;font-size:20px;color:#fff}.lb2-me-value small{display:block;color:var(--faint);font-size:10px;margin-top:3px}
.lb2-list{display:flex;flex-direction:column}.lb2-row{display:grid;grid-template-columns:34px 48px minmax(0,1fr) auto;gap:10px;align-items:center;padding:13px 8px;border-bottom:1px solid rgba(255,255,255,.045);cursor:pointer;transition:background .2s,border-radius .2s;border-radius:12px}
.lb2-row:hover{background:rgba(255,255,255,.04)}
.lb2-rank{font-size:14px;color:var(--dim);text-align:center}.lb2-rank.medal{width:26px;height:31px;clip-path:polygon(0 0,100% 0,100% 72%,50% 100%,0 72%);display:grid;place-items:center;color:#160d02;font-weight:800;background:#f6c94c}.lb2-rank.silver{background:#c6cad2}.lb2-rank.bronze{background:#c17d48}
.lb2-avatar{width:44px;height:44px;border-radius:50%;object-fit:cover;background:var(--panel-2)}.lb2-crest{display:grid;place-items:center;font:700 14px Montserrat,system-ui,sans-serif;color:#fff;letter-spacing:.02em}.lb2-row.you{background:rgba(24,0,173,.18)}.lb2-row.you .lb2-name b::after{content:'You';font-size:10px;font-weight:600;color:#fff;background:var(--lime);border-radius:5px;padding:2px 6px;margin-left:7px;vertical-align:2px}.lb2-name{min-width:0}.lb2-name b{display:block;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.lb2-name span{display:block;color:var(--faint);font-size:11px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lb2-profit{text-align:right;color:var(--positive);font-size:15px;font-weight:600}.lb2-profit small{display:flex;justify-content:flex-end;margin-top:6px}.lb2-profit small img{width:20px;height:20px;border-radius:50%;object-fit:cover;margin-left:-5px;border:2px solid #05030d}
@media(min-width:900px){.lb2-wrap{padding-top:10px}.lb2-club{flex-basis:200px}.lb2-tabs button{font-size:18px}}
@media(max-width:360px){.lb2-wrap{padding-left:16px;padding-right:16px}.lb2-clubs{margin-left:-16px;margin-right:-16px;padding-left:16px;padding-right:16px}.lb2-row{grid-template-columns:28px 42px minmax(0,1fr) auto;gap:8px}.lb2-avatar{width:40px;height:40px}.lb2-profit{font-size:13px}}
"""

lb2 = ['<main><div class="lb2-wrap">' + tab_intro('Leaderboard') +
       '<div class="lb2-section-head"><h2>Clubs to watch</h2><a href="divisions.html">View all ›</a></div>'
       '<div class="lb2-clubs">'
       '<div class="lb2-club" role="button" tabindex="0" data-club-name="Risk On"><div class="lb2-club-top"><span class="lb2-club-mark">RMO</span></div><b>Risk On</b><small>🏆 4 members</small><strong>+3,497,855 $FTR</strong></div>'
       '<div class="lb2-club" role="button" tabindex="0" data-club-name="Apex Eleven"><div class="lb2-club-top"><span class="lb2-club-mark"><img src="assets/players/mbappe.webp" alt=""></span></div><b>Apex Eleven</b><small>⚽ 20 members</small><strong>+1,853,334 $FTR</strong></div>'
       '<div class="lb2-club" role="button" tabindex="0" data-club-name="North Bank"><div class="lb2-club-top"><span class="lb2-club-mark"><img src="assets/players/saka.webp" alt=""></span></div><b>North Bank</b><small>🔥 23 members</small><strong>+1,800,986 $FTR</strong></div>'
       '</div>'
       '<div class="lb2-filter"><span class="lb2-period-label">Performance</span><div class="lb2-ranges" id="lb2Ranges"><button class="on" data-m="1" type="button">24h</button><button data-m="3" type="button">7d</button><button data-m="7" type="button">30d</button><button data-m="12" type="button">All</button></div></div>'
       '<div class="lb2-me"><img class="lb2-me-logo" src="assets/fantrade-outline-logo.png" alt=""><div><span>Your rank</span><b data-bind="rank">#124</b></div><div class="lb2-me-value">245,800<small>$FTR club value</small></div></div>'
       '<div class="lb2-list" id="lb2List">']

lb2_avatars = ["pep", "mbappe", "saka", "musiala", "vinicius", "haaland", "bellingham", "arteta", "yamal", "palmer", "rodri", "vandijk", "rice"]
lb2_bubbles = [["saka", "haaland", "mbappe"], ["bellingham", "rodri", "vinicius"], ["saka", "odegaard", "saliba"], ["musiala", "wirtz", "rodri"], ["mbappe", "vinicius", "bellingham"]]
for i, row in enumerate(BOARD):
    rank, club, manager, _holders, _value, _delta, _xi, _coach, _boost, _fp, yearly, _division, _colour = row
    if club == "Zero FC":
        continue
    rank_html = ('<span class="lb2-rank medal%s">%d</span>' %
                 (" silver" if rank == 2 else (" bronze" if rank == 3 else ""), rank)
                 if rank <= 3 else '<span class="lb2-rank">%d.</span>' % rank)
    avatar = lb2_avatars[i % len(lb2_avatars)]
    bubbles = lb2_bubbles[i % len(lb2_bubbles)]
    bubble_html = "".join('<img src="assets/players/%s.webp" alt="">' % name for name in bubbles)
    profit = yearly * 73
    lb2.append('%s<img class="lb2-avatar" src="assets/players/%s.webp" alt=""><div class="lb2-name"><b>%s</b><span>%s</span></div><div class="lb2-profit" data-profit="%d">+%s<small>%s</small></div>' %
               (rank_html, avatar, club, manager, profit, format(profit, ",d"), bubble_html))
    lb2[-1] = ('<div class="lb2-row" role="button" tabindex="0" data-club-name="%s">' % club) + lb2[-1] + '</div>'
lb2.append('</div></div></main>')

LB2_JS = ("var BOARD_DATA=[" + LB_ROWS + "];") + r"""
/* The real field, when the account can be reached.

   Every club that actually exists is listed here, ranked on season FP, with
   your own row marked. The designed rows below it are a sample field: while
   Fantrade is new they keep the board looking like a board, and they are
   labelled as what they are rather than passed off as managers. */
(function(){
  var list = document.getElementById('lb2List');
  if(!list || typeof FT === 'undefined' || !FT.leaderboard) return;
  function esc(v){ return String(v == null ? '' : v).replace(/[&<>"]/g, function(ch){
    return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[ch]; }); }
  FT.leaderboard(50).then(function(board){
    if(!board || !board.rows || !board.rows.length) return;
    var html = board.rows.map(function(r){
      var pos = r.position;
      var medal = pos <= 3
        ? '<span class="lb2-rank medal' + (pos === 2 ? ' silver' : (pos === 3 ? ' bronze' : '')) + '">' + pos + '</span>'
        : '<span class="lb2-rank">' + pos + '.</span>';
      var tint = (r.colors && r.colors[0]) || '#1800ad';
      return '<div class="lb2-row' + (r.you ? ' you' : '') + '" role="button" tabindex="0" data-club-name="'
        + esc(r.name) + '">' + medal
        + '<span class="lb2-avatar lb2-crest" style="background:linear-gradient(160deg,' + esc(tint) + ',#050505)">'
        + esc(initials(r.name)) + '</span>'
        + '<div class="lb2-name"><b>' + esc(r.name) + '</b><span>' + esc(r.display_name)
        + ' · @' + esc(r.handle) + '</span></div>'
        + '<div class="lb2-profit">' + money(Math.round(r.season_fp)) + '<small>FP</small></div></div>';
    }).join('');
    list.insertAdjacentHTML('afterbegin', html
      + '<div class="lb2-section-head" style="margin:22px 0 13px"><h2>Sample field</h2></div>');
  });
})();
document.querySelectorAll('#lb2Ranges button').forEach(function(button){
  button.addEventListener('click', function(){
    document.querySelectorAll('#lb2Ranges button').forEach(function(item){ item.classList.remove('on'); });
    button.classList.add('on');
    var multiplier = Number(button.dataset.m || 1);
    document.querySelectorAll('[data-profit]').forEach(function(value){
      value.childNodes[0].nodeValue = '+' + (Number(value.dataset.profit) * multiplier).toLocaleString('en-US');
    });
  });
});

function money(n){ return Number(n || 0).toLocaleString('en-US'); }
function initials(n){ return (n || 'FC').split(/\s+/).map(function(w){ return w.charAt(0).toUpperCase(); }).join('').slice(0, 3); }

function openClubModal(clubName){
  var b = BOARD_DATA.filter(function(x){ return x.c.toLowerCase() === clubName.toLowerCase(); })[0];
  if(!b){
    if(clubName === "Risk On") b = { c: "Risk On", m: "Marcus Vance", r: 1, v: 3497855, fp: 812, b: 18.5, h: 4, co: "FARTA · 4-3-3 High press", xi: ["Haaland", "Saka", "Mbappe"], cl: "#1800ad" };
    else if(clubName === "Apex Eleven") b = { c: "Apex Eleven", m: "Elena Rostova", r: 2, v: 1853334, fp: 786, b: 16.0, h: 20, co: "FPEP · 3-5-2 Possession", xi: ["Bellingham", "Rodri", "Vinicius"], cl: "#FF6A1F" };
    else if(clubName === "North Bank") b = { c: "North Bank", m: "David K.", r: 3, v: 1800986, fp: 754, b: 15.2, h: 23, co: "FARTA · 4-3-3 Overload", xi: ["Saka", "Odegaard", "Saliba"], cl: "#FF3B47" };
    else b = BOARD_DATA[0];
  }

  var s = FT.getState();
  var defaultStake = 5000;

  function renderClubModal(stakeAmt){
    var sharePct = ((stakeAmt / ((b.v || 200000) * 0.15 + stakeAmt)) * 100).toFixed(1);
    var estPayout = Math.round(stakeAmt * (0.15 + ((b.b || 15) / 100) * 0.1));
    return '<div class="club-inspect-wrap">'
      + '<div style="display:flex;align-items:center;gap:14px;margin-bottom:16px">'
      + '<span class="mcrest" style="width:50px;height:50px;border-radius:14px;background:linear-gradient(160deg,' + (b.cl || '#1800ad') + ',#050505);display:grid;place-items:center;font-weight:800;font-size:16px;color:#fff;border:1px solid rgba(255,255,255,.15)">' + initials(b.c) + '</span>'
      + '<div><h3 class="ft-modal-title" style="margin:0;font-size:20px">' + b.c + '</h3>'
      + '<p class="ft-modal-desc" style="margin:3px 0 0;font-size:12px">' + b.m + ' · <b style="color:var(--lime)">Rank #' + b.r + '</b></p></div>'
      + '</div>'
      + '<div class="ft-modal-card" style="margin-bottom:16px">'
      + '<div class="m-row"><span>Club Valuation</span><b>' + money(b.v) + ' $FTR</b></div>'
      + '<div class="m-row"><span>Tactics &amp; Synergy</span><b>' + (b.co || '4-3-3 High press') + ' (+' + (b.b || 15).toFixed(1) + '%)</b></div>'
      + '<div class="m-row"><span>Total Fans Points</span><b>' + money(b.fp || 750) + ' FP</b></div>'
      + '<div class="m-row total"><span>Syndicate Prize Pool</span><b style="color:var(--lime)">' + money(Math.round((b.v || 200000) * 0.15)) + ' $FTR staked</b></div>'
      + '</div>'
      + '<div class="k-label">Core XI Squad</div>'
      + '<div class="ft-modal-card" style="margin-bottom:18px">'
      + '<div class="xi">' + (b.xi || ['Saka', 'Haaland', 'Mbappe']).map(function(x){ return '<i>★ ' + x + '</i>'; }).join('') + '</div>'
      + '</div>'
      + '<div class="k-label">Invest &amp; Share Matchday Profits</div>'
      + '<div style="background:rgba(24,0,173,.07);border:1px solid rgba(24,0,173,.25);border-radius:16px;padding:16px;margin-bottom:16px">'
      + '<p style="margin:0 0 12px;font-size:12px;color:var(--dim);line-height:1.5">Stake $FTR in <b>' + b.c + '</b> to automatically receive a share of matchday winnings and player dividend distributions.</p>'
      + '<div class="field" style="margin-bottom:10px"><label>Stake amount ($FTR)</label><input id="lbStakeAmt" value="' + money(stakeAmt) + '" inputmode="numeric"></div>'
      + '<div class="quick" id="lbStakeQuick" style="margin-bottom:12px">'
      + '<button type="button" data-amt="1000">1,000</button><button type="button" data-amt="5000">5,000</button><button type="button" data-amt="10000">10,000</button><button type="button" data-amt="25000">25,000</button>'
      + '</div>'
      + '<div class="b-row" style="margin:6px 0 4px"><span>Your Profit Share</span><b style="color:var(--lime)">' + sharePct + '% pool ownership</b></div>'
      + '<div class="b-row" style="margin:4px 0 12px"><span>Est. Matchday Yield</span><b style="color:var(--positive)">+' + money(estPayout) + ' $FTR / round</b></div>'
      + '<div style="font-size:11px;color:var(--faint);margin-bottom:14px">Your balance: <b>' + money(FT.getState().wallet.balance) + ' $FTR</b></div>'
      + '<button class="btn btn-lime" id="lbConfirmStake" type="button" style="width:100%;justify-content:center">Stake ' + money(stakeAmt) + ' $FTR &amp; Join Syndicate</button>'
      + '</div>'
      + '</div>';
  }

  openModal(renderClubModal(defaultStake));

  function bindEvents(curStake){
    var inp = document.getElementById('lbStakeAmt');
    var btn = document.getElementById('lbConfirmStake');
    document.querySelectorAll('#lbStakeQuick button').forEach(function(qb){
      qb.addEventListener('click', function(){
        var amt = parseInt(qb.dataset.amt, 10);
        openModal(renderClubModal(amt));
        bindEvents(amt);
      });
    });
    if(inp && btn){
      inp.addEventListener('input', function(){
        var val = parseInt(inp.value.replace(/[^0-9]/g, ''), 10) || 0;
        btn.textContent = 'Stake ' + money(val) + ' $FTR & Join Syndicate';
      });
    }
    if(btn){
      btn.addEventListener('click', function(){
        var amt = parseInt((inp ? inp.value : curStake).toString().replace(/[^0-9]/g, ''), 10) || 0;
        if(amt <= 0){ showToast('Enter a valid staking amount.', 'error'); return; }
        var state = FT.getState();
        if(amt > state.wallet.balance){ showToast('Insufficient $FTR balance to stake ' + money(amt) + ' $FTR.', 'error'); return; }
        state.wallet.balance -= amt;
        FT.saveState();
        closeModal();
        showToast('🎉 Successfully staked ' + money(amt) + ' $FTR in ' + b.c + '! Your profit share is active.', 'success');
      });
    }
  }

  bindEvents(defaultStake);
}

document.querySelectorAll('[data-club-name]').forEach(function(el){
  el.addEventListener('click', function(){
    openClubModal(el.dataset.clubName);
  });
  el.addEventListener('keydown',function(event){if(event.key==='Enter'||event.key===' '){event.preventDefault();el.click();}});
});
"""

page("leaderboard.html", "Leaderboard — Fantrade", "".join(lb2), LB2_JS, LB2_CSS)
print("built leaderboard.html")

# ══════════════════════════════════════════════════════════════════
# NOTIFICATIONS — activity feed
# ══════════════════════════════════════════════════════════════════
from notifications_page import HTML as NT_HTML, JS as NT_JS
page("notifications.html", "Notifications — Fantrade", NT_HTML, NT_JS)
print("built notifications.html")

# ══════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════
ST_CSS = """
.sec-card{scroll-margin-top:130px}
.sec-title{display:flex;align-items:center;gap:14px;margin-bottom:20px}
.sec-title h3{font-family:Space Grotesk;font-weight:700;text-transform:uppercase;
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
.settings-head-copy h1{font:800 19px Space Grotesk,sans-serif;font-weight:700;margin:0;color:var(--ink)}
.settings-head-copy p{font-size:10.5px;color:var(--faint);margin:3px 0 0}
.settings-nav{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:7px;margin:0 0 14px}
.settings-nav a{min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding:11px 5px;border:1px solid rgba(255,255,255,.065);border-radius:12px;background:rgba(255,255,255,.025);color:var(--faint);text-decoration:none;text-align:center;font-size:9px;line-height:1.2;transition:.2s ease}
.settings-nav a .ic{width:16px;height:16px}
.settings-nav a:hover{color:var(--ink);border-color:rgba(255,255,255,.14);background:rgba(255,255,255,.045)}
.settings-nav a.on{color:#0a0d03;background:var(--lime);border-color:var(--lime);box-shadow:var(--shadow-action)}
.settings-hero{padding:3px 2px 14px}
.settings-hero h2{margin:0 0 5px;font:800 17px Space Grotesk,sans-serif!important;text-transform:none!important}
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
            '1,000,000</span></div></div>'
            '<div class="mini"><div class="k">Locked</div><div class="v"><span data-bind="locked">5,000</span></div></div>'
            '<div class="mini"><div class="k">Season payouts</div><div class="v"><span data-bind="earned">'
            '19,640</span></div></div></div>'
            '<div class="tf-row" style="margin-top:20px">@@@@</div>@@'
            '<div class="b-row"><span>Withdrawal fee</span><b>0.5% · minimum 50 $FTR</b></div>'
            '<div class="b-row"><span>Settlement window</span><b>1–2 working days</b></div>'
            '<div class="b-row total"><span>Verification status</span>'
            '<b class="settings-ok">Verified</b></div>'
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
            '<p class="settings-note">'
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
            '<div class="rowlink">@@ Full ledger export (CSV)<b><a href="wallet.html" '
            'class="app-text-link">Download</a></b></div>'
            '<div class="rowlink">@@ Gains summary for this tax year<b><a href="wallet.html" '
            'class="app-text-link">Download</a></b></div>'
            '<div class="rowlink">@@ Account data request (GDPR)<b><a href="#" id="stGdpr" '
            'class="app-text-link">Request</a></b></div>'
            '<div class="danger-zone" style="margin-top:26px">'
            '<h3 class="danger-title">Danger zone</h3>'
            '<p class="settings-note" style="margin:0 0 18px">'
            'Resetting returns this prototype to its opening state — wallet, holdings, club and activity. '
            'Closing an account sells every position at market and pays the balance out.</p>'
            '<div style="display:flex;gap:10px;flex-wrap:wrap">@@@@</div></div>'
            '</div></div>',
            ic("receipt", "ic-lg"), ic("receipt", "ic"), ic("scales", "ic"), ic("shield", "ic"),
            btn("Reset prototype data", "btn-glass", tag="button", extra='id="stReset"'),
            btn("Close account", "btn-red", tag="button", extra='id="stClose"'))

ST_JS = r"""
window.addEventListener('load',function(){var nav=document.querySelector('.settings-nav'),on=nav&&nav.querySelector('a.on');if(!on||nav.scrollWidth<=nav.clientWidth)return;nav.scrollLeft=0;var d=on.getBoundingClientRect().left-nav.getBoundingClientRect().left-parseFloat(getComputedStyle(nav).paddingLeft);if(d>0)nav.scrollLeft=d;});
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
.kc-p-username{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:22px;letter-spacing:-.01em;color:var(--ink)}
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
.kc-ref-title{font-family:Space Grotesk,sans-serif;font-weight:700;font-size:16px;color:var(--ink);margin-bottom:4px}
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

ac = ['<main><div class="kc-profile-wrap">', tab_intro('Your profile'),
      # One card carries who you are: the picture, the name, the handle and
      # the two facts that never change — when you joined and where you play.
      '<section class="profile-card">'
      '<div class="profile-card-top">'
      '<div class="profile-avatar-wrap">'
      '<button type="button" class="profile-avatar-button" id="kcAvatarBtn" aria-label="Change profile picture">'
      '<img src="assets/fantrade-outline-logo.png" alt="" width="84" height="84" id="kcProfileAvatar" data-avatar-img>'
      '<span class="profile-avatar-edit" aria-hidden="true">' + ic('camera', 'ic') + '</span>'
      '</button>'
      '<input type="file" id="kcAvatarInput" accept="image/png,image/jpeg,image/webp" hidden>'
      '</div>'
      '<div class="profile-who">'
      '<h2 id="kcUsername">Your name</h2>'
      '<p class="profile-handle" data-bind="handle">@manager</p>'
      '</div></div>'
      # Their own row: side by side they would not fit beside the picture at
      # phone width, and wrapping there pushed the avatar out of line.
      '<div class="profile-who-actions">'
      '<button type="button" class="profile-chip-btn" id="kcEditNameBtn">Edit name</button>'
      '<button type="button" class="profile-chip-btn subtle" id="kcAvatarRemove">Remove photo</button>'
      '</div>'
      '<dl class="profile-meta">'
      '<div><dt>Manager since</dt><dd id="profileSince">—</dd></div>'
      '<div><dt>Home league</dt><dd id="profileLeague">—</dd></div>'
      '<div><dt>Account ID</dt><dd><button type="button" class="profile-uid" id="kcCopyUidBtn" '
      'title="Copy account ID"><span id="kcUid">242423082</span>' + ic('copy', 'ic') + '</button></dd></div>'
      '</dl></section>',
      # What the account is worth, as one panel rather than three loose lines.
      '<dl class="profile-overview">'
      '<div class="lead"><dt>Portfolio value</dt><dd><span id="profileNet">—</span> <small>$FTR</small></dd></div>'
      '<div><dt>Activity Assets held</dt><dd id="profileHoldings">—</dd></div>'
      '<div><dt>Your club</dt><dd id="profileClub">—</dd></div>'
      '</dl>',
      '<h2 class="app-section-title">Your Fantrade</h2><div class="profile-links">']
for label, description, href, icon in [
    ('Wallet','Your balance, shares and transfers','ftr.html','wallet'),
    ('Dream Club','Your team, formation and colours','clubs.html','formation'),
    ('Security','Password and account protection','settings-security.html','shield'),
    ('Notifications','Choose what you hear from us','settings-alerts.html','bell'),
    ('Settings','Profile, club and play preferences','settings.html','filter')]:
    ac.append('<a class="profile-link" href="'+href+'"><span class="profile-link-icon">'+ic(icon,'ic')+'</span>'
              '<div><strong>'+label+'</strong><small>'+description+'</small></div>'+ic('arrow','ic')+'</a>')
ac.append('</div><details class="profile-tools"><summary><span>Membership &amp; account tools</span>'
          + ic('arrow', 'ic') + '</summary><div class="profile-tools-content">')
for ident, label in [('kcVipPill','Membership benefits'),('kcSafeguardPill','Account safeguard'),
                     ('kcVerifiedPill','Verification'),('kcLoyaltyRow','$FTR loyalty'),
                     ('kcReferralCard','Invite friends')]:
    ac.append('<button class="profile-tool" type="button" id="'+ident+'"><span>'+label+'</span>'+ic('arrow','ic')+'</button>')
ac.append('<div class="profile-tool as-row"><span>Pay fees with $FTR</span>'
          '<button type="button" class="kc-switch on" id="kcFeeSwitch" aria-label="Toggle pay fees with $FTR"><i></i></button></div>'
          '</div></details>'
          '<button type="button" class="profile-signout" id="kcSignOutBtn">Sign out</button>'
          '<div id="kcToast" class="kc-toast" role="status"><span id="kcToastText"></span></div></div></main>')

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

  // Profile picture upload
  var avatarBtn = document.getElementById('kcAvatarBtn');
  var avatarInput = document.getElementById('kcAvatarInput');
  var avatarRemove = document.getElementById('kcAvatarRemove');
  function resizeAvatar(file){
    return new Promise(function(resolve, reject){
      if(!file || !/^image\//.test(file.type || '')){ reject(new Error('Choose an image file.')); return; }
      if(file.size > 5 * 1024 * 1024){ reject(new Error('Choose an image under 5 MB.')); return; }
      var reader = new FileReader();
      reader.onerror = function(){ reject(new Error('The image could not be opened.')); };
      reader.onload = function(){
        var img = new Image();
        img.onerror = function(){ reject(new Error('The image could not be read.')); };
        img.onload = function(){
          var size = Math.min(480, Math.max(img.width, img.height));
          var canvas = document.createElement('canvas');
          canvas.width = size; canvas.height = size;
          var ctx = canvas.getContext('2d');
          ctx.fillStyle = '#050505'; ctx.fillRect(0,0,size,size);
          var scale = Math.max(size / img.width, size / img.height);
          var w = img.width * scale, h = img.height * scale;
          ctx.drawImage(img, (size - w) / 2, (size - h) / 2, w, h);
          resolve(canvas.toDataURL('image/jpeg', .86));
        };
        img.src = reader.result;
      };
      reader.readAsDataURL(file);
    });
  }
  if(avatarBtn && avatarInput){
    avatarBtn.addEventListener('click', function(){ avatarInput.click(); });
    avatarInput.addEventListener('change', function(){
      var file = avatarInput.files && avatarInput.files[0];
      if(!file) return;
      resizeAvatar(file).then(function(dataUrl){
        FT.setAvatar(dataUrl);
        showToast('Profile picture updated.');
      }).catch(function(error){ showToast(error.message); }).finally(function(){ avatarInput.value = ''; });
    });
  }
  if(avatarRemove){
    avatarRemove.addEventListener('click', function(){
      FT.setAvatar('');
      showToast('Profile picture removed.');
    });
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
  var storedName = localStorage.getItem('ft_username') || FT.getState().user.name;
  if(nameEl) nameEl.textContent = storedName;
  function updateProfileOverview(){
    var s = FT.getState();
    function set(id, text){ var el = document.getElementById(id); if(el) el.textContent = text; }
    set('profileNet', Math.round(FT.holdingsValue() + s.wallet.balance + s.wallet.locked).toLocaleString('en-US'));
    set('profileHoldings', Object.keys(s.holdings).filter(function(key){
      return s.holdings[key].shares > 0; }).length);
    set('profileClub', s.club.name);
    set('profileSince', (s.auth && s.auth.since) || '—');
    set('profileLeague', s.user.league || '—');
  }
  updateProfileOverview();
  window.addEventListener('fantrade:statechange',updateProfileOverview);

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

def settings_top(title, subtitle, back=("account.html", "Profile")):
    return ('<a class="back-btn" href="%s" aria-label="Back to %s">Back</a>'
            '<header class="app-intro settings-intro"><div><h1>%s</h1><p>%s</p></div></header>'
            ) % (back[0], back[1].lower(), title, subtitle)

# Settings reads as two groups rather than one undifferentiated wall: the
# things you set up, and the things that end or export the account.
SETTINGS_GROUPS = [
    ("Your account", ["profile", "club", "security", "alerts"]),
    ("Money and play", ["wallet", "play"]),
    ("Leaving", ["data"]),
]
SETNAV_BY_KEY = {key: (icon_name, label) for key, icon_name, label in SETNAV}

settings_sections = []
for group_title, keys in SETTINGS_GROUPS:
    rows = []
    for key in keys:
        icon_name, _ = SETNAV_BY_KEY[key]
        title, desc = SETTINGS_COPY[key]
        rows.append('<a class="settings-row%s" href="settings-%s.html">'
                    '<span class="settings-row-icon">%s</span>'
                    '<span class="settings-row-text"><b>%s</b><small>%s</small></span>%s</a>' %
                    (" danger" if key == "data" else "", key,
                     ic(icon_name, "ic"), title, desc, ic("arrow", "ic")))
    settings_sections.append('<h2 class="settings-group-title">%s</h2><div class="settings-group">%s</div>'
                             % (group_title, "".join(rows)))

settings_index = ('<main><div class="kc-settings-wrap">' +
                  settings_top("Settings", "Changes save to your Fantrade profile and follow you across devices.") +
                  "".join(settings_sections) + '</div></main>')
page("settings.html", "Profile settings — Fantrade", settings_index, ST_JS, ST_CSS)
print("built settings.html")

def settings_section(key):
    """The section pill already names the page, so the section keeps only its
    one-line explanation — no second icon-and-heading repeating the name."""
    return re.sub(r'<div class="sec-title"><span class="ibox[^"]*">.*?</span><div><h3>.*?</h3><p>(.*?)</p>\s*</div></div>',
                  r'<p class="sec-lede">\1</p>', SECTIONS[key], count=1, flags=re.S)

for key, _icon_name, _label in SETNAV:
    title, desc = SETTINGS_COPY[key]
    body = ('<main><div class="kc-settings-wrap">'
            '<a class="back-btn" href="settings.html" aria-label="Back to settings">Back</a>'
            '<h1 class="sr-only">' + title + '</h1>' +
            settings_nav(key) + settings_section(key) + '</div></main>')
    page("settings-%s.html" % key, "%s — Fantrade" % title, body, ST_JS, ST_CSS)
    print("built settings-%s.html" % key)

# Wallet routes are generated together by pages2.py.
