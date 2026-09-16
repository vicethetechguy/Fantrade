import { Prisma, PrismaClient } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';
import { InsufficientSharesError } from '../domain/errors.js';
import { ReservationPurpose } from '../domain/types.js';

export class OwnershipService {
  constructor(private prisma: PrismaClient | Prisma.TransactionClient = defaultPrisma) {}

  withTx(tx: Prisma.TransactionClient): OwnershipService {
    return new OwnershipService(tx);
  }

  /**
   * Retrieves or initializes a holding record for a user and asset.
   */
  async getOrCreateHolding(userId: string, assetId: string) {
    let holding = await this.prisma.holding.findUnique({
      where: { userId_assetId: { userId, assetId } },
    });

    if (!holding) {
      holding = await this.prisma.holding.create({
        data: {
          userId,
          assetId,
          quantity: 0,
          availableQuantity: 0,
          lockedQuantity: 0,
          averageCost: new Prisma.Decimal(0),
        },
      });
    }

    return holding;
  }

  /**
   * Atomically reserves a given quantity of shares, moving them from availableQuantity to lockedQuantity.
   */
  async reserveShares(params: {
    userId: string;
    assetId: string;
    quantity: number;
    purpose: ReservationPurpose;
    referenceId?: string;
  }) {
    const { userId, assetId, quantity, purpose, referenceId } = params;
    const holding = await this.getOrCreateHolding(userId, assetId);

    if (holding.availableQuantity < quantity) {
      const asset = await this.prisma.asset.findUnique({ where: { id: assetId } });
      throw new InsufficientSharesError(asset?.symbol || assetId, holding.availableQuantity, quantity);
    }

    // 1. Update holding quantities atomically
    const updatedHolding = await this.prisma.holding.update({
      where: { id: holding.id },
      data: {
        availableQuantity: { decrement: quantity },
        lockedQuantity: { increment: quantity },
      },
    });

    // Invariant check
    if (updatedHolding.availableQuantity + updatedHolding.lockedQuantity !== updatedHolding.quantity) {
      throw new Error(
        `Ownership invariant violation: available (${updatedHolding.availableQuantity}) + locked (${updatedHolding.lockedQuantity}) != total (${updatedHolding.quantity})`
      );
    }

    // 2. Create the reservation record
    const reservation = await this.prisma.shareReservation.create({
      data: {
        holdingId: holding.id,
        userId,
        assetId,
        quantity,
        purpose,
        referenceId,
        status: 'ACTIVE',
      },
    });

    return reservation;
  }

  /**
   * Releases previously reserved shares back to available quantity (e.g. cancelled sell order).
   */
  async releaseShares(reservationId: string) {
    const reservation = await this.prisma.shareReservation.findUnique({
      where: { id: reservationId },
    });

    if (!reservation || reservation.status !== 'ACTIVE') {
      return null;
    }

    // 1. Mark reservation as released
    await this.prisma.shareReservation.update({
      where: { id: reservation.id },
      data: { status: 'RELEASED' },
    });

    // 2. Return locked shares to available
    const holding = await this.prisma.holding.update({
      where: { id: reservation.holdingId },
      data: {
        lockedQuantity: { decrement: reservation.quantity },
        availableQuantity: { increment: reservation.quantity },
      },
    });

    return holding;
  }

  /**
   * Settles a reservation upon fill: permanently deducts the shares from the seller's locked balance.
   */
  async settleReservation(reservationId: string, quantityToSettle: number) {
    const reservation = await this.prisma.shareReservation.findUnique({
      where: { id: reservationId },
    });

    if (!reservation) {
      throw new Error(`Reservation ${reservationId} not found.`);
    }

    const settleQty = Math.min(reservation.quantity, quantityToSettle);

    // Deduct from holding total and locked quantity
    await this.prisma.holding.update({
      where: { id: reservation.holdingId },
      data: {
        quantity: { decrement: settleQty },
        lockedQuantity: { decrement: settleQty },
      },
    });

    if (reservation.quantity <= settleQty) {
      await this.prisma.shareReservation.update({
        where: { id: reservation.id },
        data: { status: 'SETTLED' },
      });
    } else {
      await this.prisma.shareReservation.update({
        where: { id: reservation.id },
        data: { quantity: { decrement: settleQty } },
      });
    }
  }

  /**
   * Credits purchased shares to the buyer and updates their weighted average cost basis.
   */
  async creditShares(userId: string, assetId: string, quantity: number, executionPrice: number | Prisma.Decimal) {
    const holding = await this.getOrCreateHolding(userId, assetId);
    const priceDec = new Prisma.Decimal(executionPrice);

    const prevTotalCost = holding.averageCost.mul(holding.quantity);
    const addedCost = priceDec.mul(quantity);
    const newQuantity = holding.quantity + quantity;
    const newAvgCost = newQuantity > 0 ? prevTotalCost.plus(addedCost).div(newQuantity) : priceDec;

    return this.prisma.holding.update({
      where: { id: holding.id },
      data: {
        quantity: newQuantity,
        availableQuantity: { increment: quantity },
        averageCost: newAvgCost,
      },
    });
  }

  /**
   * Primary Market Issuance: Transfers newly issued shares from Platform Treasury to a user.
   */
  async issuePrimaryShares(userId: string, assetId: string, quantity: number, price: number | Prisma.Decimal) {
    const asset = await this.prisma.asset.findUnique({ where: { id: assetId } });
    if (!asset || asset.treasuryShares < quantity) {
      throw new Error(`Insufficient treasury shares for asset ${assetId}`);
    }

    // Deduct from treasury, add to circulating
    await this.prisma.asset.update({
      where: { id: assetId },
      data: {
        treasuryShares: { decrement: quantity },
        circulatingShares: { increment: quantity },
      },
    });

    return this.creditShares(userId, assetId, quantity, price);
  }
}
