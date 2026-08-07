import { Outlet } from "react-router-dom";
import { DashboardSidebar } from "@/components/layout/DashboardSidebar";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { useAuth } from "@/context/AuthContext";

export function AdminDashboardLayout() {
  const { user } = useAuth();
  
  if (!user || user.role !== "admin") {
    return null; // RouteGuard will handle the actual redirect
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <DashboardSidebar 
        role={user.role} 
        title="Admin Dashboard" 
        subtitle="Platform Management" 
      />
      <div className="flex-1 flex flex-col min-w-0">
        <TopNavBar />
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
