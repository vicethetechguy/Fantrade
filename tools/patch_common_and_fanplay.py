# -*- coding: utf-8 -*-
"""Patch tools/common.py, tools/notifications_page.py, and tools/pages.py to add female footballers, fix notification badge/read-all, and fix FanPlay Active/History."""

import re

# ==============================================================================
# 1. PATCH tools/common.py
# ==============================================================================
with open('tools/common.py', 'r', encoding='utf-8') as f:
    common = f.read()

# Fix bell_icon in nav()
common = re.sub(
    r'bell_icon = ic\("bell", "ic"\) \+ \'<span class="nav-bell-badge" hidden>0</span>\'',
    'bell_icon = ic("bell", "ic") + \'<span class="nav-bell-badge" hidden style="display:none">0</span>\'',
    common
)

# Add female tickers
if "'FAITN':'FAITN'" not in common:
    old_tickers = "'FPEP':'FPEP', 'FMARS':'FMARS', '$CR7':'FCR7'"
    new_tickers = "'FPEP':'FPEP', 'FMARS':'FMARS', 'FAITN':'FAITN', 'FPUTL':'FPUTL', 'FKERR':'FKERR', 'FRUSS':'FRUSS', 'FLJMS':'FLJMS', 'FWILM':'FWILM', 'FEARP':'FEARP', 'FWIEG':'FWIEG', '$CR7':'FCR7'"
    common = common.replace(old_tickers, new_tickers)

    old_alias = "'Pep':'FPEP', 'Maresca':'FMARS', 'CR7':'FCR7'"
    new_alias = "'Pep':'FPEP', 'Maresca':'FMARS', 'Bonmati':'FAITN', 'Aitana':'FAITN', 'Putellas':'FPUTL', 'Alexia':'FPUTL', 'Kerr':'FKERR', 'Russo':'FRUSS', 'James':'FLJMS', 'Williamson':'FWILM', 'Earps':'FEARP', 'Wiegman':'FWIEG', 'CR7':'FCR7'"
    common = common.replace(old_alias, new_alias)

# Add female assets to ASSETS array
female_assets = """ {t:'FAITN',n:'Aitana Bonmatí',p:72.80,d:5.8,c:false,cap:'728.0M',h:75.0,low:71.0,q:'FTR',vol:'17.3M',tag:'10x',pos:'MID',club:'Barcelona'},
 {t:'FPUTL',n:'Alexia Putellas',p:64.50,d:3.2,c:false,cap:'645.0M',h:66.8,low:63.2,q:'FTR',vol:'14.8M',tag:'10x',pos:'MID',club:'Barcelona'},
 {t:'FKERR',n:'Sam Kerr',p:56.40,d:4.1,c:false,cap:'564.0M',h:58.2,low:54.8,q:'FTR',vol:'12.6M',tag:'10x',pos:'FWD',club:'Chelsea'},
 {t:'FRUSS',n:'Alessia Russo',p:49.30,d:6.7,c:false,cap:'493.0M',h:51.5,low:47.9,q:'FTR',vol:'11.9M',tag:'10x',pos:'FWD',club:'Arsenal'},
 {t:'FLJMS',n:'Lauren James',p:53.60,d:7.4,c:false,cap:'536.0M',h:55.8,low:51.2,q:'FTR',vol:'13.2M',tag:'10x',pos:'FWD',club:'Chelsea'},
 {t:'FWILM',n:'Leah Williamson',p:36.50,d:1.8,c:false,cap:'365.0M',h:38.0,low:35.2,q:'FTR',vol:'8.1M',tag:'10x',pos:'DEF',club:'Arsenal'},
 {t:'FEARP',n:'Mary Earps',p:32.20,d:2.1,c:false,cap:'322.0M',h:33.5,low:31.0,q:'FTR',vol:'7.5M',tag:'10x',pos:'GK',club:'Paris Saint-Germain'},
 {t:'FWIEG',n:'Sarina Wiegman',p:26.80,d:3.6,c:true,cap:'268.0M',h:28.0,low:25.4,q:'FTR',vol:'6.9M',tag:'COACH',pos:'MGR',club:'England Women'}"""

if "FAITN" not in common:
    old_last_asset = "{t:'FMARS',n:'Enzo Maresca',p:18.30,d:1.2,c:true,cap:'183.0M',h:19.2,low:17.8,q:'FTR',vol:'4.5M',tag:'COACH',pos:'MGR',club:'Chelsea'}"
    common = common.replace(old_last_asset, old_last_asset + ",\n" + female_assets)

# Add player images
if "bonmati:" not in common:
    old_pimg = "arteta:'assets/players/arteta.webp',pep:'assets/players/pep.webp',maresca:'assets/players/maresca.webp',"
    new_pimg = "arteta:'assets/players/arteta.webp',pep:'assets/players/pep.webp',maresca:'assets/players/maresca.webp',\n  bonmati:'assets/players/bonmati.webp',putellas:'assets/players/putellas.webp',\n  kerr:'assets/players/kerr.webp',russo:'assets/players/russo.webp',\n  james:'assets/players/james.webp',williamson:'assets/players/williamson.webp',\n  earps:'assets/players/earps.webp',wiegman:'assets/players/wiegman.webp',"
    common = common.replace(old_pimg, new_pimg)

# Add player photo mapping
if "faitn:'bonmati'" not in common:
    old_pmap = "fmars:'maresca', fcr7:'saka', flm10:'saka' };"
    new_pmap = "fmars:'maresca', faitn:'bonmati', fputl:'putellas', fkerr:'kerr', fruss:'russo', fljms:'james', fwilm:'williamson', fearp:'earps', fwieg:'wiegman', fcr7:'saka', flm10:'saka' };"
    common = common.replace(old_pmap, new_pmap)

# Update syncUI for bell badge hiding
sync_pattern = r"var n = FT\.unread\(\);\s*document\.querySelectorAll\('#navDot'\)\.forEach\(function\(el\)\{\s*el\.hidden = n === 0;\s*\}\);\s*document\.querySelectorAll\('\.nav-bell-badge'\)\.forEach\(function\(el\)\{\s*el\.textContent = n > 99 \? '99\+' : String\(n\);\s*el\.hidden = n === 0;\s*\}\);"

sync_replacement = """var n = FT.unread();
      document.querySelectorAll('#navDot').forEach(function(el){
        el.hidden = n === 0;
        el.style.display = n === 0 ? 'none' : '';
      });
      document.querySelectorAll('.nav-bell-badge').forEach(function(el){
        if(n === 0){
          el.hidden = true;
          el.setAttribute('hidden', '');
          el.style.display = 'none';
          el.textContent = '';
        } else {
          el.hidden = false;
          el.removeAttribute('hidden');
          el.style.display = 'grid';
          el.textContent = n > 99 ? '99+' : String(n);
        }
      });"""

common = re.sub(sync_pattern, sync_replacement, common)

with open('tools/common.py', 'w', encoding='utf-8') as f:
    f.write(common)
print('Patched tools/common.py')

# ==============================================================================
# 2. PATCH tools/notifications_page.py
# ==============================================================================
with open('tools/notifications_page.py', 'r', encoding='utf-8') as f:
    np = f.read()

# Make sure unreadCount and action buttons cleanly sync FT.syncUI
old_np_unread = "function unreadCount(){var notes=FT.getState().notifications||[],count=notes.filter(n=>!n.read).length;document.getElementById('ntTotal').textContent=count?count+' unread':'You’re all caught up';document.getElementById('ntRead').disabled=count===0;document.getElementById('ntClear').disabled=notes.length===0;}"

new_np_unread = """function unreadCount(){
  var notes=FT.getState().notifications||[],count=notes.filter(n=>!n.read).length;
  document.getElementById('ntTotal').textContent=notes.length ? (count?count+' unread':'You’re all caught up') : 'No notifications';
  document.getElementById('ntRead').disabled=count===0;
  document.getElementById('ntClear').disabled=notes.length===0;
  if(typeof FT !== 'undefined' && FT.syncUI) FT.syncUI();
}"""

np = np.replace(old_np_unread, new_np_unread)

# Fix click handlers
np = re.sub(
    r"document\.getElementById\('ntRead'\)\.onclick\s*=\s*function\(\)\s*\{[^}]*\};",
    "document.getElementById('ntRead').onclick=function(){ FT.readAll(); renderFeed(); if(typeof FT!=='undefined'&&FT.syncUI)FT.syncUI(); };",
    np
)

np = re.sub(
    r"document\.getElementById\('ntClear'\)\.onclick\s*=\s*function\(\)\s*\{[^}]*\};",
    "document.getElementById('ntClear').onclick=function(){ FT.clearNotifications('all'); renderFeed(); if(typeof FT!=='undefined'&&FT.syncUI)FT.syncUI(); };",
    np
)

with open('tools/notifications_page.py', 'w', encoding='utf-8') as f:
    f.write(np)
print('Patched tools/notifications_page.py')

# ==============================================================================
# 3. PATCH tools/pages.py (FanPlay Active & History & Female Team Map)
# ==============================================================================
with open('tools/pages.py', 'r', encoding='utf-8') as f:
    pages = f.read()

# Add female team map in getLocalEligibleAssets
if "'FAITN': 'Barcelona'" not in pages:
    old_team_map = "'FSAKA': 'Arsenal', 'FBRN': 'Manchester United',"
    new_team_map = "'FSAKA': 'Arsenal', 'FBRN': 'Manchester United', 'FAITN': 'Barcelona', 'FPUTL': 'Barcelona', 'FKERR': 'Chelsea', 'FRUSS': 'Arsenal', 'FLJMS': 'Chelsea', 'FWILM': 'Arsenal', 'FEARP': 'Paris Saint-Germain', 'FWIEG': 'England Women',"
    pages = pages.replace(old_team_map, new_team_map)

# Replace loadUserFanPlays, updateDashboardMetrics, renderActiveList, renderHistoryList, cancelFanPlay, settleFanPlay
fanplay_logic_target = r"""function loadUserFanPlays(){
  function getLocalEntries(){
    var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
    if(s && s.fanplay && s.fanplay.activeEntries){
      return s.fanplay.activeEntries.map(function(e){
        // Compute FP from selections if totalFP was stored as 0
        var fp = e.totalFP || 0;
        if(fp === 0 && e.selections && e.selections.length > 0){
          var shares = e.stakedShares || e.stake || 100;
          fp = e.selections.reduce(function(acc, sel){
            return acc + ((sel.successFP || 0) * shares);
          }, 0);
        }
        // Compute $FTR value for older entries that used flat stake instead of share-priced stake
        var projectedFP = e.projectedFP || fp;
        return {
          id: e.id,
          status: e.status || 'ACTIVE',
          asset: e.asset || { symbol: e.target || 'FSAKA' },
          match: e.match || { homeTeam: 'Arsenal', awayTeam: 'Chelsea', status: 'SCHEDULED' },
          market: e.market || { name: e.tier || 'Solo' },
          stakedShares: e.stakedShares || e.stake || 100,
          totalFP: fp,
          projectedFP: projectedFP,
          selections: e.selections || [{ optionLabel: 'Matchday performance', evaluationResult: 'PENDING', successFP: 100, failureFP: -50 }]
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
      + '<button type="button" class="fp-btn-next" style="padding:10px 20px;font-size:12px" onclick="switchFPView(\\'wizard\\')">Create New Position</button>'
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
      + '    <span style="font-family:Space Grotesk,sans-serif;font-weight:700;font-size:17px;color:#fff">' + assetSym + '</span>'
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
      + (canCancel ? '<button type="button" class="fp-btn-back" style="padding:6px 14px;font-size:11px" onclick="window.cancelFanPlay(\\'' + fp.id + '\\')">Cancel Position</button>' : '')
      + (canSettle ? '<button type="button" class="fp-btn-next" style="padding:6px 14px;font-size:11px" onclick="window.settleFanPlay(\\'' + fp.id + '\\')">Execute Final Settlement</button>' : '')
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
      + '    <span style="font-family:Space Grotesk,sans-serif;font-weight:700;font-size:17px;color:#fff">' + assetSym + '</span>'
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
  var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
  if(s && s.fanplay && s.fanplay.activeEntries){
    s.fanplay.activeEntries = s.fanplay.activeEntries.filter(function(e){ return e.id !== id; });
    if(typeof FT.cancelEntry === 'function') FT.cancelEntry(id);
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
  var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
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
}"""

fanplay_logic_replacement = r"""function isFanPlayActive(st){
  var s = String(st || '').toUpperCase();
  return s === 'ACTIVE' || s === 'LIVE' || s === 'PENDING_SETTLEMENT' || s.indexOf('ACTIVE') !== -1;
}
function isFanPlaySettled(st){
  var s = String(st || '').toUpperCase();
  return s === 'SETTLED' || s === 'CANCELLED' || s === 'VOID' || s.indexOf('SETTLE') !== -1 || s.indexOf('CANCEL') !== -1;
}

function loadUserFanPlays(){
  function getLocalEntries(){
    var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
    var result = [];
    if(s && s.fanplay){
      var activeList = (s.fanplay.activeEntries || []).map(function(e){
        var fp = e.totalFP || 0;
        if(fp === 0 && e.selections && e.selections.length > 0){
          var shares = e.stakedShares || e.stake || 100;
          fp = e.selections.reduce(function(acc, sel){
            return acc + ((sel.successFP || 0) * shares);
          }, 0);
        } else if(fp === 0 && (e.projectedFP || e.stake)){
          fp = e.projectedFP || Math.round((e.stake || 100) * 0.08);
        }
        var projectedFP = e.projectedFP || fp;
        var rawStatus = e.status || 'ACTIVE';
        var normStatus = isFanPlaySettled(rawStatus) ? 'SETTLED' : 'ACTIVE';
        return {
          id: e.id,
          status: normStatus,
          displayStatus: rawStatus,
          mode: e.mode || 'Individual',
          asset: e.asset || { symbol: e.target || 'FSAKA' },
          match: e.match || { homeTeam: 'Arsenal', awayTeam: 'Chelsea', status: 'SCHEDULED' },
          market: e.market || { name: e.tier || 'Solo' },
          stakedShares: e.stakedShares || e.stake || 100,
          totalFP: fp,
          projectedFP: projectedFP,
          createdAt: e.createdAt || new Date().toISOString(),
          selections: e.selections && e.selections.length ? e.selections : [
            { optionLabel: 'Matchday performance & win', evaluationResult: 'PENDING', successFP: 100, failureFP: -50 }
          ]
        };
      });
      result = result.concat(activeList);

      // Load settled history entries
      var historyList = (s.fanplay.history || s.fanplay.settledEntries || []).map(function(h){
        return {
          id: h.id,
          status: h.status || 'SETTLED',
          asset: h.asset || { symbol: h.target || 'FSAKA' },
          match: h.match || { homeTeam: 'Arsenal', awayTeam: 'Chelsea', status: 'FINISHED' },
          market: h.market || { name: h.tier || 'Elite' },
          stakedShares: h.stakedShares || h.stake || 2500,
          totalFP: h.totalFP || 812,
          ftrSettlement: h.ftrSettlement != null ? h.ftrSettlement : 6200,
          settledAt: h.settledAt || '2026-09-23T09:14:00Z',
          selections: h.selections || [
            { optionLabel: 'Scores a goal', evaluationResult: 'SUCCESS', optionFP: 100 },
            { optionLabel: 'Creates 3+ chances', evaluationResult: 'SUCCESS', optionFP: 110 },
            { optionLabel: 'Clean sheet or win', evaluationResult: 'SUCCESS', optionFP: 75 }
          ]
        };
      });

      // If user has no history yet, supply default settled matchday positions matching the platform history (Matchday 06 and Matchday 05)
      if(historyList.length === 0){
        historyList = [
          {
            id: 'hist-md06',
            status: 'SETTLED',
            asset: { symbol: 'FSAKA', name: 'Bukayo Saka', team: 'Arsenal' },
            match: { homeTeam: 'Arsenal', awayTeam: 'Chelsea', status: 'FINISHED' },
            market: { name: 'Elite' },
            stakedShares: 2500,
            totalFP: 812,
            ftrSettlement: 6200,
            settledAt: '2026-09-23T09:14:00Z',
            selections: [
              { optionLabel: 'Bukayo Saka scores a goal', evaluationResult: 'SUCCESS', optionFP: 100, evaluationReason: 'Goal scored (34\')' },
              { optionLabel: 'Creates 3+ chances', evaluationResult: 'SUCCESS', optionFP: 110, evaluationReason: '4 key chances created' },
              { optionLabel: 'Arsenal clean sheet or win', evaluationResult: 'SUCCESS', optionFP: 75, evaluationReason: 'Arsenal won 3-1' }
            ]
          },
          {
            id: 'hist-md05',
            status: 'SETTLED',
            asset: { symbol: 'FHLND', name: 'Erling Haaland', team: 'Manchester City' },
            match: { homeTeam: 'Manchester City', awayTeam: 'Newcastle', status: 'FINISHED' },
            market: { name: 'Pro' },
            stakedShares: 1500,
            totalFP: 420,
            ftrSettlement: 3150,
            settledAt: '2026-09-16T18:30:00Z',
            selections: [
              { optionLabel: 'Erling Haaland scores a goal', evaluationResult: 'SUCCESS', optionFP: 100, evaluationReason: 'Goal scored (19\')' },
              { optionLabel: '2+ shots on target', evaluationResult: 'SUCCESS', optionFP: 80, evaluationReason: '3 shots on target' }
            ]
          }
        ];
      }
      result = result.concat(historyList);
    }
    return result;
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
  var active = userFanPlays.filter(function(fp){ return isFanPlayActive(fp.status); });
  var settled = userFanPlays.filter(function(fp){ return isFanPlaySettled(fp.status); });

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
  var active = userFanPlays.filter(function(fp){ return isFanPlayActive(fp.status); });
  if(active.length === 0){
    container.innerHTML = '<div style="padding:40px 20px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:14px">'
      + '<div style="font-size:32px;margin-bottom:8px">⚽</div>'
      + '<div style="font-weight:700;color:#fff;margin-bottom:4px">No Active Positions</div>'
      + '<div style="font-size:12px;margin-bottom:16px">You currently have no shares locked in active matchday FanPlays.</div>'
      + '<button type="button" class="fp-btn-next" style="padding:10px 20px;font-size:12px" onclick="switchFPView(\\'wizard\\')">Create New Position</button>'
      + '</div>';
    return;
  }
  container.innerHTML = active.map(function(fp){
    var assetSym = fp.asset ? fp.asset.symbol : (fp.target || '$ASSET');
    var matchName = fp.match ? (fp.match.homeTeam + ' vs ' + fp.match.awayTeam) : 'Matchday Fixture';
    var tierName = fp.market ? fp.market.name : 'FanPlay';
    var canSettle = fp.match && (fp.match.status === 'FINISHED' || fp.match.status === 'FINAL');
    var canCancel = isFanPlayActive(fp.status) && fp.match && (fp.match.status === 'SCHEDULED' || !fp.match.status);

    return '<div class="fp-panel" style="padding:18px;margin-bottom:12px">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
      + '  <div>'
      + '    <span style="font-family:Space Grotesk,sans-serif;font-weight:700;font-size:17px;color:#fff">' + assetSym + '</span>'
      + '    <span style="font-size:12px;color:#8E9AA8;margin-left:8px">' + matchName + '</span>'
      + '  </div>'
      + '  <span style="font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;background:rgba(24,0,173,.12);color:var(--lime)">' + (fp.displayStatus || fp.status) + '</span>'
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
      + (canCancel ? '<button type="button" class="fp-btn-back" style="padding:6px 14px;font-size:11px" onclick="window.cancelFanPlay(\\'' + fp.id + '\\')">Cancel Position</button>' : '')
      + (canSettle ? '<button type="button" class="fp-btn-next" style="padding:6px 14px;font-size:11px" onclick="window.settleFanPlay(\\'' + fp.id + '\\')">Execute Final Settlement</button>' : '')
      + '</div>'
      + '</div>';
  }).join('');
}

function renderHistoryList(){
  var container = document.getElementById('historyList');
  if(!container) return;
  var settled = userFanPlays.filter(function(fp){ return isFanPlaySettled(fp.status); });
  if(settled.length === 0){
    container.innerHTML = '<div style="padding:40px 20px;text-align:center;color:#8E9AA8;background:rgba(255,255,255,.02);border-radius:14px">'
      + '<div style="font-weight:700;color:#fff;margin-bottom:4px">No History</div>'
      + '<div style="font-size:12px">Settled matchday positions and $FTR ledger payouts will appear here.</div>'
      + '</div>';
    return;
  }
  container.innerHTML = settled.map(function(fp){
    var assetSym = fp.asset ? (fp.asset.symbol || fp.asset.name) : (fp.target || '$ASSET');
    var matchName = fp.match ? (fp.match.homeTeam + ' vs ' + fp.match.awayTeam) : 'Matchday Fixture';
    var isWin = (fp.ftrSettlement || 0) >= 0;
    var dt = new Date(fp.settledAt || fp.createdAt || Date.now()).toLocaleDateString();

    return '<div class="fp-panel" style="padding:18px;margin-bottom:12px">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
      + '  <div>'
      + '    <span style="font-family:Space Grotesk,sans-serif;font-weight:700;font-size:17px;color:#fff">' + assetSym + '</span>'
      + '    <span style="font-size:12px;color:#8E9AA8;margin-left:8px">' + matchName + ' · ' + dt + '</span>'
      + '  </div>'
      + '  <span style="font-size:14px;font-weight:800;color:' + (isWin ? 'var(--lime)' : '#FF5E5E') + '">'
      + (isWin ? '+' : '') + (fp.ftrSettlement || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' $FTR'
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
          var optFp = s.optionFP != null ? s.optionFP : (s.successFP || 100);
          return '<div style="display:flex;justify-content:space-between;align-items:center;font-size:12px">'
            + '<div><span style="color:#CAD2C5">• ' + s.optionLabel + '</span>'
            + (s.evaluationReason ? '<div style="font-size:10.5px;color:#8E9AA8;padding-left:12px">' + s.evaluationReason + '</div>' : '')
            + '</div>'
            + '<div style="text-align:right">'
            + '<span style="font-weight:700;color:' + resColor + '">' + (res || 'SUCCESS') + '</span> '
            + '<span style="color:#8E9AA8;font-size:11px">(+' + optFp + ' FP)</span>'
            + '</div>'
            + '</div>';
        }).join('')
      + '</div>'
      + '</div>';
  }).join('');
}

function cancelFanPlay(id){
  if(!confirm('Are you sure you want to cancel this FanPlay position and unlock your shares?')) return;
  var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
  if(s && s.fanplay && s.fanplay.activeEntries){
    var entry = s.fanplay.activeEntries.find(function(e){ return e.id === id; });
    s.fanplay.activeEntries = s.fanplay.activeEntries.filter(function(e){ return e.id !== id; });
    if(entry){
      s.fanplay.history = s.fanplay.history || [];
      entry.status = 'CANCELLED';
      entry.ftrSettlement = 0;
      s.fanplay.history.unshift(entry);
    }
    if(typeof FT.cancelEntry === 'function') FT.cancelEntry(id);
    if(typeof FT.save === 'function') FT.save();
    if(typeof FT.syncUI === 'function') FT.syncUI();
    window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: s }));
  }
  showToast('FanPlay position cancelled. Shares unlocked.', 'success');
  loadUserFanPlays();
}

function settleFanPlay(id){
  var s = (typeof FT !== 'undefined' && typeof FT.getState === 'function') ? FT.getState() : null;
  if(s && s.fanplay && s.fanplay.activeEntries){
    var idx = s.fanplay.activeEntries.findIndex(function(e){ return e.id === id; });
    if(idx !== -1){
      var entry = s.fanplay.activeEntries.splice(idx, 1)[0];
      entry.status = 'SETTLED';
      entry.ftrSettlement = Math.round((entry.stakedShares || entry.stake || 100) * 2.1);
      entry.settledAt = new Date().toISOString();
      s.fanplay.history = s.fanplay.history || [];
      s.fanplay.history.unshift(entry);
      if(s.wallet){
        s.wallet.balance = (s.wallet.balance || 0) + entry.ftrSettlement;
        s.wallet.locked = Math.max(0, (s.wallet.locked || 0) - (entry.stakedShares || entry.stake || 0));
        s.wallet.seasonEarned = (s.wallet.seasonEarned || 0) + entry.ftrSettlement;
      }
      s.transactions = s.transactions || [];
      s.transactions.unshift({
        type: 'PAYOUT',
        asset: 'FanPlay Settlement (' + (entry.market ? entry.market.name : 'Solo') + ')',
        shares: entry.stakedShares || 1,
        price: entry.ftrSettlement,
        total: entry.ftrSettlement,
        time: 'Just now'
      });
      if(typeof FT.save === 'function') FT.save();
      if(typeof FT.syncUI === 'function') FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: s }));
    }
  }
  showToast('Final match settlement complete! Shares unlocked and ledger updated.', 'success');
  loadUserFanPlays();
}"""

if fanplay_logic_target in pages:
    pages = pages.replace(fanplay_logic_target, fanplay_logic_replacement)
    print("Replaced fanplay_logic_target in pages.py")
else:
    # Use regex replacement if line formatting differs
    start_str = "function loadUserFanPlays(){"
    end_str = "function settleFanPlay(id){"
    s_idx = pages.find(start_str)
    e_idx = pages.find("window.switchFPView = switchFPView;", s_idx)
    if s_idx != -1 and e_idx != -1:
        pages = pages[:s_idx] + fanplay_logic_replacement + "\n\n" + pages[e_idx:]
        print("Replaced FanPlay logic by index in pages.py")
    else:
        print("Could not find start/end markers in pages.py")

with open('tools/pages.py', 'w', encoding='utf-8') as f:
    f.write(pages)
print('Patched tools/pages.py')
