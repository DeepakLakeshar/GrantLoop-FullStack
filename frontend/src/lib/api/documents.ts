import { apiClient } from "@/lib/api/client";
import type { DrfPaginatedResponse } from "@/lib/api/types";
import type { GrantLoopDocument } from "@/types/entities";

export const documentsApi = {
  async upload(formData: FormData): Promise<GrantLoopDocument> {
    const { data } = await apiClient.post<GrantLoopDocument>("/documents/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/documents/${id}/`);
  },

  async listForCampaign(campaignId: string): Promise<GrantLoopDocument[]> {
    const { data } = await apiClient.get<DrfPaginatedResponse<GrantLoopDocument>>("/documents/", {
      params: { campaign: campaignId, page_size: 100 },
    });
    return data.results;
  },
};
