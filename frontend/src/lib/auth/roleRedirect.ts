import type { UserRole } from "@/types/entities";

export const ROLE_HOME: Record<UserRole, string> = {
  donor: "/dashboard/donor",
  ngo: "/dashboard/ngo",
  institution: "/dashboard/institution",
  execution_partner: "/dashboard/execution",
  admin: "/dashboard/admin",
};
