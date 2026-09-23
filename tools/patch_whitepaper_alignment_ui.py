# -*- coding: utf-8 -*-
"""
Complete alignment script for White Paper Draft v2.0:
- F-ticker system across Exchange, Dashboard, Portfolio, Trade, Asset, Swap, FanPlay
- Admin Listings & Claiming with 5% (500k) / 10% (1M) levels, 1-3 year vesting, 1% daily limit, 30% fee share, 2% burn
- Portfolio Lister Vesting & 1% daily limit dashboard
"""
import re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def patch_exchange():
    path = os.path.join(ROOT, "tools", "pages.py")
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # In exchange search: include ftSym(a.t)
    c = c.replace(
        "if(q && (a.t + ' ' + a.n).toLowerCase().indexOf(q) < 0) return false;",
        "if(q && (a.t + ' ' + ftSym(a.t) + ' ' + a.n).toLowerCase().indexOf(q) < 0) return false;"
    )

    # In exchange map: use ftSym(a.t) instead of a.t.replace('$', '')
    c = c.replace(
        "var sym = a.t.replace('$', '');",
        "var sym = ftSym(a.t);"
    )

    # In fanplay player card: use ftSym
    c = c.replace(
        "+ '<div class=\"fp-asset-sym\">' + a.symbol + '</div>'",
        "+ '<div class=\"fp-asset-sym\">' + ftSym(a.symbol) + '</div>'"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("pages.py (Exchange) patched successfully")

def patch_asset_and_trade():
    # 1. tools/pages4.py
    p4 = os.path.join(ROOT, "tools", "pages4.py")
    with open(p4, "r", encoding="utf-8") as f:
        c = f.read()

    c = c.replace(
        "var A = ASSETS.filter(function(x){ return x.t.toLowerCase() === SYM.toLowerCase(); })[0] || ASSETS[0];",
        "var A = ASSETS.filter(function(x){ return x.t.toLowerCase() === SYM.toLowerCase() || ftSym(x.t).toLowerCase() === SYM.toLowerCase(); })[0] || ASSETS[0];"
    )
    c = c.replace(
        "<span id=\"tSym\">$Saka</span>",
        "<span id=\"tSym\">FSAKA</span>"
    )
    c = c.replace(
        "if(el('tSym')) el('tSym').textContent = A.t;",
        "if(el('tSym')) el('tSym').textContent = ftSym(A.t);"
    )
    c = c.replace(
        "if(el('tQtyUnit')) el('tQtyUnit').textContent = A.t;",
        "if(el('tQtyUnit')) el('tQtyUnit').textContent = ftSym(A.t);"
    )
    c = c.replace(
        "document.title = 'Trade ' + A.t + ' — Fantrade';",
        "document.title = 'Trade ' + ftSym(A.t) + ' Activity Shares — Fantrade';"
    )

    with open(p4, "w", encoding="utf-8") as f:
        f.write(c)
    print("pages4.py (Trade) patched successfully")

    # 2. tools/asset_page.py
    ap = os.path.join(ROOT, "tools", "asset_page.py")
    with open(ap, "r", encoding="utf-8") as f:
        c = f.read()

    c = c.replace(
        "var asset = ASSETS.find(function(a){ return a.t.toLowerCase() === requested.toLowerCase(); });",
        "var asset = ASSETS.find(function(a){ return a.t.toLowerCase() === requested.toLowerCase() || ftSym(a.t).toLowerCase() === requested.toLowerCase(); });"
    )
    c = c.replace(
        "byId('assetSubtitle').textContent=asset.t + ' · ' + asset.club;",
        "byId('assetSubtitle').textContent=ftSym(asset.t) + ' · ' + asset.club;"
    )
    c = c.replace(
        "byId('assetSymbol').textContent=asset.t;",
        "byId('assetSymbol').textContent=ftSym(asset.t);"
    )
    c = c.replace(
        "+ playerPhoto(a.t,a.n) + '<span><b>' + escapeText(a.n) + '</b><small>' + escapeText(a.t + ' · ' + a.club) + '</small></span>'",
        "+ playerPhoto(a.t,a.n) + '<span><b>' + escapeText(a.n) + '</b><small>' + escapeText(ftSym(a.t) + ' · ' + a.club) + '</small></span>'"
    )

    with open(ap, "w", encoding="utf-8") as f:
        f.write(c)
    print("asset_page.py patched successfully")

def patch_portfolio():
    pp = os.path.join(ROOT, "tools", "portfolio_page.py")
    with open(pp, "r", encoding="utf-8") as f:
        c = f.read()

    # Display ftSym in portfolio rows
    c = c.replace(
        "+playerPhoto(k,h.n)+'<span><b>'+esc(h.n)+'</b><small>'+esc(k)+' · '+fmt(h.shares)+' shares'+(position?' · In club':'')+'</small></span></a>'",
        "+playerPhoto(k,h.n)+'<span><b>'+esc(h.n)+'</b><small><b>'+esc(ftSym(k))+'</b> · '+fmt(h.shares)+' shares'+(h.isLister?' · <span style=\"color:#a596ed\">Lister Allocation (1%/day trade limit)</span>':'')+(position?' · In club':'')+'</small></span></a>'"
    )

    # In CSV export: use ftSym(k)
    c = c.replace(
        "Object.keys(state.holdings).forEach(function(k){var h=state.holdings[k];rows.push([k,h.shares,h.avg,h.p,h.shares*h.p]);});",
        "Object.keys(state.holdings).forEach(function(k){var h=state.holdings[k];rows.push([ftSym(k),h.shares,h.avg,h.p,h.shares*h.p]);});"
    )

    # Add Lister Vesting & Economics section before holdings list
    lister_section = r'''
    var listerHtml = '';
    var claims = state.listerClaims || [];
    if(claims.length){
      listerHtml = '<div class="kc-group-box" style="margin-bottom:28px;background:#121411;border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:22px">'
        + '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">'
        + '  <div><h3 style="margin:0;font-size:18px;font-family:Space Grotesk,sans-serif;color:var(--ink)">Lister Allocations & Vesting</h3>'
        + '  <p style="margin:4px 0 0;font-size:12px;color:var(--dim)">Whitepaper v2.0 §8 · 1% daily trading release & 30% trading fee participation</p></div>'
        + '  <span style="background:rgba(24,0,173,.3);color:#a596ed;padding:4px 12px;border-radius:999px;font-size:11px;font-weight:600">' + claims.length + ' Launched</span>'
        + '</div>'
        + '<div style="display:grid;gap:12px">'
        + claims.map(function(cl){
            var daysLeft = Math.max(0, Math.ceil((cl.vestingUntil - Date.now()) / (1000 * 3600 * 24)));
            var dailyAvail = Math.max(0, cl.dailyLimit - (cl.tradedToday || 0));
            return '<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:14px;padding:16px;display:grid;grid-template-columns:auto 1fr auto;gap:16px;align-items:center">'
              + playerPhoto(cl.assetId, cl.name, 'kc-avatar')
              + '<div><div style="display:flex;align-items:center;gap:8px"><b>' + esc(cl.name) + '</b> <span style="background:#1800ad;color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:6px">' + esc(cl.ticker) + '</span></div>'
              + '<div style="font-size:12px;color:var(--dim);margin-top:4px">Level ' + cl.level + ' (' + cl.percent + '% of 10M) · <b>' + Number(cl.shares).toLocaleString() + ' shares</b> · ' + cl.vestingYears + '-year vesting (' + daysLeft + ' days remaining)</div>'
              + '<div style="font-size:11px;color:#a596ed;margin-top:4px">Daily Trading Release (1%): <b>' + Number(dailyAvail).toLocaleString() + ' / ' + Number(cl.dailyLimit).toLocaleString() + ' shares available today</b></div></div>'
              + '<div style="text-align:right"><div style="font-size:11px;color:var(--dim)">30% Fee Share Earned</div><b style="font-size:14px;color:var(--positive)">+' + Number(cl.feeShareEarned || 0).toLocaleString() + ' $FTR</b>'
              + '<div style="font-size:11px;color:var(--dim);margin-top:4px">Lister FP: <b style="color:var(--ink)">+' + Number(cl.listerFp || 0).toLocaleString() + ' FP</b></div></div>'
              + '</div>';
          }).join('')
        + '</div></div>';
    }
    var listerWrap = el('pfListerAllocations');
    if(!listerWrap){
      var host = el('pfRows');
      if(host && host.parentNode){
        var div = document.createElement('div');
        div.id = 'pfListerAllocations';
        host.parentNode.insertBefore(div, host);
        listerWrap = div;
      }
    }
    if(listerWrap) listerWrap.innerHTML = listerHtml;
'''
    if "listerHtml" not in c:
        c = c.replace("el('pfCount').textContent=shown.length+' of '+keys.length+' positions · Values in FTR';",
                      "el('pfCount').textContent=shown.length+' of '+keys.length+' positions · Values in FTR';" + lister_section)

    with open(pp, "w", encoding="utf-8") as f:
        f.write(c)
    print("portfolio_page.py patched successfully")

def patch_wallet():
    wp = os.path.join(ROOT, "tools", "wallet_pages.py")
    with open(wp, "r", encoding="utf-8") as f:
        c = f.read()

    c = c.replace("pickCard(f,f+' · '+fmt(h.shares)+' shares available')",
                  "pickCard(f,ftSym(f)+' · '+fmt(h.shares)+' shares available')")
    c = c.replace("pickCard(t,t+' · '+(prices[t]?",
                  "pickCard(t,ftSym(t)+' · '+(prices[t]?")
    c = c.replace("el('swGet').textContent=fmt(q.got)+' '+q.to;",
                  "el('swGet').textContent=fmt(q.got)+' '+ftSym(q.to);")
    c = c.replace("sub:k+(clubOf(k)?' · '+clubOf(k):'')",
                  "sub:ftSym(k)+(clubOf(k)?' · '+clubOf(k):'')")

    with open(wp, "w", encoding="utf-8") as f:
        f.write(c)
    print("wallet_pages.py patched successfully")

patch_exchange()
patch_asset_and_trade()
patch_portfolio()
patch_wallet()
