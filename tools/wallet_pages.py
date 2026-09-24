"""Wallet workflows using the same open layout as onboarding."""
import json
from common import ic, qr_svg, QR_ADDRESS


def intro(title, description):
    return ('<a class="back-btn" href="ftr.html" aria-label="Back to wallet">Back</a>'
            '<header class="utility-intro"><div><h1>' + title + '</h1><p>' + description + '</p></div></header>')


REVIEW = '''<dialog class="wallet-review" id="walletReview" aria-labelledby="reviewTitle">
<div class="rv-head"><span class="rv-badge" id="reviewIcon" aria-hidden="true"></span>
<div><p class="rv-eyebrow" id="reviewKind">Review</p><h2 id="reviewTitle">Review transfer</h2></div></div>
<div class="rv-hero"><span class="rv-hero-label" id="reviewHeroLabel"></span>
<div class="rv-amount"><b id="reviewAmount"></b> <small id="reviewUnit"></small></div><p class="rv-sub" id="reviewSub"></p></div>
<dl class="rv-rows" id="reviewRows"></dl>
<p class="rv-note" id="reviewText"></p>
<div class="rv-actions"><button class="app-primary" id="reviewConfirm" type="button">Confirm</button>
<button class="wallet-button" id="reviewCancel" type="button">Go back</button></div></dialog>'''


def workflow(title, description, content, review=True):
    return ('<main><div class="utility-page wallet-workflow">' + intro(title, description)
            + '<div class="utility-form">' + content + (REVIEW if review else '') + '</div></div></main>')


BALANCE = '<p class="wallet-available">Available balance<strong><span id="wBal"></span> <small>$FTR</small></strong></p>'
STATUS = '<p class="wallet-status" id="walletStatus" role="status" aria-live="polite"></p>'
DEMO = '<p class="wallet-note">Demo wallet. Transactions update your preview balance; no real funds move.</p>'

SEND_HTML = workflow('Send $FTR', 'Move funds to another manager or wallet.', BALANCE + '''
<form id="sendForm"><div class="wallet-field"><label for="sendTo">Recipient</label>
<input id="sendTo" autocomplete="off" placeholder="@handle or wallet address" required maxlength="100">
<small>Check the recipient before confirming your transfer.</small></div>
<div class="wallet-field"><label for="sendAmt">Amount</label><div class="wallet-amount">
<input id="sendAmt" type="number" min="0.01" step="0.01" inputmode="decimal" placeholder="0" required><span>$FTR</span></div></div>
<div class="wallet-quick"><button class="wallet-chip" type="button" data-amount="1000">1,000</button>
<button class="wallet-chip" type="button" data-amount="5000">5,000</button><button class="wallet-chip" type="button" id="sendMax">Max</button></div>
<dl class="wallet-summary"><div><dt>Transfer fee</dt><dd>Free</dd></div><div><dt>Balance after transfer</dt><dd id="sendAfter">—</dd></div></dl>
<button class="app-primary wallet-submit" type="submit">Review transfer</button></form>''' + STATUS + DEMO + '''
<section class="wallet-followup"><h2>Recent transfers</h2><div id="sendLog"></div>
<a class="utility-back" href="activity.html">View all activity</a></section>''')

RECEIVE_HTML = workflow('Receive $FTR', 'Your wallet address, ready to share.', '''
<div class="wallet-network"><b>Fantrade L2</b>Demo receive address</div><div class="wallet-qr">'''
                       + qr_svg(quiet=4) + '</div><p class="wallet-address" id="walletAddress">' + QR_ADDRESS + '''</p>
<button class="app-primary wallet-submit" type="button" id="copyAddr">Copy address</button>''' + STATUS + '''
<p class="wallet-note">This is the preview wallet address. Do not send real funds to it.</p>
<div class="wallet-actions"><a class="wallet-button" href="buy.html">Add demo funds</a><a class="wallet-button" href="activity.html">View activity</a></div>''', review=False)

SWAP_HTML = workflow('Swap players', 'Move between player and coach shares in one step.', '''
<form id="swapForm"><div class="wallet-field"><span class="wallet-label" id="swapFromLabel">From your portfolio</span>
<select id="swapFrom" hidden tabindex="-1" aria-hidden="true"></select>
<button type="button" class="swap-pick" id="swapFromBtn" data-pick="from" aria-haspopup="dialog" aria-labelledby="swapFromLabel swapFromBtn"></button>
<div class="swap-preview" id="swapPreview"></div></div>
<div class="wallet-field"><label for="swapQty">Shares to swap</label><div class="wallet-amount">
<input id="swapQty" type="number" min="1" step="1" inputmode="numeric" placeholder="0" required><span>shares</span></div></div>
<div class="wallet-quick"><button class="wallet-chip" type="button" id="swapHalf">Half</button><button class="wallet-chip" type="button" id="swapMax">Max</button></div>
<div class="wallet-field"><span class="wallet-label" id="swapToLabel">Receive</span>
<select id="swapTo" hidden tabindex="-1" aria-hidden="true"></select>
<button type="button" class="swap-pick" id="swapToBtn" data-pick="to" aria-haspopup="dialog" aria-labelledby="swapToLabel swapToBtn"></button></div>
<span class="wallet-label">Estimated shares received</span><div class="wallet-estimate" id="swGet">—</div>
<dl class="wallet-summary"><div><dt>Swap fee · 0.4%</dt><dd id="swFee">—</dd></div><div><dt>Change returned to wallet</dt><dd id="swDust">—</dd></div></dl>
<button class="app-primary wallet-submit" type="submit" id="swapGo">Review swap</button></form>''' + STATUS + DEMO + '''
<a class="utility-back" href="portfolio.html">View your portfolio</a>
<dialog id="swapPicker" class="asset-picker" aria-labelledby="swapPickerTitle">
<div class="asset-picker-heading"><h2 id="swapPickerTitle">Choose your shares.</h2><button type="button" id="swapPickerClose" aria-label="Close player search">''' + ic('cross', 'ic') + '''</button></div>
<label for="swapSearch">Search players, coaches or clubs</label>
<input id="swapSearch" type="search" placeholder="Try Saka or Arsenal" autocomplete="off">
<p id="swapSearchStatus" class="asset-search-status" role="status"></p>
<div id="swapSearchResults" class="asset-search-results"></div></dialog>''')

BUY_HTML = workflow('Add funds', 'Try a conversion from pounds to $FTR.', BALANCE + '''
<form id="buyForm"><div class="wallet-field"><label for="fiat">Amount in pounds</label><div class="wallet-amount">
<input id="fiat" type="number" min="0.01" step="0.01" inputmode="decimal" placeholder="0" required><span>GBP</span></div></div>
<div class="wallet-quick"><button type="button" class="wallet-chip" data-gbp="100">£100</button>
<button type="button" class="wallet-chip" data-gbp="500">£500</button><button type="button" class="wallet-chip" data-gbp="1000">£1,000</button></div>
<span class="wallet-label">You receive, after fees</span><div class="wallet-estimate"><span id="buyNet">—</span> <small>$FTR</small></div>
<dl class="wallet-summary"><div><dt>Conversion rate</dt><dd id="buyRate"></dd></div><div><dt>Conversion fee · 0.5%</dt><dd id="buyFee">—</dd></div></dl>
<button class="app-primary wallet-submit" type="submit">Review demo conversion</button></form>''' + STATUS + '''
<p class="wallet-note">Demo conversion. No card is charged. The amount is added to your preview wallet.</p>''')

WITHDRAW_HTML = workflow('Withdraw to bank', 'Move $FTR out of Fantrade and into your bank account.', BALANCE + '''
<form id="withdrawForm"><div class="wallet-field"><label for="wdAmount">Amount to withdraw</label><div class="wallet-amount">
<input id="wdAmount" type="number" min="0.01" step="0.01" inputmode="decimal" placeholder="0" required><span>$FTR</span></div></div>
<div class="wallet-quick"><button class="wallet-chip" type="button" data-wd="5000">5,000</button>
<button class="wallet-chip" type="button" data-wd="25000">25,000</button><button class="wallet-chip" type="button" id="wdMax">Max</button></div>
<h2 class="wallet-section-title">Bank account</h2>
<div class="wallet-field"><span class="wallet-label" id="wdCurrencyLabel">Currency</span><select id="wdCurrency" hidden tabindex="-1" aria-hidden="true">
<option value="GBP">British pound · GBP</option><option value="NGN">Nigerian naira · NGN</option>
<option value="EUR">Euro · EUR</option><option value="USD">US dollar · USD</option></select>
<button type="button" class="swap-pick" id="wdCurrencyBtn" aria-haspopup="dialog" aria-labelledby="wdCurrencyLabel wdCurrencyBtn"></button></div>
<div class="wallet-field"><label for="wdName">Account holder name</label><input id="wdName" autocomplete="name" placeholder="As shown on your bank account" required maxlength="80"></div>
<div class="wallet-field"><label for="wdBank">Bank name</label><input id="wdBank" autocomplete="off" placeholder="e.g. Barclays" required maxlength="60"></div>
<div class="wallet-row"><div class="wallet-field"><label for="wdSort" id="wdSortLabel">Sort code</label><input id="wdSort" inputmode="numeric" autocomplete="off" placeholder="00-00-00" maxlength="11"></div>
<div class="wallet-field"><label for="wdAcct">Account number</label><input id="wdAcct" inputmode="numeric" autocomplete="off" placeholder="8 digits" required maxlength="34"></div></div>
<label class="wallet-check"><input type="checkbox" id="wdSave" checked> Save this bank account for next time</label>
<dl class="wallet-summary"><div><dt>Withdrawal fee · 0.5%, minimum 50 $FTR</dt><dd id="wdFee">—</dd></div>
<div><dt>Total deducted</dt><dd id="wdTotal">—</dd></div><div><dt>You receive</dt><dd id="wdReceive">—</dd></div>
<div><dt>Arrives</dt><dd>1–2 working days</dd></div></dl>
<button class="app-primary wallet-submit" type="submit">Review withdrawal</button></form>''' + STATUS + '''
<p class="wallet-note">Demo withdrawal. Your preview balance updates; no real money is sent and no bank details leave this browser.</p>
<section class="wallet-followup"><h2>Recent withdrawals</h2><div id="wdLog"></div></section>
<dialog id="wdCurrencyPicker" class="asset-picker" aria-labelledby="wdCurrencyPickerTitle">
<div class="asset-picker-heading"><h2 id="wdCurrencyPickerTitle">Choose currency.</h2><button type="button" id="wdCurrencyPickerClose" aria-label="Close currency picker">''' + ic('cross', 'ic') + '''</button></div>
<p id="wdCurrencyStatus" class="asset-search-status" role="status"></p>
<div id="wdCurrencyResults" class="asset-search-results"></div></dialog>''')

ACTIVITY_HTML = ('<main><div class="utility-page">' + intro('Wallet activity', 'Follow your trades, transfers and FanPlay entries.')
                 + BALANCE + '''<div class="wallet-actions"><a class="app-primary" href="buy.html">Add funds</a>
<a class="wallet-button" href="send.html">Send</a><a class="wallet-button" href="receive.html">Receive</a>
<a class="wallet-button" href="withdraw.html">Withdraw</a></div>
<div class="wallet-field"><label for="activitySearch">Search activity</label><input id="activitySearch" type="search" placeholder="Player, recipient or transaction"></div>
<div class="wallet-tabs" aria-label="Activity filters"><button class="wallet-chip" data-category="all" aria-pressed="true">All</button>
<button class="wallet-chip" data-category="trades" aria-pressed="false">Trades</button><button class="wallet-chip" data-category="transfers" aria-pressed="false">Transfers</button>
<button class="wallet-chip" data-category="fanplay" aria-pressed="false">FanPlay</button></div>
<p class="wallet-note" id="activityCount" role="status"></p><div id="activityRows"></div>''' + STATUS + '''
'''
                 + REVIEW + '</div></main>')

COMMON_JS = r'''
function el(id){return document.getElementById(id);}
function esc(v){var span=document.createElement('span');span.textContent=String(v == null?'':v);return span.innerHTML.replace(/"/g,'&quot;');}
function amount(id){var value=el(id).value.trim();return value!=='' && /^\d+(\.\d{1,2})?$/.test(value)?Number(value):NaN;}
function fmt(n){return Number(n).toLocaleString('en-US',{maximumFractionDigits:2});}
function valid(n){return Number.isFinite(n)&&n>0&&n<=Number.MAX_SAFE_INTEGER/100;}
function status(message,error){el('walletStatus').textContent=message;el('walletStatus').dataset.error=!!error;}
function syncBal(){if(el('wBal'))el('wBal').textContent=fmt(FT.getState().wallet.balance);}
syncBal();window.addEventListener('fantrade:statechange',syncBal);
var pendingAction=null;
/* One premium review card for every wallet action: what it is, the headline
   amount, every line that makes it up, and what happens next. */
function review(o,text,action){
  if(typeof o!=='object')o={title:o,rows:String(text).split('\n').map(function(l){var i=l.indexOf(':');return i>0?[l.slice(0,i),l.slice(i+1).trim()]:[l,''];}),action:action};
  el('reviewKind').textContent=o.kind||'Review';el('reviewTitle').textContent=o.title;
  el('reviewIcon').innerHTML='<svg class="ic" aria-hidden="true"><use href="#i-'+(o.icon||'receipt')+'"/></svg>';
  el('reviewHeroLabel').textContent=o.heroLabel||'';el('reviewAmount').textContent=o.amount||'';el('reviewUnit').textContent=o.unit||'';
  el('reviewSub').textContent=o.sub||'';el('reviewAmount').parentNode.parentNode.hidden=!o.amount;
  el('reviewRows').innerHTML=(o.rows||[]).map(function(r){return '<div'+(r[2]?' class="'+r[2]+'"':'')+'><dt>'+esc(r[0])+'</dt><dd>'+esc(r[1])+'</dd></div>';}).join('');
  el('reviewText').textContent=o.note||'';el('reviewText').hidden=!o.note;
  el('reviewConfirm').textContent=o.confirm||'Confirm';
  pendingAction=o.action;el('reviewConfirm').disabled=false;el('walletReview').showModal();el('reviewCancel').focus();}
if(el('walletReview')){
  el('reviewCancel').onclick=function(){pendingAction=null;el('walletReview').close();};
  el('walletReview').addEventListener('close',function(){pendingAction=null;});
  el('reviewConfirm').onclick=function(){var action=pendingAction;if(!action)return;pendingAction=null;this.disabled=true;
    try{action();}catch(error){status(error.message,true);}finally{el('walletReview').close();}};
}
var labels={BUY:'Bought shares',SELL:'Sold shares',STAKE:'FanPlay entry',PAYOUT:'FanPlay payout',SETTLE:'Settlement',CONVERT:'Added funds',DEPOSIT:'Deposit',SEND:'Transfer sent',WITHDRAW:'Withdrawal to bank',SWAP:'Swapped shares'};
function ledgerRow(t){var down=['BUY','STAKE','SEND','WITHDRAW'].includes(t.type),neutral=t.type==='SWAP';
  return '<div class="wallet-ledger-row"><span class="ledger-icon"><svg class="ic" aria-hidden="true"><use href="#i-'+(neutral?'swap':'arrow')+'"/></svg></span><div><b>'+esc(labels[t.type]||t.type)+'</b><small>'+esc(t.asset)+'</small><small>'+esc(t.time)+'</small></div><div class="ledger-amount '+(neutral?'':down?'':'positive')+'">'+(neutral?'Value ':down?'−':'+')+fmt(t.total)+' $FTR'+(neutral?'<small>No cash transfer</small>':'')+'</div></div>';
}
'''

SEND_JS = r'''
function sendCalc(){var n=amount('sendAmt'),balance=FT.getState().wallet.balance;el('sendAfter').textContent=valid(n)?(n>balance?'Insufficient balance':fmt(balance-n)+' $FTR'):'—';}
el('sendAmt').addEventListener('input',sendCalc);
document.querySelectorAll('[data-amount]').forEach(function(b){b.onclick=function(){el('sendAmt').value=b.dataset.amount;sendCalc();};});
el('sendMax').onclick=function(){el('sendAmt').value=FT.getState().wallet.balance;sendCalc();};
el('sendForm').onsubmit=function(e){e.preventDefault();var to=el('sendTo').value.trim(),n=amount('sendAmt');status('');
  if(to.length<3){status('Enter a recipient with at least 3 characters.',true);return;}
  if(!valid(n)){status('Enter a positive amount with up to two decimal places.',true);return;}
  if(n>FT.getState().wallet.balance){status('This amount is more than your available balance.',true);return;}
  var bal=FT.getState().wallet.balance;
  review({kind:'Transfer',icon:'send',title:'Review transfer',heroLabel:'You send',amount:fmt(n),unit:'$FTR',sub:'to '+to,
    rows:[['Recipient',to],['Transfer fee','Free'],['Arrives','Instantly'],['Balance now',fmt(bal)+' $FTR'],['Balance after',fmt(bal-n)+' $FTR','rv-total']],
    note:'Transfers between managers can’t be reversed. Check the recipient before you confirm.',confirm:'Send '+fmt(n)+' $FTR',action:function(){
    FT.sendFtr(n,to,'send');el('sendAmt').value='';sendCalc();status('Sent '+fmt(n)+' $FTR to '+to+'.');}});
};
function sendLog(){var rows=FT.getState().transactions.filter(t=>t.type==='SEND').slice(0,3);el('sendLog').innerHTML=rows.map(ledgerRow).join('')||'<p class="wallet-note">Your transfers will appear here after you send $FTR.</p>';sendCalc();}
sendLog();window.addEventListener('fantrade:statechange',sendLog);
'''

RECEIVE_JS = 'var WADDR=' + json.dumps(QR_ADDRESS) + r''';
el('copyAddr').onclick=async function(){
  try{await navigator.clipboard.writeText(WADDR);status('Address copied.');}
  catch(error){var input=document.createElement('textarea');input.value=WADDR;input.style.position='fixed';input.style.opacity='0';document.body.appendChild(input);input.select();var copied=false;
    try{copied=document.execCommand('copy');}catch(e){}input.remove();el('copyAddr').focus();status(copied?'Address copied.':'Copy unavailable. Select the address above to copy it.',!copied);}
};
'''

SWAP_JS = r'''
var prices={};
function fillSwap(){var s=FT.getState(),from=el('swapFrom'),to=el('swapTo'),keepFrom=from.value,keepTo=to.value,held=Object.keys(s.holdings).filter(k=>s.holdings[k].shares>0);
  ASSETS.forEach(function(a){prices[a.t]=a.p;prices[a.t+':name']=a.n;prices[a.t+':coach']=a.c;});
  held.forEach(function(k){var h=s.holdings[k];prices[k]=h.p;prices[k+':name']=h.n;prices[k+':coach']=h.c;});
  from.innerHTML=held.map(k=>'<option value="'+esc(k)+'">'+esc(s.holdings[k].n)+' · '+esc(k)+'</option>').join('')||'<option value="">No shares held</option>';
  if(held.includes(keepFrom))from.value=keepFrom;
  var all=[...new Set(ASSETS.map(a=>a.t).concat(held))];to.innerHTML=all.map(k=>'<option value="'+esc(k)+'">'+esc(prices[k+':name'])+' · '+esc(k)+'</option>').join('');
  if(all.includes(keepTo))to.value=keepTo;else if(to.value===from.value)to.selectedIndex=1;
  el('swapGo').disabled=!held.length;swapCalc();
}
function quote(){var from=el('swapFrom').value,to=el('swapTo').value,q=amount('swapQty'),h=FT.getState().holdings[from];
  if(!h)throw new Error('Buy player or coach shares on the exchange to get started.');
  if(from===to)throw new Error('Choose a different player or coach to receive.');
  if(!valid(q)||!Number.isInteger(q))throw new Error('Enter a positive whole number of shares.');
  if(q>h.shares)throw new Error('You hold '+fmt(h.shares)+' '+from+' shares.');
  var gross=q*h.p,fee=gross*.004,net=gross-fee,got=Math.floor(net/prices[to]);
  if(!Number.isFinite(got)||got<1)throw new Error('Increase the amount to receive at least one whole share.');
  return {from:from,to:to,q:q,fee:fee,got:got,change:Math.round(net-got*prices[to])};
}
function pickCard(k,sub){if(!k||!prices[k+':name'])return '<span class="swap-pick-empty">Choose a player</span><svg class="ic swap-pick-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
  return playerPhoto(k,prices[k+':name'])+'<span class="swap-pick-text"><b>'+esc(prices[k+':name'])+'</b><small>'+esc(sub)+'</small></span><svg class="ic swap-pick-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';}
function syncPicks(){var s=FT.getState(),f=el('swapFrom').value,t=el('swapTo').value,h=s.holdings[f];
  el('swapFromBtn').innerHTML=h?pickCard(f,ftSym(f)+' · '+fmt(h.shares)+' shares available'):'<span class="swap-pick-empty">No shares held yet</span>';
  el('swapFromBtn').disabled=!h;
  el('swapToBtn').innerHTML=pickCard(t,ftSym(t)+' · '+(prices[t]?Number(prices[t]).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})+' FTR per share':''));}
function swapCalc(){var k=el('swapFrom').value,h=FT.getState().holdings[k];syncPicks();el('swapPreview').innerHTML=h?'':'<a class="utility-back" href="exchange.html">Explore players on the exchange</a>';
  try{var q=quote();el('swGet').textContent=fmt(q.got)+' '+ftSym(q.to);el('swFee').textContent=fmt(q.fee)+' $FTR';el('swDust').textContent=fmt(q.change)+' $FTR';}
  catch(e){['swGet','swFee','swDust'].forEach(id=>el(id).textContent='—');}
}
['swapFrom','swapTo'].forEach(id=>el(id).addEventListener('change',swapCalc));el('swapQty').addEventListener('input',swapCalc);
['swapHalf','swapMax'].forEach(id=>el(id).onclick=function(){var h=FT.getState().holdings[el('swapFrom').value];if(h){el('swapQty').value=Math.floor(h.shares*(id==='swapHalf'?.5:1));swapCalc();}});
el('swapForm').onsubmit=function(e){e.preventDefault();status('');try{var q=quote(),worth=q.q*FT.getState().holdings[q.from].p;review({kind:'Swap',icon:'swap',title:'Review swap',heroLabel:'You receive',amount:fmt(q.got),unit:q.to+' shares',sub:'for '+fmt(q.q)+' '+q.from+' shares',
    rows:[['You give',fmt(q.q)+' '+q.from],['Value of shares given',fmt(worth)+' $FTR'],['You receive',fmt(q.got)+' '+q.to],['Price per '+q.to+' share',fmt(prices[q.to])+' $FTR'],['Swap fee · 0.4%',fmt(q.fee)+' $FTR'],['Change returned to wallet',fmt(q.change)+' $FTR','rv-total']],
    note:'Both sides settle together. If either side can’t complete, nothing changes.',confirm:'Swap shares',action:function(){
    var result=FT.swapAssets(q.from,q.to,q.q,prices);el('swapQty').value='';swapCalc();status('Received '+fmt(result.received)+' '+q.to+' shares.');}});}catch(error){status(error.message,true);}};
/* Player picker: the same card as Switch player on the player page. */
var picking='from',picker=el('swapPicker');
function clubOf(k){var a=ASSETS.filter(function(x){return x.t===k;})[0];return a&&a.club?a.club:(prices[k+':coach']?'Coach':'');}
function pickerRows(){var s=FT.getState(),q=el('swapSearch').value.trim().toLowerCase(),rows;
  if(picking==='from'){rows=Object.keys(s.holdings).filter(k=>s.holdings[k].shares>0).map(k=>({t:k,n:s.holdings[k].n,sub:ftSym(k)+(clubOf(k)?' · '+clubOf(k):''),v:fmt(s.holdings[k].shares),u:'shares'}));}
  else{var from=el('swapFrom').value;rows=[...new Set(ASSETS.map(a=>a.t).concat(Object.keys(s.holdings)))].filter(k=>k!==from&&prices[k]).map(k=>({t:k,n:prices[k+':name'],sub:ftSym(k)+(clubOf(k)?' · '+clubOf(k):''),v:Number(prices[k]).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2}),u:'FTR'}));}
  rows=rows.filter(r=>(r.n+' '+r.sub).toLowerCase().includes(q));
  var current=el(picking==='from'?'swapFrom':'swapTo').value;
  el('swapSearchStatus').textContent=rows.length?rows.length+(picking==='from'?' holdings':' shares'):'No matches. Try another name or club.';
  el('swapSearchResults').innerHTML=rows.map(r=>'<button type="button" class="asset-search-row" data-sym="'+esc(r.t)+'"'+(r.t===current?' aria-current="true"':'')+'>'+playerPhoto(r.t,r.n)
    +'<span><b>'+esc(r.n)+'</b><small>'+esc(r.sub)+'</small></span><span class="asset-search-price">'+r.v+'<small>'+r.u+'</small></span></button>').join('');}
function openPicker(which){picking=which;el('swapPickerTitle').textContent=which==='from'?'Choose shares to swap.':'Choose what to receive.';
  el('swapSearch').value='';pickerRows();picker.showModal();document.body.classList.add('asset-picker-open');el('swapSearch').focus();}
document.querySelectorAll('[data-pick]').forEach(b=>b.addEventListener('click',function(){openPicker(b.dataset.pick);}));
el('swapSearch').addEventListener('input',pickerRows);
el('swapSearchResults').addEventListener('click',function(e){var row=e.target.closest('[data-sym]');if(!row)return;
  var sel=el(picking==='from'?'swapFrom':'swapTo');sel.value=row.dataset.sym;
  if(picking==='from'&&el('swapTo').value===sel.value){var alt=[...el('swapTo').options].map(o=>o.value).filter(v=>v!==sel.value)[0];if(alt)el('swapTo').value=alt;}
  sel.dispatchEvent(new Event('change'));picker.close();});
el('swapPickerClose').addEventListener('click',function(){picker.close();});
picker.addEventListener('close',function(){document.body.classList.remove('asset-picker-open');el(picking==='from'?'swapFromBtn':'swapToBtn').focus();});
picker.addEventListener('click',function(e){var r=picker.getBoundingClientRect();if(e.target===picker&&(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom))picker.close();});
fillSwap();window.addEventListener('fantrade:statechange',fillSwap);
'''

BUY_JS = r'''
function buyQuote(){var n=amount('fiat'),rate=FT.getState().wallet.gbpRate,gross=n*rate;return {amount:n,fee:gross*.005,net:Math.round(gross*.995)};}
function buyCalc(){var q=buyQuote();el('buyRate').textContent='£1 = '+fmt(FT.getState().wallet.gbpRate)+' $FTR';el('buyNet').textContent=valid(q.amount)?fmt(q.net):'—';el('buyFee').textContent=valid(q.amount)?fmt(q.fee)+' $FTR':'—';}
el('fiat').addEventListener('input',buyCalc);document.querySelectorAll('[data-gbp]').forEach(b=>b.onclick=function(){el('fiat').value=b.dataset.gbp;buyCalc();});
el('buyForm').onsubmit=function(e){e.preventDefault();status('');var q=buyQuote();if(!valid(q.amount)||!Number.isSafeInteger(q.net)||q.net<1){status('Enter an amount that converts to at least 1 $FTR.',true);return;}
  var bal=FT.getState().wallet.balance;
  review({kind:'Add funds',icon:'coin',title:'Review conversion',heroLabel:'You receive',amount:fmt(q.net),unit:'$FTR',sub:'for £'+fmt(q.amount),
    rows:[['You pay','£'+fmt(q.amount)],['Rate','£1 = '+fmt(FT.getState().wallet.gbpRate)+' $FTR'],['Conversion fee · 0.5%',fmt(q.fee)+' $FTR'],['Arrives','Instantly'],['Balance after',fmt(bal+q.net)+' $FTR','rv-total']],
    note:'Demo conversion. No card is charged and no real money moves.',confirm:'Add '+fmt(q.net)+' $FTR',action:function(){var got=FT.convertGbp(q.amount);el('fiat').value='';buyCalc();status('Added '+fmt(got)+' $FTR to your demo wallet.');}});
};buyCalc();
'''

ACTIVITY_JS = r'''
var category='all',categories={trades:['BUY','SELL','SWAP'],transfers:['SEND','WITHDRAW','DEPOSIT','CONVERT'],fanplay:['STAKE','PAYOUT','SETTLE']};
function activity(){var search=el('activitySearch').value.trim().toLowerCase(),list=FT.getState().transactions.filter(t=>(category==='all'||categories[category].includes(t.type))&&[labels[t.type],t.asset,t.time,t.type].join(' ').toLowerCase().includes(search));
  el('activityCount').textContent=list.length+' transaction'+(list.length===1?'':'s');el('activityRows').innerHTML=list.map(ledgerRow).join('')||'<div class="wallet-empty"><b>No activity here yet</b>'+(search||category!=='all'?'Try another search or filter.':'Your trades and transfers will appear here.')+'</div>';
}
el('activitySearch').addEventListener('input',activity);document.querySelectorAll('[data-category]').forEach(b=>b.onclick=function(){category=b.dataset.category;document.querySelectorAll('[data-category]').forEach(x=>x.setAttribute('aria-pressed',x===b));activity();});
activity();window.addEventListener('fantrade:statechange',activity);
'''

WITHDRAW_JS = r'''
var RATES={GBP:1,NGN:2050,EUR:1.17,USD:1.27},SYMBOL={GBP:'£',NGN:'₦',EUR:'€',USD:'$'},
CURS={GBP:{n:'British pound',sub:'GBP payout account'},NGN:{n:'Nigerian naira',sub:'NGN bank account'},EUR:{n:'Euro',sub:'EUR or IBAN account'},USD:{n:'US dollar',sub:'USD payout account'}};
function wdQuote(){var n=amount('wdAmount'),fee=valid(n)?Math.max(50,Math.round(n*.005)):0,cur=el('wdCurrency').value,
  gbp=valid(n)?n/FT.getState().wallet.gbpRate:0;return {n:n,fee:fee,total:n+fee,cur:cur,out:gbp*RATES[cur]};}
function wdCalc(){var q=wdQuote(),bal=FT.getState().wallet.balance;
  el('wdFee').textContent=valid(q.n)?fmt(q.fee)+' $FTR':'—';
  el('wdTotal').textContent=valid(q.n)?(q.total>bal?'More than your balance':fmt(q.total)+' $FTR'):'—';
  el('wdReceive').textContent=valid(q.n)?'≈ '+SYMBOL[q.cur]+fmt(Math.round(q.out*100)/100):'—';}
function wdBankFields(){var gb=el('wdCurrency').value==='GBP';el('wdSortLabel').textContent=gb?'Sort code':'Bank code (optional)';
  el('wdSort').placeholder=gb?'00-00-00':'Optional';el('wdAcct').placeholder=gb?'8 digits':el('wdCurrency').value==='NGN'?'10 digits (NUBAN)':'Account number or IBAN';}
function currencyCard(code){var cur=CURS[code];return '<span class="wallet-currency-dot">'+SYMBOL[code]+'</span><span class="swap-pick-text"><b>'+esc(cur.n)+'</b><small>'+code+' · '+cur.sub+'</small></span><svg class="ic swap-pick-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';}
function syncCurrencyPick(){el('wdCurrencyBtn').innerHTML=currencyCard(el('wdCurrency').value);}
var wdCurrencyPicker=el('wdCurrencyPicker');
function currencyRows(){var current=el('wdCurrency').value,keys=Object.keys(CURS);el('wdCurrencyStatus').textContent=keys.length+' payout currencies';
  el('wdCurrencyResults').innerHTML=keys.map(function(code){var cur=CURS[code];return '<button type="button" class="asset-search-row" data-currency="'+code+'"'+(code===current?' aria-current="true"':'')+'><span class="wallet-currency-dot">'+SYMBOL[code]+'</span><span><b>'+esc(cur.n)+'</b><small>'+code+' · '+esc(cur.sub)+'</small></span><span class="asset-search-price">'+code+'</span></button>';}).join('');}
function openCurrencyPicker(){currencyRows();wdCurrencyPicker.showModal();document.body.classList.add('asset-picker-open');}
var saved=(FT.getState().prefs||{}).payoutBank;
if(saved){['Currency','Name','Bank','Sort','Acct'].forEach(function(k){if(saved[k]!=null)el('wd'+k).value=saved[k];});}
wdBankFields();syncCurrencyPick();
['wdAmount'].forEach(id=>el(id).addEventListener('input',wdCalc));
el('wdCurrency').addEventListener('change',function(){wdBankFields();syncCurrencyPick();wdCalc();});
el('wdCurrencyBtn').addEventListener('click',openCurrencyPicker);
el('wdCurrencyResults').addEventListener('click',function(e){var row=e.target.closest('[data-currency]');if(!row)return;el('wdCurrency').value=row.dataset.currency;el('wdCurrency').dispatchEvent(new Event('change'));wdCurrencyPicker.close();});
el('wdCurrencyPickerClose').addEventListener('click',function(){wdCurrencyPicker.close();});
wdCurrencyPicker.addEventListener('close',function(){document.body.classList.remove('asset-picker-open');el('wdCurrencyBtn').focus();});
wdCurrencyPicker.addEventListener('click',function(e){var r=wdCurrencyPicker.getBoundingClientRect();if(e.target===wdCurrencyPicker&&(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom))wdCurrencyPicker.close();});
document.querySelectorAll('[data-wd]').forEach(b=>b.onclick=function(){el('wdAmount').value=b.dataset.wd;wdCalc();});
el('wdMax').onclick=function(){var bal=FT.getState().wallet.balance,n=Math.floor(Math.max(0,bal-Math.max(50,bal*.005))/1.005);el('wdAmount').value=n>0?n:'';wdCalc();};
function digits(v){return (v||'').replace(/[\s-]/g,'');}
el('withdrawForm').onsubmit=function(e){e.preventDefault();status('');var q=wdQuote(),cur=q.cur,
  name=el('wdName').value.trim(),bank=el('wdBank').value.trim(),sort=digits(el('wdSort').value),acct=digits(el('wdAcct').value);
  if(!valid(q.n)){status('Enter a positive amount with up to two decimal places.',true);return;}
  if(q.total>FT.getState().wallet.balance){status('Your balance cannot cover this amount plus the withdrawal fee.',true);return;}
  if(name.length<2){status('Enter the account holder name.',true);return;}
  if(bank.length<2){status('Enter your bank name.',true);return;}
  if(cur==='GBP'&&!/^\d{6}$/.test(sort)){status('Enter a 6-digit sort code.',true);return;}
  if(cur==='GBP'&&!/^\d{8}$/.test(acct)){status('Enter an 8-digit account number.',true);return;}
  if(cur==='NGN'&&!/^\d{10}$/.test(acct)){status('Enter a 10-digit NUBAN account number.',true);return;}
  if(cur!=='GBP'&&cur!=='NGN'&&!/^[A-Za-z0-9]{6,34}$/.test(acct)){status('Enter a valid account number or IBAN.',true);return;}
  var dest=bank+' ••'+acct.slice(-4)+' ('+cur+')';
  var bal=FT.getState().wallet.balance;
  review({kind:'Withdrawal',icon:'bank',title:'Review withdrawal',heroLabel:'You receive about',amount:SYMBOL[cur]+fmt(Math.round(q.out*100)/100),unit:cur,sub:'to '+name+' · '+dest,
    rows:[['Account holder',name],['Bank account',dest],['Amount',fmt(q.n)+' $FTR'],['Withdrawal fee',fmt(q.fee)+' $FTR'],['Total deducted',fmt(q.total)+' $FTR'],['Arrives','1–2 working days'],['Balance after',fmt(bal-q.total)+' $FTR','rv-total']],
    note:'Demo withdrawal. Your preview balance updates; no real money is sent.',confirm:'Withdraw '+fmt(q.n)+' $FTR',action:function(){
    if(el('wdSave').checked)FT.setPref('payoutBank',{Currency:cur,Name:name,Bank:bank,Sort:el('wdSort').value.trim(),Acct:acct});
    FT.sendFtr(q.n,dest,'withdraw',{currency:cur,holder:name,bank:bank,account:acct,save:el('wdSave').checked});
    el('wdAmount').value='';wdCalc();status('Withdrawal of '+fmt(q.n)+' $FTR requested to '+dest+'.');}});
};
function wdLog(){var rows=FT.getState().transactions.filter(t=>t.type==='WITHDRAW').slice(0,3);
  el('wdLog').innerHTML=rows.map(ledgerRow).join('')||'<p class="wallet-note">Your withdrawals will appear here.</p>';wdCalc();}
wdLog();window.addEventListener('fantrade:statechange',wdLog);
'''

PAGES = [('send', SEND_HTML, SEND_JS), ('receive', RECEIVE_HTML, RECEIVE_JS),
         ('swap', SWAP_HTML, SWAP_JS), ('buy', BUY_HTML, BUY_JS), ('withdraw', WITHDRAW_HTML, WITHDRAW_JS),
         ('activity', ACTIVITY_HTML, ACTIVITY_JS)]
