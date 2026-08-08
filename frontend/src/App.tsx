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
import { HelpCenterPage } from "@/pages/public/HelpCenterPage";

import { ProfilePage } from "@/pages/dashboard/ProfilePage";
import { SettingsPage } from "@/pages/dashboard/SettingsPage";
import { PublicRoute, ProtectedRoute, RoleProtectedRoute } from "@/routes/RouteGuards";

// Admin
import { AdminDashboardLayout } from "@/pages/dashboard/Admin/AdminDashboardLayout";
import { AdminDashboardOverview } from "@/pages/dashboard/Admin/AdminDashboardOverview";
import { CampaignApprovalQueue } from "@/pages/dashboard/Admin/CampaignApprovalQueue";
import { AdminPayoutManagement } from "@/pages/dashboard/Admin/AdminPayoutManagement";
import { AdminReports } from "@/pages/dashboard/Admin/AdminReports";
import { AdminAuditLogPage } from "@/pages/dashboard/Admin/AdminAuditLogPage";

// Donor
import { DonorDashboardLayout } from "@/pages/dashboard/Donor/DonorDashboardLayout";
import { DonorDashboardOverview } from "@/pages/dashboard/Donor/DonorDashboardOverview";
import { DonorDonationsPage } from "@/pages/dashboard/Donor/DonorDonationsPage";
import { DonorImpactPage } from "@/pages/dashboard/Donor/DonorImpactPage";
import { DonorVerificationPage } from "@/pages/dashboard/Donor/DonorVerificationPage";

// NGO
import { NgoDashboardLayout } from "@/pages/dashboard/Ngo/NgoDashboardLayout";
import { NgoDashboardOverview } from "@/pages/dashboard/Ngo/NgoDashboardOverview";
import { SubmitCasePage } from "@/pages/dashboard/Ngo/SubmitCasePage";

// Institution
import { InstitutionDashboardLayout } from "@/pages/dashboard/Institution/InstitutionDashboardLayout";
import { ExecutionDashboardLayout } from "@/pages/dashboard/Execution/ExecutionDashboardLayout";
import { AssignedMilestonesPage } from "@/pages/dashboard/Execution/AssignedMilestonesPage";
import { InstitutionDashboardOverview } from "@/pages/dashboard/Institution/InstitutionDashboardOverview";
import { InstitutionVerifyPage } from "@/pages/dashboard/Institution/InstitutionVerifyPage";
import { InstitutionFundReleasePage } from "@/pages/dashboard/Institution/InstitutionFundReleasePage";

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
        <Route path="/help" element={<HelpCenterPage />} />
      </Route>

      {/* NGO only */}
      <Route element={<RoleProtectedRoute allowedRoles={["ngo"]} />}>
        <Route element={<NgoDashboardLayout />}>
          <Route path="/dashboard/ngo" element={<NgoDashboardOverview />} />
          <Route path="/submit-case" element={<SubmitCasePage />} />
        </Route>
      </Route>

      {/* Institution only */}
      <Route element={<RoleProtectedRoute allowedRoles={["institution"]} />}>
        <Route element={<InstitutionDashboardLayout />}>
          <Route path="/dashboard/institution" element={<InstitutionDashboardOverview />} />
          <Route path="/dashboard/institution/fund-releases" element={<InstitutionFundReleasePage />} />
          <Route path="/verify" element={<InstitutionVerifyPage />} />
        </Route>
      </Route>

      {/* Donor only */}
      <Route element={<RoleProtectedRoute allowedRoles={["donor"]} />}>
        <Route path="/dashboard/donor" element={<DonorDashboardLayout />}>
          <Route index element={<DonorDashboardOverview />} />
          <Route path="donations" element={<DonorDonationsPage />} />
          <Route path="impact" element={<DonorImpactPage />} />
          <Route path="verification" element={<DonorVerificationPage />} />
        </Route>
      </Route>

      {/* Admin only */}
      <Route element={<RoleProtectedRoute allowedRoles={["admin"]} />}>
        <Route path="/dashboard/admin" element={<AdminDashboardLayout />}>
          <Route index element={<AdminDashboardOverview />} />
          <Route path="campaigns" element={<CampaignApprovalQueue />} />
          <Route path="payouts" element={<AdminPayoutManagement />} />
          <Route path="reports" element={<AdminReports />} />
          <Route path="audit" element={<AdminAuditLogPage />} />
        </Route>
      </Route>

      {/* Execution Partner only */}
      <Route element={<RoleProtectedRoute allowedRoles={["execution_partner"]} />}>
        <Route element={<ExecutionDashboardLayout />}>
          <Route path="/dashboard/execution" element={<AssignedMilestonesPage />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
