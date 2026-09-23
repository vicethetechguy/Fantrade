"""A card-free inbox with readable groups and an opaque sticky toolbar."""
HTML = '''<main><div class="utility-page inbox-page"><div class="inbox-sticky">
<header class="utility-intro"><div><h1>Notifications</h1><p>Your trades, club and account updates.</p></div>
<a class="inbox-settings" href="settings-alerts.html" aria-label="Notification settings">
<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="m9 3-1 3-3 1-2 5 2 5 3 1 1 3h6l1-3 3-1 2-5-2-5-3-1-1-3Z"/></svg></a></header>
<div class="wallet-tabs" aria-label="Notification categories" id="ntFilter">
<button class="wallet-chip" data-k="all" aria-pressed="true">All</button><button class="wallet-chip" data-k="settle" aria-pressed="false">Settlements</button>
<button class="wallet-chip" data-k="order" aria-pressed="false">Orders</button><button class="wallet-chip" data-k="club" aria-pressed="false">Club</button>
<button class="wallet-chip" data-k="system" aria-pressed="false">Account</button></div>
<div class="inbox-tools"><span id="ntTotal" role="status" aria-live="polite"></span><button class="inbox-read" id="ntRead" type="button">Mark all as read</button></div></div>
<div id="ntFeed"></div></div></main>'''

JS = r'''
var kind='all';
function esc(value){var span=document.createElement('span');span.textContent=String(value==null?'':value);return span.innerHTML.replace(/"/g,'&quot;');}
function unreadCount(){var count=FT.getState().notifications.filter(n=>!n.read).length;document.getElementById('ntTotal').textContent=count?count+' unread':'You’re all caught up';document.getElementById('ntRead').disabled=count===0;}
function renderFeed(){var list=FT.getState().notifications.filter(n=>kind==='all'||n.kind===kind),day=null,out=[];unreadCount();
  list.forEach(function(n){if(n.day!==day){day=n.day;out.push('<h2 class="inbox-day">'+esc(day)+'</h2>');}
    out.push('<button type="button" class="inbox-row '+(n.read?'':'unread')+'" data-id="'+esc(n.id)+'" aria-label="'+esc(n.title)+(n.read?'':', unread. Mark as read')+'">'
      +'<svg class="ic" aria-hidden="true"><use href="#i-'+esc(n.icon)+'"/></svg><span><strong>'+esc(n.title)+'</strong><span class="inbox-message">'+esc(n.msg)+'</span><span class="inbox-time">'+esc(n.time)+'</span></span>'
      +(n.amt?'<span class="inbox-amount '+(n.tone==='up'?'positive':n.tone==='down'?'negative':'')+'">'+esc(n.amt)+'</span>':'')+'</button>');
  });
  document.getElementById('ntFeed').innerHTML=out.join('')||'<div class="wallet-empty"><b>No notifications here</b>New updates in this category will appear here.</div>';
  document.querySelectorAll('.inbox-row').forEach(function(row){row.onclick=function(){FT.readOne(row.dataset.id);row.classList.remove('unread');row.setAttribute('aria-label',row.querySelector('strong').textContent);unreadCount();};});
}
document.querySelectorAll('[data-k]').forEach(function(b){b.onclick=function(){kind=b.dataset.k;document.querySelectorAll('[data-k]').forEach(x=>x.setAttribute('aria-pressed',x===b));renderFeed();};});
document.getElementById('ntRead').onclick=function(){FT.readAll();renderFeed();};
window.addEventListener('fantrade:statechange',renderFeed);renderFeed();
'''
