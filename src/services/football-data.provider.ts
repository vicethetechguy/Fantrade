import { PrismaClient, Prisma } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';
import {
  MatchStatus,
  FootballEventType,
  PlayerMatchEligibility,
  NormalizedFootballEvent,
  NormalizedPlayerStats,
} from '../domain/types.js';
import { DataUnavailableError } from '../domain/errors.js';

export interface IFootballDataProvider {
  getFixtures(params?: { status?: MatchStatus; limit?: number }): Promise<any[]>;
  getFixture(matchId: string): Promise<any | null>;
  getEvents(matchId: string): Promise<NormalizedFootballEvent[]>;
  getPlayerStats(matchId: string, assetId: string): Promise<NormalizedPlayerStats | null>;
  recordEvent(event: NormalizedFootballEvent): Promise<any>;
}

export class FootballDataProvider implements IFootballDataProvider {
  constructor(private prisma: PrismaClient | Prisma.TransactionClient = defaultPrisma) {}

  withTx(tx: Prisma.TransactionClient): FootballDataProvider {
    return new FootballDataProvider(tx);
  }

  async getFixtures(params?: { status?: MatchStatus; limit?: number }) {
    return this.prisma.matchFixture.findMany({
      where: params?.status ? { status: params.status } : undefined,
      take: params?.limit || 20,
      orderBy: { kickoffTime: 'asc' },
      include: {
        _count: { select: { options: true } },
      },
    });
  }

  async getFixture(matchId: string) {
    const fixture = await this.prisma.matchFixture.findUnique({
      where: { id: matchId },
      include: {
        events: { orderBy: { minute: 'asc' } },
        playerStats: { include: { asset: true } },
        options: true,
      },
    });
    return fixture;
  }

  async getEvents(matchId: string): Promise<NormalizedFootballEvent[]> {
    const records = await this.prisma.footballEventRecord.findMany({
      where: { matchId },
      orderBy: { minute: 'asc' },
    });

    return records.map((r) => ({
      matchId: r.matchId,
      minute: r.minute,
      timestamp: r.timestamp,
      eventType: r.eventType as FootballEventType,
      playerId: r.playerId || undefined,
      playerExternalId: r.playerExternalId || undefined,
      teamId: r.teamId || undefined,
      value: r.value ? r.value.toNumber() : undefined,
      metadata: r.metadata ? JSON.parse(r.metadata) : undefined,
    }));
  }

  async getPlayerStats(matchId: string, assetId: string): Promise<NormalizedPlayerStats | null> {
    const stat = await this.prisma.playerMatchStat.findUnique({
      where: { matchId_assetId: { matchId, assetId } },
      include: { match: true },
    });

    if (!stat) {
      return null;
    }

    // Determine team win if applicable
    const asset = await this.prisma.asset.findUnique({
      where: { id: assetId },
      include: { playerProfile: true, coachProfile: true },
    });
    const playerClub = asset?.playerProfile?.club || asset?.coachProfile?.club;

    let teamWon: boolean | undefined = undefined;
    if (playerClub && stat.match) {
      if (playerClub.toLowerCase().includes(stat.match.homeTeam.toLowerCase()) || stat.match.homeTeam.toLowerCase().includes(playerClub.toLowerCase())) {
        teamWon = stat.match.homeScore > stat.match.awayScore;
      } else if (playerClub.toLowerCase().includes(stat.match.awayTeam.toLowerCase()) || stat.match.awayTeam.toLowerCase().includes(playerClub.toLowerCase())) {
        teamWon = stat.match.awayScore > stat.match.homeScore;
      }
    }

    return {
      assetId: stat.assetId,
      matchId: stat.matchId,
      eligibility: stat.eligibility as PlayerMatchEligibility,
      minutesPlayed: stat.minutesPlayed,
      goals: stat.goals,
      assists: stat.assists,
      shots: stat.shots,
      shotsOnTarget: stat.shotsOnTarget,
      keyPasses: stat.keyPasses,
      yellowCards: stat.yellowCards,
      redCards: stat.redCards,
      foulsCommitted: stat.foulsCommitted,
      foulsDrawn: stat.foulsDrawn,
      teamWon,
    };
  }

  async recordEvent(event: NormalizedFootballEvent) {
    return this.prisma.footballEventRecord.create({
      data: {
        matchId: event.matchId,
        minute: event.minute,
        timestamp: event.timestamp || new Date(),
        eventType: event.eventType,
        playerId: event.playerId,
        playerExternalId: event.playerExternalId,
        teamId: event.teamId,
        value: event.value !== undefined ? new Prisma.Decimal(event.value) : undefined,
        metadata: event.metadata ? JSON.stringify(event.metadata) : undefined,
      },
    });
  }

  async updateMatchStatus(params: {
    matchId: string;
    status: MatchStatus;
    homeScore?: number;
    awayScore?: number;
    minute?: number;
    period?: string;
  }) {
    return this.prisma.matchFixture.update({
      where: { id: params.matchId },
      data: {
        status: params.status,
        homeScore: params.homeScore !== undefined ? params.homeScore : undefined,
        awayScore: params.awayScore !== undefined ? params.awayScore : undefined,
        minute: params.minute !== undefined ? params.minute : undefined,
        period: params.period !== undefined ? params.period : undefined,
      },
    });
  }
}
