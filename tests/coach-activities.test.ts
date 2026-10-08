import {describe,it,expect,vi} from 'vitest';
import {supportsActivity} from '../src/domain/activity-rules.js';
import {FanPlayEvaluationService,EvaluationInput} from '../src/services/evaluation.service.js';
import {FanPlayService} from '../src/services/fanplay.service.js';
const evaluator=new FanPlayEvaluationService();
const input=(metric:string,value:any= true,op:any='eq'):EvaluationInput=>({optionId:'opt',label:'Coach activity',category:'Coaching',predictionType:'BOOLEAN',successFP:100,failureFP:-50,stakedShares:2,assetId:'coach',assetType:'COACH',evaluationRule:{metric,op,value},coachContext:{club:'Arsenal',homeTeam:'Arsenal FC',awayTeam:'Chelsea',homeScore:2,awayScore:0,final:true}});
const sub=(team:string,minute:number):any=>({matchId:'match',minute,eventType:'SUBSTITUTION',teamId:team});
describe('Role-specific activities',()=>{
 it('separates coach decisions from player performance and rejects malformed rules',()=>{
  expect(supportsActivity('COACH',{metric:'goals',op:'gte',value:1})).toBe(false);
  expect(supportsActivity('PLAYER',{metric:'substitutions',op:'gte',value:3})).toBe(false);
  expect(supportsActivity('COACH','bad json')).toBe(false);
  expect(supportsActivity('COACH',{metric:'team_won',op:'eq',value:true})).toBe(true);
 });
 it('uses the coach team’s final score without pretending the coach has player stats',()=>{
  expect(evaluator.evaluateOption(input('team_won'),null,[])).toMatchObject({result:'SUCCESS',optionContributionFP:200});
  expect(evaluator.evaluateOption(input('clean_sheet'),null,[]).result).toBe('SUCCESS');
  const away=input('team_won');away.coachContext!.club='Chelsea';expect(evaluator.evaluateOption(away,null,[]).result).toBe('FAILURE');
 });
 it('scopes substitutions to the right team and waits on incomplete event coverage',()=>{
  expect(evaluator.evaluateOption(input('substitutions',3,'gte'),null,[sub('Chelsea',20),sub('Arsenal',50)]).result).toBe('PENDING');
  expect(evaluator.evaluateOption(input('substitutions_before_60',1,'gte'),null,[sub('Arsenal',59)]).result).toBe('SUCCESS');
  expect(evaluator.evaluateOption(input('substitutions_before_60',1,'gte'),null,[sub('Arsenal',60)]).result).toBe('PENDING');
  const marker:any={matchId:'match',minute:90,eventType:'TEAM_RESULT',teamId:'Arsenal',metadata:{completeEventTypes:['SUBSTITUTION']}};
  expect(evaluator.evaluateOption(input('substitutions',3,'gte'),null,[sub('Arsenal',50),marker]).result).toBe('FAILURE');
 });
 it('requires confirmed participation for the selected player',()=>{
  const pick=input('player_used');pick.evaluationRule.playerId='saka';
  expect(evaluator.evaluateOption(pick,null,[]).result).toBe('PENDING');
  const event:any={matchId:'match',minute:90,eventType:'MINUTES_PLAYED',teamId:'Arsenal',playerId:'saka',value:90,metadata:{participationConfirmed:true,started:true}};
  expect(evaluator.evaluateOption(pick,null,[event]).result).toBe('SUCCESS');
  event.teamId='Chelsea';expect(evaluator.evaluateOption(pick,null,[event]).result).toBe('PENDING');
 });
 it('filters wrongly published coach options from the server catalogue',async()=>{
  const db:any={fanPlayOption:{findMany:vi.fn().mockResolvedValue([{id:'goal',asset:{type:'COACH'},evaluationRule:JSON.stringify({metric:'goals',op:'gte',value:1})},{id:'win',asset:{type:'COACH'},evaluationRule:JSON.stringify({metric:'team_won',op:'eq',value:true})}])}};
  expect((await new FanPlayService(db).getOptions({assetId:'coach'})).map(o=>o.id)).toEqual(['win']);
 });
 it('rejects a coach goal prediction before a preview or any reservation',async()=>{
  const db:any={matchFixture:{findUnique:vi.fn().mockResolvedValue({id:'match',homeTeam:'Arsenal',awayTeam:'Chelsea'})},asset:{findUnique:vi.fn().mockResolvedValue({id:'coach',type:'COACH',symbol:'FARTA',coachProfile:{club:'Arsenal'}})},fanPlayOption:{findMany:vi.fn().mockResolvedValue([{assetId:'coach',matchId:'match',status:'ACTIVE',evaluationRule:JSON.stringify({metric:'goals',op:'gte',value:1})}])}};
  await expect(new FanPlayService(db).previewFanPlay({assetSymbol:'FARTA',matchId:'match',selectedOptionIds:['goal'],stakedShares:1} as any)).rejects.toMatchObject({code:'INVALID_SELECTION'});
 });
});
