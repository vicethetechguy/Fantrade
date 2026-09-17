import { PrismaClient, Prisma } from '@prisma/client';
import { randomUUID } from 'crypto';

const prisma = new PrismaClient();

export async function seed() {
  console.log('[Seed] Starting deterministic development seed...');

  // Clear existing records in reverse dependency order
  await prisma.fanPlaySettlement.deleteMany();
  await prisma.fanPlayTeamLeg.deleteMany();
  await prisma.fanPlaySelection.deleteMany();
  await prisma.fanPlay.deleteMany();
  await prisma.fanPlayOption.deleteMany();
  await prisma.playerMatchStat.deleteMany();
  await prisma.footballEventRecord.deleteMany();
  await prisma.matchFixture.deleteMany();
  await prisma.fanPlayMarketConfig.deleteMany();
  await prisma.priceHistoryPoint.deleteMany();
  await prisma.tradeFill.deleteMany();
  await prisma.trade.deleteMany();
  await prisma.order.deleteMany();
  await prisma.swap.deleteMany();
  await prisma.shareReservation.deleteMany();
  await prisma.holding.deleteMany();
  await prisma.market.deleteMany();
  await prisma.playerProfile.deleteMany();
  await prisma.coachProfile.deleteMany();
  await prisma.asset.deleteMany();
  await prisma.ledgerEntry.deleteMany();
  await prisma.ledgerAccount.deleteMany();
  await prisma.wallet.deleteMany();
  await prisma.authSession.deleteMany();
  await prisma.user.deleteMany();
  await prisma.feeConfiguration.deleteMany();
  await prisma.idempotencyRecord.deleteMany();

  // 1. Create Platform System Accounts
  const treasuryAccount = await prisma.ledgerAccount.create({
    data: {
      accountType: 'PLATFORM_TREASURY',
      balance: new Prisma.Decimal(100_000_000), // Platform FTR pool
    },
  });

  const feeAccount = await prisma.ledgerAccount.create({
    data: {
      accountType: 'PLATFORM_FEES',
      balance: new Prisma.Decimal(0),
    },
  });

  await prisma.feeConfiguration.create({
    data: {
      id: 'default',
      buyFeeRate: new Prisma.Decimal(0.004),
      sellFeeRate: new Prisma.Decimal(0.004),
      swapFeeRate: new Prisma.Decimal(0.004),
      feeAccountId: feeAccount.id,
      notes: '0.4% is inherited prototype configuration and remains subject to final economic approval.',
    },
  });

  // 2. Create Users
  const demoUser = await prisma.user.create({
    data: {
      email: 'demo@fantrade.com',
      displayName: 'Alex Morgan',
    },
  });

  const trader1 = await prisma.user.create({
    data: {
      email: 'trader1@fantrade.com',
      displayName: 'Liquidity Provider 1',
    },
  });

  const trader2 = await prisma.user.create({
    data: {
      email: 'trader2@fantrade.com',
      displayName: 'Market Maker 2',
    },
  });

  // 3. Create Wallets and Initial FTR Ledger Deposits
  for (const user of [demoUser, trader1, trader2]) {
    const wallet = await prisma.wallet.create({
      data: {
        userId: user.id,
        currency: 'FTR',
        accounts: {
          create: [
            { accountType: 'USER_AVAILABLE', balance: new Prisma.Decimal(user.email === 'demo@fantrade.com' ? 128450 : 500000) },
            { accountType: 'USER_RESERVED', balance: new Prisma.Decimal(0) },
          ],
        },
      },
      include: { accounts: true },
    });

    const userAvailable = wallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;
    const initialDeposit = user.email === 'demo@fantrade.com' ? 128450 : 500000;

    // Double-entry record for deposit
    const txGroup = randomUUID();
    await prisma.ledgerEntry.createMany({
      data: [
        {
          transactionGroup: txGroup,
          accountId: treasuryAccount.id,
          entryType: 'DEBIT',
          amount: new Prisma.Decimal(initialDeposit),
          category: 'DEPOSIT',
          description: `Opening grant transfer to ${user.email}`,
        },
        {
          transactionGroup: txGroup,
          accountId: userAvailable.id,
          entryType: 'CREDIT',
          amount: new Prisma.Decimal(initialDeposit),
          category: 'DEPOSIT',
          description: 'Opening balance grant',
        },
      ],
    });
  }

  // 4. Create 12 Assets with exactly 10,000,000 total shares each
  const assetsData = [
    { type: 'PLAYER', symbol: '$Saka', name: 'Bukayo Saka', slug: 'saka', price: 48.20, refVal: 120_000_000, club: 'Arsenal', pos: 'RW', age: 24, num: 7 },
    { type: 'PLAYER', symbol: '$Bellingham', name: 'Jude Bellingham', slug: 'bellingham', price: 92.50, refVal: 180_000_000, club: 'Real Madrid', pos: 'CAM', age: 22, num: 5 },
    { type: 'PLAYER', symbol: '$Haaland', name: 'Erling Haaland', slug: 'haaland', price: 88.00, refVal: 180_000_000, club: 'Manchester City', pos: 'ST', age: 25, num: 9 },
    { type: 'PLAYER', symbol: '$Vinicius', name: 'Vinícius Júnior', slug: 'vinicius', price: 84.10, refVal: 150_000_000, club: 'Real Madrid', pos: 'LW', age: 25, num: 7 },
    { type: 'PLAYER', symbol: '$Mbappe', name: 'Kylian Mbappé', slug: 'mbappe', price: 98.40, refVal: 180_000_000, club: 'Real Madrid', pos: 'ST', age: 26, num: 9 },
    { type: 'PLAYER', symbol: '$Foden', name: 'Phil Foden', slug: 'foden', price: 72.30, refVal: 140_000_000, club: 'Manchester City', pos: 'CAM', age: 25, num: 47 },
    { type: 'PLAYER', symbol: '$Rodri', name: 'Rodri', slug: 'rodri', price: 68.00, refVal: 130_000_000, club: 'Manchester City', pos: 'CDM', age: 29, num: 16 },
    { type: 'PLAYER', symbol: '$Saliba', name: 'William Saliba', slug: 'saliba', price: 54.00, refVal: 90_000_000, club: 'Arsenal', pos: 'CB', age: 24, num: 2 },
    { type: 'PLAYER', symbol: '$Rice', name: 'Declan Rice', slug: 'rice', price: 58.50, refVal: 110_000_000, club: 'Arsenal', pos: 'CM', age: 26, num: 41 },
    { type: 'PLAYER', symbol: '$Palmer', name: 'Cole Palmer', slug: 'palmer', price: 64.20, refVal: 100_000_000, club: 'Chelsea', pos: 'RW', age: 23, num: 20 },
    { type: 'COACH', symbol: '$Arteta', name: 'Mikel Arteta', slug: 'arteta', price: 34.00, refVal: 40_000_000, club: 'Arsenal', form: '4-3-3', exp: 6 },
    { type: 'COACH', symbol: '$Guardiola', name: 'Pep Guardiola', slug: 'guardiola', price: 42.50, refVal: 50_000_000, club: 'Manchester City', form: '3-2-4-1', exp: 17 },
  ];

  const createdAssets: Record<string, any> = {};

  for (const a of assetsData) {
    const isPlayer = a.type === 'PLAYER';
    const totalShares = 10_000_000;
    // Distribute 10,000 shares to Demo User, 50,000 to Trader 1, remaining to Platform Treasury
    const demoShares = 10_000;
    const traderShares = 50_000;
    const circulating = demoShares + traderShares;
    const treasury = totalShares - circulating;

    const asset = await prisma.asset.create({
      data: {
        type: a.type as any,
        symbol: a.symbol,
        name: a.name,
        slug: a.slug,
        status: 'ACTIVE',
        referenceValuation: new Prisma.Decimal(a.refVal),
        currentPrice: new Prisma.Decimal(a.price),
        totalShares,
        circulatingShares: circulating,
        treasuryShares: treasury,
        ...(isPlayer
          ? {
              playerProfile: {
                create: {
                  club: a.club,
                  position: (a as any).pos,
                  nationality: 'Various',
                  age: (a as any).age,
                  jerseyNumber: (a as any).num,
                },
              },
            }
          : {
              coachProfile: {
                create: {
                  club: a.club,
                  preferredFormation: (a as any).form,
                  experienceYears: (a as any).exp,
                },
              },
            }),
        market: {
          create: {
            quoteAsset: 'FTR',
            status: 'ACTIVE',
            lastPrice: new Prisma.Decimal(a.price),
            bestBid: new Prisma.Decimal((a.price * 0.98).toFixed(2)),
            bestAsk: new Prisma.Decimal((a.price * 1.02).toFixed(2)),
            high24h: new Prisma.Decimal((a.price * 1.06).toFixed(2)),
            low24h: new Prisma.Decimal((a.price * 0.94).toFixed(2)),
            volume24h: new Prisma.Decimal(125000),
            change24h: new Prisma.Decimal(4.8),
          },
        },
      },
      include: { market: true },
    });

    createdAssets[a.symbol] = asset;

    // Allocate holdings:
    // Demo user holding
    await prisma.holding.create({
      data: {
        userId: demoUser.id,
        assetId: asset.id,
        quantity: demoShares,
        availableQuantity: demoShares,
        lockedQuantity: 0,
        averageCost: new Prisma.Decimal(a.price),
      },
    });

    // Trader 1 holding
    await prisma.holding.create({
      data: {
        userId: trader1.id,
        assetId: asset.id,
        quantity: traderShares,
        availableQuantity: traderShares,
        lockedQuantity: 0,
        averageCost: new Prisma.Decimal(a.price),
      },
    });

    // Seed realistic resting orders on book (from Trader 1 & Trader 2)
    // Resting Asks (Trader 1 selling shares)
    const askPrices = [a.price * 1.01, a.price * 1.02, a.price * 1.03];
    for (let i = 0; i < askPrices.length; i++) {
      const askPx = new Prisma.Decimal(askPrices[i].toFixed(2));
      const askQty = 500 * (i + 1);

      const order = await prisma.order.create({
        data: {
          userId: trader1.id,
          marketId: asset.market!.id,
          assetId: asset.id,
          side: 'SELL',
          type: 'LIMIT',
          quantity: askQty,
          remainingQuantity: askQty,
          limitPrice: askPx,
          status: 'OPEN',
        },
      });

      // Reserve shares for resting sell order
      await prisma.shareReservation.create({
        data: {
          holdingId: (await prisma.holding.findUnique({ where: { userId_assetId: { userId: trader1.id, assetId: asset.id } } }))!.id,
          userId: trader1.id,
          assetId: asset.id,
          quantity: askQty,
          purpose: 'ORDER',
          referenceId: order.id,
          status: 'ACTIVE',
        },
      });

      // Update holding available/locked
      await prisma.holding.update({
        where: { userId_assetId: { userId: trader1.id, assetId: asset.id } },
        data: {
          availableQuantity: { decrement: askQty },
          lockedQuantity: { increment: askQty },
        },
      });
    }

    // Resting Bids (Trader 2 bidding with FTR)
    const bidPrices = [a.price * 0.99, a.price * 0.98, a.price * 0.97];
    const trader2Wallet = await prisma.wallet.findUnique({ where: { userId: trader2.id }, include: { accounts: true } });
    const t2Available = trader2Wallet!.accounts.find((x) => x.accountType === 'USER_AVAILABLE')!;
    const t2Reserved = trader2Wallet!.accounts.find((x) => x.accountType === 'USER_RESERVED')!;

    for (let i = 0; i < bidPrices.length; i++) {
      const bidPx = new Prisma.Decimal(bidPrices[i].toFixed(2));
      const bidQty = 500 * (i + 1);
      const reqFtr = bidPx.mul(bidQty).mul(1.004);

      const order = await prisma.order.create({
        data: {
          userId: trader2.id,
          marketId: asset.market!.id,
          assetId: asset.id,
          side: 'BUY',
          type: 'LIMIT',
          quantity: bidQty,
          remainingQuantity: bidQty,
          limitPrice: bidPx,
          status: 'OPEN',
        },
      });

      // Reserve FTR
      await prisma.ledgerAccount.update({
        where: { id: t2Available.id },
        data: { balance: { decrement: reqFtr } },
      });
      await prisma.ledgerAccount.update({
        where: { id: t2Reserved.id },
        data: { balance: { increment: reqFtr } },
      });

      const txG = randomUUID();
      await prisma.ledgerEntry.createMany({
        data: [
          {
            transactionGroup: txG,
            accountId: t2Available.id,
            entryType: 'DEBIT',
            amount: reqFtr,
            category: 'RESERVATION',
            referenceId: order.id,
            description: `Reserve FTR for resting BUY order ${order.id}`,
          },
          {
            transactionGroup: txG,
            accountId: t2Reserved.id,
            entryType: 'CREDIT',
            amount: reqFtr,
            category: 'RESERVATION',
            referenceId: order.id,
            description: `Reserve FTR for resting BUY order ${order.id}`,
          },
        ],
      });
    }

    // Seed historical trade with valid foreign key order records
    const histBuyOrder = await prisma.order.create({
      data: {
        userId: demoUser.id,
        marketId: asset.market!.id,
        assetId: asset.id,
        side: 'BUY',
        type: 'LIMIT',
        quantity: 1000,
        remainingQuantity: 0,
        limitPrice: new Prisma.Decimal(a.price),
        status: 'FILLED',
        timeInForce: 'GTC',
      },
    });
    const histSellOrder = await prisma.order.create({
      data: {
        userId: trader1.id,
        marketId: asset.market!.id,
        assetId: asset.id,
        side: 'SELL',
        type: 'LIMIT',
        quantity: 1000,
        remainingQuantity: 0,
        limitPrice: new Prisma.Decimal(a.price),
        status: 'FILLED',
        timeInForce: 'GTC',
      },
    });

    const histTrade = await prisma.trade.create({
      data: {
        marketId: asset.market!.id,
        assetId: asset.id,
        buyerId: demoUser.id,
        sellerId: trader1.id,
        buyOrderId: histBuyOrder.id,
        sellOrderId: histSellOrder.id,
        price: new Prisma.Decimal(a.price),
        quantity: 1000,
        totalAmount: new Prisma.Decimal(a.price * 1000),
        buyerFee: new Prisma.Decimal(a.price * 1000 * 0.004),
        sellerFee: new Prisma.Decimal(a.price * 1000 * 0.004),
        takerSide: 'BUY',
        createdAt: new Date(Date.now() - 3600 * 1000), // 1 hour ago
      },
    });

    await prisma.tradeFill.createMany({
      data: [
        {
          orderId: histBuyOrder.id,
          tradeId: histTrade.id,
          fillPrice: new Prisma.Decimal(a.price),
          fillQuantity: 1000,
        },
        {
          orderId: histSellOrder.id,
          tradeId: histTrade.id,
          fillPrice: new Prisma.Decimal(a.price),
          fillQuantity: 1000,
        },
      ],
    });

    // Seed 1m, 15m, 1h price points
    const now = new Date();
    await prisma.priceHistoryPoint.create({
      data: {
        marketId: asset.market!.id,
        interval: '1h',
        timestamp: new Date(now.getTime() - 3600 * 1000),
        open: new Prisma.Decimal(a.price * 0.98),
        high: new Prisma.Decimal(a.price * 1.03),
        low: new Prisma.Decimal(a.price * 0.97),
        close: new Prisma.Decimal(a.price),
        volume: 125000,
      },
    });
  }

  // ============================================================
  // 9. Seed FanPlay Market Configurations (§10, §11, §12)
  // ============================================================
  console.log('[Seed] Seeding FanPlay Market Configurations...');
  const marketConfigs = [
    {
      id: 'SIMPLE',
      tier: 'SIMPLE' as const,
      name: 'Simple Market',
      description: 'One clear, decisive prediction with focused exposure.',
      minSelections: 1,
      maxSelections: 1,
      allowedCategories: JSON.stringify(['GOALS', 'ASSISTS', 'CARDS', 'MATCH_OUTCOME']),
      maxFromOptionGroup: 1,
      enabled: true,
    },
    {
      id: 'PRO',
      tier: 'PRO' as const,
      name: 'Pro Market',
      description: 'Several related tactical decisions across key attacking and possession metrics.',
      minSelections: 2,
      maxSelections: 4,
      allowedCategories: JSON.stringify(['GOALS', 'ASSISTS', 'SHOOTING', 'PLAYMAKING', 'DISCIPLINE']),
      maxFromOptionGroup: 1,
      enabled: true,
    },
    {
      id: 'ELITE',
      tier: 'ELITE' as const,
      name: 'Elite Market',
      description: 'Multi-category prediction matrix testing deep football intelligence.',
      minSelections: 3,
      maxSelections: 6,
      allowedCategories: JSON.stringify(['GOALS', 'SHOOTING', 'PLAYMAKING', 'DISCIPLINE', 'DEFENDING', 'MATCH_OUTCOME']),
      maxFromOptionGroup: 1,
      enabled: true,
    },
    {
      id: 'KILLER',
      tier: 'KILLER' as const,
      name: 'Killer Market',
      description: 'Complex, high-conviction player thesis spanning multiple match dimensions.',
      minSelections: 4,
      maxSelections: 8,
      allowedCategories: JSON.stringify(['GOALS', 'SHOOTING', 'PLAYMAKING', 'DISCIPLINE', 'DEFENDING', 'MATCH_OUTCOME']),
      maxFromOptionGroup: 1,
      enabled: true,
    },
    {
      id: 'VIYNX_MOVE',
      tier: 'VIYNX_MOVE' as const,
      name: 'Viynx Move',
      description: 'Unified player + team + match thesis for master sports strategists.',
      minSelections: 5,
      maxSelections: 10,
      allowedCategories: JSON.stringify(['GOALS', 'SHOOTING', 'PLAYMAKING', 'DISCIPLINE', 'DEFENDING', 'TEAM_RESULT', 'MATCH_OUTCOME']),
      maxFromOptionGroup: 2,
      enabled: true,
    },
    {
      id: 'VIYNX_MAX',
      tier: 'VIYNX_MAX' as const,
      name: 'Viynx Max',
      description: 'Maximum configurable prediction complexity with total squad and match exposure.',
      minSelections: 6,
      maxSelections: 14,
      allowedCategories: JSON.stringify(['GOALS', 'SHOOTING', 'PLAYMAKING', 'DISCIPLINE', 'DEFENDING', 'TEAM_RESULT', 'MATCH_OUTCOME']),
      maxFromOptionGroup: 2,
      enabled: true,
    },
  ];

  for (const mc of marketConfigs) {
    await prisma.fanPlayMarketConfig.create({ data: mc });
  }

  // ============================================================
  // 10. Seed Match Fixtures (§27)
  // ============================================================
  console.log('[Seed] Seeding Match Fixtures...');
  const tomorrow = new Date(Date.now() + 24 * 3600 * 1000);
  const nextDay = new Date(Date.now() + 48 * 3600 * 1000);

  const fixtureArsenalCity = await prisma.matchFixture.create({
    data: {
      homeTeam: 'Arsenal',
      awayTeam: 'Manchester City',
      competition: 'Premier League',
      venue: 'Emirates Stadium',
      kickoffTime: tomorrow,
      cutoffTime: tomorrow,
      status: 'SCHEDULED',
      homeScore: 0,
      awayScore: 0,
    },
  });

  const fixtureClasico = await prisma.matchFixture.create({
    data: {
      homeTeam: 'Real Madrid',
      awayTeam: 'Barcelona',
      competition: 'La Liga',
      venue: 'Santiago Bernabéu',
      kickoffTime: nextDay,
      cutoffTime: nextDay,
      status: 'SCHEDULED',
      homeScore: 0,
      awayScore: 0,
    },
  });

  // ============================================================
  // 11. Seed Prediction Options (§13, §14, §15, §16, §17)
  // ============================================================
  console.log('[Seed] Seeding FanPlay Prediction Options...');
  const sakaAsset = await prisma.asset.findUnique({ where: { symbol: '$Saka' } });
  const haalandAsset = await prisma.asset.findUnique({ where: { symbol: '$Haaland' } });
  const viniciusAsset = await prisma.asset.findUnique({ where: { symbol: '$Vinicius' } });

  if (sakaAsset) {
    // 1+ goal (Option Group: saka-goals)
    const optSakaGoal1 = await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'SIMPLE',
        matchId: fixtureArsenalCity.id,
        assetId: sakaAsset.id,
        category: 'GOALS',
        predictionType: 'THRESHOLD',
        difficulty: 'MEDIUM',
        label: 'Saka scores 1+ goal',
        description: 'Bukayo Saka scores at least one goal in regular time.',
        evaluationRule: JSON.stringify({ metric: 'goals', op: 'gte', value: 1 }),
        successFP: 5,
        failureFP: -5,
        optionGroup: 'saka-goals',
      },
    });

    // 2+ goals (Option Group: saka-goals, depends on 1+ goal)
    await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'PRO',
        matchId: fixtureArsenalCity.id,
        assetId: sakaAsset.id,
        category: 'GOALS',
        predictionType: 'THRESHOLD',
        difficulty: 'HARD',
        label: 'Saka scores 2+ goals',
        description: 'Bukayo Saka scores 2 or more goals in regular time.',
        evaluationRule: JSON.stringify({ metric: 'goals', op: 'gte', value: 2 }),
        successFP: 12,
        failureFP: -8,
        optionGroup: 'saka-goals',
        dependencies: JSON.stringify([optSakaGoal1.id]),
      },
    });

    // 3+ shots (Option Group: saka-shots)
    await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'PRO',
        matchId: fixtureArsenalCity.id,
        assetId: sakaAsset.id,
        category: 'SHOOTING',
        predictionType: 'THRESHOLD',
        difficulty: 'MEDIUM',
        label: 'Saka records 3+ shots',
        description: 'Bukayo Saka takes at least 3 total shots.',
        evaluationRule: JSON.stringify({ metric: 'shots', op: 'gte', value: 3 }),
        successFP: 6,
        failureFP: -6,
        optionGroup: 'saka-shots',
      },
    });

    // 2+ key passes (Option Group: saka-passes)
    await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'PRO',
        matchId: fixtureArsenalCity.id,
        assetId: sakaAsset.id,
        category: 'PLAYMAKING',
        predictionType: 'THRESHOLD',
        difficulty: 'EASY',
        label: 'Saka records 2+ key passes',
        description: 'Bukayo Saka creates 2 or more chances from open play or set pieces.',
        evaluationRule: JSON.stringify({ metric: 'key_passes', op: 'gte', value: 2 }),
        successFP: 4,
        failureFP: -4,
        optionGroup: 'saka-passes',
      },
    });

    // Saka avoids yellow card
    await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'ELITE',
        matchId: fixtureArsenalCity.id,
        assetId: sakaAsset.id,
        category: 'DISCIPLINE',
        predictionType: 'BOOLEAN',
        difficulty: 'EASY',
        label: 'Saka avoids a yellow card',
        description: 'Bukayo Saka receives no yellow or red disciplinary bookings.',
        evaluationRule: JSON.stringify({ metric: 'yellow', op: 'avoid' }),
        successFP: 3,
        failureFP: -5,
        optionGroup: 'saka-discipline',
      },
    });

    // Arsenal wins match
    await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'ELITE',
        matchId: fixtureArsenalCity.id,
        assetId: sakaAsset.id,
        category: 'MATCH_OUTCOME',
        predictionType: 'TEAM_RESULT',
        difficulty: 'MEDIUM',
        label: 'Arsenal wins match',
        description: 'Arsenal claims victory over Manchester City at the final whistle.',
        evaluationRule: JSON.stringify({ metric: 'team_result', op: 'eq', value: true }),
        successFP: 5,
        failureFP: -5,
        optionGroup: 'arsenal-win',
      },
    });
  }

  if (haalandAsset) {
    // Haaland scores 1+ goal
    await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'SIMPLE',
        matchId: fixtureArsenalCity.id,
        assetId: haalandAsset.id,
        category: 'GOALS',
        predictionType: 'THRESHOLD',
        difficulty: 'EASY',
        label: 'Haaland scores 1+ goal',
        description: 'Erling Haaland scores at least one goal in regular time.',
        evaluationRule: JSON.stringify({ metric: 'goals', op: 'gte', value: 1 }),
        successFP: 4,
        failureFP: -6,
        optionGroup: 'haaland-goals',
      },
    });

    // Haaland records 4+ shots
    await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'PRO',
        matchId: fixtureArsenalCity.id,
        assetId: haalandAsset.id,
        category: 'SHOOTING',
        predictionType: 'THRESHOLD',
        difficulty: 'MEDIUM',
        label: 'Haaland records 4+ shots',
        description: 'Erling Haaland attempts 4 or more shots on goal.',
        evaluationRule: JSON.stringify({ metric: 'shots', op: 'gte', value: 4 }),
        successFP: 6,
        failureFP: -6,
        optionGroup: 'haaland-shots',
      },
    });
  }

  if (viniciusAsset) {
    await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'SIMPLE',
        matchId: fixtureClasico.id,
        assetId: viniciusAsset.id,
        category: 'GOALS',
        predictionType: 'THRESHOLD',
        difficulty: 'MEDIUM',
        label: 'Vinícius scores 1+ goal',
        description: 'Vinícius Júnior scores at least one goal in El Clásico.',
        evaluationRule: JSON.stringify({ metric: 'goals', op: 'gte', value: 1 }),
        successFP: 5,
        failureFP: -5,
        optionGroup: 'vini-goals',
      },
    });
  }

  console.log('[Seed] Deterministic development seed successfully completed.');
}

if (process.argv[1]?.endsWith('seed.ts') || process.argv[1]?.endsWith('seed.js')) {
  seed()
    .catch((e) => {
      console.error('[Seed Error]:', e);
      process.exit(1);
    })
    .finally(async () => {
      await prisma.$disconnect();
    });
}

