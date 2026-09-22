"""Club overview and editor, sharing an accessible formation preview."""
from app_design import intro

CLUB_HTML = '<main><div class="secondary-page clubs-page">' + intro('Your clubs', 'A team to call your own.', '<a class="app-primary" href="club-builder.html?new=1">Create club</a>') + '''
<div class="club-selector" id="clubRail" role="group" aria-label="Choose your club"></div>
<header class="club-heading"><span class="club-crest" id="clubCrest" aria-hidden="true"></span><div><h2 id="clName"></h2><p id="clubStadium"></p></div><a class="quiet-button" href="club-builder.html">Edit club</a></header>
<dl class="club-stats"><div><dt>Season points</dt><dd id="clFp"></dd></div><div><dt>Global rank</dt><dd id="clRank"></dd></div><div><dt>Division</dt><dd id="clDivision"></dd></div><div><dt>Club boost</dt><dd id="clBoost"></dd></div></dl>
<div class="club-layout"><section><div class="section-heading"><h2>Line-up</h2><span class="quiet-label" id="clubShape"></span></div><div class="formation-preview" id="clubPitch"></div><p class="quiet-note" id="clubOwnership"></p></section>
<aside class="club-next"><h2>Ready for matchday?</h2><p>Choose eligible shares and build your predictions in FanPlay.</p><a class="app-primary" href="fanplay.html">Play FanPlay</a><div class="club-links"><a href="liveboard.html">Follow the live board <span aria-hidden="true">↗</span></a><a href="leaderboard.html">See the leaderboard <span aria-hidden="true">↗</span></a><a href="divisions.html">Understand divisions <span aria-hidden="true">↗</span></a></div></aside></div>
</div></main>'''

BUILDER_HTML = '<main><div class="secondary-page builder-page">' + '<a class="back-btn" href="clubs.html" aria-label="Back to your clubs">Back</a>' + intro('Make it your club.', 'Choose a name, a colour and a shape.') + '''
<div class="builder-layout"><form id="clubForm" class="club-form">
<h2>Your club identity</h2>
<label for="clubNameInput">Club name</label><input id="clubNameInput" name="clubName" autocomplete="off" placeholder="Give your club a name" minlength="2" maxlength="40" required>
<label for="clubStadiumInput">Stadium <span>Optional</span></label><input id="clubStadiumInput" name="stadium" autocomplete="off" placeholder="Your home ground" maxlength="60">
<fieldset><legend>Club colour</legend><div class="club-swatches" id="clubColours">
<button type="button" data-colour="Indigo" data-hex="#1800ad" aria-label="Indigo" aria-pressed="true" style="--swatch:#1800ad"></button>
<button type="button" data-colour="Amber" data-hex="#ff6a1f" aria-label="Amber" aria-pressed="false" style="--swatch:#ff6a1f"></button>
<button type="button" data-colour="Blue" data-hex="#4da3ff" aria-label="Blue" aria-pressed="false" style="--swatch:#4da3ff"></button>
<button type="button" data-colour="Silver" data-hex="#e8e8e8" aria-label="Silver" aria-pressed="false" style="--swatch:#e8e8e8"></button>
<button type="button" data-colour="Violet" data-hex="#b14dff" aria-label="Violet" aria-pressed="false" style="--swatch:#b14dff"></button>
</div></fieldset>
<fieldset><legend>Formation</legend><div class="club-formations" id="clubForms"><button type="button" data-shape="4-3-3" aria-pressed="true">4-3-3</button><button type="button" data-shape="4-4-2" aria-pressed="false">4-4-2</button><button type="button" data-shape="3-5-2" aria-pressed="false">3-5-2</button><button type="button" data-shape="4-2-3-1" aria-pressed="false">4-2-3-1</button></div></fieldset>
<p class="quiet-note">Preview your formation here. Choose eligible player shares when you enter FanPlay.</p>
<p id="clubSaveStatus" class="club-save-status" role="status"></p><button class="app-primary" type="submit" id="saveClubBtn">Save club</button>
</form><section class="builder-preview"><div class="section-heading"><h2>Formation preview</h2><span class="quiet-label" id="previewShape"></span></div><div class="club-preview-identity"><span class="club-crest" id="previewCrest" aria-hidden="true"></span><div><b id="previewName"></b><p id="previewStadium"></p></div></div><div class="formation-preview" id="builderPitch"></div></section></div>
</div></main>'''

JS = r'''
(function(){
  var el=function(id){return document.getElementById(id);};
  var forms={
    '4-3-3':[[['LW','$Vinicius'],['ST','$Haaland'],['RW','$Saka']],[['CM','$Rice'],['CAM','$Bruno'],['CM','$Odegaard']],[['LB','$Davies'],['CB','$VanDijk'],['CB','$Saliba'],['RB','$White']],[['GK','$Raya']]],
    '4-4-2':[[['ST','$Haaland'],['ST','$Jackson']],[['LM','$Vinicius'],['CM','$Rice'],['CM','$Bruno'],['RM','$Saka']],[['LB','$Davies'],['CB','$VanDijk'],['CB','$Saliba'],['RB','$White']],[['GK','$Raya']]],
    '3-5-2':[[['ST','$Haaland'],['ST','$Vinicius']],[['LWB','$Davies'],['CM','$Rice'],['CM','$Odegaard'],['CAM','$Bruno'],['RWB','$Saka']],[['CB','$VanDijk'],['CB','$Saliba'],['CB','$Gabriel']],[['GK','$Raya']]],
    '4-2-3-1':[[['ST','$Haaland']],[['LW','$Vinicius'],['CAM','$Bruno'],['RW','$Saka']],[['DM','$Rice'],['DM','$Odegaard']],[['LB','$Davies'],['CB','$VanDijk'],['CB','$Saliba'],['RB','$White']],[['GK','$Raya']]]
  };
  function esc(value){var n=document.createElement('span');n.textContent=value;return n.innerHTML.replace(/"/g,'&quot;');}
  function initials(name){return name.trim().split(/\s+/).map(function(w){return w[0]||'';}).join('').slice(0,3).toUpperCase();}
  function colour(club){var value=club.color||(club.colors||[])[0]||'#1800ad';return /^#[a-f0-9]{3,8}$/i.test(value)?value:'#1800ad';}
  function pitch(shape){
    var html=(forms[shape]||forms['4-3-3']).map(function(row){return '<div class="formation-row">'+row.map(function(p){return '<div class="formation-player"><span>'+p[0]+'</span>'+playerPhoto(p[1],p[1].slice(1))+'<b>'+p[1].slice(1)+'</b></div>';}).join('')+'</div>';}).join('');
    var coach=fresh?'$Arteta':FT.getState().club.coach||'$Arteta';
    html+='<div class="formation-coach">'+playerPhoto(coach,coach.slice(1))+'<div><span>Coach</span><b>'+esc(coach)+'</b></div></div>';
    html+='<p class="formation-bench-label">Bench preview</p><div class="formation-bench">';
    ['$Alisson','$Gabriel','$Pedri','$Musiala'].forEach(function(symbol){html+='<div class="formation-player">'+playerPhoto(symbol,symbol.slice(1))+'<b>'+symbol.slice(1)+'</b></div>';});
    return html+'</div>';
  }
  function renderClub(){
    var state=FT.getState(),club=state.club;
    el('clubRail').innerHTML=state.clubs.map(function(c){return '<button type="button" data-club="'+esc(c.id)+'" aria-pressed="'+(c.id===state.activeClub)+'">'+esc(c.name)+'</button>';}).join('');
    el('clubRail').querySelectorAll('button').forEach(function(button){button.addEventListener('click',function(){FT.switchClub(button.dataset.club);var active=el('clubRail').querySelector('[aria-pressed=true]');if(active)active.focus();});});
    el('clName').textContent=club.name;el('clubStadium').textContent=club.stadium||'Your home ground';
    el('clubCrest').textContent=initials(club.name);el('clubCrest').style.background=colour(club);
    el('clubCrest').style.color=colour(club).toLowerCase()==='#e8e8e8'?'#050505':'#fff';
    el('clFp').textContent=Number(club.fp||0).toLocaleString('en-US');el('clRank').textContent=club.rank?'#'+club.rank:'—';
    el('clDivision').textContent=club.division||'Challenger';el('clBoost').textContent='+'+Number(club.boost||0).toFixed(1)+'%';
    el('clubShape').textContent=club.formation;el('clubPitch').innerHTML=pitch(club.formation);
    var held=0;(forms[club.formation]||forms['4-3-3']).flat().forEach(function(p){if(state.holdings[p[1]]&&state.holdings[p[1]].shares>0)held++;});
    el('clubOwnership').textContent='Formation preview · '+held+' of 11 featured players held. Your eligible shares are confirmed in FanPlay.';
  }
  if(el('clubRail')){renderClub();window.addEventListener('fantrade:statechange',renderClub);return;}
  var fresh=new URLSearchParams(location.search).get('new')==='1',club=FT.getState().club;
  var shape=fresh?'4-3-3':club.formation,hex=fresh?'#1800ad':colour(club),colourName=fresh?'Indigo':club.colorName||'Indigo';
  el('clubNameInput').value=fresh?'':club.name;el('clubStadiumInput').value=fresh?'':club.stadium||'';
  function preview(){
    var name=el('clubNameInput').value.trim()||'Your club';
    el('previewName').textContent=name;el('previewStadium').textContent=el('clubStadiumInput').value.trim()||'Your home ground';
    el('previewCrest').textContent=initials(name);el('previewCrest').style.background=hex;
    el('previewCrest').style.color=hex.toLowerCase()==='#e8e8e8'?'#050505':'#fff';
    el('previewShape').textContent=shape;el('builderPitch').innerHTML=pitch(shape);
    el('clubForms').querySelectorAll('button').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.shape===shape));});
    el('clubColours').querySelectorAll('button').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.hex.toLowerCase()===hex.toLowerCase()));});
    el('saveClubBtn').textContent=fresh?'Create club':'Save changes';
  }
  ['clubNameInput','clubStadiumInput'].forEach(function(id){el(id).addEventListener('input',function(){el('clubSaveStatus').textContent='';preview();});});
  el('clubForms').querySelectorAll('button').forEach(function(b){b.addEventListener('click',function(){shape=b.dataset.shape;el('clubSaveStatus').textContent='';preview();});});
  el('clubColours').querySelectorAll('button').forEach(function(b){b.addEventListener('click',function(){hex=b.dataset.hex;colourName=b.dataset.colour;el('clubSaveStatus').textContent='';preview();});});
  el('clubForm').addEventListener('submit',function(event){
    event.preventDefault();var name=el('clubNameInput').value.trim();
    if(name.length<2){el('clubSaveStatus').textContent='Enter a club name with at least two letters.';el('clubNameInput').focus();return;}
    var data={name:name,stadium:el('clubStadiumInput').value.trim()||'Unnamed ground',formation:shape,color:hex,colors:[hex,'#111310'],colorName:colourName};
    try{if(fresh){FT.createClub(data);fresh=false;history.replaceState(null,'','club-builder.html');}else{FT.saveClub(data);}el('clubSaveStatus').textContent='Saved. Your club is ready to view.';preview();}catch(error){el('clubSaveStatus').textContent=error.message;}
  });
  preview();
})();
'''
