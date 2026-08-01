import { Routes, Route } from "react-router-dom";
import { PageStub } from "@/pages/PageStub";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { ForgotPasswordPage } from "@/pages/auth/ForgotPasswordPage";
import { ResetPasswordPage } from "@/pages/auth/ResetPasswordPage";
import { LandingPage } from "@/pages/public/LandingPage";
import { CauseListingPage } from "@/pages/public/CauseListingPage";
import { CampaignDetailPage } from "@/pages/public/CampaignDetailPage";
import { PricingPage } from "@/pages/public/PricingPage";
import { NgoDashboardPage } from "@/pages/dashboard/NgoDashboardPage";
import { InstitutionDashboardPage } from "@/pages/dashboard/InstitutionDashboardPage";
import { PublicRoute, ProtectedRoute, RoleProtectedRoute } from "@/routes/RouteGuards";

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

      {/* Public, no auth required either way — Phase 3 */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/causes" element={<CauseListingPage />} />
      <Route path="/causes/:id" element={<CampaignDetailPage />} />
      <Route path="/causes/:id/transparency" element={<PageStub title="Fund Transparency" />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/how-it-works" element={<PageStub title="How it Works" />} />

      {/* Any logged-in user, regardless of role */}
      <Route element={<ProtectedRoute />}>
        <Route path="/causes/:id/donate" element={<PageStub title="Donate" />} />
        <Route path="/profile" element={<PageStub title="Profile" note="New screen — approved addition" />} />
        <Route path="/settings" element={<PageStub title="Settings" note="New screen — approved addition" />} />
        <Route path="/documents/:id" element={<PageStub title="Document Viewer" note="New screen — approved addition" />} />
      </Route>

      {/* NGO only */}
      <Route element={<RoleProtectedRoute allowedRoles={["ngo"]} />}>
        <Route path="/submit-case" element={<PageStub title="Grant Funding Request" />} />
        <Route path="/dashboard/ngo" element={<NgoDashboardPage />} />
      </Route>

      {/* Institution only */}
      <Route element={<RoleProtectedRoute allowedRoles={["institution"]} />}>
        <Route path="/verify" element={<PageStub title="Verification Dashboard" />} />
        <Route path="/dashboard/institution" element={<InstitutionDashboardPage />} />
        <Route
          path="/dashboard/institution/fund-releases"
          element={<PageStub title="Fund Release Approval" note="New screen — approved addition" />}
        />
      </Route>

      {/* Execution partner only */}
      <Route element={<RoleProtectedRoute allowedRoles={["execution_partner"]} />}>
        <Route path="/dashboard/execution" element={<PageStub title="Execution Partner" />} />
      </Route>

      {/* Donor only */}
      <Route element={<RoleProtectedRoute allowedRoles={["donor"]} />}>
        <Route path="/dashboard/donor" element={<PageStub title="Donor Dashboard" />} />
      </Route>

      {/* Admin only */}
      <Route element={<RoleProtectedRoute allowedRoles={["admin"]} />}>
        <Route
          path="/dashboard/admin"
          element={<PageStub title="Admin Dashboard" note="New screen — approved addition" />}
        />
        <Route
          path="/dashboard/admin/audit"
          element={<PageStub title="Audit Log" note="Admin-only, never donor-visible" />}
        />
      </Route>

      <Route path="*" element={<PageStub title="Not found" />} />
    </Routes>
  );
}
