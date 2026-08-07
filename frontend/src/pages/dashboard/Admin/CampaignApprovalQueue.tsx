import { useState } from "react";
import { Link } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useCampaignList } from "@/hooks/useCampaigns";
import { campaignsApi, type CampaignFilters } from "@/lib/api/campaigns";
import { DataTable, type DataTableColumn } from "@/components/shared/DataTable";
import { Pagination } from "@/components/shared/Pagination";
import { Spinner } from "@/components/shared/Spinner";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { formatCurrency, formatDate } from "@/lib/format";
import type { Campaign } from "@/types/entities";
import { CheckCircle, XCircle, Search } from "lucide-react";

export function CampaignApprovalQueue() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<CampaignFilters>({
    status: "pending_verification",
    page: 1,
    pageSize: 10,
    search: "",
  });
  const [searchInput, setSearchInput] = useState("");

  const { data, isLoading, error } = useCampaignList(filters);

  const [processingId, setProcessingId] = useState<string | null>(null);

  const handleVerify = async (campaignId: string, status: "approved" | "rejected") => {
    try {
      setProcessingId(campaignId);
      const notes = prompt(`Enter ${status === "approved" ? "approval" : "rejection"} notes (optional):`) || "";
      await campaignsApi.verifyCampaign(campaignId, status, notes);
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      queryClient.invalidateQueries({ queryKey: ["admin-dashboard"] });
    } catch (err) {
      alert("Failed to verify campaign. Please try again.");
      console.error(err);
    } finally {
      setProcessingId(null);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters((prev) => ({ ...prev, search: searchInput, page: 1 }));
  };

  const columns: DataTableColumn<Campaign>[] = [
    {
      key: "title",
      header: "Campaign",
      render: (c) => (
        <div>
          <Link to={`/causes/${c.id}`} className="font-bold text-primary hover:underline">
            {c.title}
          </Link>
          <div className="text-sm text-gray-500">{c.category.name}</div>
        </div>
      ),
    },
    {
      key: "created_by",
      header: "Creator",
      render: (c) => (
        <div className="text-sm">
          <p className="font-medium text-gray-900">{c.created_by.full_name}</p>
          <p className="text-gray-500">{c.created_by.email}</p>
        </div>
      ),
    },
    {
      key: "goal_amount",
      header: "Goal",
      render: (c) => (
        <span className="font-medium text-gray-900">
          {formatCurrency(Number(c.goal_amount), c.campaign_currency)}
        </span>
      ),
    },
    {
      key: "created_at",
      header: "Submitted",
      render: (c) => <span className="text-sm text-gray-500">{formatDate(c.created_at)}</span>,
    },
    {
      key: "actions",
      header: "Actions",
      render: (c) => (
        <div className="flex gap-2 justify-end">
          <button
            onClick={() => handleVerify(c.id, "approved")}
            disabled={processingId === c.id}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 hover:bg-green-100 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
          >
            {processingId === c.id ? <Spinner size={14} /> : <CheckCircle size={16} />}
            Approve
          </button>
          <button
            onClick={() => handleVerify(c.id, "rejected")}
            disabled={processingId === c.id}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
          >
            {processingId === c.id ? <Spinner size={14} /> : <XCircle size={16} />}
            Reject
          </button>
        </div>
      ),
    },
  ];

  if (error) {
    return (
      <ErrorBanner
        title="Failed to load campaigns"
        message="There was an error loading the campaign approval queue."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaign Approvals</h1>
          <p className="text-gray-500 mt-1">Review and approve pending campaigns before they go live.</p>
        </div>

        <form onSubmit={handleSearch} className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search campaigns or users..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary focus:border-primary"
          />
        </form>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
        <DataTable
          columns={columns}
          data={data?.results ?? []}
          isLoading={isLoading}
          emptyMessage="No campaigns pending verification at this time."
        />
        
        {data && data.count > (filters.pageSize || 10) && (
          <Pagination
            currentPage={filters.page || 1}
            totalPages={Math.ceil(data.count / (filters.pageSize || 10))}
            onPageChange={(p) => setFilters((prev) => ({ ...prev, page: p }))}
          />
        )}
      </div>
    </div>
  );
}
