import { apiClient } from "@/lib/api/client";
import type { DrfPaginatedResponse } from "@/lib/api/types";
import type { FundRelease } from "@/types/entities";

export interface PayoutFilters {
  status?: "pending" | "approved" | "processing" | "completed" | "failed" | "rejected";
  page?: number;
  pageSize?: number;
}

export const payoutsApi = {
  async list(filters: PayoutFilters = {}): Promise<DrfPaginatedResponse<FundRelease>> {
    const params = new URLSearchParams();
    if (filters.status) params.append("status", filters.status);
    if (filters.page) params.append("page", filters.page.toString());
    if (filters.pageSize) params.append("page_size", filters.pageSize.toString());
    
    const { data } = await apiClient.get<DrfPaginatedResponse<FundRelease>>("/payouts/", { params });
    return data;
  },

  async get(id: string): Promise<FundRelease> {
    const { data } = await apiClient.get<FundRelease>(`/payouts/${id}/`);
    return data;
  },

  async approve(id: string, payload: { approved_amount?: number; admin_notes?: string }): Promise<FundRelease> {
    const { data } = await apiClient.post<FundRelease>(`/payouts/${id}/approve/`, payload);
    return data;
  },

  async reject(id: string, payload: { rejection_reason?: string; admin_notes?: string }): Promise<FundRelease> {
    const { data } = await apiClient.post<FundRelease>(`/payouts/${id}/reject/`, payload);
    return data;
  },

  async process(id: string, payload: { gateway_type?: string; account_reference?: string }): Promise<FundRelease> {
    const { data } = await apiClient.post<FundRelease>(`/payouts/${id}/process/`, payload);
    return data;
  },

  async complete(id: string, payload: { transfer_reference?: string }): Promise<FundRelease> {
    const { data } = await apiClient.post<FundRelease>(`/payouts/${id}/complete/`, payload);
    return data;
  },
};
