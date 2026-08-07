import { useState } from "react";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { useAuth } from "@/context/AuthContext";
import { authApi } from "@/lib/auth/authApi";
import { CheckCircle2, AlertCircle, KeyRound, Bell } from "lucide-react";

export function SettingsPage() {
  const { user } = useAuth();
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handlePasswordReset = async () => {
    if (!user) return;
    setStatus("loading");
    try {
      await authApi.requestPasswordReset(user.email);
      setStatus("success");
    } catch {
      setStatus("error");
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-surface-container-lowest">
      <TopNavBar />
      <main className="max-w-container-sm mx-auto px-margin-desktop py-12">
        <h1 className="font-headline-lg text-headline-lg text-primary mb-8">Settings</h1>

        <div className="space-y-6">
          {/* Security Section */}
          <section className="bg-surface border border-outline-variant rounded-lg overflow-hidden">
            <div className="p-6 border-b border-outline-variant flex items-center gap-3">
              <KeyRound className="w-6 h-6 text-primary" />
              <h2 className="font-headline-md text-headline-md text-primary">Security</h2>
            </div>
            <div className="p-6 space-y-4">
              <p className="text-body-lg text-on-surface-variant">
                To change your password, we will send a secure reset link to <strong>{user.email}</strong>.
              </p>
              
              <button
                onClick={handlePasswordReset}
                disabled={status === "loading" || status === "success"}
                className="bg-primary text-white px-6 py-2 rounded font-bold hover:bg-primary-container transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {status === "loading" ? "Sending..." : "Send Password Reset Email"}
              </button>

              {status === "success" && (
                <div className="flex items-center gap-2 text-success mt-4">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="text-body-md font-medium">Reset link sent! Please check your inbox.</span>
                </div>
              )}
              {status === "error" && (
                <div className="flex items-center gap-2 text-error mt-4">
                  <AlertCircle className="w-5 h-5" />
                  <span className="text-body-md font-medium">An error occurred. Please try again.</span>
                </div>
              )}
            </div>
          </section>

          {/* Notifications Section */}
          <section className="bg-surface border border-outline-variant rounded-lg overflow-hidden">
            <div className="p-6 border-b border-outline-variant flex items-center gap-3">
              <Bell className="w-6 h-6 text-primary" />
              <h2 className="font-headline-md text-headline-md text-primary">Notifications</h2>
            </div>
            <div className="p-6">
              <p className="text-body-lg text-on-surface-variant mb-4">
                Manage how you receive updates and alerts.
              </p>
              <div className="text-sm text-on-surface-variant p-4 bg-surface-container rounded">
                Notification preferences are currently managed system-wide. Future updates will allow granular control.
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
