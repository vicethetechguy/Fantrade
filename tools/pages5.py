# -*- coding: utf-8 -*-
"""Build the wallet action pages from the shared onboarding-style workflows."""
from pathlib import Path
from common import head, atmosphere, nav, JS_SHELL
from app_design import apply_design
from wallet_pages import PAGES, COMMON_JS

OUT = Path(__file__).resolve().parent.parent
for name, body, script in PAGES:
    filename = name + '.html'
    html = (head(name.title() + ' — Fantrade', '', 'app') + atmosphere()
            + nav(filename, True) + body
            + '<script src="public/fantrade-api.js"></script><script>(function(){'
            + JS_SHELL + COMMON_JS + script + '})();</script></body></html>')
    (OUT / filename).write_text(apply_design(filename, html), encoding='utf-8')
    print('built ' + filename)
