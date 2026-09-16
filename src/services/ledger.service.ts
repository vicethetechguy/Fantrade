import { Prisma, PrismaClient } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';
import { InsufficientFtrError } from '../domain/errors.js';
import { randomUUID } from 'crypto';

export class LedgerService {
  constructor(private prisma: PrismaClient | Prisma.TransactionClient = defaultPrisma) {}

  /**
   * Returns an instance scoped to an ongoing Prisma transaction.
   */
  withTx(tx: Prisma.TransactionClient): LedgerService {
    return new LedgerService(tx);
  }

  /**
   * Retrieves or lazily initializes a user's wallet with both AVAILABLE and RESERVED accounts.
   */
  async getOrCreateWallet(userId: string) {
    let wallet = await this.prisma.wallet.findUnique({
      where: { userId },
      include: { accounts: true },
    });

    if (!wallet) {
      wallet = await this.prisma.wallet.create({
        data: {
          userId,
          currency: 'FTR',
          accounts: {
            create: [
              { accountType: 'USER_AVAILABLE', balance: new Prisma.Decimal(0) },
              { accountType: 'USER_RESERVED', balance: new Prisma.Decimal(0) },
            ],
          },
        },
        include: { accounts: true },
      });
    }

    return wallet;
  }

  /**
   * Retrieves the designated platform treasury or fee ledger account.
   */
  async getPlatformAccount(type: 'PLATFORM_TREASURY' | 'PLATFORM_FEES') {
    let account = await this.prisma.ledgerAccount.findFirst({
      where: { accountType: type, walletId: null },
    });

    if (!account) {
      account = await this.prisma.ledgerAccount.create({
        data: {
          accountType: type,
          balance: new Prisma.Decimal(0),
        },
      });
    }

    return account;
  }

  /**
   * Retrieves the authoritative FTR balance breakdown for a user.
   */
  async getBalance(userId: string) {
    const wallet = await this.getOrCreateWallet(userId);
    const availableAcc = wallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE');
    const reservedAcc = wallet.accounts.find((a) => a.accountType === 'USER_RESERVED');

    const available = availableAcc ? availableAcc.balance.toNumber() : 0;
    const reserved = reservedAcc ? reservedAcc.balance.toNumber() : 0;
    const total = available + reserved;

    return {
      available,
      reserved,
      total,
      currency: 'FTR',
    };
  }

  /**
   * Records a strictly balanced double-entry transfer between two ledger accounts.
   * Decrements fromAccount (DEBIT/CREDIT depending on asset side convention) and increments toAccount.
   */
  async recordTransfer(params: {
    transactionGroup?: string;
    fromAccountId: string;
    toAccountId: string;
    amount: number | Prisma.Decimal;
    category:
      | 'SHARE_PURCHASE'
      | 'SHARE_SALE'
      | 'TRADE_SETTLEMENT'
      | 'FEE'
      | 'FANPLAY_SETTLEMENT'
      | 'REFUND'
      | 'RESERVATION'
      | 'RELEASE'
      | 'DEPOSIT';
    referenceId?: string;
    description?: string;
  }) {
    const group = params.transactionGroup || randomUUID();
    const amountDec = new Prisma.Decimal(params.amount);

    if (amountDec.lessThanOrEqualTo(0)) {
      throw new Error(`Transfer amount must be positive, got ${params.amount}`);
    }

    // 1. Decrement source account
    await this.prisma.ledgerAccount.update({
      where: { id: params.fromAccountId },
      data: {
        balance: {
          decrement: amountDec,
        },
      },
    });

    // 2. Increment destination account
    await this.prisma.ledgerAccount.update({
      where: { id: params.toAccountId },
      data: {
        balance: {
          increment: amountDec,
        },
      },
    });

    // 3. Create immutable double-entry records
    const debitEntry = await this.prisma.ledgerEntry.create({
      data: {
        transactionGroup: group,
        accountId: params.fromAccountId,
        entryType: 'DEBIT',
        amount: amountDec,
        category: params.category,
        referenceId: params.referenceId,
        description: params.description ? `Debit: ${params.description}` : 'Debit',
      },
    });

    const creditEntry = await this.prisma.ledgerEntry.create({
      data: {
        transactionGroup: group,
        accountId: params.toAccountId,
        entryType: 'CREDIT',
        amount: amountDec,
        category: params.category,
        referenceId: params.referenceId,
        description: params.description ? `Credit: ${params.description}` : 'Credit',
      },
    });

    return { transactionGroup: group, debitEntry, creditEntry };
  }

  /**
   * Reserves FTR for an open order or FanPlay entry by moving it from AVAILABLE to RESERVED account.
   */
  async reserveFtr(userId: string, amount: number, referenceId?: string, description?: string) {
    const wallet = await this.getOrCreateWallet(userId);
    const availableAcc = wallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;
    const reservedAcc = wallet.accounts.find((a) => a.accountType === 'USER_RESERVED')!;

    if (availableAcc.balance.toNumber() < amount) {
      throw new InsufficientFtrError(availableAcc.balance.toNumber(), amount);
    }

    return this.recordTransfer({
      fromAccountId: availableAcc.id,
      toAccountId: reservedAcc.id,
      amount,
      category: 'RESERVATION',
      referenceId,
      description: description || `Reserve FTR for ${referenceId || 'order'}`,
    });
  }

  /**
   * Releases previously reserved FTR back to the user's available balance (e.g. order cancelled).
   */
  async releaseFtr(userId: string, amount: number, referenceId?: string, description?: string) {
    const wallet = await this.getOrCreateWallet(userId);
    const availableAcc = wallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;
    const reservedAcc = wallet.accounts.find((a) => a.accountType === 'USER_RESERVED')!;

    const releaseAmount = Math.min(reservedAcc.balance.toNumber(), amount);
    if (releaseAmount <= 0) return null;

    return this.recordTransfer({
      fromAccountId: reservedAcc.id,
      toAccountId: availableAcc.id,
      amount: releaseAmount,
      category: 'RELEASE',
      referenceId,
      description: description || `Release reserved FTR for ${referenceId || 'order'}`,
    });
  }

  /**
   * Credits an initial deposit to a user's wallet (credited from Platform Treasury).
   */
  async depositFtr(userId: string, amount: number, referenceId?: string) {
    const wallet = await this.getOrCreateWallet(userId);
    const availableAcc = wallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;
    const treasury = await this.getPlatformAccount('PLATFORM_TREASURY');

    return this.recordTransfer({
      fromAccountId: treasury.id,
      toAccountId: availableAcc.id,
      amount,
      category: 'DEPOSIT',
      referenceId,
      description: `Deposit to user ${userId}`,
    });
  }
}
