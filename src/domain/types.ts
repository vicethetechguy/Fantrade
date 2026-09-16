export type AssetType = 'PLAYER' | 'COACH';
export type AssetStatus = 'ACTIVE' | 'HALTED' | 'DELISTED';
export type OrderSide = 'BUY' | 'SELL';
export type OrderType = 'LIMIT' | 'MARKET';
export type OrderStatus = 'PENDING' | 'OPEN' | 'PARTIALLY_FILLED' | 'FILLED' | 'CANCELLED' | 'EXPIRED' | 'REJECTED';
export type TimeInForce = 'GTC' | 'IOC';
export type ReservationPurpose = 'ORDER' | 'FANPLAY' | 'SWAP';
export type ReservationStatus = 'ACTIVE' | 'SETTLED' | 'RELEASED';
export type AccountType = 'USER_AVAILABLE' | 'USER_RESERVED' | 'PLATFORM_TREASURY' | 'PLATFORM_FEES';
export type LedgerEntryType = 'DEBIT' | 'CREDIT';
export type LedgerCategory = 
  | 'SHARE_PURCHASE'
  | 'SHARE_SALE'
  | 'TRADE_SETTLEMENT'
  | 'FEE'
  | 'FANPLAY_SETTLEMENT'
  | 'REFUND'
  | 'RESERVATION'
  | 'RELEASE'
  | 'DEPOSIT';

export interface MarketPriceSummary {
  marketId: string;
  symbol: string;
  lastPrice: number | null;
  bestBid: number | null;
  bestAsk: number | null;
  midPrice: number | null;
  spread: number | null;
  high24h: number | null;
  low24h: number | null;
  volume24h: number | null;
  change24h: number | null;
}

export interface OrderBookLevel {
  price: number;
  shares: number;
  total: number;
  orderCount: number;
}

export interface OrderBookDepth {
  marketId: string;
  symbol: string;
  timestamp: string;
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  lastPrice: number | null;
  bestBid: number | null;
  bestAsk: number | null;
  spread: number | null;
}

export interface PlaceOrderInput {
  userId: string;
  assetSymbol: string;
  side: OrderSide;
  type?: OrderType;
  quantity: number;
  limitPrice: number;
  timeInForce?: TimeInForce;
  idempotencyKey?: string;
}

export interface SwapExecutionInput {
  userId: string;
  fromSymbol: string;
  toSymbol: string;
  shares: number;
  idempotencyKey?: string;
}

export interface SwapResult {
  fromSymbol: string;
  toSymbol: string;
  spentShares: number;
  receivedShares: number;
  grossAmount: number;
  feeAmount: number;
  dustRefund: number;
  timestamp: string;
}
