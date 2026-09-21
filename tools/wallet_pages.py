"""Wallet workflows using the same open layout as onboarding."""
import json
from common import ic, qr_svg, QR_ADDRESS


def intro(title, description):
    return ('<a class="utility-back" href="ftr.html">' + ic('arrow', 'ic') + 'Wallet</a>'
            '<header class="utility-intro"><div><h1>' + title + '</h1><p>' + description + '</p></div></header>')


REVIEW = '''<dialog class="wallet-review" id="walletReview" aria-labelledby="reviewTitle">
<h2 id="reviewTitle">Review transfer</h2><p id="reviewText"></p>
<div class="wallet-actions"><button class="wallet-button" id="reviewCancel" type="button">Go back</button>
<button class="app-primary" id="reviewConfirm" type="button">Confirm</button></div></dialog>'''


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
<form id="swapForm"><div class="wallet-field"><label for="swapFrom">From your portfolio</label><select id="swapFrom"></select>
<div class="swap-preview" id="swapPreview"></div></div>
<div class="wallet-field"><label for="swapQty">Shares to swap</label><div class="wallet-amount">
<input id="swapQty" type="number" min="1" step="1" inputmode="numeric" placeholder="0" required><span>shares</span></div></div>
<div class="wallet-quick"><button class="wallet-chip" type="button" id="swapHalf">Half</button><button class="wallet-chip" type="button" id="swapMax">Max</button></div>
<div class="wallet-field"><label for="swapTo">Receive</label><select id="swapTo"></select></div>
<span class="wallet-label">Estimated shares received</span><div class="wallet-estimate" id="swGet">—</div>
<dl class="wallet-summary"><div><dt>Swap fee · 0.4%</dt><dd id="swFee">—</dd></div><div><dt>Change returned to wallet</dt><dd id="swDust">—</dd></div></dl>
<button class="app-primary wallet-submit" type="submit" id="swapGo">Review swap</button></form>''' + STATUS + DEMO + '''
<a class="utility-back" href="portfolio.html">View your portfolio</a>''')

BUY_HTML = workflow('Add funds', 'Try a conversion from pounds to $FTR.', BALANCE + '''
<form id="buyForm"><div class="wallet-field"><label for="fiat">Amount in pounds</label><div class="wallet-amount">
<input id="fiat" type="number" min="0.01" step="0.01" inputmode="decimal" placeholder="0" required><span>GBP</span></div></div>
<div class="wallet-quick"><button type="button" class="wallet-chip" data-gbp="100">£100</button>
<button type="button" class="wallet-chip" data-gbp="500">£500</button><button type="button" class="wallet-chip" data-gbp="1000">£1,000</button></div>
<span class="wallet-label">You receive, after fees</span><div class="wallet-estimate"><span id="buyNet">—</span> <small>$FTR</small></div>
<dl class="wallet-summary"><div><dt>Conversion rate</dt><dd id="buyRate"></dd></div><div><dt>Conversion fee · 0.5%</dt><dd id="buyFee">—</dd></div></dl>
<button class="app-primary wallet-submit" type="submit">Review demo conversion</button></form>''' + STATUS + '''
<p class="wallet-note">Demo conversion. No card is charged. The amount is added to your preview wallet.</p>''')

ACTIVITY_HTML = ('<main><div class="utility-page">' + intro('Wallet activity', 'Follow your trades, transfers and FanPlay entries.')
                 + BALANCE + '''<div class="wallet-actions"><a class="app-primary" href="buy.html">Add funds</a>
<a class="wallet-button" href="send.html">Send</a><a class="wallet-button" href="receive.html">Receive</a>
<button class="wallet-button" type="button" id="withdrawOpen">Withdraw</button></div>
<div class="wallet-field"><label for="activitySearch">Search activity</label><input id="activitySearch" type="search" placeholder="Player, recipient or transaction"></div>
<div class="wallet-tabs" aria-label="Activity filters"><button class="wallet-chip" data-category="all" aria-pressed="true">All</button>
<button class="wallet-chip" data-category="trades" aria-pressed="false">Trades</button><button class="wallet-chip" data-category="transfers" aria-pressed="false">Transfers</button>
<button class="wallet-chip" data-category="fanplay" aria-pressed="false">FanPlay</button></div>
<p class="wallet-note" id="activityCount" role="status"></p><div id="activityRows"></div>''' + STATUS + '''
<dialog class="wallet-review" id="withdrawDialog" aria-labelledby="withdrawTitle"><h2 id="withdrawTitle">Demo withdrawal</h2>
<p>Withdraw to your demo payout account. No real funds move.</p><form id="withdrawForm"><div class="wallet-field"><label for="withdrawAmount">Amount in $FTR</label>
<input id="withdrawAmount" type="number" min="0.01" step="0.01" inputmode="decimal" placeholder="0" required></div>
<p id="withdrawCost">Fee: 0.5%, with a minimum of 50 $FTR.</p><p class="wallet-status" id="withdrawError" role="status"></p>
<div class="wallet-actions"><button class="wallet-button" type="button" id="withdrawCancel">Cancel</button><button class="app-primary" type="submit">Review</button></div></form></dialog>'''
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
function review(title,text,action){el('reviewTitle').textContent=title;el('reviewText').textContent=text;pendingAction=action;el('reviewConfirm').disabled=false;el('walletReview').showModal();el('reviewCancel').focus();}
if(el('walletReview')){
  el('reviewCancel').onclick=function(){pendingAction=null;el('walletReview').close();};
  el('walletReview').addEventListener('close',function(){pendingAction=null;});
  el('reviewConfirm').onclick=function(){var action=pendingAction;if(!action)return;pendingAction=null;this.disabled=true;
    try{action();}catch(error){status(error.message,true);}finally{el('walletReview').close();}};
}
var labels={BUY:'Bought shares',SELL:'Sold shares',STAKE:'FanPlay entry',PAYOUT:'FanPlay payout',SETTLE:'Settlement',CONVERT:'Added funds',DEPOSIT:'Deposit',SEND:'Transfer sent',WITHDRAW:'Withdrawal',SWAP:'Swapped shares'};
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
  review('Review transfer',fmt(n)+' $FTR to '+to+'\nTransfer fee: free\nBalance after: '+fmt(FT.getState().wallet.balance-n)+' $FTR',function(){
    FT.sendFtr(n,to,'send');el('sendAmt').value='';sendCalc();status('Sent '+fmt(n)+' $FTR to '+to+'.');});
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
function swapCalc(){var k=el('swapFrom').value,h=FT.getState().holdings[k];el('swapPreview').innerHTML=h?playerPhoto(k,h.n)+'<span>'+fmt(h.shares)+' shares available</span>':'<a class="utility-back" href="exchange.html">Explore players on the exchange</a>';
  try{var q=quote();el('swGet').textContent=fmt(q.got)+' '+q.to;el('swFee').textContent=fmt(q.fee)+' $FTR';el('swDust').textContent=fmt(q.change)+' $FTR';}
  catch(e){['swGet','swFee','swDust'].forEach(id=>el(id).textContent='—');}
}
['swapFrom','swapTo'].forEach(id=>el(id).addEventListener('change',swapCalc));el('swapQty').addEventListener('input',swapCalc);
['swapHalf','swapMax'].forEach(id=>el(id).onclick=function(){var h=FT.getState().holdings[el('swapFrom').value];if(h){el('swapQty').value=Math.floor(h.shares*(id==='swapHalf'?.5:1));swapCalc();}});
el('swapForm').onsubmit=function(e){e.preventDefault();status('');try{var q=quote();review('Review swap',fmt(q.q)+' '+q.from+' → '+fmt(q.got)+' '+q.to+'\nFee: '+fmt(q.fee)+' $FTR\nChange to wallet: '+fmt(q.change)+' $FTR',function(){
    var result=FT.swapAssets(q.from,q.to,q.q,prices);el('swapQty').value='';swapCalc();status('Received '+fmt(result.received)+' '+q.to+' shares.');});}catch(error){status(error.message,true);}};
fillSwap();window.addEventListener('fantrade:statechange',fillSwap);
'''

BUY_JS = r'''
function buyQuote(){var n=amount('fiat'),rate=FT.getState().wallet.gbpRate,gross=n*rate;return {amount:n,fee:gross*.005,net:Math.round(gross*.995)};}
function buyCalc(){var q=buyQuote();el('buyRate').textContent='£1 = '+fmt(FT.getState().wallet.gbpRate)+' $FTR';el('buyNet').textContent=valid(q.amount)?fmt(q.net):'—';el('buyFee').textContent=valid(q.amount)?fmt(q.fee)+' $FTR':'—';}
el('fiat').addEventListener('input',buyCalc);document.querySelectorAll('[data-gbp]').forEach(b=>b.onclick=function(){el('fiat').value=b.dataset.gbp;buyCalc();});
el('buyForm').onsubmit=function(e){e.preventDefault();status('');var q=buyQuote();if(!valid(q.amount)||!Number.isSafeInteger(q.net)||q.net<1){status('Enter an amount that converts to at least 1 $FTR.',true);return;}
  review('Review demo conversion','£'+fmt(q.amount)+' → '+fmt(q.net)+' $FTR\nIncludes a '+fmt(q.fee)+' $FTR fee.\nNo card will be charged.',function(){var got=FT.convertGbp(q.amount);el('fiat').value='';buyCalc();status('Added '+fmt(got)+' $FTR to your demo wallet.');});
};buyCalc();
'''

ACTIVITY_JS = r'''
var category='all',categories={trades:['BUY','SELL','SWAP'],transfers:['SEND','WITHDRAW','DEPOSIT','CONVERT'],fanplay:['STAKE','PAYOUT','SETTLE']};
function activity(){var search=el('activitySearch').value.trim().toLowerCase(),list=FT.getState().transactions.filter(t=>(category==='all'||categories[category].includes(t.type))&&[labels[t.type],t.asset,t.time,t.type].join(' ').toLowerCase().includes(search));
  el('activityCount').textContent=list.length+' transaction'+(list.length===1?'':'s');el('activityRows').innerHTML=list.map(ledgerRow).join('')||'<div class="wallet-empty"><b>No activity here yet</b>'+(search||category!=='all'?'Try another search or filter.':'Your trades and transfers will appear here.')+'</div>';
}
el('activitySearch').addEventListener('input',activity);document.querySelectorAll('[data-category]').forEach(b=>b.onclick=function(){category=b.dataset.category;document.querySelectorAll('[data-category]').forEach(x=>x.setAttribute('aria-pressed',x===b));activity();});
el('withdrawOpen').onclick=function(){el('withdrawForm').reset();el('withdrawError').textContent='';el('withdrawCost').textContent='Fee: 0.5%, with a minimum of 50 $FTR.';el('withdrawDialog').showModal();};
el('withdrawCancel').onclick=function(){el('withdrawDialog').close();};
el('withdrawAmount').oninput=function(){var n=amount('withdrawAmount');el('withdrawCost').textContent=valid(n)?'Fee: '+fmt(Math.max(50,Math.round(n*.005)))+' $FTR. Total: '+fmt(n+Math.max(50,Math.round(n*.005)))+' $FTR.':'Fee: 0.5%, with a minimum of 50 $FTR.';};
el('withdrawForm').onsubmit=function(e){e.preventDefault();var n=amount('withdrawAmount'),fee=Math.max(50,Math.round(n*.005));
  if(!valid(n)||n+fee>FT.getState().wallet.balance){el('withdrawError').textContent='Enter an amount your balance can cover, including the withdrawal fee.';return;}
  el('withdrawDialog').close();review('Review demo withdrawal',fmt(n)+' $FTR to your demo payout account\nFee: '+fmt(fee)+' $FTR\nTotal deducted: '+fmt(n+fee)+' $FTR',function(){FT.sendFtr(n,'Payout account (GBP)','withdraw');status('Demo withdrawal recorded: '+fmt(n)+' $FTR.');});
};activity();window.addEventListener('fantrade:statechange',activity);
'''

PAGES = [('send', SEND_HTML, SEND_JS), ('receive', RECEIVE_HTML, RECEIVE_JS),
         ('swap', SWAP_HTML, SWAP_JS), ('buy', BUY_HTML, BUY_JS), ('activity', ACTIVITY_HTML, ACTIVITY_JS)]
