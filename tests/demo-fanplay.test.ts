import {describe,it,expect,vi} from 'vitest';
import {FanPlayService} from '../src/services/fanplay.service.js';
describe('Demo simulation',()=>{
 it('refuses ordinary accounts before touching entries',async()=>{
  const find=vi.fn();const db:any={user:{findUnique:vi.fn().mockResolvedValue({email:'fan@example.com'})},fanPlay:{findUnique:find}};
  await expect(new FanPlayService(db).simulateDemoFanPlay('u','e')).rejects.toMatchObject({code:'DEMO_ONLY'});expect(find).not.toHaveBeenCalled();
 });
 it('settles a demo entry and releases shares without a ledger payout',async()=>{
  const update=vi.fn().mockResolvedValue({status:'SETTLED'}),release=vi.fn();
  const db:any={user:{findUnique:vi.fn().mockResolvedValue({email:'demo@fantrade.com'})},fanPlay:{findUnique:vi.fn().mockResolvedValue({userId:'u',status:'ACTIVE',reservationId:'r',stakedShares:10,selections:[{id:'p',successFP:5,failureFP:-2}]}),updateMany:vi.fn().mockResolvedValue({count:1}),update},fanPlaySelection:{update:vi.fn()}};
  const service=new FanPlayService(db);(service as any).ownershipService={releaseShares:release};
  await service.simulateDemoFanPlay('u','e');expect(release).toHaveBeenCalledOnce();expect(db.fanPlay.updateMany.mock.calls[0][0].data.ftrSettlement).toBe(0);expect(db.fanPlaySelection.update.mock.calls[0][0].data.explanation).toContain('Demo simulation');
 });
 it('cannot later pay real settlement for a simulated entry',async()=>{
  const db:any={fanPlay:{findUnique:vi.fn().mockResolvedValue({status:'SETTLED',selections:[{explanation:'Demo simulation — no FTR payout'}],settlement:null})}};
  expect(await new FanPlayService(db).settleFanPlay('e')).toMatchObject({alreadySettled:true,settlement:null});
 });
 it('does not release or pay twice when the entry has already ended',async()=>{
  const release=vi.fn();const db:any={user:{findUnique:vi.fn().mockResolvedValue({email:'demo@fantrade.com'})},fanPlay:{findUnique:vi.fn().mockResolvedValue({userId:'u',status:'SETTLED'})}};
  const service=new FanPlayService(db);(service as any).ownershipService={releaseShares:release};await service.simulateDemoFanPlay('u','e');expect(release).not.toHaveBeenCalled();
 });
});
