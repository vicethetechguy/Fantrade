#!/usr/bin/env python3
"""
tools/apply_whitepaper_lister_and_ftickers.py

Aligns all player Activity Shares with the Whitepaper F-Ticker system (FSAKA, FHLND, etc.)
and builds the complete Whitepaper Section 7 & 8 Lister Claiming infrastructure.
"""
import os, re

def patch_common():
    path = "tools/common.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update ASSETS array tickers to F-style
    old_assets = """var ASSETS=[
 {t:'$Saka',n:'Bukayo Saka',p:48.20,d:6.4,c:false,cap:'482.0M',h:51.2,low:46.8,q:'FTR',vol:'12.4M',tag:'10x',pos:'FWD',club:'Arsenal'},
 {t:'$Haaland',n:'Erling Haaland',p:71.40,d:-1.8,c:false,cap:'714.0M',h:74.0,low:70.1,q:'FTR',vol:'18.6M',tag:'10x',pos:'FWD',club:'Manchester City'},
 {t:'$Mbappe',n:'Kylian Mbappé',p:78.50,d:4.8,c:false,cap:'785.0M',h:81.0,low:76.2,q:'FTR',vol:'24.8M',tag:'10x',pos:'FWD',club:'Real Madrid'},
 {t:'$Vinicius',n:'Vinícius Júnior',p:63.10,d:0.7,c:false,cap:'631.0M',h:65.0,low:62.0,q:'FTR',vol:'15.2M',tag:'10x',pos:'FWD',club:'Real Madrid'},
 {t:'$Bellingham',n:'Jude Bellingham',p:58.90,d:3.3,c:false,cap:'589.0M',h:61.0,low:57.2,q:'FTR',vol:'14.1M',tag:'10x',pos:'MID',club:'Real Madrid'},
 {t:'$Palmer',n:'Cole Palmer',p:52.80,d:8.2,c:false,cap:'528.0M',h:54.5,low:49.1,q:'FTR',vol:'16.5M',tag:'10x',pos:'MID',club:'Chelsea'},
 {t:'$Yamal',n:'Lamine Yamal',p:66.20,d:9.4,c:false,cap:'662.0M',h:68.0,low:61.5,q:'FTR',vol:'22.1M',tag:'10x',pos:'FWD',club:'Barcelona'},
 {t:'$Musiala',n:'Jamal Musiala',p:46.70,d:5.1,c:false,cap:'467.0M',h:48.5,low:44.2,q:'FTR',vol:'11.5M',tag:'10x',pos:'MID',club:'Bayern Munich'},
 {t:'$Wirtz',n:'Florian Wirtz',p:44.60,d:3.8,c:false,cap:'446.0M',h:46.2,low:43.0,q:'FTR',vol:'10.9M',tag:'10x',pos:'MID',club:'Bayer Leverkusen'},
 {t:'$Rodri',n:'Rodri',p:61.30,d:1.4,c:false,cap:'613.0M',h:62.5,low:60.1,q:'FTR',vol:'13.7M',tag:'10x',pos:'MID',club:'Manchester City'},
 {t:'$Foden',n:'Phil Foden',p:54.10,d:-1.2,c:false,cap:'541.0M',h:56.0,low:53.2,q:'FTR',vol:'11.8M',tag:'10x',pos:'FWD',club:'Manchester City'},
 {t:'$Pedri',n:'Pedri González',p:41.15,d:-0.9,c:false,cap:'411.5M',h:42.5,low:40.1,q:'FTR',vol:'8.9M',tag:'10x',pos:'MID',club:'Barcelona'},
 {t:'$Saliba',n:'William Saliba',p:33.80,d:2.7,c:false,cap:'338.0M',h:35.0,low:32.4,q:'FTR',vol:'7.2M',tag:'10x',pos:'DEF',club:'Arsenal'},
 {t:'$Bruno',n:'Bruno Fernandes',p:39.75,d:2.1,c:false,cap:'397.5M',h:41.8,low:38.5,q:'FTR',vol:'9.8M',tag:'10x',pos:'MID',club:'Manchester United'},
 {t:'$Jackson',n:'Nicolas Jackson',p:14.85,d:11.2,c:false,cap:'148.5M',h:15.5,low:13.2,q:'FTR',vol:'5.4M',tag:'10x',pos:'FWD',club:'Chelsea'},
 {t:'$Arteta',n:'Mikel Arteta',p:22.05,d:4.9,c:true,cap:'220.5M',h:23.5,low:21.0,q:'FTR',vol:'6.1M',tag:'COACH',pos:'MGR',club:'Arsenal'},
 {t:'$Pep',n:'Pep Guardiola',p:29.60,d:-0.4,c:true,cap:'296.0M',h:30.8,low:28.9,q:'FTR',vol:'7.8M',tag:'COACH',pos:'MGR',club:'Manchester City'},
 {t:'$Maresca',n:'Enzo Maresca',p:18.30,d:1.2,c:true,cap:'183.0M',h:19.2,low:17.8,q:'FTR',vol:'4.5M',tag:'COACH',pos:'MGR',club:'Chelsea'}
];"""

    new_assets = """var ASSETS=[
 {t:'FSAKA',n:'Bukayo Saka',p:48.20,d:6.4,c:false,cap:'482.0M',h:51.2,low:46.8,q:'FTR',vol:'12.4M',tag:'10x',pos:'FWD',club:'Arsenal'},
 {t:'FHLND',n:'Erling Haaland',p:71.40,d:-1.8,c:false,cap:'714.0M',h:74.0,low:70.1,q:'FTR',vol:'18.6M',tag:'10x',pos:'FWD',club:'Manchester City'},
 {t:'FKM7',n:'Kylian Mbappé',p:78.50,d:4.8,c:false,cap:'785.0M',h:81.0,low:76.2,q:'FTR',vol:'24.8M',tag:'10x',pos:'FWD',club:'Real Madrid'},
 {t:'FVJR',n:'Vinícius Júnior',p:63.10,d:0.7,c:false,cap:'631.0M',h:65.0,low:62.0,q:'FTR',vol:'15.2M',tag:'10x',pos:'FWD',club:'Real Madrid'},
 {t:'FBEL',n:'Jude Bellingham',p:58.90,d:3.3,c:false,cap:'589.0M',h:61.0,low:57.2,q:'FTR',vol:'14.1M',tag:'10x',pos:'MID',club:'Real Madrid'},
 {t:'FPLMR',n:'Cole Palmer',p:52.80,d:8.2,c:false,cap:'528.0M',h:54.5,low:49.1,q:'FTR',vol:'16.5M',tag:'10x',pos:'MID',club:'Chelsea'},
 {t:'FYAML',n:'Lamine Yamal',p:66.20,d:9.4,c:false,cap:'662.0M',h:68.0,low:61.5,q:'FTR',vol:'22.1M',tag:'10x',pos:'FWD',club:'Barcelona'},
 {t:'FMUS',n:'Jamal Musiala',p:46.70,d:5.1,c:false,cap:'467.0M',h:48.5,low:44.2,q:'FTR',vol:'11.5M',tag:'10x',pos:'MID',club:'Bayern Munich'},
 {t:'FWRTZ',n:'Florian Wirtz',p:44.60,d:3.8,c:false,cap:'446.0M',h:46.2,low:43.0,q:'FTR',vol:'10.9M',tag:'10x',pos:'MID',club:'Bayer Leverkusen'},
 {t:'FRODR',n:'Rodri',p:61.30,d:1.4,c:false,cap:'613.0M',h:62.5,low:60.1,q:'FTR',vol:'13.7M',tag:'10x',pos:'MID',club:'Manchester City'},
 {t:'FFODN',n:'Phil Foden',p:54.10,d:-1.2,c:false,cap:'541.0M',h:56.0,low:53.2,q:'FTR',vol:'11.8M',tag:'10x',pos:'FWD',club:'Manchester City'},
 {t:'FPEDR',n:'Pedri González',p:41.15,d:-0.9,c:false,cap:'411.5M',h:42.5,low:40.1,q:'FTR',vol:'8.9M',tag:'10x',pos:'MID',club:'Barcelona'},
 {t:'FSALI',n:'William Saliba',p:33.80,d:2.7,c:false,cap:'338.0M',h:35.0,low:32.4,q:'FTR',vol:'7.2M',tag:'10x',pos:'DEF',club:'Arsenal'},
 {t:'FBRN',n:'Bruno Fernandes',p:39.75,d:2.1,c:false,cap:'397.5M',h:41.8,low:38.5,q:'FTR',vol:'9.8M',tag:'10x',pos:'MID',club:'Manchester United'},
 {t:'FJACK',n:'Nicolas Jackson',p:14.85,d:11.2,c:false,cap:'148.5M',h:15.5,low:13.2,q:'FTR',vol:'5.4M',tag:'10x',pos:'FWD',club:'Chelsea'},
 {t:'FARTA',n:'Mikel Arteta',p:22.05,d:4.9,c:true,cap:'220.5M',h:23.5,low:21.0,q:'FTR',vol:'6.1M',tag:'COACH',pos:'MGR',club:'Arsenal'},
 {t:'FPEP',n:'Pep Guardiola',p:29.60,d:-0.4,c:true,cap:'296.0M',h:30.8,low:28.9,q:'FTR',vol:'7.8M',tag:'COACH',pos:'MGR',club:'Manchester City'},
 {t:'FMARS',n:'Enzo Maresca',p:18.30,d:1.2,c:true,cap:'183.0M',h:19.2,low:17.8,q:'FTR',vol:'4.5M',tag:'COACH',pos:'MGR',club:'Chelsea'}
];"""

    if old_assets in content:
        content = content.replace(old_assets, new_assets)

    # 2. Update default holdings in common.py
    old_holdings = """    holdings: {
      '$Saka': { n: 'Bukayo Saka', shares: 10000, avg: 31.40, p: 48.20, c: false, inClub: 'RW' },
      '$Bruno': { n: 'Bruno Fernandes', shares: 5000, avg: 38.00, p: 39.75, c: false, inClub: 'CAM' },
      '$Haaland': { n: 'Erling Haaland', shares: 3000, avg: 68.50, p: 71.40, c: false, inClub: 'ST' },
      '$Arteta': { n: 'Mikel Arteta', shares: 1000, avg: 20.50, p: 22.05, c: true, inClub: 'COACH' }
    },"""

    new_holdings = """    holdings: {
      'FSAKA': { n: 'Bukayo Saka', shares: 10000, avg: 31.40, p: 48.20, c: false, inClub: 'RW' },
      'FBRN': { n: 'Bruno Fernandes', shares: 5000, avg: 38.00, p: 39.75, c: false, inClub: 'CAM' },
      'FHLND': { n: 'Erling Haaland', shares: 3000, avg: 68.50, p: 71.40, c: false, inClub: 'ST' },
      'FARTA': { n: 'Mikel Arteta', shares: 1000, avg: 20.50, p: 22.05, c: true, inClub: 'COACH' }
    },"""

    if old_holdings in content:
        content = content.replace(old_holdings, new_holdings)

    # 3. Update default clubs, fanplay, transactions in defaultState
    content = content.replace('coach: "$Arteta"', 'coach: "FARTA"')
    content = content.replace('coach: "$Pep"', 'coach: "FPEP"')
    content = content.replace('target: "$Saka"', 'target: "FSAKA"')
    content = content.replace('{ type: "BUY", asset: "$Saka"', '{ type: "BUY", asset: "FSAKA"')

    # 4. In getState(), migrate any legacy holdings keys
    migrate_snippet = """  function getState(){
    if(state) return state;
    try {
      var s = localStorage.getItem(STORAGE_KEY);
      state = s ? JSON.parse(s) : clone(defaultState);
    } catch(e){
      state = clone(defaultState);
    }
    // Migrate legacy holdings tickers ($Saka -> FSAKA, etc.)
    if(state && state.holdings){
      var keys = Object.keys(state.holdings);
      keys.forEach(function(k){
        var sym = ftSym(k);
        if(sym !== k){
          if(!state.holdings[sym]) state.holdings[sym] = state.holdings[k];
          else state.holdings[sym].shares = (state.holdings[sym].shares || 0) + (state.holdings[k].shares || 0);
          delete state.holdings[k];
        }
      });
    }"""

    old_get_state = """  function getState(){
    if(state) return state;
    try {
      var s = localStorage.getItem(STORAGE_KEY);
      state = s ? JSON.parse(s) : clone(defaultState);
    } catch(e){
      state = clone(defaultState);
    }"""

    if old_get_state in content and "Migrate legacy holdings tickers" not in content:
        content = content.replace(old_get_state, migrate_snippet)

    # 5. Ensure getAsset matches either original or ftSym
    old_get_asset = """  getAsset: function(sym){
    for(var i=0; i<ASSETS.length; i++){
      if(ASSETS[i].t === sym) return ASSETS[i];
    }
    return null;
  },"""

    new_get_asset = """  getAsset: function(sym){
    if(!sym) return null;
    var target = ftSym(sym);
    for(var i=0; i<ASSETS.length; i++){
      if(ASSETS[i].t === target || ASSETS[i].t === sym) return ASSETS[i];
    }
    return null;
  },"""

    if old_get_asset in content:
        content = content.replace(old_get_asset, new_get_asset)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("common.py patched successfully")

def patch_pages():
    path = "tools/pages.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace('[\"$Saka\",\"$Haaland\",\"$Mbappe\",\"$Yamal\"]', '[\"FSAKA\",\"FHLND\",\"FKM7\",\"FYAML\"]')
    content = content.replace("'$Saka': 'Arsenal'", "'FSAKA': 'Arsenal'")
    content = content.replace("'$Bruno': 'Manchester United'", "'FBRN': 'Manchester United'")
    content = content.replace("'$Haaland': 'Manchester City'", "'FHLND': 'Manchester City'")
    content = content.replace("'$Arteta': 'Arsenal'", "'FARTA': 'Arsenal'")
    content = content.replace("'$Mbappe': 'Real Madrid'", "'FKM7': 'Real Madrid'")
    content = content.replace("'$Yamal': 'Barcelona'", "'FYAML': 'Barcelona'")
    content = content.replace("'$Bellingham': 'Real Madrid'", "'FBEL': 'Real Madrid'")
    content = content.replace("'$Palmer': 'Chelsea'", "'FPLMR': 'Chelsea'")
    content = content.replace("'$Foden': 'Manchester City'", "'FFODN': 'Manchester City'")
    content = content.replace("'$Saliba': 'Arsenal'", "'FSALI': 'Arsenal'")
    content = content.replace("'$Pedri': 'Barcelona'", "'FPEDR': 'Barcelona'")
    content = content.replace("'$Rodri': 'Manchester City'", "'FRODR': 'Manchester City'")
    content = content.replace("'$Vinicius': 'Real Madrid'", "'FVJR': 'Real Madrid'")
    content = content.replace("'$Musiala': 'Bayern Munich'", "'FMUS': 'Bayern Munich'")
    content = content.replace("'$Wirtz': 'Bayer Leverkusen'", "'FWRTZ': 'Bayer Leverkusen'")

    content = content.replace("'$Saka': { n: 'Bukayo Saka'", "'FSAKA': { n: 'Bukayo Saka'")
    content = content.replace("'$Bruno': { n: 'Bruno Fernandes'", "'FBRN': { n: 'Bruno Fernandes'")
    content = content.replace("'$Haaland': { n: 'Erling Haaland'", "'FHLND': { n: 'Erling Haaland'")
    content = content.replace("'$Arteta': { n: 'Mikel Arteta'", "'FARTA': { n: 'Mikel Arteta'")

    content = content.replace("symbol:'$Saka'", "symbol:'FSAKA'")
    content = content.replace("symbol:'$Bruno'", "symbol:'FBRN'")
    content = content.replace("symbol:'$Haaland'", "symbol:'FHLND'")
    content = content.replace("symbol:'$Arteta'", "symbol:'FARTA'")

    content = content.replace("e.target || '$Saka'", "e.target || 'FSAKA'")
    content = content.replace('"$Saka · 42 FP"', '"FSAKA · 42 FP"')

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("pages.py patched successfully")

def patch_pages2():
    path = "tools/pages2.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace('("$Saka", "Bukayo Saka"', '("FSAKA", "Bukayo Saka"')
    content = content.replace('("$Haaland", "Erling Haaland"', '("FHLND", "Erling Haaland"')
    content = content.replace('("$Bruno", "Bruno Fernandes"', '("FBRN", "Bruno Fernandes"')
    content = content.replace('("$Arteta", "Mikel Arteta"', '("FARTA", "Mikel Arteta"')

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("pages2.py patched successfully")

def patch_pages3():
    path = "tools/pages3.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update hot filter list to F-tickers
    content = content.replace("['$Saka','$Haaland','$Mbappe','$Yamal','$Palmer','$Arteta']",
                              "['FSAKA','FHLND','FKM7','FYAML','FPLMR','FARTA']")

    # 2. Modernize and enhance claiming UI with full Whitepaper specifications
    # We replace lines 684-696 CSS and 770-772 HTML and 848-907 JS.
    # First, let's update CSS for the claim card & modal
    new_claim_css = """.home-claim-card{margin-top:18px;padding:20px;border-radius:20px;background:linear-gradient(135deg,rgba(24,0,173,.35) 0%,rgba(18,20,17,.92) 100%);border:1px solid rgba(165,150,237,.25);color:#fff;box-shadow:0 16px 36px rgba(0,0,0,.35);display:grid;gap:14px}
.home-claim-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
.home-claim-card h2{font-size:18px;margin:0 0 4px;color:#fff;font-family:Space Grotesk,sans-serif;font-weight:700;letter-spacing:-.01em}
.home-claim-card p{margin:0;color:rgba(255,255,255,.74);font-size:12px;line-height:1.55}
.home-claim-badge{display:inline-flex;align-items:center;justify-content:center;min-height:28px;padding:4px 12px;border-radius:999px;background:rgba(24,0,173,.4);border:1px solid rgba(165,150,237,.35);color:#a596ed;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;white-space:nowrap}
.home-claim-list{display:grid;gap:10px}
.home-claim-row{display:grid;grid-template-columns:44px minmax(0,1fr) auto;align-items:center;gap:12px;padding:12px 14px;border:1px solid rgba(255,255,255,.07);border-radius:14px;background:rgba(255,255,255,.04);color:#fff;text-align:left;width:100%;font:inherit;cursor:pointer;transition:all .2s ease}
.home-claim-row:hover:not([disabled]){border-color:rgba(165,150,237,.45);background:rgba(24,0,173,.18);transform:translateY(-1px)}
.home-claim-row[disabled]{cursor:default;opacity:.65;border-color:rgba(255,255,255,.04)}
.home-claim-row .player-photo{width:44px;height:44px;border-radius:50%;object-fit:cover;object-position:50% 18%;background:#050505;border:1px solid rgba(255,255,255,.1)}
.home-claim-row b{display:block;font-size:13.5px;font-family:Space Grotesk,sans-serif;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.home-claim-row small{display:block;margin-top:3px;color:rgba(255,255,255,.65);font-size:11px;line-height:1.4}
.home-claim-action{display:inline-flex;align-items:center;justify-content:center;min-height:34px;padding:8px 14px;border-radius:999px;background:var(--lime);color:#fff;font-size:11.5px;font-weight:800;letter-spacing:.02em;white-space:nowrap;box-shadow:0 6px 14px rgba(24,0,173,.35);transition:transform .15s ease}
.home-claim-row[disabled] .home-claim-action{background:rgba(255,255,255,.12);color:rgba(255,255,255,.5);box-shadow:none}
.home-claim-status{min-height:18px;font-size:11.5px;color:rgba(255,255,255,.8);margin:0}

/* Claim Modal Dialog */
.claim-modal-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.78);backdrop-filter:blur(6px);z-index:9999;display:none;place-items:center;padding:16px}
.claim-modal-backdrop.open{display:grid}
.claim-modal-dialog{background:#121411;border:1px solid rgba(165,150,237,.3);border-radius:24px;width:100%;max-width:460px;padding:24px;color:#fff;box-shadow:0 24px 60px rgba(0,0,0,.6);position:relative;animation:kcPop .2s cubic-bezier(.16,1,.3,1)}
@keyframes kcPop{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
.claim-modal-close{position:absolute;top:18px;right:18px;background:rgba(255,255,255,.08);border:0;color:#fff;width:32px;height:32px;border-radius:50%;cursor:pointer;font-size:16px;display:grid;place-items:center}
.claim-modal-head{display:flex;align-items:center;gap:14px;margin-bottom:18px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.08)}
.claim-modal-head .player-photo{width:56px;height:56px;border-radius:50%;object-fit:cover;object-position:50% 18%;border:2px solid var(--lime)}
.claim-modal-title{margin:0;font-size:18px;font-family:Space Grotesk,sans-serif;font-weight:700}
.claim-modal-sub{font-size:12px;color:rgba(255,255,255,.65);margin-top:2px}
.claim-section-lbl{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,.6);margin:14px 0 8px}
.claim-opt-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.claim-opt-btn{border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:12px;background:rgba(255,255,255,.04);color:#fff;text-align:left;cursor:pointer;font:inherit;transition:all .15s ease}
.claim-opt-btn.on{border-color:var(--lime);background:rgba(24,0,173,.22);box-shadow:0 0 0 1px var(--lime)}
.claim-opt-btn b{display:block;font-size:13px;font-family:Space Grotesk,sans-serif}
.claim-opt-btn small{display:block;margin-top:4px;font-size:10.5px;color:rgba(255,255,255,.65);line-height:1.3}
.claim-vest-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.claim-vest-btn{border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:10px 8px;background:rgba(255,255,255,.04);color:#fff;text-align:center;cursor:pointer;font:inherit;transition:all .15s ease}
.claim-vest-btn.on{border-color:var(--lime);background:rgba(24,0,173,.22);box-shadow:0 0 0 1px var(--lime)}
.claim-vest-btn b{display:block;font-size:12.5px}
.claim-vest-btn small{display:block;font-size:10px;color:rgba(255,255,255,.6);margin-top:2px}
.claim-rule-box{margin-top:14px;background:rgba(24,0,173,.14);border:1px solid rgba(165,150,237,.25);border-radius:14px;padding:12px 14px;font-size:11px;color:rgba(255,255,255,.8);line-height:1.55}
.claim-rule-box b{color:#a596ed}
.claim-fee-breakdown{margin-top:14px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:14px;padding:12px 14px;display:grid;gap:6px;font-size:11.5px}
.claim-fee-row{display:flex;justify-content:space-between;align-items:center;color:rgba(255,255,255,.7)}
.claim-fee-row.total{border-top:1px solid rgba(255,255,255,.08);padding-top:6px;margin-top:2px;font-weight:700;color:#fff;font-size:13px}
.claim-submit-btn{margin-top:16px;width:100%;min-height:46px;border-radius:999px;background:var(--lime);border:0;color:#fff;font-family:Space Grotesk,sans-serif;font-weight:700;font-size:14px;cursor:pointer;display:grid;place-items:center;transition:all .2s ease;box-shadow:0 8px 20px rgba(24,0,173,.4)}
.claim-submit-btn:hover:not([disabled]){transform:translateY(-1px);filter:brightness(1.1)}
.claim-submit-btn[disabled]{opacity:.5;cursor:not-allowed}"""

    # Replace the old CSS
    old_css_target = """.home-claim-card{margin-top:18px;padding:18px;border-radius:18px;background:#1800ad;color:#fff;box-shadow:0 16px 34px rgba(24,0,173,.28);display:grid;gap:14px}
.home-claim-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
.home-claim-card h2{font-size:20px;margin:0 0 4px;color:#fff}
.home-claim-card p{margin:0;color:rgba(255,255,255,.72);font-size:12px;line-height:1.55}
.home-claim-badge{display:inline-flex;align-items:center;justify-content:center;min-height:30px;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.14);font-size:10px;font-weight:700;white-space:nowrap}
.home-claim-list{display:grid;gap:10px}
.home-claim-row{display:grid;grid-template-columns:42px minmax(0,1fr) auto;align-items:center;gap:12px;padding:12px;border:0;border-radius:14px;background:rgba(5,5,5,.24);color:#fff;text-align:left;width:100%;font:inherit;cursor:pointer}
.home-claim-row[disabled]{cursor:default;opacity:.62}
.home-claim-row img{width:42px;height:42px;border-radius:50%;object-fit:cover;background:#050505}
.home-claim-row b{display:block;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.home-claim-row small{display:block;margin-top:3px;color:rgba(255,255,255,.64);font-size:10.5px;line-height:1.4}
.home-claim-action{display:inline-flex;align-items:center;justify-content:center;min-height:34px;padding:8px 12px;border-radius:999px;background:#fff;color:#1800ad;font-size:11px;font-weight:800;white-space:nowrap}
.home-claim-status{min-height:18px;font-size:11px;color:rgba(255,255,255,.72);margin:0}"""

    if old_css_target in content:
        content = content.replace(old_css_target, new_claim_css)

    # Replace HTML for claim section to include the modal markup
    old_html_target = ("'<div class=\"home-claim-card\" aria-labelledby=\"homeClaimTitle\"><div class=\"home-claim-head\"><div><h2 id=\"homeClaimTitle\">Claim listed players</h2>'\n"
                       "      '<p>Admin-listed Activity Shares appear here when a drop is live.</p></div><span class=\"home-claim-badge\">Admin drops</span></div>'\n"
                       "      '<div class=\"home-claim-list\" id=\"homeClaimList\" aria-live=\"polite\"></div><p class=\"home-claim-status\" id=\"homeClaimStatus\" role=\"status\"></p></div></section>']")

    new_html_target = ("'<div class=\"home-claim-card\" aria-labelledby=\"homeClaimTitle\"><div class=\"home-claim-head\"><div><h2 id=\"homeClaimTitle\">Launch & Claim Activity Shares</h2>'\n"
                       "      '<p>Admin-listed players ready for secondary market launch and FanPlay trading per Whitepaper Section 7 & 8.</p></div><span class=\"home-claim-badge\">Admin Drops</span></div>'\n"
                       "      '<div class=\"home-claim-list\" id=\"homeClaimList\" aria-live=\"polite\"></div><p class=\"home-claim-status\" id=\"homeClaimStatus\" role=\"status\"></p></div>'\n"
                       "      '<div class=\"claim-modal-backdrop\" id=\"claimModalBackdrop\" role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"claimModalTitle\">'\n"
                       "      '<div class=\"claim-modal-dialog\"><button type=\"button\" class=\"claim-modal-close\" id=\"claimModalClose\" aria-label=\"Close\">&times;</button>'\n"
                       "      '<div class=\"claim-modal-head\"><div id=\"claimModalPhoto\"></div><div><h3 class=\"claim-modal-title\" id=\"claimModalTitle\">Launch Player Shares</h3>'\n"
                       "      '<div class=\"claim-modal-sub\" id=\"claimModalSub\">Whitepaper Section 7 & 8 Lister Program</div></div></div>'\n"
                       "      '<div class=\"claim-section-lbl\">1. Select Allocation Level</div>'\n"
                       "      '<div class=\"claim-opt-grid\">'\n"
                       "      '<button type=\"button\" class=\"claim-opt-btn on\" data-level=\"1\"><b>Level 1 (5%)</b><small>500,000 Activity Shares<br>50,000 $FTR Listing Fee</small></button>'\n"
                       "      '<button type=\"button\" class=\"claim-opt-btn\" data-level=\"2\"><b>Level 2 (10%)</b><small>1,000,000 Activity Shares<br>100,000 $FTR Listing Fee</small></button>'\n"
                       "      '</div>'\n"
                       "      '<div class=\"claim-section-lbl\">2. Select Vesting Period</div>'\n"
                       "      '<div class=\"claim-vest-grid\">'\n"
                       "      '<button type=\"button\" class=\"claim-vest-btn on\" data-years=\"1\"><b>1 Year</b><small>12 mo. yield</small></button>'\n"
                       "      '<button type=\"button\" class=\"claim-vest-btn\" data-years=\"2\"><b>2 Years</b><small>24 mo. yield</small></button>'\n"
                       "      '<button type=\"button\" class=\"claim-vest-btn\" data-years=\"3\"><b>3 Years</b><small>36 mo. yield</small></button>'\n"
                       "      '</div>'\n"
                       "      '<div class=\"claim-rule-box\"><b>Lister Economics:</b> Receive <b>30% of secondary trading fees</b> during your selected vesting period. Original allocation is subject to a <b>1% daily trading limit</b> (<span id=\"claimDailyLimitTxt\">5,000</span> shares/day) and grants Pre-Airdrop Lister Fan Points.</div>'\n"
                       "      '<div class=\"claim-fee-breakdown\">'\n"
                       "      '<div class=\"claim-fee-row\"><span>Listing fee</span><span id=\"claimFeeTxt\">50,000 $FTR</span></div>'\n"
                       "      '<div class=\"claim-fee-row\"><span>Permanent burn (2%)</span><span id=\"claimBurnTxt\">1,000 $FTR</span></div>'\n"
                       "      '<div class=\"claim-fee-row\"><span>Lister Fan Points</span><span id=\"claimFpTxt\">+2,500 FP</span></div>'\n"
                       "      '<div class=\"claim-fee-row total\"><span>Total payable</span><span id=\"claimTotalTxt\">50,000 $FTR</span></div>'\n"
                       "      '</div>'\n"
                       "      '<button type=\"button\" class=\"claim-submit-btn\" id=\"claimSubmitBtn\">Pay 50,000 $FTR & Launch Shares</button>'\n"
                       "      '</div></div></section>']")

    if old_html_target in content:
        content = content.replace(old_html_target, new_html_target)

    # Replace DASH_JS claiming logic
    old_claim_js_pattern = r"\(function\(\)\{\s*var listEl = document\.getElementById\('homeClaimList'\).*?window\.addEventListener\('fantrade:statechange', loadClaims\);\s*\}\)\(\);"
    
    new_claim_js = """(function(){
  var listEl = document.getElementById('homeClaimList'), statusEl = document.getElementById('homeClaimStatus');
  var modal = document.getElementById('claimModalBackdrop'), closeBtn = document.getElementById('claimModalClose');
  var submitBtn = document.getElementById('claimSubmitBtn');
  var activeRow = null, selectedLevel = 1, selectedYears = 1;
  if(!listEl) return;

  function esc(value){ var n=document.createElement('span'); n.textContent=value == null ? '' : String(value); return n.innerHTML; }
  function assetFor(row){
    var sym = ftSym(row.asset_id || row.ticker || '');
    return ASSETS.filter(function(a){ return a.t === sym; })[0] || { t:sym, n:row.name || sym, p:Number(row.price)||0, c:row.kind === 'COACH' };
  }
  function fallbackListings(){
    var claimed = FT.getState().claimedListings || [];
    return [
      { id:'lst-saka-drop', asset_id:'FSAKA', ticker:'FSAKA', name:'Bukayo Saka', title:'Arsenal Star Drop', shares:500000 },
      { id:'lst-mbappe-drop', asset_id:'FKM7', ticker:'FKM7', name:'Kylian Mbappé', title:'Galáctico Drop', shares:500000 },
      { id:'lst-yamal-drop', asset_id:'FYAML', ticker:'FYAML', name:'Lamine Yamal', title:'Golden Boy Drop', shares:500000 },
      { id:'lst-haaland-drop', asset_id:'FHLND', ticker:'FHLND', name:'Erling Haaland', title:'Goal Machine Drop', shares:500000 }
    ].map(function(row){ row.claimed = claimed.indexOf(row.id) > -1; return row; });
  }
  function setStatus(text){ if(statusEl) statusEl.textContent = text || ''; }

  function updateModalCalculations(){
    var shares = (selectedLevel === 2) ? 1000000 : 500000;
    var fee = (selectedLevel === 2) ? 100000 : 50000;
    var burn = Math.round(fee * 0.02);
    var daily = Math.round(shares * 0.01);
    var fp = (selectedLevel === 2) ? '+5,000 FP' : '+2,500 FP';

    var dailyEl = document.getElementById('claimDailyLimitTxt');
    var feeEl = document.getElementById('claimFeeTxt');
    var burnEl = document.getElementById('claimBurnTxt');
    var fpEl = document.getElementById('claimFpTxt');
    var totEl = document.getElementById('claimTotalTxt');

    if(dailyEl) dailyEl.textContent = Number(daily).toLocaleString('en-US');
    if(feeEl) feeEl.textContent = Number(fee).toLocaleString('en-US') + ' $FTR';
    if(burnEl) burnEl.textContent = Number(burn).toLocaleString('en-US') + ' $FTR';
    if(fpEl) fpEl.textContent = fp;
    if(totEl) totEl.textContent = Number(fee).toLocaleString('en-US') + ' $FTR';

    if(submitBtn){
      var ticker = activeRow ? ftSym(activeRow.asset_id || activeRow.ticker) : 'Shares';
      submitBtn.textContent = 'Pay ' + Number(fee).toLocaleString('en-US') + ' $FTR & Launch ' + ticker;
    }
  }

  function openClaimModal(row){
    activeRow = row;
    selectedLevel = 1;
    selectedYears = 1;
    var a = assetFor(row);
    var titleEl = document.getElementById('claimModalTitle');
    var subEl = document.getElementById('claimModalSub');
    var photoEl = document.getElementById('claimModalPhoto');

    if(titleEl) titleEl.textContent = 'Launch ' + (a.n || 'Player') + ' (' + a.t + ')';
    if(subEl) subEl.textContent = (row.title || 'Official Admin Listing') + ' · 10M Total Supply';
    if(photoEl) photoEl.innerHTML = playerPhoto(a.t, a.n);

    if(modal){
      modal.querySelectorAll('.claim-opt-btn').forEach(function(b){
        b.classList.toggle('on', Number(b.dataset.level) === 1);
      });
      modal.querySelectorAll('.claim-vest-btn').forEach(function(b){
        b.classList.toggle('on', Number(b.dataset.years) === 1);
      });
      updateModalCalculations();
      modal.classList.add('open');
    }
  }

  function closeClaimModal(){
    if(modal) modal.classList.remove('open');
    activeRow = null;
  }

  if(closeBtn) closeBtn.addEventListener('click', closeClaimModal);
  if(modal){
    modal.addEventListener('click', function(e){
      if(e.target === modal) closeClaimModal();
    });
    modal.querySelectorAll('.claim-opt-btn').forEach(function(btn){
      btn.addEventListener('click', function(){
        modal.querySelectorAll('.claim-opt-btn').forEach(function(b){ b.classList.remove('on'); });
        btn.classList.add('on');
        selectedLevel = Number(btn.dataset.level) || 1;
        updateModalCalculations();
      });
    });
    modal.querySelectorAll('.claim-vest-btn').forEach(function(btn){
      btn.addEventListener('click', function(){
        modal.querySelectorAll('.claim-vest-btn').forEach(function(b){ b.classList.remove('on'); });
        btn.classList.add('on');
        selectedYears = Number(btn.dataset.years) || 1;
        updateModalCalculations();
      });
    });
  }

  if(submitBtn){
    submitBtn.addEventListener('click', function(){
      if(!activeRow) return;
      var row = activeRow;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Launching Activity Shares...';
      setStatus('Processing claim and setting up vesting...');

      var cloud = window.FTDB && FTDB.signedIn && FTDB.signedIn() && FTDB.claim;
      (cloud ? FTDB.claim(row.id, selectedLevel, selectedYears).then(function(res){
        return FT.syncCloud().then(function(){ return res; });
      }).catch(function(err){
        console.warn('[Fantrade] Cloud claim fallback to local state:', err.message);
        return FT.claimListing(row, selectedLevel, selectedYears);
      }) : Promise.resolve(FT.claimListing(row, selectedLevel, selectedYears)))
        .then(function(res){
          closeClaimModal();
          loadClaims();
          var sym = ftSym(row.asset_id || row.ticker);
          var shares = (selectedLevel === 2) ? 1000000 : 500000;
          setStatus('Successfully launched ' + sym + '! Claimed ' + Number(shares).toLocaleString('en-US') + ' shares with 1% daily trading limit & 30% trading fee participation.');
          if(window.FT && FT.notify) FT.notify('Lister Allocation Active: ' + Number(shares).toLocaleString('en-US') + ' ' + sym + ' shares vested (' + selectedYears + 'y).');
        })
        .catch(function(error){
          submitBtn.disabled = false;
          updateModalCalculations();
          setStatus(error.message || 'Claim could not be completed.');
          alert(error.message || 'Claim failed');
        });
    });
  }

  function render(rows){
    if(!rows || !rows.length){
      listEl.innerHTML = '<div class="home-claim-row" aria-disabled="true"><span></span><div><b>No active drops yet</b><small>Admin-listed Activity Assets will appear here.</small></div><span class="home-claim-action">Soon</span></div>';
      setStatus(''); return;
    }
    listEl.innerHTML = rows.slice(0, 4).map(function(row){
      var a = assetFor(row), claimed = !!row.claimed;
      return '<button type="button" class="home-claim-row" data-listing="' + esc(row.id) + '"' + (claimed ? ' disabled' : '') + '>'
        + playerPhoto(a.t, a.n)
        + '<span><b>' + esc(row.title || (a.n + ' Activity Asset')) + '</b><small>' + esc(a.t) + ' · 5% / 10% Claim · 1% daily limit</small></span>'
        + '<span class="home-claim-action">' + (claimed ? 'Claimed' : 'Launch & Claim') + '</span></button>';
    }).join('');

    listEl.querySelectorAll('button[data-listing]').forEach(function(button){
      button.addEventListener('click', function(){
        var row = rows.filter(function(x){ return x.id === button.dataset.listing; })[0];
        if(!row || row.claimed) return;
        openClaimModal(row);
      });
    });
  }

  function loadClaims(){
    setStatus('Checking active admin listings...');
    if(window.FTDB && FTDB.listings && FTDB.signedIn && FTDB.signedIn()){
      FTDB.listings().then(function(rows){ render(rows || fallbackListings()); setStatus(''); })
        .catch(function(){ render(fallbackListings()); setStatus(''); });
    } else {
      render(fallbackListings());
      setStatus('');
    }
  }
  loadClaims();
  window.addEventListener('fantrade:statechange', loadClaims);
})();"""

    content = re.sub(old_claim_js_pattern, new_claim_js, content, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("pages3.py patched successfully")

def patch_pages4():
    path = "tools/pages4.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("var SYM = param('a') || '$Saka';", "var SYM = ftSym(param('a') || 'FSAKA');")
    content = content.replace('<span id="tQtyUnit">$Saka</span>', '<span id="tQtyUnit">' + "' + SYM + '" + '</span>')
    content = content.replace('Buy $Saka', 'Buy ' + "' + SYM + '")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("pages4.py patched successfully")

def patch_asset_page():
    path = "tools/asset_page.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("var requested = new URLSearchParams(location.search).get('a') || '$Saka';",
                              "var requested = new URLSearchParams(location.search).get('a') || 'FSAKA';")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("asset_page.py patched successfully")

def patch_supabase_client():
    path = "public/fantrade-supabase.js"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old_claim = """    claim: async function (listingId) {
      await load();
      if (!client) throw new Error('Cannot reach the server right now.');
      if (!FTDB.signedIn()) throw new Error('Sign in to claim a listing.');
      var res = await client.rpc('ft_claim_listing', { p_listing: listingId });
      if (res.error) throw new Error(message(res.error));
      pullNotifications();
      return res.data;
    },"""

    new_claim = """    claim: async function (listingId, level, vestingYears) {
      await load();
      if (!client) throw new Error('Cannot reach the server right now.');
      if (!FTDB.signedIn()) throw new Error('Sign in to claim a listing.');
      var params = { p_listing: listingId };
      if (level) params.p_level = Number(level) || 1;
      if (vestingYears) params.p_vesting_years = Number(vestingYears) || 1;
      var res = await client.rpc('ft_claim_listing', params);
      if (res.error && /parameters|signature|schema cache/i.test(res.error.message)) {
        res = await client.rpc('ft_claim_listing', { p_listing: listingId });
      }
      if (res.error) throw new Error(message(res.error));
      pullNotifications();
      return res.data;
    },"""

    if old_claim in content:
        content = content.replace(old_claim, new_claim)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("fantrade-supabase.js patched successfully")

def patch_supabase_sql():
    path = "supabase/06_listings.sql"
    new_sql = """-- Fantrade · Admin-listed Activity Asset Drops & Lister Claiming Infrastructure
-- Per White Paper Draft v2.0 Section 7 & 8:
--   - 10M total conceptual supply per Activity Asset
--   - Level 1: 5% = 500,000 shares (50,000 $FTR fee)
--   - Level 2: 10% = 1,000,000 shares (100,000 $FTR fee)
--   - 2% permanent burn of listing fee
--   - Vesting duration: 1, 2, or 3 years (earns 30% trading fee participation)
--   - 1% daily trading limit on lister allocation (5k/day Level 1; 10k/day Level 2)

create table if not exists public.listings (
  id             text primary key,                       -- 'lst-saka-drop'
  asset_id       text not null references public.assets(id),
  title          text not null default '',
  shares_level1  bigint not null default 500000,
  shares_level2  bigint not null default 1000000,
  fee_level1     numeric(20,2) not null default 50000.00,
  fee_level2     numeric(20,2) not null default 100000.00,
  is_active      boolean not null default true,
  created_at     timestamptz not null default now()
);

-- Backward compatibility for column names
alter table public.listings add column if not exists shares_level1 bigint not null default 500000;
alter table public.listings add column if not exists shares_level2 bigint not null default 1000000;
alter table public.listings add column if not exists fee_level1 numeric(20,2) not null default 50000.00;
alter table public.listings add column if not exists fee_level2 numeric(20,2) not null default 100000.00;

create table if not exists public.claims (
  listing_id     text not null references public.listings(id) on delete cascade,
  user_id        uuid not null references auth.users(id) on delete cascade,
  claim_level    int not null default 1 check (claim_level in (1, 2)),
  shares         bigint not null default 500000,
  vesting_years  int not null default 1 check (vesting_years in (1, 2, 3)),
  fee_paid       numeric(20,2) not null default 50000.00,
  fee_burned     numeric(20,2) not null default 1000.00,
  daily_limit    bigint not null default 5000,
  vesting_until  timestamptz not null default (now() + interval '1 year'),
  claimed_at     timestamptz not null default now(),
  primary key (listing_id, user_id)
);

alter table public.claims add column if not exists claim_level int not null default 1;
alter table public.claims add column if not exists shares bigint not null default 500000;
alter table public.claims add column if not exists vesting_years int not null default 1;
alter table public.claims add column if not exists fee_paid numeric(20,2) not null default 50000.00;
alter table public.claims add column if not exists fee_burned numeric(20,2) not null default 1000.00;
alter table public.claims add column if not exists daily_limit bigint not null default 5000;
alter table public.claims add column if not exists vesting_until timestamptz not null default (now() + interval '1 year');

alter table public.listings enable row level security;
alter table public.claims enable row level security;

drop policy if exists listings_readable on public.listings;
create policy listings_readable on public.listings for select using (true);

drop policy if exists claims_select_own on public.claims;
create policy claims_select_own on public.claims for select using (auth.uid() = user_id);

-- ── What is claimable right now, and what this manager already took ──────
create or replace function public.ft_listings()
returns json
language plpgsql stable security definer set search_path = public, pg_temp
as $$
declare uid uuid := auth.uid();
begin
  return coalesce((select json_agg(row_to_json(row)) from (
    select l.id, l.asset_id, l.title, l.shares_level1, l.shares_level2, l.fee_level1, l.fee_level2,
           a.name, a.ticker, a.price, a.kind, a.club,
           exists (select 1 from public.claims c
                    where c.listing_id = l.id and c.user_id = uid) as claimed
      from public.listings l
      join public.assets a on a.id = l.asset_id
     where l.is_active
     order by l.created_at desc
  ) row), '[]'::json);
end;
$$;

-- ── Claim one listing: Section 7 & 8 Lister Launch Flow ──
create or replace function public.ft_claim_listing(
  p_listing text,
  p_level int default 1,
  p_vesting_years int default 1
)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  l   public.listings%rowtype;
  a   public.assets%rowtype;
  w   public.wallets%rowtype;
  v_shares bigint;
  v_fee numeric(20,2);
  v_burn numeric(20,2);
  v_daily bigint;
  v_until timestamptz;
  new_held bigint;
begin
  if p_listing is null or p_listing = '' then raise exception 'Pick a listing to claim'; end if;
  if p_level not in (1, 2) then p_level := 1; end if;
  if p_vesting_years not in (1, 2, 3) then p_vesting_years := 1; end if;

  select * into l from public.listings where id = p_listing and is_active for update;
  if not found then raise exception 'That listing is no longer available'; end if;

  if exists (select 1 from public.claims where listing_id = p_listing and user_id = uid) then
    raise exception 'You have already claimed this listing';
  end if;

  select * into a from public.assets where id = l.asset_id for update;
  if not found then raise exception 'That asset is not listed'; end if;

  -- Economics per Section 7 & 8
  if p_level = 2 then
    v_shares := coalesce(l.shares_level2, 1000000);
    v_fee    := coalesce(l.fee_level2, 100000.00);
    v_daily  := 10000;
  else
    v_shares := coalesce(l.shares_level1, 500000);
    v_fee    := coalesce(l.fee_level1, 50000.00);
    v_daily  := 5000;
  end if;

  v_burn  := round(v_fee * 0.02, 2);
  v_until := now() + (p_vesting_years || ' years')::interval;

  -- Check & deduct wallet balance
  select * into w from public.wallets where user_id = uid for update;
  if w.balance < v_fee then
    raise exception 'Insufficient $FTR balance. Required: % $FTR, available: % $FTR', v_fee, w.balance;
  end if;

  update public.wallets
     set balance = balance - v_fee, updated_at = now()
   where user_id = uid;

  -- Record claim
  insert into public.claims (
    listing_id, user_id, claim_level, shares, vesting_years, fee_paid, fee_burned, daily_limit, vesting_until
  ) values (
    p_listing, uid, p_level, v_shares, p_vesting_years, v_fee, v_burn, v_daily, v_until
  );

  -- Credit shares to user holdings
  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, l.asset_id, v_shares, a.price)
  on conflict (user_id, asset_id) do update
    set avg_cost = round(((public.holdings.shares * public.holdings.avg_cost) + (v_shares * a.price))
                         / (public.holdings.shares + v_shares), 4),
        shares = public.holdings.shares + v_shares,
        updated_at = now()
  returning public.holdings.shares into new_held;

  -- Increase circulating supply
  update public.assets
     set circulating = least(total_shares, circulating + v_shares), updated_at = now()
   where id = l.asset_id;

  -- Record transaction
  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'GRANT', l.asset_id,
          'Lister Launch (Level ' || p_level || ' · ' || p_vesting_years || 'y vesting): ' || coalesce(l.title, a.name),
          v_shares, a.price, v_fee, v_burn, w.balance - v_fee);

  return json_build_object(
    'listing', l.id,
    'asset', l.asset_id,
    'name', a.name,
    'ticker', a.ticker,
    'shares', v_shares,
    'level', p_level,
    'vesting_years', p_vesting_years,
    'fee_paid', v_fee,
    'fee_burned', v_burn,
    'daily_limit', v_daily,
    'held', new_held
  );
end;
$$;

-- Overload for single-parameter callers
create or replace function public.ft_claim_listing(p_listing text)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
begin
  return public.ft_claim_listing(p_listing, 1, 1);
end;
$$;

-- Seed listings with proper F-style tickers
insert into public.listings (id, asset_id, title, shares_level1, shares_level2, fee_level1, fee_level2, is_active) values
  ('lst-saka-drop',   'FSAKA', 'Arsenal Star Drop',    500000, 1000000, 50000, 100000, true),
  ('lst-mbappe-drop', 'FKM7',  'Galáctico Drop',       500000, 1000000, 50000, 100000, true),
  ('lst-yamal-drop',  'FYAML', 'Golden Boy Drop',      500000, 1000000, 50000, 100000, true),
  ('lst-haaland-drop','FHLND', 'Goal Machine Drop',    500000, 1000000, 50000, 100000, true)
on conflict (id) do update
  set asset_id = excluded.asset_id,
      title = excluded.title,
      shares_level1 = excluded.shares_level1,
      shares_level2 = excluded.shares_level2,
      fee_level1 = excluded.fee_level1,
      fee_level2 = excluded.fee_level2,
      is_active = excluded.is_active;

-- Permissions
revoke execute on all functions in schema public from public, anon;
grant execute on function public.ft_listings() to authenticated;
grant execute on function public.ft_claim_listing(text, int, int) to authenticated;
grant execute on function public.ft_claim_listing(text) to authenticated;
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_sql)
    print("06_listings.sql updated successfully")

if __name__ == "__main__":
    patch_common()
    patch_pages()
    patch_pages2()
    patch_pages3()
    patch_pages4()
    patch_asset_page()
    patch_supabase_client()
    patch_supabase_sql()
    print("All patches completed!")
