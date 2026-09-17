import { describe, it, expect, beforeEach } from 'vitest';
import { prisma } from '../src/database/client.js';
import { FanPlayService } from '../src/services/fanplay.service.js';
import { OwnershipService } from '../src/services/ownership.service.js';
import { LedgerService } from '../src/services/ledger.service.js';
import { FootballDataProvider } from '../src/services/football-data.provider.js';
import { TeamBoostService } from '../src/services/team-boost.service.js';
import { ReconciliationService } from '../src/services/reconciliation.service.js';
import { seed } from '../prisma/seed.js';
import {
  InsufficientAvailableSharesError,
  OptionConflictError,
  MatchStartedError,
} from '../src/domain/errors.js';

describe('FanPlay Engine Production Tests (Prompt 4, §68–§76)', () => {
  let fanPlayService: FanPlayService;
  let ownershipService: OwnershipService;
  let ledgerService: LedgerService;
  let footballDataProvider: FootballDataProvider;
  let teamBoostService: TeamBoostService;
  let reconciliationService: ReconciliationService;

  beforeEach(async () => {
    await seed();
    fanPlayService = new FanPlayService();
    ownershipService = new OwnershipService();
    ledgerService = new LedgerService();
    footballDataProvider = new FootballDataProvider();
    teamBoostService = new TeamBoostService();
    reconciliationService = new ReconciliationService();
  });

  // ============================================================
  // §69: CRITICAL FP TEST (+5 / -5 with 500 shares)
  // ============================================================
  it('calculates FP as (Option FP × Staked Shares) and converts 1,000 FP = 1 $FTR for positive and negative outcomes (§69)', async () => {
    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;
    const sakaAsset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' } }))!;
    const fixture = (await prisma.matchFixture.findFirst({ where: { homeTeam: 'Arsenal' } }))!;

    // Set demoUser available Saka shares to 500
    await prisma.holding.update({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
      data: { quantity: 500, availableQuantity: 500, lockedQuantity: 0 },
    });

    // Reset demoUser available FTR to 1,000.00
    const wallet = await ledgerService.getOrCreateWallet(demoUser.id);
    const availAcc = wallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;
    await prisma.ledgerAccount.update({
      where: { id: availAcc.id },
      data: { balance: 1000.0 },
    });

    const optGoal = (await prisma.fanPlayOption.findFirst({
      where: { matchId: fixture.id, assetId: sakaAsset.id, label: 'Saka scores 1+ goal' },
    }))!;

    // 1. Activate FanPlay with 500 shares stake
    const fanPlay = await fanPlayService.activateFanPlay({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      matchId: fixture.id,
      marketTier: 'SIMPLE',
      selectedOptionIds: [optGoal.id],
      stakedShares: 500,
    });

    expect(fanPlay.status).toBe('ACTIVE');
    expect(fanPlay.stakedShares).toBe(500);

    // Verify shares are locked (§7, §8)
    const holdingAfterLock = await prisma.holding.findUnique({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
    });
    expect(holdingAfterLock?.lockedQuantity).toBe(500);
    expect(holdingAfterLock?.availableQuantity).toBe(0);

    // 2. Simulate match event: Saka scores at minute 24
    await footballDataProvider.recordEvent({
      matchId: fixture.id,
      minute: 24,
      eventType: 'GOAL',
      playerId: sakaAsset.id,
    });
    // Record player match stat
    await prisma.playerMatchStat.create({
      data: {
        matchId: fixture.id,
        assetId: sakaAsset.id,
        minutesPlayed: 90,
        goals: 1,
        shots: 2,
      },
    });

    // Mark match as FULL_TIME
    await footballDataProvider.updateMatchStatus({
      matchId: fixture.id,
      status: 'FULL_TIME',
      homeScore: 1,
      awayScore: 0,
    });

    // 3. Settle FanPlay
    const { settlement, fanPlay: settledFp } = await fanPlayService.settleFanPlay(fanPlay.id);

    // Success outcome:
    // +5 FP × 500 shares = +2,500 FP
    // 2,500 / 1,000 = +2.5 $FTR (§4, §69)
    expect(settledFp.status).toBe('SETTLED');
    expect(settlement.totalFP).toBe(2500);
    expect(settlement.ftrAmount.toNumber()).toBe(2.5);

    // Verify double-entry ledger: User credited with 2.5 FTR (§33, §38)
    const userBalanceAfter = await ledgerService.getBalance(demoUser.id);
    expect(userBalanceAfter.available).toBe(1002.5);

    // Verify share unlock: 500 shares returned to available (§35)
    const holdingAfterSettle = await prisma.holding.findUnique({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
    });
    expect(holdingAfterSettle?.lockedQuantity).toBe(0);
    expect(holdingAfterSettle?.availableQuantity).toBe(500);
    expect(holdingAfterSettle?.quantity).toBe(500);
  });

  // ============================================================
  // §70: MULTIPLE OPTION TEST (+5, +6, -3 with 500 shares)
  // ============================================================
  it('correctly calculates multiple option combinations: (+5, +6, -3) × 500 = 4,000 FP -> +4 FTR (§70)', async () => {
    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;
    const sakaAsset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' } }))!;
    const fixture = (await prisma.matchFixture.findFirst({ where: { homeTeam: 'Arsenal' } }))!;

    // Set demoUser available Saka shares to 500
    await prisma.holding.update({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
      data: { quantity: 500, availableQuantity: 500, lockedQuantity: 0 },
    });

    // Options in Pro/Elite market:
    // 1. Goal: +5 / -5 (Succeeds)
    // 2. 3+ shots: +6 / -6 (Succeeds)
    // 3. Avoid yellow: +3 / -5 (Fails -> -5 FP)
    // Let's create a specific test option with failureFP = -3 to exactly match §70
    const opt3 = await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'PRO',
        matchId: fixture.id,
        assetId: sakaAsset.id,
        category: 'PLAYMAKING',
        predictionType: 'THRESHOLD',
        difficulty: 'MEDIUM',
        label: 'Saka records 4+ key passes',
        description: 'Bukayo Saka creates 4 or more chances.',
        evaluationRule: JSON.stringify({ metric: 'key_passes', op: 'gte', value: 4 }),
        successFP: 5,
        failureFP: -3, // Exactly -3 on failure per §70
        optionGroup: 'saka-passes-test',
      },
    });

    const optGoal = (await prisma.fanPlayOption.findFirst({
      where: { matchId: fixture.id, assetId: sakaAsset.id, label: 'Saka scores 1+ goal' },
    }))!;
    const optShots = (await prisma.fanPlayOption.findFirst({
      where: { matchId: fixture.id, assetId: sakaAsset.id, label: 'Saka records 3+ shots' },
    }))!;

    // Activate FanPlay with the 3 options
    const fanPlay = await fanPlayService.activateFanPlay({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      matchId: fixture.id,
      marketTier: 'PRO',
      selectedOptionIds: [optGoal.id, optShots.id, opt3.id],
      stakedShares: 500,
    });

    // Player stats:
    // Goals: 1 (succeeds -> +5)
    // Shots: 4 (succeeds -> +6)
    // Key passes: 1 (fails target of 4 -> -3)
    await prisma.playerMatchStat.create({
      data: {
        matchId: fixture.id,
        assetId: sakaAsset.id,
        minutesPlayed: 90,
        goals: 1,
        shots: 4,
        keyPasses: 1,
      },
    });

    await footballDataProvider.updateMatchStatus({
      matchId: fixture.id,
      status: 'FULL_TIME',
      homeScore: 1,
      awayScore: 0,
    });

    const { settlement } = await fanPlayService.settleFanPlay(fanPlay.id);

    // Total: 5 + 6 - 3 = 8 FP
    // 8 FP × 500 shares = 4,000 FP
    // 4,000 / 1,000 = +4 FTR (§70)
    expect(settlement.totalFP).toBe(4000);
    expect(settlement.ftrAmount.toNumber()).toBe(4.0);
  });

  // ============================================================
  // §71: NEGATIVE SETTLEMENT TEST (-5, -6, -3 with 500 shares)
  // ============================================================
  it('correctly processes all-failing options (-5, -6, -3) × 500 = -7,000 FP -> -7 FTR debit and unlocks shares (§71)', async () => {
    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;
    const sakaAsset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' } }))!;
    const fixture = (await prisma.matchFixture.findFirst({ where: { homeTeam: 'Arsenal' } }))!;

    await prisma.holding.update({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
      data: { quantity: 500, availableQuantity: 500, lockedQuantity: 0 },
    });

    // Reset demoUser FTR to 100.00
    const wallet = await ledgerService.getOrCreateWallet(demoUser.id);
    const availAcc = wallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE')!;
    await prisma.ledgerAccount.update({
      where: { id: availAcc.id },
      data: { balance: 100.0 },
    });

    const opt1 = await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'PRO',
        matchId: fixture.id,
        assetId: sakaAsset.id,
        category: 'GOALS',
        predictionType: 'THRESHOLD',
        difficulty: 'HARD',
        label: 'Saka scores 3+ goals',
        description: 'Saka scores a hat-trick',
        evaluationRule: JSON.stringify({ metric: 'goals', op: 'gte', value: 3 }),
        successFP: 15,
        failureFP: -5,
        optionGroup: 'neg-test-1',
      },
    });

    const opt2 = await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'PRO',
        matchId: fixture.id,
        assetId: sakaAsset.id,
        category: 'SHOOTING',
        predictionType: 'THRESHOLD',
        difficulty: 'HARD',
        label: 'Saka records 6+ shots',
        description: 'Saka shoots 6+ times',
        evaluationRule: JSON.stringify({ metric: 'shots', op: 'gte', value: 6 }),
        successFP: 12,
        failureFP: -6,
        optionGroup: 'neg-test-2',
      },
    });

    const opt3 = await prisma.fanPlayOption.create({
      data: {
        marketConfigId: 'PRO',
        matchId: fixture.id,
        assetId: sakaAsset.id,
        category: 'PLAYMAKING',
        predictionType: 'THRESHOLD',
        difficulty: 'HARD',
        label: 'Saka records 5+ key passes',
        description: 'Saka creates 5+ chances',
        evaluationRule: JSON.stringify({ metric: 'key_passes', op: 'gte', value: 5 }),
        successFP: 10,
        failureFP: -3,
        optionGroup: 'neg-test-3',
      },
    });

    const fanPlay = await fanPlayService.activateFanPlay({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      matchId: fixture.id,
      marketTier: 'PRO',
      selectedOptionIds: [opt1.id, opt2.id, opt3.id],
      stakedShares: 500,
    });

    // Zero goals, 1 shot, 0 key passes -> all 3 fail (-5, -6, -3)
    await prisma.playerMatchStat.create({
      data: {
        matchId: fixture.id,
        assetId: sakaAsset.id,
        minutesPlayed: 90,
        goals: 0,
        shots: 1,
        keyPasses: 0,
      },
    });

    await footballDataProvider.updateMatchStatus({
      matchId: fixture.id,
      status: 'FULL_TIME',
      homeScore: 0,
      awayScore: 0,
    });

    const { settlement } = await fanPlayService.settleFanPlay(fanPlay.id);

    // Total FP: -14 FP × 500 = -7,000 FP
    // Settlement: -7.0 FTR (§71)
    expect(settlement.totalFP).toBe(-7000);
    expect(settlement.ftrAmount.toNumber()).toBe(-7.0);

    // Verify ledger debit: 100.0 - 7.0 = 93.0 FTR
    const balAfter = await ledgerService.getBalance(demoUser.id);
    expect(balAfter.available).toBe(93.0);

    // Verify shares unlock (§35, §71)
    const holdingAfter = await prisma.holding.findUnique({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
    });
    expect(holdingAfter?.lockedQuantity).toBe(0);
    expect(holdingAfter?.availableQuantity).toBe(500);
  });

  // ============================================================
  // §72: OPTION GROUP TEST
  // ============================================================
  it('prevents selecting multiple options from the same option group when maxFromOptionGroup is 1 (§72)', async () => {
    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;
    const fixture = (await prisma.matchFixture.findFirst({ where: { homeTeam: 'Arsenal' } }))!;
    const sakaAsset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' } }))!;

    const optGoal1 = (await prisma.fanPlayOption.findFirst({
      where: { matchId: fixture.id, assetId: sakaAsset.id, label: 'Saka scores 1+ goal' },
    }))!;
    const optGoal2 = (await prisma.fanPlayOption.findFirst({
      where: { matchId: fixture.id, assetId: sakaAsset.id, label: 'Saka scores 2+ goals' },
    }))!;

    // Both options belong to optionGroup: 'saka-goals'
    await expect(
      fanPlayService.activateFanPlay({
        userId: demoUser.id,
        assetSymbol: '$Saka',
        matchId: fixture.id,
        marketTier: 'PRO',
        selectedOptionIds: [optGoal1.id, optGoal2.id],
        stakedShares: 100,
      })
    ).rejects.toThrow(OptionConflictError);
  });

  // ============================================================
  // §73: OWNERSHIP CONCURRENCY TEST
  // ============================================================
  it('prevents total locked shares from exceeding owned shares during concurrent activations (§73)', async () => {
    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;
    const sakaAsset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' } }))!;
    const fixture = (await prisma.matchFixture.findFirst({ where: { homeTeam: 'Arsenal' } }))!;

    // Set owned = 500, available = 500, locked = 0
    await prisma.holding.update({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
      data: { quantity: 500, availableQuantity: 500, lockedQuantity: 0 },
    });

    const opt = (await prisma.fanPlayOption.findFirst({
      where: { matchId: fixture.id, assetId: sakaAsset.id, label: 'Saka scores 1+ goal' },
    }))!;

    // Two requests attempt to stake 300 shares simultaneously (total requested: 600 > 500 owned)
    const reqA = fanPlayService.activateFanPlay({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      matchId: fixture.id,
      marketTier: 'SIMPLE',
      selectedOptionIds: [opt.id],
      stakedShares: 300,
      idempotencyKey: 'concurrent-a-' + Date.now(),
    });

    const reqB = fanPlayService.activateFanPlay({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      matchId: fixture.id,
      marketTier: 'SIMPLE',
      selectedOptionIds: [opt.id],
      stakedShares: 300,
      idempotencyKey: 'concurrent-b-' + Date.now(),
    });

    const results = await Promise.allSettled([reqA, reqB]);
    const succeeded = results.filter((r) => r.status === 'fulfilled');
    const failed = results.filter((r) => r.status === 'rejected');

    // Exactly one should succeed and one should fail with InsufficientAvailableSharesError
    expect(succeeded.length).toBe(1);
    expect(failed.length).toBe(1);

    const holding = await prisma.holding.findUnique({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
    });
    expect(holding?.lockedQuantity).toBe(300);
    expect(holding?.availableQuantity).toBe(200);
    expect(holding?.quantity).toBe(500);
  });

  // ============================================================
  // §74: SETTLEMENT IDEMPOTENCY TEST
  // ============================================================
  it('ensures settling the same FanPlay twice executes exactly once with no duplicate ledger transfers or share releases (§74)', async () => {
    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;
    const sakaAsset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' } }))!;
    const fixture = (await prisma.matchFixture.findFirst({ where: { homeTeam: 'Arsenal' } }))!;

    await prisma.holding.update({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
      data: { quantity: 500, availableQuantity: 500, lockedQuantity: 0 },
    });

    const opt = (await prisma.fanPlayOption.findFirst({
      where: { matchId: fixture.id, assetId: sakaAsset.id, label: 'Saka scores 1+ goal' },
    }))!;

    const fanPlay = await fanPlayService.activateFanPlay({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      matchId: fixture.id,
      marketTier: 'SIMPLE',
      selectedOptionIds: [opt.id],
      stakedShares: 200,
    });

    await prisma.playerMatchStat.create({
      data: {
        matchId: fixture.id,
        assetId: sakaAsset.id,
        minutesPlayed: 90,
        goals: 1,
      },
    });

    await footballDataProvider.updateMatchStatus({
      matchId: fixture.id,
      status: 'FULL_TIME',
      homeScore: 1,
      awayScore: 0,
    });

    // First settlement
    const res1 = await fanPlayService.settleFanPlay(fanPlay.id);
    expect(res1.alreadySettled).toBe(false);

    const balAfter1 = await ledgerService.getBalance(demoUser.id);

    // Second settlement (idempotent call)
    const res2 = await fanPlayService.settleFanPlay(fanPlay.id);
    expect(res2.alreadySettled).toBe(true);
    expect(res2.settlement.id).toBe(res1.settlement.id);

    // Balance must NOT have changed again
    const balAfter2 = await ledgerService.getBalance(demoUser.id);
    expect(balAfter2.available).toBe(balAfter1.available);

    // Total settlements in database for this FanPlay must be exactly 1
    const count = await prisma.fanPlaySettlement.count({
      where: { fanPlayId: fanPlay.id },
    });
    expect(count).toBe(1);
  });

  // ============================================================
  // §75: EXCHANGE VS FANPLAY CONFLICT TEST
  // ============================================================
  it('prevents FanPlay from staking shares already reserved by the Exchange order book (§75)', async () => {
    const demoUser = (await prisma.user.findUnique({ where: { email: 'demo@fantrade.com' } }))!;
    const sakaAsset = (await prisma.asset.findUnique({ where: { symbol: '$Saka' } }))!;
    const fixture = (await prisma.matchFixture.findFirst({ where: { homeTeam: 'Arsenal' } }))!;

    // User owns 500 shares
    await prisma.holding.update({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
      data: { quantity: 500, availableQuantity: 500, lockedQuantity: 0 },
    });

    // Exchange reserves 300 shares for a resting sell order (§75)
    await ownershipService.reserveShares({
      userId: demoUser.id,
      assetId: sakaAsset.id,
      quantity: 300,
      purpose: 'ORDER',
    });

    const opt = (await prisma.fanPlayOption.findFirst({
      where: { matchId: fixture.id, assetId: sakaAsset.id, label: 'Saka scores 1+ goal' },
    }))!;

    // FanPlay attempts to stake 300 shares (only 200 available)
    await expect(
      fanPlayService.activateFanPlay({
        userId: demoUser.id,
        assetSymbol: '$Saka',
        matchId: fixture.id,
        marketTier: 'SIMPLE',
        selectedOptionIds: [opt.id],
        stakedShares: 300,
      })
    ).rejects.toThrow(InsufficientAvailableSharesError);

    // FanPlay can successfully stake <= 200 shares
    const fp = await fanPlayService.activateFanPlay({
      userId: demoUser.id,
      assetSymbol: '$Saka',
      matchId: fixture.id,
      marketTier: 'SIMPLE',
      selectedOptionIds: [opt.id],
      stakedShares: 200,
    });

    expect(fp.status).toBe('ACTIVE');

    const holdingFinal = await prisma.holding.findUnique({
      where: { userId_assetId: { userId: demoUser.id, assetId: sakaAsset.id } },
    });
    expect(holdingFinal?.availableQuantity).toBe(0);
    expect(holdingFinal?.lockedQuantity).toBe(500); // 300 from exchange + 200 from fanplay
  });

  // ============================================================
  // §76: TEAM MODE EQUAL EXPOSURE TEST
  // ============================================================
  it('distributes team stake exposure equally across squad assets and calculates boost (§76)', async () => {
    const assets = Array.from({ length: 11 }, (_, i) => ({
      assetId: `asset-${i + 1}`,
      symbol: `$Player${i + 1}`,
      type: 'PLAYER' as const,
      ownedShares: 1000,
    }));

    const distribution = teamBoostService.distributeEqualExposure(assets, 2000);

    // 2,000 shares across 11 players:
    // Base: 181 shares
    // Remainder: 9 players get 182, 2 players get 181
    const totalAllocated = distribution.reduce((sum, d) => sum + d.allocatedShares, 0);
    expect(totalAllocated).toBe(2000);

    const counts182 = distribution.filter((d) => d.allocatedShares === 182).length;
    const counts181 = distribution.filter((d) => d.allocatedShares === 181).length;
    expect(counts182).toBe(9);
    expect(counts181).toBe(2);

    // Team Boost calculation test
    const boostResult = teamBoostService.calculateTeamBoost(10000, {
      coachBonusMultiplier: 1.15,
      boostStatus: 'TBD',
    });
    expect(boostResult.boostContributionFP).toBe(1500);
    expect(boostResult.finalTeamFP).toBe(11500);
  });

  // ============================================================
  // RECONCILIATION AUDIT TEST
  // ============================================================
  it('maintains system-wide double-entry ledger balance and 10M share integrity after FanPlay settlements', async () => {
    const audit = await reconciliationService.runAudit();
    expect(audit.isHealthy).toBe(true);
    expect(audit.ledgerReconciliation.passed).toBe(true);
    expect(audit.ledgerReconciliation.totalDebits).toBe(audit.ledgerReconciliation.totalCredits);
    expect(audit.ledgerReconciliation.imbalance).toBe(0);
    expect(audit.assetReconciliation.passed).toBe(true);
    expect(audit.assetReconciliation.discrepancies.length).toBe(0);
    expect(audit.ownershipReconciliation.passed).toBe(true);
  });
});

