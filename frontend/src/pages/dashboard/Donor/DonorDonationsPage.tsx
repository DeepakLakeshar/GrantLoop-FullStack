import { useState } from "react";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { DataTable, type DataTableColumn } from "@/components/shared/DataTable";
import { Spinner } from "@/components/shared/Spinner";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { DonationDetailModal } from "@/components/feature/DonationDetailModal";
import { useDonorHistory } from "@/hooks/useDonorDashboard";
import { formatCurrency, formatDate } from "@/lib/format";
import type { Donation } from "@/types/entities";

export function DonorDonationsPage() {
  const [selectedDonationId, setSelectedDonationId] = useState<string | null>(null);
  const { data: historyData, isLoading, isError } = useDonorHistory();

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
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="font-headline-lg text-headline-lg text-primary">My Donations</h1>
      </div>

      <section className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
        {isLoading ? (
          <div className="py-16 flex justify-center">
            <Spinner size={24} className="text-primary" />
          </div>
        ) : isError ? (
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

      {selectedDonationId && (
        <DonationDetailModal
          donationId={selectedDonationId}
          onClose={() => setSelectedDonationId(null)}
        />
      )}
    </div>
  );
}
