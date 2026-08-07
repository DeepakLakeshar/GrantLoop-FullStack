import { Link } from "react-router-dom";
import { TopNavBar } from "@/components/layout/TopNavBar";

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex flex-col bg-surface">
      <TopNavBar />
      <main className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <h1 className="text-display-md font-bold text-primary mb-4">404</h1>
        <h2 className="text-headline-sm font-bold text-on-surface mb-6">Page Not Found</h2>
        <p className="text-body-lg text-on-surface-variant max-w-md mx-auto mb-8">
          The page you are looking for doesn't exist or is not available in this version.
        </p>
        <Link
          to="/"
          className="bg-primary text-on-primary font-label-lg font-bold px-6 py-3 rounded-full hover:opacity-90 transition-opacity"
        >
          Return Home
        </Link>
      </main>
    </div>
  );
}
