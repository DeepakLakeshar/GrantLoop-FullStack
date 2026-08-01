import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  HeartHandshake,
  BarChart3,
  ShieldCheck,
  Settings,
  HelpCircle,
  LogOut,
  FileCheck2,
  Wallet,
  Users,
  ScrollText,
} from "lucide-react";
import type { UserRole } from "@/types/entities";

interface SidebarLink {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

// One nav config per role — same visual component, different links.
// This is the "DashboardSidebar (variant per role)" from the frontend review.
const ROLE_LINKS: Record<UserRole, SidebarLink[]> = {
  donor: [
    { to: "/dashboard/donor", label: "Overview", icon: LayoutDashboard },
    { to: "/dashboard/donor/donations", label: "My Donations", icon: HeartHandshake },
    { to: "/dashboard/donor/impact", label: "Impact Reports", icon: BarChart3 },
    { to: "/dashboard/donor/verification", label: "Verification Hub", icon: ShieldCheck },
  ],
  ngo: [
    { to: "/dashboard/ngo", label: "My Campaigns", icon: LayoutDashboard },
    { to: "/submit-case", label: "Submit Case", icon: FileCheck2 },
  ],
  institution: [
    { to: "/dashboard/institution", label: "Overview", icon: LayoutDashboard },
    { to: "/verify", label: "Verification Queue", icon: ShieldCheck },
    { to: "/dashboard/institution/fund-releases", label: "Fund Releases", icon: Wallet },
  ],
  execution_partner: [
    { to: "/dashboard/execution", label: "Assigned Milestones", icon: LayoutDashboard },
  ],
  admin: [
    { to: "/dashboard/admin", label: "Overview", icon: LayoutDashboard },
    { to: "/dashboard/admin/users", label: "Users & NGOs", icon: Users },
    { to: "/dashboard/admin/audit", label: "Audit Log", icon: ScrollText },
  ],
};

interface DashboardSidebarProps {
  role: UserRole;
  title: string;
  subtitle?: string;
}

export function DashboardSidebar({ role, title, subtitle }: DashboardSidebarProps) {
  const links = ROLE_LINKS[role];

  return (
    <aside className="h-screen w-64 fixed left-0 top-0 bg-surface-container-low border-r border-outline-variant flex flex-col p-6 space-y-4 pt-20">
      <div className="mb-6">
        <h2 className="text-headline-sm font-headline-sm font-bold text-primary">{title}</h2>
        {subtitle && <p className="text-label-caps font-label-caps text-on-surface-variant">{subtitle}</p>}
      </div>
      <nav className="flex-grow space-y-2">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end
            className={({ isActive }) =>
              `flex items-center gap-3 p-3 rounded-lg transition-colors active:scale-95 ${
                isActive
                  ? "bg-secondary-container text-on-secondary-container font-bold"
                  : "text-on-surface-variant hover:bg-surface-container-high"
              }`
            }
          >
            <Icon className="w-5 h-5" />
            <span className="font-body-md">{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-outline-variant pt-4 space-y-2">
        <NavLink
          to="/settings"
          className="flex items-center gap-3 p-2 text-on-surface-variant hover:text-primary transition-colors"
        >
          <Settings className="w-5 h-5" />
          <span className="font-label-caps">Settings</span>
        </NavLink>
        <NavLink
          to="/help"
          className="flex items-center gap-3 p-2 text-on-surface-variant hover:text-primary transition-colors"
        >
          <HelpCircle className="w-5 h-5" />
          <span className="font-label-caps">Help Center</span>
        </NavLink>
        <button className="flex items-center gap-3 p-2 text-on-surface-variant hover:text-error transition-colors w-full text-left">
          <LogOut className="w-5 h-5" />
          <span className="font-label-caps">Log Out</span>
        </button>
      </div>
    </aside>
  );
}
