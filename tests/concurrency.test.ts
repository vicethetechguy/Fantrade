import { describe, it, expect, beforeEach } from 'vitest';
import { prisma } from '../src/database/client.js';
import { OrderService } from '../src/services/order.service.js';
import { LedgerService } from '../src/services/ledger.service.js';
import { seed } from '../prisma/seed.js';

describe('Concurrency, Idempotency & Safety Tests (§26, §56, §57)', () => {
  let orderService: OrderService;
  let ledgerService: LedgerService;

  beforeEach(async () => {
    await seed();
    orderService = new OrderService();
    ledgerService = new LedgerService();
  });

  it('prevents double-execution when the same idempotency key is submitted twice (§56)', async () => {
    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;
    const idempotencyKey = 'test-idemp-' + Date.now();

    const order1 = await orderService.placeOrder({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      side: 'BUY',
      quantity: 10,
      limitPrice: 20.0,
      idempotencyKey,
    });

    const order2 = await orderService.placeOrder({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      side: 'BUY',
      quantity: 10,
      limitPrice: 20.0,
      idempotencyKey,
    });

    expect(order1.id).toBe(order2.id);

    const ordersInDb = await prisma.order.findMany({
      where: { idempotencyKey },
    });
    expect(ordersInDb.length).toBe(1);
  });

  it('prevents double-spending when attempting to sell more shares than owned (§57)', async () => {
    const trader1 = (await prisma.user.findUnique({ where: { email: 'trader1@fantrade.com' } }))!;
    const asset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' } }))!;

    // Set trader1 total shares to exactly 100
    await prisma.shareReservation.deleteMany({ where: { assetId: asset.id, userId: trader1.id } });
    await prisma.holding.update({
      where: { userId_assetId: { userId: trader1.id, assetId: asset.id } },
      data: { quantity: 100, availableQuantity: 100, lockedQuantity: 0 },
    });

    // 1. First order: SELL 100
    const order1 = await orderService.placeOrder({
      userId: trader1.id,
      assetSymbol: '$Saka',
      side: 'SELL',
      quantity: 100,
      limitPrice: 60.0,
    });
    expect(order1.status).toBe('OPEN');

    // Available is now 0 (100 locked)
    const holdingAfter = await prisma.holding.findUnique({
      where: { userId_assetId: { userId: trader1.id, assetId: asset.id } },
    });
    expect(holdingAfter!.availableQuantity).toBe(0);
    expect(holdingAfter!.lockedQuantity).toBe(100);

    // 2. Second order: attempt to SELL 100 again -> MUST FAIL
    await expect(
      orderService.placeOrder({
        userId: trader1.id,
        assetSymbol: '$Saka',
        side: 'SELL',
        quantity: 100,
        limitPrice: 60.0,
      })
    ).rejects.toThrow('Insufficient available shares');

    // Never allow negative ownership
    const finalHolding = await prisma.holding.findUnique({
      where: { userId_assetId: { userId: trader1.id, assetId: asset.id } },
    });
    expect(finalHolding!.availableQuantity).toBe(0);
    expect(finalHolding!.quantity).toBe(100);
  });

  it('prevents self-trading when a user attempts to cross their own order (§26)', async () => {
    const trader1 = (await prisma.user.findUnique({ where: { email: 'trader1@fantrade.com' } }))!;
    const asset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' } }))!;

    // Place a resting SELL order at 50.00
    await orderService.placeOrder({
      userId: trader1.id,
      assetSymbol: '$Saka',
      side: 'SELL',
      quantity: 20,
      limitPrice: 50.0,
    });

    // Same user attempts to place a crossing BUY order at 50.00 -> MUST FAIL
    await expect(
      orderService.placeOrder({
        userId: trader1.id,
        assetSymbol: '$Saka',
        side: 'BUY',
        quantity: 20,
        limitPrice: 50.0,
      })
    ).rejects.toThrow('Self-trade prevented');
  });

  it('releases reserved FTR and shares upon order cancellation (§20)', async () => {
    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;

    const balanceBefore = await ledgerService.getBalance(demoUser.id);

    // Place BUY order
    const order = await orderService.placeOrder({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      side: 'BUY',
      quantity: 10,
      limitPrice: 30.0, // not crossing any resting ask
    });

    const balanceDuring = await ledgerService.getBalance(demoUser.id);
    expect(balanceDuring.reserved).toBeGreaterThan(balanceBefore.reserved);
    expect(balanceDuring.available).toBeLessThan(balanceBefore.available);

    // Cancel order
    await orderService.cancelOrder(demoUser.id, order.id);

    const balanceAfter = await ledgerService.getBalance(demoUser.id);
    expect(balanceAfter.available).toBeCloseTo(balanceBefore.available, 2);
    expect(balanceAfter.reserved).toBe(0);
  });
});
