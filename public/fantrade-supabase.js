/**
 * Fantrade · Supabase bridge.
 *
 * The pages stay exactly as they are: they read and write the in-memory FT
 * state and never await anything. This file keeps that state and the database
 * in step around it.
 *
 *   · On load it restores the signed-in session and pulls one snapshot
 *     (profile, wallet, holdings, transactions) into FT.
 *   · Every money action the app performs is mirrored to a database function
 *     straight afterwards. The database re-checks the price, the balance and
 *     the share count, so the browser can never talk it into a bad trade.
 *   · If the call fails — offline, signed out, or refused — the local state is
 *     re-synced from the database and the reason is shown, so what you see is
 *     always what the database actually holds.
 *
 * The anon key below is the publishable key. It is meant to ship in the page:
 * row-level security is what protects the data, and every write goes through a
 * function that starts from the signed-in user.
 */
(function (window) {
  var CONFIG = {
    url: 'https://ajjwodnjcnmkzguospay.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqandvZG5qY25ta3pndW9zcGF5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAwOTI3NjMsImV4cCI6MjEwNTY2ODc2M30.7KUEO-9rzcWcvCezLw26WMyDQWvbCCy15zzk-wyTnrg',
    cdn: 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'
  };

  var client = null, ready = null, lastError = null, session = null;

  /* ── Signed-out visitors belong on the sign-in page ──────────────────
     The app pages are for managers, so one opened without a session hands
     over to signin.html, which brings it back here once the manager is in.
     Two things are left alone: a page that cannot reach the database at all
     (it runs from this browser, as it always has), and a browser that signed
     in while the database was down, which keeps its own session.

     The board is deliberately not on this list — it is the one page an
     unsigned visitor may read — nor are the marketing pages or the auth
     screens themselves. */
  var IN_APP = ['account', 'activity', 'asset', 'buy', 'club-builder', 'clubs',
    'dashboard', 'divisions', 'exchange', 'fanplay', 'ftr', 'liveboard', 'notifications',
    'onboarding', 'portfolio', 'receive', 'send', 'settings', 'settings-alerts',
    'settings-club', 'settings-data', 'settings-play', 'settings-profile',
    'settings-security', 'settings-wallet', 'swap', 'trade', 'wallet', 'withdraw'];

  function pageName() {
    return ((window.location.pathname.split('/').pop() || 'index.html')
      .replace(/\.html$/i, '')).toLowerCase();
  }

  /* The pages each keep their own copy of the state under this key (see the
     STORAGE_KEY in any page's own script), so it is read straight from here —
     window.FT is not shared with the page. */
  function localSession() {
    try {
      var raw = window.localStorage.getItem('fantrade_v1_state') || window.localStorage.getItem('fantrade_v2_state');
      if (!raw) return true;
      var saved = JSON.parse(raw);
      if (saved && saved.auth && saved.auth.signedIn === false) return false;
      return true;
    } catch (error) { return true; }
  }

  function guard() {
    if (session || !client || localSession()) return;
    var page = pageName();
    if (IN_APP.indexOf(page) === -1) return;
    window.location.replace('signin.html?next=' + encodeURIComponent(page + '.html'));
  }

  function load() {
    if (ready) return ready;
    ready = import(CONFIG.cdn)
      .then(function (mod) {
        client = mod.createClient(CONFIG.url, CONFIG.anonKey, {
          auth: { persistSession: true, autoRefreshToken: true, storageKey: 'fantrade_auth' }
        });
        client.auth.onAuthStateChange(function (_event, next) {
          session = next;
          window.dispatchEvent(new CustomEvent('fantrade:auth', { detail: next }));
          if (!next) guard();
        });
        return client.auth.getSession();
      })
      .then(function (res) {
        session = res && res.data ? res.data.session : null;
        guard();
        pullNotifications();
        return client;
      })
      .catch(function (error) {
        lastError = error;
        console.warn('[Fantrade] Database unavailable, working from this browser only:', error && error.message);
        return null;
      });
    return ready;
  }

  function message(error) {
    var text = (error && (error.message || error.error_description)) || 'Something went wrong';
    if (/Invalid login credentials/i.test(text)) return 'That email and password do not match an account.';
    if (/already registered|already exists/i.test(text)) return 'There is already an account with that email.';
    if (/Email not confirmed/i.test(text)) return 'Confirm your email address first, then sign in.';
    if (/Failed to fetch|NetworkError/i.test(text)) return 'Cannot reach the server right now.';
    return text;
  }

  /* ── Notifications ─────────────────────────────────────────────────
     The pages render their own list; this keeps it in step with the table
     so a notice raised on one device turns up on the next. The browser
     makes the row's id, which is what stops the same notice counting
     twice when both copies meet in the merge. */
  var lastNotes = null;

  function noteId() {
    return 'n-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 7);
  }

  function broadcastNotes(rows) {
    if (rows) lastNotes = rows;
    if (!lastNotes) return;
    window.dispatchEvent(new CustomEvent('fantrade:notifications', { detail: lastNotes }));
  }

  function pullNotifications() {
    if (!FTDB.signedIn()) return Promise.resolve(null);
    return FTDB.notifications().then(function (rows) {
      if (rows) broadcastNotes(rows);
      return rows;
    }).catch(function () { return null; });
  }

  /* A page that has just woken up asks; whoever holds the list answers. */
  window.addEventListener('fantrade:notifications:want', function () {
    if (lastNotes) broadcastNotes(); else pullNotifications();
  });
  window.addEventListener('focus', function () { pullNotifications(); });

  var FTDB = {
    config: CONFIG,
    ready: load,
    client: function () { return client; },
    online: function () { return !!client; },
    session: function () { return session; },
    signedIn: function () { return !!(session && session.user); },
    userId: function () { return session && session.user ? session.user.id : null; },

    /* ── Account ──────────────────────────────────────────────── */
    signUp: async function (email, password, meta) {
      await load();
      if (!client) throw new Error('Cannot reach the server right now.');
      var res = await client.auth.signUp({ email: email, password: password, options: { data: meta || {} } });
      if (res.error) throw new Error(message(res.error));
      session = res.data.session;
      if (session) {
        await FTDB.notify({ kind: 'system', icon: 'star', title: 'Welcome to Fantrade',
          msg: 'Your manager account is ready, ' + email + '.', amt: '', tone: '' });
        pullNotifications();
      }
      return { session: session, needsConfirmation: !session };
    },
    signIn: async function (email, password) {
      await load();
      if (!client) throw new Error('Cannot reach the server right now.');
      var res = await client.auth.signInWithPassword({ email: email, password: password });
      if (res.error) throw new Error(message(res.error));
      session = res.data.session;
      await FTDB.notify({ kind: 'system', icon: 'shield', title: 'Signed in',
        msg: email + ' signed in to Fantrade.', amt: '', tone: '' });
      pullNotifications();
      return session;
    },
    signOut: async function () {
      await load();
      if (client) { try { await client.auth.signOut(); } catch (e) {} }
      session = null;
    },

    /* ── Data ─────────────────────────────────────────────────── */
    assets: async function () {
      await load();
      if (!client) return null;
      var res = await client.from('assets').select('*').eq('is_active', true).order('price', { ascending: false });
      return res.error ? null : res.data;
    },
    snapshot: async function () {
      await load();
      if (!client || !FTDB.signedIn()) return null;
      var res = await client.rpc('ft_snapshot');
      if (res.error) { console.warn('[Fantrade] snapshot failed:', res.error.message); return null; }
      return res.data;
    },
    /* The board is the one thing a signed-out visitor may read. */
    board: async function (limit) {
      await load();
      if (!client) return null;
      var res = await client.rpc('ft_leaderboard', { p_limit: limit || 50 });
      if (res.error) { console.warn('[Fantrade] leaderboard failed:', res.error.message); return null; }
      return res.data;
    },
    /* ── Notifications ──────────────────────────────────────────── */
    notifications: async function (limit) {
      await load();
      if (!client || !FTDB.signedIn()) return null;
      var res = await client.from('notifications')
        .select('id,kind,icon,title,msg,amt,tone,read_at,created_at')
        .order('created_at', { ascending: false })
        .limit(limit || 100);
      return res.error ? null : res.data;
    },
    notify: async function (row) {
      await load();
      if (!client || !FTDB.signedIn() || !row) return null;
      var res = await client.from('notifications').insert({
        id: row.id || noteId(), user_id: FTDB.userId(),
        kind: row.kind || 'system', icon: row.icon || 'bell',
        title: row.title, msg: row.msg || '', amt: row.amt || '', tone: row.tone || ''
      });
      if (res.error) { console.warn('[Fantrade] notification not stored:', res.error.message); return null; }
      return row;
    },
    markRead: async function (ids) {
      await load();
      if (!client || !FTDB.signedIn() || !ids || !ids.length) return null;
      var res = await client.from('notifications')
        .update({ read_at: new Date().toISOString() }).in('id', ids).select('id');
      if (res.error) { console.warn('[Fantrade] read state not stored:', res.error.message); return null; }
      return true;
    },

    /* ── Listings (admin drops) ──────────────────────────────── */
    /* The rows an admin listed from the Table Editor, each flagged with
       whether this manager has already claimed it. Null when the database
       has no 06_listings.sql yet — the page shows its fallback copy. */
    listings: async function () {
      await load();
      if (!client || !FTDB.signedIn()) return null;
      var res = await client.rpc('ft_listings');
      if (res.error) { console.warn('[Fantrade] listings unavailable:', res.error.message); return null; }
      return res.data;
    },
    claim: async function (listingId, level, vestingYears) {
      await load();
      if (!client) throw new Error('Cannot reach the server right now.');
      if (!FTDB.signedIn()) throw new Error('Sign in to claim a listing.');
      var params = { p_listing: listingId };
      if (level) params.p_level = Number(level) || 1;
      if (vestingYears) params.p_vesting_years = Number(vestingYears) || 1;
      var res = await client.rpc('ft_claim_listing', params);
      if (res.error && /parameters|signature|schema cache/i.test(res.error.message)) {
        res = await client.rpc('ft_claim_listing', { p_listing: listingId });
      }
      if (res.error) throw new Error(message(res.error));
      pullNotifications();
      return res.data;
    },

    /* ── Profile photo ───────────────────────────────────────── */
    /* A resized data URL, written straight to the manager's own profile row
       (01_schema's owner-only update policy). Warn-only: without
       07_profile_photo.sql the photo simply stays on this device. */
    saveAvatar: async function (dataUrl) {
      await load();
      if (!client || !FTDB.signedIn()) return null;
      var res = await client.from('profiles')
        .update({ avatar_url: dataUrl || '' }).eq('id', FTDB.userId());
      if (res.error) { console.warn('[Fantrade] photo not stored:', res.error.message); return null; }
      return true;
    },
    call: async function (fn, args) {
      await load();
      if (!client) throw new Error('Cannot reach the server right now.');
      if (!FTDB.signedIn()) throw new Error('Sign in to save this to your account.');
      /* Any notice this call is about lands through the page that made it;
         this pull picks up everything raised elsewhere since last look. */
      pullNotifications();
      var res = await client.rpc(fn, args || {});
      if (res.error) throw new Error(message(res.error));
      return res.data;
    }
  };

  window.FTDB = FTDB;
  load();
})(window);
