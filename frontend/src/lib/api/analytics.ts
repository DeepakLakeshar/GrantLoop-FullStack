import { apiClient } from "@/lib/api/client";
import type { AdminDashboardMetrics } from "@/types/analytics";

export const analyticsApi = {
  async getAdminDashboard(): Promise<AdminDashboardMetrics> {
    const { data } = await apiClient.get<AdminDashboardMetrics>("/analytics/admin/");
    return data;
  },

  async getDonorDashboard(): Promise<any> {
    const { data } = await apiClient.get<any>("/analytics/donor/");
    return data;
  },
};
