# -*- coding: utf-8 -*-
"""Wallet destinations. Send, Receive, Swap, Buy and the ledger each get their
own screen, reached from a button on the wallet card — nothing stacks."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import head, atmosphere, nav, footer, ic, JS_SHELL, qr_svg, QR_ADDRESS

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


def page(fname, title, body, js="", css="", app=True):
    html = (head(title, css, "app" if app else "") + atmosphere() + nav(fname, app) + body +
            "<script src=\"public/fantrade-api.js\"></script><script>(function(){" + JS_SHELL + js + "})();</script></body></html>")
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as fh:
        fh.write(html)
    return len(html)


WAL_CSS = """
.kc-wallet-wrap{max-width:680px;margin:0 auto;padding:12px 16px 84px}
.kc-topbar{display:flex;align-items:center;justify-content:space-between;padding:8px 0 18px}
.kc-top-title{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;font-size:17px;letter-spacing:-.01em;text-transform:uppercase}
.kc-icon-btn{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;color:#8E9AA8;cursor:pointer;transition:all .2s ease;text-decoration:none}
.kc-icon-btn:hover{color:#fff;background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.15)}
.kc-icon-btn .ic{width:18px;height:18px}
.kc-bal-badge{display:flex;align-items:center;gap:7px;padding:6px 12px;border-radius:999px;background:rgba(196,248,42,.08);border:1px solid rgba(196,248,42,.25);color:#C4F82A;font-family:'Montserrat', sans-serif;font-size:12px;font-weight:600;text-decoration:none;transition:all .2s}
.kc-bal-badge:hover{background:rgba(196,248,42,.15)}
.kc-bal-dot{width:6px;height:6px;border-radius:50%;background:#C4F82A;box-shadow:0 0 8px #C4F82A}

.kc-stack{display:flex;flex-direction:column;gap:16px}
.kc-stack .bezel{border-radius:20px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.07);overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.kc-stack .core{border-radius:19px}
.maxbtn{border:1px solid rgba(196,248,42,.3);background:rgba(196,248,42,.09);color:var(--lime);
  border-radius:999px;padding:5px 12px;font-weight:600;font-size:9px;letter-spacing:.12em;
  text-transform:uppercase;cursor:pointer;flex:none;transition:all .5s var(--ease)}
.maxbtn:hover{background:rgba(196,248,42,.18)}
.dist{display:flex;align-items:center;gap:26px;flex-wrap:wrap}
.dist .key{display:flex;flex-direction:column;gap:12px;flex:1;min-width:180px}
.dist .kr{display:flex;align-items:center;gap:11px;font-size:13px;color:var(--dim)}
.dist .kr i{width:10px;height:10px;border-radius:3px;display:block;flex:none}
.dist .kr b{margin-left:auto;font-family:'Montserrat', sans-serif;color:var(--ink);font-weight:400}
"""


def shell(fname, title, label, icon, body_inner, js, tone=""):
    """Mobile crypto container: header bar with back navigation, title, live balance, and stacked cards."""
    head_html = T('<main><div class="kc-wallet-wrap">'
                  '<div class="kc-topbar">'
                  '<div style="display:flex;align-items:center;gap:12px;min-width:0">'
                  '<a class="kc-icon-btn" href="ftr.html" aria-label="Back to Assets">@@</a>'
                  '<div class="kc-top-title" style="white-space:nowrap">@@</div>'
                  '</div>'
                  '<a class="kc-bal-badge" href="ftr.html" title="Available balance">'
                  '<span class="kc-bal-dot"></span><span id="wBal">128,450</span> $FTR</a>'
                  '</div>'
                  '<div class="kc-stack">',
                  ic("arrow", "ic"), label)
    sync = r"""
function el(id){ return document.getElementById(id); }
function num(v){ return parseInt(String(v).replace(/[^0-9]/g, ''), 10) || 0; }
function money(n){ return Math.round(n).toLocaleString('en-US'); }
function syncBal(){ el('wBal').textContent = FT.getState().wallet.balance.toLocaleString('en-US'); }
syncBal();
window.addEventListener('fantrade:statechange', syncBal);
"""
    return page(fname, title, head_html + body_inner + '</div></div></main>',
                sync + js, WAL_CSS)



# ══════════════════════════════════════════════════════════════════
# SEND
# ══════════════════════════════════════════════════════════════════
send = [T('<div class="bezel c7" data-reveal><div class="core pad">'
          '<div class="tf" id="f-sendTo"><label for="sendTo">To manager or address</label>'
          '<div class="inp">@@<input id="sendTo" type="text" placeholder="@handle or 0x…"></div>'
          '<div class="err">Enter a handle or a wallet address.</div></div>'
          '<div class="field"><label>Amount</label><input id="sendAmt" value="2,500" inputmode="numeric">'
          '</div>'
          '<div class="quick"><button data-sa="1000">1,000</button><button data-sa="5000">5,000</button>'
          '<button data-sa="10000">10,000</button>'
          '<button type="button" class="maxbtn" id="sendMax">Max</button></div>'
          '<div class="line"><span>Network fee</span><b>0 $FTR</b></div>'
          '<div class="line"><span>Arrives</span><b>Instantly</b></div>'
          '<div class="line"><span>Balance after</span><b id="sendAfter">125,950 $FTR</b></div>'
          '@@'
          '<div class="warn">@@<p>Transfers between managers are final. Check the handle before you '
          'send.</p></div>'
          '</div></div>',
          ic("user", "ic"),
          btn("Send $FTR", tag="button",
              extra='id="sendGo" style="width:100%;justify-content:space-between;margin-top:18px"'),
          ic("flag", "ic"))]

send.append('<div class="bezel c5" data-reveal><div class="core pad">'
            '<div class="k-label">Recent</div>'
            '<div class="quickrow" id="quickRow"></div>'
            '<div class="k-label" style="margin-top:26px">Last transfers</div>'
            '<div id="sendLog"></div></div></div>')

SEND_JS = r"""
function wrap(id){ return document.getElementById('f-' + id); }
function sendAfter(){
  el('sendAfter').textContent =
    money(Math.max(0, FT.getState().wallet.balance - num(el('sendAmt').value))) + ' $FTR';
}
el('sendAmt').addEventListener('input', sendAfter);
document.querySelectorAll('[data-sa]').forEach(function(b){
  b.addEventListener('click', function(){
    el('sendAmt').value = (+b.dataset.sa).toLocaleString('en-US'); sendAfter();
  });
});
el('sendMax').addEventListener('click', function(){
  el('sendAmt').value = FT.getState().wallet.balance.toLocaleString('en-US'); sendAfter();
});
el('sendGo').addEventListener('click', function(){
  var to = el('sendTo').value.trim();
  if(to.length < 3){ wrap('sendTo').classList.add('bad'); return; }
  wrap('sendTo').classList.remove('bad');
  try {
    var r = FT.sendFtr(num(el('sendAmt').value), to, 'send');
    showToast(money(r.sent) + ' $FTR sent to ' + to + '.', 'success');
    sendAfter(); renderLog();
  } catch(e){ showToast(e.message, 'error'); }
});

var RECENT = [{n:'GoonerDAO', h:'@gooner_dao', c:'#EF0107'}, {n:'KaiserWeb3', h:'@kaiserweb3', c:'#DC052D'},
              {n:'MilanoWhale', h:'@milanowhale', c:'#4DA6FF'}, {n:'LagosLedger', h:'@lagosledger', c:'#C4F82A'},
              {n:'SambaStake', h:'@sambastake', c:'#FF6A1F'}];
var box = el('quickRow');
box.innerHTML = RECENT.map(function(r){
  return '<button class="qp" type="button" data-handle="' + r.h + '">'
    + '<span class="av" style="background:linear-gradient(160deg,' + r.c + ',rgba(0,0,0,.45))">'
    + r.n.slice(0, 2).toUpperCase() + '</span><span>' + r.n + '</span></button>';
}).join('');
box.querySelectorAll('.qp').forEach(function(b){
  b.addEventListener('click', function(){
    el('sendTo').value = b.dataset.handle;
    el('sendTo').focus();
  });
});

function renderLog(){
  var s = FT.getState();
  var rows = (s.transactions || []).filter(function(t){
    return t.type === 'SEND' || t.type === 'WITHDRAW';
  }).slice(0, 6);
  el('sendLog').innerHTML = rows.length ? rows.map(function(t){
    return '<div class="trow"><span class="coin">'
      + '<svg class="ic" aria-hidden="true"><use href="#i-send"/></svg></span>'
      + '<div class="bd"><div class="t">' + t.asset + '</div><div class="d">' + t.time + '</div></div>'
      + '<div class="a" style="color:var(--red)">-' + money(t.total) + '</div></div>';
  }).join('') : '<div class="empty-state"><svg class="ic-xl" aria-hidden="true">'
    + '<use href="#i-send"/></svg>Nothing sent yet.</div>';
}
renderLog();
sendAfter();
window.addEventListener('fantrade:statechange', function(){ sendAfter(); renderLog(); });
"""
shell("send.html", "Send $FTR — Fantrade", "Send", "send", "".join(send), SEND_JS)


# ══════════════════════════════════════════════════════════════════
# RECEIVE
# ══════════════════════════════════════════════════════════════════
recv = [T('<div class="bezel c7" data-reveal><div class="core pad">'
          '<button class="netsel" type="button" id="netSel">'
          '<span class="coin lime">@@</span>'
          '<span style="min-width:0"><span class="k">Network</span>'
          '<span class="v" id="netName">Fantrade L2 · Mainnet</span></span>'
          '<span class="chev"></span></button>'
          '<div class="qr">@@<span class="mark">@@</span></div>'
          '<div class="addr" id="walAddr"></div>'
          '@@'
          '</div></div>',
          ic("layers", "ic"), qr_svg(), ic("ball", "ic"),
          btn("Copy address", tag="button",
              extra='id="copyAddr" style="width:100%;justify-content:space-between"'))]

recv.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
              '<div class="k-label">Details</div>'
              '<div class="line"><span>Asset</span><b>$FTR and share tokens</b></div>'
              '<div class="line"><span>Minimum</span><b>1 $FTR</b></div>'
              '<div class="line"><span>Confirmations</span><b>1</b></div>'
              '<div class="line"><span>Deposit fee</span><b>0 $FTR</b></div>'
              '<div class="warn" style="margin-top:20px">@@<p>Send only $FTR and Fantrade-issued share '
              'tokens to this address. Anything else is unrecoverable.</p></div>'
              '<div style="margin-top:18px">@@</div>'
              '</div></div>', ic("flag", "ic"),
              btn("Buy $FTR instead", "btn-glass", "buy.html",
                  extra='style="width:100%;justify-content:space-between"')))

RECV_JS = ("var WADDR=" + ('"%s"' % QR_ADDRESS) + ";") + r"""
(function(){
  var cols = ['var(--lime)', 'var(--amber)', '#4DA6FF', 'var(--ink)'];
  var out = '', i = 0;
  while(i < WADDR.length){
    out += '<i style="color:' + cols[(i / 4 | 0) % 4] + '">' + WADDR.slice(i, i + 4) + '</i>';
    i += 4;
  }
  el('walAddr').innerHTML = out;
})();

el('copyAddr').addEventListener('click', function(){
  function done(){ showToast('Receive address copied.', 'success'); }
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(WADDR).then(done, fallback);
  } else { fallback(); }
  function fallback(){
    var ta = document.createElement('textarea');
    ta.value = WADDR; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); done(); }
    catch(e){ showToast('Copy failed — select the address manually.', 'error'); }
    ta.remove();
  }
});

el('netSel').addEventListener('click', function(){
  openModal('<h3 class="ft-modal-title">Receiving network</h3>'
    + '<div class="ft-modal-card">'
    + '<div class="m-row"><span>Fantrade L2 · Mainnet</span><b style="color:var(--lime)">Instant · no gas</b></div>'
    + '<div class="m-row"><span>Ethereum · Mainnet</span><b>~3 min · gas applies</b></div>'
    + '<div class="m-row"><span>Base</span><b>~40 sec · low gas</b></div>'
    + '<div class="m-row total"><span>Polygon</span><b>~1 min · low gas</b></div></div>');
});
"""
shell("receive.html", "Receive $FTR — Fantrade", "Receive", "receive", "".join(recv), RECV_JS)


# ══════════════════════════════════════════════════════════════════
# SWAP
# ══════════════════════════════════════════════════════════════════
swap = [T('<div class="bezel c7" data-reveal><div class="core pad">'
          '<div class="tf" id="f-swapFrom"><label for="swapFrom">From</label><div class="inp">@@'
          '<select id="swapFrom"></select><span class="chev"></span></div>'
          '<div class="hint" id="swapHold">—</div></div>'
          '<div class="field"><label>Shares</label><input id="swapQty" value="1,000" inputmode="numeric"></div>'
          '<div class="quick"><button data-sq="250">250</button><button data-sq="500">500</button>'
          '<button data-sq="1000">1,000</button>'
          '<button type="button" class="maxbtn" id="swapMax">Max</button></div>'
          '<div class="tf" id="f-swapTo" style="margin-top:14px"><label for="swapTo">To</label>'
          '<div class="inp">@@<select id="swapTo"></select><span class="chev"></span></div></div>'
          '<div class="line"><span>You give</span><b id="swGive">—</b></div>'
          '<div class="line"><span>Swap fee (0.4%)</span><b id="swFee">—</b></div>'
          '<div class="line"><span>You receive</span><b id="swGet">—</b></div>'
          '<div class="line"><span>Dust returned</span><b id="swDust">—</b></div>'
          '@@</div></div>',
          ic("swap", "ic"), ic("target", "ic"),
          btn("Swap assets", tag="button",
              extra='id="swapGo" style="width:100%;justify-content:space-between;margin-top:18px"'))]

swap.append(T('<div class="bezel c5" data-reveal><div class="core">'
              '<div style="padding:24px 24px 10px"><div class="k-label" style="margin:0">What you hold</div>'
              '</div><div id="swHold"></div>'
              '<div style="padding:14px 24px 24px">@@</div>'
              '</div></div>',
              btn("Open the exchange", "btn-glass", "exchange.html",
                  extra='style="width:100%;justify-content:space-between"')))

SWAP_JS = r"""
var PRICES = {};
function fillSwap(){
  var s = FT.getState(), from = el('swapFrom'), to = el('swapTo');
  var held = Object.keys(s.holdings);
  var all = {};
  held.forEach(function(k){ all[k] = s.holdings[k].p; });
  ASSETS.forEach(function(a){ all[a.t] = a.p; PRICES[a.t] = a.p; });
  held.forEach(function(k){ PRICES[k] = s.holdings[k].p; });

  var keepFrom = from.value, keepTo = to.value;
  from.innerHTML = held.map(function(k){
    return '<option value="' + k + '">' + k + ' · ' + s.holdings[k].shares.toLocaleString('en-US')
      + ' shares</option>';
  }).join('') || '<option value="">Nothing held yet</option>';
  to.innerHTML = Object.keys(all).map(function(k){
    return '<option value="' + k + '">' + k + ' · ' + all[k].toFixed(2) + ' $FTR</option>';
  }).join('');
  if(keepFrom && s.holdings[keepFrom]) from.value = keepFrom;
  if(keepTo && all[keepTo]) to.value = keepTo;
  else if(to.value === from.value && to.options.length > 1) to.selectedIndex = 1;
  swapCalc();
}
function swapCalc(){
  var s = FT.getState(), fk = el('swapFrom').value, tk = el('swapTo').value;
  var h = s.holdings[fk];
  if(!h){ ['swGive','swFee','swGet','swDust'].forEach(function(i){ el(i).textContent = '—'; });
    el('swapHold').textContent = 'Buy something on the exchange first.'; return; }
  el('swapHold').textContent = 'You hold ' + h.shares.toLocaleString('en-US') + ' at '
    + h.p.toFixed(2) + ' $FTR.';
  var q = Math.min(num(el('swapQty').value), h.shares);
  var gross = q * h.p, fee = gross * 0.004, net = gross - fee;
  var tp = PRICES[tk] || 0, got = tp ? Math.floor(net / tp) : 0;
  el('swGive').textContent = q.toLocaleString('en-US') + ' ' + fk + ' · ' + money(gross) + ' $FTR';
  el('swFee').textContent = money(fee) + ' $FTR';
  el('swGet').textContent = got.toLocaleString('en-US') + ' ' + tk;
  el('swDust').textContent = money(Math.max(0, net - got * tp)) + ' $FTR';
}
el('swapQty').addEventListener('input', swapCalc);
['swapFrom','swapTo'].forEach(function(i){ el(i).addEventListener('change', swapCalc); });
document.querySelectorAll('[data-sq]').forEach(function(b){
  b.addEventListener('click', function(){
    el('swapQty').value = (+b.dataset.sq).toLocaleString('en-US'); swapCalc();
  });
});
el('swapMax').addEventListener('click', function(){
  var h = FT.getState().holdings[el('swapFrom').value];
  if(h){ el('swapQty').value = h.shares.toLocaleString('en-US'); swapCalc(); }
});
el('swapGo').addEventListener('click', function(){
  var fk = el('swapFrom').value, tk = el('swapTo').value;
  if(!fk){ showToast('Nothing to swap yet.', 'error'); return; }
  if(fk === tk){ showToast('Pick two different assets.', 'error'); return; }
  try {
    var r = FT.swapAssets(fk, tk, num(el('swapQty').value), PRICES);
    showToast(r.spent.toLocaleString('en-US') + ' ' + fk + ' swapped for '
      + r.received.toLocaleString('en-US') + ' ' + tk + '.', 'success');
  } catch(e){ showToast(e.message, 'error'); }
});

function renderHold(){
  var s = FT.getState();
  el('swHold').innerHTML = Object.keys(s.holdings).map(function(k){
    var h = s.holdings[k];
    return '<div class="arow" style="grid-template-columns:1.7fr 1fr"><div class="who">'
      + '<span class="coin' + (h.c ? ' am' : ' lime') + '">'
      + '<svg class="ic" aria-hidden="true"><use href="#i-' + (h.c ? 'whistle' : 'boot') + '"/></svg></span>'
      + '<div style="min-width:0"><div class="nm">' + h.n + '</div>'
      + '<div class="qt">' + h.shares.toLocaleString('en-US') + ' ' + k + '</div></div></div>'
      + '<div><div class="val">' + money(h.shares * h.p) + '</div>'
      + '<div class="chg">' + h.p.toFixed(2) + ' $FTR</div></div></div>';
  }).join('') || '<div class="empty-state"><svg class="ic-xl" aria-hidden="true">'
    + '<use href="#i-swap"/></svg>No positions to swap yet.</div>';
}
fillSwap(); renderHold();
window.addEventListener('fantrade:statechange', function(){ fillSwap(); renderHold(); });
"""
shell("swap.html", "Swap — Fantrade", "Swap", "swap", "".join(swap), SWAP_JS)


# ══════════════════════════════════════════════════════════════════
# BUY
# ══════════════════════════════════════════════════════════════════
buy = [T('<div class="bezel c7" data-reveal><div class="core pad">'
         '<div class="field"><label>You pay</label><input id="fiat" value="1,000" inputmode="numeric"></div>'
         '<div style="display:flex;align-items:center;gap:12px;margin:6px 0 4px">@@'
         '<span style="color:var(--faint);font-size:12.5px">1 GBP = 12.40 $FTR · held for 30s</span></div>'
         '<div class="field"><label>You receive</label><input id="ftr" value="12,400" readonly></div>'
         '<div class="quick"><button data-f="100">£100</button><button data-f="500">£500</button>'
         '<button data-f="1000">£1,000</button><button data-f="5000">£5,000</button></div>'
         '<div class="line"><span>Conversion fee (0.5%)</span><b id="cFee">62</b></div>'
         '<div class="line"><span>Credited</span><b id="cNet">12,338 $FTR</b></div>'
         '<div class="line"><span>Settles</span><b>Instantly</b></div>'
         '@@</div></div>',
         ic("swap", "ic"),
         btn("Convert to $FTR", tag="button",
             extra='id="convertBtn" style="width:100%;justify-content:space-between;margin-top:18px"'))]

buy.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
             '<div class="k-label">Payment method</div>'
             '<button class="netsel" type="button" id="paySel" style="margin-top:12px">'
             '<span class="coin lime">@@</span>'
             '<span style="min-width:0"><span class="k">Paying with</span>'
             '<span class="v" id="payName">Visa ·· 4417</span></span>'
             '<span class="chev"></span></button>'
             '<div class="line" style="margin-top:18px"><span>Daily limit</span><b>£25,000</b></div>'
             '<div class="line"><span>Remaining today</span><b>£24,000</b></div>'
             '<div class="line"><span>Currency</span><b>GBP</b></div>'
             '<p style="font-size:11.5px;color:var(--faint);font-weight:300;margin-top:16px;line-height:1.6">'
             'Prototype build — no card is charged.</p>'
             '</div></div>', ic("bank", "ic")))

BUY_JS = r"""
var fi = el('fiat'), fo = el('ftr');
function conv(){
  var v = num(fi.value), gross = v * 12.4, fee = gross * 0.005;
  fo.value = money(gross);
  el('cFee').textContent = money(fee);
  el('cNet').textContent = money(gross - fee) + ' $FTR';
}
fi.addEventListener('input', function(){
  var v = fi.value.replace(/[^0-9]/g, '');
  fi.value = v ? (+v).toLocaleString('en-US') : '';
  conv();
});
document.querySelectorAll('[data-f]').forEach(function(b){
  b.addEventListener('click', function(){ fi.value = (+b.dataset.f).toLocaleString('en-US'); conv(); });
});
el('convertBtn').addEventListener('click', function(){
  var v = num(fi.value);
  if(v <= 0){ showToast('Enter an amount in GBP to convert.', 'error'); return; }
  var net = FT.convertGbp(v);
  showToast('£' + v.toLocaleString('en-US') + ' converted into ' + net.toLocaleString('en-US')
    + ' $FTR.', 'success');
});
el('paySel').addEventListener('click', function(){
  openModal('<h3 class="ft-modal-title">Payment method</h3>'
    + '<div class="ft-modal-card">'
    + '<div class="m-row"><span>Visa ·· 4417</span><b style="color:var(--lime)">Instant</b></div>'
    + '<div class="m-row"><span>Mastercard ·· 9082</span><b>Instant</b></div>'
    + '<div class="m-row"><span>Open banking</span><b>~10 sec</b></div>'
    + '<div class="m-row total"><span>Bank transfer</span><b>1 working day</b></div></div>');
});
conv();
"""
shell("buy.html", "Buy $FTR — Fantrade", "Buy", "coin", "".join(buy), BUY_JS)


# ══════════════════════════════════════════════════════════════════
# ACTIVITY — balance history, the ledger, supply, deposit / withdraw
# ══════════════════════════════════════════════════════════════════
act = [T('<div class="bezel c7" data-reveal><div class="core pad">'
         '<div class="rowhead"><div class="k-label">Balance history</div>'
         '<div class="range" id="walRange" style="margin-left:auto">'
         '<button type="button" aria-pressed="true" data-r="1D">1D</button>'
         '<button type="button" aria-pressed="false" data-r="1W">1W</button>'
         '<button type="button" aria-pressed="false" data-r="1M">1M</button>'
         '<button type="button" aria-pressed="false" data-r="1Y">1Y</button>'
         '<button type="button" aria-pressed="false" data-r="All">All</button></div></div>'
         '<div class="bal-delta" id="walDelta" style="margin-bottom:10px">@@<span>2.35% today</span></div>'
         '<div class="bal-chart" id="walChart" style="height:190px"></div>'
         '<div class="b-row" style="margin-top:20px"><span>Locked in entries</span>'
         '<b data-bind="locked">5,000</b></div>'
         '<div class="b-row"><span>Held in shares</span><b data-bind="assets">917,000</b></div>'
         '<div class="b-row total"><span>Net worth</span><b data-bind="net">1,050,450</b></div>'
         '<div style="display:flex;gap:10px;margin-top:22px;flex-wrap:wrap">@@@@</div>'
         '</div></div>', ic("arrow", "ic"),
         btn("Deposit", tag="button", extra='id="depositBtn" style="flex:1;justify-content:space-between"'),
         btn("Withdraw", "btn-glass", tag="button",
             extra='id="withdrawBtn" style="flex:1;justify-content:space-between"'))]

act.append(T('<div class="bezel c5" data-reveal><div class="core pad">'
             '<div class="k-label">Circulating supply</div>'
             '<div class="dist" style="margin-top:10px">'
             '<svg viewBox="0 0 42 42" style="width:112px;height:112px;flex:none">'
             '<circle cx="21" cy="21" r="15.9" fill="none" stroke="rgba(255,255,255,.07)" stroke-width="5"/>'
             '<circle cx="21" cy="21" r="15.9" fill="none" stroke="#C4F82A" stroke-width="5" '
             'stroke-dasharray="46 54" stroke-dashoffset="25" transform="rotate(-90 21 21)"/>'
             '<circle cx="21" cy="21" r="15.9" fill="none" stroke="#FF6A1F" stroke-width="5" '
             'stroke-dasharray="28 72" stroke-dashoffset="79" transform="rotate(-90 21 21)"/>'
             '<circle cx="21" cy="21" r="15.9" fill="none" stroke="rgba(255,255,255,.28)" stroke-width="5" '
             'stroke-dasharray="14 86" stroke-dashoffset="51" transform="rotate(-90 21 21)"/></svg>'
             '<div class="key">'
             '<div class="kr"><i style="background:#C4F82A"></i>Held by fans<b>46%</b></div>'
             '<div class="kr"><i style="background:#FF6A1F"></i>Staked in rounds<b>28%</b></div>'
             '<div class="kr"><i style="background:rgba(255,255,255,.28)"></i>Rewards pool<b>14%</b></div>'
             '<div class="kr"><i style="background:rgba(255,255,255,.08)"></i>Treasury<b>12%</b></div>'
             '</div></div></div></div>'))

act.append(T('<div class="bezel c12" data-reveal><div class="core pad">'
             '<div class="rowhead"><div class="k-label">Transaction history</div>'
             '<a class="seeall" href="portfolio.html">Full ledger @@</a></div>'
             '<div id="txHistory"></div></div></div>', ic("arrow", "ic-sm")))

ACT_JS = r"""
var SERIES = {
  '1D': series(30, 0.12, 2.6, 11),
  '1W': series(34, 0.35, 3.4, 23),
  '1M': series(40, 0.9, 5.2, 47),
  '1Y': series(48, 1.9, 7.5, 91),
  'All': series(56, 2.6, 9.0, 137)
};
var DELTA = { '1D': 2.35, '1W': 6.10, '1M': 14.82, '1Y': 61.40, 'All': 184.20 };
var WORD = { '1D': 'today', '1W': 'this week', '1M': 'this month', '1Y': 'this year', 'All': 'all time' };
function paint(r){
  drawArea(el('walChart'), SERIES[r], DELTA[r] >= 0);
  el('walDelta').querySelector('span').textContent = DELTA[r].toFixed(2) + '% ' + WORD[r];
}
document.querySelectorAll('#walRange button').forEach(function(b){
  b.addEventListener('click', function(){
    document.querySelectorAll('#walRange button').forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
    b.setAttribute('aria-pressed', 'true');
    paint(b.dataset.r);
  });
});

var LICON = { BUY:'candle', SELL:'candle', STAKE:'bolt', PAYOUT:'trophy', CONVERT:'swap',
              DEPOSIT:'wallet', WITHDRAW:'bank', SEND:'send', SWAP:'swap', SETTLE:'trophy' };
function label(t){
  if(t.type === 'BUY')  return 'Bought ' + t.shares.toLocaleString('en-US') + ' ' + t.asset;
  if(t.type === 'SELL') return 'Sold ' + t.shares.toLocaleString('en-US') + ' ' + t.asset;
  if(t.type === 'STAKE') return 'Staked ' + t.asset;
  if(t.type === 'SEND') return 'Sent to ' + t.asset;
  if(t.type === 'WITHDRAW') return 'Withdrawn to ' + t.asset;
  if(t.type === 'SWAP') return 'Swapped ' + t.asset;
  if(t.type === 'CONVERT') return 'Added via ' + t.asset;
  if(t.type === 'DEPOSIT') return 'Added via direct deposit';
  return t.asset;
}
function renderHistory(){
  var s = FT.getState(), box = el('txHistory');
  if(!s.transactions || !s.transactions.length){
    box.innerHTML = '<div class="empty-state"><svg class="ic-xl" aria-hidden="true">'
      + '<use href="#i-receipt"/></svg>No movements yet.</div>';
    return;
  }
  box.innerHTML = s.transactions.slice(0, 14).map(function(t){
    var down = ['BUY','STAKE','SEND','WITHDRAW'].indexOf(t.type) > -1;
    return '<div class="trow"><span class="coin' + (down ? '' : ' lime') + '">'
      + '<svg class="ic" aria-hidden="true"><use href="#i-' + (LICON[t.type] || 'receipt') + '"/></svg></span>'
      + '<div class="bd"><div class="t">' + label(t) + '</div><div class="d">' + t.time + '</div></div>'
      + '<div class="a ' + (down ? 'down' : 'up') + '" style="color:' + (down ? 'var(--red)' : 'var(--lime)')
      + '">' + (down ? '-' : '+') + money(t.total) + '</div></div>';
  }).join('');
}

el('depositBtn').addEventListener('click', function(e){
  e.preventDefault();
  openModal('<h3 class="ft-modal-title">Deposit $FTR</h3>'
    + '<div class="field"><label>Amount ($FTR)</label><input id="depAmt" value="25,000" inputmode="numeric"></div>'
    + '<div class="quick"><button data-dep="5000">5K</button><button data-dep="25000">25K</button>'
    + '<button data-dep="50000">50K</button><button data-dep="100000">100K</button></div>'
    + '<div style="display:flex;gap:10px;margin-top:18px">'
    + '<button class="btn btn-lime" id="depGo" type="button" style="flex:1;justify-content:center">Confirm</button>'
    + '<button class="btn btn-glass" id="depNo" type="button" style="flex:1;justify-content:center">Cancel</button></div>');
  var inp = el('depAmt');
  document.querySelectorAll('[data-dep]').forEach(function(b){
    b.addEventListener('click', function(){ inp.value = (+b.dataset.dep).toLocaleString('en-US'); });
  });
  el('depNo').addEventListener('click', closeModal);
  el('depGo').addEventListener('click', function(){
    var a = num(inp.value);
    if(a <= 0){ showToast('Enter a valid amount.', 'error'); return; }
    FT.depositFtr(a); closeModal();
    showToast(money(a) + ' $FTR deposited.', 'success');
  });
});

el('withdrawBtn').addEventListener('click', function(e){
  e.preventDefault();
  var s = FT.getState();
  openModal('<h3 class="ft-modal-title">Withdraw $FTR</h3>'
    + '<div class="field"><label>Amount ($FTR)</label><input id="wdAmt" value="10,000" inputmode="numeric"></div>'
    + '<div class="ft-modal-card">'
    + '<div class="m-row"><span>Available</span><b>' + money(s.wallet.balance) + ' $FTR</b></div>'
    + '<div class="m-row"><span>Locked in entries</span><b>' + money(s.wallet.locked) + ' $FTR</b></div>'
    + '<div class="m-row total"><span>Withdrawal fee</span><b>0.5% · minimum 50 $FTR</b></div></div>'
    + '<div style="display:flex;gap:10px">'
    + '<button class="btn btn-lime" id="wdGo" type="button" style="flex:1;justify-content:center">Withdraw</button>'
    + '<button class="btn btn-glass" id="wdNo" type="button" style="flex:1;justify-content:center">Cancel</button></div>');
  el('wdNo').addEventListener('click', closeModal);
  el('wdGo').addEventListener('click', function(){
    try {
      var r = FT.sendFtr(num(el('wdAmt').value), 'Payout account (GBP)', 'withdraw');
      closeModal();
      showToast(money(r.sent) + ' $FTR withdrawn · ' + money(r.fee) + ' $FTR fee.', 'success');
    } catch(err){ showToast(err.message, 'error'); }
  });
});

paint('1D'); renderHistory();
window.addEventListener('fantrade:statechange', renderHistory);
"""
shell("activity.html", "Activity — Fantrade", "Activity", "receipt", "".join(act), ACT_JS)

print("built send.html + receive.html + swap.html + buy.html + activity.html")
