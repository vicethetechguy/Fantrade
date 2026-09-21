"""Onboarding-inspired presentation for the refreshed app destinations."""
PAGES = {'dashboard.html', 'exchange.html', 'fanplay.html', 'leaderboard.html', 'account.html', 'ftr.html', 'wallet.html', 'asset.html', 'trade.html'}
COMMUNITY_PAGES = {'portfolio.html', 'clubs.html', 'club-builder.html', 'liveboard.html', 'divisions.html'}
PAGES |= COMMUNITY_PAGES

def apply_design(filename, html):
    if filename not in PAGES:
        return html
    styles = '<link rel="stylesheet" href="public/app-onboarding.css">'
    if filename == 'asset.html':
        styles += '<link rel="stylesheet" href="public/asset-details.css">'
    if filename == 'trade.html':
        styles += '<link rel="stylesheet" href="public/app-secondary.css">'
    if filename in COMMUNITY_PAGES:
        styles += '<link rel="stylesheet" href="public/app-community.css">'
    return html.replace('</head>', styles + '</head>', 1).replace('<body class="app">', '<body class="app calm">', 1)

def intro(title, description, action=''):
    return ('<header class="app-intro"><div><h1>' + title + '</h1><p>' + description + '</p></div>' + action + '</header>')
