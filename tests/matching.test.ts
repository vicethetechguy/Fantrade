import { describe, it, expect, beforeEach } from 'vitest';
import { prisma } from '../src/database/client.js';
import { OrderService } from '../src/services/order.service.js';
import { MatchingService } from '../src/services/matching.service.js';
import { LedgerService } from '../src/services/ledger.service.js';
import { OwnershipService } from '../src/services/ownership.service.js';
import { FeeService } from '../src/services/fee.service.js';
import { ReconciliationService } from '../src/services/reconciliation.service.js';
import { seed } from '../prisma/seed.js';

describe('Critical Matching & Order Engine Tests (§55)', () => {
  let orderService: OrderService;
  let matchingService: MatchingService;
  let ledgerService: LedgerService;
  let ownershipService: OwnershipService;
  let feeService: FeeService;
  let reconciliationService: ReconciliationService;

  beforeEach(async () => {
    // Reset database to deterministic clean state
    await seed();

    orderService = new OrderService();
    matchingService = new MatchingService();
    ledgerService = new LedgerService();
    ownershipService = new OwnershipService();
    feeService = new FeeService();
    reconciliationService = new ReconciliationService();
  });

  it('matches orders according to FIFO price-time priority with resting order execution price (§55)', async () => {
    // Setup test scenario:
    // User A (trader1) sells 100 @ 10.00
    // User A (trader1) sells 100 @ 11.00
    // User B (demoUser) buys 150 @ 11.00
    // Expected:
    // 100 shares match @ 10.00 (from first ask)
    // 50 shares match @ 11.00 (from second ask)
    // Remaining on book: 50 shares of second ask @ 11.00
    // Buyer is completely FILLED

    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;
    const trader1 = (await prisma.user.findUnique({ where: { email: 'trader1@fantrade.com' } }))!;
    const asset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' }, include: { market: true } }))!;

    // Clean out prior trades, reservations and orders for this test asset
    await prisma.tradeFill.deleteMany({ where: { trade: { assetId: asset.id } } });
    await prisma.trade.deleteMany({ where: { assetId: asset.id } });
    await prisma.shareReservation.deleteMany({ where: { assetId: asset.id } });
    await prisma.order.deleteMany({ where: { assetId: asset.id } });

    // Reset trader1 available shares to 1,000 and adjust treasury to maintain 10M invariant
    const curHolding = await prisma.holding.findUnique({
      where: { userId_assetId: { userId: trader1.id, assetId: asset.id } },
    });
    const shareDiff = (curHolding?.quantity || 0) - 1000;
    if (shareDiff !== 0) {
      await prisma.asset.update({
        where: { id: asset.id },
        data: { treasuryShares: { increment: shareDiff } },
      });
    }

    await prisma.holding.update({
      where: { userId_assetId: { userId: trader1.id, assetId: asset.id } },
      data: { quantity: 1000, availableQuantity: 1000, lockedQuantity: 0 },
    });

    // Reset demoUser available FTR to 50,000
    const demoWallet = await ledgerService.getOrCreateWallet(demoUser.id);
    const demoAvail = demoWallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;
    await prisma.ledgerAccount.update({
      where: { id: demoAvail.id },
      data: { balance: 50000 },
    });

    // 1. Trader 1 places SELL 100 @ 10.00
    const sell1 = await orderService.placeOrder({
      userId: trader1.id,
      assetSymbol: '$Saka',
      side: 'SELL',
      quantity: 100,
      limitPrice: 10.0,
    });

    // 2. Trader 1 places SELL 100 @ 11.00
    const sell2 = await orderService.placeOrder({
      userId: trader1.id,
      assetSymbol: '$Saka',
      side: 'SELL',
      quantity: 100,
      limitPrice: 11.0,
    });

    expect(sell1.status).toBe('OPEN');
    expect(sell2.status).toBe('OPEN');

    // 3. Demo User places aggressive BUY 150 @ 11.00
    const buyOrder = await orderService.placeOrder({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      side: 'BUY',
      quantity: 150,
      limitPrice: 11.0,
    });

    // 4. Verification of Order Statuses
    const updatedBuy = (await prisma.order.findUnique({ where: { id: buyOrder.id } }))!;
    const updatedSell1 = (await prisma.order.findUnique({ where: { id: sell1.id } }))!;
    const updatedSell2 = (await prisma.order.findUnique({ where: { id: sell2.id } }))!;

    expect(updatedBuy.status).toBe('FILLED');
    expect(updatedBuy.remainingQuantity).toBe(0);

    expect(updatedSell1.status).toBe('FILLED');
    expect(updatedSell1.remainingQuantity).toBe(0);

    expect(updatedSell2.status).toBe('PARTIALLY_FILLED');
    expect(updatedSell2.remainingQuantity).toBe(50); // 100 - 50 = 50 remaining

    // 5. Verification of Trades Created
    const trades = await prisma.trade.findMany({
      where: { marketId: asset.market!.id, buyOrderId: buyOrder.id },
      orderBy: { price: 'asc' },
    });

    expect(trades.length).toBe(2);
    // Trade 1: 100 @ 10.00
    expect(trades[0].quantity).toBe(100);
    expect(trades[0].price.toNumber()).toBe(10.0);
    expect(trades[0].totalAmount.toNumber()).toBe(1000.0);

    // Trade 2: 50 @ 11.00
    expect(trades[1].quantity).toBe(50);
    expect(trades[1].price.toNumber()).toBe(11.0);
    expect(trades[1].totalAmount.toNumber()).toBe(550.0);

    // 6. Verification of Double-Entry Ledger and Reconciliation Audit
    const auditReport = await reconciliationService.runAudit();
    if (!auditReport.isHealthy) {
      console.error('Audit report failed:', JSON.stringify(auditReport, null, 2));
    }
    expect(auditReport.isHealthy).toBe(true);
    expect(auditReport.assetReconciliation.passed).toBe(true);
    expect(auditReport.ownershipReconciliation.passed).toBe(true);
    expect(auditReport.orderReconciliation.passed).toBe(true);
    expect(auditReport.ledgerReconciliation.passed).toBe(true);
    expect(auditReport.ledgerReconciliation.imbalance).toBeLessThan(0.0001);
  });
});
