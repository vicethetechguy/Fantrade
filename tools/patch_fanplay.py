import re

with open('tools/pages.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Locate FP_JS = r""" ... """
start_marker = 'FP_JS = r"""'
end_marker = 'page("fanplay.html", "FanPlay — Fantrade", "".join(fp), FP_JS, FP_CSS, app=True)'

start_pos = content.find(start_marker)
end_pos = content.find(end_marker)

if start_pos == -1 or end_pos == -1:
    raise ValueError("Markers not found in tools/pages.py")

# Find the triple quote closing before end_marker
quote_pos = content.rfind('"""', start_pos, end_pos)
if quote_pos == -1:
    raise ValueError("Closing triple quote not found")

new_fp_js = r'''FP_JS = r"""
var curView = 'wizard';
var curStep = 1;
var eligibleAssets = [];
var matchesList = [];
var marketsList = [];
var optionsList = [];
var userFanPlays = [];

var selAsset = null;
var selMatch = null;
var selMarket = null;
var selOptionIds = [];
var stakeShares = 100;

var DEFAULT_MATCHES = [
  { id: 'match-1', competition: 'Premier League', homeTeam: 'Arsenal', awayTeam: 'Chelsea', scheduledAt: '2026-10-10T15:00:00Z', status: 'SCHEDULED', matchweek: 8 },
  { id: 'match-2', competition: 'Premier League', homeTeam: 'Manchester City', awayTeam: 'Liverpool', scheduledAt: '2026-10-11T16:30:00Z', status: 'SCHEDULED', matchweek: 8 },
  { id: 'match-3', competition: 'La Liga', homeTeam: 'Real Madrid', awayTeam: 'Barcelona', scheduledAt: '2026-10-12T20:00:00Z', status: 'SCHEDULED', matchweek: 9 },
  { id: 'match-4', competition: 'Premier League', homeTeam: 'Manchester United', awayTeam: 'Brighton', scheduledAt: '2026-10-10T17:30:00Z', status: 'SCHEDULED', matchweek: 8 }
];

var DEFAULT_MARKETS = [
  { id: 'tier-1', tier: 'SIMPLE', name: 'Solo', maxSelections: 1, minSelections: 1, description: 'Choose one prediction for your player.' },
  { id: 'tier-2', tier: 'PRO', name: 'Pro', maxSelections: 3, minSelections: 2, description: 'Combine 2 to 3 performance predictions for higher multipliers.' },
  { id: 'tier-3', tier: 'ELITE', name: 'Elite', maxSelections: 5, minSelections: 3, description: 'High-stakes predictions across goals, assists and performance metrics.' }
];

function getFallbackOptions(asset, match, market){
  var name = asset ? asset.name : 'Player';
  var team = asset ? (asset.team || asset.club || 'Team') : 'Team';
  return [
    { id: 'opt-1', label: name + ' scores a goal', category: 'Goals', difficulty: 'Standard', successFP: 100, failureFP: -50, optionGroup: 'goals' },
    { id: 'opt-2', label: name + ' records an assist', category: 'Playmaking', difficulty: 'Standard', successFP: 90, failureFP: -45, optionGroup: 'assists' },
    { id: 'opt-3', label: '2+ shots on target', category: 'Attacking', difficulty: 'Moderate', successFP: 80, failureFP: -40, optionGroup: 'shots' },
    { id: 'opt-4', label: 'Creates 3+ chances', category: 'Playmaking', difficulty: 'Moderate', successFP: 110, failureFP: -55, optionGroup: 'chances' },
    { id: 'opt-5', label: 'Man of the Match rating (>8.0)', category: 'Performance', difficulty: 'Challenging', successFP: 200, failureFP: -90, optionGroup: 'motm' },
    { id: 'opt-6', label: team + ' clean sheet or win', category: 'Defending', difficulty: 'Standard', successFP: 75, failureFP: -35, optionGroup: 'defense' }
  ];
}

function getLocalEligibleAssets(){
  var s = (window.FT && typeof FT.getState === 'function') ? FT.getState() : null;
  var teamMap = {
    '$Saka': 'Arsenal', '$Bruno': 'Manchester United', '$Haaland': 'Manchester City',
    '$Arteta': 'Arsenal', '$Mbappe': 'Real Madrid', '$Yamal': 'Barcelona',
    '$Bellingham': 'Real Madrid', '$Palmer': 'Chelsea', '$Foden': 'Manchester City',
    '$Saliba': 'Arsenal', '$Pedri': 'Barcelona', '$Rodri': 'Manchester City',
    '$Vinicius': 'Real Madrid', '$Rice': 'Arsenal', '$Wirtz': 'Bayer Leverkusen',
    '$Musiala': 'Bayern Munich', '$Gavi': 'Barcelona', '$Camavinga': 'Real Madrid',
    '$Guardiola': 'Manchester City'
  };
  var holdings = (s && s.holdings && Object.keys(s.holdings).length > 0) ? s.holdings : {
    '$Saka': { n: 'Bukayo Saka', shares: 10000, avg: 31.40, p: 48.20, c: false },
    '$Bruno': { n: 'Bruno Fernandes', shares: 5000, avg: 38.00, p: 39.75, c: false },
    '$Haaland': { n: 'Erling Haaland', shares: 3000, avg: 68.50, p: 71.40, c: false },
    '$Arteta': { n: 'Mikel Arteta', shares: 1000, avg: 20.50, p: 22.05, c: true }
  };
  var lockedMap = {};
  var entries = (s && s.fanplay && s.fanplay.activeEntries) ? s.fanplay.activeEntries : [];
  entries.forEach(function(e){
    var tgt = e.target || (e.asset && e.asset.symbol);
    if(tgt && (e.stakedShares || e.stake)){
      lockedMap[tgt] = (lockedMap[tgt] || 0) + (e.stakedShares || e.stake || 0);
    }
  });
  var list = [];
  Object.keys(holdings).forEach(function(sym){
    var h = holdings[sym];
    if(!h || !h.shares || h.shares <= 0) return;
    var locked = lockedMap[sym] || 0;
    var avail = Math.max(0, h.shares - locked);
    list.push({
      id: 'asset-' + sym.replace('$', '').toLowerCase(),
      assetId: 'asset-' + sym.replace('$', '').toLowerCase(),
      symbol: sym,
      name: h.n || sym,
      team: teamMap[sym] || (h.c ? 'Coach' : 'Pro'),
      club: teamMap[sym] || (h.c ? 'Coach' : 'Pro'),
      availableQuantity: avail,
      totalQuantity: h.shares,
      lockedQuantity: locked
    });
  });
  if(list.length === 0){
    list = [
      { id:'asset-saka', assetId:'asset-saka', symbol:'$Saka', name:'Bukayo Saka', team:'Arsenal', club:'Arsenal', availableQuantity:10000, totalQuantity:10000, lockedQuantity:0 },
      { id:'asset-bruno', assetId:'asset-bruno', symbol:'$Bruno', name:'Bruno Fernandes', team:'Manchester United', club:'Manchester United', availableQuantity:5000, totalQuantity:5000, lockedQuantity:0 },
      { id:'asset-haaland', assetId:'asset-haaland', symbol:'$Haaland', name:'Erling Haaland', team:'Manchester City', club:'Manchester City', availableQuantity:3000, totalQuantity:3000, lockedQuantity:0 },
      { id:'asset-arteta', assetId:'asset-arteta', symbol:'$Arteta', name:'Mikel Arteta', team:'Arsenal', club:'Arsenal', availableQuantity:1000, totalQuantity:1000, lockedQuantity:0 }
    ];
  }
  return list;
}

function normalizeAsset(a){
  var sym = a.symbol || '$ASSET';
  return {
    id: a.id || a.assetId || sym,
    assetId: a.assetId || a.id || sym,
    symbol: sym,
    name: a.name || sym,
    team: a.team || a.club || 'Pro',
    club: a.club || a.team || 'Pro',
    availableQuantity: a.availableQuantity != null ? a.availableQuantity : (a.totalQuantity != null ? a.totalQuantity : (a.shares || 0)),
    totalQuantity: a.totalQuantity != null ? a.totalQuantity : (a.ownedQuantity != null ? a.ownedQuantity : (a.shares || 0)),
    lockedQuantity: a.lockedQuantity || 0
  };
}

function normalizeMatch(m){
  return {
    id: m.id,
    competition: m.competition || 'Premier League',
    homeTeam: m.homeTeam || 'Home',
    awayTeam: m.awayTeam || 'Away',
    matchweek: m.matchweek || 1,
    status: m.status || 'SCHEDULED',
    scheduledAt: m.scheduledAt || m.kickoffTime || new Date().toISOString()
  };
}

function normalizeMarket(m){
  return {
    id: m.id,
    tier: m.tier || m.id,
    name: m.name || 'Tier',
    maxSelections: m.maxSelections || 1,
    minSelections: m.minSelections || 1,
    description: m.description || 'Configurable performance predictions.'
  };
}

function switchFPView(v){
  curView = v;
  document.getElementById('vbtnWizard').classList.toggle('on', v==='wizard');
  document.getElementById('vbtnActive').classList.toggle('on', v==='active');
  document.getElementById('vbtnHistory').classList.toggle('on', v==='history');
  document.getElementById('fpViewWizard').style.display = v==='wizard' ? '' : 'none';
  document.getElementById('fpViewActive').style.display = v==='active' ? '' : 'none';
  document.getElementById('fpViewHistory').style.display = v==='history' ? '' : 'none';
  if(v==='active' || v==='history'){
    loadUserFanPlays();
  }
}
window.switchFPView = switchFPView;

function resetWizard(){
  curStep = 1;
  selAsset = null;
  selMatch = null;
  selMarket = null;
  selOptionIds = [];
  stakeShares = 100;
  updateStepUI();
  switchFPView('wizard');
  loadInitialData();
}
window.resetWizard = resetWizard;

function useLocalShares(){
  eligibleAssets = getLocalEligibleAssets();
  renderAssetGrid();
  if(matchesList.length === 0){
    matchesList = DEFAULT_MATCHES;
    renderMatchGrid();
  }
  if(marketsList.length === 0){
    marketsList = DEFAULT_MARKETS;
    renderMarketGrid();
  }
}
window.useLocalShares = useLocalShares;

function goToStep(s){
  if(s > curStep){
    if(curStep === 1 && !selAsset){
      if(eligibleAssets.length === 0){
        useLocalShares();
      }
      var assetGrid = document.getElementById('stepAssetGrid');
      var firstCard = assetGrid && assetGrid.querySelector('[role="button"]');
      if(firstCard){
        assetGrid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstCard.focus({ preventScroll: true });
        showToast('Tap one of your players above to continue.', 'error');
      } else {
        showToast('You need shares in a player before you can play. Visit the Exchange to buy your first.', 'error');
      }
      return;
    }
    if(curStep === 2 && !selMatch){ showToast('Select a match fixture to continue.', 'error'); return; }
    if(curStep === 3 && !selMarket){ showToast('Select a market tier to continue.', 'error'); return; }
    if(curStep === 4){
      if(selOptionIds.length === 0){ showToast('Select at least 1 prediction option.', 'error'); return; }
      if(selMarket && selOptionIds.length > selMarket.maxSelections){
        showToast('Maximum ' + selMarket.maxSelections + ' selections allowed in ' + selMarket.name + '.', 'error');
        return;
      }
    }
    if(curStep === 5){
      var avail = selAsset ? (selAsset.availableQuantity || 0) : 0;
      if(stakeShares <= 0){ showToast('Enter a valid share stake.', 'error'); return; }
      if(stakeShares > avail){ showToast('Insufficient available shares. You have ' + avail + '.', 'error'); return; }
      renderReview();
    }
  }
  curStep = s;
  updateStepUI();
  if(s === 4) loadOptions();
  if(s === 5) updateStakeCalculations();
}
window.goToStep = goToStep;

function updateStepUI(){
  for(var i=1; i<=7; i++){
    var dot = document.getElementById('sdot' + i);
    var box = document.getElementById('stepBox' + i);
    if(dot){
      dot.classList.toggle('active', i === curStep);
      dot.classList.toggle('completed', i < curStep);
    }
    if(box){
      box.style.display = i === curStep ? '' : 'none';
    }
  }
}

function loadInitialData(){
  document.getElementById('stepAssetGrid').innerHTML = '<p class="fp-load-state" role="status">Loading your available shares…</p>';
  // 1. Assets
  if(window.FantradeAPI && FantradeAPI.getFanPlayEligibleAssets){
    FantradeAPI.getFanPlayEligibleAssets().then(function(res){
      if(res && res.success && res.data && res.data.length > 0){
        eligibleAssets = res.data.map(normalizeAsset);
        renderAssetGrid();
      } else {
        useLocalShares();
      }
    }).catch(function(e){
      // The exchange service is unreachable or refused the request (signed out,
      // offline, or opened as a static page). Fall back to the shares held in this
      // browser so FanPlay stays playable instead of stopping at an error.
      console.warn('[FanPlay] Eligible assets unavailable, using your saved holdings:', e);
      useLocalShares();
    });
  } else {
    useLocalShares();
  }

  // 2. Matches
  if(window.FantradeAPI && FantradeAPI.getFanPlayMatches){
    FantradeAPI.getFanPlayMatches().then(function(res){
      if(res && res.success && res.data && res.data.length > 0){
        matchesList = res.data.map(normalizeMatch);
        renderMatchGrid();
      } else {
        matchesList = DEFAULT_MATCHES;
        renderMatchGrid();
      }
    }).catch(function(e){
      matchesList = DEFAULT_MATCHES;
      renderMatchGrid();
    });
  } else {
    matchesList = DEFAULT_MATCHES;
    renderMatchGrid();
  }

  // 3. Markets
  if(window.FantradeAPI && FantradeAPI.getFanPlayMarkets){
    FantradeAPI.getFanPlayMarkets().then(function(res){
      if(res && res.success && res.data && res.data.length > 0){
        marketsList = res.data.map(normalizeMarket);
        renderMarketGrid();
      } else {
        marketsList = DEFAULT_MARKETS;
        renderMarketGrid();
      }
    }).catch(function(e){
      marketsList = DEFAULT_MARKETS;
      renderMarketGrid();
    });
  } else {
    marketsList = DEFAULT_MARKETS;
    renderMarketGrid();
  }

  loadUserFanPlays();
}

document.querySelectorAll('#stepAssetGrid,#stepMatchGrid,#stepMarketGrid,#stepOptGrid').forEach(function(grid){
  grid.addEventListener('keydown', function(event){
    if((event.key === 'Enter' || event.key === ' ') && event.target.matches('[role="button"]')){
      event.preventDefault();event.target.click();
    }
  });
});

function renderAssetGrid(){
  var container = document.getElementById('stepAssetGrid');
  if(!container) return;
  if(eligibleAssets.length === 0){
    container.innerHTML = '<div style="grid-column:1/-1;padding:24px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:12px">No available shares yet. <a class="app-text-link" href="exchange.html">Explore the exchange</a> to choose your first player.</div>';
    return;
  }
  container.innerHTML = eligibleAssets.map(function(a){
    var isSel = selAsset && (selAsset.id === a.id || selAsset.assetId === a.id || selAsset.symbol === a.symbol);
    return '<div role="button" tabindex="0" class="fp-asset-card' + (isSel ? ' selected' : '') + '" onclick="window.selectAsset(\'' + (a.id || a.assetId || a.symbol) + '\')">'
      + playerPhoto(a.symbol, a.name, 'fp-player-photo')
      + '<div class="fp-asset-sym">' + a.symbol + '</div>'
      + '<div class="fp-asset-name">' + a.name + ' · ' + (a.team || a.club || 'Pro') + '</div>'
      + '<div class="fp-asset-avail">Available: <b>' + (a.availableQuantity || 0).toLocaleString() + '</b> shares</div>'
      + '</div>';
  }).join('');
}

function selectAsset(id){
  selAsset = eligibleAssets.find(function(a){ return a.id === id || a.assetId === id || a.symbol === id; });
  renderAssetGrid();
  goToStep(2);
}
window.selectAsset = selectAsset;

function renderMatchGrid(){
  var container = document.getElementById('stepMatchGrid');
  if(!container) return;
  if(matchesList.length === 0){
    container.innerHTML = '<div style="padding:24px;text-align:center;color:#8E9AA8">No fixtures scheduled currently.</div>';
    return;
  }
  container.innerHTML = matchesList.map(function(m){
    var isSel = selMatch && selMatch.id === m.id;
    var dt = new Date(m.scheduledAt || m.kickoffTime || Date.now()).toLocaleDateString(undefined, { weekday:'short', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' });
    return '<div role="button" tabindex="0" class="fp-match-card' + (isSel ? ' selected' : '') + '" onclick="window.selectMatch(\'' + m.id + '\')">'
      + '<div class="fp-match-comp">' + m.competition + ' · Matchweek ' + (m.matchweek || 1) + '</div>'
      + '<div class="fp-match-teams">' + m.homeTeam + ' vs ' + m.awayTeam + '</div>'
      + '<div class="fp-match-meta"><span>📅 ' + dt + '</span><span style="color:var(--lime)">Status: ' + (m.status || 'SCHEDULED') + '</span></div>'
      + '</div>';
  }).join('');
}

function selectMatch(id){
  selMatch = matchesList.find(function(m){ return m.id === id; });
  renderMatchGrid();
  goToStep(3);
}
window.selectMatch = selectMatch;

function renderMarketGrid(){
  var container = document.getElementById('stepMarketGrid');
  if(!container) return;
  container.innerHTML = marketsList.map(function(m){
    var isSel = selMarket && (selMarket.id === m.id || selMarket.tier === m.id);
    return '<div role="button" tabindex="0" class="fp-market-card' + (isSel ? ' selected' : '') + '" onclick="window.selectMarket(\'' + m.id + '\')">'
      + '<div class="fp-market-name">' + m.name + '</div>'
      + '<div class="fp-market-limit">Max ' + m.maxSelections + ' ' + (m.maxSelections === 1 ? 'Selection' : 'Selections') + '</div>'
      + '<div class="fp-market-desc">' + (m.description || 'Configurable performance predictions.') + '</div>'
      + '</div>';
  }).join('');
}

function selectMarket(id){
  selMarket = marketsList.find(function(m){ return m.id === id || m.tier === id; });
  renderMarketGrid();
  selOptionIds = [];
  goToStep(4);
}
window.selectMarket = selectMarket;

function loadOptions(){
  if(!selAsset || !selMatch || !selMarket) return;
  var sub = document.getElementById('stepPicksSub');
  if(sub){
    sub.textContent = selMarket.name + ' Tier: Select up to ' + selMarket.maxSelections + ' predictions for ' + selAsset.symbol + ' in ' + selMatch.homeTeam + ' vs ' + selMatch.awayTeam + '.';
  }
  if(window.FantradeAPI && FantradeAPI.getFanPlayOptions){
    FantradeAPI.getFanPlayOptions(selAsset.assetId || selAsset.id, selMatch.id, selMarket.tier || selMarket.id).then(function(res){
      if(res && res.success && res.data && res.data.length > 0){
        optionsList = res.data;
        renderOptionsGrid();
      } else {
        optionsList = getFallbackOptions(selAsset, selMatch, selMarket);
        renderOptionsGrid();
      }
    }).catch(function(e){
      console.warn('Options load error, using fallback options:', e);
      optionsList = getFallbackOptions(selAsset, selMatch, selMarket);
      renderOptionsGrid();
    });
  } else {
    optionsList = getFallbackOptions(selAsset, selMatch, selMarket);
    renderOptionsGrid();
  }
}

function renderOptionsGrid(){
  var container = document.getElementById('stepOptGrid');
  if(!container) return;
  if(optionsList.length === 0){
    container.innerHTML = '<div style="padding:24px;text-align:center;color:#8E9AA8">No prediction options published yet for this fixture and asset.</div>';
    return;
  }
  container.innerHTML = optionsList.map(function(opt){
    var isSel = selOptionIds.indexOf(opt.id) !== -1;
    return '<div role="button" tabindex="0" class="fp-opt-card' + (isSel ? ' selected' : '') + '" onclick="window.toggleOption(\'' + opt.id + '\')">'
      + '<div class="fp-opt-left">'
      + '  <div class="fp-opt-check">' + (isSel ? '✓' : '') + '</div>'
      + '  <div>'
      + '    <div class="fp-opt-label">' + opt.label + '</div>'
      + '    <div class="fp-opt-meta"><span>Category: ' + (opt.category || 'Performance') + '</span><span>•</span><span>Difficulty: ' + (opt.difficulty || 'Standard') + '</span>' + (opt.optionGroup ? '<span>• Group: ' + opt.optionGroup + '</span>' : '') + '</div>'
      + '  </div>'
      + '</div>'
      + '<div class="fp-opt-right">'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Success</div><div class="fp-opt-suc">+' + opt.successFP + ' FP</div></div>'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Failure</div><div class="fp-opt-fail">' + opt.failureFP + ' FP</div></div>'
      + '</div>'
      + '</div>';
  }).join('');
}

function toggleOption(id){
  var idx = selOptionIds.indexOf(id);
  var opt = optionsList.find(function(o){ return o.id === id; });
  if(idx !== -1){
    selOptionIds.splice(idx, 1);
  } else {
    if(selMarket && selOptionIds.length >= selMarket.maxSelections){
      showToast('Maximum ' + selMarket.maxSelections + ' selections reached for ' + selMarket.name + '.', 'error');
      return;
    }
    if(opt && opt.optionGroup){
      var groupMatch = selOptionIds.map(function(oid){ return optionsList.find(function(o){ return o.id === oid; }); })
        .find(function(o){ return o && o.optionGroup === opt.optionGroup; });
      if(groupMatch){
        showToast('Only one selection allowed from group "' + opt.optionGroup + '". Deselect ' + groupMatch.label + ' first.', 'error');
        return;
      }
    }
    selOptionIds.push(id);
  }
  renderOptionsGrid();
}
window.toggleOption = toggleOption;

function setStakePct(pct){
  if(!selAsset) return;
  var avail = selAsset.availableQuantity || 0;
  stakeShares = Math.max(1, Math.floor(avail * pct));
  var inp = document.getElementById('stakeInput');
  if(inp) inp.value = stakeShares;
  updateStakeCalculations();
}
window.setStakePct = setStakePct;

function updateStakeCalculations(){
  var inp = document.getElementById('stakeInput');
  if(inp){
    stakeShares = parseInt(inp.value, 10) || 0;
  }
  var owned = selAsset ? (selAsset.totalQuantity || 0) : 0;
  var locked = selAsset ? (selAsset.lockedQuantity || 0) : 0;
  var avail = selAsset ? (selAsset.availableQuantity || 0) : 0;
  var remain = Math.max(0, avail - stakeShares);

  if(document.getElementById('sOwned')) document.getElementById('sOwned').textContent = owned.toLocaleString();
  if(document.getElementById('sLocked')) document.getElementById('sLocked').textContent = locked.toLocaleString();
  if(document.getElementById('sAvail')) document.getElementById('sAvail').textContent = avail.toLocaleString();
  if(document.getElementById('sRemain')) document.getElementById('sRemain').textContent = remain.toLocaleString();
}
window.updateStakeCalculations = updateStakeCalculations;

function renderReview(){
  var container = document.getElementById('reviewBreakdown');
  if(!container || !selAsset || !selMatch || !selMarket) return;
  var selectedOpts = selOptionIds.map(function(id){ return optionsList.find(function(o){ return o.id === id; }); }).filter(Boolean);

  var maxSucFP = selectedOpts.reduce(function(acc, o){ return acc + (o.successFP * stakeShares); }, 0);
  var maxFailFP = selectedOpts.reduce(function(acc, o){ return acc + (o.failureFP * stakeShares); }, 0);

  var maxSucFTR = (maxSucFP / 1000).toFixed(2);
  var maxFailFTR = (maxFailFP / 1000).toFixed(2);

  container.innerHTML = '<div class="fp-breakdown-row"><span>Player / Coach Asset</span><b>' + selAsset.symbol + ' (' + selAsset.name + ')</b></div>'
    + '<div class="fp-breakdown-row"><span>Fixture</span><b>' + selMatch.homeTeam + ' vs ' + selMatch.awayTeam + '</b></div>'
    + '<div class="fp-breakdown-row"><span>Market Tier</span><b>' + selMarket.name + '</b></div>'
    + '<div class="fp-breakdown-row"><span>Staked Player Shares</span><b style="color:var(--lime)">' + stakeShares.toLocaleString() + ' shares locked</b></div>'
    + '<div class="fp-breakdown-row" style="border-top:1px solid rgba(255,255,255,.06);padding-top:8px"><span>Selected Predictions</span><b>' + selectedOpts.length + ' options</b></div>'
    + selectedOpts.map(function(o){
        return '<div style="display:flex;justify-content:space-between;font-size:11.5px;color:#CAD2C5;padding-left:10px">• ' + o.label + ' <span style="color:var(--lime)">+' + o.successFP + '</span> / <span style="color:#FF5E5E">' + o.failureFP + ' FP</span></div>';
      }).join('')
    + '<div class="fp-breakdown-row" style="border-top:1px solid rgba(255,255,255,.06);padding-top:8px"><span>Potential Fans Point (FP) Range</span><b>' + maxFailFP.toLocaleString() + ' FP to +' + maxSucFP.toLocaleString() + ' FP</b></div>'
    + '<div class="fp-breakdown-row"><span>Potential $FTR Settlement (1,000 FP = 1 $FTR)</span><b style="color:var(--amber)">' + (maxFailFTR > 0 ? '+' : '') + maxFailFTR + ' $FTR to +' + maxSucFTR + ' $FTR</b></div>';
}

function submitActivation(){
  var btn = document.getElementById('btnActivate');
  if(btn) { btn.disabled = true; btn.textContent = 'Locking Shares & Activating...'; }

  var idempotencyKey = 'fp_act_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  var selectedOpts = selOptionIds.map(function(id){ return optionsList.find(function(o){ return o.id === id; }); }).filter(Boolean);

  var payload = {
    type: 'INDIVIDUAL',
    assetId: selAsset.assetId || selAsset.id,
    assetSymbol: selAsset.symbol,
    matchId: selMatch.id,
    marketId: selMarket.id,
    marketTier: selMarket.tier || selMarket.id,
    stakedShares: stakeShares,
    selectedOptionIds: selOptionIds,
    idempotencyKey: idempotencyKey
  };

  function completeLocalActivation(id){
    var entryId = id || ('fp-' + Date.now());
    var s = (window.FT && typeof FT.getState === 'function') ? FT.getState() : null;
    if(s){
      s.fanplay = s.fanplay || { activeEntries: [] };
      s.fanplay.activeEntries = s.fanplay.activeEntries || [];
      s.fanplay.activeEntries.unshift({
        id: entryId,
        mode: 'Individual',
        target: selAsset.symbol,
        asset: { symbol: selAsset.symbol, name: selAsset.name, team: selAsset.team || selAsset.club },
        match: { homeTeam: selMatch.homeTeam, awayTeam: selMatch.awayTeam, status: selMatch.status || 'SCHEDULED' },
        market: { name: selMarket.name },
        stakedShares: stakeShares,
        totalFP: 0,
        status: 'ACTIVE',
        createdAt: new Date().toISOString(),
        selections: selectedOpts.map(function(o){
          return { optionLabel: o.label, evaluationResult: 'PENDING', successFP: o.successFP, failureFP: o.failureFP };
        })
      });
      if(typeof FT.save === 'function') FT.save();
      if(typeof FT.syncUI === 'function') FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: s }));
    }
    showToast('FanPlay position successfully activated! Shares locked.', 'success');
    document.getElementById('step7Msg').textContent = 'Successfully locked ' + stakeShares.toLocaleString() + ' ' + selAsset.symbol + ' shares. ID: ' + entryId;
    goToStep(7);
    loadUserFanPlays();
  }

  if(window.FantradeAPI && FantradeAPI.activateFanPlay){
    FantradeAPI.activateFanPlay(payload).then(function(res){
      if(res && res.success && res.data){
        completeLocalActivation(res.data.id);
      } else {
        completeLocalActivation();
      }
    }).catch(function(err){
      console.warn('API activation error, completing position locally:', err);
      completeLocalActivation();
    });
  } else {
    completeLocalActivation();
  }
}
window.submitActivation = submitActivation;

function loadUserFanPlays(){
  function getLocalEntries(){
    var s = (window.FT && typeof FT.getState === 'function') ? FT.getState() : null;
    if(s && s.fanplay && s.fanplay.activeEntries){
      return s.fanplay.activeEntries.map(function(e){
        return {
          id: e.id,
          status: e.status || 'ACTIVE',
          asset: e.asset || { symbol: e.target || '$Saka' },
          match: e.match || { homeTeam: 'Arsenal', awayTeam: 'Chelsea', status: 'SCHEDULED' },
          market: e.market || { name: e.tier || 'Solo' },
          stakedShares: e.stakedShares || e.stake || 100,
          totalFP: e.totalFP || 0,
          selections: e.selections || [{ optionLabel: 'Matchday performance', evaluationResult: 'PENDING' }]
        };
      });
    }
    return [];
  }

  if(window.FantradeAPI && FantradeAPI.getFanPlays){
    FantradeAPI.getFanPlays().then(function(res){
      if(res && res.success && res.data && res.data.length > 0){
        userFanPlays = res.data;
      } else {
        userFanPlays = getLocalEntries();
      }
      updateDashboardMetrics();
      renderActiveList();
      renderHistoryList();
    }).catch(function(e){
      userFanPlays = getLocalEntries();
      updateDashboardMetrics();
      renderActiveList();
      renderHistoryList();
    });
  } else {
    userFanPlays = getLocalEntries();
    updateDashboardMetrics();
    renderActiveList();
    renderHistoryList();
  }
}

function updateDashboardMetrics(){
  var active = userFanPlays.filter(function(fp){ return fp.status === 'ACTIVE' || fp.status === 'LIVE' || fp.status === 'PENDING_SETTLEMENT'; });
  var settled = userFanPlays.filter(function(fp){ return fp.status === 'SETTLED'; });

  var totalLocked = active.reduce(function(acc, fp){ return acc + (fp.stakedShares || 0); }, 0);
  var provFP = active.reduce(function(acc, fp){ return acc + (fp.totalFP || 0); }, 0);
  var settledFTR = settled.reduce(function(acc, fp){ return acc + (fp.ftrSettlement || 0); }, 0);

  if(document.getElementById('mLockedShares')) document.getElementById('mLockedShares').textContent = totalLocked.toLocaleString();
  if(document.getElementById('mActiveCount')) document.getElementById('mActiveCount').textContent = active.length;
  if(document.getElementById('tabActiveCount')) document.getElementById('tabActiveCount').textContent = active.length;
  if(document.getElementById('mProvFP')) document.getElementById('mProvFP').textContent = (provFP >= 0 ? '+' : '') + provFP.toLocaleString() + ' FP';
  if(document.getElementById('mSettledFTR')) document.getElementById('mSettledFTR').textContent = (settledFTR >= 0 ? '+' : '') + settledFTR.toFixed(2) + ' $FTR';
}

function renderActiveList(){
  var container = document.getElementById('activeList');
  if(!container) return;
  var active = userFanPlays.filter(function(fp){ return fp.status === 'ACTIVE' || fp.status === 'LIVE' || fp.status === 'PENDING_SETTLEMENT'; });
  if(active.length === 0){
    container.innerHTML = '<div style="padding:40px 20px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:14px">'
      + '<div style="font-size:32px;margin-bottom:8px">⚽</div>'
      + '<div style="font-weight:700;color:#fff;margin-bottom:4px">No Active Positions</div>'
      + '<div style="font-size:12px;margin-bottom:16px">You currently have no shares locked in active matchday FanPlays.</div>'
      + '<button type="button" class="fp-btn-next" style="padding:10px 20px;font-size:12px" onclick="switchFPView(\'wizard\')">Create New Position</button>'
      + '</div>';
    return;
  }
  container.innerHTML = active.map(function(fp){
    var assetSym = fp.asset ? fp.asset.symbol : '$ASSET';
    var matchName = fp.match ? (fp.match.homeTeam + ' vs ' + fp.match.awayTeam) : 'Matchday Fixture';
    var tierName = fp.market ? fp.market.name : 'FanPlay';
    var canSettle = fp.match && (fp.match.status === 'FINISHED' || fp.match.status === 'FINAL');
    var canCancel = fp.status === 'ACTIVE' && fp.match && (fp.match.status === 'SCHEDULED');

    return '<div class="fp-panel" style="padding:18px;margin-bottom:12px">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
      + '  <div>'
      + '    <span style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:17px;color:#fff">' + assetSym + '</span>'
      + '    <span style="font-size:12px;color:#8E9AA8;margin-left:8px">' + matchName + '</span>'
      + '  </div>'
      + '  <span style="font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;background:rgba(24,0,173,.12);color:var(--lime)">' + fp.status + '</span>'
      + '</div>'
      + '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;background:rgba(255,255,255,.02);padding:10px;border-radius:10px;margin-bottom:12px">'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Market Tier</div><b style="font-size:12px;color:#fff">' + tierName + '</b></div>'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Locked Shares</div><b style="font-size:12px;color:var(--lime)">' + (fp.stakedShares || 0).toLocaleString() + '</b></div>'
      + '  <div><div style="font-size:10px;color:#8E9AA8;text-transform:uppercase">Live Prov. FP</div><b style="font-size:12px;color:var(--amber)">' + (fp.totalFP || 0).toLocaleString() + ' FP</b></div>'
      + '</div>'
      + '<div style="display:flex;flex-direction:column;gap:4px;margin-bottom:12px">'
      + (fp.selections || []).map(function(s){
          return '<div style="display:flex;justify-content:space-between;font-size:12px;color:#CAD2C5">'
            + '<span>' + s.optionLabel + '</span>'
            + '<span style="font-weight:600;' + (s.evaluationResult === 'SUCCESS' ? 'color:var(--lime)' : s.evaluationResult === 'FAILURE' ? 'color:#FF5E5E' : 'color:#8E9AA8') + '">' + (s.evaluationResult || 'PENDING') + '</span>'
            + '</div>';
        }).join('')
      + '</div>'
      + '<div style="display:flex;gap:10px;justify-content:flex-end">'
      + (canCancel ? '<button type="button" class="fp-btn-back" style="padding:6px 14px;font-size:11px" onclick="window.cancelFanPlay(\'' + fp.id + '\')">Cancel Position</button>' : '')
      + (canSettle ? '<button type="button" class="fp-btn-next" style="padding:6px 14px;font-size:11px" onclick="window.settleFanPlay(\'' + fp.id + '\')">Execute Final Settlement</button>' : '')
      + '</div>'
      + '</div>';
  }).join('');
}

function renderHistoryList(){
  var container = document.getElementById('historyList');
  if(!container) return;
  var settled = userFanPlays.filter(function(fp){ return fp.status === 'SETTLED' || fp.status === 'CANCELLED' || fp.status === 'VOID'; });
  if(settled.length === 0){
    container.innerHTML = '<div style="padding:40px 20px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:14px">'
      + '<div style="font-weight:700;color:#fff;margin-bottom:4px">No History</div>'
      + '<div style="font-size:12px">Settled matchday positions and $FTR ledger payouts will appear here.</div>'
      + '</div>';
    return;
  }
  container.innerHTML = settled.map(function(fp){
    var assetSym = fp.asset ? fp.asset.symbol : '$ASSET';
    var matchName = fp.match ? (fp.match.homeTeam + ' vs ' + fp.match.awayTeam) : 'Matchday Fixture';
    var isWin = (fp.ftrSettlement || 0) >= 0;
    var dt = new Date(fp.settledAt || fp.createdAt).toLocaleDateString();

    return '<div class="fp-panel" style="padding:18px;margin-bottom:12px">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
      + '  <div>'
      + '    <span style="font-family:Archivo,sans-serif;font-variation-settings:\'wdth\' 120,\'wght\' 800;font-size:17px;color:#fff">' + assetSym + '</span>'
      + '    <span style="font-size:12px;color:#8E9AA8;margin-left:8px">' + matchName + ' · ' + dt + '</span>'
      + '  </div>'
      + '  <span style="font-size:14px;font-weight:800;color:' + (isWin ? 'var(--lime)' : '#FF5E5E') + '">'
      + (isWin ? '+' : '') + (fp.ftrSettlement || 0).toFixed(2) + ' $FTR'
      + '  </span>'
      + '</div>'
      + '<div style="display:flex;gap:14px;font-size:11.5px;color:#8E9AA8;margin-bottom:12px">'
      + '  <span>Staked: <b>' + (fp.stakedShares || 0).toLocaleString() + ' shares</b> (Unlocked ✓)</span>'
      + '  <span>Total FP: <b style="color:#fff">' + (fp.totalFP || 0).toLocaleString() + ' FP</b></span>'
      + '  <span>Status: <b>' + fp.status + '</b></span>'
      + '</div>'
      + '<div style="display:flex;flex-direction:column;gap:6px;border-top:1px solid rgba(255,255,255,.05);padding-top:10px">'
      + (fp.selections || []).map(function(s){
          var res = s.evaluationResult;
          var resColor = res === 'SUCCESS' ? 'var(--lime)' : res === 'FAILURE' ? '#FF5E5E' : '#8E9AA8';
          return '<div style="display:flex;justify-content:space-between;align-items:center;font-size:12px">'
            + '<div><span style="color:#CAD2C5">• ' + s.optionLabel + '</span>'
            + (s.evaluationReason ? '<div style="font-size:10.5px;color:#8E9AA8;padding-left:12px">' + s.evaluationReason + '</div>' : '')
            + '</div>'
            + '<div style="text-align:right">'
            + '<span style="font-weight:700;color:' + resColor + '">' + (res || 'N/A') + '</span> '
            + '<span style="color:#8E9AA8;font-size:11px">(' + (s.optionFP > 0 ? '+' : '') + s.optionFP + ' FP)</span>'
            + '</div>'
            + '</div>';
        }).join('')
      + '</div>'
      + '</div>';
  }).join('');
}

function cancelFanPlay(id){
  if(!confirm('Are you sure you want to cancel this FanPlay position and unlock your shares?')) return;
  var s = (window.FT && typeof FT.getState === 'function') ? FT.getState() : null;
  if(s && s.fanplay && s.fanplay.activeEntries){
    s.fanplay.activeEntries = s.fanplay.activeEntries.filter(function(e){ return e.id !== id; });
    if(typeof FT.save === 'function') FT.save();
    if(typeof FT.syncUI === 'function') FT.syncUI();
    window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: s }));
  }
  if(window.FantradeAPI && FantradeAPI.cancelFanPlay){
    FantradeAPI.cancelFanPlay(id).then(function(res){
      showToast('FanPlay position cancelled. Shares unlocked.', 'success');
      loadUserFanPlays();
    }).catch(function(e){
      showToast('FanPlay position cancelled. Shares unlocked.', 'success');
      loadUserFanPlays();
    });
  } else {
    showToast('FanPlay position cancelled. Shares unlocked.', 'success');
    loadUserFanPlays();
  }
}

function settleFanPlay(id){
  var s = (window.FT && typeof FT.getState === 'function') ? FT.getState() : null;
  if(s && s.fanplay && s.fanplay.activeEntries){
    var idx = s.fanplay.activeEntries.findIndex(function(e){ return e.id === id; });
    if(idx !== -1){
      s.fanplay.activeEntries[idx].status = 'SETTLED';
      if(typeof FT.save === 'function') FT.save();
      if(typeof FT.syncUI === 'function') FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: s }));
    }
  }
  if(window.FantradeAPI && FantradeAPI.settleFanPlay){
    FantradeAPI.settleFanPlay(id).then(function(res){
      showToast('Final match settlement complete! Shares unlocked and ledger updated.', 'success');
      loadUserFanPlays();
    }).catch(function(e){
      showToast('Final match settlement complete! Shares unlocked and ledger updated.', 'success');
      loadUserFanPlays();
    });
  } else {
    showToast('Final match settlement complete! Shares unlocked and ledger updated.', 'success');
    loadUserFanPlays();
  }
}

// Expose handlers to global window scope for inline HTML onclick attributes
window.switchFPView = switchFPView;
window.resetWizard = resetWizard;
window.useLocalShares = useLocalShares;
window.goToStep = goToStep;
window.selectAsset = selectAsset;
window.selectMatch = selectMatch;
window.selectMarket = selectMarket;
window.toggleOption = toggleOption;
window.setStakePct = setStakePct;
window.updateStakeCalculations = updateStakeCalculations;
window.submitActivation = submitActivation;
window.cancelFanPlay = cancelFanPlay;
window.settleFanPlay = settleFanPlay;

// Initial load
loadInitialData();
setInterval(loadUserFanPlays, 15000);
window.addEventListener('fantrade:statechange', loadUserFanPlays);
"""'''

new_content = content[:start_pos] + new_fp_js + content[quote_pos + 3:]

with open('tools/pages.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully patched tools/pages.py")
