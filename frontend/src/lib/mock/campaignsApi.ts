import type { Campaign, Category } from "@/types/entities";
import {
  MOCK_CAMPAIGNS,
  MOCK_CATEGORIES,
  MOCK_BENEFICIARIES,
  MOCK_MILESTONES,
  MOCK_FUND_ALLOCATIONS,
  MOCK_CAMPAIGN_UPDATES,
  MOCK_TRANSPARENCY_LOGS,
  MOCK_DOCUMENTS,
  getDonorCount,
} from "@/lib/mock/mockData";

// Every function here returns a Promise shaped exactly like the future
// GET /api/v1/campaigns/... response. Swapping this module for real
// Axios calls later requires zero changes in hooks/ or components/.
const NETWORK_DELAY_MS = 250;
function delay<T>(value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), NETWORK_DELAY_MS));
}

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

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  page: number;
  pageSize: number;
}

// Public listing only ever shows live/completed — draft/pending/rejected/
// archived are never donor-facing, per Architecture Freeze v1.0.
const PUBLIC_STATUSES = new Set(["live", "completed"]);

export const campaignsApi = {
  async list(filters: CampaignFilters = {}): Promise<PaginatedResponse<Campaign>> {
    let results = MOCK_CAMPAIGNS.filter((c) => PUBLIC_STATUSES.has(c.status));

    if (filters.status) {
      results = results.filter((c) => c.status === filters.status);
    }
    if (filters.search) {
      const q = filters.search.toLowerCase();
      results = results.filter((c) => c.title.toLowerCase().includes(q));
    }
    if (filters.categorySlug) {
      results = results.filter((c) => c.category?.slug === filters.categorySlug);
    }
    if (filters.countryCode) {
      results = results.filter((c) => c.location_country === filters.countryCode);
    }
    if (filters.minGoal !== undefined) {
      results = results.filter((c) => c.goal_amount >= filters.minGoal!);
    }
    if (filters.maxGoal !== undefined) {
      results = results.filter((c) => c.goal_amount <= filters.maxGoal!);
    }

    switch (filters.sort) {
      case "most_funded":
        results = [...results].sort((a, b) => b.funding_percentage - a.funding_percentage);
        break;
      case "goal_high_low":
        results = [...results].sort((a, b) => b.goal_amount - a.goal_amount);
        break;
      case "ending_soon":
        results = [...results].sort((a, b) => {
          if (!a.end_date) return 1;
          if (!b.end_date) return -1;
          return new Date(a.end_date).getTime() - new Date(b.end_date).getTime();
        });
        break;
      case "newest":
      default:
        results = [...results].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    }

    const page = filters.page ?? 1;
    const pageSize = filters.pageSize ?? 12;
    const start = (page - 1) * pageSize;
    const paged = results.slice(start, start + pageSize);

    return delay({ results: paged, count: results.length, page, pageSize });
  },

  async categories(): Promise<Category[]> {
    return delay(MOCK_CATEGORIES);
  },

  async detail(id: string) {
    const campaign = MOCK_CAMPAIGNS.find((c) => c.id === id);
    if (!campaign) throw new Error("Campaign not found");
    return delay({
      campaign,
      beneficiaries: MOCK_BENEFICIARIES[id] ?? [],
      milestones: MOCK_MILESTONES[id] ?? [],
      fundAllocation: MOCK_FUND_ALLOCATIONS[id] ?? null,
      updates: MOCK_CAMPAIGN_UPDATES[id] ?? [],
      transparencyLog: MOCK_TRANSPARENCY_LOGS[id] ?? [],
      documents: MOCK_DOCUMENTS[id] ?? [],
      donorCount: getDonorCount(id),
    });
  },

  async related(campaignId: string, categorySlug: string | undefined): Promise<Campaign[]> {
    const results = MOCK_CAMPAIGNS.filter(
      (c) => c.id !== campaignId && PUBLIC_STATUSES.has(c.status) && c.category?.slug === categorySlug
    );
    return delay(results.slice(0, 3));
  },

  /** NGO Dashboard's "My Campaigns" — unlike list(), this intentionally
   * returns every status (draft, pending_verification, rejected, etc.),
   * since an NGO needs to see and manage its own unpublished campaigns,
   * not just what the public sees. */
  async listMine(ngoUserId: string): Promise<Campaign[]> {
    const results = MOCK_CAMPAIGNS.filter((c) => c.created_by.id === ngoUserId);
    return delay(results);
  },
};
