import { apiClient } from "@/lib/api/client";
import type { DrfPaginatedResponse } from "@/lib/api/types";
import type { ReportExport } from "@/types/entities";

export const reportsApi = {
  async getDonationsReport(): Promise<DrfPaginatedResponse<any>> {
    const { data } = await apiClient.get<DrfPaginatedResponse<any>>("/reports/donations/");
    return data;
  },

  async exportDonationsReport(format: string = "csv"): Promise<ReportExport> {
    const { data } = await apiClient.post<ReportExport>("/reports/donations/export/", { format });
    return data;
  },

  async getCampaignsReport(): Promise<DrfPaginatedResponse<any>> {
    const { data } = await apiClient.get<DrfPaginatedResponse<any>>("/reports/campaigns/");
    return data;
  },

  async exportCampaignsReport(format: string = "csv"): Promise<ReportExport> {
    const { data } = await apiClient.post<ReportExport>("/reports/campaigns/export/", { format });
    return data;
  },

  async getNgosReport(): Promise<DrfPaginatedResponse<any>> {
    const { data } = await apiClient.get<DrfPaginatedResponse<any>>("/reports/ngos/");
    return data;
  },

  async exportNgosReport(format: string = "csv"): Promise<ReportExport> {
    const { data } = await apiClient.post<ReportExport>("/reports/ngos/export/", { format });
    return data;
  },

  async getBeneficiariesReport(): Promise<DrfPaginatedResponse<any>> {
    const { data } = await apiClient.get<DrfPaginatedResponse<any>>("/reports/beneficiaries/");
    return data;
  },

  async exportBeneficiariesReport(format: string = "csv"): Promise<ReportExport> {
    const { data } = await apiClient.post<ReportExport>("/reports/beneficiaries/export/", { format });
    return data;
  },

  async getPayoutsReport(): Promise<DrfPaginatedResponse<any>> {
    const { data } = await apiClient.get<DrfPaginatedResponse<any>>("/reports/payouts/");
    return data;
  },

  async exportPayoutsReport(format: string = "csv"): Promise<ReportExport> {
    const { data } = await apiClient.post<ReportExport>("/reports/payouts/export/", { format });
    return data;
  },

  async getFinancialReport(): Promise<DrfPaginatedResponse<any>> {
    const { data } = await apiClient.get<DrfPaginatedResponse<any>>("/reports/financial/");
    return data;
  },

  async exportFinancialReport(format: string = "csv"): Promise<ReportExport> {
    const { data } = await apiClient.post<ReportExport>("/reports/financial/export/", { format });
    return data;
  },

  async getAuditLogsReport(): Promise<DrfPaginatedResponse<any>> {
    const { data } = await apiClient.get<DrfPaginatedResponse<any>>("/reports/audit-logs/");
    return data;
  },

  async exportAuditLogsReport(format: string = "csv"): Promise<ReportExport> {
    const { data } = await apiClient.post<ReportExport>("/reports/audit-logs/export/", { format });
    return data;
  },
};
