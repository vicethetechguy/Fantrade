import { PrismaClient, Prisma } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';

export type NegativeBalancePolicy = 
  | 'ALLOW_NEGATIVE'       // Standard ledger debit: user account balance can drop below zero into debt
  | 'CLAMP_TO_AVAILABLE'   // Debit is capped to user's available balance (zero floor)
  | 'ISOLATED_DEBT_RECORD';// Creates a separate isolated debt ledger record

export interface RiskPolicyConfig {
  negativeBalancePolicy: NegativeBalancePolicy;
  minStakeShares: number;
  maxStakeShares: number;
  maxLossLimitFP?: number;
  unresolvedEconomicPolicyStatus: 'TBD';
}

export class RiskPolicyService {
  private config: RiskPolicyConfig = {
    // Default to ALLOW_NEGATIVE double-entry accounting per financial principles,
    // explicitly marked as TBD pending final product executive sign-off.
    negativeBalancePolicy: 'ALLOW_NEGATIVE',
    minStakeShares: 1,
    maxStakeShares: 10000000,
    unresolvedEconomicPolicyStatus: 'TBD',
  };

  constructor(private prisma: PrismaClient | Prisma.TransactionClient = defaultPrisma) {}

  getConfig(): RiskPolicyConfig {
    return { ...this.config };
  }

  setNegativeBalancePolicy(policy: NegativeBalancePolicy) {
    this.config.negativeBalancePolicy = policy;
  }

  /**
   * Evaluates the effective debit amount when a FanPlay results in negative $FTR settlement.
   *
   * @param userAvailableBalance The user's current USER_AVAILABLE ledger account balance.
   * @param rawDebitAmount The absolute positive number to debit (e.g. 2.5 for -2.5 $FTR).
   * @returns The exact amount to debit from USER_AVAILABLE according to configured risk policy.
   */
  resolveNegativeSettlementDebit(userAvailableBalance: number, rawDebitAmount: number): {
    effectiveDebit: number;
    uncoveredDebt: number;
    policyApplied: NegativeBalancePolicy;
  } {
    const raw = Math.abs(rawDebitAmount);

    switch (this.config.negativeBalancePolicy) {
      case 'CLAMP_TO_AVAILABLE': {
        const effectiveDebit = Math.min(Math.max(0, userAvailableBalance), raw);
        const uncoveredDebt = raw - effectiveDebit;
        return { effectiveDebit, uncoveredDebt, policyApplied: 'CLAMP_TO_AVAILABLE' };
      }
      case 'ISOLATED_DEBT_RECORD': {
        const effectiveDebit = Math.min(Math.max(0, userAvailableBalance), raw);
        const uncoveredDebt = raw - effectiveDebit;
        return { effectiveDebit, uncoveredDebt, policyApplied: 'ISOLATED_DEBT_RECORD' };
      }
      case 'ALLOW_NEGATIVE':
      default: {
        return { effectiveDebit: raw, uncoveredDebt: 0, policyApplied: 'ALLOW_NEGATIVE' };
      }
    }
  }
}
