"""The original compact social leaderboard, with current season data."""
LEADERBOARD_HTML = r'''<main><div class="lb2-wrap restored-leaderboard">
<header class="lb2-section-head lb2-heading"><h1>Leaderboard</h1><a href="divisions.html">Divisions ↗</a></header>
<section aria-labelledby="lb2HighlightsTitle"><div class="lb2-section-head"><h2 id="lb2HighlightsTitle">Clubs to watch</h2><span id="standingsSource" role="status">Loading standings…</span></div><div class="lb2-clubs" id="lb2Clubs"></div></section>
<div class="lb2-filter"><button type="button" class="lb2-select" id="lb2Division" aria-haspopup="dialog">All clubs <span aria-hidden="true">⌄</span></button><span class="lb2-season">Season FP</span><button type="button" class="lb2-search-toggle" id="lb2SearchToggle" aria-label="Search clubs" aria-expanded="false" aria-controls="lb2SearchPanel"><svg class="ic" aria-hidden="true"><use href="#i-search"/></svg></button></div>
<div id="lb2SearchPanel" hidden><label class="lb2-search"><span class="sr-only">Search clubs and managers</span><input id="standingsSearch" type="search" placeholder="Find a club or manager" autocomplete="off"></label></div>
<a class="lb2-me" href="clubs.html" aria-label="Open your club"><span class="lb2-me-logo"><img src="assets/brand/fantrade-mark-white.svg" alt=""></span><span class="lb2-me-copy"><small>Your rank</small><b id="standingsMyRank">Not ranked yet</b></span><span class="lb2-me-value"><b id="standingsMyValue">—</b><small>$FTR club value</small></span></a>
<p class="sr-only" id="standingsCount" role="status"></p><div class="lb2-list" id="lb2List" aria-label="Club rankings"></div>
<p class="lb2-note">Ranked by season Fans Points. Club values are available when you open a club.</p>
</div></main>'''
LEADERBOARD_JS = r'''
var standingsRows=[],standingsPreview=true,standingsDivision='all';
function standingsEscape(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function standingsNumber(v){return Number(v||0).toLocaleString('en-US',{maximumFractionDigits:0});}
function standingsInitials(v){return String(v||'FC').split(/\s+/).map(function(w){return w.charAt(0);}).join('').slice(0,2).toUpperCase();}
function standingsMark(r){return '<span class="lb2-avatar lb2-crest">'+standingsEscape(standingsInitials(r.name))+'</span>';}
function standingsMedal(r){return '<span class="lb2-rank'+(r.position<=3?' medal'+(r.position===2?' silver':r.position===3?' bronze':''):'')+'">'+r.position+(r.position>3?'.':'')+'</span>';}
function standingsSquad(r){return r.squad&&r.squad.length?'<small class="lb2-squad">'+r.squad.slice(0,3).map(function(n){return playerPhoto(n.replace(/\s+\d+$/,''),n.replace(/\s+\d+$/,''));}).join('')+'</small>':'<small class="lb2-score-unit">FP</small>';}
function bindStandingButtons(){document.querySelectorAll('[data-standing]').forEach(function(button){button.onclick=function(){var r=standingsRows.find(function(row){return row.id===button.dataset.standing;});if(!r)return;openModal('<span class="premium-eyebrow">'+(standingsPreview?'Preview club':'Season standing')+'</span><h2 class="ft-modal-title">'+standingsEscape(r.name)+'</h2><p class="ft-modal-desc">'+standingsEscape(r.manager)+'</p><div class="lb2-detail-score"><b>#'+r.position+'</b><span>'+standingsNumber(r.fp)+' FP</span></div><p class="ft-modal-desc">Club value: '+standingsNumber(r.value)+' $FTR.</p><a class="app-primary" href="divisions.html">Explore divisions</a>');};});}
function renderStandings(){
 var q=document.getElementById('standingsSearch').value.trim().toLowerCase();
 var rows=standingsRows.filter(function(r){return (standingsDivision==='all'||r.division===standingsDivision)&&(r.name+' '+r.manager).toLowerCase().includes(q);});
 document.getElementById('standingsCount').textContent=rows.length+' clubs'+(standingsPreview?' · Preview field':'');
 document.getElementById('lb2List').innerHTML=rows.map(function(r){return '<button type="button" class="lb2-row'+(r.you?' you':'')+'" data-standing="'+standingsEscape(r.id)+'">'+standingsMedal(r)+standingsMark(r)+'<span class="lb2-name"><b>'+standingsEscape(r.name)+(r.you?'<em>You</em>':'')+'</b><span>'+standingsEscape(r.manager)+'</span></span><span class="lb2-profit">'+standingsNumber(r.fp)+standingsSquad(r)+'</span></button>';}).join('')||'<div class="lb2-empty"><h3>'+ (q?'No clubs found.':'No clubs in this field yet.')+'</h3><p>'+(q?'Try a different club or manager name.':'Clubs appear here as they join the season.')+'</p></div>';
 bindStandingButtons();
}
function renderHighlights(){document.getElementById('lb2Clubs').innerHTML=standingsRows.slice(0,3).map(function(r){return '<button type="button" class="lb2-club" data-standing="'+standingsEscape(r.id)+'">'+standingsMark(r)+'<b>'+standingsEscape(r.name)+'</b><small>'+standingsEscape(r.manager)+'</small><strong>'+standingsNumber(r.fp)+'<small>season FP</small></strong></button>';}).join('');}
function adoptStandings(rows,preview){
 standingsPreview=preview;standingsRows=rows;
 document.getElementById('standingsSource').textContent=preview?'Preview · Sample clubs':'Live club standings';
 var mine=rows.find(function(r){return r.you;});document.getElementById('standingsMyRank').textContent=mine?'Rank #'+mine.position:'Not ranked yet';document.getElementById('standingsMyValue').textContent=mine?standingsNumber(mine.value):'—';
 renderHighlights();renderStandings();
}
document.getElementById('standingsSearch').addEventListener('input',renderStandings);
document.getElementById('lb2SearchToggle').onclick=function(){var panel=document.getElementById('lb2SearchPanel'),open=panel.hidden;panel.hidden=!open;this.setAttribute('aria-expanded',String(open));if(open)document.getElementById('standingsSearch').focus();else{document.getElementById('standingsSearch').value='';renderStandings();}};
document.getElementById('lb2Division').onclick=function(){var divisions=Array.from(new Set(standingsRows.map(function(r){return r.division;}).filter(Boolean)));openModal('<h2 class="ft-modal-title">Choose your field</h2><div class="lb2-division-options"><button class="app-primary" type="button" data-board-division="all">All clubs</button>'+divisions.map(function(d){return '<button type="button" class="app-primary" data-board-division="'+standingsEscape(d)+'">'+standingsEscape(d)+'</button>';}).join('')+'</div>');document.querySelectorAll('[data-board-division]').forEach(function(b){b.onclick=function(){standingsDivision=this.dataset.boardDivision;document.getElementById('lb2Division').textContent=standingsDivision==='all'?'All clubs ⌄':standingsDivision+' ⌄';closeModal();renderStandings();};});};
var samples=BOARD_DATA.filter(function(r){return !r.you;}).map(function(r,i){return {id:'sample-'+i,name:r.c,manager:r.m,fp:r.fp,value:r.v,division:r.dv,you:false,squad:r.xi};}).sort(function(a,b){return b.fp-a.fp;}).map(function(r,i){r.position=i+1;return r;});
adoptStandings(samples,true);
FT.leaderboard(100).then(function(board){if(!board||!Array.isArray(board.rows))return;adoptStandings(board.rows.map(function(r){return {id:String(r.id),name:r.name,manager:r.display_name+' · @'+r.handle,position:Number(r.position),fp:Number(r.season_fp),value:Number(r.value),division:r.division,you:!!r.you};}),false);});
'''
