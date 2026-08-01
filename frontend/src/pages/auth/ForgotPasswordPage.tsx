import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router-dom";
import { MailCheck } from "lucide-react";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { FormField } from "@/components/shared/FormField";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { Spinner } from "@/components/shared/Spinner";
import { authApi } from "@/lib/auth/authApi";
import { forgotPasswordSchema, type ForgotPasswordFormValues } from "@/lib/auth/validation";
import { ApiError } from "@/lib/api/errors";

export function ForgotPasswordPage() {
  const [serverError, setServerError] = useState<ApiError | null>(null);
  const [submittedEmail, setSubmittedEmail] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
  });

  async function onSubmit(values: ForgotPasswordFormValues) {
    setServerError(null);
    try {
      await authApi.requestPasswordReset(values.email);
      // Deliberately shown regardless of whether the email exists — never
      // reveal account existence through this form's response.
      setSubmittedEmail(values.email);
    } catch (err) {
      setServerError(err instanceof ApiError ? err : new ApiError("Something went wrong. Please try again.", "unknown", null));
    }
  }

  if (submittedEmail) {
    return (
      <AuthLayout eyebrow="Institutional Access" title="Check your email">
        <div className="text-center space-y-4">
          <MailCheck className="w-10 h-10 text-secondary mx-auto" />
          <p className="text-body-md text-on-surface-variant">
            If an account exists for <span className="font-bold text-on-surface">{submittedEmail}</span>, a reset
            link has been sent. It expires in 24 hours.
          </p>
          <Link to="/login" className="text-primary font-bold hover:underline inline-block">
            Back to sign in
          </Link>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      eyebrow="Institutional Access"
      title="Reset your password"
      subtitle="Enter your email and we'll send you a reset link."
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
        {serverError && <ErrorBanner kind={serverError.kind} message={serverError.message} />}

        <FormField
          label="Email address"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-primary text-white py-3 rounded font-bold hover:bg-primary-container transition-all active:scale-95 disabled:opacity-60 disabled:active:scale-100 flex items-center justify-center gap-2"
        >
          {isSubmitting && <Spinner size={16} />}
          {isSubmitting ? "Sending…" : "Send reset link"}
        </button>
      </form>

      <p className="text-center text-body-md text-on-surface-variant mt-6">
        <Link to="/login" className="text-primary font-bold hover:underline">
          Back to sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
