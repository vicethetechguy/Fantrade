import { Request, Response, NextFunction } from 'express';
import { prisma } from '../../database/client.js';
import { AuthenticatedRequest } from './auth.middleware.js';

export async function idempotencyMiddleware(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const key = req.headers['idempotency-key'] as string;
  if (!key) {
    return next();
  }

  try {
    const existing = await prisma.idempotencyRecord.findUnique({
      where: { key },
    });

    if (existing && existing.expiresAt > new Date()) {
      return res.status(existing.responseStatus).json(JSON.parse(existing.responseBody));
    }

    // Intercept response to store result
    const originalJson = res.json.bind(res);
    res.json = (body: any): Response => {
      if (res.statusCode >= 200 && res.statusCode < 300) {
        prisma.idempotencyRecord
          .create({
            data: {
              key,
              endpoint: req.originalUrl,
              userId: req.user?.id || 'anonymous',
              responseStatus: res.statusCode,
              responseBody: JSON.stringify(body),
              expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24h
            },
          })
          .catch((err) => console.error('[Idempotency] Save error:', err));
      }
      return originalJson(body);
    };

    next();
  } catch (err) {
    next(err);
  }
}
