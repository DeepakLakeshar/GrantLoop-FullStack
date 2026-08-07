import { apiClient } from "@/lib/api/client";
import type { DrfPaginatedResponse } from "@/lib/api/types";
import type { Donation } from "@/types/entities";

export const donationsApi = {
  async list(): Promise<DrfPaginatedResponse<Donation>> {
    const { data } = await apiClient.get<DrfPaginatedResponse<Donation>>("/donations/");
    return data;
  },

  async get(id: string): Promise<Donation> {
    const { data } = await apiClient.get<Donation>(`/donations/${id}/`);
    return data;
  },
};
