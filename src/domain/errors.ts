export class DomainError extends Error {
  public readonly code: string;
  public readonly statusCode: number;

  constructor(message: string, code: string, statusCode = 400) {
    super(message);
    this.name = 'DomainError';
    this.code = code;
    this.statusCode = statusCode;
  }
}

export class InsufficientFtrError extends DomainError {
  constructor(available: number, required: number) {
    super(
      `Insufficient $FTR balance (${available.toLocaleString('en-US')} available, ${required.toLocaleString('en-US')} required).`,
      'INSUFFICIENT_FTR',
      400
    );
  }
}

export class InsufficientSharesError extends DomainError {
  constructor(symbol: string, available: number, required: number) {
    super(
      `Insufficient available shares of ${symbol} (${available.toLocaleString('en-US')} available, ${required.toLocaleString('en-US')} requested).`,
      'INSUFFICIENT_SHARES',
      400
    );
  }
}

export class SelfTradeError extends DomainError {
  constructor(symbol: string) {
    super(
      `Self-trade prevented: cannot match order against your own resting order for ${symbol}.`,
      'SELF_TRADE_PREVENTED',
      400
    );
  }
}

export class OrderNotFoundError extends DomainError {
  constructor(orderId: string) {
    super(`Order ${orderId} not found.`, 'ORDER_NOT_FOUND', 404);
  }
}

export class OrderNotOpenError extends DomainError {
  constructor(orderId: string, currentStatus: string) {
    super(`Order ${orderId} cannot be cancelled because it is in status '${currentStatus}'.`, 'ORDER_NOT_OPEN', 400);
  }
}

export class MarketHaltedError extends DomainError {
  constructor(symbol: string) {
    super(`Trading is currently halted for ${symbol}.`, 'MARKET_HALTED', 403);
  }
}

export class DuplicateRequestError extends DomainError {
  constructor(key: string) {
    super(`Duplicate request with idempotency key '${key}'.`, 'DUPLICATE_REQUEST', 409);
  }
}

export class UnauthorizedError extends DomainError {
  constructor(message = 'Unauthorized request.') {
    super(message, 'UNAUTHORIZED', 401);
  }
}

export class InvalidOrderInputError extends DomainError {
  constructor(message: string) {
    super(message, 'INVALID_ORDER_INPUT', 400);
  }
}

export class InsufficientAvailableSharesError extends DomainError {
  constructor(symbol: string, available: number, requested: number) {
    super(
      `Insufficient available shares of ${symbol} to stake in FanPlay. Owned available: ${available}, requested stake: ${requested}.`,
      'INSUFFICIENT_AVAILABLE_SHARES',
      400
    );
  }
}

export class MatchStartedError extends DomainError {
  constructor(matchId: string) {
    super(`Cannot activate FanPlay: match ${matchId} has already reached or passed its activation cutoff point.`, 'MATCH_STARTED', 400);
  }
}

export class MarketDisabledError extends DomainError {
  constructor(tier: string) {
    super(`FanPlay market tier '${tier}' is currently disabled.`, 'MARKET_DISABLED', 403);
  }
}

export class OptionConflictError extends DomainError {
  constructor(message: string) {
    super(message, 'OPTION_CONFLICT', 400);
  }
}

export class InvalidSelectionError extends DomainError {
  constructor(message: string) {
    super(message, 'INVALID_SELECTION', 400);
  }
}

export class FanPlayNotFoundError extends DomainError {
  constructor(fanPlayId: string) {
    super(`FanPlay position ${fanPlayId} not found.`, 'FANPLAY_NOT_FOUND', 404);
  }
}

export class AlreadySettledError extends DomainError {
  constructor(fanPlayId: string) {
    super(`FanPlay position ${fanPlayId} has already been settled.`, 'ALREADY_SETTLED', 400);
  }
}

export class SettlementUnavailableError extends DomainError {
  constructor(reason: string) {
    super(`Settlement unavailable: ${reason}`, 'SETTLEMENT_UNAVAILABLE', 400);
  }
}

export class DataUnavailableError extends DomainError {
  constructor(source: string) {
    super(`Authoritative football data is currently unavailable from ${source}.`, 'DATA_UNAVAILABLE', 503);
  }
}

