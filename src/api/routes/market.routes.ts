import { Router } from 'express';
import { MarketService } from '../../services/market.service.js';

export const marketRouter = Router();
const marketService = new MarketService();

// GET /api/markets/:idOrSymbol/order-book - Real aggregated order book depth
marketRouter.get('/:idOrSymbol/order-book', async (req, res, next) => {
  try {
    const depth = await marketService.getOrderBook(req.params.idOrSymbol);
    res.json({ orderBook: depth });
  } catch (err) {
    next(err);
  }
});

// GET /api/markets/:idOrSymbol/trades - Real recent trade executions
marketRouter.get('/:idOrSymbol/trades', async (req, res, next) => {
  try {
    const limit = parseInt((req.query.limit as string) || '50', 10);
    const trades = await marketService.getRecentTrades(req.params.idOrSymbol, limit);
    res.json({ trades });
  } catch (err) {
    next(err);
  }
});

// GET /api/markets/:idOrSymbol/stats - 24h market price summary
marketRouter.get('/:idOrSymbol/stats', async (req, res, next) => {
  try {
    const stats = await marketService.getMarketStats(req.params.idOrSymbol);
    res.json({ stats });
  } catch (err) {
    next(err);
  }
});

// GET /api/markets/:idOrSymbol/price-history - OHLCV candlesticks
marketRouter.get('/:idOrSymbol/price-history', async (req, res, next) => {
  try {
    const interval = (req.query.interval as string) || '1m';
    const limit = parseInt((req.query.limit as string) || '100', 10);
    const candles = await marketService.getPriceHistory(req.params.idOrSymbol, interval, limit);
    res.json({ candles });
  } catch (err) {
    next(err);
  }
});
