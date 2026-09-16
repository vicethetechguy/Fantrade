import { Router } from 'express';
import { z } from 'zod';
import { SwapService } from '../../services/swap.service.js';
import { authMiddleware, AuthenticatedRequest } from '../middlewares/auth.middleware.js';
import { idempotencyMiddleware } from '../middlewares/idempotency.middleware.js';

export const swapRouter = Router();
const swapService = new SwapService();

const swapSchema = z.object({
  fromSymbol: z.string(),
  toSymbol: z.string(),
  shares: z.number().int().positive(),
});

// POST /api/swaps - Execute atomic asset swap
swapRouter.post(
  '/',
  authMiddleware,
  idempotencyMiddleware,
  async (req: AuthenticatedRequest, res, next) => {
    try {
      const { fromSymbol, toSymbol, shares } = swapSchema.parse(req.body);
      const idempotencyKey = req.headers['idempotency-key'] as string;

      const result = await swapService.executeSwap({
        userId: req.user!.id,
        fromSymbol,
        toSymbol,
        shares,
        idempotencyKey,
      });

      res.status(200).json({ swap: result });
    } catch (err) {
      next(err);
    }
  }
);
