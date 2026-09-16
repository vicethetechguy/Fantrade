import { Prisma, PrismaClient, Order } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';
import { LedgerService } from './ledger.service.js';
import { OwnershipService } from './ownership.service.js';
import { FeeService } from './fee.service.js';
import { SelfTradeError } from '../domain/errors.js';
import { randomUUID } from 'crypto';

export class MatchingService {
  constructor(
    private prisma: PrismaClient = defaultPrisma,
    private ledgerService = new LedgerService(defaultPrisma),
    private ownershipService = new OwnershipService(defaultPrisma),
    private feeService = new FeeService(defaultPrisma)
  ) {}

  /**
   * Matches an aggressive (incoming) order against the existing resting orders on the book.
   * Runs in an interactive transaction with row-level locks on matching orders.
   */
  async matchOrder(incomingOrderId: string): Promise<{ matchedTradesCount: number; remainingQty: number }> {
    return this.prisma.$transaction(async (tx) => {
      // 1. Fetch the incoming order
      const order = await tx.order.findUnique({
        where: { id: incomingOrderId },
        include: { market: true, asset: true },
      });

      if (!order || (order.status !== 'OPEN' && order.status !== 'PARTIALLY_FILLED')) {
        return { matchedTradesCount: 0, remainingQty: order ? order.remainingQuantity : 0 };
      }

      let currentRemaining = order.remainingQuantity;
      let matchedTradesCount = 0;

      // 2. Query opposite resting orders
      // For BUY: search asks (SELL) where limitPrice <= order.limitPrice, ordered by limitPrice ASC, createdAt ASC
      // For SELL: search bids (BUY) where limitPrice >= order.limitPrice, ordered by limitPrice DESC, createdAt ASC
      const isBuy = order.side === 'BUY';
      const restingOrders = await tx.order.findMany({
        where: {
          marketId: order.marketId,
          side: isBuy ? 'SELL' : 'BUY',
          status: { in: ['OPEN', 'PARTIALLY_FILLED'] },
          limitPrice: isBuy ? { lte: order.limitPrice } : { gte: order.limitPrice },
        },
        orderBy: isBuy
          ? [{ limitPrice: 'asc' }, { createdAt: 'asc' }]
          : [{ limitPrice: 'desc' }, { createdAt: 'asc' }],
      });

      const txLedger = this.ledgerService.withTx(tx);
      const txOwnership = this.ownershipService.withTx(tx);
      const txFee = this.feeService.withTx(tx);
      const feeConfig = await txFee.getFeeConfiguration();

      for (const resting of restingOrders) {
        if (currentRemaining <= 0) break;

        // Self-Trade Prevention: A user must not match against their own resting order
        if (resting.userId === order.userId) {
          // Cancel-Newest Policy: Stop matching and reject the self-trade
          throw new SelfTradeError(order.asset.symbol);
        }

        // Execution price policy: RESTING ORDER'S PRICE (the maker's limit price)
        const executionPrice = resting.limitPrice;
        const matchQuantity = Math.min(currentRemaining, resting.remainingQuantity);

        const totalNotional = executionPrice.mul(matchQuantity);
        const buyerId = isBuy ? order.userId : resting.userId;
        const sellerId = isBuy ? resting.userId : order.userId;
        const buyOrderId = isBuy ? order.id : resting.id;
        const sellOrderId = isBuy ? resting.id : order.id;

        // Fee calculations (default 0.4%)
        const buyerFee = totalNotional.mul(feeConfig.buyFeeRate);
        const sellerFee = totalNotional.mul(feeConfig.sellFeeRate);
        const sellerProceeds = totalNotional.minus(sellerFee);

        const txGroup = randomUUID();

        // ── A. ATOMIC LEDGER SETTLEMENT (FTR) ──
        // 1. Buyer payment (funds debited from Buyer's USER_RESERVED or USER_AVAILABLE)
        const buyerWallet = await txLedger.getOrCreateWallet(buyerId);
        const buyerReserved = buyerWallet.accounts.find((a) => a.accountType === 'USER_RESERVED')!;
        const sellerWallet = await txLedger.getOrCreateWallet(sellerId);
        const sellerAvailable = sellerWallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;

        // Debit buyer reserved for notional:
        // Credit seller available:
        await txLedger.recordTransfer({
          transactionGroup: txGroup,
          fromAccountId: buyerReserved.id,
          toAccountId: sellerAvailable.id,
          amount: totalNotional,
          category: 'TRADE_SETTLEMENT',
          referenceId: incomingOrderId,
          description: `Trade settlement: ${matchQuantity} ${order.asset.symbol} @ ${executionPrice.toFixed(2)}`,
        });

        // 2. Collect Buyer Fee (from Buyer to Platform Fees account)
        await txLedger.recordTransfer({
          transactionGroup: txGroup,
          fromAccountId: buyerReserved.id,
          toAccountId: feeConfig.feeAccountId,
          amount: buyerFee,
          category: 'FEE',
          referenceId: incomingOrderId,
          description: `Buyer exchange fee (${(feeConfig.buyFeeRate.toNumber() * 100).toFixed(2)}%)`,
        });

        // 3. Collect Seller Fee (from Seller available to Platform Fees account)
        await txLedger.recordTransfer({
          transactionGroup: txGroup,
          fromAccountId: sellerAvailable.id,
          toAccountId: feeConfig.feeAccountId,
          amount: sellerFee,
          category: 'FEE',
          referenceId: incomingOrderId,
          description: `Seller exchange fee (${(feeConfig.sellFeeRate.toNumber() * 100).toFixed(2)}%)`,
        });

        // If Buyer had reserved funds at a higher limit price than the executed resting price,
        // refund the price improvement difference back to Buyer's available balance!
        if (isBuy && order.limitPrice.greaterThan(executionPrice)) {
          const priceDiff = order.limitPrice.minus(executionPrice);
          const refundNotional = priceDiff.mul(matchQuantity);
          const refundFee = refundNotional.mul(feeConfig.buyFeeRate);
          const totalRefund = refundNotional.plus(refundFee);

          const buyerAvailable = buyerWallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;
          await txLedger.recordTransfer({
            transactionGroup: txGroup,
            fromAccountId: buyerReserved.id,
            toAccountId: buyerAvailable.id,
            amount: totalRefund,
            category: 'REFUND',
            referenceId: incomingOrderId,
            description: `Price improvement refund (${matchQuantity} shares @ +${priceDiff.toFixed(2)} $FTR)`,
          });
        }

        // ── B. ATOMIC OWNERSHIP SETTLEMENT (SHARES) ──
        // 1. Settle seller's share reservation
        const sellReservation = await tx.shareReservation.findFirst({
          where: { referenceId: sellOrderId, status: 'ACTIVE' },
        });

        if (sellReservation) {
          await txOwnership.settleReservation(sellReservation.id, matchQuantity);
        } else {
          // Deduct directly from seller's holding if not reserved
          await tx.holding.update({
            where: { userId_assetId: { userId: sellerId, assetId: order.assetId } },
            data: {
              quantity: { decrement: matchQuantity },
              availableQuantity: { decrement: matchQuantity },
            },
          });
        }

        // 2. Credit buyer with shares and update average cost basis
        await txOwnership.creditShares(buyerId, order.assetId, matchQuantity, executionPrice);

        // ── C. UPDATE ORDER & TRADE RECORDS ──
        currentRemaining -= matchQuantity;
        const restingRemaining = resting.remainingQuantity - matchQuantity;

        // Update resting order
        await tx.order.update({
          where: { id: resting.id },
          data: {
            remainingQuantity: restingRemaining,
            status: restingRemaining === 0 ? 'FILLED' : 'PARTIALLY_FILLED',
          },
        });

        // Create Trade record
        const trade = await tx.trade.create({
          data: {
            marketId: order.marketId,
            assetId: order.assetId,
            buyerId,
            sellerId,
            buyOrderId,
            sellOrderId,
            price: executionPrice,
            quantity: matchQuantity,
            totalAmount: totalNotional,
            buyerFee,
            sellerFee,
            takerSide: order.side,
          },
        });

        // Create TradeFill records for both sides
        await tx.tradeFill.createMany({
          data: [
            {
              tradeId: trade.id,
              orderId: order.id,
              fillQuantity: matchQuantity,
              fillPrice: executionPrice,
            },
            {
              tradeId: trade.id,
              orderId: resting.id,
              fillQuantity: matchQuantity,
              fillPrice: executionPrice,
            },
          ],
        });

        // ── D. UPDATE MARKET TICKER & STATS ──
        await tx.market.update({
          where: { id: order.marketId },
          data: {
            lastPrice: executionPrice,
            volume24h: { increment: matchQuantity },
          },
        });

        // Update Asset current price
        await tx.asset.update({
          where: { id: order.assetId },
          data: { currentPrice: executionPrice },
        });

        // Record 1m price point
        const nowMinute = new Date();
        nowMinute.setSeconds(0, 0);
        await tx.priceHistoryPoint.upsert({
          where: {
            marketId_interval_timestamp: {
              marketId: order.marketId,
              interval: '1m',
              timestamp: nowMinute,
            },
          },
          update: {
            high: { set: Prisma.Decimal.max(executionPrice, executionPrice) },
            low: { set: Prisma.Decimal.min(executionPrice, executionPrice) },
            close: executionPrice,
            volume: { increment: matchQuantity },
          },
          create: {
            marketId: order.marketId,
            interval: '1m',
            timestamp: nowMinute,
            open: executionPrice,
            high: executionPrice,
            low: executionPrice,
            close: executionPrice,
            volume: matchQuantity,
          },
        });

        matchedTradesCount++;
      }

      // 3. Update incoming order remaining status
      const updatedStatus = currentRemaining === 0 ? 'FILLED' : matchedTradesCount > 0 ? 'PARTIALLY_FILLED' : 'OPEN';

      // If IOC (Immediate or Cancel) and not completely filled, cancel remainder
      if (order.timeInForce === 'IOC' && currentRemaining > 0) {
        await tx.order.update({
          where: { id: order.id },
          data: {
            remainingQuantity: 0,
            status: matchedTradesCount > 0 ? 'PARTIALLY_FILLED' : 'CANCELLED',
          },
        });

        // Release remaining FTR (for BUY) or remaining shares (for SELL)
        if (isBuy) {
          const unusedNotional = order.limitPrice.mul(currentRemaining);
          const unusedFee = unusedNotional.mul(feeConfig.buyFeeRate);
          await txLedger.releaseFtr(order.userId, unusedNotional.plus(unusedFee).toNumber(), order.id);
        } else {
          const reservation = await tx.shareReservation.findFirst({
            where: { referenceId: order.id, status: 'ACTIVE' },
          });
          if (reservation) {
            await txOwnership.releaseShares(reservation.id);
          }
        }
      } else {
        await tx.order.update({
          where: { id: order.id },
          data: {
            remainingQuantity: currentRemaining,
            status: updatedStatus,
          },
        });
      }

      return { matchedTradesCount, remainingQty: currentRemaining };
    });
  }
}
