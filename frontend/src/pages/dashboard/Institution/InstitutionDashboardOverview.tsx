import { Link } from "react-router-dom";
import { FileCheck2, Users, Wallet, FileText } from "lucide-react";
import { MetricCard } from "@/components/shared/MetricCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { DataTable, type DataTableColumn } from "@/components/shared/DataTable";
import { Spinner } from "@/components/shared/Spinner";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { useInstitutionDashboard } from "@/hooks/useInstitutionDashboard";
import { formatCurrency, formatDate } from "@/lib/format";
import { ApiError } from "@/lib/api/errors";
import type { Campaign, Beneficiary, FundRelease, Verification } from "@/types/entities";

type PendingBeneficiaryRow = Beneficiary & { campaignTitle: string };
type PendingFundReleaseRow = FundRelease & { campaignTitle: string; milestoneTitle: string };
type RecentApprovalRow = Verification & { campaignTitle: string };

export function InstitutionDashboardOverview() {
  const { data, isLoading, isError, error } = useInstitutionDashboard();

  const campaignColumns: DataTableColumn<Campaign>[] = [
    {
      key: "title",
      header: "Campaign",
      render: (c) => (
        <Link to={`/causes/${c.id}`} className="font-bold text-primary hover:underline">
          {c.title}
        </Link>
      ),
    },
    { key: "category", header: "Category", render: (c) => c.category?.name ?? "—" },
    { key: "goal", header: "Goal", render: (c) => formatCurrency(c.goal_amount, c.campaign_currency), align: "right" },
    { key: "submitted", header: "Submitted", render: (c) => formatDate(c.created_at) },
    {
      key: "actions",
      header: "",
      align: "right",
      render: () => (
        <div className="flex justify-end gap-2">
          <button className="px-3 py-1.5 text-label-caps font-label-caps bg-primary text-white rounded hover:opacity-90 transition-all">
            Review campaign
          </button>
        </div>
      ),
    },
  ];

  const beneficiaryColumns: DataTableColumn<PendingBeneficiaryRow>[] = [
    { key: "name", header: "Beneficiary", render: (b) => <span className="font-bold text-primary">{b.name}</span> },
    { key: "campaign", header: "Campaign", render: (b) => b.campaignTitle },
    { key: "contact", header: "Contact", render: (b) => b.contact_email },
    {
      key: "actions",
      header: "",
      align: "right",
      render: () => (
        <button className="px-3 py-1.5 text-label-caps font-label-caps bg-primary text-white rounded hover:opacity-90 transition-all">
          Verify beneficiary
        </button>
      ),
    },
  ];

  const fundReleaseColumns: DataTableColumn<PendingFundReleaseRow>[] = [
    { key: "campaign", header: "Campaign", render: (fr) => fr.campaignTitle },
    { key: "milestone", header: "Milestone", render: (fr) => fr.milestoneTitle },
    { key: "amount", header: "Amount", render: (fr) => formatCurrency(fr.amount, "USD"), align: "right" },
    { key: "requested", header: "Requested", render: (fr) => formatDate(fr.created_at) },
    {
      key: "actions",
      header: "",
      align: "right",
      render: () => (
        <div className="flex justify-end gap-2">
          <button className="px-3 py-1.5 text-label-caps font-label-caps bg-secondary text-on-secondary rounded hover:opacity-90 transition-all">
            Approve
          </button>
          <button className="px-3 py-1.5 text-label-caps font-label-caps border border-outline-variant text-error rounded hover:bg-error-container/20 transition-all">
            Reject
          </button>
        </div>
      ),
    },
  ];

  const approvedColumns: DataTableColumn<RecentApprovalRow>[] = [
    { key: "campaign", header: "Campaign", render: (v) => <span className="font-bold text-primary">{v.campaignTitle}</span> },
    { key: "status", header: "Status", render: (v) => <StatusBadge status={v.status} /> },
    { key: "date", header: "Approved", render: (v) => formatDate(v.created_at) },
    {
      key: "actions",
      header: "",
      align: "right",
      render: () => (
        <button className="px-3 py-1.5 text-label-caps font-label-caps border border-outline-variant text-primary rounded hover:bg-surface-container-low transition-all flex items-center gap-1.5 ml-auto">
          <FileText className="w-3.5 h-3.5" />
          View documents
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-8">
      <h1 className="font-headline-lg text-headline-lg text-primary">Verification Overview</h1>

      {isError && <ErrorBanner kind={error instanceof ApiError ? error.kind : "unknown"} />}

      {isLoading ? (
        <div className="py-24 flex justify-center">
          <Spinner size={28} className="text-primary" />
        </div>
      ) : data ? (
        <>
          <section className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
            <MetricCard label="Pending" value={String(data.stats.pending)} />
            <MetricCard label="Approved" value={String(data.stats.approved)} />
            <MetricCard label="Rejected" value={String(data.stats.rejected)} />
          </section>

          <section className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-outline-variant flex items-center gap-2">
              <FileCheck2 className="w-5 h-5 text-primary" />
              <h2 className="font-headline-sm text-headline-sm text-primary">Pending Campaign Verifications</h2>
            </div>
            <DataTable
              columns={campaignColumns}
              rows={data.pendingCampaigns}
              rowKey={(c) => c.id}
              emptyMessage="No campaigns awaiting verification."
            />
          </section>

          <section className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-outline-variant flex items-center gap-2">
              <Users className="w-5 h-5 text-primary" />
              <h2 className="font-headline-sm text-headline-sm text-primary">Pending Beneficiary Verifications</h2>
            </div>
            <DataTable
              columns={beneficiaryColumns}
              rows={data.pendingBeneficiaries}
              rowKey={(b) => b.id}
              emptyMessage="No beneficiaries awaiting verification."
            />
          </section>

          <section className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-outline-variant flex items-center gap-2">
              <Wallet className="w-5 h-5 text-primary" />
              <h2 className="font-headline-sm text-headline-sm text-primary">Pending Fund Release Requests</h2>
            </div>
            <DataTable
              columns={fundReleaseColumns}
              rows={data.pendingFundReleases}
              rowKey={(fr) => fr.id}
              emptyMessage="No fund release requests pending."
            />
          </section>

          <section className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-outline-variant">
              <h2 className="font-headline-sm text-headline-sm text-primary">Recently Approved Campaigns</h2>
            </div>
            <DataTable
              columns={approvedColumns}
              rows={data.recentlyApproved}
              rowKey={(v) => v.id}
              emptyMessage="No approvals yet."
            />
          </section>
        </>
      ) : null}
    </div>
  );
}
