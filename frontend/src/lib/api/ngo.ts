import { apiClient } from "@/lib/api/client";

export interface NgoMetrics {
  total_raised: number;
  live_campaigns_count: number;
  pending_verifications_count: number;
}

export const ngoApi = {
  async getMetrics(): Promise<NgoMetrics> {
    const { data } = await apiClient.get<NgoMetrics>("/analytics/ngo/");
    return data;
  },
};
