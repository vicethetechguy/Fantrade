import { PrismaClient, Prisma } from '@prisma/client';
import { prisma as defaultPrisma } from '../database/client.js';

export interface TeamMemberAsset {
  assetId: string;
  symbol: string;
  type: 'PLAYER' | 'COACH';
  club?: string;
  position?: string;
  ownedShares: number;
}

export interface TeamExposureDistribution {
  assetId: string;
  allocatedShares: number;
}

export interface TeamBoostParameters {
  formation?: string;          // e.g. "4-3-3"
  coachBonusMultiplier?: number;
  chemistryScore?: number;    // e.g. 0-100
  boostStatus: 'TBD';
}

export class TeamBoostService {
  constructor(private prisma: PrismaClient | Prisma.TransactionClient = defaultPrisma) {}

  /**
   * Deterministically distributes a total team share stake equally across all eligible squad assets.
   * Total allocated shares across all assets will strictly equal totalStakeShares.
   */
  distributeEqualExposure(
    eligibleAssets: TeamMemberAsset[],
    totalStakeShares: number
  ): TeamExposureDistribution[] {
    const n = eligibleAssets.length;
    if (n === 0) {
      throw new Error('Cannot distribute exposure: squad contains zero eligible assets.');
    }

    const basePerAsset = Math.floor(totalStakeShares / n);
    const remainder = totalStakeShares % n;

    // Distribute base to all, and distribute 1 remainder share each to the first `remainder` assets
    // Sorted deterministically by assetId
    const sorted = [...eligibleAssets].sort((a, b) => a.assetId.localeCompare(b.assetId));

    return sorted.map((asset, index) => {
      const extra = index < remainder ? 1 : 0;
      return {
        assetId: asset.assetId,
        allocatedShares: basePerAsset + extra,
      };
    });
  }

  /**
   * Calculates the configurable team boost contribution on accumulated squad FP.
   * Per §43 & §44, the exact formula is documented as TBD and remains configurable.
   */
  calculateTeamBoost(
    accumulatedSquadFP: number,
    params: TeamBoostParameters = { boostStatus: 'TBD' }
  ): {
    boostMultiplier: number;
    boostContributionFP: number;
    finalTeamFP: number;
  } {
    // Configurable boost factor (default to 0 extra boost / 1.0x factor until approved by product)
    const multiplier = params.coachBonusMultiplier ?? 1.0;
    const boostContributionFP = Math.round(accumulatedSquadFP * (multiplier - 1.0));
    const finalTeamFP = accumulatedSquadFP + boostContributionFP;

    return {
      boostMultiplier: multiplier,
      boostContributionFP,
      finalTeamFP,
    };
  }
}
