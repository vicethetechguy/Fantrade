import { PrismaClient, Prisma } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';
import { OrderBookDepth, OrderBookLevel, MarketPriceSummary } from '../domain/types.js';

export class MarketService {
  constructor(private prisma: PrismaClient = defaultPrisma) {}

  /**
   * Derives a real, authentic order book depth for a market from open orders.
   * Groups by price level and sorts by Price-Time Priority.
   */
  async getOrderBook(marketIdOrSymbol: string): Promise<OrderBookDepth> {
    const market = await this.resolveMarket(marketIdOrSymbol);

    // Fetch open bids (BUY) ordered by price DESC, createdAt ASC
    const bidsRaw = await this.prisma.order.findMany({
      where: {
        marketId: market.id,
        side: 'BUY',
        status: { in: ['OPEN', 'PARTIALLY_FILLED'] },
        remainingQuantity: { gt: 0 },
      },
      orderBy: [{ limitPrice: 'desc' }, { createdAt: 'asc' }],
    });

    // Fetch open asks (SELL) ordered by price ASC, createdAt ASC
    const asksRaw = await this.prisma.order.findMany({
      where: {
        marketId: market.id,
        side: 'SELL',
        status: { in: ['OPEN', 'PARTIALLY_FILLED'] },
        remainingQuantity: { gt: 0 },
      },
      orderBy: [{ limitPrice: 'asc' }, { createdAt: 'asc' }],
    });

    // Aggregate bids by price level
    const bidsMap = new Map<number, { shares: number; count: number }>();
    for (const b of bidsRaw) {
      const px = b.limitPrice.toNumber();
      const cur = bidsMap.get(px) || { shares: 0, count: 0 };
      cur.shares += b.remainingQuantity;
      cur.count += 1;
      bidsMap.set(px, cur);
    }

    // Aggregate asks by price level
    const asksMap = new Map<number, { shares: number; count: number }>();
    for (const a of asksRaw) {
      const px = a.limitPrice.toNumber();
      const cur = asksMap.get(px) || { shares: 0, count: 0 };
      cur.shares += a.remainingQuantity;
      cur.count += 1;
      asksMap.set(px, cur);
    }

    let bidCum = 0;
    const bids: OrderBookLevel[] = Array.from(bidsMap.entries())
      .sort((a, b) => b[0] - a[0]) // price desc
      .map(([price, val]) => {
        bidCum += val.shares;
        return { price, shares: val.shares, total: bidCum, orderCount: val.count };
      });

    let askCum = 0;
    const asks: OrderBookLevel[] = Array.from(asksMap.entries())
      .sort((a, b) => a[0] - b[0]) // price asc
      .map(([price, val]) => {
        askCum += val.shares;
        return { price, shares: val.shares, total: askCum, orderCount: val.count };
      });

    const bestBid = bids.length > 0 ? bids[0].price : null;
    const bestAsk = asks.length > 0 ? asks[0].price : null;
    const spread = bestBid !== null && bestAsk !== null ? Math.max(0, bestAsk - bestBid) : null;

    return {
      marketId: market.id,
      symbol: market.baseAsset.symbol,
      timestamp: new Date().toISOString(),
      bids,
      asks,
      lastPrice: market.lastPrice ? market.lastPrice.toNumber() : null,
      bestBid,
      bestAsk,
      spread,
    };
  }

  /**
   * Retrieves real recent trade executions for a market.
   */
  async getRecentTrades(marketIdOrSymbol: string, limit = 50) {
    const market = await this.resolveMarket(marketIdOrSymbol);

    return this.prisma.trade.findMany({
      where: { marketId: market.id },
      orderBy: { createdAt: 'desc' },
      take: limit,
      select: {
        id: true,
        price: true,
        quantity: true,
        totalAmount: true,
        takerSide: true,
        createdAt: true,
      },
    });
  }

  /**
   * Retrieves or computes real 24h market statistics based strictly on executed trades.
   */
  async getMarketStats(marketIdOrSymbol: string): Promise<MarketPriceSummary> {
    const market = await this.resolveMarket(marketIdOrSymbol);
    const depth = await this.getOrderBook(market.id);

    const since24h = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const trades24h = await this.prisma.trade.findMany({
      where: { marketId: market.id, createdAt: { gte: since24h } },
      orderBy: { createdAt: 'asc' },
    });

    let high24h: number | null = null;
    let low24h: number | null = null;
    let volume24h = 0;
    let change24h: number | null = null;

    if (trades24h.length > 0) {
      high24h = Math.max(...trades24h.map((t) => t.price.toNumber()));
      low24h = Math.min(...trades24h.map((t) => t.price.toNumber()));
      volume24h = trades24h.reduce((acc, t) => acc + t.quantity, 0);

      const firstPrice = trades24h[0].price.toNumber();
      const lastPrice = trades24h[trades24h.length - 1].price.toNumber();
      change24h = firstPrice > 0 ? ((lastPrice - firstPrice) / firstPrice) * 100 : 0;
    }

    const midPrice =
      depth.bestBid !== null && depth.bestAsk !== null ? (depth.bestBid + depth.bestAsk) / 2 : null;

    return {
      marketId: market.id,
      symbol: market.baseAsset.symbol,
      lastPrice: market.lastPrice ? market.lastPrice.toNumber() : null,
      bestBid: depth.bestBid,
      bestAsk: depth.bestAsk,
      midPrice,
      spread: depth.spread,
      high24h,
      low24h,
      volume24h: trades24h.length > 0 ? volume24h : null,
      change24h,
    };
  }

  /**
   * Returns real aggregated price history points (candlesticks).
   */
  async getPriceHistory(marketIdOrSymbol: string, interval = '1m', limit = 100) {
    const market = await this.resolveMarket(marketIdOrSymbol);

    return this.prisma.priceHistoryPoint.findMany({
      where: { marketId: market.id, interval },
      orderBy: { timestamp: 'desc' },
      take: limit,
    });
  }

  private async resolveMarket(idOrSymbol: string) {
    let market = await this.prisma.market.findFirst({
      where: {
        OR: [{ id: idOrSymbol }, { baseAsset: { symbol: idOrSymbol } }],
      },
      include: { baseAsset: true },
    });

    if (!market) {
      throw new Error(`Market for ${idOrSymbol} not found.`);
    }

    return market;
  }
}
