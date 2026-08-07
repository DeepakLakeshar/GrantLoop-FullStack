import { Link } from "react-router-dom";
import { MetricCard } from "@/components/shared/MetricCard";
import { Spinner } from "@/components/shared/Spinner";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { useDonorMetrics } from "@/hooks/useDonorDashboard";
import { formatCurrency } from "@/lib/format";

export function DonorDashboardOverview() {
  const { data: metrics, isLoading, isError } = useDonorMetrics();

  const totalDonated = metrics?.total_amount_donated ?? 0;
  const campaignsSupported = metrics?.campaigns_supported ?? 0;
  const averageDonation = metrics?.average_donation ?? 0;

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="font-headline-lg text-headline-lg text-primary">Overview</h1>
        <Link
          to="/causes"
          className="bg-primary text-white px-6 py-3 rounded font-bold hover:bg-primary-container transition-all active:scale-95"
        >
          Find a Cause
        </Link>
      </div>

      {isLoading ? (
        <div className="py-8 flex justify-center">
          <Spinner size={32} className="text-primary" />
        </div>
      ) : isError ? (
        <div className="py-4">
          <ErrorBanner kind="unknown" message="Failed to load dashboard metrics." />
        </div>
      ) : (
        <section className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
          <MetricCard label="Total Donated" value={formatCurrency(totalDonated, "INR")} />
          <MetricCard label="Campaigns Supported" value={String(campaignsSupported)} />
          <MetricCard label="Average Donation" value={formatCurrency(averageDonation, "INR")} />
        </section>
      )}
    </div>
  );
}
