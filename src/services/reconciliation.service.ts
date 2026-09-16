import { PrismaClient, Prisma } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';

export interface ReconciliationReport {
  timestamp: string;
  isHealthy: boolean;
  assetReconciliation: {
    passed: boolean;
    totalAssetsAudited: number;
    discrepancies: Array<{ symbol: string; expected: number; actual: number; delta: number }>;
  };
  ownershipReconciliation: {
    passed: boolean;
    totalHoldingsAudited: number;
    discrepancies: Array<{ holdingId: string; userId: string; symbol: string; error: string }>;
  };
  orderReconciliation: {
    passed: boolean;
    totalOrdersAudited: number;
    discrepancies: Array<{ orderId: string; expectedTotal: number; actualTotal: number }>;
  };
  ledgerReconciliation: {
    passed: boolean;
    totalDebits: number;
    totalCredits: number;
    imbalance: number;
    accountsAudited: number;
  };
}

export class ReconciliationService {
  constructor(private prisma: PrismaClient = defaultPrisma) {}

  /**
   * Runs an end-to-end mathematical and financial audit across all platform assets, holdings, orders, and ledger accounts.
   */
  async runAudit(): Promise<ReconciliationReport> {
    // 1. Asset 10,000,000 Shares Reconciliation
    const assets = await this.prisma.asset.findMany({
      include: {
        holdings: true,
      },
    });

    const assetDiscrepancies: Array<{ symbol: string; expected: number; actual: number; delta: number }> = [];

    for (const a of assets) {
      const userSharesSum = a.holdings.reduce((sum, h) => sum + h.quantity, 0);
      const actualTotal = a.treasuryShares + userSharesSum;
      const expectedTotal = a.totalShares; // Always 10,000,000

      if (actualTotal !== expectedTotal) {
        assetDiscrepancies.push({
          symbol: a.symbol,
          expected: expectedTotal,
          actual: actualTotal,
          delta: actualTotal - expectedTotal,
        });
      }
    }

    // 2. Ownership Invariant: quantity == availableQuantity + lockedQuantity
    const holdings = await this.prisma.holding.findMany({
      include: { asset: true },
    });

    const ownershipDiscrepancies: Array<{ holdingId: string; userId: string; symbol: string; error: string }> = [];

    for (const h of holdings) {
      if (h.availableQuantity + h.lockedQuantity !== h.quantity) {
        ownershipDiscrepancies.push({
          holdingId: h.id,
          userId: h.userId,
          symbol: h.asset.symbol,
          error: `Holding mismatch: ${h.availableQuantity} avail + ${h.lockedQuantity} locked != ${h.quantity} total`,
        });
      }
    }

    // 3. Order Invariant: originalQuantity == filledQuantity + remainingQuantity
    const orders = await this.prisma.order.findMany({
      include: { fills: true },
    });

    const orderDiscrepancies: Array<{ orderId: string; expectedTotal: number; actualTotal: number }> = [];

    for (const o of orders) {
      const filledSum = o.fills.reduce((sum, f) => sum + f.fillQuantity, 0);
      if (o.status === 'FILLED' || o.status === 'OPEN' || o.status === 'PARTIALLY_FILLED') {
        const total = filledSum + o.remainingQuantity;
        if (total !== o.quantity) {
          orderDiscrepancies.push({
            orderId: o.id,
            expectedTotal: o.quantity,
            actualTotal: total,
          });
        }
      }
    }

    // 4. Double-Entry Ledger Invariant: sum(debits) == sum(credits)
    const debitAggregate = await this.prisma.ledgerEntry.aggregate({
      where: { entryType: 'DEBIT' },
      _sum: { amount: true },
    });

    const creditAggregate = await this.prisma.ledgerEntry.aggregate({
      where: { entryType: 'CREDIT' },
      _sum: { amount: true },
    });

    const totalDebits = debitAggregate._sum.amount ? debitAggregate._sum.amount.toNumber() : 0;
    const totalCredits = creditAggregate._sum.amount ? creditAggregate._sum.amount.toNumber() : 0;
    const imbalance = Math.abs(totalDebits - totalCredits);

    const accountsCount = await this.prisma.ledgerAccount.count();

    const isHealthy =
      assetDiscrepancies.length === 0 &&
      ownershipDiscrepancies.length === 0 &&
      orderDiscrepancies.length === 0 &&
      imbalance < 0.0001;

    return {
      timestamp: new Date().toISOString(),
      isHealthy,
      assetReconciliation: {
        passed: assetDiscrepancies.length === 0,
        totalAssetsAudited: assets.length,
        discrepancies: assetDiscrepancies,
      },
      ownershipReconciliation: {
        passed: ownershipDiscrepancies.length === 0,
        totalHoldingsAudited: holdings.length,
        discrepancies: ownershipDiscrepancies,
      },
      orderReconciliation: {
        passed: orderDiscrepancies.length === 0,
        totalOrdersAudited: orders.length,
        discrepancies: orderDiscrepancies,
      },
      ledgerReconciliation: {
        passed: imbalance < 0.0001,
        totalDebits,
        totalCredits,
        imbalance,
        accountsAudited: accountsCount,
      },
    };
  }
}
