"""Premium P2P funding and cash-out, sharing the existing wallet shell."""
P2P_HTML = r'''<main><div class="p2p-page">
<a class="utility-back" href="wallet.html">← Wallet</a>
<header class="p2p-intro"><div><p class="p2p-kicker">FANTRADE P2P</p><h1>Funds, on your terms.</h1><p>Buy and sell $FTR in your local currency, directly with other fans.</p></div><button type="button" class="app-primary" id="p2pPost">Create an offer</button></header>
<div class="p2p-notice" id="p2pNotice" role="status"></div>
<nav class="p2p-tabs" aria-label="P2P sections"><button type="button" data-view="BUY" aria-pressed="true">Buy $FTR</button><button type="button" data-view="SELL" aria-pressed="false">Sell $FTR</button><button type="button" data-view="ORDERS" aria-pressed="false">My orders <span id="p2pOrderCount"></span></button><button type="button" data-view="OFFERS" aria-pressed="false">My offers</button></nav>
<div class="p2p-layout"><section>
<div class="p2p-filters" id="p2pFilters"><button type="button" id="p2pCurrency" aria-haspopup="dialog">USD ▾</button><button type="button" id="p2pMethod" aria-haspopup="dialog">All payments ▾</button><button type="button" id="p2pRefresh" aria-label="Refresh P2P offers">↻</button></div>
<p id="p2pStatus" class="p2p-status" role="status" aria-live="polite"></p><div id="p2pList"></div>
</section><aside class="p2p-guide"><span class="p2p-shield"><svg class="ic" aria-hidden="true"><use href="#i-shield"/></svg></span><h2>Protected by escrow.</h2><p>Fantrade locks the seller’s $FTR before the buyer pays. It stays locked until receipt is confirmed.</p><ol><li><b>Choose your offer</b><span>Compare the rate, limits and payment method.</span></li><li><b>Pay the seller directly</b><span>Use the payment details inside your order. Fantrade does not hold your bank payment.</span></li><li><b>Receive your $FTR</b><span>The seller confirms receipt and releases the tokens to your wallet.</span></li></ol><p class="p2p-available">Available to sell<strong id="p2pBalance">— $FTR</strong></p><p>Keep payment and messages inside the order. Never release $FTR based only on a screenshot.</p></aside></div>
<dialog id="p2pDialog" class="p2p-dialog" aria-labelledby="p2pDialogTitle"><header><h2 id="p2pDialogTitle"></h2><button type="button" id="p2pClose" aria-label="Close dialog">×</button></header><div id="p2pDialogBody"></div></dialog>
</div></main><script src="public/p2p.js"></script>'''
P2P_JS = "window.FantradeP2P.mount({FT:FT,showToast:showToast});"
