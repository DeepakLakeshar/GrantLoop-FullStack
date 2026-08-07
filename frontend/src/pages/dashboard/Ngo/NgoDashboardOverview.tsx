import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { MetricCard } from "@/components/shared/MetricCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { ProgressBar } from "@/components/shared/ProgressBar";
import { DataTable, type DataTableColumn } from "@/components/shared/DataTable";
import { Spinner } from "@/components/shared/Spinner";
import { useAuth } from "@/context/AuthContext";
import { useMyCampaigns } from "@/hooks/useCampaigns";
import { useNgoMetrics } from "@/hooks/useNgoDashboard";
import { formatCurrency, formatDate } from "@/lib/format";
import type { Campaign } from "@/types/entities";

export function NgoDashboardOverview() {
  const { user } = useAuth();
  const { data: campaigns, isLoading: isCampaignsLoading } = useMyCampaigns(user?.id);
  const { data: metrics } = useNgoMetrics();

  const totalRaised = metrics?.total_raised ?? 0;
  const liveCount = metrics?.live_campaigns_count ?? 0;
  const pendingCount = metrics?.pending_verifications_count ?? 0;

  const columns: DataTableColumn<Campaign>[] = [
    {
      key: "title",
      header: "Campaign",
      render: (c) => (
        <Link to={`/causes/${c.id}`} className="font-bold text-primary hover:underline">
          {c.title}
        </Link>
      ),
    },
    { key: "status", header: "Status", render: (c) => <StatusBadge status={c.status} /> },
    {
      key: "progress",
      header: "Funding progress",
      render: (c) => (
        <div className="w-48">
          <ProgressBar
            percentage={c.funding_percentage}
            sublabel={`${formatCurrency(c.raised_amount, c.campaign_currency)} of ${formatCurrency(c.goal_amount, c.campaign_currency)}`}
          />
        </div>
      ),
    },
    { key: "created_at", header: "Submitted", render: (c) => formatDate(c.created_at) },
  ];

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="font-headline-lg text-headline-lg text-primary">My Campaigns</h1>
        <Link
          to="/submit-case"
          className="flex items-center gap-2 bg-primary text-white px-6 py-3 rounded font-bold hover:bg-primary-container transition-all active:scale-95"
        >
          <Plus className="w-5 h-5" />
          New campaign
        </Link>
      </div>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
        <MetricCard label="Total raised across campaigns" value={formatCurrency(totalRaised, "INR")} />
        <MetricCard label="Live campaigns" value={String(liveCount)} />
        <MetricCard label="Awaiting verification" value={String(pendingCount)} />
      </section>

      <section className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-outline-variant">
          <h2 className="font-headline-sm text-headline-sm text-primary">All campaigns</h2>
        </div>
        {isCampaignsLoading ? (
          <div className="py-16 flex justify-center">
            <Spinner size={24} className="text-primary" />
          </div>
        ) : (
          <DataTable
            columns={columns}
            rows={campaigns ?? []}
            rowKey={(c) => c.id}
            emptyMessage="You haven't submitted a campaign yet."
          />
        )}
      </section>
    </div>
  );
}
