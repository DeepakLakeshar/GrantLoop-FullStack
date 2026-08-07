import { Routes, Route, Navigate } from "react-router-dom";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { ForgotPasswordPage } from "@/pages/auth/ForgotPasswordPage";
import { ResetPasswordPage } from "@/pages/auth/ResetPasswordPage";
import { LandingPage } from "@/pages/public/LandingPage";
import { CauseListingPage } from "@/pages/public/CauseListingPage";
import { CampaignDetailPage } from "@/pages/public/CampaignDetailPage";
import { PricingPage } from "@/pages/public/PricingPage";
import { NotFoundPage } from "@/pages/public/NotFoundPage";
import { NgoDashboardPage } from "@/pages/dashboard/NgoDashboardPage";
import { InstitutionDashboardPage } from "@/pages/dashboard/InstitutionDashboardPage";
import { DonorDashboardPage } from "@/pages/dashboard/DonorDashboardPage";
import { ProfilePage } from "@/pages/dashboard/ProfilePage";
import { SettingsPage } from "@/pages/dashboard/SettingsPage";
import { PublicRoute, ProtectedRoute, RoleProtectedRoute } from "@/routes/RouteGuards";

import { AdminDashboardLayout } from "@/pages/dashboard/Admin/AdminDashboardLayout";
import { AdminDashboardOverview } from "@/pages/dashboard/Admin/AdminDashboardOverview";
import { CampaignApprovalQueue } from "@/pages/dashboard/Admin/CampaignApprovalQueue";
import { AdminPayoutManagement } from "@/pages/dashboard/Admin/AdminPayoutManagement";
import { AdminReports } from "@/pages/dashboard/Admin/AdminReports";

// Route map — mirrors the frozen Frontend Architecture Review, section 4,
// plus the seven approved new screens. Auth pages are wrapped in
// PublicRoute (redirects an already-logged-in user away); dashboard
// pages are wrapped in RoleProtectedRoute (redirects a wrong-role user to
// their own dashboard, and an anonymous user to /login).
export default function App() {
  return (
    <Routes>
      {/* Public, unauthenticated-only */}
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
      </Route>

      {/* Public, no auth required either way */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/causes" element={<CauseListingPage />} />
      <Route path="/causes/:id" element={<CampaignDetailPage />} />
      <Route path="/pricing" element={<PricingPage />} />

      {/* Any logged-in user, regardless of role */}
      <Route element={<ProtectedRoute />}>
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/settings/notifications" element={<Navigate to="/settings" replace />} />
      </Route>

      {/* NGO only */}
      <Route element={<RoleProtectedRoute allowedRoles={["ngo"]} />}>
        <Route path="/dashboard/ngo" element={<NgoDashboardPage />} />
      </Route>

      {/* Institution only */}
      <Route element={<RoleProtectedRoute allowedRoles={["institution"]} />}>
        <Route path="/dashboard/institution" element={<InstitutionDashboardPage />} />
      </Route>

      {/* Donor only */}
      <Route element={<RoleProtectedRoute allowedRoles={["donor"]} />}>
        <Route path="/dashboard/donor" element={<DonorDashboardPage />} />
      </Route>

      {/* Admin only */}
      <Route element={<RoleProtectedRoute allowedRoles={["admin"]} />}>
        <Route path="/dashboard/admin" element={<AdminDashboardLayout />}>
          <Route index element={<AdminDashboardOverview />} />
          <Route path="campaigns" element={<CampaignApprovalQueue />} />
          <Route path="payouts" element={<AdminPayoutManagement />} />
          <Route path="reports" element={<AdminReports />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
