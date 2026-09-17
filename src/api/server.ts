import express from 'express';
import cors from 'cors';
import path from 'path';
import { config } from '../config/index.js';
import { authRouter } from './routes/auth.routes.js';
import { assetRouter } from './routes/asset.routes.js';
import { marketRouter } from './routes/market.routes.js';
import { orderRouter } from './routes/order.routes.js';
import { portfolioRouter } from './routes/portfolio.routes.js';
import { swapRouter } from './routes/swap.routes.js';
import { walletRouter } from './routes/wallet.routes.js';
import { reconciliationRouter } from './routes/reconciliation.routes.js';
import { fanplayRouter } from './routes/fanplay.routes.js';
import { errorHandler } from './middlewares/error.middleware.js';

export function createServer() {
  const app = express();

  app.use(cors());
  app.use(express.json());

  // Health check
  app.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'fantrade-api', timestamp: new Date().toISOString() });
  });

  // REST API Routes
  app.use('/api/auth', authRouter);
  app.use('/api/assets', assetRouter);
  app.use('/api/markets', marketRouter);
  app.use('/api/orders', orderRouter);
  app.use('/api/portfolio', portfolioRouter);
  app.use('/api/swaps', swapRouter);
  app.use('/api/wallet', walletRouter);
  app.use('/api/fanplay', fanplayRouter);
  app.use('/api/reconcile', reconciliationRouter);

  // Serve static UI prototype pages alongside the API for seamless development
  app.use(express.static(path.resolve(process.cwd())));

  // Error handling middleware
  app.use(errorHandler);

  return app;
}

export function startServer(port = config.port) {
  const app = createServer();
  return app.listen(port, () => {
    console.log(`[Fantrade API] Server running on http://localhost:${port}`);
    console.log(`[Fantrade API] Health check: http://localhost:${port}/health`);
  });
}

if (process.argv[1]?.includes('server')) {
  startServer();
}

