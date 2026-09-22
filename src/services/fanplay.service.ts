import { PrismaClient, Prisma } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';
import { OwnershipService } from './ownership.service.js';
import { LedgerService } from './ledger.service.js';
import { FanPlayEvaluationService } from './evaluation.service.js';
import { FootballDataProvider } from './football-data.provider.js';
import { RiskPolicyService } from './risk-policy.service.js';
import { TeamBoostService } from './team-boost.service.js';
import {
  CreateFanPlayInput,
  FanPlayPreview,
  FanPlayStatus,
  MarketTier,
  EvaluationRule,
  NormalizedPlayerStats,
} from '../domain/types.js';
import {
  DomainError,
  InsufficientAvailableSharesError,
  MatchStartedError,
  MarketDisabledError,
  OptionConflictError,
  InvalidSelectionError,
  FanPlayNotFoundError,
  AlreadySettledError,
  SettlementUnavailableError,
} from '../domain/errors.js';
import { randomUUID } from 'crypto';

export class FanPlayService {
  private ownershipService: OwnershipService;
  private ledgerService: LedgerService;
  private evaluationService: FanPlayEvaluationService;
  private footballDataProvider: FootballDataProvider;
  private riskPolicyService: RiskPolicyService;
  private teamBoostService: TeamBoostService;

  constructor(private prisma: PrismaClient | Prisma.TransactionClient = defaultPrisma) {
    this.ownershipService = new OwnershipService(this.prisma);
    this.ledgerService = new LedgerService(this.prisma);
    this.evaluationService = new FanPlayEvaluationService();
    this.footballDataProvider = new FootballDataProvider(this.prisma);
    this.riskPolicyService = new RiskPolicyService(this.prisma);
    this.teamBoostService = new TeamBoostService(this.prisma);
  }

  withTx(tx: Prisma.TransactionClient): FanPlayService {
    return new FanPlayService(tx);
  }

  // ============================================================
  // MARKET CONFIGURATIONS & ELIGIBILITY (§10, §11, §12)
  // ============================================================

  async getMarkets() {
    return this.prisma.fanPlayMarketConfig.findMany({
      where: { enabled: true },
      orderBy: { tier: 'asc' },
    });
  }

  async getEligibleAssets(userId: string) {
    const holdings = await this.prisma.holding.findMany({
      where: { userId, availableQuantity: { gt: 0 } },
      include: {
        asset: {
          include: {
            playerProfile: true,
            coachProfile: true,
            market: true,
          },
        },
      },
    });

    return holdings.map((h) => ({
      id: h.assetId,
      assetId: h.assetId,
      symbol: h.asset.symbol,
      name: h.asset.name,
      type: h.asset.type,
      team: h.asset.playerProfile?.club || h.asset.coachProfile?.club || 'Club',
      club: h.asset.playerProfile?.club || h.asset.coachProfile?.club || 'Club',
      position: h.asset.playerProfile?.position || 'Coach',
      totalQuantity: h.quantity,
      ownedQuantity: h.quantity,
      availableQuantity: h.availableQuantity,
      lockedQuantity: h.lockedQuantity,
      currentPrice: h.asset.currentPrice.toNumber(),
    }));
  }

  async getOptions(params: {
    matchId?: string;
    assetId?: string;
    marketTier?: MarketTier;
  }) {
    return this.prisma.fanPlayOption.findMany({
      where: {
        matchId: params.matchId,
        assetId: params.assetId !== undefined ? params.assetId : undefined,
        marketConfig: params.marketTier ? { tier: params.marketTier } : undefined,
        status: 'ACTIVE',
      },
      include: {
        asset: true,
        match: true,
      },
    });
  }

  // ============================================================
  // PREVIEW CALCULATION (§6, §51)
  // ============================================================

  async previewFanPlay(input: CreateFanPlayInput): Promise<FanPlayPreview> {
    const match = await this.prisma.matchFixture.findUnique({
      where: { id: input.matchId },
    });
    if (!match) throw new Error(`Match ${input.matchId} not found.`);

    let assetSymbol = input.assetSymbol;
    let assetId = '';
    if (input.assetSymbol) {
      const asset = await this.prisma.asset.findUnique({ where: { symbol: input.assetSymbol } });
      if (!asset) throw new Error(`Asset ${input.assetSymbol} not found.`);
      assetId = asset.id;
      assetSymbol = asset.symbol;
    }

    const options = await this.prisma.fanPlayOption.findMany({
      where: { id: { in: input.selectedOptionIds } },
    });

    if (options.length === 0) {
      throw new InvalidSelectionError('At least one prediction option must be selected.');
    }

    const stake = input.stakedShares;
    const maxPotentialFP = options.reduce((sum, o) => sum + o.successFP * stake, 0);
    const minPotentialFP = options.reduce((sum, o) => sum + o.failureFP * stake, 0);

    return {
      assetSymbol,
      matchName: `${match.homeTeam} vs ${match.awayTeam}`,
      marketTier: input.marketTier,
      stakedShares: stake,
      selectionsCount: options.length,
      maxPotentialFP,
      minPotentialFP,
      maxPotentialFTR: maxPotentialFP / 1000,
      minPotentialFTR: minPotentialFP / 1000,
      lockedShares: stake,
    };
  }

  // ============================================================
  // TRANSACTIONAL ACTIVATION (§24, §25, §6, §7, §8)
  // ============================================================

  async activateFanPlay(input: CreateFanPlayInput) {
    if (this.prisma instanceof PrismaClient) {
      return this.prisma.$transaction(async (tx) => {
        return new FanPlayService(tx).activateFanPlay(input);
      });
    }

    // 1. Idempotency Check (§25)
    if (input.idempotencyKey) {
      const existing = await this.prisma.fanPlay.findUnique({
        where: { idempotencyKey: input.idempotencyKey },
        include: { selections: true },
      });
      if (existing) {
        return existing;
      }
    }

    // 2. Validate User
    const user = await this.prisma.user.findUnique({ where: { id: input.userId } });
    if (!user || user.status !== 'ACTIVE') {
      throw new DomainError('User not found or account is not active.', 'USER_INACTIVE', 403);
    }

    // 3. Validate Match & Cutoff (§27)
    const match = await this.prisma.matchFixture.findUnique({ where: { id: input.matchId } });
    if (!match) {
      throw new DomainError(`Match ${input.matchId} does not exist.`, 'MATCH_NOT_FOUND', 404);
    }
    const now = new Date();
    if (now >= match.cutoffTime || (match.status !== 'SCHEDULED' && match.status !== 'LINEUPS_CONFIRMED')) {
      throw new MatchStartedError(match.id);
    }

    // 4. Validate Market Configuration (§12)
    const marketConfig = await this.prisma.fanPlayMarketConfig.findUnique({
      where: { tier: input.marketTier },
    });
    if (!marketConfig || !marketConfig.enabled) {
      throw new MarketDisabledError(input.marketTier);
    }

    // 5. Validate Selection Count
    if (
      input.selectedOptionIds.length < marketConfig.minSelections ||
      input.selectedOptionIds.length > marketConfig.maxSelections
    ) {
      throw new InvalidSelectionError(
        `Market tier '${input.marketTier}' requires between ${marketConfig.minSelections} and ${marketConfig.maxSelections} selections (received: ${input.selectedOptionIds.length}).`
      );
    }

    // 6. Fetch Options & Validate Constraints (§15, §16, §17)
    const options = await this.prisma.fanPlayOption.findMany({
      where: { id: { in: input.selectedOptionIds }, matchId: match.id },
    });
    if (options.length !== input.selectedOptionIds.length) {
      throw new InvalidSelectionError('One or more selected prediction options are invalid or do not belong to this match.');
    }

    // Option Groups: Enforce maxFromOptionGroup (§15, §72)
    const groupCounts = new Map<string, number>();
    for (const opt of options) {
      if (opt.optionGroup) {
        const cur = groupCounts.get(opt.optionGroup) || 0;
        if (cur >= marketConfig.maxFromOptionGroup) {
          throw new OptionConflictError(
            `Option group conflict: only ${marketConfig.maxFromOptionGroup} selection is permitted from group '${opt.optionGroup}'.`
          );
        }
        groupCounts.set(opt.optionGroup, cur + 1);
      }
    }

    // Dependencies (§16): If option requires another option, it must be selected
    const selectedSet = new Set(input.selectedOptionIds);
    for (const opt of options) {
      if (opt.dependencies) {
        const requiredIds: string[] = JSON.parse(opt.dependencies);
        for (const reqId of requiredIds) {
          if (!selectedSet.has(reqId)) {
            throw new OptionConflictError(
              `Selection '${opt.label}' requires dependent option ${reqId} to also be selected.`
            );
          }
        }
      }
    }

    // Contradictions (§17): Cannot select contradictory options
    for (const opt of options) {
      if (opt.contradictions) {
        const prohibitedIds: string[] = JSON.parse(opt.contradictions);
        for (const pId of prohibitedIds) {
          if (selectedSet.has(pId)) {
            throw new OptionConflictError(
              `Selection contradiction: '${opt.label}' cannot be selected alongside option ${pId}.`
            );
          }
        }
      }
    }

    // 7. Validate Ownership & Stake (§6, §7, §8)
    if (input.stakedShares <= 0) {
      throw new InvalidSelectionError('Staked share quantity must be greater than zero.');
    }

    const type = input.type || 'INDIVIDUAL';
    let targetAssetId: string | undefined = undefined;
    let reservationId: string | undefined = undefined;

    if (type === 'INDIVIDUAL') {
      if (!input.assetSymbol) {
        throw new InvalidSelectionError('An individual FanPlay requires an assetSymbol.');
      }
      const asset = await this.prisma.asset.findUnique({ where: { symbol: input.assetSymbol } });
      if (!asset || asset.status !== 'ACTIVE') {
        throw new DomainError(`Asset ${input.assetSymbol} not found or inactive.`, 'ASSET_INACTIVE', 400);
      }
      targetAssetId = asset.id;

      // Ownership Check
      const holding = await this.prisma.holding.findUnique({
        where: { userId_assetId: { userId: input.userId, assetId: asset.id } },
      });
      const available = holding?.availableQuantity || 0;
      if (available < input.stakedShares) {
        throw new InsufficientAvailableSharesError(asset.symbol, available, input.stakedShares);
      }

      // 8. Atomically Reserve Shares (§7, §8, §62)
      const reservation = await this.ownershipService.reserveShares({
        userId: input.userId,
        assetId: asset.id,
        quantity: input.stakedShares,
        purpose: 'FANPLAY',
      });
      reservationId = reservation.id;
    } else {
      // TEAM Mode (§40, §41, §42, §76)
      // Equal distribution across eligible squad assets
      const eligibleHoldings = await this.prisma.holding.findMany({
        where: { userId: input.userId, availableQuantity: { gt: 0 } },
        include: { asset: true },
      });
      if (eligibleHoldings.length === 0) {
        throw new InsufficientAvailableSharesError('Squad', 0, input.stakedShares);
      }

      const teamAssets = eligibleHoldings.map((h) => ({
        assetId: h.assetId,
        symbol: h.asset.symbol,
        type: h.asset.type as 'PLAYER' | 'COACH',
        ownedShares: h.availableQuantity,
      }));

      const distribution = this.teamBoostService.distributeEqualExposure(teamAssets, input.stakedShares);

      // Verify each asset has sufficient available shares and reserve them
      for (const dist of distribution) {
        const h = eligibleHoldings.find((e) => e.assetId === dist.assetId);
        if (!h || h.availableQuantity < dist.allocatedShares) {
          throw new InsufficientAvailableSharesError(h?.asset.symbol || dist.assetId, h?.availableQuantity || 0, dist.allocatedShares);
        }
      }

      // Reserve the shares for the first asset as primary or lock individually
      // For team mode, we reserve the primary squad stake
      const primaryDist = distribution[0];
      const reservation = await this.ownershipService.reserveShares({
        userId: input.userId,
        assetId: primaryDist.assetId,
        quantity: input.stakedShares,
        purpose: 'FANPLAY',
      });
      reservationId = reservation.id;
      targetAssetId = primaryDist.assetId;
    }

    // 9. Create FanPlay Record (§22)
    const fanPlayId = randomUUID();
    const fanPlay = await this.prisma.fanPlay.create({
      data: {
        id: fanPlayId,
        userId: input.userId,
        type,
        assetId: targetAssetId,
        dreamClubId: input.dreamClubId,
        matchId: match.id,
        marketConfigId: marketConfig.id,
        stakedShares: input.stakedShares,
        status: 'ACTIVE',
        reservationId,
        idempotencyKey: input.idempotencyKey,
        teamExposure: input.teamExposure !== undefined ? new Prisma.Decimal(input.teamExposure) : undefined,
        activatedAt: new Date(),
      },
    });

    // Update reservation referenceId to point to the created fanPlay
    if (reservationId) {
      await this.prisma.shareReservation.update({
        where: { id: reservationId },
        data: { referenceId: fanPlay.id },
      });
    }

    // 10. Create Selections with Immutable Activation Snapshots (§23)
    for (const opt of options) {
      await this.prisma.fanPlaySelection.create({
        data: {
          fanPlayId: fanPlay.id,
          optionId: opt.id,
          assetId: opt.assetId || targetAssetId,
          label: opt.label,
          category: opt.category,
          predictionType: opt.predictionType,
          successFP: opt.successFP,
          failureFP: opt.failureFP,
          evaluationRuleSnapshot: opt.evaluationRule,
          evaluationResult: 'PENDING',
        },
      });
    }

    // Return active FanPlay with selections
    return this.prisma.fanPlay.findUniqueOrThrow({
      where: { id: fanPlay.id },
      include: {
        selections: true,
        asset: true,
        match: true,
        marketConfig: true,
      },
    });
  }

  // ============================================================
  // CANCELLATION (§26)
  // ============================================================

  async cancelFanPlay(userId: string, fanPlayId: string) {
    if (this.prisma instanceof PrismaClient) {
      return this.prisma.$transaction(async (tx) => {
        return new FanPlayService(tx).cancelFanPlay(userId, fanPlayId);
      });
    }

    const fanPlay = await this.prisma.fanPlay.findUnique({
      where: { id: fanPlayId },
      include: { match: true },
    });
    if (!fanPlay) throw new FanPlayNotFoundError(fanPlayId);
    if (fanPlay.userId !== userId) throw new DomainError('Unauthorized to cancel this FanPlay.', 'UNAUTHORIZED', 403);
    if (fanPlay.status !== 'ACTIVE') {
      throw new DomainError(`Cannot cancel FanPlay in status '${fanPlay.status}'.`, 'INVALID_STATUS', 400);
    }
    if (new Date() >= fanPlay.match.cutoffTime) {
      throw new MatchStartedError(fanPlay.matchId);
    }

    // Release locked shares (§35)
    if (fanPlay.reservationId) {
      await this.ownershipService.releaseShares(fanPlay.reservationId);
    }

    return this.prisma.fanPlay.update({
      where: { id: fanPlay.id },
      data: { status: 'CANCELLED' },
    });
  }

  // ============================================================
  // AUTHORITATIVE IDEMPOTENT SETTLEMENT (§36, §37, §38, §69-74)
  // ============================================================

  async settleFanPlay(fanPlayId: string, forceFinal = false) {
    if (this.prisma instanceof PrismaClient) {
      return this.prisma.$transaction(async (tx) => {
        return new FanPlayService(tx).settleFanPlay(fanPlayId, forceFinal);
      });
    }

    // 1. Load FanPlay
    const fanPlay = await this.prisma.fanPlay.findUnique({
      where: { id: fanPlayId },
      include: {
        selections: { include: { option: true } },
        match: true,
        asset: true,
        settlement: true,
      },
    });

    if (!fanPlay) throw new FanPlayNotFoundError(fanPlayId);

    // Idempotency check (§36, §74): If already settled, return existing settlement
    if (fanPlay.status === 'SETTLED' && fanPlay.settlement) {
      return {
        alreadySettled: true,
        settlement: fanPlay.settlement,
        fanPlay,
      };
    }

    // Verify match status (§21, §37)
    if (!forceFinal && fanPlay.match.status !== 'FULL_TIME') {
      throw new SettlementUnavailableError(
        `Match ${fanPlay.matchId} is not in final FULL_TIME state (current status: ${fanPlay.match.status}).`
      );
    }

    // 2. Fetch authoritative match events and player stats (§20, §54)
    const events = await this.footballDataProvider.getEvents(fanPlay.matchId);
    let playerStats: NormalizedPlayerStats | null = null;
    if (fanPlay.assetId) {
      playerStats = await this.footballDataProvider.getPlayerStats(fanPlay.matchId, fanPlay.assetId);
    }

    // 3. Evaluate each selection deterministically (§19, §30, §31)
    const evaluationInputs = fanPlay.selections.map((sel) => {
      let parsedRule: EvaluationRule;
      try {
        parsedRule = JSON.parse(sel.evaluationRuleSnapshot);
      } catch {
        parsedRule = { metric: 'goals', op: 'gte', value: 1 };
      }

      return {
        optionId: sel.optionId,
        label: sel.label,
        category: sel.category,
        predictionType: sel.predictionType,
        successFP: sel.successFP,
        failureFP: sel.failureFP,
        evaluationRule: parsedRule,
        assetId: sel.assetId || fanPlay.assetId || undefined,
        stakedShares: fanPlay.stakedShares,
      };
    });

    const evalResult = this.evaluationService.evaluateFanPlay(evaluationInputs, playerStats, events);

    // 4. Update individual selection results
    for (const selRes of evalResult.selections) {
      await this.prisma.fanPlaySelection.updateMany({
        where: { fanPlayId: fanPlay.id, optionId: selRes.optionId },
        data: {
          evaluationResult: selRes.result,
          resultFP: selRes.optionResultFP,
          optionContributionFP: selRes.optionContributionFP,
          explanation: selRes.explanation,
          evaluatedAt: new Date(),
        },
      });
    }

    // 5. Total FP and FTR Conversion (§4, §31, §33)
    // Conversion: 1,000 FP = 1 $FTR
    const totalFP = evalResult.totalFP;
    const ftrAmount = totalFP / 1000;
    const ftrAmountDec = new Prisma.Decimal(Math.abs(ftrAmount));

    // 6. Double-Entry Ledger Integration (§33, §38, §63)
    const ledgerTxGroup = randomUUID();
    const treasuryAccount = await this.ledgerService.getPlatformAccount('PLATFORM_TREASURY');
    const userWallet = await this.ledgerService.getOrCreateWallet(fanPlay.userId);
    const userAvailable = userWallet.accounts.find((a) => a.accountType === 'USER_AVAILABLE');

    if (!userAvailable) {
      throw new Error(`User available ledger account not found for user ${fanPlay.userId}`);
    }

    if (ftrAmount > 0) {
      // Positive settlement: Credit user from platform treasury (§33)
      await this.ledgerService.recordTransfer({
        transactionGroup: ledgerTxGroup,
        fromAccountId: treasuryAccount.id,
        toAccountId: userAvailable.id,
        amount: ftrAmountDec,
        category: 'FANPLAY_SETTLEMENT',
        referenceId: fanPlay.id,
        description: `FanPlay reward settlement: +${ftrAmount} FTR (${totalFP.toLocaleString()} FP)`,
      });
    } else if (ftrAmount < 0) {
      // Negative settlement: Debit user to platform treasury (§32, §33, §34, §71)
      const userBal = userAvailable.balance.toNumber();
      const riskResolution = this.riskPolicyService.resolveNegativeSettlementDebit(userBal, Math.abs(ftrAmount));

      if (riskResolution.effectiveDebit > 0) {
        await this.ledgerService.recordTransfer({
          transactionGroup: ledgerTxGroup,
          fromAccountId: userAvailable.id,
          toAccountId: treasuryAccount.id,
          amount: new Prisma.Decimal(riskResolution.effectiveDebit),
          category: 'FANPLAY_SETTLEMENT',
          referenceId: fanPlay.id,
          description: `FanPlay negative settlement: -${riskResolution.effectiveDebit} FTR (${totalFP.toLocaleString()} FP) [Policy: ${riskResolution.policyApplied}]`,
        });
      }
    }

    // 7. Release Share Reservation (§35, §71, §74)
    // Staked shares unlock and return to available quantity. Shares are NOT destroyed.
    if (fanPlay.reservationId) {
      await this.ownershipService.releaseShares(fanPlay.reservationId);
    }

    // 8. Create Immutable Settlement Record & Audit Trail (§36, §39)
    const settlementId = randomUUID();
    const auditSnapshot = JSON.stringify({
      fanPlayId: fanPlay.id,
      userId: fanPlay.userId,
      assetSymbol: fanPlay.asset?.symbol,
      stakedShares: fanPlay.stakedShares,
      totalFP,
      ftrAmount,
      selections: evalResult.selections,
      ledgerTxGroup,
      settledAt: new Date().toISOString(),
      ruleVersion: 'v2.0',
    });

    const settlement = await this.prisma.fanPlaySettlement.create({
      data: {
        id: settlementId,
        fanPlayId: fanPlay.id,
        userId: fanPlay.userId,
        totalFP,
        ftrAmount: new Prisma.Decimal(ftrAmount),
        ledgerTxGroup,
        status: 'COMPLETED',
        auditSnapshot,
      },
    });

    // 9. Mark FanPlay as SETTLED
    const updatedFanPlay = await this.prisma.fanPlay.update({
      where: { id: fanPlay.id },
      data: {
        status: 'SETTLED',
        totalFP,
        ftrSettlement: new Prisma.Decimal(ftrAmount),
        settledAt: new Date(),
      },
      include: {
        selections: true,
        settlement: true,
      },
    });

    return {
      alreadySettled: false,
      settlement,
      fanPlay: updatedFanPlay,
    };
  }

  // ============================================================
  // USER FANPLAY QUERIES & LIVE TRACKING (§29, §45, §46)
  // ============================================================

  async getUserFanPlays(userId: string, status?: FanPlayStatus) {
    return this.prisma.fanPlay.findMany({
      where: {
        userId,
        status: status ? status : undefined,
      },
      orderBy: { createdAt: 'desc' },
      include: {
        asset: true,
        match: true,
        marketConfig: true,
        selections: true,
        settlement: true,
      },
    });
  }

  async getFanPlayById(id: string) {
    const fp = await this.prisma.fanPlay.findUnique({
      where: { id },
      include: {
        asset: { include: { playerProfile: true, coachProfile: true } },
        match: { include: { events: true } },
        marketConfig: true,
        selections: { include: { option: true } },
        settlement: true,
      },
    });
    if (!fp) throw new FanPlayNotFoundError(id);
    return fp;
  }

  async getLiveFanPlay(id: string) {
    const fanPlay = await this.getFanPlayById(id);

    // If live, compute provisional FP
    let provisionalFP = 0;
    const events = await this.footballDataProvider.getEvents(fanPlay.matchId);
    let playerStats: NormalizedPlayerStats | null = null;
    if (fanPlay.assetId) {
      playerStats = await this.footballDataProvider.getPlayerStats(fanPlay.matchId, fanPlay.assetId);
    }

    if (fanPlay.status === 'LIVE' || fanPlay.status === 'ACTIVE') {
      const inputs = fanPlay.selections.map((s) => ({
        optionId: s.optionId,
        label: s.label,
        category: s.category,
        predictionType: s.predictionType,
        successFP: s.successFP,
        failureFP: s.failureFP,
        evaluationRule: JSON.parse(s.evaluationRuleSnapshot),
        assetId: s.assetId || fanPlay.assetId || undefined,
        stakedShares: fanPlay.stakedShares,
      }));
      const provEval = this.evaluationService.evaluateFanPlay(inputs, playerStats, events);
      provisionalFP = provEval.totalFP;
    } else if (fanPlay.totalFP !== null) {
      provisionalFP = fanPlay.totalFP;
    }

    return {
      fanPlay,
      events,
      playerStats,
      provisionalFP,
      provisionalFTR: provisionalFP / 1000,
      isProvisional: fanPlay.status !== 'SETTLED',
    };
  }
}
