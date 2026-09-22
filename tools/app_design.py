"""Onboarding-inspired presentation for the refreshed app destinations."""
PAGES = {'dashboard.html', 'exchange.html', 'fanplay.html', 'leaderboard.html', 'account.html', 'ftr.html', 'wallet.html', 'asset.html', 'trade.html'}
COMMUNITY_PAGES = {'portfolio.html', 'clubs.html', 'club-builder.html', 'liveboard.html', 'divisions.html'}
PAGES |= COMMUNITY_PAGES
UTILITY_PAGES = {'notifications.html', 'send.html', 'receive.html', 'swap.html', 'buy.html', 'withdraw.html', 'activity.html'}
PAGES |= UTILITY_PAGES
SETTINGS_PAGES = {'settings.html'} | {'settings-%s.html' % k for k in ('profile', 'club', 'security', 'alerts', 'wallet', 'play', 'data')}
PAGES |= SETTINGS_PAGES
GUIDE_PAGES = {'how-it-works.html'}
PAGES |= GUIDE_PAGES

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
    if filename in UTILITY_PAGES:
        styles += '<link rel="stylesheet" href="public/app-wallet.css">'
    if filename in SETTINGS_PAGES:
        styles += '<link rel="stylesheet" href="public/app-settings.css">'
    if filename in GUIDE_PAGES:
        styles += '<link rel="stylesheet" href="public/app-guide.css">'
    return html.replace('</head>', styles + '</head>', 1).replace('<body class="app">', '<body class="app calm">', 1)

def tab_intro(title, action=''):
    """Main tab destinations: the taskbar already says where you are, so the
    page name is kept for screen readers only and just the action shows."""
    return ('<header class="app-intro tab-intro"><h1 class="sr-only">' + title + '</h1>' + action + '</header>')

def intro(title, description, action=''):
    return ('<header class="app-intro"><div><h1>' + title + '</h1><p>' + description + '</p></div>' + action + '</header>')
