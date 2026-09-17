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

// ============================================================
// FANPLAY DOMAIN TYPES (PROMPT 4)
// ============================================================

export type FanPlayType = 'INDIVIDUAL' | 'TEAM';

export type FanPlayStatus =
  | 'DRAFT'
  | 'ACTIVE'
  | 'LIVE'
  | 'PENDING_SETTLEMENT'
  | 'SETTLED'
  | 'CANCELLED'
  | 'SUSPENDED'
  | 'VOID'
  | 'DISPUTED';

export type MarketTier =
  | 'SIMPLE'
  | 'PRO'
  | 'ELITE'
  | 'KILLER'
  | 'VIYNX_MOVE'
  | 'VIYNX_MAX';

export type PredictionType =
  | 'BOOLEAN'
  | 'THRESHOLD'
  | 'EXACT'
  | 'RANGE'
  | 'TEAM_RESULT';

export type OptionDifficulty = 'EASY' | 'MEDIUM' | 'HARD' | 'EXTREME';

export type OptionEvaluationResult = 'PENDING' | 'SUCCESS' | 'FAILURE' | 'VOID';

export type MatchStatus =
  | 'SCHEDULED'
  | 'LINEUPS_CONFIRMED'
  | 'LIVE'
  | 'HALFTIME'
  | 'FULL_TIME'
  | 'POSTPONED'
  | 'ABANDONED'
  | 'CANCELLED';

export type FootballEventType =
  | 'GOAL'
  | 'ASSIST'
  | 'YELLOW_CARD'
  | 'RED_CARD'
  | 'SHOT'
  | 'SHOT_ON_TARGET'
  | 'KEY_PASS'
  | 'FOUL'
  | 'OFFSIDE'
  | 'SUBSTITUTION'
  | 'MINUTES_PLAYED'
  | 'TEAM_RESULT'
  | 'CORNERS'
  | 'CARDS';

export type PlayerMatchEligibility =
  | 'CONFIRMED_STARTER'
  | 'BENCH'
  | 'INJURED'
  | 'SUSPENDED'
  | 'UNKNOWN';

export interface EvaluationRule {
  metric: string;
  op: 'gte' | 'lte' | 'eq' | 'gt' | 'lt' | 'between' | 'contains' | 'avoid';
  value?: number | string | boolean;
  min?: number;
  max?: number;
}

export interface CreateFanPlayInput {
  userId: string;
  type?: FanPlayType;
  assetSymbol?: string;
  dreamClubId?: string;
  matchId: string;
  marketTier: MarketTier;
  selectedOptionIds: string[];
  stakedShares: number;
  idempotencyKey?: string;
  teamExposure?: number;
}

export interface FanPlayPreview {
  assetSymbol?: string;
  matchName: string;
  marketTier: MarketTier;
  stakedShares: number;
  selectionsCount: number;
  maxPotentialFP: number;
  minPotentialFP: number;
  maxPotentialFTR: number;
  minPotentialFTR: number;
  lockedShares: number;
}

export interface NormalizedFootballEvent {
  matchId: string;
  minute: number;
  timestamp?: Date;
  eventType: FootballEventType;
  playerId?: string;
  playerExternalId?: string;
  teamId?: string;
  value?: number;
  metadata?: Record<string, any>;
}

export interface NormalizedPlayerStats {
  assetId: string;
  matchId: string;
  eligibility: PlayerMatchEligibility;
  minutesPlayed: number;
  goals: number;
  assists: number;
  shots: number;
  shotsOnTarget: number;
  keyPasses: number;
  yellowCards: number;
  redCards: number;
  foulsCommitted: number;
  foulsDrawn: number;
  teamWon?: boolean;
}

