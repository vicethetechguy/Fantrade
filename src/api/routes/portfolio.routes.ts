import { Router } from 'express';
import { prisma } from '../../database/client.js';
import { authMiddleware, AuthenticatedRequest } from '../middlewares/auth.middleware.js';

export const portfolioRouter = Router();

// GET /api/portfolio - Get current holdings and unrealized P&L
portfolioRouter.get('/', authMiddleware, async (req: AuthenticatedRequest, res, next) => {
  try {
    const holdings = await prisma.holding.findMany({
      where: {
        userId: req.user!.id,
        quantity: { gt: 0 },
      },
      include: {
        asset: {
          select: {
            symbol: true,
            name: true,
            type: true,
            currentPrice: true,
          },
        },
        reservations: {
          where: { status: 'ACTIVE' },
        },
      },
      orderBy: { quantity: 'desc' },
    });

    const positions = holdings.map((h) => {
      const curPrice = h.asset.currentPrice.toNumber();
      const avgCost = h.averageCost.toNumber();
      const currentValue = h.quantity * curPrice;
      const totalCost = h.quantity * avgCost;
      const unrealizedPnl = currentValue - totalCost;
      const unrealizedPnlPct = totalCost > 0 ? (unrealizedPnl / totalCost) * 100 : 0;

      return {
        id: h.id,
        assetId: h.assetId,
        symbol: h.asset.symbol,
        name: h.asset.name,
        type: h.asset.type,
        quantity: h.quantity,
        availableQuantity: h.availableQuantity,
        lockedQuantity: h.lockedQuantity,
        averageCost: avgCost,
        currentPrice: curPrice,
        currentValue,
        unrealizedPnl,
        unrealizedPnlPct,
      };
    });

    const totalPortfolioValue = positions.reduce((acc, p) => acc + p.currentValue, 0);

    res.json({
      positions,
      totalPortfolioValue,
    });
  } catch (err) {
    next(err);
  }
});
