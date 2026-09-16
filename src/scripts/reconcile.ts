import { ReconciliationService } from '../services/reconciliation.service.js';
import { prisma } from '../database/client.js';

async function main() {
  console.log('============================================================');
  console.log('FANTRADE FINANCIAL & ASSET RECONCILIATION AUDIT');
  console.log('============================================================\n');

  const reconciliationService = new ReconciliationService(prisma);
  const report = await reconciliationService.runAudit();

  console.log(`Audit Timestamp: ${report.timestamp}`);
  console.log(`Overall Health: ${report.isHealthy ? '✅ PASSED (All Invariants Intact)' : '❌ FAILED'}\n`);

  console.log('1. ASSET SUPPLY RECONCILIATION (10,000,000 Rule):');
  console.log(`   Audited: ${report.assetReconciliation.totalAssetsAudited} assets`);
  console.log(`   Status:  ${report.assetReconciliation.passed ? '✅ PASSED' : '❌ DISCREPANCIES DETECTED'}`);
  if (!report.assetReconciliation.passed) {
    console.error('   Discrepancies:', report.assetReconciliation.discrepancies);
  }

  console.log('\n2. OWNERSHIP RECONCILIATION (quantity == available + locked):');
  console.log(`   Audited: ${report.ownershipReconciliation.totalHoldingsAudited} holdings`);
  console.log(`   Status:  ${report.ownershipReconciliation.passed ? '✅ PASSED' : '❌ DISCREPANCIES DETECTED'}`);
  if (!report.ownershipReconciliation.passed) {
    console.error('   Discrepancies:', report.ownershipReconciliation.discrepancies);
  }

  console.log('\n3. ORDER INVARIANT RECONCILIATION (quantity == filled + remaining):');
  console.log(`   Audited: ${report.orderReconciliation.totalOrdersAudited} orders`);
  console.log(`   Status:  ${report.orderReconciliation.passed ? '✅ PASSED' : '❌ DISCREPANCIES DETECTED'}`);
  if (!report.orderReconciliation.passed) {
    console.error('   Discrepancies:', report.orderReconciliation.discrepancies);
  }

  console.log('\n4. DOUBLE-ENTRY LEDGER RECONCILIATION (debits == credits):');
  console.log(`   Total Debits:  ${report.ledgerReconciliation.totalDebits.toLocaleString('en-US')} $FTR`);
  console.log(`   Total Credits: ${report.ledgerReconciliation.totalCredits.toLocaleString('en-US')} $FTR`);
  console.log(`   Imbalance:     ${report.ledgerReconciliation.imbalance.toFixed(4)} $FTR`);
  console.log(`   Status:        ${report.ledgerReconciliation.passed ? '✅ PASSED' : '❌ DISCREPANCY DETECTED'}`);

  console.log('\n============================================================');
  process.exit(report.isHealthy ? 0 : 1);
}

main().catch((err) => {
  console.error('[Reconcile Script Error]:', err);
  process.exit(1);
});
