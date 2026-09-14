# Generators

The fourteen HTML pages in the repository root are generated, not hand-edited.

- `common.py` — design tokens, CSS, icon sprite, the `FT` state store, nav (public / app / auth) and footer
- `experience.py` — simplified landing page, home dashboard, user guide, guided FanPlay entry, and final responsive styles; `prepare()` applies these screens before generation
- `icons_data.py` — Phosphor Light icon paths, compiled to a sprite
- `pages.py` — builds index, exchange, clubs, fanplay
- `pages2.py` — builds ftr, how-it-works
- `pages3.py` — builds signin, signup, onboarding, dashboard, portfolio, leaderboard, notifications, settings

```bash
cd tools && python3 pages.py && python3 pages2.py && python3 pages3.py
```

All three scripts write to the repository root. Edit the generators, not the HTML, or the next
build will overwrite your changes.

`check-experience.cjs` checks all pages at four viewport widths and exercises search, buying,
FanPlay confirmation and error states, persistence, club saving, and mobile navigation.
It uses Playwright with installed Edge. Set `PLAYWRIGHT_MODULE` if your Playwright package
is in a different location. Screenshots are written to `artifacts/` for visual review.
