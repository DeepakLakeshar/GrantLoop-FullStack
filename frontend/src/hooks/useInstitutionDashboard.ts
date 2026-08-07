import { useQuery } from "@tanstack/react-query";
import { institutionApi } from "@/lib/api/institution";

export function useInstitutionDashboard() {
  return useQuery({
    queryKey: ["institution-dashboard"],
    queryFn: () => institutionApi.getDashboard(),
  });
}
