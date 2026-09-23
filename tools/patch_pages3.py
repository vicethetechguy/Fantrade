import re
from pathlib import Path

p3_path = Path("tools/pages3.py")
content = p3_path.read_text(encoding="utf-8")

# 1. Add AUTH_PAGE_CSS and SIGNUP_PAGE_CSS
auth_css_code = '''
AUTH_PAGE_CSS = """
html, body{
  height:100%!important;height:100dvh!important;max-height:100dvh!important;
  overflow:hidden!important;position:fixed!important;width:100%!important;
}
.auth{
  height:100%!important;height:100dvh!important;max-height:100dvh!important;
  overflow:hidden!important;min-height:0!important;display:grid;grid-template-columns:1.05fr 1fr;
}
.auth-brand{
  height:100%!important;height:100dvh!important;max-height:100dvh!important;
  overflow:hidden!important;padding:max(50px,calc(42px + env(safe-area-inset-top))) 48px 36px!important;
  justify-content:center!important;
}
.auth-brand h1{font-size:clamp(28px,3.2vw,44px)!important;margin-top:14px!important}
.auth-brand .lede{margin-top:14px!important;font-size:13.5px!important}
.proof{margin-top:24px!important;gap:12px!important}
.proof .pr{gap:12px!important;font-size:12px!important}
.auth-form{
  height:100%!important;height:100dvh!important;max-height:100dvh!important;
  overflow:hidden!important;justify-content:center!important;
  padding:max(50px,calc(42px + env(safe-area-inset-top))) 32px max(16px,env(safe-area-inset-bottom))!important;
}
.auth-form .inner{max-width:420px!important;width:100%!important}
.auth-form h2{font-size:clamp(22px,2.4vw,32px)!important;margin:0 0 2px!important}
.auth-sub{font-size:12px!important;margin:2px 0 16px!important;line-height:1.45!important}
.tf{margin-bottom:10px!important}
.tf label{font-size:9px!important;margin-bottom:4px!important}
.tf .inp{padding:9px 14px!important;border-radius:12px!important}
.tf input,.tf select{font-size:13px!important}
.checkrow{margin:6px 0 14px!important;font-size:11.5px!important}
.splitline{margin:12px 0!important;font-size:8.5px!important}
.oauth{gap:8px!important}
.oauth button{padding:10px 8px!important;font-size:11.5px!important;border-radius:12px!important}
.auth-alt{margin-top:12px!important;font-size:11.5px!important}
.nav-min{top:14px!important;padding:0 24px!important}
@media (max-width:768px){
  .auth{grid-template-columns:1fr!important}
  .auth-brand{display:none!important}
  .auth-form{padding:max(42px,calc(34px + env(safe-area-inset-top))) 20px max(12px,env(safe-area-inset-bottom))!important}
  .auth-form .inner{max-width:380px!important}
  .auth-form h2{font-size:21px!important}
  .auth-sub{font-size:11px!important;margin:2px 0 10px!important}
  .tf{margin-bottom:7px!important}
  .tf label{font-size:8.5px!important;margin-bottom:2px!important}
  .tf .inp{padding:7px 11px!important;border-radius:9px!important}
  .tf input,.tf select{font-size:12.5px!important}
  .checkrow{margin:6px 0 10px!important;font-size:10.5px!important;gap:7px!important}
  .checkrow .box{width:16px!important;height:16px!important;border-radius:5px!important}
  .btn{min-height:40px!important;padding:9px 16px!important;font-size:12.5px!important;border-radius:10px!important}
  .splitline{margin:8px 0!important;font-size:8.5px!important}
  .oauth{display:grid!important;grid-template-columns:repeat(3,1fr)!important;gap:6px!important}
  .oauth button{padding:7px 4px!important;font-size:10.5px!important;border-radius:9px!important;gap:4px!important}
  .oauth button .ic{width:12px!important;height:12px!important}
  .auth-alt{margin-top:8px!important;font-size:11px!important}
  .demo-note{margin-top:6px!important;padding:6px 8px!important;font-size:9.5px!important;line-height:1.35!important}
  .nav-min{top:10px!important;padding:0 16px!important}
}
"""

SIGNUP_PAGE_CSS = AUTH_PAGE_CSS + """
@media (max-width:768px){
  .auth-form h2{font-size:19px!important}
  .auth-sub{font-size:10.5px!important;margin:1px 0 6px!important}
  .tf{margin-bottom:5px!important}
  .tf label{font-size:8px!important;margin-bottom:2px!important}
  .tf .inp{padding:5.5px 10px!important;border-radius:8px!important}
  .tf input,.tf select{font-size:12px!important}
  .strength{margin-top:2px!important;gap:3px!important}
  .strength i{height:2px!important}
  .hint{margin:1px 0 3px!important;font-size:9px!important}
  .checkrow{margin:4px 0 6px!important;font-size:10px!important;gap:6px!important;line-height:1.25!important}
  .checkrow .box{width:14px!important;height:14px!important;border-radius:4px!important}
  .btn{min-height:36px!important;padding:7px 12px!important;font-size:12px!important;border-radius:9px!important}
  .splitline{margin:5px 0!important;font-size:8px!important}
  .oauth{display:grid!important;grid-template-columns:repeat(3,1fr)!important;gap:5px!important}
  .oauth button{padding:5px 3px!important;font-size:10px!important;border-radius:8px!important;gap:4px!important}
  .auth-alt{margin-top:5px!important;font-size:10px!important}
  .nav-min{top:8px!important;padding:0 14px!important}
}
"""
'''

content = content.replace(
    '# ══════════════════════════════════════════════════════════════════\n# SIGN IN',
    auth_css_code + '\n# ══════════════════════════════════════════════════════════════════\n# SIGN IN'
)

content = content.replace(
    'page("signin.html", "Sign in — Fantrade", "".join(si), SIGNIN_JS, chrome=False)',
    'page("signin.html", "Sign in — Fantrade", "".join(si), SIGNIN_JS, css=AUTH_PAGE_CSS, chrome=False)'
)

content = content.replace(
    'page("signup.html", "Create account — Fantrade", "".join(su), SIGNUP_JS, chrome=False)',
    'page("signup.html", "Create account — Fantrade", "".join(su), SIGNUP_JS, css=SIGNUP_PAGE_CSS, chrome=False)'
)

# 2. Update Onboarding: Immediate Player Share Purchase at Step 1
old_ob_steps = '''STEPS = [("01", "Manager profile"), ("02", "Fund your wallet"),
         ("03", "First asset"), ("04", "Name your club")]'''

new_ob_steps = '''STEPS = [("01", "Buy player shares"), ("02", "Manager profile"),
         ("03", "Name your club"), ("04", "Matchday ready")]'''

content = content.replace(old_ob_steps, new_ob_steps)

# Replace the onboarding step panes
old_step_panes = '''# step 1
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
            '<p>Roughly £4,030 at today\\'s rate. Enough for a starting eleven and your first Elite-tier entry.</p></div>'
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
ob.append('</div>')'''

new_step_panes = '''# step 1: Buy player shares immediately with welcome grant
ob.append('<div class="step-pane on" data-pane="0">'
          '<div class="grant" style="margin-bottom:18px"><div class="k">🎉 Welcome Grant · 50,000 $FTR Ready</div>'
          '<div class="v">50,000<span style="font-size:17px;color:var(--faint);letter-spacing:0"> $FTR</span></div>'
          '<p>Start trading immediately. Pick a star footballer below to buy your opening fractional shares with 1 tap.</p></div>'
          '<h4 class="ob-h4">Select your star player</h4>'
          '<p class="ob-p">Every player has a fixed supply of 10,000,000 shares. Choose which asset to back:</p>'
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
ob.append('<div class="field" style="margin-top:16px"><label>Shares to buy</label>'
          '<input id="obShares" value="500" inputmode="numeric"></div>'
          '<div class="quick"><button data-s="100">100</button><button data-s="250">250</button>'
          '<button data-s="500">500</button><button data-s="1000">1,000</button></div>'
          '<div class="line"><span>Subtotal</span><b id="obSub">—</b></div>'
          '<div class="line"><span>Protocol fee (0.4%)</span><b id="obFee">—</b></div>'
          '<div class="line"><span>Total</span><b id="obTot">—</b></div>')
ob.append(btn("Buy shares &amp; continue" + ARROW, tag="button", extra='id="obBuy" style="width:100%;justify-content:space-between;margin-top:16px"'))
ob.append('</div>')

# step 2: Manager profile
ob.append('<div class="step-pane" data-pane="1">'
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

# step 3: Name your club
ob.append('<div class="step-pane" data-pane="2">'
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

# step 4: Review & Gameweek Readiness
ob.append('<div class="step-pane" data-pane="3">'
          '<h4 class="ob-h4">Ready for Gameweek 28</h4>'
          '<p class="ob-p">Your starter shares are in your wallet and your club identity is registered. '
          'You are ready to enter the trading arena.</p>'
          '<div class="grant" style="background:radial-gradient(ellipse at 50% 120%,rgba(24,0,173,.22),rgba(24,0,173,.04) 70%)">'
          '<div class="k">Desk Status</div>'
          '<div class="v" style="font-size:28px">Ready for Matchday</div>'
          '<p>Gameweek 28 locks in 3 hours. Complete your eleven or stake in syndicates anytime from your desk.</p>'
          '</div></div>')'''

content = content.replace(old_step_panes, new_step_panes)

# Update OB_JS
old_ob_js = '''var step = 0, PANES = document.querySelectorAll('.step-pane'), STEPS_N = PANES.length;
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
}'''

new_ob_js = '''var step = 0, PANES = document.querySelectorAll('.step-pane'), STEPS_N = PANES.length;
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
  try {
    var r = FT.executeTrade('buy', picked.sym, picked.nm, sh, picked.px, picked.coach);
    showToast('🎉 ' + sh.toLocaleString('en-US') + ' ' + picked.sym + ' shares purchased! You are officially an owner.', 'success');
    sum();
    setTimeout(function(){
      if(step === 0){ step = 1; render(); sum(); }
    }, 600);
  } catch(err){ showToast(err.message, 'error'); }
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
    return true;
  }
  return true;
}'''

content = content.replace(old_ob_js, new_ob_js)

# Select first player pick by default in onboarding
content = content.replace(
    'render(); sum(); cost();',
    'render(); sum(); var firstP = document.querySelector("#obPicks .pick"); if(firstP) firstP.click();'
)

# 3. Update Leaderboard: Clans -> Clubs, View other user clubs, Invest & Stake
content = content.replace('.lb2-clans{', '.lb2-clubs{')
content = content.replace('.lb2-clan{', '.lb2-club{')
content = content.replace('.lb2-clan-top', '.lb2-club-top')
content = content.replace('.lb2-clan-mark', '.lb2-club-mark')
content = content.replace('.lb2-clan b{', '.lb2-club b{')
content = content.replace('.lb2-clan small{', '.lb2-club small{')
content = content.replace('.lb2-clan strong{', '.lb2-club strong{')
content = content.replace('.lb2-clan{flex-basis:200px}', '.lb2-club{flex-basis:200px}')
content = content.replace('.lb2-clans{margin-left:-16px', '.lb2-clubs{margin-left:-16px')

# Add interactive styles for .lb2-club and .lb2-row
content = content.replace(
    '.lb2-club{flex:0 0 182px;background:var(--panel);border:1px solid var(--hair);border-radius:17px;padding:14px;text-decoration:none;color:#fff}',
    '.lb2-club{flex:0 0 182px;background:var(--panel);border:1px solid var(--hair);border-radius:17px;padding:14px;text-decoration:none;color:#fff;cursor:pointer;transition:transform .2s,border-color .2s,background .2s;text-align:left;border:1px solid rgba(255,255,255,.08)}\n.lb2-club:hover{border-color:rgba(24,0,173,.5);transform:translateY(-2px);background:rgba(255,255,255,.05)}'
)
content = content.replace(
    '.lb2-row{display:grid;grid-template-columns:34px 48px minmax(0,1fr) auto;gap:10px;align-items:center;padding:13px 0;border-bottom:1px solid rgba(255,255,255,.045)}',
    '.lb2-row{display:grid;grid-template-columns:34px 48px minmax(0,1fr) auto;gap:10px;align-items:center;padding:13px 8px;border-bottom:1px solid rgba(255,255,255,.045);cursor:pointer;transition:background .2s,border-radius .2s;border-radius:12px}\n.lb2-row:hover{background:rgba(255,255,255,.04)}'
)

# Replace "Clans" section in lb2 HTML
old_lb2_clans = '''       '<div class="lb2-section-head"><h2>Clans <span>New</span></h2><a href="divisions.html">View all ›</a></div>'
       '<div class="lb2-clans">'
       '<a class="lb2-clan" href="clubs.html"><div class="lb2-clan-top"><span class="lb2-clan-mark">RMO</span></div><b>Risk On</b><small>🏆 4 members</small><strong>+3,497,855 $FTR</strong></a>'
       '<a class="lb2-clan" href="clubs.html"><div class="lb2-clan-top"><span class="lb2-clan-mark"><img src="assets/players/mbappe.webp" alt=""></span></div><b>Apex Eleven</b><small>⚽ 20 members</small><strong>+1,853,334 $FTR</strong></a>'
       '<a class="lb2-clan" href="clubs.html"><div class="lb2-clan-top"><span class="lb2-clan-mark"><img src="assets/players/saka.webp" alt=""></span></div><b>North Bank</b><small>🔥 23 members</small><strong>+1,800,986 $FTR</strong></a>'
       '</div>'''

new_lb2_clans = '''       '<div class="lb2-section-head"><h2>Clubs <span>New</span></h2><a href="divisions.html">View all ›</a></div>'
       '<div class="lb2-clubs">'
       '<div class="lb2-club" role="button" tabindex="0" data-club-name="Risk On"><div class="lb2-club-top"><span class="lb2-club-mark">RMO</span></div><b>Risk On</b><small>🏆 4 members</small><strong>+3,497,855 $FTR</strong></div>'
       '<div class="lb2-club" role="button" tabindex="0" data-club-name="Apex Eleven"><div class="lb2-club-top"><span class="lb2-club-mark"><img src="assets/players/mbappe.webp" alt=""></span></div><b>Apex Eleven</b><small>⚽ 20 members</small><strong>+1,853,334 $FTR</strong></div>'
       '<div class="lb2-club" role="button" tabindex="0" data-club-name="North Bank"><div class="lb2-club-top"><span class="lb2-club-mark"><img src="assets/players/saka.webp" alt=""></span></div><b>North Bank</b><small>🔥 23 members</small><strong>+1,800,986 $FTR</strong></div>'
       '</div>'''

content = content.replace(old_lb2_clans, new_lb2_clans)

# Add data-club-name to lb2-row
old_lb2_row = "lb2[-1] = '<div class=\"lb2-row\">' + lb2[-1] + '</div>'"
new_lb2_row = "lb2[-1] = ('<div class=\"lb2-row\" role=\"button\" tabindex=\"0\" data-club-name=\"%s\">' % club) + lb2[-1] + '</div>'"
content = content.replace(old_lb2_row, new_lb2_row)

# Update LB2_JS to handle club info and staking modal
old_lb2_js = '''LB2_JS = r"""
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
"""'''

new_lb2_js = '''LB2_JS = ("var BOARD_DATA=[" + LB_ROWS + "];") + r"""
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
function initials(n){ return (n || 'FC').split(/\\s+/).map(function(w){ return w.charAt(0).toUpperCase(); }).join('').slice(0, 3); }

function openClubModal(clubName){
  var b = BOARD_DATA.filter(function(x){ return x.c.toLowerCase() === clubName.toLowerCase(); })[0];
  if(!b){
    if(clubName === "Risk On") b = { c: "Risk On", m: "Marcus Vance", r: 1, v: 3497855, fp: 812, b: 18.5, h: 4, co: "$Arteta · 4-3-3 High press", xi: ["Haaland", "Saka", "Mbappe"], cl: "#1800ad" };
    else if(clubName === "Apex Eleven") b = { c: "Apex Eleven", m: "Elena Rostova", r: 2, v: 1853334, fp: 786, b: 16.0, h: 20, co: "$Pep · 3-5-2 Possession", xi: ["Bellingham", "Rodri", "Vinicius"], cl: "#FF6A1F" };
    else if(clubName === "North Bank") b = { c: "North Bank", m: "David K.", r: 3, v: 1800986, fp: 754, b: 15.2, h: 23, co: "$Arteta · 4-3-3 Overload", xi: ["Saka", "Odegaard", "Saliba"], cl: "#FF3B47" };
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
});
"""'''

content = content.replace(old_lb2_js, new_lb2_js)

p3_path.write_text(content, encoding="utf-8")
print("Successfully patched tools/pages3.py!")
