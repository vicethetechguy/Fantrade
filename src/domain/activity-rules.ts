import { AssetType, EvaluationRule } from './types.js';
const coachMetrics = new Set(['team_result','teamresult','team_won','win','clean_sheet','substitutions','substitutions_before_60','player_used','player_started']);
const playerMetrics = new Set(['goals','goal','assists','assist','shots','shot','shotsontarget','shots_on_target','keypasses','key_passes','key_pass','yellowcards','yellow_card','yellow','redcards','red_card','red','fouls','foulscommitted','minutes','minutesplayed','team_result','teamresult','team_won','win']);
export function activityRule(value: string | EvaluationRule): EvaluationRule | null {
  try { const rule = typeof value === 'string' ? JSON.parse(value) : value;
    return rule && typeof rule.metric === 'string' && ['gte','lte','eq','gt','lt','between','contains','avoid'].includes(rule.op) ? rule : null;
  } catch { return null; }
}
export function supportsActivity(type: AssetType, value: string | EvaluationRule): boolean {
  const rule=activityRule(value);
  return !!rule && (type==='COACH'?coachMetrics:playerMetrics).has(rule.metric.toLowerCase()) &&
    (!['player_used','player_started'].includes(rule.metric.toLowerCase()) || typeof rule.playerId==='string' && !!rule.playerId);
}
