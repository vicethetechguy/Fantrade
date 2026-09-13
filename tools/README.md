# Generators

The six HTML pages in the repository root are generated, not hand-edited.

- `common.py` — design tokens, CSS, icon sprite, nav and footer
- `icons_data.py` — Phosphor Light icon paths, compiled to a sprite
- `pages.py` — builds index, exchange, clubs, fanplay
- `pages2.py` — builds ftr, how-it-works

```bash
cd tools && python3 pages.py && python3 pages2.py
```

Both scripts write to the repository root. Edit the generators, not the HTML, or the next
build will overwrite your changes.
