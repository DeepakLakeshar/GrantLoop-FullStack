import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { Footer } from "@/components/layout/Footer";

interface AuthLayoutProps {
  eyebrow: string;
  title: string;
  subtitle?: string;
  children: ReactNode;
}

/** Shared shell for Login, Register, Forgot Password, Reset Password.
 * Same centered-card pattern as the Donation Flow mockup (white card,
 * border-outline-variant, rounded-xl, shadow-sm) — the closest existing
 * analog identified in the Frontend Architecture Review, reused rather
 * than inventing a new auth-specific layout. */
export function AuthLayout({ eyebrow, title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <TopNavBar />
      <main className="flex-1 flex items-center justify-center px-margin-mobile md:px-margin-desktop py-16">
        <div className="w-full max-w-md">
          <div className="flex items-center gap-2 justify-center mb-4 text-secondary">
            <ShieldCheck className="w-[18px] h-[18px]" />
            <span className="font-label-caps text-label-caps uppercase tracking-widest">{eyebrow}</span>
          </div>
          <h1 className="font-headline-md text-headline-md text-primary text-center mb-2">{title}</h1>
          {subtitle && (
            <p className="text-body-md text-on-surface-variant text-center mb-8">{subtitle}</p>
          )}
          <div className="bg-white border border-outline-variant rounded-xl shadow-sm p-8">
            {children}
          </div>
          <p className="text-center text-body-md text-on-surface-variant mt-6">
            <Link to="/" className="text-primary font-bold hover:underline">
              Back to GrantLoop
            </Link>
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
