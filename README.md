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
| `clubs.html` | Zero FC dashboard, club value chart, eight-step club builder with live formation switching (4-3-3 / 4-4-2 / 3-5-2 / 4-2-3-1), chemistry factors, club table |
| `fanplay.html` | Individual vs Dream Club entry, six market tiers, live matchday board, settlement countdown, scoring rules |
| `ftr.html` | $FTR wallet — balance, GBP conversion with fees, supply distribution, full ledger |
| `how-it-works.html` | The six-step loop in full, settlement timeline, mode comparison, FAQ |

## Running it

No tooling required. Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Design system

- **Display type** — Archivo at `wdth 125`, weights 800–900, uppercase
- **Body type** — Montserrat 300–600
- **Numerals** — JetBrains Mono, tabular figures (prices, share counts, FP totals only)
- **Surface** — OLED black `#050505`, fixed mesh orbs, 4% film grain, hairlines at `rgba(255,255,255,.08)`
- **Accents** — lime `#C4F82A` (players, actions), amber `#FF6A1F` (coaches, high-risk tiers)
- **Structure** — double-bezel containers (outer shell `p-8` at `2rem` radius, inner core at `calc(2rem - .5rem)`)
- **Motion** — `cubic-bezier(.32,.72,0,1)` throughout; scroll entry via `IntersectionObserver`; `prefers-reduced-motion` respected
- **Layout** — asymmetrical bento grids, collapsing to single column below 768px

Source generators for the pages live in `tools/` — they emit the HTML from a shared design system so the
six pages can't drift apart.

## Icons

[Phosphor Icons](https://github.com/phosphor-icons/core) (Light weight), MIT licensed, compiled into an
inline SVG sprite per page. No CDN dependency at runtime.

## Status

Prototype. All figures, prices, fixtures and balances shown are illustrative. Nothing here is connected
to a backend, a data provider, or a payment rail.
