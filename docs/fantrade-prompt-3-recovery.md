# Prompt 3 Recovery Report

## Previous Agent
Claude Opus 5.5

## Current Agent
Antigravity / Gemini 3.8 Flash High

## Prompt
Phase 2 — Prompt 3 — Market & Exchange Engine

---

## Executive Summary
This audit was conducted immediately following an unexpected session termination during Claude Opus 5.5's implementation of **Phase 2 / Prompt 3: Market & Exchange Engine**. 

**Primary Finding:**
The repository contains **zero persisted application code, database models, migrations, or backend architecture** from Phase 2 / Prompt 3. The codebase is currently frozen at the exact state of the **Phase 1 static prototype** (last committed at `dec64a7` on Tue Sep 15 15:38:02 2026), alongside an untracked Phase 1 audit document (`Claude outputs/AUDIT-PHASE-1.md` written at 7:01 PM on Sep 15, 2026).

All exchange features currently visible in the UI (order book ladder, limit order ticket, buy/sell executions, swap engine, and portfolio balances) are **client-side simulations and mathematical mockups** operating on a single `localStorage` JSON blob (`fantrade_v1_state`) and procedural JavaScript math (`Math.sin` order books, static asset arrays, in-memory arrays).

---

## Repository State

### Framework & Stack
- **Framework:** None. Pure static HTML5, vanilla JavaScript, and hand-crafted CSS.
- **Package Manager:** None. No `package.json`, `node_modules`, `pnpm-lock.yaml`, `Pipfile`, or `requirements.txt`.
- **Build System:** Python 3 string templating scripts in `tools/` (`pages.py`, `pages2.py`, `pages3.py`, `pages4.py`, `pages5.py`, `common.py`, `icons_data.py`, `qr_data.py`, `experience.py`). Running these scripts outputs 32 static `.html` files directly into the repository root.
- **Routing:** Static filesystem routing via native `<a>` hyperlinks and URL query parameters (e.g. `asset.html?a=$Saka`, `trade.html?a=$Saka`, `trade.html?side=sell`). Full page reloads occur on navigation.
- **Styling:** Inlined CSS custom properties within a `~2,500`-line `<style>` tag per page. A scoped trading density stylesheet (`DENSE_CSS` targeting `body.app`) governs in-app pages.
- **State Management:** Browser `localStorage['fantrade_v1_state']`. Controlled by a global IIFE exposing `window.FT` with helper methods (`getState()`, `save()`, `executeTrade()`, `swapAssets()`, etc.), broadcasting updates via `window.dispatchEvent(new CustomEvent('fantrade:statechange'))`.
- **Authentication:** Simulated client-side. `FT.signIn()` accepts any email address without validating passwords or contacting any authentication authority.
- **Backend / API / Server:** None. Zero server processes, zero API routes (`/api/*`), and zero backend middleware.
- **Assets:** 12 hardcoded instruments defined in an in-memory JS array in `tools/common.py` (10 footballers, 2 managers).

---

## Git State

### Status & Working Tree
- **Active Branch:** `main` (tracked to `origin/main`, up to date).
- **Working Tree Cleanliness:** Clean, with exactly **one untracked file**:
  `Claude outputs/AUDIT-PHASE-1.md` (68,650 bytes, created/modified Sep 15 2026 19:01:16).
- **Uncommitted Code Changes:** None (`git diff` and `git diff --cached` are empty).
- **Stashes:** None (`git stash list` is empty).
- **Dangling Objects:** Exactly one dangling tree (`396f1ae04168a8482618a93fb3fe2d637bb88dde`), representing a prior build iteration; no dangling commit objects.

### Recent Commit Log
| Hash | Date | Author | Message |
|---|---|---|---|
| `dec64a7` | 2026-09-15 15:38:02 +0100 | vicethetechguy | Match landing header height to in-app, Fans Point rename, spot-style trade terminal |
| `9938741` | 2026-09-15 15:12:58 +0100 | vicethetechguy | Rename Fantrade Points to Fans Point |
| `a76fbe5` | 2026-09-15 14:08:47 +0100 | vicethetechguy | Multi-club support, FanPlay redesign, Team index, split settings pages |
| `37c2ed8` | 2026-09-15 10:58:53 +0100 | vicethetechguy | feat: add interactive staking, matchday alerts, and live scores board enhancements |
| `f330972` | 2026-09-15 10:04:12 +0100 | vicethetechguy | feat: add liveboard and granular settings drilldown pages, update navigation and generator tools |

All git commits represent Phase 1 UI iterations. There are no commits for Phase 2.

---

## Database State

- **Database Engine:** None (no PostgreSQL, MySQL, SQLite, MongoDB, or Redis).
- **ORM / Query Builder:** None (no Prisma, Drizzle, Sequelize, TypeORM, SQLAlchemy, Alembic).
- **Schema Files:** None.
- **Migration Files:** None.
- **Migration Status:** Non-existent (0 migrations applied, 0 pending).

### Model Inventory
| Expected Prompt 3 Model | Exists in DB? | Migration Exists? | Service/Repo Exists? | API Exists? | Current Reality |
|---|---|---|---|---|---|
| `markets` | NO | NO | NO | NO | Static array `ASSETS` in `tools/common.py` |
| `orders` | NO | NO | NO | NO | In-memory volatile JS array `OPEN = []` in `trade.html` |
| `order_book` | NO | NO | NO | NO | Procedural client sine function `book2()` |
| `order_items` | NO | NO | NO | NO | None |
| `trades` | NO | NO | NO | NO | `state.transactions` unindexed log in `localStorage` |
| `reservations` | NO | NO | NO | NO | None |
| `share_reservations` | NO | NO | NO | NO | None |
| `ftr_reservations` | NO | NO | NO | NO | `state.wallet.locked` (only used by FanPlay) |
| `fees` | NO | NO | NO | NO | Hardcoded `0.004` (0.4%) multiplier in JS |
| `swaps` | NO | NO | NO | NO | Client-side math in `FT.swapAssets()` |
| `price_history` | NO | NO | NO | NO | Procedural SVG generator (`drawCandles()`) |
| `market_statistics` | NO | NO | NO | NO | Derived mock formulas (`sHigh = px * 1.05`, etc.) |
| `inventory` | NO | NO | NO | NO | None |

---

## Prompt 3 Feature Classification (35 Items)

Statuses used: **COMPLETE**, **PARTIAL**, **MOCKED**, **SIMULATED**, **MISSING**, **BLOCKED**, **UNKNOWN**.

| # | Feature | Status | UI Status | Frontend State | Real Server / DB Logic | Evidence & Code Reference |
|---|---|---|---|---|---|---|
| 1 | Market domain | **SIMULATED** | COMPLETE | MOCK DATA | MISSING | `exchange.html` and `asset.html` render 12 assets from `tools/common.py` (`ASSETS`). No dynamic market lifecycle or DB entities. |
| 2 | Primary market | **MISSING** | MISSING | MISSING | MISSING | No issuance interface, IPO pricing, or primary distribution logic exists in the repository. |
| 3 | Secondary market | **SIMULATED** | COMPLETE | LOCAL STORAGE | MISSING | Peer-to-peer trading does not exist. Users trade instantly against a static price in client state without counterparties. |
| 4 | Supply states | **MOCKED** | COMPLETE | MOCK DATA | MISSING | Displayed as static metrics on `asset.html` ("Coin info" tab). Circulating vs locked vs authorized supply is not modeled. |
| 5 | Reference price | **MOCKED** | COMPLETE | MOCK DATA | MISSING | Displayed statically on `asset.html` (`A.p`). No reference/oracle pricing calculations exist. |
| 6 | Current price | **SIMULATED** | COMPLETE | LOCAL STORAGE | MISSING | Static price in `ASSETS[i].p`. Ticks decoratively via `setInterval` in UI; not driven by order-book matching. |
| 7 | Best bid | **MOCKED** | COMPLETE | MOCK DATA | MISSING | `#tBids` generated dynamically in `book2()` via `px - step`. |
| 8 | Best ask | **MOCKED** | COMPLETE | MOCK DATA | MISSING | `#tAsks` generated dynamically in `book2()` via `px + step`. |
| 9 | Mid price | **MISSING** | MISSING | MISSING | MISSING | No mid-price calculation or indicator exists on the terminal or in state. |
| 10 | Last trade | **SIMULATED** | COMPLETE | LOCAL STORAGE | MISSING | Displayed as `#tLast` in `trade.html`. Updates only when local user executes a market trade. |
| 11 | Real order book | **MOCKED** | COMPLETE | MOCK DATA | MISSING | Visual ladder is generated via `Math.sin((i+1)*2.7) * 41000` in `tools/pages4.py:58`. Zero database persistence or real orders. |
| 12 | LIMIT orders | **SIMULATED** | COMPLETE | VOLATILE JS | MISSING | Ticket accepts limit orders, but `tools/pages4.py:652` unshifts them into volatile array `OPEN = []`. Lost on page refresh. |
| 13 | Buy | **SIMULATED** | COMPLETE | LOCAL STORAGE | MISSING | `FT.executeTrade('buy')` in `tools/common.py:2120` debits `state.wallet.balance`, updates `state.holdings`, but has no backend verification. |
| 14 | Sell | **SIMULATED** | COMPLETE | LOCAL STORAGE | MISSING | `FT.executeTrade('sell')` in `tools/common.py:2134` decrements `state.holdings`, credits wallet balance; client-only. |
| 15 | Share reservations | **MISSING** | MISSING | MISSING | MISSING | Placing an order or entering FanPlay does not lock or reserve shares. Shares can be double-sold. |
| 16 | FTR reservations | **MISSING** | PARTIAL | LOCAL STORAGE | MISSING | `state.wallet.locked` exists for FanPlay stakes, but placing an exchange limit buy reserves 0 FTR. |
| 17 | Transactional trade execution | **MISSING** | COMPLETE | LOCAL STORAGE | MISSING | No ACID transactions, two-phase commits, or mutexes. Pure synchronous JS mutations. |
| 18 | Partial fills | **MISSING** | MISSING | MISSING | MISSING | Market orders fill 100% instantly; limit orders never fill. No partial fill logic exists. |
| 19 | Order lifecycle | **MISSING** | PARTIAL | VOLATILE JS | MISSING | No order status state machine (`PENDING`, `OPEN`, `FILLED`, `CANCELLED`, `EXPIRED`). |
| 20 | Cancellation | **SIMULATED** | COMPLETE | VOLATILE JS | MISSING | "Cancel" button in `#tLedger` calls `OPEN.splice(i, 1)`. Since no funds/shares were locked, no release occurs. |
| 21 | Expiration | **MISSING** | MISSING | MISSING | MISSING | No Time-In-Force (GTC, IOC, FOK, Day) mechanics or expiration routines. |
| 22 | Primary inventory | **MISSING** | MISSING | MISSING | MISSING | No corporate treasury or primary inventory account exists. |
| 23 | Secondary ownership transfer | **MISSING** | PARTIAL | LOCAL STORAGE | MISSING | Ownership is created from void upon Buy and destroyed upon Sell. No counterparty balance transfer occurs. |
| 24 | Swap engine | **SIMULATED** | COMPLETE | LOCAL STORAGE | MISSING | `FT.swapAssets()` in `tools/common.py:2304` converts from-asset to to-asset via price ratio with 0.4% fee in `localStorage`. |
| 25 | Centralized fees | **MOCKED** | COMPLETE | HARDCODED JS | MISSING | Fixed 0.4% (`subtotal * 0.004`) in `FT.executeTrade` and `FT.swapAssets`. Fees are destroyed rather than routed to a treasury. |
| 26 | FTR ledger integration | **BLOCKED** | PARTIAL | LOCAL STORAGE | MISSING | Blocked by lack of centralized ledger service. `state.transactions` is an unverified local array. |
| 27 | Price statistics | **MOCKED** | COMPLETE | MOCK DATA | MISSING | 24h high/low and volume in `asset.html` are calculated from static multipliers on the current price. |
| 28 | Price history | **MOCKED** | COMPLETE | MOCK DATA | MISSING | Candlestick and area charts rendered via SVG (`drawCandles`) using procedural noise. No time-series DB. |
| 29 | Asset/Exchange integration | **PARTIAL** | COMPLETE | LOCAL STORAGE | MISSING | Navigation flows seamlessly between `exchange.html`, `asset.html`, and `trade.html` via query params and shared state. |
| 30 | Mobile Exchange UI | **COMPLETE** | COMPLETE | LOCAL STORAGE | N/A | Highly polished responsive layout (320px–1440px), dense trading mode (`body.app`), touch steppers, zero overflow. |
| 31 | Security | **MISSING** | N/A | NONE | MISSING | No authentication checks, token signing, or input validation. Client can alter state arbitrarily in browser console. |
| 32 | Race-condition protection | **MISSING** | N/A | NONE | MISSING | Concurrent browser tabs can clobber `localStorage` state without concurrency controls. |
| 33 | Idempotency | **MISSING** | N/A | NONE | MISSING | No idempotency keys on trades or orders; rapid submissions trigger duplicate executions. |
| 34 | Self-trade prevention | **MISSING** | N/A | NONE | MISSING | No counterparty matching logic exists to detect or reject self-trades. |
| 35 | Admin market controls | **MISSING** | MISSING | MISSING | MISSING | No administrative interface or logic for market pauses, circuit breakers, or asset listing. |

---

## Order Book Deep Dive

The order book UI on `trade.html` and `asset.html` creates the visual appearance of a high-frequency spot exchange. However, static analysis of `tools/pages4.py` (lines 50–74) reveals that the order book is **completely synthetic**:

```javascript
var TICK = 1;
function book2(box, side, count, onPick){
  var rows = [], px = A.p, total = 0;
  for(var i = 0; i < count; i++){
    var step = (i + 1) * (px * 0.0016) * TICK;
    var p = side === 'bid' ? px - step : px + step;
    var size = Math.round(3100 + Math.abs(Math.sin((i + 1) * 2.7)) * 41000);
    total += size;
    rows.push({ p: p, s: size, t: total });
  }
  var max = rows[rows.length - 1].t;
  if(side === 'ask') rows.reverse();
  var host = document.getElementById(box);
  host.innerHTML = rows.map(function(r){
    return '<div class="b2row ' + side + '" data-px="' + r.p.toFixed(2) + '">'
      + '<i style="width:' + (r.t / max * 100).toFixed(0) + '%"></i>'
      + '<span>' + r.p.toFixed(2) + '</span><span>' + fmt(r.s) + '</span></div>';
  }).join('');
...
```

### Key Order Book Realities:
1. **Depth is derived from a Sine Wave:** The depth ladder sizes are computed purely by `Math.sin((i + 1) * 2.7) * 41000`.
2. **Order Submission is Volatile:** When a user places a Limit Order via the UI ticket, the order is appended to an in-memory array (`OPEN.unshift(...)`, `tools/pages4.py:652`). It is never persisted to `localStorage` or any database, and disappears when the user navigates away or refreshes the page.
3. **No Matching Engine:** No matching algorithm (e.g., price-time priority / FIFO) exists. Limit bids and asks on the screen never interact with incoming market or limit orders.
4. **No Asset or Balance Escrow:** Submitting a limit buy order does not deduct or escrow FTR. Submitting a limit sell order does not deduct or escrow shares.

---

## Ownership Engine Integration Audit

Prompt 2 intended to establish the Asset + Ownership Engine. In the existing repository:
- **Client-Side Ownership State:** Tracked inside `state.holdings` in `localStorage`.
- **Holding Structure:** `{ n: assetName, shares: count, avg: price, p: price, c: isCoach, inClub: 'SUB' }`.
- **Integrity Gaps:**
  - **No Reservation System:** Shares held in `state.holdings` can be traded on `trade.html` even while entered into an active round on `fanplay.html`.
  - **Dream Club Decoupling:** In `clubs.html`, the starting XI on the pitch is rendered from a hardcoded table (`FORMS` in `tools/common.py`), completely bypassing `state.holdings`. A user holding 4 assets is shown fielding 11 players.
  - **Single-User Void:** All buy orders create new shares out of thin air; all sell orders delete shares into thin air. There is no global registry of authorized, issued, or circulating shares across users.

---

## FTR Ledger Integration Audit

- **Ledger Architecture:** MISSING / BLOCKED.
- **Current Transaction Tracking:** Every transaction (trade, swap, deposit) merely unshifts an object onto an unindexed array: `state.transactions.unshift({ type, asset, shares, price, total, time })`.
- **Deficiencies:**
  - No double-entry bookkeeping (no debits and credits balancing to zero).
  - No immutable transaction IDs or cryptographic hashes.
  - No settlement account, fee treasury, or liquidity reserve accounts.
  - Vulnerable to arbitrary tampering in local storage.

---

## Fee Logic Audit

- **Current Fee:** Hardcoded at **0.4%** across all trades and swaps.
  - `tools/common.py:2117`: `var fee = subtotal * 0.004;`
  - `tools/common.py:2309`: `var fee = gross * 0.004;`
  - `tools/pages4.py:486, 507`: Hardcoded labels `Fee (0.4%)`.
- **Configuration:** Not configurable. Hardcoded directly into client JavaScript.
- **Economic Destination:** Fees are merely deducted from the trade proceeds or added to the buy cost and then discarded. They are not credited to an admin wallet, platform treasury, or staking reward pool.

---

## Security & Vulnerability Findings

1. **Complete Client-Side Trust:** All business logic (pricing, balance calculation, share quantities, fees) executes client-side without server validation.
2. **Zero Authentication Enforcement:** `FT.signIn` allows instant access with arbitrary email strings and arbitrary passwords.
3. **Double-Spend & Over-Selling:** Because limit orders do not lock funds or shares, a user can place multiple limit sells exceeding their total holdings or sell shares currently locked in FanPlay.
4. **Cross-Tab Race Conditions:** Multiple tabs operating on `localStorage` without Mutex or storage-event synchronisation will overwrite and destroy wallet balances and trade history.
5. **No Idempotency:** Double-clicking the "Buy" or "Swap" buttons triggers multiple rapid executions.

---

## Build and Test Audit

- **Syntax Compilation:** Passed. All 9 Python scripts compile cleanly with zero errors (`python -m py_compile tools/*.py`).
- **Playwright Test Suite (`tools/check-experience.cjs`):** Present. Inspects responsive viewport overflow and basic DOM flows.
- **Application Test Suite:** No unit tests, integration tests, or end-to-end tests exist for the Exchange Engine or Market Domain.
- **Production Build:** No bundler (Vite, Webpack) is used. Direct Python script execution generates the static site.

---

## Likely Claude Stopping Point

### Evidence:
1. Git history terminates at commit `dec64a7` (Sep 15, 2026, 15:38:02).
2. The only untracked file in the workspace is `Claude outputs/AUDIT-PHASE-1.md`, modified at 19:01:16 on Sep 15, 2026.
3. `AUDIT-PHASE-1.md` concludes with:
   > *"End of Phase 1 audit. No code was modified. No redesign was started."*
4. There are no modified files, unstaged changes, temporary files, or new directories in `Fantrade New` created after 19:01:16 on Sep 15.

### Conclusion:
**Exact stopping point cannot be proven** regarding what Claude Opus 5.5 was typing in the web chat window when session credits expired.

**However, regarding the codebase itself:**
**Claude stopped before persisting or applying ANY code for Phase 2 / Prompt 3.**
Claude did not begin modifying files on disk for Prompt 3, did not create any backend files, did not create any database migrations, and did not alter the existing Phase 1 Python generators.

---

## Safe Continuation Point

The safest continuation point is **at the very beginning of Phase 2**:

1. **Do not attempt to layer real matching onto the static Python generators:** The existing Python scripts generate static HTML files with inline client JavaScript. Attempting to build an ACID order-matching engine or double-entry ledger inside this static generator setup is impossible.
2. **Establish the Backend & Database Foundation First:**
   Before implementing Prompt 3 (Exchange Engine), the platform requires:
   - Backend runtime (Node.js/TypeScript or Python/FastAPI).
   - Relational Database (PostgreSQL) with connection pooling.
   - Core Schema: Users, Wallets, Ledger Accounts, Assets, Holdings, Market Pairs, Orders, Trades, Reservations.
3. **Implement Prompt 1 & Prompt 2 Domain Models in the Database:**
   - Asset Engine: Persisted Asset schema (tickers, supply, role, status).
   - Ownership Engine: Persisted User Holdings and Share Reservation schema.
4. **Implement Prompt 3 (Market & Exchange Engine):**
   - Centralized Order Book with Price-Time Priority.
   - Transactional trade execution with balance and share escrow.
   - Double-entry ledger integration for FTR and platform fees.

---

## Files Modified by Claude (Phase 1 Baseline)
These files represent Claude's Phase 1 work leading up to the audit:
- `tools/common.py`
- `tools/pages.py`
- `tools/pages2.py`
- `tools/pages3.py`
- `tools/pages4.py`
- `tools/pages5.py`
- `tools/icons_data.py`
- `tools/experience.py`
- `trade.html`
- `asset.html`
- `exchange.html`
- `dashboard.html`
- `clubs.html`
- `fanplay.html`
- `ftr.html`
- `how-it-works.html`
- `index.html`
- `Claude outputs/AUDIT-PHASE-1.md`

---

## DO NOT CHANGE (Systems to Preserve)
When Phase 2 implementation begins, the following high-value design and UX assets should be strictly preserved:
1. **Design System & Typography:** Archivo (display), Montserrat (body), and JetBrains Mono (tabular numerals).
2. **Color Palette:** OLED black `#050505`, Lime `#C4F82A`, Amber `#FF6A1F`, and Red `#FF3B47`.
3. **Dense Trading Theme (`DENSE_CSS`):** The compact typography scale and spacing on `body.app`.
4. **Mobile Navigation Shell:** Floating top bar and 5-destination taskbar (`Home`, `Exchange`, `FanPlay`, `Leaderboard`, `Account`).
5. **Responsive Engineering:** The zero-overflow layout discipline across 320px, 390px, 768px, and 1440px viewports.
6. **Trade Terminal Visual Layout:** The spot-style two-column layout on `trade.html` (order book ladder side-by-side with order ticket, ledger below).

---

## Recommended Next Action
**DO NOT continue modifying static Python generators for Exchange logic.**

The immediate next step for Phase 2 continuation is:
1. Approve a backend architectural stack (e.g. Node.js / TypeScript / NestJS or Express, with PostgreSQL and Prisma/Drizzle).
2. Initialize the backend project structure and configure database connectivity.
3. Author and apply initial database migrations establishing the **Asset Engine**, **Ownership Engine**, and **FTR Ledger** schemas, which are hard prerequisites for the **Exchange & Market Engine**.
