import { describe, it, expect, beforeEach } from 'vitest';
import { prisma } from '../src/database/client.js';
import { ReconciliationService } from '../src/services/reconciliation.service.js';
import { seed } from '../prisma/seed.js';

describe('Global Platform Reconciliation Audit Tests (§9, §11, §14, §28, §49)', () => {
  let reconciliationService: ReconciliationService;

  beforeEach(async () => {
    await seed();
    reconciliationService = new ReconciliationService();
  });

  it('verifies every asset has exactly 10,000,000 shares reconciled between treasury and users (§9, §28)', async () => {
    const assets = await prisma.asset.findMany({ include: { holdings: true } });

    expect(assets.length).toBe(12);

    for (const a of assets) {
      expect(a.totalShares).toBe(10_000_000);

      const userShares = a.holdings.reduce((sum, h) => sum + h.quantity, 0);
      expect(a.treasuryShares + userShares).toBe(10_000_000);
      expect(a.circulatingShares).toBe(userShares);
    }
  });

  it('verifies ownership integrity across all holdings (quantity = available + locked) (§11)', async () => {
    const holdings = await prisma.holding.findMany();
    expect(holdings.length).toBeGreaterThan(0);

    for (const h of holdings) {
      expect(h.availableQuantity + h.lockedQuantity).toBe(h.quantity);
      expect(h.availableQuantity).toBeGreaterThanOrEqual(0);
      expect(h.lockedQuantity).toBeGreaterThanOrEqual(0);
    }
  });

  it('verifies double-entry ledger balance (total debits == total credits) (§14, §58)', async () => {
    const auditReport = await reconciliationService.runAudit();

    expect(auditReport.ledgerReconciliation.passed).toBe(true);
    expect(auditReport.ledgerReconciliation.imbalance).toBeLessThan(0.0001);
    expect(auditReport.ledgerReconciliation.totalDebits).toBeGreaterThan(0);
    expect(auditReport.ledgerReconciliation.totalCredits).toBe(auditReport.ledgerReconciliation.totalDebits);
  });
});
