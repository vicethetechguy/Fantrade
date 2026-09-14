# Fantrade

> Own the game. Build your club. Play to earn.

Front-end prototype for **Fantrade** — a football ownership economy where fans buy shares in players
and coaches, assemble them into a Dream Club, and enter that club into FanPlay each matchday.

This repository contains the marketing site and interactive product prototype. Every page is a
self-contained HTML file with no build step and no runtime dependencies beyond Google Fonts.

## Pages

| File | What it covers |
| --- | --- |
| `index.html` | Landing page — the three layers (Own / Build / Play), live exchange console, Dream Club preview, the Fantrade loop, house rules |
| `exchange.html` | Market table with player/coach filtering and search, working buy/sell ticket with live fee calculation, supply ring, movers, coach index |
| `clubs.html` | Zero FC dashboard with Line-ups / League position / Form tabs, live position ladder and form pills, club value chart, eight-step club builder with live formation switching (4-3-3 / 4-4-2 / 3-5-2 / 4-2-3-1), chemistry factors, club table |
| `fanplay.html` | Individual vs Dream Club entry, six market tiers, live scores board — date strip, featured match with ticking minute, fixtures grouped by competition with follow stars — settlement countdown, scoring rules |
| `ftr.html` | $FTR wallet — balance hero with range-switched chart, Send / Receive / Swap / Buy panes, scannable receive QR, asset list, activity, supply distribution |
| `how-it-works.html` | The six-step loop in full, settlement timeline, mode comparison, FAQ |
| `signin.html` | Split-screen sign in — validation, password reveal, passkey/social stubs, reset-link modal |
| `signup.html` | Account creation — password strength meter, region select, terms gate, hands off to onboarding |
| `onboarding.html` | Four-step setup wizard — manager profile, opening grant, first share purchase, club identity |
| `dashboard.html` | **Home** — net worth with range-switched chart, club summary, live lock countdown, matchday board, movers, activity, entries |
| `account.html` | Account hub — identity card, and the way in to the wallet, portfolio, club, league table, notifications and settings |
| `portfolio.html` | Portfolio & ledger — holdings table with filters and live P&L, allocation split, settlement ledger, yield, CSV export |
| `leaderboard.html` | Global standings — division filters, search and sort, club inspection, promotion matrix, syndicate index |
| `notifications.html` | Activity feed — day grouping, per-kind filters, unread state, per-channel toggles |
| `settings.html` | Profile, club identity, security and sessions, notification channels, payouts, responsible play, danger zone |

## Running it

No tooling required. Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Navigation

Three shells.

**App pages** get two floating bars and nothing else — no hamburger, no slide-out menu, no page links
up top. A slim top bar carries the logo, the $FTR balance chip (which opens the wallet) and the
notification bell. A floating taskbar at the bottom carries the only five destinations:

    Home · Exchange · FanPlay · Leaderboard · Account

FanPlay sits in the middle on a lime disc. Every other page lights up one of those five — Dream Clubs
and onboarding light Home; the wallet, portfolio, notifications and settings light Account. That
mapping is `TAB_OF` in `common.py`, and `nav()` takes the page's filename so a page can never
mislabel its own tab.

**Marketing pages** (`index`, `how-it-works`) keep the public nav with Sign in and Get started.
**Auth pages** use a stripped shell: logo, one way back, no footer.

## State

Everything is driven by `FT`, a small localStorage-backed store in `common.py` (`JS_SHELL`). It holds the
session (`auth`), manager and club, wallet, holdings, FanPlay entries, transactions, notifications and
preferences, and emits `fantrade:statechange` so open pages re-render. Signing up, onboarding, buying a
share, staking a round, claiming yield, saving settings and marking activity read all write to it, so the
prototype stays consistent as you move between pages. Settings → Danger zone resets it.

## Design system

- **Display type** — Archivo at `wdth 125`, weights 800–900, uppercase
- **Body type** — Montserrat 300–600
- **Numerals** — JetBrains Mono, tabular figures (prices, share counts, FP totals only)
- **Surface** — OLED black `#050505`, fixed mesh orbs, 4% film grain, hairlines at `rgba(255,255,255,.08)`
- **Accents** — lime `#C4F82A` (players, actions), amber `#FF6A1F` (coaches, high-risk tiers), red `#FF3B47` reserved for live match states only
- **Structure** — double-bezel containers (outer shell `p-8` at `2rem` radius, inner core at `calc(2rem - .5rem)`)
- **Wallet components** — shared across wallet, dashboard and portfolio: balance hero (`.bal-big` / `.bal-delta` / `.bal-chart`), range pills (`.range`), four-up action tiles (`.acts4`), asset rows with circular marks and sparklines (`.arow` / `.coin`), receive panel (`.netsel` / `.qr` / `.addr`), amber warning strips (`.warn`)
- **Shell** — floating top bar (`.topbar`) and floating taskbar (`.taskbar`); the taskbar reserves footer space through `.taskbar ~ footer` so nothing is covered
- **Matchday components** — shared across FanPlay and Dream Clubs: date strip (`.dates` / `.livetgl`), featured match card (`.feat` / `.minute` / `.tcrest`), competition groups and fixture rows (`.comp` / `.fixt` / `.star`), tab strip (`.tabstrip`), form pills (`.form5`), live position ladder (`.gauge` / `.ladder` / `.rung`)
- **Motion** — `cubic-bezier(.32,.72,0,1)` throughout; scroll entry via `IntersectionObserver`; `prefers-reduced-motion` respected
- **Layout** — asymmetrical bento grids, collapsing to single column below 768px

Source generators for the pages live in `tools/` — they emit the HTML from a shared design system so the
fourteen pages can't drift apart.

## The receive QR

`tools/qr_data.py` holds a pre-computed QR matrix (error-correction level H) for the demo receive address, so
the generators never need a QR library installed. `common.qr_svg()` renders it as a single SVG path with
merged horizontal runs. It is a real, scannable code — the Fantrade mark punched through the middle sits well
inside level H's recovery budget. Regenerate it with `segno.make(ADDRESS, error="h").matrix` if the address
changes.

## Icons

[Phosphor Icons](https://github.com/phosphor-icons/core) (Light weight), MIT licensed, compiled into an
inline SVG sprite per page. No CDN dependency at runtime.

## Status

Prototype. All figures, prices, fixtures and balances shown are illustrative. Nothing here is connected
to a backend, a data provider, or a payment rail.
