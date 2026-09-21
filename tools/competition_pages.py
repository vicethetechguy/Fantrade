"""Focused matchday and division destinations."""
from html import escape
from app_design import intro


def board_html(competitions):
    html = ['<main><div class="secondary-page board-page">', intro('Live board', 'Keep your eye on the game.', '<a class="quiet-button" href="fanplay.html">Open FanPlay</a>'),
            '<div class="board-toolbar"><div class="quiet-tabs" id="boardFilters" role="group" aria-label="Fixture filter"><button type="button" data-filter="all" aria-pressed="true">All fixtures</button><button type="button" data-filter="live" aria-pressed="false">Live</button><button type="button" data-filter="following" aria-pressed="false">Following</button></div><label class="quiet-search"><span class="sr-only">Search teams or competitions</span><input type="search" id="boardSearch" placeholder="Search teams or leagues" autocomplete="off"></label></div>',
            '<p class="quiet-note">Preview fixtures · Matchweek 7</p><p class="quiet-note" id="boardCount" role="status"></p><div id="boardGroups">']
    for code, name, week, fixtures in competitions:
        html.append('<section class="competition-group"><h2>'+escape(name)+'</h2>')
        for fid, home, hsh, hc, hs, away, ash, ac, away_score, status, clock, mine in fixtures:
            live = status in ('live', 'ht')
            label = home + ' vs ' + away
            html.append('<article class="match-row" data-fixture="'+fid+'" data-live="'+str(live).lower()+'" data-search="'+escape((label+' '+name).lower(),quote=True)+'">'
                        '<div class="match-time'+(' positive' if live else '')+'">'+escape(clock)+'</div><div class="match-teams">'
                        '<div><span class="match-crest" style="--team:'+hc+'">'+hsh+'</span><b>'+home+'</b><span>'+hs+'</span></div>'
                        '<div><span class="match-crest" style="--team:'+ac+'">'+ash+'</span><b>'+away+'</b><span>'+away_score+'</span></div>'
                        + ('<p class="match-player">'+escape(mine)+'</p>' if mine else '') + '</div>'
                        '<button class="match-follow" type="button" data-fav="'+fid+'" data-label="'+escape(label,quote=True)+'" aria-pressed="false" aria-label="Follow '+escape(label,quote=True)+'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3l-5.6 2.9 1.1-6.2L3 9.6l6.2-.9z"/></svg></button></article>')
        html.append('</section>')
    html.append('</div><div class="quiet-empty" id="boardEmpty" hidden><h2>No fixtures in this view.</h2><p>Try another team or follow a fixture from the All fixtures tab.</p><button class="quiet-button" type="button" id="boardReset">Show all fixtures</button></div></div></main>')
    return ''.join(html)


BOARD_JS = r'''
(function(){
  var filter='all',el=function(id){return document.getElementById(id);};
  function render(){
    var search=el('boardSearch').value.trim().toLowerCase(),count=0;
    document.querySelectorAll('.match-row').forEach(function(row){
      var followed=FT.isFav(row.dataset.fixture),button=row.querySelector('.match-follow');
      button.setAttribute('aria-pressed',String(followed));button.setAttribute('aria-label',(followed?'Unfollow ':'Follow ')+button.dataset.label);
      row.hidden=!(row.dataset.search.includes(search)&&(filter==='all'||filter==='live'&&row.dataset.live==='true'||filter==='following'&&followed));if(!row.hidden)count++;
    });
    document.querySelectorAll('.competition-group').forEach(function(group){group.hidden=![...group.querySelectorAll('.match-row')].some(function(row){return !row.hidden;});});
    el('boardCount').textContent=count+' '+(count===1?'fixture':'fixtures')+(filter==='live'?' in play':filter==='following'?' followed':'');el('boardEmpty').hidden=count>0;
    el('boardFilters').querySelectorAll('button').forEach(function(button){button.setAttribute('aria-pressed',String(button.dataset.filter===filter));});
  }
  el('boardFilters').querySelectorAll('button').forEach(function(button){button.addEventListener('click',function(){filter=button.dataset.filter;render();});});
  el('boardSearch').addEventListener('input',render);
  document.querySelectorAll('.match-follow').forEach(function(button){button.addEventListener('click',function(){FT.toggleFav(button.dataset.fav);});});
  el('boardReset').addEventListener('click',function(){filter='all';el('boardSearch').value='';render();el('boardFilters').querySelector('button').focus();});
  window.addEventListener('fantrade:statechange',render);render();
})();
'''

DIVISIONS_HTML = '<main><div class="secondary-page divisions-page">' + intro('Find your division.', 'Follow your club’s place in the competition.', '<a class="quiet-button" href="leaderboard.html">Leaderboard</a>') + '''
<section class="division-standing"><p class="quiet-label">Your club</p><h2 id="divisionClub"></h2><p id="divisionStanding"></p></section>
<section class="division-tiers" aria-label="Division tiers">
<article class="division-tier" data-division="Apex"><span class="tier-number">01</span><div><h2>Apex <span class="tier-current" hidden>Your division</span></h2><p>Ranks 1–150 worldwide</p></div><div class="tier-share"><b>50%</b><span>of prize pool</span></div></article>
<article class="division-tier" data-division="Contender"><span class="tier-number">02</span><div><h2>Contender <span class="tier-current" hidden>Your division</span></h2><p>Ranks 151–500</p></div><div class="tier-share"><b>30%</b><span>of prize pool</span></div></article>
<article class="division-tier" data-division="Challenger"><span class="tier-number">03</span><div><h2>Challenger &amp; Rising Star <span class="tier-current" hidden>Your division</span></h2><p>Ranks 501+ and academy formations</p></div><div class="tier-share"><b>20%</b><span>of prize pool</span></div></article>
</section>
<section class="division-guide"><h2>How your club scores</h2><div class="division-steps">
<div><span>01</span><h3>Player performance</h3><p>Goals, assists, clean sheets and defensive actions contribute to your points.</p></div>
<div><span>02</span><h3>Your captain</h3><p>The captain’s armband applies a 1.5× weighting to their contribution.</p></div>
<div><span>03</span><h3>Team synergy</h3><p>Player links and a compatible coach add to your club’s multiplier.</p></div>
<div><span>04</span><h3>Round settlement</h3><p>Final match results determine points and rewards for the round.</p></div>
</div><div class="division-actions"><a class="app-primary" href="clubs.html">Open your club</a><a class="quiet-button" href="how-it-works.html#rules">Read the scoring rules</a></div></section>
</div></main>'''

DIVISIONS_JS = r'''
(function(){function render(){var club=FT.getState().club,division=club.division||'Challenger';document.getElementById('divisionClub').textContent=club.name;document.getElementById('divisionStanding').textContent=division+' division'+(club.rank?' · Rank #'+club.rank:'');document.querySelectorAll('.division-tier').forEach(function(row){var active=row.dataset.division===division||row.dataset.division==='Challenger'&&division==='Rising Star';row.classList.toggle('current',active);row.querySelector('.tier-current').hidden=!active;});}render();window.addEventListener('fantrade:statechange',render);})();
'''
