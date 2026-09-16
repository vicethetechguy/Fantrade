import { Router } from 'express';
import { LedgerService } from '../../services/ledger.service.js';
import { prisma } from '../../database/client.js';
import { authMiddleware, AuthenticatedRequest } from '../middlewares/auth.middleware.js';

export const walletRouter = Router();
const ledgerService = new LedgerService();

// GET /api/wallet - Get authoritative wallet balance
walletRouter.get('/', authMiddleware, async (req: AuthenticatedRequest, res, next) => {
  try {
    const balance = await ledgerService.getBalance(req.user!.id);
    res.json({ wallet: balance });
  } catch (err) {
    next(err);
  }
});

// GET /api/wallet/ledger - Get immutable transaction audit log
walletRouter.get('/ledger', authMiddleware, async (req: AuthenticatedRequest, res, next) => {
  try {
    const wallet = await ledgerService.getOrCreateWallet(req.user!.id);
    const accountIds = wallet.accounts.map((a) => a.id);

    const entries = await prisma.ledgerEntry.findMany({
      where: {
        accountId: { in: accountIds },
      },
      orderBy: { createdAt: 'desc' },
      take: 100,
    });

    res.json({ entries });
  } catch (err) {
    next(err);
  }
});
