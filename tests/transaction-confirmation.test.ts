import { describe, it, expect, vi } from 'vitest';
import { Prisma } from '@prisma/client';
import { OrderService } from '../src/services/order.service.js';
import { idempotencyMiddleware } from '../src/api/middlewares/idempotency.middleware.js';
import { prisma } from '../src/database/client.js';

describe('Transaction confirmation regressions (isolated, no database writes)', () => {
  it('releases the reservation and rejects an order when matching fails', async () => {
    const failure = new Error('Matching unavailable');
    const db: any = {asset:{findUnique:vi.fn().mockResolvedValue({id:'asset',status:'ACTIVE',market:{id:'market',status:'ACTIVE'}})},$transaction:vi.fn().mockResolvedValue({id:'order'}),order:{update:vi.fn().mockResolvedValue({})}};
    const fee: any = {calculateFee:vi.fn().mockResolvedValue({feeAmount:new Prisma.Decimal(0.04)})};
    const matching: any = {matchOrder:vi.fn().mockRejectedValue(failure)};
    const service = new OrderService(db, {} as any, {} as any, fee, matching);
    const cancel = vi.spyOn(service,'cancelOrder').mockResolvedValue({} as any);
    await expect(service.placeOrder({userId:'user',assetSymbol:'FSAKA',side:'BUY',quantity:10,limitPrice:1})).rejects.toBe(failure);
    expect(cancel).toHaveBeenCalledWith('user','order');
    expect(db.order.update).toHaveBeenCalledWith({where:{id:'order'},data:{status:'REJECTED'}});
  });
  it('cannot replay another user’s order even before a cached HTTP receipt exists', async () => {
    const db:any={order:{findUnique:vi.fn().mockResolvedValue({id:'other-order',userId:'another-user'})}};
    const service=new OrderService(db);
    await expect(service.placeOrder({userId:'user',assetSymbol:'FSAKA',side:'BUY',quantity:10,limitPrice:1,idempotencyKey:'shared-key'})).rejects.toMatchObject({code:'DUPLICATE_REQUEST'});
  });
  it.each([['different-user','/api/orders'],['user','/api/swaps']])('rejects a cached response belonging to %s at %s', async (userId,endpoint) => {
    const read=vi.spyOn(prisma.idempotencyRecord,'findUnique').mockResolvedValue({userId,endpoint,expiresAt:new Date(Date.now()+60000),responseStatus:201,responseBody:'{"order":{"id":"private"}}'} as any);
    const res:any={status:vi.fn().mockReturnThis(),json:vi.fn()};const next=vi.fn();
    try{await idempotencyMiddleware({headers:{'idempotency-key':'key'},originalUrl:'/api/orders',user:{id:'user'}} as any,res,next);expect(res.status).toHaveBeenCalledWith(409);expect(next).not.toHaveBeenCalled();expect(res.json.mock.calls[0][0]).not.toHaveProperty('order');}finally{read.mockRestore();}
  });
});
