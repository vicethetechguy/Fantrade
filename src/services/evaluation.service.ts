import { clubKey } from '../domain/fixture-eligibility.js';
import { supportsActivity } from '../domain/activity-rules.js';
import {
  OptionEvaluationResult,
  EvaluationRule,
  NormalizedFootballEvent,
  NormalizedPlayerStats,
} from '../domain/types.js';

export interface EvaluationInput {
  optionId: string;
  label: string;
  category: string;
  predictionType: string;
  successFP: number;
  failureFP: number;
  evaluationRule: EvaluationRule;
  assetId?: string;
  assetType?: 'PLAYER' | 'COACH';
  coachContext?: {club:string;homeTeam:string;awayTeam:string;homeScore:number;awayScore:number;final:boolean};
  stakedShares: number;
}

export interface EvaluationResult {
  optionId: string;
  result: OptionEvaluationResult;
  optionResultFP: number;
  optionContributionFP: number;
  explanation: string;
}

export class FanPlayEvaluationService {
  /**
   * Deterministically evaluates a single prediction option against player stats and match events.
   */
  evaluateOption(
    input: EvaluationInput,
    stats: NormalizedPlayerStats | null,
    events: NormalizedFootballEvent[]
  ): EvaluationResult {
    if(input.assetType==='COACH') return this.evaluateCoach(input,events);
    const { rule, successFP, failureFP, stakedShares } = {
      rule: input.evaluationRule,
      successFP: input.successFP,
      failureFP: input.failureFP,
      stakedShares: input.stakedShares,
    };

    let isSuccess = false;
    let explanation = '';

    const metric = rule.metric?.toLowerCase() || '';
    const op = rule.op;
    const targetVal = rule.value;

    // 1. Metric evaluation against normalized player stats
    if (stats) {
      let actualVal: number | boolean | undefined = undefined;

      switch (metric) {
        case 'goals':
        case 'goal':
          actualVal = stats.goals;
          break;
        case 'assists':
        case 'assist':
          actualVal = stats.assists;
          break;
        case 'shots':
        case 'shot':
          actualVal = stats.shots;
          break;
        case 'shotsontarget':
        case 'shots_on_target':
          actualVal = stats.shotsOnTarget;
          break;
        case 'keypasses':
        case 'key_passes':
        case 'key_pass':
          actualVal = stats.keyPasses;
          break;
        case 'yellowcards':
        case 'yellow_card':
        case 'yellow':
          actualVal = stats.yellowCards;
          break;
        case 'redcards':
        case 'red_card':
        case 'red':
          actualVal = stats.redCards;
          break;
        case 'fouls':
        case 'foulscommitted':
          actualVal = stats.foulsCommitted;
          break;
        case 'team_result':
        case 'teamresult':
        case 'team_won':
        case 'win':
          actualVal = stats.teamWon;
          break;
        case 'minutes':
        case 'minutesplayed':
          actualVal = stats.minutesPlayed;
          break;
        default:
          break;
      }

      if (actualVal !== undefined) {
        if (typeof actualVal === 'boolean') {
          isSuccess = Boolean(targetVal) === actualVal;
          explanation = `Team result condition was ${actualVal ? 'met' : 'not met'} (expected: ${targetVal}).`;
        } else if (typeof actualVal === 'number') {
          const numTarget = typeof targetVal === 'number' ? targetVal : Number(targetVal || 0);

          switch (op) {
            case 'gte':
              isSuccess = actualVal >= numTarget;
              explanation = `Recorded ${actualVal} ${metric} (target: ${numTarget}+).`;
              break;
            case 'lte':
              isSuccess = actualVal <= numTarget;
              explanation = `Recorded ${actualVal} ${metric} (target: ${numTarget} or fewer).`;
              break;
            case 'eq':
              isSuccess = actualVal === numTarget;
              explanation = `Recorded exactly ${actualVal} ${metric} (target: ${numTarget}).`;
              break;
            case 'gt':
              isSuccess = actualVal > numTarget;
              explanation = `Recorded ${actualVal} ${metric} (target: > ${numTarget}).`;
              break;
            case 'lt':
              isSuccess = actualVal < numTarget;
              explanation = `Recorded ${actualVal} ${metric} (target: < ${numTarget}).`;
              break;
            case 'between': {
              const min = rule.min ?? 0;
              const max = rule.max ?? 100;
              isSuccess = actualVal >= min && actualVal <= max;
              explanation = `Recorded ${actualVal} ${metric} (target range: ${min}-${max}).`;
              break;
            }
            case 'avoid':
              isSuccess = actualVal === 0;
              explanation = actualVal === 0 ? `Successfully avoided ${metric}.` : `Incurred ${actualVal} ${metric}.`;
              break;
            default:
              isSuccess = actualVal >= numTarget;
              explanation = `Recorded ${actualVal} ${metric}.`;
          }
        }
      }
    }

    // 2. Fallback / Event-stream evaluation if stats did not resolve or op is 'contains' / 'avoid'
    if (explanation === '') {
      const playerEvents = events.filter((e) => !input.assetId || e.playerId === input.assetId);

      if (op === 'contains' || op === 'avoid') {
        const matchingEvents = playerEvents.filter((e) => {
          const typeStr = e.eventType.toLowerCase();
          return typeStr.includes(metric) || metric.includes(typeStr);
        });

        if (op === 'contains') {
          isSuccess = matchingEvents.length > 0;
          explanation = isSuccess
            ? `Event occurred at minute ${matchingEvents[0].minute}.`
            : `Event ${metric} did not occur in match.`;
        } else {
          // avoid
          isSuccess = matchingEvents.length === 0;
          explanation = isSuccess
            ? `Player avoided ${metric}.`
            : `Player incurred ${metric} at minute ${matchingEvents[0].minute}.`;
        }
      } else {
        return this.pending(input, `Awaiting verified data for '${metric}'.`);
      }
    }

    const result: OptionEvaluationResult = isSuccess ? 'SUCCESS' : 'FAILURE';
    const optionResultFP = isSuccess ? successFP : failureFP;
    const optionContributionFP = optionResultFP * stakedShares;

    return {
      optionId: input.optionId,
      result,
      optionResultFP,
      optionContributionFP,
      explanation,
    };
  }

  private pending(input: EvaluationInput, explanation: string): EvaluationResult {
    return {optionId:input.optionId,result:'PENDING',optionResultFP:0,optionContributionFP:0,explanation};
  }

  private evaluateCoach(input: EvaluationInput, events: NormalizedFootballEvent[]): EvaluationResult {
    const ctx=input.coachContext, rule=input.evaluationRule, metric=rule.metric.toLowerCase();
    if(!ctx || !ctx.final || !supportsActivity('COACH',rule)) return this.pending(input,'Awaiting a verified coach activity and final fixture.');
    const home=clubKey(ctx.club)===clubKey(ctx.homeTeam),away=clubKey(ctx.club)===clubKey(ctx.awayTeam);
    if(!home && !away) return this.pending(input,'The coach team could not be matched to this fixture.');
    const own=home?ctx.homeScore:ctx.awayScore,opponent=home?ctx.awayScore:ctx.homeScore;
    // Never interpret another team's events as this coach's decisions. Providers can
    // supply a canonical team name in teamId or metadata.teamName.
    const teamEvents=events.filter(e=>clubKey(e.metadata?.teamName || e.teamId)===clubKey(ctx.club));
    let actual:number|boolean|undefined;
    if(['team_result','teamresult','team_won','win'].includes(metric)) actual=own>opponent;
    else if(metric==='clean_sheet') actual=opponent===0;
    else if(metric.startsWith('substitutions')) {
      const subs=teamEvents.filter(e=>e.eventType==='SUBSTITUTION' && (metric!=='substitutions_before_60' || e.minute<60));
      const complete=teamEvents.some(e=>Array.isArray(e.metadata?.completeEventTypes) && e.metadata.completeEventTypes.includes('SUBSTITUTION'));
      // Positive thresholds can be proved by observed events; absence needs complete coverage.
      const threshold=Number(rule.value);
      const proven=(rule.op==='gte'&&subs.length>=threshold)||(rule.op==='gt'&&subs.length>threshold)||(rule.op==='contains'&&subs.length>0);
      if(!complete&&!proven)return this.pending(input,'Awaiting complete team substitution data.');
      actual=subs.length;
    } else if(['player_used','player_started'].includes(metric)) {
      const participation=teamEvents.find(e=>e.eventType==='MINUTES_PLAYED' && e.playerId===rule.playerId && e.metadata?.participationConfirmed===true);
      if(!participation || (metric==='player_started' && typeof participation.metadata?.started!=='boolean'))return this.pending(input,'Awaiting confirmed player selection data.');
      actual=metric==='player_started'?participation.metadata!.started:Number(participation.value)>0;
    }
    if(actual===undefined)return this.pending(input,'Awaiting verified coach data.');
    let success=false;
    if(typeof actual==='boolean'){
      if(rule.op!=='eq'||typeof rule.value!=='boolean')return this.pending(input,'Invalid team-result rule.');
      success=actual===rule.value;
    }else{
      const target=Number(rule.value);
      switch(rule.op){case 'gte':success=actual>=target;break;case 'gt':success=actual>target;break;case 'lte':success=actual<=target;break;case 'lt':success=actual<target;break;case 'eq':success=actual===target;break;case 'between':success=actual>=(rule.min??0)&&actual<=(rule.max??Infinity);break;case 'contains':success=actual>0;break;case 'avoid':success=actual===0;break;}
    }
    const fp=success?input.successFP:input.failureFP;
    return {optionId:input.optionId,result:success?'SUCCESS':'FAILURE',optionResultFP:fp,optionContributionFP:fp*input.stakedShares,explanation:`Verified coach activity: ${metric} = ${actual}.`};
  }

  /**
   * Evaluates all selections for a FanPlay position and computes aggregated results.
   */
  evaluateFanPlay(
    selections: EvaluationInput[],
    stats: NormalizedPlayerStats | null,
    events: NormalizedFootballEvent[]
  ) {
    const evaluatedSelections = selections.map((sel) => this.evaluateOption(sel, stats, events));

    const totalFP = evaluatedSelections.reduce((sum, s) => sum + s.optionContributionFP, 0);
    // 1,000 FP = 1 $FTR (§4, §31, §33)
    const ftrSettlement = totalFP / 1000;

    return {
      selections: evaluatedSelections,
      totalFP,
      ftrSettlement,
    };
  }
}
