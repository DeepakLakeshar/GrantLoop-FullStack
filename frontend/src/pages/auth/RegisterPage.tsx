import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { FormField } from "@/components/shared/FormField";
import { PasswordInput } from "@/components/shared/PasswordInput";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { Spinner } from "@/components/shared/Spinner";
import { useAuth } from "@/context/AuthContext";
import { registerSchema, type RegisterFormValues } from "@/lib/auth/validation";
import { ApiError } from "@/lib/api/errors";
import { ROLE_HOME } from "@/lib/auth/roleRedirect";

const ROLE_OPTIONS: { value: RegisterFormValues["role"]; label: string; description: string }[] = [
  { value: "donor", label: "Donor", description: "Support verified causes" },
  { value: "ngo", label: "NGO", description: "Request funding for a cause" },
  { value: "institution", label: "Institution", description: "Verify NGO cases" },
  { value: "execution_partner", label: "Execution Partner", description: "Implement funded projects" },
];

export function RegisterPage() {
  const { register: registerAccount } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<ApiError | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { fullName: "", email: "", password: "", confirmPassword: "", role: "donor" },
  });

  const selectedRole = watch("role");

  async function onSubmit(values: RegisterFormValues) {
    setServerError(null);
    try {
      const user = await registerAccount({
        full_name: values.fullName,
        email: values.email,
        password: values.password,
        role: values.role,
      });
      navigate(ROLE_HOME[user.role], { replace: true });
    } catch (err) {
      setServerError(err instanceof ApiError ? err : new ApiError("Registration failed. Please try again.", "unknown", null));
    }
  }

  return (
    <AuthLayout eyebrow="Institutional Trust" title="Create your account" subtitle="Join a transparent funding network.">
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
        {serverError && <ErrorBanner kind={serverError.kind} message={serverError.message} />}

        <FormField label="Full name" autoComplete="name" error={errors.fullName?.message} {...register("fullName")} />
        <FormField label="Email address" type="email" autoComplete="email" error={errors.email?.message} {...register("email")} />

        <div>
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase block mb-2">
            Password
          </label>
          <PasswordInput autoComplete="new-password" error={errors.password?.message} {...register("password")} />
        </div>

        <div>
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase block mb-2">
            Confirm password
          </label>
          <PasswordInput autoComplete="new-password" error={errors.confirmPassword?.message} {...register("confirmPassword")} />
        </div>

        <fieldset>
          <legend className="font-label-caps text-label-caps text-on-surface-variant uppercase mb-3">
            Account type
          </legend>
          <div className="grid grid-cols-2 gap-3">
            {ROLE_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setValue("role", option.value, { shouldValidate: true })}
                className={`text-left p-3 rounded-lg border transition-all ${
                  selectedRole === option.value
                    ? "border-primary bg-primary-container/5"
                    : "border-outline-variant hover:border-primary/50"
                }`}
              >
                <p className="font-body-md font-bold text-primary">{option.label}</p>
                <p className="text-data-table text-on-surface-variant">{option.description}</p>
              </button>
            ))}
          </div>
          {errors.role && <p className="text-error text-data-table font-data-table mt-2">{errors.role.message}</p>}
        </fieldset>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-primary text-white py-3 rounded font-bold hover:bg-primary-container transition-all active:scale-95 disabled:opacity-60 disabled:active:scale-100 flex items-center justify-center gap-2"
        >
          {isSubmitting && <Spinner size={16} />}
          {isSubmitting ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="text-center text-body-md text-on-surface-variant mt-6">
        Already have an account?{" "}
        <Link to="/login" className="text-primary font-bold hover:underline">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
