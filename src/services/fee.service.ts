import { Prisma, PrismaClient } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';
import { config } from '../config/index.js';

export class FeeService {
  constructor(private prisma: PrismaClient | Prisma.TransactionClient = defaultPrisma) {}

  withTx(tx: Prisma.TransactionClient): FeeService {
    return new FeeService(tx);
  }

  /**
   * Retrieves the active fee configuration, falling back to default 0.4%.
   * "0.4% is inherited prototype configuration and remains subject to final economic approval."
   */
  async getFeeConfiguration() {
    let feeConfig = await this.prisma.feeConfiguration.findUnique({
      where: { id: 'default' },
    });

    if (!feeConfig) {
      // Lazy initialize default configuration
      const platformFeeAccount = await this.prisma.ledgerAccount.findFirst({
        where: { accountType: 'PLATFORM_FEES', walletId: null },
      });

      let feeAccountId = platformFeeAccount?.id;
      if (!feeAccountId) {
        const created = await this.prisma.ledgerAccount.create({
          data: {
            accountType: 'PLATFORM_FEES',
            balance: new Prisma.Decimal(0),
          },
        });
        feeAccountId = created.id;
      }

      feeConfig = await this.prisma.feeConfiguration.create({
        data: {
          id: 'default',
          buyFeeRate: new Prisma.Decimal(config.economics.buyFeeRate),
          sellFeeRate: new Prisma.Decimal(config.economics.sellFeeRate),
          swapFeeRate: new Prisma.Decimal(config.economics.swapFeeRate),
          feeAccountId,
          notes: '0.4% is inherited prototype configuration and remains subject to final economic approval.',
        },
      });
    }

    return feeConfig;
  }

  /**
   * Calculates fee amount for a given notional value and side.
   */
  async calculateFee(notionalAmount: number | Prisma.Decimal, side: 'BUY' | 'SELL' | 'SWAP') {
    const feeConfig = await this.getFeeConfiguration();
    const notionalDec = new Prisma.Decimal(notionalAmount);

    let rate = feeConfig.buyFeeRate;
    if (side === 'SELL') rate = feeConfig.sellFeeRate;
    if (side === 'SWAP') rate = feeConfig.swapFeeRate;

    const fee = notionalDec.mul(rate);
    return {
      feeRate: rate.toNumber(),
      feeAmount: fee,
      feeAccountId: feeConfig.feeAccountId,
    };
  }
}
