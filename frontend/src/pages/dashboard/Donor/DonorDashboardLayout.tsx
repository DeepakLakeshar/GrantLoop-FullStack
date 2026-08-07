import { Outlet } from "react-router-dom";
import { DashboardSidebar } from "@/components/layout/DashboardSidebar";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { useAuth } from "@/context/AuthContext";

export function DonorDashboardLayout() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-surface">
      <TopNavBar />
      <DashboardSidebar role="donor" title="Donor Dashboard" subtitle={user?.username} />
      <main className="ml-64 p-margin-desktop max-w-container-max mx-auto space-y-8">
        <Outlet />
      </main>
    </div>
  );
}
