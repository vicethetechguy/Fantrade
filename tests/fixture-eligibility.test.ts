import { describe,it,expect,vi } from 'vitest';
import { FanPlayService } from '../src/services/fanplay.service.js';
import { clubInFixture } from '../src/domain/fixture-eligibility.js';
describe('FanPlay team eligibility',()=>{
 it('accepts the player’s team in either home or away position and handles provider abbreviations',()=>{
  expect(clubInFixture('Manchester City','Man City','Arsenal')).toBe(true);
  expect(clubInFixture('Arsenal FC','Chelsea','Arsenal')).toBe(true);
  expect(clubInFixture('Barcelona Femení','Barcelona Women','Chelsea Women')).toBe(true);
 });
 it('refuses an unrelated fixture in the server preview before calculating predictions',async()=>{
  const options=vi.fn();const db:any={matchFixture:{findUnique:vi.fn().mockResolvedValue({id:'fixture',homeTeam:'Arsenal',awayTeam:'Chelsea'})},asset:{findUnique:vi.fn().mockResolvedValue({id:'asset',symbol:'FMBP',playerProfile:{club:'Real Madrid'}})},fanPlayOption:{findMany:options}};
  const service=new FanPlayService(db);await expect(service.previewFanPlay({assetSymbol:'FMBP',matchId:'fixture',selectedOptionIds:['goal'],stakedShares:1} as any)).rejects.toMatchObject({code:'INVALID_SELECTION'});expect(options).not.toHaveBeenCalled();
 });
 it('rejects unrelated fixtures, unknown clubs and the other gender’s team',()=>{
  expect(clubInFixture('Arsenal','Manchester City','Liverpool')).toBe(false);
  expect(clubInFixture('Arsenal Women','Arsenal','Chelsea')).toBe(false);
  expect(clubInFixture('Club','Club','Arsenal')).toBe(false);
  expect(clubInFixture(undefined,'Arsenal','Chelsea')).toBe(false);
 });
});
