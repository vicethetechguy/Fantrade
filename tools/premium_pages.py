"""Season standings: consistent FP ranking, live data and an explicit preview."""
LEADERBOARD_HTML = r'''<main><div class="lb2-wrap premium-standings">
<header class="standings-intro"><h1>Leaderboard</h1><a class="app-primary standings-guide" href="divisions.html">Divisions ↗</a></header>
<div class="standings-meta"><span><i></i> Season standings</span><span id="standingsSource" role="status">Loading standings…</span></div>
<h2 class="standings-highlights-title">Clubs to watch</h2><section class="standings-podium" id="standingsPodium" aria-label="Clubs to watch"></section>
<section class="standings-mine" aria-label="Your club"><span class="standings-mine-mark"><img src="assets/brand/fantrade-mark-white.svg" alt=""></span><div><small>Your club</small><b data-bind="club">Your club</b><span id="standingsMyRank">Not ranked yet</span></div><div class="standings-mine-points"><b id="standingsMyFP">—</b><small>season FP</small></div><a href="clubs.html" aria-label="Open your club"><span aria-hidden="true">↗</span></a></section>
<section class="standings-field" aria-labelledby="standingsFieldTitle"><div class="standings-controls"><div><h2 id="standingsFieldTitle">Club standings</h2><p id="standingsCount" role="status"></p></div><label class="standings-search"><svg class="ic" aria-hidden="true"><use href="#i-search"/></svg><span class="sr-only">Search clubs and managers</span><input id="standingsSearch" type="search" placeholder="Find a club or manager" autocomplete="off"></label></div>
<div class="standings-columns" aria-hidden="true"><span>Rank / Club</span><span>Club value · $FTR</span><span>Season FP</span></div><div class="lb2-list" id="lb2List"></div></section>
<p class="standings-note">Ranked by season Fans Points. Club value is shown for context and does not determine rank.</p>
</div></main>'''
LEADERBOARD_JS = r'''
var standingsRows=[],standingsPreview=true;
function standingsEscape(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function standingsNumber(v){return Number(v||0).toLocaleString('en-US',{maximumFractionDigits:0});}
function standingsMark(row){return '<span class="standings-crest"><img src="assets/brand/fantrade-mark-white.svg" alt=""></span>';}
function renderStandings(){
  var q=document.getElementById('standingsSearch').value.trim().toLowerCase();
  var rows=standingsRows.filter(function(r){return (r.name+' '+r.manager).toLowerCase().includes(q);});
  document.getElementById('standingsCount').textContent=rows.length+' '+(rows.length===1?'club':'clubs')+(standingsPreview?' · Preview field':'');
  document.getElementById('lb2List').innerHTML=rows.map(function(r){return '<button type="button" class="lb2-row standings-row'+(r.you?' you':'')+'" data-standing="'+standingsEscape(r.id)+'"><span class="standings-rank">'+r.position.toString().padStart(2,'0')+'</span>'+standingsMark(r)+'<span class="standings-club"><b>'+standingsEscape(r.name)+(r.you?'<em>You</em>':'')+'</b><small>'+standingsEscape(r.manager)+'</small></span><span class="standings-value">'+standingsNumber(r.value)+'<small>$FTR</small></span><span class="standings-points">'+standingsNumber(r.fp)+'<small>FP</small></span></button>';}).join('')||'<div class="standings-empty"><h3>'+ (q?'No clubs found.':'The next chapter starts with you.')+'</h3><p>'+(q?'Try a different club or manager name.':'Clubs will appear here as they join the season.')+'</p></div>';
  document.querySelectorAll('[data-standing]').forEach(function(button){button.onclick=function(){var r=standingsRows.find(function(row){return row.id===button.dataset.standing;});if(!r)return;openModal('<span class="premium-eyebrow">'+(standingsPreview?'Preview club':'Season standing')+'</span><h2 class="ft-modal-title">'+standingsEscape(r.name)+'</h2><p class="ft-modal-desc">'+standingsEscape(r.manager)+'</p><div class="standings-dialog-score">#'+r.position+' <span>'+standingsNumber(r.fp)+' FP</span></div><p class="ft-modal-desc">Club value: '+standingsNumber(r.value)+' $FTR. Rankings follow season Fans Points.</p><a class="app-primary" href="divisions.html">Explore divisions</a>');};});
}
function renderPodium(){
 document.getElementById('standingsPodium').innerHTML=standingsRows.slice(0,3).map(function(r,i){return '<article class="standings-leader leader-'+(i+1)+'"><div class="standings-leader-top"><span>'+'Rank #'+r.position+'</span><b>0'+(i+1)+'</b></div>'+standingsMark(r)+'<h2>'+standingsEscape(r.name)+'</h2><p>'+standingsEscape(r.manager)+'</p><div class="standings-leader-score">'+standingsNumber(r.fp)+'<small>season FP</small></div></article>';}).join('');
}
function adoptStandings(rows,preview){
 standingsPreview=preview;standingsRows=rows;
 document.getElementById('standingsSource').textContent=preview?'Preview · Sample clubs':'Live club standings';
 var mine=rows.find(function(r){return r.you;});
 document.getElementById('standingsMyRank').textContent=mine?'Rank #'+mine.position:'Not ranked yet';
 document.getElementById('standingsMyFP').textContent=mine?standingsNumber(mine.fp):'—';
 renderPodium();renderStandings();
}
document.getElementById('standingsSearch').addEventListener('input',renderStandings);
var samples=BOARD_DATA.filter(function(r){return !r.you;}).map(function(r,i){return {id:'sample-'+i,name:r.c,manager:r.m,fp:r.fp,value:r.v,division:r.dv,you:false};}).sort(function(a,b){return b.fp-a.fp;}).map(function(r,i){r.position=i+1;return r;});
adoptStandings(samples,true);
FT.leaderboard(100).then(function(board){if(!board||!Array.isArray(board.rows))return;adoptStandings(board.rows.map(function(r){return {id:String(r.id),name:r.name,manager:r.display_name+' · @'+r.handle,position:Number(r.position),fp:Number(r.season_fp),value:Number(r.value),division:r.division,you:!!r.you};}),false);});
'''
