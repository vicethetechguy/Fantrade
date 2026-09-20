"""Onboarding-inspired presentation for the six main app destinations."""
PAGES = {'dashboard.html', 'exchange.html', 'fanplay.html', 'leaderboard.html', 'account.html', 'ftr.html', 'wallet.html'}

def apply_design(filename, html):
    if filename not in PAGES:
        return html
    return html.replace('</head>', '<link rel="stylesheet" href="public/app-onboarding.css"></head>', 1).replace('<body class="app">', '<body class="app calm">', 1)

def intro(title, description, action=''):
    return ('<header class="app-intro"><div><h1>' + title + '</h1><p>' + description + '</p></div>' + action + '</header>')
