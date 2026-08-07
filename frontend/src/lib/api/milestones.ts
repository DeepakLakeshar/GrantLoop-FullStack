import { apiClient } from "@/lib/api/client";
import type { DrfPaginatedResponse } from "@/lib/api/types";
import type { Milestone } from "@/types/entities";

export const milestonesApi = {
  async listForCampaign(campaignId: string): Promise<Milestone[]> {
    const { data } = await apiClient.get<DrfPaginatedResponse<Milestone>>("/milestones/", {
      params: { campaign: campaignId, page_size: 100 },
    });
    return data.results;
  },
};
