import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { CheckCircle2 } from "lucide-react";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { PasswordInput } from "@/components/shared/PasswordInput";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { Spinner } from "@/components/shared/Spinner";
import { authApi } from "@/lib/auth/authApi";
import { resetPasswordSchema, type ResetPasswordFormValues } from "@/lib/auth/validation";
import { ApiError } from "@/lib/api/errors";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<ApiError | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { newPassword: "", confirmPassword: "" },
  });

  async function onSubmit(values: ResetPasswordFormValues) {
    if (!token) return;
    setServerError(null);
    try {
      await authApi.confirmPasswordReset(token, values.newPassword);
      setSuccess(true);
    } catch (err) {
      setServerError(
        err instanceof ApiError
          ? err
          : new ApiError("This reset link is invalid or has expired.", "unknown", null)
      );
    }
  }

  if (!token) {
    return (
      <AuthLayout eyebrow="Institutional Access" title="Invalid reset link">
        <ErrorBanner kind="validation" message="This password reset link is missing or malformed. Request a new one." />
        <Link to="/forgot-password" className="text-primary font-bold hover:underline mt-6 inline-block">
          Request a new link
        </Link>
      </AuthLayout>
    );
  }

  if (success) {
    return (
      <AuthLayout eyebrow="Institutional Access" title="Password updated">
        <div className="text-center space-y-4">
          <CheckCircle2 className="w-10 h-10 text-secondary mx-auto" />
          <p className="text-body-md text-on-surface-variant">Your password has been changed.</p>
          <button
            onClick={() => navigate("/login", { replace: true })}
            className="bg-primary text-white px-6 py-3 rounded font-bold hover:bg-primary-container transition-all"
          >
            Sign in
          </button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout eyebrow="Institutional Access" title="Set a new password">
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
        {serverError && <ErrorBanner kind={serverError.kind} message={serverError.message} />}

        <div>
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase block mb-2">
            New password
          </label>
          <PasswordInput autoComplete="new-password" error={errors.newPassword?.message} {...register("newPassword")} />
        </div>

        <div>
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase block mb-2">
            Confirm new password
          </label>
          <PasswordInput
            autoComplete="new-password"
            error={errors.confirmPassword?.message}
            {...register("confirmPassword")}
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-primary text-white py-3 rounded font-bold hover:bg-primary-container transition-all active:scale-95 disabled:opacity-60 disabled:active:scale-100 flex items-center justify-center gap-2"
        >
          {isSubmitting && <Spinner size={16} />}
          {isSubmitting ? "Updating…" : "Update password"}
        </button>
      </form>
    </AuthLayout>
  );
}
