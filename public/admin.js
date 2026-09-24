/* Fantrade Admin.
 *
 * A separate app from the one managers use. It signs in with a normal
 * Fantrade account and then talks to the database only through the
 * ft_admin_* functions in supabase/09_admin.sql, each of which refuses
 * anyone who is not on the admin list. Nothing here is trusted: hiding a
 * button is manners, the database is the lock.
 *
 * Until 09_admin.sql has been run (or when the database cannot be reached)
 * the admin can open on sample data instead, clearly marked, so the screens
 * can be looked at. Sample data never mixes with real data.
 */
const CONFIG = {
  url: 'https://ajjwodnjcnmkzguospay.supabase.co',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqandvZG5qY25ta3pndW9zcGF5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAwOTI3NjMsImV4cCI6MjEwNTY2ODc2M30.7KUEO-9rzcWcvCezLw26WMyDQWvbCCy15zzk-wyTnrg',
  cdn: 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'
};
const FTR_USD = 0.1;                       // 1 $FTR = $0.10, as the app shows it
const LEVEL_SHARES = { 1: 500000, 2: 1000000 };

const app = document.getElementById('app');
let sb = null, mode = 'live', me = null, sessionEmail = '';
const cache = {};
const ui = { players: { status: 'all', q: '' }, claims: { q: '' }, managers: { q: '' }, fanplay: { status: 'all' } };

/* ── Small helpers ─────────────────────────────────────────────────── */
const esc = v => String(v == null ? '' : v).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const num = (n, d = 0) => (Number(n) || 0).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
function compact(n) {
  n = Number(n) || 0; const a = Math.abs(n);
  if (a >= 1e9) return (n / 1e9).toFixed(2).replace(/\.?0+$/, '') + 'B';
  if (a >= 1e6) return (n / 1e6).toFixed(2).replace(/\.?0+$/, '') + 'M';
  if (a >= 1e4) return (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'K';
  return num(n, a % 1 ? 2 : 0);
}
function usd(ftr) {
  const d = (Number(ftr) || 0) * FTR_USD, a = Math.abs(d);
  if (a >= 1e4) return '$' + compact(d);
  if (a >= 100) return '$' + num(d);
  return '$' + d.toFixed(a < 1 && a > 0 ? 3 : 2);
}
function day(iso) { if (!iso) return '—'; const d = new Date(iso); return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }); }
function ago(iso) {
  if (!iso) return '';
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 60) return 'just now'; if (s < 3600) return Math.floor(s / 60) + 'm ago';
  if (s < 86400) return Math.floor(s / 3600) + 'h ago'; if (s < 86400 * 7) return Math.floor(s / 86400) + 'd ago';
  return day(iso);
}
function initials(name) { const w = String(name || '?').trim().split(/\s+/); return ((w[0] || '?')[0] + (w.length > 1 ? w[w.length - 1][0] : '')).toUpperCase(); }
function avatar(name, size) {
  const hues = ['#1800ad', '#3a1fbf', '#0b5fae', '#5a2d9c', '#14418f', '#2c2396', '#7a2a8f'];
  let h = 0; for (const c of String(name)) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  const dim = size ? `;width:${size}px;height:${size}px;font-size:${Math.round(size / 2.8)}px` : '';
  return `<span class="av" style="background:${hues[h % hues.length]}${dim}">${esc(initials(name))}</span>`;
}
function claimCost(price, level) { return Math.round((Number(price) || 0) * LEVEL_SHARES[level || 1]); }
function greeting() { const h = new Date().getHours(); return h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening'; }
function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

/* ── Icons (24px, stroked) ─────────────────────────────────────────── */
const P = {
  overview: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
  players: '<path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
  claims: '<ellipse cx="9" cy="7" rx="6" ry="3"/><path d="M3 7v5c0 1.7 2.7 3 6 3s6-1.3 6-3V7"/><path d="M9 15v2c0 1.7 2.7 3 6 3s6-1.3 6-3v-5c0-1.6-2.4-2.9-5.5-3"/>',
  managers: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.6 3.4-5.5 6.5-5.5s5.7 1.9 6.5 5.5"/><path d="M16 4.6a3.5 3.5 0 010 6.8M18 14.8c1.9.7 3.1 2.4 3.5 5.2"/>',
  fanplay: '<circle cx="12" cy="12" r="9"/><path d="M12 7.5l3.8 2.8-1.4 4.5H9.6l-1.4-4.5z"/><path d="M12 3v4.5M20.6 9.6l-4.8.7M17.3 19.3l-2.9-4.5M6.7 19.3l2.9-4.5M3.4 9.6l4.8.7"/>',
  log: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  upload: '<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2"/>',
  download: '<path d="M12 4v12M7 11l5 5 5-5"/><path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
  x: '<path d="M6 6l12 12M18 6L6 18"/>',
  logout: '<path d="M15 4h3a2 2 0 012 2v12a2 2 0 01-2 2h-3"/><path d="M10 16l-4-4 4-4M6 12h10"/>',
  external: '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v4a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2h4"/>',
  pause: '<path d="M9 5v14M15 5v14"/>',
  play: '<path d="M8 5l11 7-11 7z"/>',
  trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 002 2h6a2 2 0 002-2l1-12M9 7V4h6v3"/>',
  edit: '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  alert: '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17h.01"/>',
  chevron: '<path d="M9 6l6 6-6 6"/>',
  lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/>',
  file: '<path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5"/>',
  check: '<path d="M5 12l5 5 9-10"/>',
  userx: '<circle cx="10" cy="8" r="3.5"/><path d="M3.5 20c.8-3.6 3.4-5.5 6.5-5.5 1.5 0 2.9.4 4 1.3"/><path d="M16 16l5 5M21 16l-5 5"/>'
};
const ic = (n, cls) => `<svg class="ic${cls ? ' ' + cls : ''}" viewBox="0 0 24 24" aria-hidden="true">${P[n] || ''}</svg>`;

/* ── Toasts, dialog, drawer ────────────────────────────────────────── */
function toast(msg, err) {
  const box = document.getElementById('toasts'); const t = document.createElement('div');
  t.className = 'toast' + (err ? ' err' : ''); t.innerHTML = ic(err ? 'alert' : 'check') + '<span>' + esc(msg) + '</span>';
  box.appendChild(t); setTimeout(() => t.remove(), err ? 6000 : 3400);
}
function scrim(on) { const s = document.getElementById('scrim'); if (s) s.classList.toggle('open', on); }
function openDialog(html, wide) {
  const d = document.getElementById('dialog');
  d.innerHTML = `<div class="dialog-box${wide ? ' wide' : ''}" role="dialog" aria-modal="true">${html}</div>`;
  scrim(true); requestAnimationFrame(() => d.classList.add('open'));
  const f = d.querySelector('[autofocus],input,button'); if (f) setTimeout(() => f.focus(), 60);
  return d.firstElementChild;
}
function closeDialog() { const d = document.getElementById('dialog'); if (!d) return; d.classList.remove('open'); d.innerHTML = ''; if (!document.getElementById('drawer').classList.contains('open')) scrim(false); }
function confirmBox({ title, body, ok = 'Confirm', danger }) {
  return new Promise(resolve => {
    const box = openDialog(`<h2>${esc(title)}</h2><p>${body}</p><div class="dialog-actions">
      <button class="btn btn-ghost" data-v="0">Cancel</button><button class="btn ${danger ? 'btn-danger' : 'btn-primary'}" data-v="1" autofocus>${esc(ok)}</button></div>`);
    box.addEventListener('click', e => { const b = e.target.closest('[data-v]'); if (!b) return; closeDialog(); resolve(b.dataset.v === '1'); });
  });
}
function openDrawer(html) {
  const d = document.getElementById('drawer'); d.innerHTML = html; d.classList.add('open'); scrim(true);
  const f = d.querySelector('input:not([readonly]),select,textarea'); if (f) setTimeout(() => f.focus(), 120);
  return d;
}
function closeDrawer() { const d = document.getElementById('drawer'); if (!d) return; d.classList.remove('open'); scrim(false); }
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  if (document.getElementById('dialog')?.classList.contains('open')) closeDialog(); else closeDrawer();
  document.getElementById('side')?.classList.remove('open');
});

/* ── Data ──────────────────────────────────────────────────────────── */
async function loadClient() {
  const mod = await Promise.race([import(CONFIG.cdn), new Promise((_, no) => setTimeout(() => no(new Error('timeout')), 8000))]);
  sb = mod.createClient(CONFIG.url, CONFIG.anonKey, { auth: { storageKey: 'fantrade-admin-auth', persistSession: true, autoRefreshToken: true } });
}
async function api(fn, args) {
  if (mode === 'sample') return SAMPLE.call(fn, args || {});
  const { data, error } = await sb.rpc(fn, args || {});
  if (error) throw new Error(error.message);
  return data;
}
const missingFn = e => /could not find the function|schema cache|does not exist/i.test(String(e && e.message));

/* ── Getting in ────────────────────────────────────────────────────── */
function gateShell(inner) {
  app.className = ''; app.removeAttribute('aria-busy');
  app.innerHTML = `<div class="gate">
    <section class="gate-art">
      <div class="brand"><img src="assets/fantrade-logo.png" alt="" width="30" height="30">Fantrade Admin</div>
      <div><h1>Run the market behind the game.</h1>
        <p>Clear footballers for listing, watch claims launch them onto the Exchange, look after managers, and keep an eye on every matchday.</p></div>
      <div class="gate-rows">
        <div class="gate-row">${ic('lock')}Only accounts on the admin list can get in.</div>
        <div class="gate-row">${ic('log')}Every change you make is written to the activity log.</div>
        <div class="gate-row">${ic('fanplay')}FanPlay settles from verified match data, never from a click.</div>
      </div>
    </section>
    <section class="gate-form"><div class="gate-card">${inner}</div></section></div>`;
}
function renderSignIn(opts = {}) {
  gateShell(`
    <h2>Sign in</h2><p>Use the Fantrade account that has admin access.</p>
    ${opts.offline ? `<div class="gate-note"><b>Can't reach Fantrade's database from here.</b> Check your connection, or look around with sample data.</div>` : ''}
    <form id="signin" novalidate>
      <div class="field"><label for="em">Email</label><input class="input" id="em" type="email" autocomplete="username" required></div>
      <div class="field"><label for="pw">Password</label><input class="input" id="pw" type="password" autocomplete="current-password" required></div>
      <p class="form-error" id="err">${esc(opts.error || '')}</p>
      <button class="btn btn-primary btn-block" ${opts.offline ? 'disabled' : ''}>Sign in</button>
    </form>
    <div class="gate-alt">Just want to see it? <button class="btn btn-ghost btn-sm" id="sample">Look around with sample data</button></div>`);
  document.getElementById('sample').onclick = enterSample;
  document.getElementById('signin').onsubmit = async e => {
    e.preventDefault();
    const btn = e.target.querySelector('button'), err = document.getElementById('err');
    const email = document.getElementById('em').value.trim(), password = document.getElementById('pw').value;
    if (!email || !password) { err.textContent = 'Enter your email and password.'; return; }
    btn.disabled = true; btn.textContent = 'Signing in…'; err.textContent = '';
    const { error } = await sb.auth.signInWithPassword({ email, password });
    if (error) { btn.disabled = false; btn.textContent = 'Sign in'; err.textContent = error.message; return; }
    afterSignIn();
  };
}
function grantSql(email) {
  return `insert into public.admins (user_id)\nselect id from auth.users where email = '${String(email || 'you@example.com').replace(/'/g, "''")}'\non conflict do nothing;`;
}
function renderGate(kind) {
  const setup = kind === 'setup';
  gateShell(`
    <h2>${setup ? 'One step left' : 'Not an admin yet'}</h2>
    <p>${setup ? "Fantrade's database doesn't have the admin functions yet." : `You're signed in as ${esc(sessionEmail)}, but this account isn't on the admin list.`}</p>
    <div class="gate-note">${setup
      ? `In Supabase, open the SQL editor and run <b>supabase/09_admin.sql</b>. Then add yourself as the first admin:`
      : `Someone with database access can add you in the Supabase SQL editor:`}
      <pre class="code">${esc(grantSql(sessionEmail))}</pre></div>
    <div class="grid">
      <button class="btn btn-primary btn-block" id="again">Check again</button>
      <button class="btn btn-block" id="sample">Look around with sample data</button>
      <button class="btn btn-ghost btn-block" id="out">Sign out</button>
    </div>`);
  document.getElementById('again').onclick = afterSignIn;
  document.getElementById('sample').onclick = enterSample;
  document.getElementById('out').onclick = signOut;
}
async function afterSignIn() {
  mode = 'live';
  const { data } = await sb.auth.getUser(); sessionEmail = data && data.user ? data.user.email : '';
  try { me = await api('ft_admin_whoami'); }
  catch (e) { if (missingFn(e)) return renderGate('setup'); return renderSignIn({ error: e.message }); }
  if (!me || !me.is_admin) return renderGate('notadmin');
  startShell();
}
function enterSample() {
  mode = 'sample'; me = { is_admin: true, role: 'admin', name: 'Sample admin', handle: 'sample_admin', email: 'sample@fantrade.app' };
  Object.keys(cache).forEach(k => delete cache[k]);
  startShell();
}
async function signOut() {
  if (mode === 'live' && sb) await sb.auth.signOut();
  mode = 'live'; me = null; Object.keys(cache).forEach(k => delete cache[k]);
  location.hash = ''; sb ? renderSignIn() : boot();
}

/* ── The shell ─────────────────────────────────────────────────────── */
const NAV = [
  ['overview', 'Overview', 'overview'], ['players', 'Players', 'players'], ['claims', 'Claims', 'claims'],
  ['managers', 'Managers', 'managers'], ['fanplay', 'FanPlay', 'fanplay'], ['log', 'Activity log', 'log']
];
function startShell() {
  app.className = ''; app.removeAttribute('aria-busy');
  app.innerHTML = `<div class="shell">
    <aside class="side" id="side" aria-label="Admin">
      <div class="side-brand"><img src="assets/fantrade-logo.png" alt="">Fantrade<small>Admin</small></div>
      <nav class="nav" id="nav">${NAV.map(([k, label, icon]) => `<a href="#/${k}" data-k="${k}">${ic(icon)}<span>${label}</span><span class="count" hidden></span></a>`).join('')}</nav>
      <div class="side-foot">
        <a class="side-link" href="dashboard.html" target="_blank" rel="noopener">${ic('external')}Open the Fantrade app</a>
        <div class="me">${avatar(me.name || me.handle)}<div class="me-text"><b>${esc(me.name || me.handle)}</b><small>${esc(me.role === 'viewer' ? 'Viewer' : 'Admin')} · ${esc(me.email || '@' + me.handle)}</small></div>
          <button class="icon-btn" id="out" title="Sign out" aria-label="Sign out">${ic('logout')}</button></div>
      </div>
    </aside>
    <div class="content">
      <header class="topbar"><button class="icon-btn" id="menu" aria-label="Open menu">${ic('menu')}</button>
        <img src="assets/fantrade-logo.png" alt=""><b>Admin</b></header>
      <main class="main" id="view"></main>
    </div></div>
    <div class="scrim" id="scrim"></div><aside class="drawer" id="drawer" aria-label="Details"></aside><div class="dialog" id="dialog"></div>`;
  document.getElementById('out').onclick = signOut;
  document.getElementById('menu').onclick = () => { document.getElementById('side').classList.add('open'); scrim(true); };
  document.getElementById('scrim').onclick = () => { closeDialog(); closeDrawer(); document.getElementById('side').classList.remove('open'); };
  window.onhashchange = route;
  route();
  refreshCounts();
}
function banner() {
  return mode === 'sample'
    ? `<div class="banner">${ic('info')}<span><b>Sample data.</b> Nothing here is real, and nothing you change is saved to Fantrade.</span>
       <button class="btn btn-sm" id="leaveSample">Sign in for real</button></div>` : '';
}
function head(title, sub, actions = '') {
  return banner() + `<div class="page-head"><div><h1>${title}</h1>${sub ? `<p>${sub}</p>` : ''}</div><div class="page-actions">${actions}</div></div>`;
}
function wireBanner() { const b = document.getElementById('leaveSample'); if (b) b.onclick = () => { mode = 'live'; me = null; location.hash = ''; boot(); }; }
async function refreshCounts() {
  try {
    const o = cache.overview || (cache.overview = await api('ft_admin_overview'));
    setCount('players', o.open_to_claim); setCount('fanplay', o.fanplay_pending);
  } catch (e) { /* counts are a nicety */ }
}
function setCount(k, n) { const el = document.querySelector(`#nav a[data-k="${k}"] .count`); if (!el) return; el.hidden = !n; el.textContent = n; }
const VIEWS = {};
function route() {
  const k = (location.hash.replace(/^#\/?/, '').split('/')[0]) || 'overview';
  const key = VIEWS[k] ? k : 'overview';
  document.querySelectorAll('#nav a').forEach(a => { if (a.dataset.k === key) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
  document.getElementById('side')?.classList.remove('open'); closeDrawer(); closeDialog();
  const view = document.getElementById('view'); view.scrollTop = 0; window.scrollTo(0, 0);
  VIEWS[key](view).catch(e => {
    view.innerHTML = head('Something went wrong') + `<div class="card empty"><b>That didn't load.</b>${esc(e.message)}</div>`; wireBanner();
  });
}
function loading(view, title, sub) { view.innerHTML = head(title, sub) + `<div class="card empty"><b>Loading…</b></div>`; wireBanner(); }

/* ── Overview ──────────────────────────────────────────────────────── */
VIEWS.overview = async view => {
  const who = (me.name || '').split(' ')[0];
  loading(view, 'Overview');
  const o = cache.overview = await api('ft_admin_overview');
  setCount('players', o.open_to_claim); setCount('fanplay', o.fanplay_pending);
  const attn = [
    [o.fanplay_pending, 'FanPlay entries waiting on results', '#/fanplay'],
    [o.paused, o.paused === 1 ? 'player paused from claiming' : 'players paused from claiming', '#/players'],
    [o.suspended, o.suspended === 1 ? 'manager suspended' : 'managers suspended', '#/managers'],
  ].filter(a => a[0] > 0);
  view.innerHTML = head(`${greeting()}${who && mode === 'live' ? ', ' + esc(who) : ''}.`, "Here's where Fantrade stands right now.") + `
    <div class="kpis">
      <div class="kpi lead"><span class="kpi-label">${ic('claims')}Claim revenue</span><span class="kpi-val num">${compact(o.claims_paid)} <small style="font-size:14px">$FTR</small></span>
        <span class="kpi-sub">≈ ${usd(o.claims_paid)} · ${compact(o.claims_burned)} burned</span></div>
      <div class="kpi"><span class="kpi-label">${ic('managers')}Managers</span><span class="kpi-val num">${num(o.managers)}</span><span class="kpi-sub">+${num(o.managers_7d)} this week</span></div>
      <div class="kpi"><span class="kpi-label">${ic('claims')}$FTR in wallets</span><span class="kpi-val num">${compact(o.wallet_ftr)}</span><span class="kpi-sub">≈ ${usd(o.wallet_ftr)} · ${compact(o.locked_ftr)} locked</span></div>
      <div class="kpi"><span class="kpi-label">${ic('players')}Open to claim</span><span class="kpi-val num">${num(o.open_to_claim)}</span><span class="kpi-sub">${num(o.paused)} paused</span></div>
      <div class="kpi"><span class="kpi-label">${ic('overview')}Players trading</span><span class="kpi-val num">${num(o.trading)}</span><span class="kpi-sub">${num(o.claims)} launched by claims</span></div>
      <div class="kpi"><span class="kpi-label">${ic('fanplay')}FanPlay live</span><span class="kpi-val num">${num(o.fanplay_active)}</span><span class="kpi-sub">${num(o.fanplay_pending)} awaiting settlement</span></div>
    </div>
    <div class="two">
      <section class="card"><div class="card-head"><div><h2>Claims, last 14 days</h2><p>Players launched each day by a manager's claim</p></div></div>
        <div class="chart" id="chart"></div></section>
      <section class="card"><div class="card-head"><div><h2>Needs attention</h2><p>Things waiting on someone</p></div></div>
        ${attn.length ? `<div class="attn">${attn.map(a => `<a href="${a[2]}"><b class="num">${num(a[0])}</b><span>${a[1]}</span>${ic('chevron')}</a>`).join('')}</div>`
          : `<div class="empty"><b>All clear.</b>Nothing is waiting on you right now.</div>`}</section>
    </div>
    <section class="card" style="margin-top:16px"><div class="card-head"><div><h2>Recent activity</h2><p>Claims, sign-ups and admin changes</p></div>
      <a class="btn btn-sm" href="#/log">Activity log</a></div>
      ${(o.recent || []).length ? `<div class="feed">${o.recent.map(feedRow).join('')}</div>` : `<div class="empty"><b>Quiet so far.</b>Activity shows up here as it happens.</div>`}
    </section>`;
  wireBanner();
  const ch = document.getElementById('chart'); drawBars(ch, o.claims_by_day || []);
  window.onresize = debounce(() => { if (document.body.contains(ch)) drawBars(ch, o.claims_by_day || []); }, 150);
};
function feedRow(r) {
  const icon = r.kind === 'claim' ? 'claims' : r.kind === 'signup' ? 'managers' : 'edit';
  return `<div class="feed-row"><span class="feed-dot ${r.kind}">${ic(icon)}</span>
    <div class="feed-text"><b>@${esc(r.who || 'someone')}</b> ${esc(humanAction(r.what))}<small>${ago(r.at)}</small></div>
    ${r.amount != null ? `<span class="feed-amt num">${compact(r.amount)} $FTR</span>` : ''}</div>`;
}
/* One series, one hue, no legend: the title names it. Every bar has a hover
   target taller than the bar and a tooltip with the exact numbers. */
function drawBars(el, rows) {
  if (!el) return;
  const W = Math.max(300, Math.round(el.clientWidth || 640)), H = 220, L = 30, B = 26, T = 10, max = Math.max(1, ...rows.map(r => r.claims));
  const step = Math.max(1, Math.ceil(max / 3)), top = step * 3;
  const cw = (W - L) / Math.max(1, rows.length), bw = Math.min(26, cw * .56);
  const y = v => T + (H - B - T) * (1 - v / top);
  let g = '';
  for (let v = 0; v <= top; v += step) g += `<line class="grid-line" x1="${L}" x2="${W}" y1="${y(v)}" y2="${y(v)}"/><text class="axis" x="${L - 8}" y="${y(v) + 3.5}" text-anchor="end">${v}</text>`;
  const bars = rows.map((r, i) => {
    const x = L + cw * i + (cw - bw) / 2, h = Math.max(r.claims ? 3 : 0, (H - B - T) * r.claims / top);
    const label = new Date(r.day).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
    return `<g data-i="${i}"><rect class="hit" x="${L + cw * i}" y="${T}" width="${cw}" height="${H - B - T}" data-i="${i}"/>
      <path class="bar" d="${h ? `M${x},${y(0)} V${y(0) - h + 4} q0,-4 4,-4 h${bw - 8} q4,0 4,4 V${y(0)} Z` : ''}"><title>${label}: ${r.claims} claims</title></path>
      ${(rows.length - 1 - i) % (W < 520 ? 4 : 2) ? '' : `<text class="axis" x="${L + cw * i + cw / 2}" y="${H - 6}" text-anchor="middle">${label}</text>`}</g>`;
  }).join('');
  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Claims per day for the last 14 days">${g}${bars}</svg><div class="tip" id="tip"></div>`;
  const tip = el.querySelector('#tip'), svg = el.querySelector('svg');
  svg.addEventListener('mousemove', e => {
    const g = e.target.closest('g[data-i]'); el.querySelectorAll('.bar.on').forEach(b => b.classList.remove('on'));
    if (!g) { tip.classList.remove('show'); return; }
    const hit = g.querySelector('.hit'), r = rows[+g.dataset.i], bar = g.querySelector('.bar'); bar.classList.add('on');
    const box = el.getBoundingClientRect(), hb = hit.getBoundingClientRect();
    tip.innerHTML = `<b>${new Date(r.day).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' })}</b><br>${r.claims} ${r.claims === 1 ? 'claim' : 'claims'} · ${compact(r.paid)} $FTR`;
    tip.style.left = (hb.left - box.left + hb.width / 2) + 'px';
    tip.style.top = (y(r.claims) * box.height / H - 8) + 'px';
    tip.classList.add('show');
  });
  svg.addEventListener('mouseleave', () => { tip.classList.remove('show'); el.querySelectorAll('.bar.on').forEach(b => b.classList.remove('on')); });
}
function humanAction(a) {
  const map = { 'players.upsert': 'updated the player list', 'player.pause': 'paused a player', 'player.reopen': 'reopened a player',
    'player.remove': 'removed a player', 'manager.suspend': 'suspended a manager', 'manager.reinstate': 'reinstated a manager' };
  const [act, ...rest] = String(a || '').replace(/lst-/g, '').split(' · ');
  return (map[act] || act) + (rest.length ? ' · ' + rest.join(' · ') : '');
}

/* ── Players (eligibility) ─────────────────────────────────────────── */
const STATUS_LABEL = { open: 'Open to claim', paused: 'Paused', claimed: 'Claimed' };
VIEWS.players = async view => {
  loading(view, 'Players');
  cache.players = await api('ft_admin_players');
  drawPlayers(view);
};
function drawPlayers(view) {
  const all = cache.players || [], st = ui.players;
  const counts = { all: all.length, open: 0, paused: 0, claimed: 0 }; all.forEach(p => counts[p.status]++);
  const q = st.q.toLowerCase();
  const rows = all.filter(p => (st.status === 'all' || p.status === st.status)
    && (!q || [p.name, p.ticker, p.club, p.league].join(' ').toLowerCase().includes(q)));
  const canWrite = me.role !== 'viewer';
  view.innerHTML = head('Players', 'Who managers are allowed to claim. A player has to be on this list before anyone can launch their Activity Shares.',
    `<button class="btn" id="tmpl">${ic('download')}Template</button>
     ${canWrite ? `<button class="btn" id="upl">${ic('upload')}Upload CSV</button><button class="btn btn-primary" id="add">${ic('plus')}Add player</button>` : ''}`) + `
    <div class="toolbar">
      <label class="search">${ic('search')}<span class="sr">Search players</span><input class="input" id="pq" type="search" placeholder="Search name, ticker or club" value="${esc(st.q)}"></label>
      <div class="chips" role="group" aria-label="Status">${['all', 'open', 'paused', 'claimed'].map(k =>
        `<button class="chip" data-s="${k}" aria-pressed="${st.status === k}">${k === 'all' ? 'All' : STATUS_LABEL[k]} <i>${counts[k]}</i></button>`).join('')}</div>
    </div>
    <div class="table-wrap"><div class="table-scroll"><table class="t">
      <thead><tr><th>Player</th><th>Club</th><th>Pos</th><th class="r">Reference price</th><th class="r">5% claim costs</th><th>Status</th><th class="r"><span class="sr">Actions</span></th></tr></thead>
      <tbody>${rows.map(p => playerRow(p, canWrite)).join('') || `<tr><td colspan="7"><div class="empty"><b>No players here.</b>${all.length ? 'Try another filter or search.' : 'Upload a CSV or add your first player.'}</div></td></tr>`}</tbody>
    </table></div><div class="table-foot">${rows.length} of ${all.length} players · Prices in $FTR, 1 $FTR = $0.10</div></div>`;
  wireBanner();
  const pq = document.getElementById('pq');
  pq.oninput = debounce(() => { st.q = pq.value; drawPlayers(view); const n = document.getElementById('pq'); n.focus(); n.setSelectionRange(n.value.length, n.value.length); }, 180);
  view.querySelectorAll('[data-s]').forEach(b => b.onclick = () => { st.status = b.dataset.s; drawPlayers(view); });
  document.getElementById('tmpl').onclick = downloadTemplate;
  if (canWrite) { document.getElementById('upl').onclick = openUpload; document.getElementById('add').onclick = () => editPlayer(null); }
  view.querySelector('tbody').onclick = async e => {
    const b = e.target.closest('[data-act]'); if (!b) return;
    const p = all.find(x => x.listing_id === b.dataset.id); if (!p) return;
    if (b.dataset.act === 'edit') editPlayer(p);
    if (b.dataset.act === 'pause' || b.dataset.act === 'reopen') {
      try { await api('ft_admin_set_open', { p_listing: p.listing_id, p_open: b.dataset.act === 'reopen' });
        toast(`${p.name} ${b.dataset.act === 'reopen' ? 'is open to claim again' : 'is paused'}`); delete cache.overview; await reloadPlayers(); refreshCounts(); }
      catch (err) { toast(err.message, true); }
    }
    if (b.dataset.act === 'remove') {
      const ok = await confirmBox({ title: `Remove ${p.name}?`, body: `${esc(p.name)} (${esc(p.ticker)}) comes off the list and can no longer be claimed. You can add them again later.`, ok: 'Remove player', danger: true });
      if (!ok) return;
      try { await api('ft_admin_remove_player', { p_listing: p.listing_id }); toast(`${p.name} removed`); delete cache.overview; await reloadPlayers(); refreshCounts(); }
      catch (err) { toast(err.message, true); }
    }
  };
}
async function reloadPlayers() { cache.players = await api('ft_admin_players'); const v = document.getElementById('view'); if (location.hash.startsWith('#/players')) drawPlayers(v); }
function playerRow(p, canWrite) {
  const claimed = p.status === 'claimed';
  const acts = !canWrite ? '' : claimed ? `<a class="btn btn-ghost btn-sm" href="#/claims">View claim</a>` : `
    <button class="icon-btn" data-act="edit" data-id="${esc(p.listing_id)}" title="Edit" aria-label="Edit ${esc(p.name)}">${ic('edit')}</button>
    <button class="icon-btn" data-act="${p.status === 'open' ? 'pause' : 'reopen'}" data-id="${esc(p.listing_id)}" title="${p.status === 'open' ? 'Pause' : 'Reopen'}" aria-label="${p.status === 'open' ? 'Pause' : 'Reopen'} ${esc(p.name)}">${ic(p.status === 'open' ? 'pause' : 'play')}</button>
    <button class="icon-btn" data-act="remove" data-id="${esc(p.listing_id)}" title="Remove" aria-label="Remove ${esc(p.name)}">${ic('trash')}</button>`;
  return `<tr>
    <td><div class="who">${avatar(p.name)}<div class="who-text"><b>${esc(p.name)}</b><small><span class="tick">${esc(p.ticker)}</span>${p.kind === 'COACH' ? ' · Coach' : ''}</small></div></div></td>
    <td><div class="who-text"><b>${esc(p.club || '—')}</b><small>${esc(p.league || '')}</small></div></td>
    <td>${esc(p.position || '—')}</td>
    <td class="r money num"><b>${num(p.reference_value, 2)}</b><small>${usd(p.reference_value)} a share</small></td>
    <td class="r money num"><b>${compact(claimCost(p.reference_value, 1))}</b><small>≈ ${usd(claimCost(p.reference_value, 1))}</small></td>
    <td><span class="pill ${p.status}">${STATUS_LABEL[p.status]}</span>${claimed && p.claimed_by ? `<small class="faint" style="display:block;margin-top:4px">by @${esc(p.claimed_by)}</small>` : ''}</td>
    <td class="r"><div class="row-actions">${acts}</div></td></tr>`;
}
const POSITIONS = [['GK', 'Goalkeeper'], ['DEF', 'Defender'], ['MID', 'Midfielder'], ['FWD', 'Forward'], ['MGR', 'Manager / coach']];
function editPlayer(p) {
  const isNew = !p; p = p || { ticker: 'F', name: '', kind: 'PLAYER', club: '', league: '', position: 'FWD', reference_value: '' };
  const d = openDrawer(`
    <div class="drawer-head"><div><h2>${isNew ? 'Add a player' : 'Edit ' + esc(p.name)}</h2>
      <p>${isNew ? 'They go on the list open to claim straight away.' : 'Changes apply until someone claims them.'}</p></div>
      <button class="icon-btn" data-close aria-label="Close">${ic('x')}</button></div>
    <form class="drawer-body" id="pf" novalidate>
      <div class="field"><label for="f-name">Full name</label><input class="input" id="f-name" required value="${esc(p.name)}" placeholder="e.g. Victor Osimhen"></div>
      <div class="grid-2">
        <div class="field"><label for="f-ticker">F-ticker</label><input class="input" id="f-ticker" required value="${esc(p.ticker)}" ${isNew ? '' : 'readonly'} maxlength="7" style="text-transform:uppercase"></div>
        <div class="field"><label for="f-kind">Type</label><select class="select" id="f-kind"><option value="PLAYER"${p.kind !== 'COACH' ? ' selected' : ''}>Player</option><option value="COACH"${p.kind === 'COACH' ? ' selected' : ''}>Coach</option></select></div>
      </div>
      <p class="hint">${isNew ? 'F plus 2–6 letters or digits. It can never be changed once issued.' : 'Tickers are permanent once issued.'}</p>
      <div class="grid-2">
        <div class="field"><label for="f-club">Club</label><input class="input" id="f-club" value="${esc(p.club || '')}" placeholder="e.g. Galatasaray"></div>
        <div class="field"><label for="f-league">League</label><input class="input" id="f-league" value="${esc(p.league || '')}" placeholder="e.g. Süper Lig"></div>
      </div>
      <div class="grid-2">
        <div class="field"><label for="f-pos">Position</label><select class="select" id="f-pos">${POSITIONS.map(([v, l]) => `<option value="${v}"${p.position === v ? ' selected' : ''}>${l}</option>`).join('')}</select></div>
        <div class="field"><label for="f-price">Reference price ($FTR a share)</label><input class="input num" id="f-price" inputmode="decimal" value="${esc(p.reference_value)}" placeholder="e.g. 41.30"></div>
      </div>
      <div class="callout" id="f-calc">${ic('info')}<span></span></div>
      <p class="form-error" id="f-err"></p>
    </form>
    <div class="drawer-foot"><button class="btn btn-ghost" data-close>Cancel</button><button class="btn btn-primary" id="f-save">${isNew ? 'Add player' : 'Save changes'}</button></div>`);
  const calc = () => {
    const v = parseFloat(d.querySelector('#f-price').value);
    d.querySelector('#f-calc span').innerHTML = v > 0
      ? `≈ <b>${usd(v)}</b> a share. A 5% claim (500,000 shares) costs <b>${num(claimCost(v, 1))} $FTR</b> (≈ ${usd(claimCost(v, 1))}); 10% costs ${num(claimCost(v, 2))} $FTR.`
      : 'Set a reference price to see what claiming this player will cost.';
  };
  calc(); d.querySelector('#f-price').oninput = calc;
  d.querySelectorAll('[data-close]').forEach(b => b.onclick = e => { e.preventDefault(); closeDrawer(); });
  const save = async e => {
    e && e.preventDefault();
    const row = { ticker: d.querySelector('#f-ticker').value.trim().toUpperCase(), name: d.querySelector('#f-name').value.trim(),
      kind: d.querySelector('#f-kind').value, club: d.querySelector('#f-club').value.trim(), league: d.querySelector('#f-league').value.trim(),
      position: d.querySelector('#f-pos').value, reference_value: d.querySelector('#f-price').value.trim() };
    const problem = validateRow(row); const err = d.querySelector('#f-err');
    if (problem) { err.textContent = problem; return; }
    const btn = d.querySelector('#f-save'); btn.disabled = true; err.textContent = '';
    try {
      const res = await api('ft_admin_upsert_players', { p_rows: [row] });
      if (res.skipped && res.skipped.length) { err.textContent = res.skipped[0].reason; btn.disabled = false; return; }
      toast(isNew ? `${row.name} is open to claim` : `${row.name} updated`); closeDrawer(); delete cache.overview; await reloadPlayers(); refreshCounts();
    } catch (x) { err.textContent = x.message; btn.disabled = false; }
  };
  d.querySelector('#f-save').onclick = save; d.querySelector('#pf').onsubmit = save;
}
function validateRow(r) {
  if (!/^F[A-Z0-9]{2,6}$/.test(r.ticker)) return 'Ticker must be F plus 2–6 letters or digits, e.g. FOSIM.';
  if (!r.name || r.name.length < 2) return 'Add the player\'s name.';
  if (!['PLAYER', 'COACH'].includes(r.kind)) return 'Type must be Player or Coach.';
  const v = parseFloat(String(r.reference_value).replace(/[$,\s]/g, ''));
  if (!(v > 0)) return 'Reference price must be above 0.';
  if (r.position && !POSITIONS.some(([p]) => p === r.position)) return 'Position must be GK, DEF, MID, FWD or MGR.';
  return '';
}

/* ── CSV upload ────────────────────────────────────────────────────── */
const TEMPLATE = 'ticker,name,kind,club,league,position,reference_value\n'
  + 'FOSIM,Victor Osimhen,PLAYER,Galatasaray,Süper Lig,FWD,41.30\n'
  + 'FSHAW,Khadija Shaw,PLAYER,Manchester City,WSL,FWD,32.50\n';
function downloadFile(name, text) {
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob(['﻿' + text], { type: 'text/csv;charset=utf-8' }));
  a.download = name; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
}
function downloadTemplate() { downloadFile('fantrade-players-template.csv', TEMPLATE); }
function parseCsv(text) {
  text = text.replace(/^﻿/, ''); const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
    else if (c === '"') q = true;
    else if (c === ',' || c === ';' || c === '\t') { row.push(cell); cell = ''; }
    else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(cell); rows.push(row); row = []; cell = ''; }
    else cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows.filter(r => r.some(c => c.trim() !== ''));
}
const HEADERS = { ticker: ['ticker', 'symbol', 'fticker'], name: ['name', 'player', 'fullname', 'playername'], kind: ['kind', 'type'],
  club: ['club', 'team'], league: ['league', 'competition'], position: ['position', 'pos'],
  reference_value: ['referencevalue', 'reference', 'referenceprice', 'price', 'value'] };
function rowsFromCsv(text) {
  const grid = parseCsv(text); if (!grid.length) throw new Error('That file is empty.');
  const hdr = grid[0].map(h => h.toLowerCase().replace(/[^a-z]/g, ''));
  const idx = {}; for (const [k, names] of Object.entries(HEADERS)) idx[k] = hdr.findIndex(h => names.includes(h));
  if (idx.ticker < 0 || idx.name < 0 || idx.reference_value < 0) throw new Error('The first row needs at least these columns: ticker, name, reference_value.');
  const seen = new Set(), existing = new Map((cache.players || []).map(p => [p.ticker, p]));
  return grid.slice(1).map((cells, i) => {
    const get = k => idx[k] >= 0 ? String(cells[idx[k]] || '').trim() : '';
    let kind = get('kind').toUpperCase(); if (['MANAGER', 'MGR', 'COACH'].includes(kind)) kind = 'COACH'; if (!kind) kind = 'PLAYER';
    let pos = get('position').toUpperCase(); pos = { GOALKEEPER: 'GK', DEFENDER: 'DEF', MIDFIELDER: 'MID', FORWARD: 'FWD', STRIKER: 'FWD', MANAGER: 'MGR', COACH: 'MGR' }[pos] || pos || (kind === 'COACH' ? 'MGR' : 'FWD');
    const r = { line: i + 2, ticker: get('ticker').toUpperCase(), name: get('name'), kind, club: get('club'), league: get('league'), position: pos,
      reference_value: get('reference_value').replace(/[$,\s]/g, '') };
    r.problem = validateRow(r);
    if (!r.problem && seen.has(r.ticker)) r.problem = 'This ticker is in the file twice.';
    seen.add(r.ticker);
    const ex = existing.get(r.ticker);
    if (!r.problem && ex && ex.status === 'claimed') r.problem = 'Already launched, so it will be skipped.';
    r.update = !r.problem && !!ex;
    return r;
  });
}
function openUpload() {
  const box = openDialog(`<h2>Upload players</h2><p>Add or update the players managers can claim, from a CSV file.</p>
    <div class="upload-body" id="ub">
      <label class="drop" id="drop" tabindex="0">${ic('upload')}<b>Drop a CSV here, or choose a file</b>
        <span>Columns: ticker, name, kind, club, league, position, reference_value</span>
        <input type="file" id="file" accept=".csv,text/csv" hidden></label>
      <p class="hint" style="margin-top:12px">Players already on the list are updated. Anyone who has already launched is left alone. <button class="btn btn-ghost btn-sm" id="tmpl2">${ic('download')}Download the template</button></p>
    </div>
    <div class="dialog-actions" id="ua"><button class="btn btn-ghost" data-close>Cancel</button></div>`, true);
  const drop = box.querySelector('#drop'), input = box.querySelector('#file');
  box.querySelector('#tmpl2').onclick = downloadTemplate;
  box.addEventListener('click', e => { if (e.target.closest('[data-close]')) closeDialog(); });
  drop.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); input.click(); } };
  ['dragenter', 'dragover'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add('over'); }));
  ['dragleave', 'drop'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.remove('over'); }));
  drop.addEventListener('drop', e => { const f = e.dataTransfer.files[0]; if (f) readFile(f); });
  input.onchange = () => { if (input.files[0]) readFile(input.files[0]); };
  function readFile(f) {
    if (f.size > 2e6) { toast('That file is over 2 MB. Split it into smaller files.', true); return; }
    const fr = new FileReader();
    fr.onload = () => { try { preview(f.name, rowsFromCsv(String(fr.result))); } catch (e) { toast(e.message, true); } };
    fr.readAsText(f);
  }
  function preview(name, rows) {
    const good = rows.filter(r => !r.problem), bad = rows.filter(r => r.problem);
    const adds = good.filter(r => !r.update).length, ups = good.length - adds;
    box.querySelector('#ub').innerHTML = `
      <div class="upload-sum"><span class="pill plain file">${ic('file')} ${esc(name)}</span>
        <span class="pill open">${adds} new</span>${ups ? `<span class="pill paused">${ups} to update</span>` : ''}${bad.length ? `<span class="pill bad">${bad.length} with problems</span>` : ''}</div>
      <div class="table-wrap" style="background:var(--panel-2)"><div class="table-scroll"><table class="t" style="min-width:680px">
        <thead><tr><th>Row</th><th>Player</th><th>Club</th><th>Pos</th><th class="r">Price</th><th>Check</th></tr></thead>
        <tbody>${rows.map(r => `<tr>
          <td class="faint num">${r.line}</td>
          <td><div class="who-text"><b>${esc(r.name || '—')}</b><small><span class="tick">${esc(r.ticker || '—')}</span></small></div></td>
          <td><div class="who-text"><b>${esc(r.club || '—')}</b><small>${esc(r.league)}</small></div></td>
          <td>${esc(r.position)}</td>
          <td class="r money num"><b>${r.reference_value ? num(r.reference_value, 2) : '—'}</b>${r.reference_value > 0 ? `<small>${usd(r.reference_value)}</small>` : ''}</td>
          <td>${r.problem ? `<span class="issue">${esc(r.problem)}</span>` : r.update ? '<span class="note-up">Updates the listed player</span>' : '<span class="note-ok">Ready to add</span>'}</td></tr>`).join('')}</tbody>
      </table></div></div>`;
    box.querySelector('#ua').innerHTML = `<button class="btn btn-ghost" id="again">Choose another file</button>
      <button class="btn btn-primary" id="pub" ${good.length ? '' : 'disabled'}>Publish ${good.length} ${good.length === 1 ? 'player' : 'players'}</button>`;
    box.querySelector('#again').onclick = () => { closeDialog(); openUpload(); };
    box.querySelector('#pub').onclick = async () => {
      const btn = box.querySelector('#pub'); btn.disabled = true; btn.textContent = 'Publishing…';
      try {
        const res = await api('ft_admin_upsert_players', { p_rows: good.map(({ line, problem, update, ...r }) => r) });
        box.querySelector('#ub').innerHTML = `<div class="callout">${ic('check')}<span>Added <b>${res.added}</b> and updated <b>${res.updated}</b>. They're open to claim now.</span></div>
          ${res.skipped && res.skipped.length ? `<h3 style="font-size:14px;margin:8px 0">Skipped by the database</h3><div class="list">${res.skipped.map(s =>
            `<div class="list-row"><span><b>${esc(s.name || s.ticker)}</b> <small>${esc(s.ticker)}</small></span><span class="issue">${esc(s.reason)}</span></div>`).join('')}</div>` : ''}`;
        box.querySelector('#ua').innerHTML = `<button class="btn btn-primary" data-close>Done</button>`;
        delete cache.overview; await reloadPlayers(); refreshCounts();
      } catch (e) { toast(e.message, true); btn.disabled = false; btn.textContent = `Publish ${good.length} players`; }
    };
  }
}

/* ── Claims ────────────────────────────────────────────────────────── */
VIEWS.claims = async view => {
  loading(view, 'Claims');
  cache.claims = await api('ft_admin_claims');
  drawClaims(view);
};
function drawClaims(view) {
  const all = cache.claims || [], q = ui.claims.q.toLowerCase();
  const rows = all.filter(c => !q || [c.name, c.ticker, c.handle, c.display_name].join(' ').toLowerCase().includes(q));
  const paid = all.reduce((t, c) => t + Number(c.fee_paid || 0), 0), burned = all.reduce((t, c) => t + Number(c.fee_burned || 0), 0);
  const shares = all.reduce((t, c) => t + Number(c.shares || 0), 0);
  view.innerHTML = head('Claims', 'Every player a manager has launched: what they took, what they paid and when their shares vest.',
    `<button class="btn" id="exp" ${all.length ? '' : 'disabled'}>${ic('download')}Export CSV</button>`) + `
    <div class="kpis four">
      <div class="kpi lead"><span class="kpi-label">Paid for claims</span><span class="kpi-val num">${compact(paid)}</span><span class="kpi-sub">$FTR · ≈ ${usd(paid)}</span></div>
      <div class="kpi"><span class="kpi-label">Players launched</span><span class="kpi-val num">${num(all.length)}</span><span class="kpi-sub">by claim</span></div>
      <div class="kpi"><span class="kpi-label">Burned (2%)</span><span class="kpi-val num">${compact(burned)}</span><span class="kpi-sub">$FTR gone for good</span></div>
      <div class="kpi"><span class="kpi-label">Shares claimed</span><span class="kpi-val num">${compact(shares)}</span><span class="kpi-sub">vesting to listers</span></div>
    </div>
    <div class="toolbar"><label class="search">${ic('search')}<span class="sr">Search claims</span><input class="input" id="cq" type="search" placeholder="Search player or manager" value="${esc(ui.claims.q)}"></label></div>
    <div class="table-wrap"><div class="table-scroll"><table class="t">
      <thead><tr><th>Player</th><th>Claimed by</th><th>Level</th><th class="r">Paid</th><th class="r">Burned</th><th>Vesting</th><th>Claimed</th></tr></thead>
      <tbody>${rows.map(claimRow).join('') || `<tr><td colspan="7"><div class="empty"><b>No claims yet.</b>When a manager launches a player, it shows up here.</div></td></tr>`}</tbody>
    </table></div><div class="table-foot">${rows.length} of ${all.length} claims</div></div>`;
  wireBanner();
  const cq = document.getElementById('cq');
  cq.oninput = debounce(() => { ui.claims.q = cq.value; drawClaims(view); const n = document.getElementById('cq'); n.focus(); n.setSelectionRange(n.value.length, n.value.length); }, 180);
  document.getElementById('exp').onclick = () => {
    const cols = ['ticker', 'name', 'handle', 'claim_level', 'shares', 'fee_paid', 'fee_burned', 'vesting_years', 'claimed_at', 'vesting_until'];
    const q = v => /[",\n]/.test(String(v)) ? '"' + String(v).replace(/"/g, '""') + '"' : String(v == null ? '' : v);
    downloadFile('fantrade-claims.csv', cols.join(',') + '\n' + all.map(c => cols.map(k => q(c[k])).join(',')).join('\n'));
  };
}
function claimRow(c) {
  const start = new Date(c.claimed_at).getTime(), end = new Date(c.vesting_until).getTime();
  const pct = Math.max(0, Math.min(100, (Date.now() - start) / Math.max(1, end - start) * 100));
  return `<tr>
    <td><div class="who">${avatar(c.name)}<div class="who-text"><b>${esc(c.name)}</b><small><span class="tick">${esc(c.ticker)}</span> ${esc(c.club || '')}</small></div></div></td>
    <td><div class="who-text"><b>@${esc(c.handle || '—')}</b><small>${esc(c.display_name || '')}</small></div></td>
    <td><span class="pill claimed">Level ${c.claim_level} · ${c.claim_level === 2 ? '10' : '5'}%</span><small class="faint" style="display:block;margin-top:4px">${num(c.shares)} shares</small></td>
    <td class="r money num"><b>${num(c.fee_paid)}</b><small>≈ ${usd(c.fee_paid)}</small></td>
    <td class="r money num"><b>${num(c.fee_burned)}</b><small>$FTR</small></td>
    <td><div class="vest"><div class="vest-bar"><i style="width:${pct.toFixed(1)}%"></i></div><small>${c.vesting_years}y · vests ${day(c.vesting_until)}</small></div></td>
    <td><div class="who-text"><b>${day(c.claimed_at)}</b><small>${ago(c.claimed_at)}</small></div></td></tr>`;
}

/* ── Managers ──────────────────────────────────────────────────────── */
VIEWS.managers = async view => {
  loading(view, 'Managers');
  cache.managers = await api('ft_admin_managers', { p_query: ui.managers.q, p_limit: 200 });
  drawManagers(view);
};
function drawManagers(view) {
  const rows = cache.managers || [];
  view.innerHTML = head('Managers', 'Everyone with a Fantrade account. Open one to see their wallet, what they hold and what they have done.') + `
    <div class="toolbar"><label class="search">${ic('search')}<span class="sr">Search managers</span><input class="input" id="mq" type="search" placeholder="Search name, @handle or email" value="${esc(ui.managers.q)}"></label></div>
    <div class="table-wrap"><div class="table-scroll"><table class="t">
      <thead><tr><th>Manager</th><th>Joined</th><th class="r">Wallet</th><th class="r">Holdings</th><th>Status</th><th></th></tr></thead>
      <tbody>${rows.map(m => `<tr class="click" data-id="${esc(m.id)}" tabindex="0">
        <td><div class="who">${avatar(m.display_name || m.handle)}<div class="who-text"><b>${esc(m.display_name)}</b><small>@${esc(m.handle)}${m.email ? ' · ' + esc(m.email) : ''}</small></div></div></td>
        <td><div class="who-text"><b>${day(m.created_at)}</b><small>${esc(m.region || '')}</small></div></td>
        <td class="r money num"><b>${num(m.balance)}</b><small>${Number(m.locked) ? compact(m.locked) + ' locked' : '≈ ' + usd(m.balance)}</small></td>
        <td class="r money num"><b>${compact(m.holdings_value)}</b><small>${num(m.positions)} ${m.positions == 1 ? 'player' : 'players'}</small></td>
        <td>${m.suspended ? '<span class="pill bad">Suspended</span>' : m.is_admin ? '<span class="pill claimed">Admin</span>' : '<span class="pill open">Active</span>'}</td>
        <td class="r faint">${ic('chevron')}</td></tr>`).join('') || `<tr><td colspan="6"><div class="empty"><b>No one matches.</b>Try a different name, handle or email.</div></td></tr>`}</tbody>
    </table></div><div class="table-foot">${rows.length} ${rows.length === 1 ? 'manager' : 'managers'}${rows.length >= 200 ? ' · showing the newest 200, search to find others' : ''}</div></div>`;
  wireBanner();
  const mq = document.getElementById('mq');
  mq.oninput = debounce(async () => {
    ui.managers.q = mq.value;
    try { cache.managers = await api('ft_admin_managers', { p_query: ui.managers.q, p_limit: 200 }); } catch (e) { toast(e.message, true); return; }
    drawManagers(view); const n = document.getElementById('mq'); n.focus(); n.setSelectionRange(n.value.length, n.value.length);
  }, 260);
  const tb = view.querySelector('tbody');
  tb.onclick = e => { const tr = e.target.closest('tr[data-id]'); if (tr) openManager(tr.dataset.id); };
  tb.onkeydown = e => { const tr = e.target.closest('tr[data-id]'); if (tr && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openManager(tr.dataset.id); } };
}
async function openManager(id) {
  const d = openDrawer(`<div class="drawer-head"><div><h2>Loading…</h2></div><button class="icon-btn" data-close aria-label="Close">${ic('x')}</button></div>`);
  d.querySelector('[data-close]').onclick = closeDrawer;
  let m; try { m = await api('ft_admin_manager', { p_user: id }); } catch (e) { toast(e.message, true); closeDrawer(); return; }
  const p = m.profile, w = m.wallet || {}, hv = (m.holdings || []).reduce((t, h) => t + Number(h.value || 0), 0);
  const self = p.handle === me.handle, canWrite = me.role !== 'viewer';
  d.innerHTML = `
    <div class="drawer-head">${avatar(p.display_name || p.handle, 52)}<div><h2>${esc(p.display_name)}</h2>
      <p>@${esc(p.handle)}${p.email ? ' · ' + esc(p.email) : ''}</p>
      <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">${p.suspended ? '<span class="pill bad">Suspended</span>' : '<span class="pill open">Active</span>'}${p.is_admin ? '<span class="pill claimed">Admin</span>' : ''}
        <span class="pill plain">Joined ${day(p.created_at)}</span></div></div>
      <button class="icon-btn" data-close aria-label="Close">${ic('x')}</button></div>
    <div class="drawer-body">
      <div class="mini-kpis"><div class="mini"><span>Wallet</span><b class="num">${compact(w.balance)}</b></div>
        <div class="mini"><span>Locked</span><b class="num">${compact(w.locked)}</b></div>
        <div class="mini"><span>Holdings</span><b class="num">${compact(hv)}</b></div></div>
      ${p.suspended ? `<div class="banner" style="margin:14px 0 0">${ic('alert')}<span><b>Suspended ${ago(p.suspended_at)}.</b> ${esc(p.suspended_reason || '')}</span></div>` : ''}
      <div class="section"><h3>Holdings</h3>${(m.holdings || []).length ? `<div class="list">${m.holdings.map(h => `<div class="list-row">
        <span><span class="tick">${esc(h.ticker)}</span> ${esc(h.name)}</span><span class="num">${num(h.shares)} <small>shares</small></span><b class="num" style="min-width:90px;text-align:right">${compact(h.value)}</b></div>`).join('')}</div>`
        : '<p class="faint">Holds no shares.</p>'}</div>
      <div class="section"><h3>Recent transactions</h3>${(m.transactions || []).length ? `<div class="list">${m.transactions.map(t => `<div class="list-row">
        <span>${esc(t.label || t.type)} <small>· ${ago(t.created_at)}</small></span><span class="pill plain">${esc(t.type)}</span><b class="num" style="min-width:90px;text-align:right">${compact(t.total)}</b></div>`).join('')}</div>`
        : '<p class="faint">No transactions yet.</p>'}</div>
      <div class="section"><h3>FanPlay</h3>${(m.fanplay || []).length ? `<div class="list">${m.fanplay.map(f => `<div class="list-row">
        <span>${esc(f.target)} <small>· MD ${esc(f.matchday)} · ${esc(f.mode)}</small></span>${statusPill(f.status)}<b class="num" style="min-width:70px;text-align:right">${compact(f.projected_fp)} FP</b></div>`).join('')}</div>`
        : '<p class="faint">No FanPlay entries.</p>'}</div>
      ${canWrite && !self && !p.is_admin ? `<div class="section"><h3>Account</h3>${p.suspended
        ? `<p class="muted" style="margin:0 0 12px">Reinstating lets them trade, claim and play again straight away.</p><button class="btn btn-primary" id="reinstate">Reinstate account</button>`
        : `<p class="muted" style="margin:0 0 12px">A suspended manager can still sign in and look, but can't buy, sell, claim or play until you reinstate them.</p>
           <div class="field"><label for="why">Reason (kept in the activity log)</label><textarea class="textarea" id="why" placeholder="e.g. Payment reversed by the bank"></textarea></div>
           <button class="btn btn-danger" id="suspend">${ic('userx')}Suspend account</button>`}</div>` : ''}
    </div>`;
  d.querySelectorAll('[data-close]').forEach(b => b.onclick = closeDrawer);
  const act = async (suspend) => {
    const reason = suspend ? (d.querySelector('#why').value || '').trim() : null;
    if (suspend && reason.length < 3) { toast('Give a reason for the suspension.', true); d.querySelector('#why').focus(); return; }
    const ok = await confirmBox(suspend
      ? { title: `Suspend @${p.handle}?`, body: 'They will not be able to trade, claim or play until reinstated.', ok: 'Suspend', danger: true }
      : { title: `Reinstate @${p.handle}?`, body: 'They can trade, claim and play again straight away.', ok: 'Reinstate' });
    if (!ok) return;
    try {
      await api('ft_admin_suspend', { p_user: id, p_suspend: suspend, p_reason: reason });
      toast(suspend ? `@${p.handle} suspended` : `@${p.handle} reinstated`); delete cache.overview;
      cache.managers = await api('ft_admin_managers', { p_query: ui.managers.q, p_limit: 200 });
      if (location.hash.startsWith('#/managers')) drawManagers(document.getElementById('view'));
      openManager(id);
    } catch (e) { toast(e.message, true); }
  };
  const s = d.querySelector('#suspend'); if (s) s.onclick = () => act(true);
  const r = d.querySelector('#reinstate'); if (r) r.onclick = () => act(false);
}

/* ── FanPlay ───────────────────────────────────────────────────────── */
const FP_STATUS = { ACTIVE: ['Active', 'open'], LIVE: ['Live', 'open'], PENDING_SETTLEMENT: ['Awaiting result', 'paused'], SETTLED: ['Settled', 'claimed'],
  VOID: ['Void', 'plain'], CANCELLED: ['Cancelled', 'plain'], SUSPENDED: ['Suspended', 'bad'], DISPUTED: ['Disputed', 'bad'], DRAFT: ['Draft', 'plain'] };
const statusPill = s => { const [l, c] = FP_STATUS[s] || [s, 'plain']; return `<span class="pill ${c}">${esc(l)}</span>`; };
VIEWS.fanplay = async view => {
  loading(view, 'FanPlay');
  cache.fanplay = await api('ft_admin_fanplay');
  drawFanplay(view);
};
function drawFanplay(view) {
  const f = cache.fanplay || {}, s = f.by_status || {}, st = ui.fanplay;
  const groups = { all: null, live: ['ACTIVE', 'LIVE'], pending: ['PENDING_SETTLEMENT'], settled: ['SETTLED'], other: ['VOID', 'CANCELLED', 'SUSPENDED', 'DISPUTED', 'DRAFT'] };
  const cnt = k => (groups[k] || []).reduce((t, x) => t + (s[x] || 0), 0);
  const all = f.entries || [], rows = all.filter(e => !groups[st.status] || groups[st.status].includes(e.status));
  view.innerHTML = head('FanPlay', 'Every matchday entry, from the moment shares are locked to the result.') + `
    <div class="callout">${ic('lock')}<span>This view is read-only on purpose. Entries settle from verified match data on the server (white paper §14.6), so no one can settle, pay or change a result from a browser, admins included.</span></div>
    <div class="kpis four">
      <div class="kpi lead"><span class="kpi-label">Live now</span><span class="kpi-val num">${num(cnt('live'))}</span><span class="kpi-sub">entries with shares locked</span></div>
      <div class="kpi"><span class="kpi-label">Awaiting result</span><span class="kpi-val num">${num(cnt('pending'))}</span><span class="kpi-sub">match over, not yet settled</span></div>
      <div class="kpi"><span class="kpi-label">Settled</span><span class="kpi-val num">${num(cnt('settled'))}</span><span class="kpi-sub">all time</span></div>
      <div class="kpi"><span class="kpi-label">Void or cancelled</span><span class="kpi-val num">${num(cnt('other'))}</span><span class="kpi-sub">shares returned</span></div>
    </div>
    ${(f.matchdays || []).length ? `<section class="card" style="margin-bottom:16px"><div class="card-head"><div><h2>By matchday</h2><p>Where each matchday stands</p></div></div>
      <div class="table-scroll"><table class="t" style="min-width:560px"><thead><tr><th>Matchday</th><th class="r">Entries</th><th class="r">Live</th><th class="r">Awaiting</th><th class="r">Settled</th><th class="r">Shares staked</th><th class="r">Projected FP</th></tr></thead>
      <tbody>${f.matchdays.map(m => `<tr><td><b>MD ${esc(m.matchday)}</b></td><td class="r num">${num(m.entries)}</td><td class="r num">${num(m.live)}</td><td class="r num">${num(m.pending)}</td><td class="r num">${num(m.settled)}</td><td class="r num">${compact(m.shares_staked)}</td><td class="r num">${compact(m.projected_fp)}</td></tr>`).join('')}</tbody></table></div></section>` : ''}
    <div class="toolbar"><div class="chips" role="group" aria-label="Status">${[['all', 'All'], ['live', 'Live'], ['pending', 'Awaiting result'], ['settled', 'Settled'], ['other', 'Void or cancelled']].map(([k, l]) =>
      `<button class="chip" data-s="${k}" aria-pressed="${st.status === k}">${l} <i>${k === 'all' ? all.length : cnt(k)}</i></button>`).join('')}</div></div>
    <div class="table-wrap"><div class="table-scroll"><table class="t">
      <thead><tr><th>Manager</th><th>Entry</th><th>Matchday</th><th class="r">Shares</th><th class="r">Projected FP</th><th class="r">Scored FP</th><th>Status</th><th>Placed</th></tr></thead>
      <tbody>${rows.map(e => `<tr>
        <td><b>@${esc(e.handle || '—')}</b></td>
        <td><div class="who-text"><b>${esc(e.target)}</b><small>${esc(e.mode)}${e.match && e.match.home ? ' · ' + esc(e.match.home) + ' v ' + esc(e.match.away) : ''}</small></div></td>
        <td>MD ${esc(e.matchday)}</td>
        <td class="r num">${e.staked_shares ? num(e.staked_shares) + (e.ticker ? ` <span class="tick">${esc(e.ticker)}</span>` : '') : '—'}</td>
        <td class="r num">${compact(e.projected_fp)}</td>
        <td class="r num">${e.scored_fp == null ? '<span class="faint">—</span>' : compact(e.scored_fp)}</td>
        <td>${statusPill(e.status)}</td>
        <td><small class="faint">${ago(e.created_at)}</small></td></tr>`).join('') || `<tr><td colspan="8"><div class="empty"><b>No entries here.</b>FanPlay entries appear as managers lock shares for a matchday.</div></td></tr>`}</tbody>
    </table></div><div class="table-foot">${rows.length} of ${all.length} entries${all.length >= 200 ? ' · the newest 200' : ''}</div></div>`;
  wireBanner();
  view.querySelectorAll('[data-s]').forEach(b => b.onclick = () => { st.status = b.dataset.s; drawFanplay(view); });
}

/* ── Activity log ──────────────────────────────────────────────────── */
VIEWS.log = async view => {
  loading(view, 'Activity log');
  const rows = await api('ft_admin_log', { p_limit: 200 });
  view.innerHTML = head('Activity log', 'Every change made from this admin, newest first. It cannot be edited or cleared from here.') + `
    <div class="table-wrap"><div class="table-scroll"><table class="t">
      <thead><tr><th>When</th><th>Admin</th><th>What happened</th><th>Details</th></tr></thead>
      <tbody>${rows.map(r => `<tr>
        <td><div class="who-text"><b>${day(r.created_at)}</b><small>${new Date(r.created_at).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })} · ${ago(r.created_at)}</small></div></td>
        <td><b>@${esc(r.handle || 'removed')}</b></td>
        <td>${esc(humanAction(r.action))}${r.target ? ` <span class="tick">${esc(String(r.target).replace(/^lst-/, ''))}</span>` : ''}</td>
        <td class="muted" style="white-space:normal">${logDetail(r)}</td></tr>`).join('') || `<tr><td colspan="4"><div class="empty"><b>Nothing yet.</b>Changes made here will be listed.</div></td></tr>`}</tbody>
    </table></div></div>`;
  wireBanner();
};
function logDetail(r) {
  const d = r.detail || {};
  if (r.action === 'players.upsert') return `${d.added || 0} added, ${d.updated || 0} updated${d.skipped ? `, ${d.skipped} skipped` : ''}`;
  if (d.reason) return esc(d.reason);
  if (d.name) return esc(d.name);
  return '';
}

/* ── Sample data (only when chosen, always labelled) ───────────────── */
const SAMPLE = (() => {
  const now = Date.now(), D = 86400000, iso = t => new Date(t).toISOString();
  const P = [
    ['FCR7', 'Cristiano Ronaldo', 'Al Nassr', 'Saudi Pro League', 'FWD', 34.60], ['FLM10', 'Lionel Messi', 'Inter Miami', 'MLS', 'FWD', 38.20],
    ['FKANE', 'Harry Kane', 'Bayern Munich', 'Bundesliga', 'FWD', 62.40], ['FRICE', 'Declan Rice', 'Arsenal', 'Premier League', 'MID', 49.60],
    ['FVVD', 'Virgil van Dijk', 'Liverpool', 'Premier League', 'DEF', 29.80], ['FOSIM', 'Victor Osimhen', 'Galatasaray', 'Süper Lig', 'FWD', 41.30],
    ['FSALH', 'Mohamed Salah', 'Trabzonspor', 'Süper Lig', 'FWD', 27.90], ['FLOOK', 'Ademola Lookman', 'Atlético Madrid', 'La Liga', 'FWD', 18.40],
    ['FCHUK', 'Samuel Chukwueze', 'AC Milan', 'Serie A', 'FWD', 1.85], ['FSHAW', 'Khadija Shaw', 'Manchester City', 'WSL', 'FWD', 32.50],
    ['FPAJR', 'Ewa Pajor', 'Barcelona', 'Liga F', 'FWD', 30.10], ['FRODM', 'Trinity Rodman', 'Washington Spirit', 'NWSL', 'FWD', 26.40],
    ['FKELY', 'Chloe Kelly', 'Arsenal', 'WSL', 'FWD', 22.80], ['FAJBD', 'Rasheedat Ajibade', 'Paris Saint-Germain', 'Première Ligue', 'FWD', 1.60],
    ['FALOZ', 'Michelle Alozie', 'Chicago Stars', 'NWSL', 'DEF', 1.20]
  ];
  const M = [
    ['amaka_fc', 'Amaka Obi', 'Nigeria', 3], ['tobi_eleven', 'Tobi Adeyemi', 'Nigeria', 5], ['gooner_jess', 'Jess Morgan', 'United Kingdom', 9],
    ['kwame_m', 'Kwame Mensah', 'Ghana', 12], ['lp_scout', 'Liam Price', 'United Kingdom', 16], ['sofi_r', 'Sofia Reyes', 'Spain', 20],
    ['dan_okoro', 'Daniel Okoro', 'United Kingdom', 24], ['priya_fc', 'Priya Shah', 'United Kingdom', 31], ['tomh', 'Tom Harris', 'Ireland', 40],
    ['chioma_e', 'Chioma Eze', 'Nigeria', 44], ['marcus_l', 'Marcus Lee', 'United States', 52], ['sample_admin', 'Sample admin', 'United Kingdom', 90]
  ].map(([h, n, r, ago], i) => ({ id: 'u' + i, handle: h, display_name: n, email: h + '@example.com', region: r, created_at: iso(now - ago * D),
    suspended: h === 'chioma_e', suspended_reason: h === 'chioma_e' ? 'Card payment reversed by the bank; under review.' : null,
    suspended_at: h === 'chioma_e' ? iso(now - 2 * D) : null, is_admin: h === 'sample_admin',
    balance: [75000, 216000, 1000000, 640500, 1000000, 412000, 88000, 1000000, 530000, 12000, 1000000, 1000000][i], locked: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0][i] }));
  const claimsDef = [['FCHUK', 'amaka_fc', 1, 2, 1], ['FAJBD', 'tobi_eleven', 1, 1, 3], ['FALOZ', null, 0, 0, 0], ['FLOOK', 'kwame_m', 1, 3, 5],
    ['FKELY', 'gooner_jess', 1, 2, 6], ['FRODM', 'sofi_r', 2, 3, 9], ['FPAJR', 'priya_fc', 1, 1, 12]];
  const players = P.map(([t, n, c, l, pos, v]) => ({ listing_id: 'lst-' + t, asset_id: '$' + t, ticker: t, name: n, kind: 'PLAYER', club: c, league: l, position: pos,
    reference_value: v, status: 'open', claimed_by: null, claimed_at: null, created_at: iso(now - 20 * D) }));
  const byT = t => players.find(p => p.ticker === t), byH = h => M.find(m => m.handle === h);
  const claims = [];
  claimsDef.forEach(([t, h, lvl, yrs, daysAgo]) => {
    const p = byT(t); if (!h) { p.status = 'paused'; return; }
    const m = byH(h), shares = LEVEL_SHARES[lvl], paid = Math.round(shares * p.reference_value), at = now - daysAgo * D - 3600e3 * (daysAgo + 2);
    p.status = 'claimed'; p.claimed_by = h; p.claimed_at = iso(at);
    claims.push({ listing_id: p.listing_id, ticker: t, name: p.name, club: p.club, handle: h, display_name: m.display_name, user_id: m.id, claim_level: lvl,
      shares, vesting_years: yrs, fee_paid: paid, fee_burned: Math.round(paid * .02), daily_limit: shares / 100, claimed_at: iso(at),
      vesting_until: iso(at + yrs * 365 * D), reference_value: p.reference_value });
  });
  const fixtures = [['Arsenal', 'Chelsea'], ['Galatasaray', 'Fenerbahçe'], ['Barcelona', 'Real Madrid'], ['Manchester City', 'Liverpool'], ['AC Milan', 'Inter']];
  const targets = [['FCHUK', 'Samuel Chukwueze'], ['FSAKA', 'Bukayo Saka'], ['FHLND', 'Erling Haaland'], ['FAJBD', 'Rasheedat Ajibade'], ['FKM7', 'Kylian Mbappé']];
  const entries = [];
  for (let i = 0; i < 18; i++) {
    const md = i < 7 ? 7 : i < 12 ? 6 : 5, m = M[i % 11], tg = targets[i % 5], fx = fixtures[i % 5], dream = i % 4 === 0;
    const status = md === 7 ? (i % 3 ? 'ACTIVE' : 'LIVE') : md === 6 ? (i === 11 ? 'VOID' : 'PENDING_SETTLEMENT') : 'SETTLED';
    const proj = 120 + (i * 37) % 260;
    entries.push({ id: 'e' + i, handle: m.handle, mode: dream ? 'Dream Club' : 'Individual', target: dream ? m.display_name.split(' ')[0] + ' FC' : tg[1],
      ticker: dream ? null : tg[0], staked_shares: dream ? 0 : 500 + (i * 250) % 3000, matchday: md, status, projected_fp: proj,
      scored_fp: status === 'SETTLED' ? Math.round(proj * (i % 2 ? 1.3 : .4)) : null, created_at: iso(now - (8 - md) * 5 * D - i * 3600e3),
      match: { home: fx[0], away: fx[1] } });
  }
  const log = [
    { id: 5, action: 'manager.suspend', target: '@chioma_e', detail: { reason: 'Card payment reversed by the bank; under review.' }, created_at: iso(now - 2 * D), handle: 'sample_admin' },
    { id: 4, action: 'player.pause', target: 'lst-FALOZ', detail: {}, created_at: iso(now - 4 * D), handle: 'sample_admin' },
    { id: 3, action: 'players.upsert', target: null, detail: { added: 15, updated: 0, skipped: 0 }, created_at: iso(now - 20 * D), handle: 'sample_admin' }
  ];
  const note = (action, target, detail) => log.unshift({ id: log.length + 1, action, target, detail: detail || {}, created_at: iso(Date.now()), handle: 'sample_admin' });
  const clone = x => JSON.parse(JSON.stringify(x));
  const holdingsFor = m => claims.filter(c => c.handle === m.handle).map(c => ({ ticker: c.ticker, name: c.name, shares: c.shares, locked: 0, avg_cost: c.reference_value, price: c.reference_value, value: c.shares * c.reference_value }))
    .concat(m.handle === 'sample_admin' ? [] : [{ ticker: 'FSAKA', name: 'Bukayo Saka', shares: 1000 + m.handle.length * 150, locked: 0, avg_cost: 44, price: 48.2, value: (1000 + m.handle.length * 150) * 48.2 }]);
  const fn = {
    ft_admin_whoami: () => ({ is_admin: true, role: 'admin', handle: 'sample_admin', name: 'Sample admin', email: 'sample@fantrade.app' }),
    ft_admin_overview: () => {
      const recent = claims.map(c => ({ kind: 'claim', at: c.claimed_at, who: c.handle, what: `claimed ${c.claim_level === 2 ? 10 : 5}% of ${c.name}`, amount: c.fee_paid }))
        .concat(M.map(m => ({ kind: 'signup', at: m.created_at, who: m.handle, what: 'joined Fantrade', amount: null })))
        .concat(log.map(l => ({ kind: 'admin', at: l.created_at, who: l.handle, what: l.action + (l.target ? ' · ' + l.target : ''), amount: null })))
        .sort((a, b) => new Date(b.at) - new Date(a.at)).slice(0, 12);
      const days = []; for (let i = 13; i >= 0; i--) {
        const d0 = new Date(now - i * D); d0.setHours(0, 0, 0, 0); const k = d0.toDateString();
        const cs = claims.filter(c => new Date(c.claimed_at).toDateString() === k);
        days.push({ day: d0.toISOString(), claims: cs.length, paid: cs.reduce((t, c) => t + c.fee_paid, 0) });
      }
      return { managers: M.length, managers_7d: M.filter(m => now - new Date(m.created_at) < 7 * D).length, suspended: M.filter(m => m.suspended).length,
        wallet_ftr: M.reduce((t, m) => t + m.balance, 0), locked_ftr: 0,
        open_to_claim: players.filter(p => p.status === 'open').length, paused: players.filter(p => p.status === 'paused').length,
        trading: 26 + claims.length, claims: claims.length, claims_paid: claims.reduce((t, c) => t + c.fee_paid, 0), claims_burned: claims.reduce((t, c) => t + c.fee_burned, 0),
        fanplay_active: entries.filter(e => ['ACTIVE', 'LIVE'].includes(e.status)).length, fanplay_pending: entries.filter(e => e.status === 'PENDING_SETTLEMENT').length,
        claims_by_day: days, recent };
    },
    ft_admin_players: () => clone(players).sort((a, b) => ({ open: 0, paused: 1, claimed: 2 }[a.status] - { open: 0, paused: 1, claimed: 2 }[b.status]) || a.name.localeCompare(b.name)),
    ft_admin_upsert_players: ({ p_rows }) => {
      let added = 0, updated = 0; const skipped = [];
      p_rows.forEach(r => {
        const problem = validateRow(r); if (problem) { skipped.push({ ticker: r.ticker, name: r.name, reason: problem }); return; }
        if (['FSAKA', 'FHLND', 'FKM7', 'FYAML', 'FAITN'].includes(r.ticker)) { skipped.push({ ticker: r.ticker, name: r.name, reason: 'Already launched, so it can no longer be edited here' }); return; }
        const ex = byT(r.ticker), v = parseFloat(r.reference_value);
        if (ex) { if (ex.status === 'claimed') { skipped.push({ ticker: r.ticker, name: r.name, reason: 'Already launched, so it can no longer be edited here' }); return; }
          Object.assign(ex, { name: r.name, kind: r.kind, club: r.club, league: r.league, position: r.position, reference_value: v }); updated++; }
        else { players.push({ listing_id: 'lst-' + r.ticker, asset_id: '$' + r.ticker, ticker: r.ticker, name: r.name, kind: r.kind, club: r.club, league: r.league,
          position: r.position, reference_value: v, status: 'open', claimed_by: null, claimed_at: null, created_at: iso(Date.now()) }); added++; }
      });
      note('players.upsert', null, { added, updated, skipped: skipped.length });
      return { added, updated, skipped };
    },
    ft_admin_set_open: ({ p_listing, p_open }) => { const p = players.find(x => x.listing_id === p_listing); if (!p) throw new Error('No such listing');
      if (p.status === 'claimed') throw new Error('This player has been claimed and is trading'); p.status = p_open ? 'open' : 'paused';
      note(p_open ? 'player.reopen' : 'player.pause', p_listing); return { listing: p_listing, open: p_open }; },
    ft_admin_remove_player: ({ p_listing }) => { const i = players.findIndex(x => x.listing_id === p_listing); if (i < 0) throw new Error('No such listing');
      if (players[i].status === 'claimed') throw new Error('This player has launched and cannot be removed');
      note('player.remove', players[i].ticker, { name: players[i].name }); players.splice(i, 1); return { removed: p_listing }; },
    ft_admin_claims: () => clone(claims).sort((a, b) => new Date(b.claimed_at) - new Date(a.claimed_at)),
    ft_admin_managers: ({ p_query }) => { const q = String(p_query || '').toLowerCase();
      return clone(M.filter(m => !q || [m.handle, m.display_name, m.email].join(' ').toLowerCase().includes(q))).map(m => {
        const h = holdingsFor(m); return Object.assign(m, { holdings_value: h.reduce((t, x) => t + x.value, 0), positions: h.length }); }); },
    ft_admin_manager: ({ p_user }) => { const m = M.find(x => x.id === p_user); if (!m) throw new Error('No such manager');
      const tx = claims.filter(c => c.handle === m.handle).map(c => ({ type: 'GRANT', label: `Claimed ${c.claim_level === 2 ? 10 : 5}% of ${c.name}`, ticker: c.ticker, shares: c.shares, total: c.fee_paid, created_at: c.claimed_at }))
        .concat([{ type: 'GRANT', label: 'Welcome balance', ticker: null, shares: 0, total: 1000000, created_at: m.created_at }]);
      return { profile: clone(m), wallet: { balance: m.balance, locked: m.locked }, holdings: holdingsFor(m), transactions: tx,
        fanplay: entries.filter(e => e.handle === m.handle).map(e => ({ mode: e.mode, target: e.target, matchday: e.matchday, status: e.status, projected_fp: e.projected_fp, created_at: e.created_at })) }; },
    ft_admin_suspend: ({ p_user, p_suspend, p_reason }) => { const m = M.find(x => x.id === p_user); if (!m) throw new Error('No such manager');
      if (m.is_admin) throw new Error('Remove admin rights before suspending an admin');
      Object.assign(m, { suspended: p_suspend, suspended_reason: p_suspend ? p_reason : null, suspended_at: p_suspend ? iso(Date.now()) : null });
      note(p_suspend ? 'manager.suspend' : 'manager.reinstate', '@' + m.handle, { reason: p_reason }); return { handle: m.handle, suspended: p_suspend }; },
    ft_admin_fanplay: () => {
      const by = {}; entries.forEach(e => by[e.status] = (by[e.status] || 0) + 1);
      const mds = [...new Set(entries.map(e => e.matchday))].sort((a, b) => b - a).map(md => { const es = entries.filter(e => e.matchday === md);
        return { matchday: md, entries: es.length, live: es.filter(e => ['ACTIVE', 'LIVE'].includes(e.status)).length, pending: es.filter(e => e.status === 'PENDING_SETTLEMENT').length,
          settled: es.filter(e => e.status === 'SETTLED').length, shares_staked: es.reduce((t, e) => t + e.staked_shares, 0), projected_fp: es.reduce((t, e) => t + e.projected_fp, 0) }; });
      return { by_status: by, matchdays: mds, entries: clone(entries) };
    },
    ft_admin_log: () => clone(log)
  };
  return { call: async (name, args) => { await new Promise(r => setTimeout(r, 120)); if (!fn[name]) throw new Error('Not available in sample mode'); return fn[name](args); } };
})();

/* ── Start ─────────────────────────────────────────────────────────── */
async function boot() {
  app.className = 'boot'; app.setAttribute('aria-busy', 'true');
  app.innerHTML = '<div class="boot-mark"><img src="assets/fantrade-logo.png" alt="" width="40" height="40"><span>Fantrade Admin</span></div>';
  try { if (!sb) await loadClient(); } catch (e) { return renderSignIn({ offline: true }); }
  try {
    const { data } = await sb.auth.getSession();
    if (!data || !data.session) return renderSignIn();
    await afterSignIn();
  } catch (e) { renderSignIn({ error: e.message }); }
}
boot();
