import { Router } from 'express';
import { prisma } from '../../database/client.js';
import { z } from 'zod';
import { randomUUID } from 'crypto';
import { authMiddleware, AuthenticatedRequest } from '../middlewares/auth.middleware.js';

export const authRouter = Router();

const signInSchema = z.object({
  email: z.string().email(),
  password: z.string().optional(),
});

authRouter.post('/signin', async (req, res, next) => {
  try {
    const { email } = signInSchema.parse(req.body);

    let user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      // Auto-provision user in dev/prototype mode
      user = await prisma.user.create({
        data: {
          email,
          displayName: email.split('@')[0],
        },
      });
    }

    const token = randomUUID();
    const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

    await prisma.authSession.create({
      data: {
        userId: user.id,
        token,
        expiresAt,
      },
    });

    res.json({
      user: {
        id: user.id,
        email: user.email,
        displayName: user.displayName,
      },
      token,
      expiresAt: expiresAt.toISOString(),
    });
  } catch (err) {
    next(err);
  }
});

authRouter.get('/me', authMiddleware, async (req: AuthenticatedRequest, res, next) => {
  try {
    const user = await prisma.user.findUnique({
      where: { id: req.user!.id },
      select: { id: true, email: true, displayName: true, createdAt: true },
    });
    res.json({ user });
  } catch (err) {
    next(err);
  }
});
