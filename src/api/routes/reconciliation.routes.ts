import { Router } from 'express';
import { ReconciliationService } from '../../services/reconciliation.service.js';

export const reconciliationRouter = Router();
const reconciliationService = new ReconciliationService();

// GET /api/reconcile - Run full financial and inventory integrity audit
reconciliationRouter.get('/', async (req, res, next) => {
  try {
    const report = await reconciliationService.runAudit();
    const statusCode = report.isHealthy ? 200 : 500;
    res.status(statusCode).json({ reconciliation: report });
  } catch (err) {
    next(err);
  }
});
