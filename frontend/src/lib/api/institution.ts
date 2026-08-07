import { apiClient } from "@/lib/api/client";
import type { DrfPaginatedResponse } from "@/lib/api/types";
import type { Campaign, Beneficiary, Verification, FundRelease } from "@/types/entities";

export interface InstitutionDashboardData {
  pendingCampaigns: Campaign[];
  pendingBeneficiaries: (Beneficiary & { campaignTitle: string })[];
  pendingFundReleases: (FundRelease & { campaignTitle: string; milestoneTitle: string })[];
  recentlyApproved: (Verification & { campaignTitle: string })[];
  stats: { pending: number; approved: number; rejected: number };
}

export const institutionApi = {
  async getDashboard(): Promise<InstitutionDashboardData> {
    const [
      { data: campaignsRes },
      { data: beneficiariesRes },
      { data: payoutsRes },
      { data: approvedVerificationsRes },
      { data: pendingVerificationsRes },
      { data: rejectedVerificationsRes },
    ] = await Promise.all([
      apiClient.get<DrfPaginatedResponse<Campaign>>("/campaigns/", {
        params: { status: "pending_verification", page_size: 10 },
      }),
      apiClient.get<DrfPaginatedResponse<Beneficiary>>("/beneficiaries/", {
        params: { verification_status: "pending", page_size: 10 },
      }),
      apiClient.get<DrfPaginatedResponse<FundRelease>>("/payouts/", {
        params: { status: "pending", page_size: 10 },
      }),
      apiClient.get<DrfPaginatedResponse<Verification>>("/verifications/", {
        params: { status: "approved", page_size: 10 },
      }),
      apiClient.get<DrfPaginatedResponse<Verification>>("/verifications/", {
        params: { status: "pending", page_size: 1 },
      }),
      apiClient.get<DrfPaginatedResponse<Verification>>("/verifications/", {
        params: { status: "rejected", page_size: 1 },
      }),
    ]);

    // Enhance beneficiaries with campaign titles (the mock expected this)
    // The backend serializer might not include campaignTitle, so we just fallback to the campaign ID or try to fetch it if really needed,
    // but typically DRF might nest it or we just use ID for now to avoid N+1 on frontend
    const pendingBeneficiaries = beneficiariesRes.results.map((b) => ({
      ...b,
      campaignTitle: (b as any).campaign_title ?? b.campaign,
    }));

    const pendingFundReleases = payoutsRes.results.map((fr) => ({
      ...fr,
      campaignTitle: (fr as any).campaign_title ?? fr.milestone, // Backend payout usually has campaign
      milestoneTitle: (fr as any).milestone_title ?? fr.milestone,
    }));

    const recentlyApproved = approvedVerificationsRes.results.map((v) => ({
      ...v,
      campaignTitle: (v as any).campaign_title ?? v.campaign,
    }));

    return {
      pendingCampaigns: campaignsRes.results,
      pendingBeneficiaries,
      pendingFundReleases,
      recentlyApproved,
      stats: {
        pending: pendingVerificationsRes.count,
        approved: approvedVerificationsRes.count,
        rejected: rejectedVerificationsRes.count,
      },
    };
  },
};
