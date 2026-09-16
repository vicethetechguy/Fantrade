import { PrismaClient, Prisma } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';
import { LedgerService } from './ledger.service.js';
import { OwnershipService } from './ownership.service.js';
import { FeeService } from './fee.service.js';
import { SwapExecutionInput, SwapResult } from '../domain/types.js';
import {
  InsufficientSharesError,
  InvalidOrderInputError,
  MarketHaltedError,
} from '../domain/errors.js';
import { randomUUID } from 'crypto';

export class SwapService {
  constructor(
    private prisma: PrismaClient = defaultPrisma,
    private ledgerService = new LedgerService(defaultPrisma),
    private ownershipService = new OwnershipService(defaultPrisma),
    private feeService = new FeeService(defaultPrisma)
  ) {}

  /**
   * Executes an atomic asset swap: fromAsset shares -> toAsset shares, collecting fee and returning dust.
   */
  async executeSwap(input: SwapExecutionInput): Promise<SwapResult> {
    const { userId, fromSymbol, toSymbol, shares, idempotencyKey } = input;

    if (fromSymbol === toSymbol) {
      throw new InvalidOrderInputError('Cannot swap an asset for itself. Pick two different assets.');
    }

    if (shares <= 0) {
      throw new InvalidOrderInputError('Shares to swap must be greater than zero.');
    }

    // Resolve assets
    const [fromAsset, toAsset] = await Promise.all([
      this.prisma.asset.findUnique({ where: { symbol: fromSymbol } }),
      this.prisma.asset.findUnique({ where: { symbol: toSymbol } }),
    ]);

    if (!fromAsset || !toAsset) {
      throw new InvalidOrderInputError(`One or both assets not found: ${fromSymbol}, ${toSymbol}`);
    }

    if (fromAsset.status !== 'ACTIVE' || toAsset.status !== 'ACTIVE') {
      throw new MarketHaltedError(`${fromSymbol} or ${toSymbol}`);
    }

    const fromPrice = fromAsset.currentPrice;
    const toPrice = toAsset.currentPrice;

    if (fromPrice.lessThanOrEqualTo(0) || toPrice.lessThanOrEqualTo(0)) {
      throw new InvalidOrderInputError('Asset current price must be positive for swapping.');
    }

    const grossAmount = fromPrice.mul(shares);
    const feeCalc = await this.feeService.calculateFee(grossAmount, 'SWAP');
    const netAmount = grossAmount.minus(feeCalc.feeAmount);

    const receivedShares = Math.floor(netAmount.div(toPrice).toNumber());
    if (receivedShares < 1) {
      throw new InvalidOrderInputError(
        `Swapping ${shares} ${fromSymbol} does not yield enough value to receive at least 1 share of ${toSymbol}.`
      );
    }

    const spentCost = toPrice.mul(receivedShares);
    const dustRefund = netAmount.minus(spentCost);

    return this.prisma.$transaction(async (tx) => {
      const txOwnership = this.ownershipService.withTx(tx);
      const txLedger = this.ledgerService.withTx(tx);

      // 1. Verify and deduct fromAsset shares
      const holding = await tx.holding.findUnique({
        where: { userId_assetId: { userId, assetId: fromAsset.id } },
      });

      if (!holding || holding.availableQuantity < shares) {
        throw new InsufficientSharesError(fromSymbol, holding ? holding.availableQuantity : 0, shares);
      }

      await tx.holding.update({
        where: { id: holding.id },
        data: {
          quantity: { decrement: shares },
          availableQuantity: { decrement: shares },
        },
      });

      // 2. Credit toAsset shares with weighted average cost
      await txOwnership.creditShares(userId, toAsset.id, receivedShares, toPrice);

      // 3. Ledger: Record fee transfer to Platform Fees account
      const txGroup = randomUUID();
      const userWallet = await txLedger.getOrCreateWallet(userId);
      const userAvailable = userWallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;

      // Transfer swap fee to platform fee account
      await txLedger.recordTransfer({
        transactionGroup: txGroup,
        fromAccountId: userAvailable.id,
        toAccountId: feeCalc.feeAccountId,
        amount: feeCalc.feeAmount,
        category: 'FEE',
        description: `Swap fee: ${shares} ${fromSymbol} -> ${receivedShares} ${toSymbol}`,
      });

      // Credit dust refund back to user available wallet
      if (dustRefund.greaterThan(0)) {
        const treasury = await txLedger.getPlatformAccount('PLATFORM_TREASURY');
        await txLedger.recordTransfer({
          transactionGroup: txGroup,
          fromAccountId: treasury.id,
          toAccountId: userAvailable.id,
          amount: dustRefund,
          category: 'REFUND',
          description: `Swap dust refund: ${dustRefund.toFixed(2)} $FTR`,
        });
      }

      // 4. Record Swap history
      await tx.swap.create({
        data: {
          userId,
          fromAssetId: fromAsset.id,
          toAssetId: toAsset.id,
          fromShares: shares,
          toShares: receivedShares,
          fromPrice,
          toPrice,
          fee: feeCalc.feeAmount,
          dustRefund,
          idempotencyKey,
          status: 'COMPLETED',
        },
      });

      return {
        fromSymbol,
        toSymbol,
        spentShares: shares,
        receivedShares,
        grossAmount: grossAmount.toNumber(),
        feeAmount: feeCalc.feeAmount.toNumber(),
        dustRefund: dustRefund.toNumber(),
        timestamp: new Date().toISOString(),
      };
    });
  }
}
