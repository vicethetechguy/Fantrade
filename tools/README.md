# Generators

The fifteen HTML pages in the repository root are generated, not hand-edited.

- `common.py` — design tokens, CSS, icon sprite, the `FT` state store, the shell (top bar, five-item taskbar, `TAB_OF` mapping, marketing and auth navs) and footer
- `icons_data.py` — Phosphor Light icon paths, compiled to a sprite
- `qr_data.py` — pre-computed QR matrix for the wallet receive address (keeps the build dependency-free)
- `pages.py` — builds index, exchange, clubs, fanplay
- `pages2.py` — builds ftr, how-it-works
- `pages3.py` — builds signin, signup, onboarding, dashboard (Home), portfolio, leaderboard, notifications, settings, account

```bash
cd tools && python3 pages.py && python3 pages2.py && python3 pages3.py
```

All three scripts write to the repository root. Edit the generators, not the HTML, or the next
build will overwrite your changes.
