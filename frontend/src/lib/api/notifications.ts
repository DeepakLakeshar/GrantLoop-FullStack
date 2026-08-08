import { apiClient } from "@/lib/api/client";
import type { DrfPaginatedResponse } from "@/lib/api/types";
import type { Notification } from "@/types/entities";

export const notificationsApi = {
  async list(): Promise<DrfPaginatedResponse<Notification>> {
    // The backend may return a plain array or a DRF‑paginated response.
    const { data } = await apiClient.get<any>("/notifications/");
    if (Array.isArray(data)) {
      // Convert plain array into a DRF‑like paginated object.
      return {
        results: data,
        count: data.length,
        next: null,
        previous: null,
      } as unknown as DrfPaginatedResponse<Notification>;
    }
    // Assume DRF paginated response already.
    return data as DrfPaginatedResponse<Notification>;
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
