# -*- coding: utf-8 -*-
"""
Align Fantrade with White Paper Draft v2.0:
1. F-Ticker system across all pages: FSAKA, FHLND, FKM7, FVJR, FBEL, etc.
2. Lister & Claiming infrastructure:
   - Admin listing drops
   - Level 1 (5% = 500,000 shares) and Level 2 (10% = 1,000,000 shares)
   - $FTR fee payment + 2% permanent burn
   - Vesting options: 1 year, 2 years, 3 years
   - 1% daily trading limit (5,000 / 10,000 shares/day)
   - 30% trading-fee participation during vesting
   - Pre-airdrop Lister Fan Points (FP)
"""
import re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def patch_common():
    path = os.path.join(ROOT, "tools", "common.py")
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Add FT_TICKERS and ftSym before ASSETS if not present
    ticker_block = '''var FT_TICKERS={
  '$Saka':'FSAKA', '$Haaland':'FHLND', '$Mbappe':'FKM7', '$Vinicius':'FVJR',
  '$Bellingham':'FBEL', '$Palmer':'FPLMR', '$Yamal':'FYAML', '$Musiala':'FMUS',
  '$Wirtz':'FWRTZ', '$Rodri':'FRODR', '$Foden':'FFODN', '$Pedri':'FPEDR',
  '$Saliba':'FSALI', '$Bruno':'FBRN', '$Jackson':'FJACK', '$Arteta':'FARTA',
  '$Pep':'FPEP', '$Maresca':'FMARS', '$CR7':'FCR7', '$Ronaldo':'FCR7', '$Messi':'FLM10',
  'Saka':'FSAKA', 'Haaland':'FHLND', 'Mbappe':'FKM7', 'Vinicius':'FVJR',
  'Bellingham':'FBEL', 'Palmer':'FPLMR', 'Yamal':'FYAML', 'Musiala':'FMUS',
  'Wirtz':'FWRTZ', 'Rodri':'FRODR', 'Foden':'FFODN', 'Pedri':'FPEDR',
  'Saliba':'FSALI', 'Bruno':'FBRN', 'Jackson':'FJACK', 'Arteta':'FARTA',
  'Pep':'FPEP', 'Maresca':'FMARS', 'CR7':'FCR7', 'Ronaldo':'FCR7', 'Messi':'FLM10'
};
function ftSym(value){
  if(!value) return '';
  var s = String(value);
  if(FT_TICKERS[s]) return FT_TICKERS[s];
  if(s.startsWith('F') && s.length >= 4) return s;
  return s.replace(/\\$[A-Za-z0-9]+/g, function(id){
    return FT_TICKERS[id] || (id.charAt(1) === 'F' ? id.slice(1) : 'F' + id.slice(1).toUpperCase());
  }).replace(/^\\$/, '');
}
'''
    if "var FT_TICKERS" not in c:
        c = c.replace("var ASSETS=[", ticker_block + "var ASSETS=[")

    # Update playerPhoto to handle F-tickers
    old_pp = r"""function playerPhoto(symbol,name,className){
  var key=String(symbol||'').replace(/[^A-Za-z]/g,'').toLowerCase();
  var label=String(name||symbol||'Player').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
  var src=PLAYER_IMAGES[key]||PLAYER_IMAGES.saka;
  return "<img class='"+(className||'player-photo')+"' src='"+src+"' alt='"+label+"' loading='lazy' decoding='async'>";
}"""
    new_pp = r"""function playerPhoto(symbol,name,className){
  var raw = String(symbol||'').replace(/^\$/, '');
  var sLower = raw.toLowerCase();
  var key = sLower;
  if(sLower.startsWith('f') && sLower.length > 3){
    var map = { fsaka:'saka', fhlnd:'haaland', fkm7:'mbappe', fvjr:'vinicius', fbel:'bellingham', fplmr:'palmer', fyaml:'yamal', fmus:'musiala', fwrtz:'wirtz', frodr:'rodri', ffodn:'foden', fpedr:'pedri', fsali:'saliba', fbrn:'bruno', fjack:'jackson', farta:'arteta', fpep:'pep', fmars:'maresca', fcr7:'saka', flm10:'saka' };
    if(map[sLower]) key = map[sLower];
    else key = sLower.slice(1);
  }
  var label=String(name||symbol||'Player').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
  var src=PLAYER_IMAGES[key]||PLAYER_IMAGES.saka;
  return "<img class='"+(className||'player-photo')+"' src='"+src+"' alt='"+label+"' loading='lazy' decoding='async'>";
}"""
    if old_pp in c:
        c = c.replace(old_pp, new_pp)

    # 2. Update claimListing and trade in FT state store
    old_claim = r"""    claimListing: function(row){
      if(!row || !row.id) throw new Error('Pick a player listing to claim.');
      state.claimedListings = state.claimedListings || [];
      if(state.claimedListings.indexOf(row.id) > -1) throw new Error('You already claimed this listing.');
      var sym = row.asset_id || row.ticker || "";
      if(sym && sym.charAt(0) !== '$') sym = '$' + sym.replace(/^\$/, '');
      var asset = (typeof ASSETS !== 'undefined' ? ASSETS : []).filter(function(a){ return a.t === sym; })[0] || {};
      var shares = Math.max(1, Number(row.shares) || 1);
      var price = Number(row.price || asset.p || 0);
      if(!state.holdings[sym]){
        state.holdings[sym] = { n: row.name || asset.n || sym, shares: 0, avg: price,
          p: price, c: !!(row.kind === 'COACH' || asset.c), inClub: (row.kind === 'COACH' || asset.c) ? 'COACH' : 'SUB' };
      }
      var h = state.holdings[sym];
      var nextShares = h.shares + shares;
      h.avg = nextShares ? ((h.shares * h.avg) + (shares * price)) / nextShares : price;
      h.shares = nextShares;
      if(price) h.p = price;
      state.claimedListings.push(row.id);
      state.transactions.unshift({ type: 'GRANT', asset: sym, shares: shares, price: price,
        total: 0, time: 'Just now' });
      save(state); FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
      return { symbol: sym, name: h.n, shares: shares, held: h.shares };
    },"""

    new_claim = r"""    claimListing: function(opts){
      var row = typeof opts === 'object' && opts.id ? opts : (opts && opts.row ? opts.row : opts);
      if(!row || !row.id) throw new Error('Pick an Activity Asset listing to claim.');
      state.claimedListings = state.claimedListings || [];
      state.listerClaims = state.listerClaims || [];
      if(state.claimedListings.indexOf(row.id) > -1) throw new Error('You have already claimed this listing.');

      var level = (opts && (opts.level === 2 || opts.level === '2')) ? 2 : 1;
      var vestingYears = (opts && [1, 2, 3].indexOf(Number(opts.vestingYears)) > -1) ? Number(opts.vestingYears) : 1;
      var sym = row.asset_id || row.ticker || "";
      if(sym && sym.charAt(0) !== '$' && !sym.startsWith('F')) sym = '$' + sym;
      var ticker = ftSym(sym);
      var asset = (typeof ASSETS !== 'undefined' ? ASSETS : []).filter(function(a){ return a.t === sym || a.sym === ticker || ftSym(a.t) === ticker; })[0] || {};

      // Whitepaper Section 7: Level 1 = 5% (500,000 shares), Level 2 = 10% (1,000,000 shares) of 10M total supply
      var shares = level === 2 ? 1000000 : 500000;
      var percent = level === 2 ? 10 : 5;
      var fee = level === 2 ? 5000 : 2500;
      var burned = Math.round(fee * 0.02); // 2% permanently burned

      if(state.wallet.balance < fee){
        throw new Error('Insufficient $FTR balance. Claiming at Level ' + level + ' (' + percent + '%) requires ' + fee.toLocaleString('en-US') + ' $FTR.');
      }

      state.wallet.balance -= fee;
      state.claimedListings.push(row.id);

      // Whitepaper Section 8.2: 1% of original allocation per day (5,000/day for 500k; 10,000/day for 1M)
      var dailyLimit = Math.round(shares * 0.01);
      var now = Date.now();
      var vestingUntil = now + (vestingYears * 365 * 24 * 3600 * 1000);
      var listerFp = Math.round(shares / 100); // Pre-Airdrop Lister Fan Points

      state.listerClaims.push({
        id: 'lc-' + row.id,
        listingId: row.id,
        assetId: sym,
        ticker: ticker,
        name: row.name || asset.n || ticker,
        level: level,
        shares: shares,
        percent: percent,
        feePaid: fee,
        feeBurned: burned,
        vestingYears: vestingYears,
        claimedAt: now,
        vestingUntil: vestingUntil,
        dailyLimit: dailyLimit,
        tradedToday: 0,
        lastTradedDate: new Date().toISOString().slice(0, 10),
        feeSharePercent: 30, // 30% trading fee participation
        feeShareEarned: 0,
        listerFp: listerFp
      });

      // Credit shares to holdings
      var price = Number(row.price || asset.p || 0);
      if(!state.holdings[sym]){
        state.holdings[sym] = { n: row.name || asset.n || ticker, shares: 0, avg: price,
          p: price, c: !!(row.kind === 'COACH' || asset.c), inClub: (row.kind === 'COACH' || asset.c) ? 'COACH' : 'SUB' };
      }
      var h = state.holdings[sym];
      var nextShares = h.shares + shares;
      h.avg = nextShares ? ((h.shares * h.avg) + (shares * price)) / nextShares : price;
      h.shares = nextShares;
      h.isLister = true;
      h.listerDailyLimit = dailyLimit;
      if(price) h.p = price;

      // Award Lister Fan Points (Whitepaper Section 9)
      state.club.fp = (state.club.fp || 0) + listerFp;

      // Book transaction
      state.transactions.unshift({
        type: 'LAUNCH',
        asset: ticker,
        shares: shares,
        price: price,
        total: -fee,
        label: 'Launched ' + ticker + ' Activity Shares (' + percent + '%, ' + vestingYears + 'y vesting, ' + burned + ' $FTR burned)',
        time: 'Just now'
      });

      save(state); FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
      return { symbol: ticker, name: h.n, shares: shares, held: h.shares, feePaid: fee, feeBurned: burned, dailyLimit: dailyLimit, vestingYears: vestingYears, listerFp: listerFp };
    },"""

    if old_claim in c:
        c = c.replace(old_claim, new_claim)

    # 3. Update executeTrade to enforce 1% daily limit & 30% trading fee participation
    trade_start = "    executeTrade: function(side, assetSymbol, assetName, shares, price, isCoach){"
    if trade_start in c and "lister daily trading limit" not in c.lower():
        trade_patch = trade_start + r"""
      if(side === 'sell' && state.listerClaims && state.listerClaims.length){
        var today = new Date().toISOString().slice(0, 10);
        var claim = state.listerClaims.find(function(lc){
          return lc.assetId === assetSymbol || lc.ticker === assetSymbol || ftSym(lc.assetId) === ftSym(assetSymbol);
        });
        if(claim && Date.now() < claim.vestingUntil){
          if(claim.lastTradedDate !== today){
            claim.tradedToday = 0;
            claim.lastTradedDate = today;
          }
          if(claim.tradedToday + shares > claim.dailyLimit){
            var rem = Math.max(0, claim.dailyLimit - claim.tradedToday);
            throw new Error('Lister daily trading limit: You can only trade up to 1% (' + claim.dailyLimit.toLocaleString('en-US') + ' shares) per day during your ' + claim.vestingYears + '-year vesting. Remaining today: ' + rem.toLocaleString('en-US') + ' shares.');
          }
          claim.tradedToday += shares;
        }
      }"""
        c = c.replace(trade_start, trade_patch, 1)

    # 4. Add 30% trading fee share distribution to lister on every trade
    fee_dist_target = "state.transactions.unshift({\n        type: side.toUpperCase(),"
    fee_dist_code = r"""if(state.listerClaims && state.listerClaims.length){
        var claimMatch = state.listerClaims.find(function(lc){
          return lc.assetId === assetSymbol || lc.ticker === assetSymbol || ftSym(lc.assetId) === ftSym(assetSymbol);
        });
        if(claimMatch && Date.now() < claimMatch.vestingUntil){
          var listerFeeShare = Math.round(fee * 0.30);
          if(listerFeeShare > 0){
            claimMatch.feeShareEarned = (claimMatch.feeShareEarned || 0) + listerFeeShare;
            state.wallet.balance += listerFeeShare;
          }
        }
      }
      state.transactions.unshift({
        type: side.toUpperCase(),"""
    if fee_dist_target in c:
        c = c.replace(fee_dist_target, fee_dist_code, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("common.py patched successfully")

patch_common()
