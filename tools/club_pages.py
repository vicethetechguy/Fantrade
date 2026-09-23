"""Club overview and editor, sharing an accessible formation preview."""
from app_design import intro

CLUB_HTML = '<main><div class="secondary-page clubs-page">' + intro('Your club', 'A team to call your own.') + '''
<header class="club-heading" id="clubHeading"><span class="club-crest" id="clubCrest" aria-hidden="true"></span><div><h2 id="clName"></h2><p id="clubStadium"></p></div><a class="quiet-button" href="club-builder.html">Edit club</a></header>
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
    '4-3-3':[[['LW','FVJR'],['ST','FHLND'],['RW','FSAKA']],[['CM','$Rice'],['CAM','FBRN'],['CM','$Odegaard']],[['LB','$Davies'],['CB','$VanDijk'],['CB','FSALI'],['RB','$White']],[['GK','$Raya']]],
    '4-4-2':[[['ST','FHLND'],['ST','FJACK']],[['LM','FVJR'],['CM','$Rice'],['CM','FBRN'],['RM','FSAKA']],[['LB','$Davies'],['CB','$VanDijk'],['CB','FSALI'],['RB','$White']],[['GK','$Raya']]],
    '3-5-2':[[['ST','FHLND'],['ST','FVJR']],[['LWB','$Davies'],['CM','$Rice'],['CM','$Odegaard'],['CAM','FBRN'],['RWB','FSAKA']],[['CB','$VanDijk'],['CB','FSALI'],['CB','$Gabriel']],[['GK','$Raya']]],
    '4-2-3-1':[[['ST','FHLND']],[['LW','FVJR'],['CAM','FBRN'],['RW','FSAKA']],[['DM','$Rice'],['DM','$Odegaard']],[['LB','$Davies'],['CB','$VanDijk'],['CB','FSALI'],['RB','$White']],[['GK','$Raya']]]
  };
  function esc(value){var n=document.createElement('span');n.textContent=value;return n.innerHTML.replace(/"/g,'&quot;');}
  function initials(name){return name.trim().split(/\s+/).map(function(w){return w[0]||'';}).join('').slice(0,3).toUpperCase();}
  function colour(club){var value=club.color||(club.colors||[])[0]||'#1800ad';return /^#[a-f0-9]{3,8}$/i.test(value)?value:'#1800ad';}
  function meta(symbol){return (typeof ASSETS!=='undefined'?ASSETS:[]).filter(function(a){return a.t===symbol;})[0]||{};}
  function groupForSlot(label){
    if(label==='GK') return 'GK';
    if(['LB','CB','RB','LWB','RWB'].indexOf(label)>-1) return 'DEF';
    if(['DM','CM','CAM','LM','RM'].indexOf(label)>-1) return 'MID';
    return 'FWD';
  }
  function ownedPlayers(){
    var holdings=FT.getState().holdings||{};
    return Object.keys(holdings).filter(function(symbol){
      var h=holdings[symbol];return h&&h.shares>0&&!h.c;
    }).map(function(symbol){
      var h=holdings[symbol],m=meta(symbol);
      return {symbol:symbol,name:h.n||m.n||symbol.slice(1),pos:m.pos||'FWD'};
    });
  }
  function pickPlayer(slot,pool,used){
    var wanted=groupForSlot(slot),pick=null;
    pick=pool.filter(function(p){return !used[p.symbol]&&p.pos===wanted;})[0];
    if(!pick&&wanted!=='GK') pick=pool.filter(function(p){return !used[p.symbol]&&p.pos!=='GK';})[0];
    if(pick) used[pick.symbol]=true;
    return pick;
  }
  function playerSlot(label,pick){
    if(!pick) return '<div class="formation-player empty"><span>'+esc(label)+'</span><i>Empty</i><b>Own shares</b></div>';
    return '<div class="formation-player"><span>'+esc(label)+'</span>'+playerPhoto(pick.symbol,pick.name)+'<b>'+esc(pick.name.replace(/ .*/,''))+'</b></div>';
  }
  function pitch(shape){
    var pool=ownedPlayers(),used={},rows=forms[shape]||forms['4-3-3'];
    var html=rows.map(function(row){return '<div class="formation-row">'+row.map(function(p){return playerSlot(p[0],pickPlayer(p[0],pool,used));}).join('')+'</div>';}).join('');
    var state=FT.getState(),coachSymbol=state.club.coach||'FARTA',coach=state.holdings[coachSymbol];
    if(coach&&coach.shares>0){html+='<div class="formation-coach">'+playerPhoto(coachSymbol,coach.n||coachSymbol.slice(1))+'<div><span>Coach</span><b>'+esc(coach.n||coachSymbol)+'</b></div></div>';}
    else{html+='<div class="formation-coach empty"><span class="empty-coach">Coach</span><div><span>Coach</span><b>Own a coach share</b></div></div>';}
    var bench=pool.filter(function(p){return !used[p.symbol];}).slice(0,4);
    html+='<p class="formation-bench-label">Owned bench</p><div class="formation-bench">';
    html+=bench.length?bench.map(function(p){return '<div class="formation-player">'+playerPhoto(p.symbol,p.name)+'<b>'+esc(p.name.replace(/ .*/,''))+'</b></div>';}).join(''):'<p class="quiet-note">No extra owned players yet.</p>';
    return html+'</div>';
  }
  function renderClub(){
    var state=FT.getState(),club=state.club;
    el('clName').textContent=club.name;el('clubStadium').textContent=club.stadium||'Your home ground';
    el('clubCrest').textContent=initials(club.name);el('clubCrest').style.background=colour(club);
    el('clubCrest').style.color=colour(club).toLowerCase()==='#e8e8e8'?'#050505':'#fff';
    el('clFp').textContent=Number(club.fp||0).toLocaleString('en-US');el('clRank').textContent=club.rank?'#'+club.rank:'—';
    el('clDivision').textContent=club.division||'Challenger';el('clBoost').textContent='+'+Number(club.boost||0).toFixed(1)+'%';
    el('clubShape').textContent=club.formation;el('clubPitch').innerHTML=pitch(club.formation);
    var starterSlots=(forms[club.formation]||forms['4-3-3']).flat().length;
    var held=Math.min(starterSlots,ownedPlayers().length);
    el('clubOwnership').textContent=held+' of '+starterSlots+' line-up slots filled from owned Activity Shares. Empty slots need a claimed or bought player share.';
  }
  if(el('clubHeading')){renderClub();window.addEventListener('fantrade:statechange',renderClub);return;}
  // A manager has one club, made at onboarding, so the builder only ever edits.
  var club=FT.getState().club;
  var shape=club.formation,hex=colour(club),colourName=club.colorName||'Indigo';
  el('clubNameInput').value=club.name;el('clubStadiumInput').value=club.stadium||'';
  function preview(){
    var name=el('clubNameInput').value.trim()||'Your club';
    el('previewName').textContent=name;el('previewStadium').textContent=el('clubStadiumInput').value.trim()||'Your home ground';
    el('previewCrest').textContent=initials(name);el('previewCrest').style.background=hex;
    el('previewCrest').style.color=hex.toLowerCase()==='#e8e8e8'?'#050505':'#fff';
    el('previewShape').textContent=shape;el('builderPitch').innerHTML=pitch(shape);
    el('clubForms').querySelectorAll('button').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.shape===shape));});
    el('clubColours').querySelectorAll('button').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.hex.toLowerCase()===hex.toLowerCase()));});
    el('saveClubBtn').textContent='Save changes';
  }
  ['clubNameInput','clubStadiumInput'].forEach(function(id){el(id).addEventListener('input',function(){el('clubSaveStatus').textContent='';preview();});});
  el('clubForms').querySelectorAll('button').forEach(function(b){b.addEventListener('click',function(){shape=b.dataset.shape;el('clubSaveStatus').textContent='';preview();});});
  el('clubColours').querySelectorAll('button').forEach(function(b){b.addEventListener('click',function(){hex=b.dataset.hex;colourName=b.dataset.colour;el('clubSaveStatus').textContent='';preview();});});
  el('clubForm').addEventListener('submit',function(event){
    event.preventDefault();var name=el('clubNameInput').value.trim();
    if(name.length<2){el('clubSaveStatus').textContent='Enter a club name with at least two letters.';el('clubNameInput').focus();return;}
    var data={name:name,stadium:el('clubStadiumInput').value.trim()||'Unnamed ground',formation:shape,color:hex,colors:[hex,'#111310'],colorName:colourName};
    try{FT.saveClub(data);el('clubSaveStatus').textContent='Saved. Your club is ready to view.';preview();}catch(error){el('clubSaveStatus').textContent=error.message;}
  });
  preview();
})();
'''
