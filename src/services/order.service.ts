import { PrismaClient, Prisma, Order } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';
import { LedgerService } from './ledger.service.js';
import { OwnershipService } from './ownership.service.js';
import { FeeService } from './fee.service.js';
import { MatchingService } from './matching.service.js';
import { PlaceOrderInput } from '../domain/types.js';
import {
  InsufficientFtrError,
  InsufficientSharesError,
  OrderNotFoundError,
  OrderNotOpenError,
  MarketHaltedError,
  DuplicateRequestError,
  InvalidOrderInputError,
  SelfTradeError,
} from '../domain/errors.js';
import { config } from '../config/index.js';

export class OrderService {
  constructor(
    private prisma: PrismaClient = defaultPrisma,
    private ledgerService = new LedgerService(defaultPrisma),
    private ownershipService = new OwnershipService(defaultPrisma),
    private feeService = new FeeService(defaultPrisma),
    private matchingService = new MatchingService(defaultPrisma)
  ) {}

  /**
   * Places a limit order with atomic balance/share reservation and triggers matching.
   */
  async placeOrder(input: PlaceOrderInput): Promise<Order> {
    const { userId, assetSymbol, side, quantity, limitPrice, timeInForce = 'GTC', idempotencyKey } = input;

    // 1. Validation
    if (quantity < config.marketSafety.minOrderQuantity || quantity > config.marketSafety.maxOrderQuantity) {
      throw new InvalidOrderInputError(`Quantity must be between ${config.marketSafety.minOrderQuantity} and ${config.marketSafety.maxOrderQuantity.toLocaleString('en-US')}.`);
    }

    if (limitPrice < config.marketSafety.minLimitPrice || limitPrice > config.marketSafety.maxLimitPrice) {
      throw new InvalidOrderInputError(`Limit price must be between ${config.marketSafety.minLimitPrice} and ${config.marketSafety.maxLimitPrice.toLocaleString('en-US')} $FTR.`);
    }

    // 2. Idempotency Check
    if (idempotencyKey) {
      const existingOrder = await this.prisma.order.findUnique({
        where: { idempotencyKey },
      });
      if (existingOrder) {
        return existingOrder;
      }
    }

    // 3. Resolve Asset and Market
    const asset = await this.prisma.asset.findUnique({
      where: { symbol: assetSymbol },
      include: { market: true },
    });

    if (!asset || !asset.market) {
      throw new InvalidOrderInputError(`Asset market for ${assetSymbol} not found.`);
    }

    if (asset.status !== 'ACTIVE' || asset.market.status !== 'ACTIVE') {
      throw new MarketHaltedError(assetSymbol);
    }

    const priceDec = new Prisma.Decimal(limitPrice);
    const notional = priceDec.mul(quantity);
    const feeCalc = await this.feeService.calculateFee(notional, side);
    const requiredFtr = notional.plus(feeCalc.feeAmount);

    // 4. Atomic Execution & Reservation inside a single DB transaction
    const createdOrder = await this.prisma.$transaction(async (tx) => {
      const txLedger = this.ledgerService.withTx(tx);
      const txOwnership = this.ownershipService.withTx(tx);

      // Create the order record in OPEN state
      const order = await tx.order.create({
        data: {
          userId,
          marketId: asset.market!.id,
          assetId: asset.id,
          side,
          type: input.type || 'LIMIT',
          quantity,
          remainingQuantity: quantity,
          limitPrice: priceDec,
          status: 'OPEN',
          timeInForce,
          idempotencyKey,
        },
      });

      if (side === 'BUY') {
        // Reserve required FTR (notional + fee)
        await txLedger.reserveFtr(
          userId,
          requiredFtr.toNumber(),
          order.id,
          `Reserve FTR for BUY ${quantity} ${assetSymbol} @ ${limitPrice}`
        );
      } else {
        // Reserve required shares
        await txOwnership.reserveShares({
          userId,
          assetId: asset.id,
          quantity,
          purpose: 'ORDER',
          referenceId: order.id,
        });
      }

      return order;
    });

    // 5. Trigger Matching Engine
    try {
      await this.matchingService.matchOrder(createdOrder.id);
    } catch (err: any) {
      if (err instanceof SelfTradeError || err?.name === 'SelfTradeError' || err?.code === 'SELF_TRADE_PREVENTED') {
        // Reject the order, release reserved funds/shares, and rethrow
        await this.cancelOrder(userId, createdOrder.id);
        await this.prisma.order.update({
          where: { id: createdOrder.id },
          data: { status: 'REJECTED' },
        });
        throw err;
      }
      console.warn(`[OrderService] Match warning for order ${createdOrder.id}:`, err);
    }

    // Return the updated order with latest status
    return (await this.prisma.order.findUnique({ where: { id: createdOrder.id } }))!;
  }

  /**
   * Cancels an open or partially filled order, releasing any remaining reserved FTR or shares.
   */
  async cancelOrder(userId: string, orderId: string): Promise<Order> {
    return this.prisma.$transaction(async (tx) => {
      const order = await tx.order.findUnique({
        where: { id: orderId },
        include: { asset: true },
      });

      if (!order) {
        throw new OrderNotFoundError(orderId);
      }

      if (order.userId !== userId) {
        throw new Error('Unauthorized to cancel this order.');
      }

      if (order.status !== 'OPEN' && order.status !== 'PARTIALLY_FILLED') {
        throw new OrderNotOpenError(orderId, order.status);
      }

      const txLedger = this.ledgerService.withTx(tx);
      const txOwnership = this.ownershipService.withTx(tx);
      const txFee = this.feeService.withTx(tx);
      const feeConfig = await txFee.getFeeConfiguration();

      const remaining = order.remainingQuantity;

      if (remaining > 0) {
        if (order.side === 'BUY') {
          // Release remaining FTR (proportional notional + fee)
          const remainingNotional = order.limitPrice.mul(remaining);
          const remainingFee = remainingNotional.mul(feeConfig.buyFeeRate);
          const totalToRelease = remainingNotional.plus(remainingFee);

          await txLedger.releaseFtr(
            userId,
            totalToRelease.toNumber(),
            order.id,
            `Cancel remaining BUY ${remaining} ${order.asset.symbol}`
          );
        } else {
          // Release remaining shares
          const reservation = await tx.shareReservation.findFirst({
            where: { referenceId: order.id, status: 'ACTIVE' },
          });
          if (reservation) {
            await txOwnership.releaseShares(reservation.id);
          }
        }
      }

      return tx.order.update({
        where: { id: order.id },
        data: {
          remainingQuantity: 0,
          status: 'CANCELLED',
        },
      });
    });
  }

  /**
   * Lists orders for a user with optional status filter.
   */
  async getUserOrders(userId: string, status?: string) {
    return this.prisma.order.findMany({
      where: {
        userId,
        ...(status ? { status: status as any } : {}),
      },
      include: {
        asset: { select: { symbol: true, name: true, type: true } },
      },
      orderBy: { createdAt: 'desc' },
    });
  }
}
