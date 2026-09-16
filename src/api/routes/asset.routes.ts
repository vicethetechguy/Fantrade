import { Router } from 'express';
import { prisma } from '../../database/client.js';

export const assetRouter = Router();

// GET /api/assets - List all assets (players and coaches)
assetRouter.get('/', async (req, res, next) => {
  try {
    const type = req.query.type as string;
    const search = req.query.q as string;

    const assets = await prisma.asset.findMany({
      where: {
        ...(type && (type === 'PLAYER' || type === 'COACH') ? { type } : {}),
        ...(search
          ? {
              OR: [
                { name: { contains: search, mode: 'insensitive' } },
                { symbol: { contains: search, mode: 'insensitive' } },
              ],
            }
          : {}),
      },
      include: {
        playerProfile: true,
        coachProfile: true,
        market: {
          select: {
            id: true,
            lastPrice: true,
            bestBid: true,
            bestAsk: true,
            high24h: true,
            low24h: true,
            volume24h: true,
            change24h: true,
          },
        },
      },
      orderBy: { symbol: 'asc' },
    });

    res.json({ assets });
  } catch (err) {
    next(err);
  }
});

// GET /api/assets/:idOrSymbol - Get single asset details
assetRouter.get('/:idOrSymbol', async (req, res, next) => {
  try {
    const { idOrSymbol } = req.params;

    const asset = await prisma.asset.findFirst({
      where: {
        OR: [{ id: idOrSymbol }, { symbol: idOrSymbol }, { slug: idOrSymbol }],
      },
      include: {
        playerProfile: true,
        coachProfile: true,
        market: true,
      },
    });

    if (!asset) {
      return res.status(404).json({ error: { code: 'ASSET_NOT_FOUND', message: `Asset ${idOrSymbol} not found.` } });
    }

    res.json({ asset });
  } catch (err) {
    next(err);
  }
});
