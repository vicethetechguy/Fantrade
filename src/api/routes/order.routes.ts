import { Router } from 'express';
import { z } from 'zod';
import { OrderService } from '../../services/order.service.js';
import { authMiddleware, AuthenticatedRequest } from '../middlewares/auth.middleware.js';
import { idempotencyMiddleware } from '../middlewares/idempotency.middleware.js';

export const orderRouter = Router();
const orderService = new OrderService();

const placeOrderSchema = z.object({
  assetSymbol: z.string(),
  side: z.enum(['BUY', 'SELL']),
  type: z.enum(['LIMIT', 'MARKET']).optional().default('LIMIT'),
  quantity: z.number().int().positive(),
  limitPrice: z.number().positive(),
  timeInForce: z.enum(['GTC', 'IOC']).optional().default('GTC'),
});

// POST /api/orders - Place a limit buy or sell order
orderRouter.post(
  '/',
  authMiddleware,
  idempotencyMiddleware,
  async (req: AuthenticatedRequest, res, next) => {
    try {
      const validated = placeOrderSchema.parse(req.body);
      const idempotencyKey = req.headers['idempotency-key'] as string;

      const order = await orderService.placeOrder({
        userId: req.user!.id,
        assetSymbol: validated.assetSymbol,
        side: validated.side,
        type: validated.type,
        quantity: validated.quantity,
        limitPrice: validated.limitPrice,
        timeInForce: validated.timeInForce,
        idempotencyKey,
      });

      res.status(201).json({ order });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/orders - Get active user orders
orderRouter.get('/', authMiddleware, async (req: AuthenticatedRequest, res, next) => {
  try {
    const status = req.query.status as string;
    const orders = await orderService.getUserOrders(req.user!.id, status);
    res.json({ orders });
  } catch (err) {
    next(err);
  }
});

// POST /api/orders/:id/cancel - Cancel an open order
orderRouter.post('/:id/cancel', authMiddleware, async (req: AuthenticatedRequest, res, next) => {
  try {
    const cancelled = await orderService.cancelOrder(req.user!.id, req.params.id);
    res.json({ order: cancelled, message: 'Order successfully cancelled. Reserved funds/shares released.' });
  } catch (err) {
    next(err);
  }
});
