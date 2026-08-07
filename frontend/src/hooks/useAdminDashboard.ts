import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api/analytics";

export function useAdminDashboard() {
  return useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: () => analyticsApi.getAdminDashboard(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
