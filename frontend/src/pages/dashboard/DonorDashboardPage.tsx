import { useState } from "react";
import { Link } from "react-router-dom";
import { DashboardSidebar } from "@/components/layout/DashboardSidebar";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { MetricCard } from "@/components/shared/MetricCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { DataTable, type DataTableColumn } from "@/components/shared/DataTable";
import { Spinner } from "@/components/shared/Spinner";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { DonationDetailModal } from "@/components/feature/DonationDetailModal";
import { useAuth } from "@/context/AuthContext";
import { useDonorMetrics, useDonorHistory } from "@/hooks/useDonorDashboard";
import { formatCurrency, formatDate } from "@/lib/format";
import type { Donation } from "@/types/entities";

export function DonorDashboardPage() {
  const { user } = useAuth();
  const [selectedDonationId, setSelectedDonationId] = useState<string | null>(null);
  const { data: metrics, isLoading: isMetricsLoading, isError: isMetricsError } = useDonorMetrics();
  const { data: historyData, isLoading: isHistoryLoading, isError: isHistoryError } = useDonorHistory();

  const totalDonated = metrics?.total_amount_donated ?? 0;
  const campaignsSupported = metrics?.campaigns_supported ?? 0;
  const averageDonation = metrics?.average_donation ?? 0;

  const donations = historyData?.results ?? [];

  const columns: DataTableColumn<Donation>[] = [
    {
      key: "campaign",
      header: "Campaign",
      render: (d) => (
        <span className="font-bold text-primary">
          Campaign #{d.campaign}
        </span>
      ),
    },
    {
      key: "amount",
      header: "Amount",
      render: (d) => formatCurrency(d.settled_amount || d.original_amount, d.settled_currency || d.original_currency || "INR"),
    },
    {
      key: "status",
      header: "Status",
      render: (d) => <StatusBadge status={d.status} />,
    },
    {
      key: "date",
      header: "Date",
      render: (d) => formatDate(d.timestamp),
    },
    {
      key: "actions",
      header: "",
      render: (d) => (
        <button
          onClick={() => setSelectedDonationId(d.id)}
          className="text-label-caps text-primary font-bold hover:underline"
        >
          View Details
        </button>
      ),
    },
  ];

  return (
    <div className="min-h-screen">
      <TopNavBar />
      <DashboardSidebar role="donor" title="Donor Dashboard" subtitle={user?.username} />
      <main className="ml-64 p-margin-desktop max-w-container-max mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="font-headline-lg text-headline-lg text-primary">Overview</h1>
          <Link
            to="/causes"
            className="bg-primary text-white px-6 py-3 rounded font-bold hover:bg-primary-container transition-all active:scale-95"
          >
            Find a Cause
          </Link>
        </div>

        {isMetricsLoading ? (
          <div className="py-8 flex justify-center">
            <Spinner size={32} className="text-primary" />
          </div>
        ) : isMetricsError ? (
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

        <section className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-outline-variant flex justify-between items-center">
            <h2 className="font-headline-sm text-headline-sm text-primary">Donation History</h2>
          </div>
          {isHistoryLoading ? (
            <div className="py-16 flex justify-center">
              <Spinner size={24} className="text-primary" />
            </div>
          ) : isHistoryError ? (
            <div className="p-6">
              <ErrorBanner kind="unknown" message="Failed to load donation history." />
            </div>
          ) : (
            <DataTable
              columns={columns}
              rows={donations}
              rowKey={(d) => d.id}
              emptyMessage="You haven't made any donations yet."
            />
          )}
        </section>
      </main>

      {selectedDonationId && (
        <DonationDetailModal
          donationId={selectedDonationId}
          onClose={() => setSelectedDonationId(null)}
        />
      )}
    </div>
  );
}
