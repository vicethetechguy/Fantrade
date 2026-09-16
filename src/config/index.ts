import dotenv from 'dotenv';
dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3001', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  databaseUrl: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/fantrade',
  jwtSecret: process.env.JWT_SECRET || 'fantrade-dev-secret-key-2026',

  // Economic Configuration
  // "0.4% is inherited prototype configuration and remains subject to final economic approval."
  economics: {
    buyFeeRate: parseFloat(process.env.DEFAULT_BUY_FEE_RATE || '0.004'),
    sellFeeRate: parseFloat(process.env.DEFAULT_SELL_FEE_RATE || '0.004'),
    swapFeeRate: parseFloat(process.env.DEFAULT_SWAP_FEE_RATE || '0.004'),
    totalSharesPerAsset: 10_000_000,
  },

  marketSafety: {
    minOrderQuantity: 1,
    maxOrderQuantity: 1_000_000,
    minLimitPrice: 0.01,
    maxLimitPrice: 1_000_000.0,
  },
};
