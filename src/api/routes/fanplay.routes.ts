import { Router, Response, NextFunction } from 'express';
import { z } from 'zod';
import { FanPlayService } from '../../services/fanplay.service.js';
import { authMiddleware, AuthenticatedRequest } from '../middlewares/auth.middleware.js';
import { idempotencyMiddleware } from '../middlewares/idempotency.middleware.js';
import { MarketTier, FanPlayType } from '../../domain/types.js';

export const fanplayRouter = Router();
const fanPlayService = new FanPlayService();

// Validation Schemas
const PreviewSchema = z.object({
  type: z.enum(['INDIVIDUAL', 'TEAM']).optional().default('INDIVIDUAL'),
  assetSymbol: z.string().optional(),
  dreamClubId: z.string().optional(),
  matchId: z.string().uuid(),
  marketTier: z.enum(['SIMPLE', 'PRO', 'ELITE', 'KILLER', 'VIYNX_MOVE', 'VIYNX_MAX']),
  selectedOptionIds: z.array(z.string().uuid()).min(1),
  stakedShares: z.number().int().positive(),
  teamExposure: z.number().optional(),
});

const ActivateSchema = z.object({
  type: z.enum(['INDIVIDUAL', 'TEAM']).optional().default('INDIVIDUAL'),
  assetSymbol: z.string().optional(),
  dreamClubId: z.string().optional(),
  matchId: z.string().uuid(),
  marketTier: z.enum(['SIMPLE', 'PRO', 'ELITE', 'KILLER', 'VIYNX_MOVE', 'VIYNX_MAX']),
  selectedOptionIds: z.array(z.string().uuid()).min(1),
  stakedShares: z.number().int().positive(),
  teamExposure: z.number().optional(),
  idempotencyKey: z.string().optional(),
});

// ============================================================
// 1. PUBLIC & DISCOVERY ROUTES
// ============================================================

// GET /api/fanplay/markets
fanplayRouter.get('/markets', async (req, res: Response, next: NextFunction) => {
  try {
    const markets = await fanPlayService.getMarkets();
    res.json({ success: true, data: markets });
  } catch (err) {
    next(err);
  }
});

// GET /api/fanplay/matches
fanplayRouter.get('/matches', async (req, res: Response, next: NextFunction) => {
  try {
    const status = req.query.status as any;
    const matches = await fanPlayService['footballDataProvider'].getFixtures({ status });
    res.json({ success: true, data: matches });
  } catch (err) {
    next(err);
  }
});

// GET /api/fanplay/options
fanplayRouter.get('/options', async (req, res: Response, next: NextFunction) => {
  try {
    const { matchId, assetId, marketTier } = req.query;
    const options = await fanPlayService.getOptions({
      matchId: matchId ? String(matchId) : undefined,
      assetId: assetId ? String(assetId) : undefined,
      marketTier: marketTier ? (String(marketTier) as MarketTier) : undefined,
    });
    res.json({ success: true, data: options });
  } catch (err) {
    next(err);
  }
});

// ============================================================
// 2. AUTHENTICATED USER ROUTES
// ============================================================

// GET /api/fanplay/eligible-assets
fanplayRouter.get('/eligible-assets', authMiddleware, async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const userId = req.user!.id;
    const assets = await fanPlayService.getEligibleAssets(userId);
    res.json({ success: true, data: assets });
  } catch (err) {
    next(err);
  }
});

// POST /api/fanplay/preview
fanplayRouter.post('/preview', authMiddleware, async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const userId = req.user!.id;
    const validated = PreviewSchema.parse(req.body);
    const preview = await fanPlayService.previewFanPlay({
      ...validated,
      userId,
    });
    res.json({ success: true, data: preview });
  } catch (err) {
    next(err);
  }
});

// POST /api/fanplay/activate
fanplayRouter.post(
  '/activate',
  authMiddleware,
  idempotencyMiddleware,
  async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    try {
      const userId = req.user!.id;
      const validated = ActivateSchema.parse(req.body);
      const idempotencyKey = (req.headers['idempotency-key'] as string) || validated.idempotencyKey;

      const fanPlay = await fanPlayService.activateFanPlay({
        ...validated,
        userId,
        idempotencyKey,
      });

      res.status(201).json({
        success: true,
        message: 'FanPlay position activated successfully. Shares have been locked.',
        data: fanPlay,
      });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/fanplay (list user FanPlays)
fanplayRouter.get('/', authMiddleware, async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const userId = req.user!.id;
    const status = req.query.status as any;
    const fanPlays = await fanPlayService.getUserFanPlays(userId, status);
    res.json({ success: true, data: fanPlays });
  } catch (err) {
    next(err);
  }
});

// GET /api/fanplay/:id
fanplayRouter.get('/:id', authMiddleware, async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const fanPlay = await fanPlayService.getFanPlayById(req.params.id);
    res.json({ success: true, data: fanPlay });
  } catch (err) {
    next(err);
  }
});

// POST /api/fanplay/:id/cancel
fanplayRouter.post('/:id/cancel', authMiddleware, async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const userId = req.user!.id;
    const cancelled = await fanPlayService.cancelFanPlay(userId, req.params.id);
    res.json({
      success: true,
      message: 'FanPlay cancelled. Locked shares have been returned to available balance.',
      data: cancelled,
    });
  } catch (err) {
    next(err);
  }
});

// GET /api/fanplay/:id/live
fanplayRouter.get('/:id/live', authMiddleware, async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const liveData = await fanPlayService.getLiveFanPlay(req.params.id);
    res.json({ success: true, data: liveData });
  } catch (err) {
    next(err);
  }
});

// GET /api/fanplay/:id/settlement
fanplayRouter.get('/:id/settlement', authMiddleware, async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const fanPlay = await fanPlayService.getFanPlayById(req.params.id);
    if (!fanPlay.settlement) {
      return res.status(404).json({
        success: false,
        error: { code: 'NOT_YET_SETTLED', message: 'FanPlay has not been settled yet.' },
      });
    }
    res.json({ success: true, data: fanPlay.settlement });
  } catch (err) {
    next(err);
  }
});

// POST /api/fanplay/:id/settle (system / admin settlement execution)
fanplayRouter.post('/:id/settle', authMiddleware, async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const forceFinal = req.body.forceFinal === true;
    const result = await fanPlayService.settleFanPlay(req.params.id, forceFinal);
    res.json({
      success: true,
      message: result.alreadySettled ? 'FanPlay already settled (idempotent result).' : 'FanPlay settled successfully.',
      data: result,
    });
  } catch (err) {
    next(err);
  }
});
