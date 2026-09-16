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
