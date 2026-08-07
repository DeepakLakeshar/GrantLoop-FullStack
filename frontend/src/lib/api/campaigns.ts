import { apiClient, buildUrlParams } from "@/lib/api/client";
import type { PaginatedResponse, DrfPaginatedResponse } from "@/lib/api/types";
import type {
  Campaign,
  Category,
  Beneficiary,
  Milestone,
  FundAllocation,
  CampaignUpdate,
  TransparencyLogEntry,
  GrantLoopDocument,
} from "@/types/entities";

export interface CampaignFilters {
  search?: string;
  categorySlug?: string;
  countryCode?: string;
  status?: "live" | "completed";
  minGoal?: number;
  maxGoal?: number;
  sort?: "newest" | "most_funded" | "ending_soon" | "goal_high_low";
  page?: number;
  pageSize?: number;
}

export const campaignsApi = {
  async list(filters: CampaignFilters = {}): Promise<PaginatedResponse<Campaign>> {
    const apiFilters: Record<string, string | number | undefined> = {
      status: filters.status,
      search: filters.search,
      category__slug: filters.categorySlug,
      location_country: filters.countryCode,
      min_goal: filters.minGoal,
      max_goal: filters.maxGoal,
    };

    const params = buildUrlParams(apiFilters);

    switch (filters.sort) {
      case "most_funded":
        params.append("ordering", "-funding_percentage");
        break;
      case "goal_high_low":
        params.append("ordering", "-goal_amount");
        break;
      case "ending_soon":
        params.append("ordering", "end_date");
        break;
      case "newest":
      default:
        params.append("ordering", "-created_at");
        break;
    }

    const page = filters.page ?? 1;
    const pageSize = filters.pageSize ?? 12;
    params.append("page", page.toString());
    params.append("page_size", pageSize.toString());

    const { data } = await apiClient.get<DrfPaginatedResponse<Campaign>>("/campaigns/", { params });

    return {
      results: data.results,
      count: data.count,
      page,
      pageSize,
    };
  },

  async categories(): Promise<Category[]> {
    const { data } = await apiClient.get<DrfPaginatedResponse<Category> | Category[]>("/categories/");
    if ("results" in data && Array.isArray(data.results)) {
      return data.results;
    }
    return data as Category[];
  },

  async detail(id: string) {
    const [
      { data: campaign },
      { data: beneficiariesResponse },
      { data: milestonesResponse },
      { data: updatesResponse },
      { data: documentsResponse },
      { data: transparencyResponse },
    ] = await Promise.all([
      apiClient.get<Campaign>(`/campaigns/${id}/`),
      apiClient.get<DrfPaginatedResponse<Beneficiary>>(`/beneficiaries/`, { params: { campaign: id } }),
      apiClient.get<DrfPaginatedResponse<Milestone>>(`/milestones/`, { params: { campaign: id } }),
      apiClient.get<DrfPaginatedResponse<CampaignUpdate>>(`/campaign-updates/`, { params: { campaign: id } }),
      apiClient.get<DrfPaginatedResponse<GrantLoopDocument>>(`/documents/`, { params: { campaign: id } }),
      apiClient.get<DrfPaginatedResponse<TransparencyLogEntry>>(`/transparency-logs/`, { params: { campaign: id } }),
    ]);

    let fundAllocation: FundAllocation | null = null;
    try {
        const { data: allocation } = await apiClient.get<FundAllocation>(`/campaigns/${id}/allocation/`);
        fundAllocation = allocation;
    } catch {
        // Ignored
    }

    let donorCount = 0;
    try {
        const { data: metrics } = await apiClient.get<{ donor_count: number }>(`/campaigns/${id}/metrics/`);
        donorCount = metrics.donor_count ?? 0;
    } catch {
        // Ignored
    }

    return {
      campaign,
      beneficiaries: beneficiariesResponse.results,
      milestones: milestonesResponse.results,
      fundAllocation,
      updates: updatesResponse.results,
      transparencyLog: transparencyResponse.results,
      documents: documentsResponse.results,
      donorCount,
    };
  },

  async related(campaignId: string, categorySlug: string | undefined): Promise<Campaign[]> {
    const params = new URLSearchParams();
    if (categorySlug) params.append("category__slug", categorySlug);
    params.append("page_size", "3");
    
    const { data } = await apiClient.get<DrfPaginatedResponse<Campaign>>("/campaigns/", { params });
    return data.results.filter(c => c.id !== campaignId).slice(0, 3);
  },

  async listMine(ngoUserId: string): Promise<Campaign[]> {
    const params = new URLSearchParams();
    params.append("created_by", ngoUserId);
    params.append("page_size", "50");

    const { data } = await apiClient.get<DrfPaginatedResponse<Campaign>>("/campaigns/", { params });
    return data.results;
  },

  async verifyCampaign(campaignId: string, status: "approved" | "rejected" | "more_info_requested", notes: string = "") {
    const { data } = await apiClient.post("/verifications/", {
      campaign: campaignId,
      status,
      notes,
    });
    return data;
  },
};
