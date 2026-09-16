import { Request, Response, NextFunction } from 'express';
import { prisma } from '../../database/client.js';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email: string;
    displayName: string;
  };
}

export async function authMiddleware(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  try {
    const authHeader = req.headers.authorization;
    const explicitUserId = req.headers['x-user-id'] as string;

    if (explicitUserId) {
      const user = await prisma.user.findUnique({ where: { id: explicitUserId } });
      if (user) {
        req.user = { id: user.id, email: user.email, displayName: user.displayName };
        return next();
      }
    }

    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const session = await prisma.authSession.findUnique({
        where: { token },
        include: { user: true },
      });

      if (session && session.expiresAt > new Date()) {
        req.user = {
          id: session.user.id,
          email: session.user.email,
          displayName: session.user.displayName,
        };
        return next();
      }
    }

    // Fallback during prototype transition: use default demo user
    const demoUser = await prisma.user.findFirst({ where: { email: 'demo@fantrade.com' } });
    if (demoUser) {
      req.user = { id: demoUser.id, email: demoUser.email, displayName: demoUser.displayName };
      return next();
    }

    return res.status(401).json({
      error: {
        code: 'UNAUTHORIZED',
        message: 'Authentication required.',
      },
    });
  } catch (err) {
    next(err);
  }
}
