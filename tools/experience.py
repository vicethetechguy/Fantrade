"""Focused product screens and shared responsive styling for the HTML generators."""

CSS = r"""
:root{--dim:#adb4ae;--faint:#949e96;--hair:rgba(255,255,255,.12);--r-out:18px;--r-in:14px}
body{background:#0c100e;line-height:1.6}
.ux-page ~ .orb, .ux-page ~ .grain{display:none}
.ux-page h1, .ux-page h2, .ux-page h3, .ux-page h4{font-variation-settings:'wdth' 100,'wght' 700;text-transform:none;line-height:1.14;letter-spacing:-.025em}
.phead{padding:130px 0 24px}.phead h1{font-size:clamp(32px,4vw,48px);margin:12px 0}.phead .lede{max-width:650px;font-size:16px;margin:12px 0 0}
.ux-page section{padding:32px 0}.sec-head{margin-bottom:24px}
.ux-page .bezel{box-shadow:none;background:transparent;border:1px solid var(--hair);padding:0}.ux-page .core{background:#121814;box-shadow:none}
.pad{padding:26px}.pad-sm{padding:22px}.bento>*{min-width:0}.statbar{margin-top:20px}
.ux-page .btn{min-height:44px;text-transform:none;letter-spacing:0;font-family:Montserrat,system-ui,sans-serif;font-weight:600;font-size:13px;transition:background .15s;border-radius:12px;padding:11px 18px;justify-content:center;white-space:normal;box-shadow:none}
.ux-page .btn .cap{display:none}.ux-page .btn:hover{transform:none}.ux-page .btn[disabled]{opacity:.45;cursor:not-allowed}
.nav-island .btn{white-space:nowrap!important}
.nav-actions{display:flex;align-items:center;gap:10px}
.nav-links{gap:20px}.nav-links a{padding:10px 0}.nav-wallet .pulse{display:none}.nav-wallet{white-space:nowrap}
.overlay a{font-family:Montserrat,sans-serif;text-transform:none}.overlay{visibility:hidden;background:#0c100e!important}.menu-open .overlay{visibility:visible;opacity:1!important;background:#0c100e!important}
.overlay .btn{font-size:14px!important;font-family:Montserrat,system-ui,sans-serif!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:.08em!important;min-height:48px!important;border-radius:999px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;width:100%!important;margin-top:12px!important}
.seg button,.tradebtn,.quick button{min-height:44px;letter-spacing:0;text-transform:none}.field input{min-width:0}.searchbox input{width:100%;min-width:0}
[data-reveal]{opacity:1!important;transform:none!important;filter:none!important;transition:none!important}
.logo{font-family:Montserrat,system-ui,sans-serif}
.ux-steps,.ux-details,section[id]{scroll-margin-top:110px}
.ux-exchange .ticket>.seg{margin-top:4px}
.ux-exchange .ticket .line b{font-size:13px}
.skip-link{position:fixed;left:16px;top:-100px;z-index:200;background:var(--lime);color:#111;padding:12px}.skip-link:focus{top:12px}
.ux-page{padding:126px 0 56px}.ux-heading{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:28px}.ux-heading h1{font-size:clamp(32px,4vw,46px);margin:8px 0 12px}.ux-heading p{color:var(--dim);max-width:650px;margin:0}.eyebrow{font-size:12px;font-weight:600;color:var(--lime);letter-spacing:.05em}
.ux-card{background:#141b17;border:1px solid var(--hair);border-radius:18px;padding:26px;min-width:0}.ux-card h2{font-size:23px;margin-bottom:12px}.ux-card h3{font-size:18px;margin-bottom:10px}.ux-card p{color:var(--dim)}
.ux-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:20px 0}.ux-two{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(280px,1fr);gap:24px;align-items:start}.ux-stack{display:grid;gap:20px}.ux-row{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}.ux-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}
.ux-note{font-size:13px;color:var(--dim);line-height:1.6}.ux-banner{padding:16px 20px;border:1px solid #415135;background:#1b2519;border-radius:12px;margin-bottom:24px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}.ux-banner a,.ux-success a{display:inline-flex;align-items:center;justify-content:center;min-height:34px;padding:7px 16px;border:0;border-radius:999px;background:#1800ad;color:#fff;font-size:12px;font-weight:600;text-decoration:none;white-space:nowrap}.ux-banner a:hover,.ux-success a:hover{background:#3311cc;color:#fff}.ux-number{width:32px;height:32px;display:grid;place-items:center;border-radius:50%;background:#293c1a;color:var(--lime);font-weight:700;margin-bottom:16px}
.ux-value{font-size:30px;font-family:'Montserrat', sans-serif;overflow-wrap:anywhere;margin:8px 0}.ux-metric p{margin:0}.ux-list{padding:0;list-style:none;margin:0}.ux-list li{padding:16px 0;border-bottom:1px solid var(--hair)}.ux-list li:last-child{border:0}.ux-list small{display:block;color:var(--dim);margin-top:4px}
.ux-steps{display:flex;gap:8px;list-style:none;padding:0;margin:0 0 24px}.ux-steps li{flex:1;padding:12px;border-bottom:2px solid var(--hair);color:var(--dim);font-size:13px}.ux-steps li[aria-current=step]{border-color:var(--lime);color:var(--lime)}
.ux-choice{display:block;width:100%;border:1px solid var(--hair);border-radius:12px;padding:16px;margin:12px 0;background:#111713;color:var(--ink);text-align:left;cursor:pointer;min-height:64px;font-size:15px}.ux-choice[aria-pressed=true]{border-color:var(--lime);background:#233019}.ux-choice small{display:block;color:var(--dim);margin-top:4px;font-size:13px}
.ux-label{display:block;margin:20px 0 8px;font-weight:600;font-size:14px}.ux-select{width:100%;border:1px solid var(--hair);border-radius:10px;background:#0c100e;color:var(--ink);padding:14px;font-size:16px}.ux-error{color:#ff9d9d;margin:12px 0}.ux-success{border:1px solid var(--lime);border-radius:14px;padding:20px;margin-top:20px}
.ux-details{border:1px solid var(--hair);border-radius:14px;padding:18px 20px;margin:20px 0}.ux-details summary{cursor:pointer;font-weight:600;min-height:28px}.ux-details p{margin:14px 0 0;color:var(--dim)}.ux-details table{width:100%;border-collapse:collapse;margin-top:16px;font-size:13px}.ux-details th,.ux-details td{text-align:left;padding:10px 6px;border-bottom:1px solid var(--hair)}
.ux-footer{padding:26px 0 90px;border-top:1px solid var(--hair);color:var(--dim);font-size:12px}.ux-footer .wrap{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}.ux-footer a{margin-right:16px}.mobile-tabs{display:none}
.ux-exchange .mhead,.ux-exchange .mrow{grid-template-columns:minmax(140px,1.6fr) 90px 72px 70px;gap:12px;padding:16px}.ux-exchange .mhead span:nth-child(4),.ux-exchange .mhead span:nth-child(5),.ux-exchange .mrow>div:nth-child(4),.ux-exchange .mrow>div:nth-child(5){display:none}.ux-exchange .ticket{position:sticky;top:110px;scroll-margin-top:110px}.ux-exchange .ticket .line{gap:12px;flex-wrap:wrap}.ux-exchange .rail .searchbox{flex:1}.ux-exchange .t-nm{white-space:normal}.ux-exchange .statbar{display:none}
@media(min-width:1001px){.ux-exchange .c8{grid-column:span 8}.ux-exchange .c4{grid-column:span 4}}
@media(max-width:1100px){.nav-links{gap:13px}.nav-wallet{display:none}.ux-exchange .c8,.ux-exchange .c4{grid-column:span 12}}
@media(max-width:1024px){.nav-links{display:none!important}.burger{display:block!important}}
@media(max-width:900px){.burger{display:block}.ux-two{grid-template-columns:1fr}.ux-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.ux-grid>:last-child:nth-child(odd){grid-column:1/-1}}
@media(max-width:768px){
  .wrap{padding-left:20px;padding-right:20px}
  .nav-island{top:10px!important;left:12px!important;right:12px!important;width:auto!important;max-width:calc(100vw - 24px)!important;padding:6px 8px 6px 14px!important;display:flex!important;justify-content:space-between!important;align-items:center!important;box-sizing:border-box!important}
  .nav-island .logo{font-size:14px!important;gap:8px!important;flex:none!important}
  .nav-actions,.nav-island div[style*="display:flex"]{display:none!important}
  .nav-wallet{display:none!important}
  .burger{width:40px!important;height:40px!important;display:block!important;flex:none!important}
  .phead{padding:106px 0 16px}.phead h1{font-size:34px}.phead .lede{font-size:15px}
  .ux-page{padding:92px 0 44px!important}
  .ux-heading{align-items:flex-start;flex-direction:column;gap:14px}
  .ux-heading h1{font-size:clamp(24px, 7.5vw, 36px)!important;line-height:1.15!important;overflow-wrap:break-word!important;word-break:break-word!important}
  .ux-heading p{font-size:14px!important;line-height:1.55!important}
  .ux-card{padding:20px}.ux-grid{grid-template-columns:1fr}.ux-heading .btn{min-height:40px}.ux-two{gap:18px}.ux-value{font-size:27px}.ux-steps li{padding:10px 4px;font-size:12px}.ux-footer{padding-bottom:105px}.ux-actions .btn{flex:1}.ux-actions{gap:10px}
  .ux-exchange .mhead,.ux-exchange .mrow{grid-template-columns:minmax(95px,1fr) 68px 58px;gap:8px;padding:14px 12px}
  .ux-exchange .mhead span:nth-child(3),.ux-exchange .mrow>div:nth-child(3){display:none}
  .ux-exchange .mhead span:nth-child(6),.ux-exchange .mrow>div:nth-child(6){display:block}
  .ux-exchange .mrow .badge{display:none}.ux-exchange .tradebtn{width:58px;padding:8px 6px}.ux-exchange .rail .searchbox{flex-basis:100%;order:-1}.ux-exchange .ticket{position:static}.ux-exchange .rail{gap:12px}.ux-exchange .ticket .field input{width:60%}
  .mobile-tabs{display:flex;position:fixed;bottom:0;left:0;right:0;z-index:65;background:#141b17;border-top:1px solid var(--hair);padding:8px 8px max(8px,env(safe-area-inset-bottom));justify-content:space-around}
  .mobile-tabs a{font-size:10px;display:flex;align-items:center;flex-direction:column;gap:4px;min-height:44px;min-width:52px;color:var(--dim)}
  .mobile-tabs a[aria-current=page]{color:var(--lime)}.mobile-tabs svg{width:20px;height:20px}
  body{padding-bottom:64px}.overlay{padding-bottom:100px}.btn,.tradebtn{min-height:44px}.pad{padding:20px}.b-row,.line{gap:12px}.b-row b,.line b{overflow-wrap:anywhere;text-align:right}.ux-details{padding:16px}.ux-exchange .mhead{font-size:10px;letter-spacing:0}.ux-exchange .tick{font-size:12px}
}
"""

def heading(title, description, label="Fantrade", action=True):
    return ('<div class="ux-heading"><div><span class="eyebrow">'+label+'</span><h1>'+title+'</h1><p>'+description+'</p></div>'+
            ('<a class="btn btn-glass" href="how-it-works.html">How to play</a>' if action else '')+'</div>')

def guide_cards():
    steps = [('1','Buy your first shares','Find a player in the Exchange. Choose a quantity and review the cost before buying.','exchange.html','Browse players'),
             ('2','Choose how to play','Enter one player you own, or build a Dream Club to enter a whole squad.','clubs.html#builder','Build a club'),
             ('3','Enter FanPlay','Choose a scoring tier, review the 2,500 $FTR stake, then confirm your entry.','fanplay.html','Play FanPlay')]
    return '<div class="ux-grid">'+''.join('<article class="ux-card"><span class="ux-number">'+n+'</span><h2>'+t+'</h2><p>'+d+'</p><a class="btn btn-glass" href="'+url+'">'+cta+'</a></article>' for n,t,d,url,cta in steps)+'</div>'

GUIDE = '<main class="ux-page" id="main"><div class="wrap">'+heading('Your first matchday, made simple.','Buy shares → choose your entry → play FanPlay. Start with one player; building a club is optional.','The Fantrade guide',False)+ '<div class="ux-banner"><span>Try the demo with an illustrative $FTR balance. No real money is used.</span><a href="signup.html">Create a demo account</a></div>'+guide_cards()+'''
<div class="ux-two"><article class="ux-card"><h2>How to enter FanPlay</h2><ol class="ux-list">
<li><b>Choose a player or Dream Club.</b><small>Individual mode only needs shares in one player. Club mode needs 11 owned starters and an owned coach.</small></li>
<li><b>Choose a scoring tier.</b><small>Simple is the easiest starting point: goals, assists and clean sheets. Other tiers count more events and can subtract more points.</small></li>
<li><b>Review your entry.</b><small>Check your selection, tier and 2,500 $FTR stake. The stake is deducted only when you confirm.</small></li>
<li><b>Follow your entry.</b><small>Your active entry appears on FanPlay and your dashboard. In the full product, match performances determine points and settlement; this demo does not settle live matches.</small></li></ol><div class="ux-actions"><a class="btn btn-lime" href="fanplay.html">Try FanPlay</a></div></article>
<aside class="ux-stack"><article class="ux-card"><h2>A few useful words</h2><ul class="ux-list"><li><b>$FTR</b><small>The balance used to buy shares and enter FanPlay.</small></li><li><b>Shares</b><small>Your holdings in a player or coach. Owning shares makes them eligible for your entry.</small></li><li><b>FP · Fantrade Points</b><small>A score for football performance. Points are different from your wallet balance.</small></li><li><b>Stake</b><small>The amount committed when you confirm a FanPlay entry.</small></li></ul></article></aside></div>
<details class="ux-details"><summary>Do I need a whole club to start?</summary><p>No. Buy shares in one player, choose Individual on FanPlay and select that player. You can build a club later.</p></details>
<details class="ux-details"><summary>Where do I find my shares and balance?</summary><p>Portfolio shows your holdings and transaction history. Wallet shows available $FTR and the demo funding controls.</p><div class="ux-actions"><a class="btn btn-glass" href="portfolio.html">Portfolio</a><a class="btn btn-glass" href="ftr.html">Wallet</a></div></details>
<details class="ux-details"><summary>Are points or rewards guaranteed?</summary><p>No. Higher tiers have larger multipliers and more ways to lose points. The demo uses example data and does not predict a return or process real payments.</p></details></div></main>'''

DASHBOARD = '<main class="ux-page" id="main"><div class="wrap">'+heading('Your Fantrade home','Your balance, your next step, and your active entries.','Overview')+'''
<div class="ux-banner"><div><b id="nextTitle">Ready for your next matchday?</b><div class="ux-note" id="nextNote">Choose an entry in FanPlay.</div></div><a id="nextLink" href="fanplay.html">Continue to FanPlay →</a></div>
<div class="ux-grid"><article class="ux-card ux-metric"><p>Available balance</p><div class="ux-value"><span data-bind="balance"></span></div><p>$FTR · <a href="ftr.html">Open wallet →</a></p></article><article class="ux-card ux-metric"><p>Shares value</p><div class="ux-value"><span data-bind="assets"></span></div><p>$FTR · <a href="portfolio.html">View portfolio →</a></p></article><article class="ux-card ux-metric"><p>Active entries</p><div class="ux-value" id="homeCount">0</div><p><a href="fanplay.html#entries">View FanPlay →</a></p></article></div>
<div class="ux-two"><article class="ux-card"><div class="ux-row"><h2>Your entries</h2><a href="fanplay.html">New entry →</a></div><ul class="ux-list" id="homeEntries"></ul></article><article class="ux-card"><h2>Your Dream Club</h2><p><b data-bind="club"></b></p><p>Manage your identity and formation, then enter your squad in FanPlay.</p><a class="btn btn-glass" href="clubs.html">Manage club</a></article></div>
<details class="ux-details"><summary>New to Fantrade? Start here</summary>'''+guide_cards()+'''<a href="how-it-works.html">Read the full guide →</a></details></div></main>'''

DASH_JS = r"""
function homeRender(){var s=FT.getState();FT.syncUI();document.getElementById('homeCount').textContent=s.fanplay.activeEntries.length;renderEntries('homeEntries');
var owned=Object.keys(s.holdings).some(function(k){return s.holdings[k].shares>0&&!s.holdings[k].c;});
if(!owned){document.getElementById('nextTitle').textContent='Start with a player you believe in';document.getElementById('nextNote').textContent='Buy your first player shares to unlock Individual FanPlay.';var a=document.getElementById('nextLink');a.href='exchange.html';a.textContent='Find a player →';}}
homeRender();window.addEventListener('fantrade:statechange',homeRender);
"""

SHARED_JS = r"""
function uxEscape(v){var el=document.createElement('span');el.textContent=String(v==null?'':v);return el.innerHTML;}
function renderEntries(id){var el=document.getElementById(id);if(!el)return;var entries=FT.getState().fanplay.activeEntries;el.innerHTML=entries.length?entries.map(function(e){return '<li><div class="ux-row"><b>'+uxEscape(e.target)+'</b><span>'+uxEscape(e.tier)+'</span></div><small>'+uxEscape(e.status)+' · '+Number(e.stake).toLocaleString()+' $FTR committed</small></li>';}).join(''):'<li>No active entries yet. Choose a player to get started.</li>';}
document.querySelectorAll('.nav-links a').forEach(function(a){if(a.pathname===location.pathname){a.classList.add('on');a.setAttribute('aria-current','page');}});
var navLogo=document.querySelector('.nav-island .logo');if(navLogo&&document.querySelector('.mobile-tabs'))navLogo.href='dashboard.html';
document.querySelectorAll('input:not([aria-label]):not([id])').forEach(function(el){if(el.placeholder)el.setAttribute('aria-label',el.placeholder);});
document.querySelectorAll('.field label').forEach(function(l){var i=l.parentElement.querySelector('input,select');if(i){if(!i.id)i.id='field-'+Array.from(document.querySelectorAll('input,select')).indexOf(i);l.htmlFor=i.id;}});
"""

FANPLAY = '<main class="ux-page" id="main"><div class="wrap">'+heading('Play your next matchday','Choose who to enter, pick a scoring tier, and review before you commit.','FanPlay · demo round')+'''
<div class="ux-two"><div><ol class="ux-steps" aria-label="Entry progress"><li aria-current="step">1 · Choose entry</li><li>2 · Scoring tier</li><li>3 · Review</li></ol>
<div class="ux-card" id="entryWizard"><div id="fpStep1"><h2>Who would you like to enter?</h2><p>Start with one player, or use your Dream Club.</p>
<button class="ux-choice" data-mode="solo" aria-pressed="true"><b>Individual</b><small>One player you own · easiest way to start</small></button><button class="ux-choice" data-mode="club" aria-pressed="false"><b>Dream Club</b><small>Your owned starting XI and coach</small></button>
<div id="playerField"><label class="ux-label" for="entryPlayer">Choose your player</label><select class="ux-select" id="entryPlayer"></select></div><p class="ux-note" id="ownershipNote"></p><div class="ux-actions"><a class="btn btn-glass" href="exchange.html">Buy shares</a><button class="btn btn-lime" id="fpNext1">Choose tier →</button></div></div>
<div id="fpStep2" hidden><h2>Choose your scoring tier</h2><p>Simple is a good place to learn. Higher tiers count more events and penalties.</p><div id="basicTiers"></div><details class="ux-details"><summary>More scoring tiers</summary><div id="advancedTiers"></div></details><div class="ux-actions"><button class="btn btn-glass" data-back="1">Back</button><button class="btn btn-lime" id="fpNext2">Review entry →</button></div></div>
<div id="fpStep3" hidden><h2>Review your entry</h2><p>Your balance changes only after you confirm.</p><ul class="ux-list" id="entryReview"></ul><p class="ux-note">This demo commits 2,500 $FTR from your available balance. Example points are not a promised payout.</p><p class="ux-error" id="entryError" role="alert"></p><div class="ux-actions"><button class="btn btn-glass" data-back="2">Back</button><button class="btn btn-lime" id="confirmEntry">Confirm · 2,500 $FTR</button></div></div>
<div id="entrySuccess" hidden class="ux-success" role="status"><h2>You’re in!</h2><p id="successText"></p><p>Your entry is saved below. You can also find it on your dashboard.</p><div class="ux-actions"><a class="btn btn-lime" href="dashboard.html">Go to dashboard</a><button class="btn btn-glass" id="anotherEntry">Create another entry</button></div></div></div></div>
<aside class="ux-stack"><article class="ux-card"><h2>Before you play</h2><ul class="ux-list"><li><b>Own your selection</b><small>Individual: shares in one player. Dream Club: 11 starters and a coach.</small></li><li><b>Entry stake: 2,500 $FTR</b><small>Available: <span data-bind="balance"></span> $FTR. <a href="ftr.html">Open wallet →</a></small></li><li><b>Follow your entry</b><small>Football events earn or lose points according to your tier. This prototype uses demo data; live settlement is not connected.</small></li></ul></article><a class="btn btn-glass" href="how-it-works.html">Read the step-by-step guide</a></aside></div>
<section id="entries"><div class="ux-card"><h2>Your active entries</h2><ul class="ux-list" id="fanplayEntries"></ul></div></section>
<details class="ux-details" id="rules"><summary>How scoring works</summary><p>FP means Fantrade Points. Here are example outfield scoring values; position and coach scoring may differ.</p><table><thead><tr><th>Event</th><th>Simple</th><th>Elite</th><th>Viynx Max</th></tr></thead><tbody><tr><td>Goal</td><td>6</td><td>4</td><td>9</td></tr><tr><td>Assist</td><td>4</td><td>3</td><td>6</td></tr><tr><td>Clean sheet</td><td>5</td><td>1</td><td>7</td></tr><tr><td>Yellow card</td><td>−1</td><td>−1</td><td>−3</td></tr><tr><td>Big chance missed</td><td>—</td><td>−2</td><td>−4</td></tr></tbody></table></details>
<details class="ux-details" id="tiers"><summary>What do the tiers mean?</summary><p>Simple ×1: core football events. PRO ×1.4: adds key passes and duels. Elite ×2: wider, position-weighted scoring. Killer ×3: stronger penalties. Viynx Move ×4.5: momentum scoring. Viynx Max ×7: the largest multiplier and penalties. Multipliers apply to points, not a guaranteed cash return.</p></details></div></main>'''

FP_JS = r"""
var entryMode='solo',entryTier='Simple',entryMult=1,entryStage=1,entryBusy=false;
var tierData=[['Simple',1,'Core events · recommended for your first entry'],['PRO',1.4,'Adds key passes and duels'],['Elite',2,'More events with position weighting'],['Killer',3,'Stronger penalties for cards, misses and errors'],['Viynx Move',4.5,'Momentum scoring with larger swings'],['Viynx Max',7,'Largest multiplier and penalties']];
function eligiblePlayers(){var s=FT.getState();return Object.keys(s.holdings).filter(function(k){return s.holdings[k].shares>0&&!s.holdings[k].c;});}
function clubReady(){var s=FT.getState();return Object.keys(s.holdings).filter(function(k){var h=s.holdings[k];return h.shares>0&&!h.c&&h.inClub&&h.inClub!=='BENCH'&&h.inClub!=='SUB';}).length>=11&&s.holdings[s.club.coach]&&s.holdings[s.club.coach].shares>0;}
function entryEligible(){return entryMode==='solo'?eligiblePlayers().includes(document.getElementById('entryPlayer').value):clubReady();}
function selectionName(){return entryMode==='club'?FT.getState().club.name:document.getElementById('entryPlayer').value;}
function syncSelection(){var s=FT.getState(),select=document.getElementById('entryPlayer'),previous=select.value;select.innerHTML=eligiblePlayers().map(function(k){return '<option value="'+uxEscape(k)+'">'+uxEscape(s.holdings[k].n)+' · '+uxEscape(k)+'</option>';}).join('')||'<option value="">No player shares yet</option>';if(eligiblePlayers().includes(previous))select.value=previous;document.getElementById('playerField').hidden=entryMode==='club';document.getElementById('ownershipNote').textContent=entryMode==='solo'?(eligiblePlayers().length?'Only players you own are shown.':'Buy shares in a player to start.'):clubReady()?'Your club has 11 owned starters and an owned coach.':'Club entry needs 11 owned starters and an owned coach. Start with Individual mode or manage your club.';document.getElementById('fpNext1').disabled=!entryEligible();renderEntries('fanplayEntries');FT.syncUI();}
function goStep(n){entryStage=n;[1,2,3].forEach(function(i){document.getElementById('fpStep'+i).hidden=i!==n;var li=document.querySelectorAll('.ux-steps li')[i-1];if(i===n)li.setAttribute('aria-current','step');else li.removeAttribute('aria-current');});if(n===3){document.getElementById('entryError').textContent='';document.getElementById('entryReview').innerHTML=[['Entry',selectionName()],['Mode',entryMode==='solo'?'Individual':'Dream Club'],['Scoring tier',entryTier+' · ×'+entryMult],['Stake','2,500 $FTR'],['Balance after entry',(FT.getState().wallet.balance-2500).toLocaleString()+' $FTR']].map(function(r){return '<li class="ux-row"><span>'+r[0]+'</span><b>'+uxEscape(r[1])+'</b></li>';}).join('');}var h=document.querySelector('#fpStep'+n+' h2');h.tabIndex=-1;h.focus();}
document.querySelectorAll('[data-mode]').forEach(function(b){b.addEventListener('click',function(){entryMode=b.dataset.mode;document.querySelectorAll('[data-mode]').forEach(function(x){x.setAttribute('aria-pressed',String(x===b));});syncSelection();});});
tierData.forEach(function(t,i){var b=document.createElement('button');b.className='ux-choice';b.setAttribute('aria-pressed',String(i===0));b.innerHTML='<b>'+t[0]+' · ×'+t[1]+'</b><small>'+t[2]+'</small>';b.addEventListener('click',function(){entryTier=t[0];entryMult=t[1];document.querySelectorAll('#basicTiers button,#advancedTiers button').forEach(function(x){x.setAttribute('aria-pressed',String(x===b));});});document.getElementById(i<3?'basicTiers':'advancedTiers').appendChild(b);});
document.getElementById('entryPlayer').addEventListener('change',function(){document.getElementById('fpNext1').disabled=!entryEligible();});
document.getElementById('fpNext1').onclick=function(){if(entryEligible())goStep(2);};document.getElementById('fpNext2').onclick=function(){goStep(3);};document.querySelectorAll('[data-back]').forEach(function(b){b.onclick=function(){goStep(+b.dataset.back);};});
document.getElementById('confirmEntry').onclick=function(){if(entryBusy)return;entryBusy=true;this.disabled=true;try{if(!entryEligible())throw new Error('Your selection is no longer eligible. Go back and choose an owned player.');var target=selectionName();FT.activateFanPlayEntry({mode:entryMode,target:target,tier:entryTier,mult:entryMult,stake:2500,projectedFP:Math.round(100*entryMult*(entryMode==='club'?1.15:1))});document.getElementById('fpStep3').hidden=true;document.getElementById('entrySuccess').hidden=false;document.getElementById('successText').textContent=target+' · '+entryTier+' · 2,500 $FTR committed.';document.querySelectorAll('.ux-steps li').forEach(function(li){li.removeAttribute('aria-current');});renderEntries('fanplayEntries');}catch(e){document.getElementById('entryError').textContent=e.message;entryBusy=false;this.disabled=false;}};
document.getElementById('anotherEntry').onclick=function(){entryBusy=false;document.getElementById('confirmEntry').disabled=false;document.getElementById('entrySuccess').hidden=true;syncSelection();goStep(1);};
syncSelection();window.addEventListener('fantrade:statechange',syncSelection);if(location.hash==='#rules'||location.hash==='#tiers')document.querySelector(location.hash).open=true;
"""

LANDING = '<main class="ux-page" id="main"><div class="wrap">'+heading('Football knowledge. Your team.','Buy shares in players and coaches, build a Dream Club, and put your football knowledge to work in FanPlay.','Welcome to Fantrade',False)+'''<div class="ux-actions"><a class="btn btn-lime" href="signup.html">Get started</a><a class="btn btn-glass" href="how-it-works.html">See how it works</a></div><p class="ux-note" style="margin-top:16px">Interactive demo · illustrative balances and match data</p>'''+guide_cards()+'''<article class="ux-card"><div class="ux-row"><div><h2>One player is enough to begin.</h2><p>Learn with Individual FanPlay. Build a full club when you’re ready.</p></div><a class="btn btn-lime" href="exchange.html">Explore the Exchange</a></div></article></div></main>'''

def prepare(fname, body, js):
    screens = {'how-it-works.html':(GUIDE,''), 'dashboard.html':(DASHBOARD,DASH_JS), 'fanplay.html':(FANPLAY,FP_JS)}
    body, js = screens.get(fname,(body,js))
    if fname == 'exchange.html':
        body='<div class="ux-exchange">'+body+'</div>'
    if '<main' in body and 'id="main"' not in body:
        body=body.replace('<main', '<main id="main"',1)
    return body, SHARED_JS+js
