import { useQuery } from "@tanstack/react-query";
import { campaignsApi, type CampaignFilters } from "@/lib/mock/campaignsApi";

export function useCampaignList(filters: CampaignFilters) {
  return useQuery({
    queryKey: ["campaigns", filters],
    queryFn: () => campaignsApi.list(filters),
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => campaignsApi.categories(),
    staleTime: 5 * 60_000, // categories change rarely
  });
}

export function useCampaignDetail(id: string | undefined) {
  return useQuery({
    queryKey: ["campaign", id],
    queryFn: () => campaignsApi.detail(id!),
    enabled: !!id,
  });
}

export function useRelatedCampaigns(campaignId: string | undefined, categorySlug: string | undefined) {
  return useQuery({
    queryKey: ["related-campaigns", campaignId, categorySlug],
    queryFn: () => campaignsApi.related(campaignId!, categorySlug),
    enabled: !!campaignId,
  });
}

export function useMyCampaigns(ngoUserId: string | undefined) {
  return useQuery({
    queryKey: ["my-campaigns", ngoUserId],
    queryFn: () => campaignsApi.listMine(ngoUserId!),
    enabled: !!ngoUserId,
  });
}
