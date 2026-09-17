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
          actualVal = stats.teamWon === true;
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
        // Default to failure if unresolvable
        isSuccess = false;
        explanation = `No conclusive event or statistic recorded for '${metric}'.`;
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
