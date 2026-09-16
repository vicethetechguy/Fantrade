# FANTRADE — PHASE 1 AUDIT
### Product, UX, UI, Information Architecture, Interaction, Motion, Responsiveness, Technical Structure

**Audited build:** `Fantrade New` — 32 HTML pages, 8,096 lines of Python across 8 generator modules
**Method:** static source inspection of every generator and every built page, plus instrumented browser measurement (27–32 pages × 8 viewport widths, 320 → 1920px) for overflow, contrast, touch targets, type size, focus order, labelling, landmarks, payload and request profile
**Nothing in the codebase was modified. No files were created in the project. No redesign was started.**

---

## 1. EXECUTIVE SUMMARY

Fantrade today is an **exceptionally well-executed static prototype of a product whose core mechanic has not been built yet.**

Both halves of that sentence matter.

The craft is real and unusually high for this stage. Zero horizontal overflow across 8 widths and 27 pages. A coherent OLED-black and lime visual language that does not look like a Tailwind template. Real tabular-numeral typography. A working state store with optimistic updates and event-driven re-rendering. An order book that reads like an order book. `prefers-reduced-motion` honoured. That is a genuine asset and most of it should survive Phase 2 intact.

But three findings outrank everything else in this document:

**1. FanPlay — the mechanic the entire product exists to serve — does not implement the model you describe.** The current screen asks for *mode → tier → $FTR stake*. Your model is *asset → market → **options within that market** → **share** stake → **gain and loss preview** → activate*. There is no options layer in the code at all. Stakes are denominated in $FTR, not shares. There is no downside preview and no negative-FP path anywhere in the codebase. The projection is literally `base = 100` — a hardcoded constant that never reads the player you selected. FanPlay is, right now, a beautiful shell around a number that does not mean anything.

**2. Ownership — the product's founding rule — is decorative on the screen that most depends on it.** The Dream Club pitch renders eleven named players plus a bench from a hardcoded `FORMS` lookup table. The demo user owns four assets. The app therefore shows you fielding seven players you do not own, on the page whose entire premise is "you cannot play what you do not own." Anyone technical who opens this will spot it in ninety seconds, and it undermines the trust the rest of the UI works hard to build.

**3. There is no product architecture to redesign into.** No framework, no build step, no bundler, no router, no backend, no database, no API layer, no real authentication. `signIn()` accepts any email and never checks a password. State is one localStorage key. Every one of the 32 pages inlines a full copy of the stylesheet (100–109 KB), the full script shell (35–50 KB) and the full 47-symbol icon sprite — 5.7 MB of HTML total, with roughly 140 KB of byte-identical CSS and JS re-parsed on every single navigation and never cached. Phase 2 cannot be a visual redesign layered onto this. It needs a framework decision first, or the redesign will be thrown away twice.

**The honest assessment:** the *surface* is close to good. The *product* is about 35% built, and the most valuable 65% — FanPlay markets and options, real ownership enforcement, the FP↔$FTR conversion in both directions, and any backend at all — is missing rather than wrong. That is better news than it sounds. Missing is cheaper to fix than wrong.

**Do not let Phase 2 be a reskin.** The visual layer is not the bottleneck. If the next phase spends its budget on gradients and cards, Fantrade will look world-class and still be unable to answer "what can I lose?"

---

## 2. CURRENT PRODUCT ARCHITECTURE

### 2.1 What it actually is

| Layer | Reality |
|---|---|
| Framework | **None.** Static HTML, hand-generated |
| Build system | Python 3 string templating. `python3 pages.py && pages2 … pages5` |
| Package manager / deps | **None.** Zero npm, zero pip. No `package.json`, no lockfile |
| Router | Filesystem. `<a href="asset.html?a=$Saka">`. Full page loads |
| Component model | Python functions returning HTML strings |
| Styling | One ~2,500-line inline `<style>` per page, hand-written CSS with custom properties |
| State | `localStorage['fantrade_v1_state']`, single JSON blob, `FT` module in an IIFE |
| Reactivity | `window.dispatchEvent(new CustomEvent('fantrade:statechange'))` + manual re-render |
| API layer | **None** |
| Database | **None** |
| Auth | **Simulated.** Any email signs in; password is never validated |
| Charts | Hand-rolled SVG (`drawArea`, `drawCandles`, `spark`, `idx_chart`) |
| Icons | Inline SVG `<symbol>` sprite, 47 symbols, duplicated into every page |
| External requests | Google Fonts only. Zero other network calls |

### 2.2 Generator map

| File | Lines | Builds |
|---|---|---|
| `common.py` | 2,495 | Tokens, all CSS, icon sprite, `FT` store, shell (top bar, taskbar, `TAB_OF`), footer, charts, QR |
| `icons_data.py` | 68 | 40 Phosphor Light paths + 7 hand-drawn stroked icons |
| `qr_data.py` | 48 | Pre-computed QR matrix (avoids a runtime dependency — a good call) |
| `pages.py` | 1,490 | index, exchange, clubs, club-builder, fanplay, liveboard |
| `pages2.py` | 371 | ftr, how-it-works |
| `pages3.py` | 2,148 | signin, signup, onboarding, dashboard, portfolio, leaderboard, notifications, account, settings ×8 |
| `pages4.py` | 914 | asset, trade, divisions |
| `pages5.py` | 562 | send, receive, swap, buy, activity |

### 2.3 Measured payload profile

| Metric | Value |
|---|---|
| Total HTML shipped | **5.7 MB across 32 pages** |
| Inline CSS per page | 100–109 KB (identical on every page) |
| Inline JS per page | 35–50 KB (largely identical) |
| Icon symbols per page | 47 shipped; 7–21 used per page; **4 never used anywhere** (`armband`, `filter`, `hand`, `run`) |
| Cacheable shared assets | **0 bytes** |
| DOM nodes | 248 (signin) → 788 (index) — healthy |
| Images | **0** on every page — all vector. Genuinely good |
| External requests | Google Fonts only |

**The architectural verdict:** this is a very good *prototype* architecture and a completely unviable *product* architecture. It was the right call to get here. It is the wrong thing to redesign on top of.

---

## 3. ROUTE INVENTORY

**Priority key:** A = Critical · B = Important · C = Secondary · D = Utility

| # | Route | Purpose | Main actions | Data source | UX | UI | Mobile | Key problems | Pri |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `index.html` | Marketing landing | Sign up, explore | Static | 6/10 | 8/10 | 8/10 | Never defines $FTR; "Play to earn" reads crypto; no loss disclosure | **A** |
| 2 | `how-it-works.html` | Explains the loop | Read | Static | 7/10 | 8/10 | 8/10 | Buried behind nav; the real explanation lives here, not on the landing | **A** |
| 3 | `signin.html` | Sign in | Email + password | `FT.signIn` | 6/10 | 8/10 | 7/10 | No password check; decorative Passkey/Google/Wallet buttons; no forgot-password | **A** |
| 4 | `signup.html` | Create account | Form + terms | `FT.signUp` | 7/10 | 8/10 | 7/10 | Promises "50,000 $FTR", state seeds 128,450; fake SSO; no verification | **A** |
| 5 | `onboarding.html` | 4-step setup | Handle, fund, first asset, club | `FT.completeOnboarding` | 7/10 | **9/10** | 7/10 | Everything pre-filled, so nothing is decided; taskbar lets you escape the funnel | **A** |
| 6 | `dashboard.html` | Logged-in home | Scan, jump | `FT` state | 7/10 | 8/10 | 8/10 | Net worth 1,050,450 vs club value 245,800 vs holdings 917,000 — three unreconciled numbers | **A** |
| 7 | `exchange.html` | Market list | Search, filter, sort, drill | `ASSETS` (12) | 7/10 | 8/10 | 8/10 | Claims "420 markets", ships 12; no player/coach separation beyond a filter | **A** |
| 8 | `asset.html` | One asset's market | Chart, book, favourite, trade | `ASSETS` + holdings | 7/10 | 8/10 | 7/10 | **No `<h1>`**; football stats are thin; no FanPlay eligibility signal | **A** |
| 9 | `trade.html` | Order ticket | Buy / sell / swap, limit / market / stop | `FT.executeTrade` | 8/10 | **9/10** | 8/10 | **No `<h1>`**; 6 unlabelled inputs; focus rings suppressed | **A** |
| 10 | `clubs.html` | Dream Club | View XI, switch club | `FT.clubs()` + hardcoded `FORMS` | 5/10 | 8/10 | 7/10 | **XI is not derived from holdings** — shows 11 players, user owns 4 | **A** |
| 11 | `club-builder.html` | Build / edit a club | Name, shape, colour, save | `FT.createClub` | 5/10 | 7/10 | 7/10 | "Eight steps" promised, ~3 exist; slots don't validate ownership | **A** |
| 12 | `fanplay.html` | Enter a round | Mode, club, tier, stake | `FT.activateFanPlayEntry` | **4/10** | 8/10 | 8/10 | **No options layer. Stakes $FTR not shares. No loss preview. `base=100` hardcoded** | **A** |
| 13 | `liveboard.html` | Live scores | Follow fixtures, filter | Hardcoded `MATCHDAY` | 7/10 | 8/10 | 8/10 | Not connected to your entry; scores drift randomly | **B** |
| 14 | `leaderboard.html` | Standings | Search, sort, inspect | Hardcoded `BOARD` | 7/10 | 8/10 | 7/10 | 13 rows claiming 1,420 clubs; no pagination | **B** |
| 15 | `divisions.html` | Tier structure | Read | Static | 7/10 | 7/10 | 7/10 | Low traffic, fine as is | **C** |
| 16 | `portfolio.html` | Holdings + ledger | Filter, export, claim | `FT` holdings | 7/10 | 8/10 | 7/10 | "Export CSV" does nothing real; P&L partly hardcoded | **B** |
| 17 | `ftr.html` | Wallet | Card + assets, 4 actions | `FT.wallet` | 8/10 | **9/10** | **9/10** | **No `<h1>`**; otherwise the cleanest screen in the app | **A** |
| 18–21 | `send` `receive` `swap` `buy` | Wallet actions | Transfer, QR, swap, convert | `FT` methods | 8/10 | 8/10 | 8/10 | **No `<h1>`**; unlabelled amount fields | **B** |
| 22 | `activity.html` | Balance history, ledger, supply | Deposit, withdraw | `FT.transactions` | 7/10 | 8/10 | 7/10 | Supply donut is decorative — invented percentages | **C** |
| 23 | `notifications.html` | Feed | Filter, mark read | `FT.notifications` | 8/10 | 8/10 | 8/10 | Solid | **B** |
| 24 | `account.html` | Account hub | Navigate | `FT` state | 8/10 | 8/10 | 8/10 | Good hub pattern | **B** |
| 25 | `settings.html` | Settings hub | Navigate, sign out | Static | 8/10 | 8/10 | 8/10 | Good | **C** |
| 26–32 | `settings-*` ×7 | Profile, club, security, alerts, wallet, play, data | Edit + save | `FT` prefs | 7/10 | 7/10 | 7/10 | Security page is entirely cosmetic — no real 2FA or sessions | **C/D** |

**Missing routes that the product needs:** `404`, `forgot-password`, `verify-email`, `coaches` (a first-class coach market), `players` (discovery distinct from the raw ticker), `fanplay/[entry]` (a live entry view), `fanplay/history` (settled rounds), `club/[id]` (public club pages — required if leaderboards are to mean anything), `asset/[id]/fanplay` (per-asset market entry).

---

## 4. LANDING PAGE AUDIT

Read as a first-time visitor who has never heard of Fantrade.

| Question | Answer | Evidence |
|---|---|---|
| Do I understand what Fantrade is? | **Partly** | "A football ownership economy" + "Own the game. Build your club. Play to earn." I get *ownership* and *football*. I do not get the mechanism |
| Do I understand what I own? | **No** | "Player shares" appears **twice** in the entire page. Never defined, never illustrated |
| Do I understand what a player share is? | **No** | "Ten million shares, fixed" appears in a rules card two-thirds down. That is the single clearest statement on the page and it is buried |
| Do I understand what $FTR is? | **No** | Mentioned **28 times**, defined **zero times**. Is it a token? Points? Money? Can I withdraw it? |
| Why would I buy a player share? | **Weakly** | "Three jobs" is the right idea but is abstract: Own / Build / Play with no worked example |
| Do I understand FanPlay? | **No** | Named 10 times. Never shown. No screenshot, no example round, no numbers |
| Do I understand how I earn? | **No** | "Play to earn" is a claim, not an explanation |
| **What happens if I lose FP?** | **No — and this is the serious one** | **The landing page does not mention loss anywhere.** For a product where negative FP debits a real balance, that is both a comprehension failure and a regulatory exposure |
| Do I understand $FTR → shares → FanPlay → FP → $FTR? | **No** | The loop exists as six `<h4>`s (Take a position / Hold the shares / Assemble the club / Enter a round / Settle in $FTR / Grow the portfolio) but they are prose steps, not a diagram, and FP is never named in them |
| Is the value proposition immediately obvious? | **No** | I know it is about football and ownership. I could not explain it to a friend |
| Does it feel premium? | **Yes** | Genuinely. The type, the black, the restraint |
| Does it feel like a real financial product? | **Partly** | It looks like one. It does not *disclose* like one |
| Does anything feel AI-generated? | **Yes, in places** | See §18 |
| Is there unnecessary copy? | **Yes** | The "keeps it honest" section is five cards where two would do |
| Is the hierarchy strong? | **Yes at the top, weak below** | The hero is excellent. Below the fold every section is the same weight |
| Is the CTA obvious? | **Yes** | "Start trading" is unambiguous |
| Does the page create trust? | **Mixed** | Design says yes; absence of risk language, real numbers and any named team says no |

### The landing page's five specific failures

1. **$FTR is never defined.** The most-repeated term on the page has no explanation. One sentence would fix it.
2. **Player shares are never shown.** Not one example of a real asset with a price, a share count and what owning it does for you. The exchange console lower down is the closest thing and it reads as decoration.
3. **FanPlay is invisible.** The product's differentiator is named ten times and demonstrated zero times.
4. **No loss disclosure.** A product that can debit your balance must say so above the fold.
5. **"Play to earn" is the wrong phrase.** It is crypto-2021 vocabulary and it invites exactly the comparison the product should avoid. Fantrade's story is *ownership plus football knowledge*, not yield.

**What already works and must survive:** the hero typography, the black, the pill CTA pair, the three proof chips (10,000,000 shares per asset / 2,140 players & coaches / Settled in $FTR), and the live exchange console below the fold. That console is the single best argument the page makes — it should be promoted, not buried.

---

## 5. AUTHENTICATION & ONBOARDING AUDIT

### Sign up — 7/10 UX, 8/10 UI

Four fields, a live password-strength meter, an explicit terms checkbox with an age gate, per-field inline errors. That is a well-built form. Three problems:

- **"Start with 50,000 $FTR" is contradicted by the app.** The state seeds `balance: 128450`. First impression after signup is a number that does not match the promise.
- **Passkey / Google / Wallet are decorative.** They render, they have `data-provider`, they do nothing. Fake SSO on a financial product is a trust liability, not a placeholder.
- **No email verification route exists.** `signUp()` sets `verified: true` immediately.

### Sign in — 6/10

- **No password validation whatsoever.** `signIn(email, name)` sets `signedIn = true` and returns. Any string works.
- **No forgot-password route.** For a product holding a balance this is a required flow, not a nice-to-have.

### Onboarding — 7/10 UX, **9/10 UI**

The strongest-designed screen in the product. The persistent right-hand summary rail ("Your setup so far" → Manager / Handle / Region / Wallet / First asset / Club / Ready for) with "What happens next" underneath is genuinely excellent UX — it answers "where am I and what is this for" at every step. **Keep this pattern and reuse it in FanPlay.**

Its problems are conceptual, not visual:

- **Every field is pre-filled, so the user decides nothing.** Handle is `@alex_trader`, region United Kingdom, wallet already 128,450 $FTR, club already "Zero FC · 4-3-3" — at *step 1*. The funnel teaches the user that their input does not matter.
- **Step 2 "Fund your wallet" funds an already-funded wallet.**
- **The app taskbar is visible throughout**, so the user can leave the funnel at any point and land in a half-configured app.
- **Step 3 buys the first asset but never explains what a share is** — the one moment where that explanation would land.

### First-time experience verdict

**A new user cannot understand what to do without assistance.** They can complete the flow — the forms are clear — but they will arrive at the dashboard without knowing what they own, what $FTR is, or what they are supposed to do next. The onboarding teaches mechanics (fill this field) rather than the model (this is what ownership buys you).

---

## 6. APP UX AUDIT

### Navigation — strong, and the best structural decision in the product

Five destinations (Home · Exchange · FanPlay · Leaderboard · Account), FanPlay centre, floating taskbar, slim top bar with the $FTR chip and the bell. Every one of the 32 pages maps to exactly one tab via `TAB_OF`. Breadcrumbs on every drill-down. **This is genuinely good and should not be touched.**

Two gaps: there is no global search (only a market search inside the Exchange), and no back-affordance in the top bar on desktop — users rely on browser back.

### Information hierarchy — the app's weakest non-FanPlay dimension

The **numbers do not reconcile**, and on a financial product that is fatal to trust:

| Surface | Number shown |
|---|---|
| Dashboard "Net worth" | 1,050,450 $FTR |
| Dashboard "Held in shares" | 917,000 |
| Dashboard "Club valuation" | 245,800 |
| Clubs page "Club value" | 245,800 (Starting XI 180,600 + Bench 45,200 + Coach 20,000) |
| Actual holdings (4 assets × price) | ≈ 917,000 |

The club is valued at 245,800 while containing eleven players whose combined market value would far exceed the user's entire 917,000 portfolio. **These are three different fictions that do not agree.** A user who adds them up loses confidence in every number on the screen.

### Where users are forced to think too much

1. **FanPlay projection.** "100 FP × 2.0 × +15% = 230." Where does 100 come from? It is a constant. The user cannot verify anything.
2. **Club boost.** +15% is asserted on the dashboard, the clubs page and FanPlay, with a "chemistry" explanation on a marketing page. The number is stored, never computed.
3. **Locked vs available $FTR.** `wallet.locked` is shown in three places with no explanation of what unlocks it or when.
4. **Fans Point.** FP appears throughout the app and is never defined in-app. `how-it-works.html` is the only place it is explained, and it is in the marketing nav.

### Missing information

- No FanPlay history. Settled rounds vanish — only `activeEntries` exists.
- No per-asset performance data worth the name. An asset page for a footballer shows a candlestick chart and an order book, and almost no football.
- No fee schedule anywhere except inline "(0.4%)".
- No statement of what happens on a losing round.

---

## 7. EXCHANGE AUDIT

### Can the user immediately understand… ?

| | Verdict |
|---|---|
| Who the player is | **Yes** — name, ticker, avatar, SHARE/COACH tag |
| Player value | **Partly** — price in $FTR with a £ equivalent. Market cap is a static string (`cap:'482.0M'`), not computed |
| Share price | **Yes** — clear, tabular, well set |
| Their owned shares | **Yes** — "you hold 10,000" inline on the row. Good |
| Available shares | **No** — float, circulating supply and available-to-buy are never shown |
| Market movement | **Yes** — 24h pill, live tick simulation |
| Buy / Sell / Swap | **Yes** — the rebuilt ticket is the strongest screen in the app |
| Their exposure | **No** — no position size, no average cost, no unrealised P&L on the trade screen |
| Potential portfolio value | **No** — no "if you buy this, your portfolio becomes…" |
| Transaction history | **Partly** — "Your fills" exists but is scoped to the current asset only |

### The Exchange's real problems

1. **12 assets, marketed as 420.** The page footer says "12 of 12 assets" while the CTA says "All 420 markets" and the landing claims "2,140 players & coaches". Pick a number and make it true.
2. **Coaches are a filter, not a market.** Coaches are your most distinctive asset class — the thing no competitor has — and they are a chip labelled "Coaches" in a list of footballers. They deserve their own surface.
3. **No discovery layer.** There is a search box and six sort tabs. There is no "rising", no "by position", no "by league", no "by club", no watchlist, no comparison. For 12 assets that is fine; for 2,140 it is unusable.
4. **The Team index is the user's own portfolio, not a market index.** It is labelled like a market indicator and sits where a market indicator belongs. It is genuinely useful — but it should be named for what it is.
5. **Nothing links a market to FanPlay.** The Exchange and FanPlay are two products in one app. An asset row should tell me whether that player is playing this window, and let me stake from there.

**Does it feel like a premium financial marketplace rather than a generic crypto dashboard?** The *trade ticket* does — order book left, ticket right, tick grouping, depth tints, %-slider. The *list* does too. What is missing is the **football**. Strip the names and this is a crypto exchange. There is no fixture, no form, no position, no minutes, no club crest, no next opponent. The football culture the brief asks for is almost entirely absent from the surface that matters most.

---

## 8. PLAYER & COACH ASSET PAGE AUDIT

`asset.html` is well built and structurally sound: price header, 24h high/low/volume, five timeframes, candlesticks, a sticky Buy/Sell bar, and four panes (Order book / Trade history / Coin info / Your position).

**The problem is that it is a crypto asset page with a footballer's name on it.**

| Can the user understand… | Verdict |
|---|---|
| Who the asset is | Name + ticker + role. **No photo, no club, no position, no age, no league** |
| Current value | Yes |
| Share price | Yes |
| Price movement | Yes — the candlesticks are good |
| Market activity | Yes — book and trade history |
| Their holdings | Yes — in the "Your position" pane, but buried behind a tab |
| Buy / Sell / Swap | Yes — via the sticky bar |
| **FanPlay eligibility** | **No — entirely absent** |
| **Performance** | **No** |
| **Football statistics** | **No — none at all** |
| Ownership information | Partly — no holder count, no float |

### What is missing

The tab literally named **"Coin info"** on a page about Bukayo Saka is the single clearest symptom of the product's identity problem.

An asset page for a footballer must answer: who is he, who does he play for, what position, what form, what is his next fixture, how has he scored in FanPlay historically, is he fit, is he starting, and how many FP has he generated for holders. **None of that exists.** The football data layer is not thin — it is absent.

Coaches are worse: identical layout, `whistle` icon instead of `boot`, amber instead of lime. A coach's value derives from results, formation match and club modifier — none of which appear. **Coach pages need their own information model, not a colour swap.**

---

## 9. FANPLAY AUDIT

This is the section that should drive Phase 2.

### What exists today

```
Mode (Individual | Dream Club)
  → Club picker (Dream Club mode only)
  → Market tier (6 cards, each carrying one multiplier and a variance bar)
  → Stake amount in $FTR (field + quick amounts + weekly-cap meter)
  → Projection: base 100 FP × (1 + club boost) × tier multiplier
  → Activate → debits $FTR, creates an entry, one entry per club per round
```

### Gap analysis against your stated model

| Your model | Implementation status |
|---|---|
| **INDIVIDUAL** | |
| 1. Choose a player | ⚠️ Partial — mode exists, but the player is hardcoded `$Bruno`. There is no player picker |
| 2. Choose a market | ✅ Six tiers exist and are selectable |
| 3. **Choose options within that market** | ❌ **Does not exist in any form.** No data structure, no UI, no concept. Markets are a single multiplier |
| 4. **Stake player shares** | ❌ Stake is denominated in **$FTR**. Shares are never debited |
| 5. **Preview potential gain AND potential loss** | ❌ Gain only. **The word "loss" does not appear in the FanPlay code path** |
| 6. Confirm / activate | ✅ Works, with duplicate protection |
| 7. Match happens | ⚠️ Simulated on a separate page, unconnected to the entry |
| 8. Real events generate FP | ❌ No engine. No event model |
| 9. Positive FP → $FTR | ❌ No settlement path |
| 10. **Negative FP reduces $FTR** | ❌ **Does not exist. There is no downside anywhere in the product** |
| **TEAM** | |
| 1. Choose a club | ✅ Club rail works well |
| 2. Choose a market | ✅ |
| 3. Choose options | ❌ Same gap |
| 4. Stake amount/% of team shares | ❌ $FTR again |
| 5. **Distribute exposure equally across eligible team assets** | ❌ No distribution logic |
| 6–8. Preview accumulated FP / gain / loss | ❌ Single flat number |
| 9. Activate | ✅ |
| 10–13. Per-asset outcomes → accumulate → convert | ❌ None of it |

### The `base = 100` problem

```js
var base = 100, total = Math.round(base * (1 + boost) * mult);
```

The projected FP is a constant multiplied by two other constants. It does not read the player, the fixture, the market, the options, the stake, or anything else. **Change the stake from 1,000 to 100,000 $FTR and the projection does not move.** A user who notices this — and a serious one will, in about thirty seconds — will conclude the whole product is a mock-up. This single line does more damage to credibility than every visual issue in this document combined.

### Subscription gating

You are removing it. **It is not in the code** — all six tiers are already selectable with no gate. Nothing to remove.

### What the six markets currently mean vs what they need to mean

Today each tier is `(name, multiplier, one-line description, variance %)`. The description says what *counts* (goals, assists, key passes…). Under your model a market is a **set of selectable options** the user picks from, with complexity and exposure scaling up the ladder. That is a completely different data structure — markets need an options schema, options need odds/weights, and selections need to compose into a settlement rule. **None of this is modelled.** This is the single largest piece of new product design Phase 2 must produce, and it is a product-design job before it is a UI job.

---

## 10. FANPLAY UX AUDIT — THE EIGHT QUESTIONS

| Question | Answered today? | Detail |
|---|---|---|
| **What am I playing?** | ⚠️ Partially | Mode is clear. Whether I am playing a *fixture*, a *window* or a *season* is never stated on the screen |
| **Who am I playing?** | ⚠️ Partially | Club mode shows the club. Individual mode shows `$Bruno` with no way to change it |
| **What market am I using?** | ✅ Yes | The tier cards are the best part of the screen — name, ×multiplier, variance bar |
| **What options did I select?** | ❌ **No** | There are no options |
| **How many shares am I staking?** | ❌ **No** | The field is in $FTR. Shares are never mentioned |
| **What can I gain?** | ⚠️ Weak | "Projected 230 FP" — but FP is undefined in-app and never converted to $FTR on screen |
| **What can I lose?** | ❌ **No** | Nothing on the page suggests loss is possible |
| **What happens after I activate?** | ❌ **No** | A toast, an entry count, and the button greys out. No confirmation screen, no "here is your entry", no link to watch it |

**Six of eight unanswered or half-answered on the product's most important screen.** The brief says the user should never have to guess these. Today they must guess most of them.

### What the redesign must add (product, not pixels)

1. An **asset picker** for Individual mode.
2. An **options layer** — the core missing concept.
3. **Share-denominated staking**, with the share balance visible and debited.
4. A **two-sided preview**: maximum gain, maximum loss, break-even, in both FP and $FTR.
5. A **confirmation step** — this is a financial commitment and it currently takes one click with no review.
6. An **entry detail screen** — what I staked, on whom, which options, what it is worth live.
7. **Settlement** — the round closing, the FP landing, the $FTR moving, in both directions.

---

## 11. DREAM CLUB AUDIT

### What exists

Multi-club support (up to six), a switcher rail, per-club colour/crest/formation/division/rank/boost, a pitch renderer with four formations, a bench with auto-sub copy, a captain with ×1.5, tabs for line-ups / league position / form, and a club-value breakdown.

**The visual execution of the pitch is very good.** It reads as football, not as a dashboard. Keep it.

### The fatal flaw

```python
FORMS = {'4-3-3': [[['ST','$Haaland']], [['LW','$Vinicius'],['CAM','$Bruno',1],['RW','$Saka']], …
```

**The eleven is a hardcoded lookup table.** It is not derived from `state.holdings`. The demo user holds four assets — `$Saka`, `$Bruno`, `$Haaland`, `$Arteta` — and the pitch renders `$Vinicius`, `$Rice`, `$Odegaard`, `$Davies`, `$VanDijk`, `$Saliba`, `$White`, `$Raya` plus a four-man bench.

The club-builder has the same issue: slots do not validate against holdings, and the promised "eight steps" is closer to three (name, shape, colour).

**"You cannot use a player you do not own" is the product's founding rule, and the screen that exists to express it violates it.** This is not a UI bug. It is the number-two priority in this document after FanPlay.

### Also missing

- **Club value is a stored constant** (245,800), not the sum of the assets on the pitch.
- **The boost is a stored constant** (+15%), not computed from chemistry, coach match or squad completeness — despite three separate surfaces explaining how it is "calculated".
- **No empty state.** A brand-new user with zero holdings has no defined Dream Club experience.
- **Clubs are private.** Leaderboards rank 1,420 clubs that cannot be viewed. The social layer the rankings imply does not exist.

### Split by layer

| Needs architecture | Needs UI only |
|---|---|
| Derive the XI from holdings | Pitch visual language |
| Validate every slot against ownership | Club switcher rail |
| Compute club value from assets | Tabs and form table |
| Compute the boost from real inputs | Crest and colour system |
| Public club pages | Club-value breakdown |
| Empty state for zero holdings | — |

---

## 12. ICONOGRAPHY AUDIT

### Inventory

| Source | Count | Style |
|---|---|---|
| Phosphor Icons (Light) | **40** | Filled outline — paths tracing a stroke |
| Hand-drawn (added during build) | **7** | True strokes — `stroke-width:12`, round caps |
| Emoji used as UI | **0** ✅ |
| Raster / 3D / stock illustration | **0** ✅ |
| Never used anywhere | **4** | `armband`, `filter`, `hand`, `run` |

### Findings

1. **Two rendering models in one set.** Phosphor Light icons are *filled outlines*; the seven taskbar icons are *stroked paths*. At 20px they read similarly by luck, not by design. At 34px (`.ic-xl`, used in empty states) the difference is visible. **This is the main icon-system defect.**
2. **The taskbar set is bespoke and unversioned.** `home`, `market`, `podium`, `profile`, `send`, `receive`, `bell` were drawn by hand with hardcoded coordinates. They are the icons the user sees most. They have no source file, no grid, no export pipeline.
3. **Four dead symbols ship on all 32 pages.** Small cost, but it signals the sprite is not curated.
4. **Sizing is inconsistent.** Four size classes (15/20/26/34px) plus ad-hoc overrides in at least a dozen places (`.coin .ic{19px}`, `.bell .ic{15px}`, `.pairhead .chip .ic{16px}`, `.seg2 .ic{19px}`…). There is no size scale, only exceptions.
5. **`.ibox` — the 40px rounded icon container — is used decoratively.** On `how-it-works` it appears on nearly every card. That is one of the strongest "AI-generated dashboard" tells in the product (§18).
6. **Semantic mismatches remain.** `candle` (a chart) does duty for order type. `layers` means "network". `flag` means "warning". `hand` meant "send" before the rename. `receipt` means "jump to orders" on the trade page.
7. **No icon means anything football-specific beyond four.** `ball`, `boot`, `whistle`, `pitch`, `crest`, `formation`, `subs`, `stadium`, `armband` exist — that is actually a decent football vocabulary and is the most Fantrade-specific asset in the system. **It is under-used.** The app leans on generic chart/wallet/receipt icons where a football metaphor would differentiate it.

### Direction for Phase 2 (do not implement yet)

One geometry, one stroke weight, one grid, one export pipeline. Reduce the set to what is actually used (43), split into **UI icons** (navigation, actions, states — neutral, 1.5px stroke) and **Fantrade glyphs** (boot, whistle, crest, pitch, armband — the brand layer, used sparingly and at larger sizes). Remove `.ibox` from decorative use entirely.

---

## 13. MOTION & INTERACTION AUDIT

### Inventory

| Measure | Value |
|---|---|
| `transition` declarations | **71** |
| Durations | .5s ×29, .6s ×16, .4s ×15, .7s ×13, .9s ×5, and 8 others |
| Easing curves | `cubic-bezier(.32,.72,0,1)` (primary), `cubic-bezier(.16,1,.3,1)` (secondary) |
| `@keyframes` | **1** (`blip` — the live dot) |
| `prefers-reduced-motion` | **Handled**, in CSS and in JS (`reduce` flag) ✅ |
| `setInterval` timers | **6** — countdowns, price ticks, live score drift, running FP |
| Page transitions | None (full page loads) |
| Scroll reveal | `IntersectionObserver` + `[data-reveal]` on ~every block |

### What feels right

- The easing curve is well chosen — a proper decelerating curve, not `ease-in-out`.
- Reduced-motion support is real and complete. Rare at this stage.
- The `.blip` live dot and the red live-fixture tint are restrained and appropriate.
- Toasts and modals animate cleanly.

### What feels wrong

1. **Everything is too slow.** 29 transitions at 500ms and 13 at 700ms. A *trading* interface should feel instant — hover and press feedback belongs at 120–180ms. At half a second, the UI feels like it is thinking. **This is the single biggest motion problem and it is a one-line-per-rule fix.**
2. **Scroll reveal is applied indiscriminately.** Nearly every block fades up on entry, including inside the logged-in app. On a landing page that is fine. On a dashboard the user visits ten times a day it is friction — data should be *there*, not arrive.
3. **No number animation.** Prices, balances and FP snap between values. For a live market this is the one place motion would genuinely help — a counting/ticking transition on value change would make the product feel alive in the way the brief asks for.
4. **No page transitions at all.** Full page loads mean a white-to-black flash on every navigation. On mobile this reads as a website, not an app.
5. **No optimistic/pending states.** Trades apply instantly with a toast. Real settlement has latency; there is no pattern for it.
6. **Live simulation is random, not modelled.** Scores drift on `Math.random() < 0.08`. It animates, but it does not mean anything.

---

## 14. MOBILE / RESPONSIVE AUDIT

### The headline result — and it is genuinely excellent

**Zero horizontal overflow across 8 widths × 27 pages = 216 page-width combinations tested.** 320, 360, 390, 414, 768, 1024, 1440, 1920. Not one failure.

That is a rare result and it is the strongest single engineering fact in this audit. Combined with the safe-area handling, the `-webkit-text-size-adjust` lock and the 16px input font (preventing iOS auto-zoom), the responsive foundation is solid. **Preserve it.**

### Confirmed problems

1. **Type runs far too small on phones.** Measured at 320–414px: `8.5px`, `9px`, `9.5px`, `10px` on labels, sub-lines, metadata and table headers across every page — and `7.5px` on the pitch position labels. iOS guidance is 11px minimum; 12px is the practical floor for sustained reading. **This is systemic, not local.**
2. **Touch targets below 44px are everywhere.** Measured on phone widths: the logo (95×22), the header CTA (123×31), crumbs (13×13 icon), `.bell` (31×31), `.eye` password toggle (38×11), `.maxbtn` (66×27), stepper buttons (~28×34), tick-size select (57×21), star/favourite buttons (19px). Apple and Google both specify 44×44 / 48×48. **Almost nothing in the app meets it.** The `.btn{min-height:46px}` rule exists for in-page buttons — that discipline needs to extend to every interactive element.
3. **Tables degrade by hiding columns.** `.dh/.dr` drop children at breakpoints. It works visually but the data is simply gone — there is no way to reach the hidden columns on a phone. For the portfolio and leaderboard, that is real information loss.
4. **The trade terminal at 320px is dense to the point of strain.** Two columns, 10.5px book rows. It matches the reference app, but the reference has a larger minimum.
5. **The pitch at 320px** renders 7.5px position labels — effectively unreadable.
6. **No landscape handling.** A phone in landscape gets the desktop layout at ~700px tall with a fixed top bar and taskbar eating ~90px.
7. **No tablet-specific layout.** 768–1024px inherits mobile rules; a 1024px iPad gets phone-scale type in a 1024px container.

---

## 15. ACCESSIBILITY AUDIT

### Contrast — measured, not estimated

| Token | Hex | On `--core` #0A0B0C | Verdict |
|---|---|---|---|
| `--ink` | #F4F6F1 | **18.10:1** | Pass |
| `--lime` | #C4F82A | **15.77:1** | Pass |
| `--amber` | #FF6A1F | **6.88:1** | Pass |
| `--red` | #FF5E5E | **6.58:1** | Pass |
| `--dim` | #8B918A | **6.11:1** | Pass |
| **`--faint`** | **#5A605B** | **3.06:1** | **FAIL** — needs 4.5:1 |

`--faint` fails AA for normal text — and it is used almost exclusively at **8.5–11px**, which is precisely where the 4.5:1 threshold applies. It drives `.k-label`, `.sub-line`, `.meta`, `.qt`, `.hint`, `.mkhead`, `.tline span`, `.lbl`, `.cd` and the pcts scale. **This is one token change that fixes dozens of violations across every page.** Raising it to roughly `#7A817B` clears 4.5:1 while keeping the hierarchy.

### Focus

- A good global rule exists: `:focus-visible{outline:1.5px solid var(--lime);outline-offset:4px}`.
- **But five `outline:none` declarations kill it** on `.searchbox input`, `.field input`, `.tf input/select/textarea`, `.stp input` and `.otype select`. A keyboard tab-walk through the trade ticket confirmed it: the order-type select, the limit, quantity and amount fields, and the book buttons all showed `outline: 0px`. **Every form field in the app — sign-in, sign-up, send, swap, trade — is keyboard-invisible.**

### Labels

**12 unlabelled form controls** across 6 pages: `obFiat`, `obShares` (onboarding), `q` (exchange search), `tType`, `tStop`, `tLimit`, `tQty`, `tAmt`, `swQty` (trade), `fpStake` (fanplay), `sendAmt` (send), `swapQty` (swap). The visible label sits in a sibling `<span class="lbl">` with no `for`/`id` relationship, so a screen reader announces "edit text, blank".

### Structure

- **Five pages have no `<h1>`:** `asset`, `trade`, `ftr`, `send`, `swap`. On `asset` and `trade` the heading vacuum is the whole page.
- **No skip link on any page.** With a fixed top bar, a 5-item taskbar and a 5-column footer, a keyboard user traverses ~15 links before reaching content on every navigation.
- `<main>`, `<nav>`, `<header>`, `<footer>` are used correctly ✅
- `aria-live` region present for toasts ✅
- `aria-pressed` / `aria-selected` used correctly on tabs and toggles ✅
- **13 `<button>` elements without `type` on onboarding** (default `submit` inside a form is a latent bug).
- Escape closes modals ✅; focus is **not** trapped inside them ✗; focus is **not** returned to the trigger on close ✗.

### Motion

`prefers-reduced-motion` is properly handled in both CSS and JS. ✅

---

## 16. PERFORMANCE AUDIT

*Reported only — nothing optimised.*

| Finding | Severity | Detail |
|---|---|---|
| **No shared, cacheable assets** | **Critical** | Every page inlines 100–109 KB CSS + 35–50 KB JS + a 47-symbol sprite. A user navigating 10 pages downloads and re-parses ~1.4 MB of identical bytes. Extracting one `app.css` + one `app.js` would cut repeat-navigation payload by ~95% |
| Total HTML weight | High | 5.7 MB for 32 pages |
| Dead icon symbols | Low | 4 unused symbols × 32 pages |
| No compression configured | Medium | These files gzip to roughly 15% of source; nothing in the repo configures it |
| 6 `setInterval` timers | Medium | Countdown, price ticks, score drift, FP ticker — all run indefinitely, none pause on `visibilitychange`. Battery cost on mobile |
| Inline `style` attributes | Medium | Up to 99 per page (leaderboard) — unstyleable, uncacheable, hard to theme |
| No lazy loading | Low | Moot today (zero images), will matter when player photos arrive |
| Layout shift | Low | Charts draw from JS after paint; `[data-reveal]` starts elements translated |
| Font loading | Low | Three families from Google Fonts with `display=swap`. Correct, but three families is a lot |
| No image pipeline | — | Positive today, but the product needs player photography and there is no strategy for it |

Measured page load on localhost: **654–1000 ms**. That is local disk with no latency — the real-world number will be dominated by the uncached 140 KB per navigation.

---

## 17. DESIGN SYSTEM AUDIT

### Colour

```
--void   #050505   page background
--core   #0A0B0C   card interior
--shell  rgba(255,255,255,.035)   card frame
--hair   rgba(255,255,255,.08)    borders
--hair-2 rgba(255,255,255,.14)    hover borders
--ink    #F4F6F1   primary text
--dim    #8B918A   secondary text
--faint  #5A605B   tertiary text        ← fails AA
--lime   #C4F82A   primary / players / positive
--amber  #FF6A1F   coaches / boost / warning
--red    #FF5E5E   negative
--live   #FF3B47   live-only accent (separate from --red)
```

**Assessment:** tight, disciplined, and genuinely distinctive. Eleven tokens for a product this size is restraint, not poverty.

**Gaps:** no success token distinct from `--lime` (so "positive price" and "primary action" are the same colour — a real problem on a trading surface where the CTA and the gain indicator should not be identical); no info/neutral token; `--red` and `--live` overlap in meaning; no elevation scale (one `--ambient` shadow); no semantic aliases (`--text-primary`, `--surface-1`) so every consumer references raw tokens.

### Typography

| Family | Use | Weights |
|---|---|---|
| **Archivo** (variable) | Display, headings, buttons | wdth 125, wght 800–900, uppercase |
| **Montserrat** | Body, labels, UI | 300–600 |
| **JetBrains Mono** | All numbers, tabular | 300–500 |

**This is the strongest part of the design system.** Using a monospace with tabular numerals for every financial figure is exactly right and it is the main reason the product reads as credible. Keep all three.

**Gaps:** no type scale — sizes are declared ad hoc (measured: 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 16, 17, 19, 22, 24, 26… ≈ **22 distinct sizes**). There are two parallel scales (marketing vs `body.app` DENSE_CSS) with no documented relationship. Line-height is set globally at 1.7 and overridden everywhere.

### Spacing

No scale exists. Padding values in use include 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 26, 28, 30, 34, 36, 38, 40, 44px. Gaps similarly. **This is the least systematic dimension of the design system** and the main reason small inconsistencies keep appearing between screens.

### Radius

`--r-out: 2rem`, `--r-in: calc(2rem - .5rem)` as tokens — but literal values (6, 7, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 999px) appear throughout. Roughly 14 radii in use against 2 tokens.

### Components

| Component | State |
|---|---|
| Buttons | 6 variants (`btn-lime`, `btn-glass`, `btn-red`, `btn-sm`, `bigbtn`, `tradebtn`) — **overlapping and undocumented** |
| Inputs | 5 unrelated patterns (`.field`, `.tf`, `.stp`, `.tfield`, `.searchbox`) — **the worst duplication in the system** |
| Cards | `.bezel > .core` double-bezel, plus `.bezel.flat`, `.bezel.tight` — coherent |
| Tables | `.dt/.dh/.dr` + per-page column overrides — works, but every table redefines its columns inline |
| Tabs | 4 systems: `.tabs`, `.utabs`, `.tabstrip`, `.seg2`, `.sideseg` — **five, actually** |
| Badges | `.tag`, `.pill`, `.lev`, `.mine` — overlapping |
| Dropdowns | `.otype`, `.netsel`, `.ticksel`, `.tf select` — four patterns |
| Modals | One system, well built ✅ |
| Toasts | One system, well built ✅ |
| Navigation | One system, excellent ✅ |
| Charts | 4 renderers (`drawArea`, `drawCandles`, `spark`, `idx_chart`) — no shared axis, tooltip or legend model |
| Empty states | One pattern, 16 uses ✅ |
| **Loading states** | **None** |
| **Skeletons** | **None** |
| **Error states** | **None** — no 404, no failure UI |

---

## 18. BRAND CONSISTENCY AUDIT

### Consistent ✅
Colour palette · three type families · double-bezel card · taskbar · top bar · footer · crumb pattern · toast · modal · lime-for-players / amber-for-coaches

### Inconsistent ✗

1. **Terminology — the most damaging category.**
   - **"Fans Point" vs "Fantrade Points" vs "FP".** The app now says "Fans Point". This audit brief says "Fantrade Points". Both are in circulation. **Decide and enforce, including in internal documents.**
   - "Dream Club" / "club" / "syndicate" / "team" — four words for one object, all in use.
   - "Manager" / "fan" / "user" / "holder" — four words for one person.
   - "Market tier" / "market" / "tier" — used interchangeably for the same thing, which becomes actively confusing once markets gain options.
   - "Round" / "window" / "matchday" / "gameweek" — four words for one time period.
2. **Numbers contradict across surfaces.** 50,000 $FTR promised at signup vs 128,450 seeded. 420 markets vs 12 assets. 2,140 players & coaches vs 12. 1,420 clubs vs 13 rows. 48,206 vs 1,420 as the club population (both appear).
3. **Five input patterns, five tab systems, six button variants.**
4. **Two type scales** with no documented relationship.
5. **Radius drift** — 14 values against 2 tokens.
6. **Icon weight** — two rendering models (§12).

**Brand identity to preserve:** the OLED black, the lime, the Archivo-uppercase display voice, the monospace numerals, the double-bezel, and the five-tab shell. That combination is Fantrade's and does not look like anything else. **Do not let Phase 2 redesign the brand.** The problems above are consistency problems, not identity problems.

---

## 19. "AI-GENERATED FEEL" AUDIT

Ranked by how strongly each signals machine-generated UI.

| # | Pattern | Where | Why it reads as AI-generated |
|---|---|---|---|
| 1 | **The `.ibox` icon-in-rounded-square on every card** | how-it-works, account, settings, index, fanplay | The single most recognisable LLM-UI tell. A 40px rounded container with a centred icon, repeated down a page, is the default output of every AI UI prompt. It carries no information |
| 2 | **Uniform card grids where every card has icon + title + one-line description** | index (three-jobs, keeps-it-honest), how-it-works (mechanics, tiers, chemistry), account, settings | Real products vary card weight by importance. Identical cards mean the layout was generated, not designed |
| 3 | **Three floating gradient orbs behind every page** | Global `atmosphere()` | Ambient blurred colour blobs are the most over-used AI background. They are on all 32 pages and add nothing |
| 4 | **Explanatory copy in the voice of a product explaining itself** | Largely removed this cycle, but remnants persist in how-it-works and the landing | "Every asset you own does three jobs" is a sentence a model writes, not a team |
| 5 | **Six equal market tiers with escalating multipliers and variance bars** | fanplay | Suspiciously tidy: ×1, ×1.4, ×2, ×3, ×4.5, ×7 with variance 18/32/50/68/84/100. Real products have irregular, playtested numbers |
| 6 | **Round numbers everywhere** | Throughout | 10,000,000 shares. 420 markets. 1,420 clubs. 2,140 players. 0.4% fee both sides. +15% boost. 100 base FP. Real data is untidy |
| 7 | **Gradient-filled hero card with a large number** | ftr wallet | The lime gradient balance card with the giant figure is the default "wallet UI" output |
| 8 | **Decorative donut with invented percentages** | activity (circulating supply 46/28/14/12) | A chart of numbers nobody computed |
| 9 | **Glassmorphism on the nav island** | Global | `backdrop-filter: blur(22px) saturate(160%)` — executed well, but the pattern itself is generic |
| 10 | **Everything fades up on scroll** | Global `[data-reveal]` | Uniform reveal on every block is a generated-site signature |
| 11 | **Five-column footer with invented link groups** | Global | "Press" and "Contact" link to `#`. A footer sized for a company that does not exist yet |
| 12 | **Placeholder names that read as generated** | Throughout | "Zero FC", "Apex Titans FC", "Galactico Syndicate", "Bavarian Meta XI", "@CryptoKlopp", "@SatoshiZidane" — the crypto-portmanteau handles in particular |
| 13 | **"Viynx Move" / "Viynx Max"** | fanplay tiers | Invented-brand-word pattern with no explanation anywhere |
| 14 | **Perfectly balanced bento grids** | dashboard, portfolio, account | c5+c4+c3 / c7+c5 columns that always sum to 12 with nothing dominant |
| 15 | **Every section introduced by an eyebrow + heading + lede** | Largely removed this cycle from the app; still the structure of the marketing pages | The three-part section header is the most predictable AI layout unit |

**The deepest problem underneath all fifteen:** *every screen is weighted the same.* Real products have a hierarchy of importance across screens — one thing dominates, the rest support. Fantrade gives the wallet balance, the club crest, the FanPlay projection and the settings list roughly equal visual authority. That evenness, more than any single pattern above, is what makes it feel generated.

---

## 20. WORLD-CLASS BENCHMARK

Measured against the quality bar of top-tier fintech, trading, sports and marketplace products — studying quality, not copying anyone.

| Dimension | Fantrade | Bar | Gap |
|---|---|---|---|
| **Visual craft** | 8/10 | 9/10 | Close. Genuinely distinctive |
| **Typography** | 8.5/10 | 9/10 | Nearly there. Needs a scale, not new fonts |
| **Clarity of proposition** | 4/10 | 9/10 | **Large.** A visitor cannot explain the product after reading the page |
| **Trust signals** | 3/10 | 9/10 | **Large.** No risk disclosure, no real auth, no fee schedule, fake SSO, contradictory numbers |
| **Information hierarchy** | 5/10 | 9/10 | **Large.** Everything weighted equally; numbers do not reconcile |
| **Interaction feedback** | 6/10 | 9/10 | Toasts good; no loading, pending, error or settlement states |
| **Motion quality** | 5/10 | 8/10 | Well-chosen curve, wrong durations, no number animation |
| **Responsiveness** | 8/10 | 9/10 | **Best dimension.** Zero overflow. Type and targets too small |
| **Accessibility** | 4/10 | 8/10 | Focus suppressed, contrast token fails, unlabelled fields, missing h1s |
| **Product depth** | 3/10 | 9/10 | **Largest gap.** The core mechanic is not implemented |
| **Product personality** | 7/10 | 9/10 | Strong visual identity, weak product voice. Football culture barely present in the app |
| **Domain authenticity** | 3/10 | 9/10 | A footballer's page has a tab called "Coin info". No fixtures, form, positions or photos anywhere |

**Where Fantrade already competes:** visual restraint, typographic discipline, responsive engineering, navigation architecture.

**Where it is not yet in the conversation:** product completeness, trust infrastructure, information hierarchy, and — most tellingly — **football**. A premium football product should be unmistakably about football on every screen. Today, remove the names and Fantrade is a well-designed crypto exchange.

---

## 21. UX FRICTION MAP

Scored: Severity (1–5) · User impact (1–5) · Frequency (1–5) · Fix difficulty (1–5, 5 = hardest)

### Top 10 UX problems

| # | Problem | Sev | Imp | Freq | Diff |
|---|---|---|---|---|---|
| 1 | FanPlay has no options layer — the core mechanic is absent | 5 | 5 | 5 | 5 |
| 2 | No loss preview, no negative FP path anywhere | 5 | 5 | 5 | 4 |
| 3 | Stakes are $FTR, model requires shares | 5 | 5 | 5 | 3 |
| 4 | Dream Club XI not derived from holdings — breaks the founding rule | 5 | 5 | 4 | 3 |
| 5 | `base = 100` — the projection is a constant | 5 | 5 | 5 | 3 |
| 6 | Net worth / club value / holdings do not reconcile | 4 | 5 | 5 | 2 |
| 7 | No settlement experience — rounds never resolve | 5 | 4 | 4 | 5 |
| 8 | FP never defined in-app | 4 | 5 | 5 | 1 |
| 9 | No FanPlay history — settled entries vanish | 4 | 4 | 3 | 3 |
| 10 | No confirmation step before committing a stake | 4 | 4 | 4 | 2 |

### Top 10 visual problems

| # | Problem | Sev | Imp | Freq | Diff |
|---|---|---|---|---|---|
| 1 | Every screen weighted equally — no dominance | 4 | 4 | 5 | 4 |
| 2 | `.ibox` used decoratively | 3 | 3 | 4 | 1 |
| 3 | ~22 type sizes, no scale | 4 | 3 | 5 | 3 |
| 4 | No spacing scale | 4 | 3 | 5 | 3 |
| 5 | Two icon rendering models | 3 | 2 | 5 | 2 |
| 6 | Five input patterns | 3 | 3 | 4 | 3 |
| 7 | Five tab systems | 3 | 2 | 4 | 3 |
| 8 | Gradient orbs on all 32 pages | 2 | 2 | 5 | 1 |
| 9 | 14 radii vs 2 tokens | 2 | 2 | 5 | 2 |
| 10 | No football imagery anywhere | 4 | 4 | 5 | 4 |

### Top 10 navigation problems

| # | Problem | Sev | Imp | Freq | Diff |
|---|---|---|---|---|---|
| 1 | Exchange and FanPlay are unconnected | 4 | 4 | 4 | 3 |
| 2 | No global search | 3 | 3 | 4 | 3 |
| 3 | No FanPlay history destination | 4 | 4 | 3 | 2 |
| 4 | Live board separate from your entry | 3 | 3 | 3 | 3 |
| 5 | Coaches have no destination of their own | 3 | 3 | 3 | 3 |
| 6 | Taskbar visible during onboarding | 3 | 3 | 1 | 1 |
| 7 | No public club pages despite leaderboards | 3 | 3 | 2 | 4 |
| 8 | No 404 | 2 | 2 | 1 | 1 |
| 9 | Full page loads — white flash | 3 | 3 | 5 | 5 |
| 10 | No skip link | 3 | 2 | 5 | 1 |

### Top 10 onboarding problems

| # | Problem | Sev | Imp | Freq | Diff |
|---|---|---|---|---|---|
| 1 | Every field pre-filled — nothing is decided | 4 | 4 | 5 | 2 |
| 2 | Never explains what a share is | 5 | 5 | 5 | 2 |
| 3 | 50,000 vs 128,450 $FTR contradiction | 4 | 4 | 5 | 1 |
| 4 | Wallet funded before "fund your wallet" | 4 | 3 | 5 | 2 |
| 5 | Never explains FP | 5 | 5 | 5 | 2 |
| 6 | Never shows FanPlay | 4 | 4 | 5 | 3 |
| 7 | User can escape the funnel via the taskbar | 3 | 3 | 3 | 1 |
| 8 | No email verification | 4 | 3 | 5 | 4 |
| 9 | No forgot-password | 4 | 3 | 2 | 3 |
| 10 | No first-session guidance after onboarding | 4 | 4 | 5 | 3 |

### Top 10 trust problems

| # | Problem | Sev | Imp | Freq | Diff |
|---|---|---|---|---|---|
| 1 | No password validation — any email signs in | 5 | 5 | 5 | 4 |
| 2 | Fake Passkey / Google / Wallet buttons | 5 | 4 | 3 | 1 |
| 3 | No risk or loss disclosure anywhere | 5 | 5 | 5 | 2 |
| 4 | Numbers contradict across screens | 4 | 5 | 5 | 2 |
| 5 | Club shows players the user does not own | 5 | 4 | 4 | 3 |
| 6 | 420 markets claimed, 12 exist | 4 | 4 | 5 | 2 |
| 7 | Security settings are entirely cosmetic | 4 | 3 | 2 | 4 |
| 8 | No fee schedule | 3 | 3 | 3 | 1 |
| 9 | No terms, privacy or responsible-play content behind the links | 4 | 3 | 2 | 2 |
| 10 | "Play to earn" framing invites the wrong comparison | 4 | 4 | 5 | 1 |

### Top 10 mobile problems

| # | Problem | Sev | Imp | Freq | Diff |
|---|---|---|---|---|---|
| 1 | Touch targets below 44px throughout | 4 | 4 | 5 | 2 |
| 2 | Type at 7.5–10px on phones | 4 | 4 | 5 | 3 |
| 3 | Tables hide columns with no way to reach them | 4 | 4 | 4 | 3 |
| 4 | Trade terminal density at 320px | 3 | 3 | 3 | 3 |
| 5 | Pitch labels at 7.5px | 4 | 3 | 3 | 2 |
| 6 | No landscape handling | 3 | 2 | 2 | 3 |
| 7 | No tablet layer — 1024px gets phone type | 3 | 3 | 3 | 3 |
| 8 | Fixed bars consume ~90px of a short viewport | 3 | 3 | 5 | 3 |
| 9 | White flash between pages | 3 | 3 | 5 | 5 |
| 10 | 140 KB re-parsed per navigation on mobile CPU | 4 | 4 | 5 | 3 |

### Top 10 "AI-generated" visual problems
See §19 — items 1–10 there are the ranked list. The highest-leverage removals are `.ibox` decoration (1), uniform card grids (2), and the gradient orbs (3).

---

## 22. USER JOURNEY AUDIT

**Journey 1 — Visitor → Landing → Sign up → Onboarding → Dashboard**
Works end to end. **Friction:** the visitor never learns what a share or $FTR is; signup promises 50,000 $FTR and delivers 128,450; onboarding pre-fills every decision; the dashboard arrives with no orientation. **The user completes the funnel without understanding the product.**

**Journey 2 — $FTR → Discover player → Buy shares → Portfolio**
The best-working journey in the app. Exchange → asset → trade → portfolio is coherent and the state updates correctly throughout. **Friction:** discovery is a flat list of 12; the asset page carries no football information to decide on; the portfolio does not confirm the purchase changed anything.

**Journey 3 — Player → Buy/Sell → Exchange → Portfolio**
Works. Limit orders rest, market orders fill, cancel works, holdings update. **Friction:** no order confirmation step; no position or average cost on the ticket; "Your fills" is scoped to one asset so there is no consolidated fill history.

**Journey 4 — Player → FanPlay → Market → Options → Shares → Preview → Activate**
**This journey does not exist.** You cannot choose a player (Individual mode is hardcoded to `$Bruno`). You cannot choose options (none exist). You cannot stake shares (stakes are $FTR). The preview is one-sided. There is no confirmation. **Four of seven steps are missing.**

**Journey 5 — Dream Club → Assets → Team FanPlay → Accumulated FP → Settlement**
Partially exists. Club selection and staking work. **Missing:** exposure is not distributed across assets, per-asset outcomes are not calculated, FP is not accumulated, and there is no settlement.

**Journey 6 — FanPlay → Positive FP → $FTR**
**Does not exist.** No settlement engine, no conversion, no payout. The only trace is a seeded transaction labelled "Matchday 06 Settle +6,200" in the ledger.

**Journey 7 — FanPlay → Negative FP → $FTR deduction**
**Does not exist in any form.** No negative FP, no deduction, no warning, no disclosure. **Given this is a real financial consequence in your model, this is the highest-risk gap in the product** — both for user trust and for whatever regulatory posture Fantrade eventually takes.

---

## 23. TOP 25 PRIORITY PROBLEMS

| # | Problem | Type | Severity |
|---|---|---|---|
| 1 | FanPlay has no options layer | Product | **Critical** |
| 2 | No negative FP / loss path anywhere | Product + Legal | **Critical** |
| 3 | Stakes denominated in $FTR, not shares | Product | **Critical** |
| 4 | `base = 100` — projection is a constant | Product | **Critical** |
| 5 | Dream Club XI not derived from holdings | Product | **Critical** |
| 6 | No settlement engine — rounds never resolve | Product | **Critical** |
| 7 | No real authentication | Technical + Trust | **Critical** |
| 8 | No product architecture (no framework/backend/API) | Technical | **Critical** |
| 9 | No risk or loss disclosure | Trust + Legal | **Critical** |
| 10 | Landing never defines $FTR, shares or FP | Product/UX | **High** |
| 11 | Net worth / club value / holdings do not reconcile | UX + Trust | **High** |
| 12 | Focus rings suppressed on every form field | Accessibility | **High** |
| 13 | `--faint` fails AA at the sizes it is used | Accessibility | **High** |
| 14 | No football data on football asset pages | Product | **High** |
| 15 | Touch targets below 44px throughout | Mobile | **High** |
| 16 | Type at 7.5–10px on phones | Mobile | **High** |
| 17 | No shared cacheable assets — 140 KB per navigation | Performance | **High** |
| 18 | Fake Passkey/Google/Wallet buttons | Trust | **High** |
| 19 | Numbers contradict (420/12, 50k/128k, 2140/12) | Trust | **High** |
| 20 | 12 unlabelled form controls | Accessibility | **Medium** |
| 21 | 5 pages with no `<h1>` | Accessibility | **Medium** |
| 22 | Motion too slow for a trading product (.5–.7s) | Motion | **Medium** |
| 23 | Coaches have no distinct information model | Product | **Medium** |
| 24 | 22 type sizes / no spacing scale / 14 radii | Design system | **Medium** |
| 25 | Terminology inconsistent (Fans Point vs FP vs Fantrade Points; club/syndicate/team) | Brand | **Medium** |

---

## 24. WHAT SHOULD BE PRESERVED

**Do not let Phase 2 touch these. They are the product's real assets.**

1. **The colour system.** Eleven disciplined tokens. OLED black + lime + amber is Fantrade's and nobody else's.
2. **The three type families.** Archivo / Montserrat / JetBrains Mono, and especially the tabular monospace for every figure. This is why the product reads as credible.
3. **The five-tab navigation architecture** with FanPlay centred, the `TAB_OF` mapping, and breadcrumbs on every drill-down.
4. **The double-bezel card** (`.bezel > .core`) and the `.flat` variant. Distinctive and well-built.
5. **The responsive engineering.** Zero overflow across 216 tested combinations. Whatever Phase 2 does, it must not regress this.
6. **`prefers-reduced-motion` support** in both CSS and JS.
7. **The `FT` state store's shape** — optimistic update, save, `syncUI`, dispatch `statechange`. The pattern is right even when the persistence layer changes.
8. **The trade ticket** — order book + ticket + ledger. Best screen in the app.
9. **The onboarding summary rail.** Best UX pattern in the product. Reuse it in FanPlay.
10. **The wallet page.** Card + assets, actions as destinations. Cleanest information hierarchy anywhere in the app.
11. **The pitch renderer's visual language** (not its data source).
12. **The football icon vocabulary** — boot, whistle, crest, pitch, formation, subs, armband, stadium. Under-used, but the most brand-specific asset in the system.
13. **The zero-image, all-vector approach** for UI chrome.
14. **The dependency-free QR implementation.**
15. **Empty states, toasts and modals** — one pattern each, well built.

---

## 25. WHAT SHOULD BE REDESIGNED

### Product-level (design the model first, then the screens)
1. **FanPlay, completely** — options schema, share staking, two-sided preview, confirmation, entry detail, settlement.
2. **Dream Club ownership** — derive the XI from holdings; validate every slot; compute club value and boost.
3. **The asset page** — rebuild around football, not candlesticks. Fixtures, form, position, minutes, FanPlay history.
4. **A coach information model** distinct from players.
5. **The economic model surface** — one place that states, in-app, what FP is, how it converts, and what a loss costs.

### UX-level
6. **Landing page narrative** — define $FTR, show a share, demonstrate FanPlay, disclose risk.
7. **Onboarding** — make decisions real; teach the model, not the form.
8. **Dashboard hierarchy** — one dominant thing, reconciled numbers.
9. **Exchange discovery** — positions, leagues, fixtures, watchlists; connect it to FanPlay.
10. **Settlement and history** — the loop must visibly close.

### UI-level (cheap, high return)
11. **Type scale** — ~8 sizes, documented, two scales reconciled.
12. **Spacing scale** — 4pt base, ~8 steps.
13. **Radius scale** — 4 values.
14. **One input component** replacing five.
15. **One tab component** replacing five.
16. **Icon system** — one geometry, one weight, UI set vs brand glyph set.
17. **Motion timing** — 120–180ms for feedback, 240–320ms for transitions; add number animation.
18. **Mobile type and target minimums** — 12px floor, 44px targets.
19. **Remove decorative `.ibox`, gradient orbs and uniform card grids.**
20. **Loading, pending, error and skeleton states** — currently absent.

---

## 26. WHAT SHOULD NOT BE TOUCHED

1. The `TAB_OF` route→tab mapping and the five-destination rule.
2. The colour tokens (except raising `--faint` for contrast).
3. The three font families.
4. The responsive breakpoint structure and overflow discipline.
5. `prefers-reduced-motion` handling.
6. The modal, toast and empty-state systems.
7. The QR implementation.
8. The `.bezel > .core` card construction.
9. The existing URL/filename scheme — until the framework decision is made, changing routes only creates churn.
10. The generator architecture itself — **until Phase 2 decides on a framework.** Rewriting the Python to produce slightly different HTML is wasted work if the target is React/Next.

---

## 27. RECOMMENDED REDESIGN ORDER

**Phase 2a — Decide (no code)**
1. Framework and backend decision. Everything else depends on it.
2. The FanPlay market/options model — as a written specification with worked examples, before any UI.
3. The economic rules — FP generation, FP→$FTR conversion, negative-FP debit, caps, limits.
4. Terminology lock — one word per concept, written down.
5. Reconcile every number in the demo data set.

**Phase 2b — Foundations**
6. Design tokens: type scale, spacing scale, radius scale, semantic colour aliases.
7. Icon system rebuild on one geometry.
8. Core component set: one input, one tab, one button family, one table, one chart shell.
9. Motion specification.
10. Accessibility baseline: focus, contrast, labels, headings, skip link.

**Phase 2c — Core product**
11. FanPlay Individual, end to end.
12. FanPlay Team, end to end.
13. Settlement — including the loss path.
14. Dream Club ownership enforcement.
15. Asset and coach pages rebuilt around football.

**Phase 2d — Surround**
16. Landing page narrative.
17. Onboarding.
18. Exchange discovery.
19. Dashboard hierarchy.
20. History, notifications, social.

---

## 28. PHASE 2 RECOMMENDATIONS

**1. Do not start with visual design.** The highest-severity problems in this document are product-model problems. A visual redesign layered on the current FanPlay would produce a more beautiful screen that still cannot answer "what can I lose?".

**2. Write the FanPlay specification before opening a design tool.** Markets, options, weights, settlement, conversion, downside — with worked numeric examples for at least Simple and Viynx Max. Everything else in Phase 2 follows from that document.

**3. Make the framework decision now.** Phase 2 will produce components. Producing them as Python-generated HTML strings and then porting them to a framework means paying twice.

**4. Fix the trust cluster early — it is cheap.** Real password validation, remove or implement the SSO buttons, reconcile the contradictory numbers, add risk disclosure. Days of work, and it changes how every subsequent screen is read.

**5. Fix the accessibility cluster early — it is cheaper still.** Remove five `outline:none` declarations, raise one colour token, add twelve labels, add five `<h1>`s, add a skip link. A day of work that removes four of the twenty-five priority problems.

**6. Put football back in the product.** This is the differentiator and it is nearly absent from the app. Fixtures, form, positions, photography, crests, minutes, next opponent. A page about a footballer with a tab called "Coin info" is the clearest sign Fantrade is currently wearing someone else's clothes.

**7. Protect what works.** The navigation, the type system, the colour discipline, the responsive engineering and the trade ticket are genuinely good. The risk in Phase 2 is not that it fails to improve things — it is that a redesign sweeps away the parts that are already right.

**8. Design for one dominant thing per screen.** The most effective single change against the "AI-generated" feel is not removing gradients — it is deciding what matters most on each screen and letting everything else recede.

---

*End of Phase 1 audit. No code was modified. No redesign was started.*
