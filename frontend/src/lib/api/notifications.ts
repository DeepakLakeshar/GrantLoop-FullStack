import { apiClient } from "@/lib/api/client";
import type { DrfPaginatedResponse } from "@/lib/api/types";
import type { Notification } from "@/types/entities";

export const notificationsApi = {
  async list(): Promise<DrfPaginatedResponse<Notification>> {
    const { data } = await apiClient.get<DrfPaginatedResponse<Notification>>("/notifications/");
    return data;
  },

  async getUnreadCount(): Promise<number> {
    const { data } = await apiClient.get<{ count: number }>("/notifications/unread-count/");
    return data.count;
  },

  async markAsRead(id: string): Promise<void> {
    await apiClient.post(`/notifications/${id}/mark-read/`);
  },

  async markAllAsRead(): Promise<void> {
    await apiClient.post("/notifications/mark-all-read/");
  },
};
