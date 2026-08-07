import { useQuery } from "@tanstack/react-query";
import { ngoApi } from "@/lib/api/ngo";

export function useNgoMetrics() {
  return useQuery({
    queryKey: ["ngo-metrics"],
    queryFn: () => ngoApi.getMetrics(),
  });
}
