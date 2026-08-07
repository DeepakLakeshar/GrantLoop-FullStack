import { apiClient } from "@/lib/api/client";
import type { DrfPaginatedResponse } from "@/lib/api/types";
import type { Beneficiary } from "@/types/entities";

export const beneficiariesApi = {
  async listForCampaign(campaignId: string): Promise<Beneficiary[]> {
    const { data } = await apiClient.get<DrfPaginatedResponse<Beneficiary>>("/beneficiaries/", {
      params: { campaign: campaignId, page_size: 100 },
    });
    return data.results;
  },
};
