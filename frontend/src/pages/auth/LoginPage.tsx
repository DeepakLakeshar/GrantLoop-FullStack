import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { FormField } from "@/components/shared/FormField";
import { PasswordInput } from "@/components/shared/PasswordInput";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { Spinner } from "@/components/shared/Spinner";
import { useAuth } from "@/context/AuthContext";
import { loginSchema, type LoginFormValues } from "@/lib/auth/validation";
import { ApiError } from "@/lib/api/errors";
import { ROLE_HOME } from "@/lib/auth/roleRedirect";

interface LocationState {
  from?: { pathname: string };
}

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverError, setServerError] = useState<ApiError | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "", rememberMe: true },
  });

  async function onSubmit(values: LoginFormValues) {
    setServerError(null);
    try {
      const user = await login({ email: values.email, password: values.password }, values.rememberMe);
      const state = location.state as LocationState | null;
      const redirectTo = state?.from?.pathname ?? ROLE_HOME[user.role];
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setServerError(err instanceof ApiError ? err : new ApiError("Sign in failed. Please try again.", "unknown", null));
    }
  }

  return (
    <AuthLayout eyebrow="Institutional Access" title="Sign in to GrantLoop" subtitle="Track your donations and verified impact.">
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
        {serverError && <ErrorBanner kind={serverError.kind} message={serverError.message} />}

        <FormField
          label="Email address"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />

        <div>
          <div className="flex justify-between items-baseline mb-2">
            <label htmlFor="password" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
              Password
            </label>
            <Link to="/forgot-password" className="text-label-caps text-primary font-bold hover:underline">
              Forgot password?
            </Link>
          </div>
          <PasswordInput
            id="password"
            autoComplete="current-password"
            error={errors.password?.message}
            {...register("password")}
          />
        </div>

        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" className="rounded text-primary focus:ring-primary border-outline-variant" {...register("rememberMe")} />
          <span className="text-body-md text-on-surface-variant">Remember me on this device</span>
        </label>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-primary text-white py-3 rounded font-bold hover:bg-primary-container transition-all active:scale-95 disabled:opacity-60 disabled:active:scale-100 flex items-center justify-center gap-2"
        >
          {isSubmitting && <Spinner size={16} />}
          {isSubmitting ? "Signing in…" : "Sign in"}
        </button>
      </form>

      <p className="text-center text-body-md text-on-surface-variant mt-6">
        New to GrantLoop?{" "}
        <Link to="/register" className="text-primary font-bold hover:underline">
          Create an account
        </Link>
      </p>
    </AuthLayout>
  );
}
