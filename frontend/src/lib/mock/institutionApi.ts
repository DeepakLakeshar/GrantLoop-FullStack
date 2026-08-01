import {
  MOCK_CAMPAIGNS,
  MOCK_BENEFICIARIES,
  MOCK_VERIFICATIONS,
  MOCK_FUND_RELEASES,
  MOCK_MILESTONES,
} from "@/lib/mock/mockData";
import type { Campaign, Beneficiary, Verification, FundRelease } from "@/types/entities";

function delay<T>(data: T, ms = 300): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms));
}

export interface InstitutionDashboardData {
  pendingCampaigns: Campaign[];
  pendingBeneficiaries: (Beneficiary & { campaignTitle: string })[];
  pendingFundReleases: (FundRelease & { campaignTitle: string; milestoneTitle: string })[];
  recentlyApproved: (Verification & { campaignTitle: string })[];
  stats: { pending: number; approved: number; rejected: number };
}

/** Everything an institution needs to see in one screen, assembled from
 * the existing Campaign/Beneficiary/Verification/FundRelease/Milestone
 * mock data — no new fields, just filtering and joining what already
 * exists, mirroring how a real Django view would annotate/join these. */
export const institutionApi = {
  async getDashboard(): Promise<InstitutionDashboardData> {
    const allBeneficiaries = Object.entries(MOCK_BENEFICIARIES).flatMap(([campaignId, list]) =>
      list.map((b) => ({ ...b, campaignTitle: MOCK_CAMPAIGNS.find((c) => c.id === campaignId)?.title ?? campaignId }))
    );

    const allMilestones = Object.values(MOCK_MILESTONES).flat();

    const pendingFundReleases = MOCK_FUND_RELEASES.filter((fr) => fr.status === "pending").map((fr) => {
      const milestone = allMilestones.find((m) => m.id === fr.milestone);
      const campaign = MOCK_CAMPAIGNS.find((c) => c.id === milestone?.campaign);
      return { ...fr, campaignTitle: campaign?.title ?? "—", milestoneTitle: milestone?.title ?? "—" };
    });

    const recentlyApproved = MOCK_VERIFICATIONS.filter((v) => v.status === "approved")
      .map((v) => ({ ...v, campaignTitle: MOCK_CAMPAIGNS.find((c) => c.id === v.campaign)?.title ?? v.campaign }))
      .sort((a, b) => b.created_at.localeCompare(a.created_at));

    const stats = {
      pending: MOCK_VERIFICATIONS.filter((v) => v.status === "pending").length,
      approved: MOCK_VERIFICATIONS.filter((v) => v.status === "approved").length,
      rejected: MOCK_VERIFICATIONS.filter((v) => v.status === "rejected").length,
    };

    return delay({
      pendingCampaigns: MOCK_CAMPAIGNS.filter((c) => c.status === "pending_verification"),
      pendingBeneficiaries: allBeneficiaries.filter((b) => b.verification_status === "pending"),
      pendingFundReleases,
      recentlyApproved,
      stats,
    });
  },
};
