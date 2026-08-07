import { useQuery } from "@tanstack/react-query";
import { payoutsApi, type PayoutFilters } from "@/lib/api/payouts";

export function usePayoutsList(filters: PayoutFilters) {
  return useQuery({
    queryKey: ["payouts", filters],
    queryFn: () => payoutsApi.list(filters),
  });
}
