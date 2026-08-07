import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api/analytics";
import { donationsApi } from "@/lib/api/donations";

export function useDonorMetrics() {
  return useQuery({
    queryKey: ["donor-metrics"],
    queryFn: () => analyticsApi.getDonorDashboard(),
  });
}

export function useDonorHistory() {
  return useQuery({
    queryKey: ["donor-history"],
    queryFn: () => donationsApi.list(),
  });
}
