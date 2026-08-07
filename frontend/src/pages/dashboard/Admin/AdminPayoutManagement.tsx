import { useState } from "react";
import { Link } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { usePayoutsList } from "@/hooks/usePayouts";
import { payoutsApi, type PayoutFilters } from "@/lib/api/payouts";
import { DataTable, type DataTableColumn } from "@/components/shared/DataTable";
import { Pagination } from "@/components/shared/Pagination";
import { Spinner } from "@/components/shared/Spinner";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { formatCurrency, formatDate } from "@/lib/format";
import type { Payout } from "@/types/entities";
import { CheckCircle, XCircle, RefreshCw, Send, ListFilter } from "lucide-react";

export function AdminPayoutManagement() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<PayoutFilters>({
    status: "pending",
    page: 1,
    pageSize: 10,
  });

  const { data, error } = usePayoutsList(filters);

  const [processingId, setProcessingId] = useState<string | null>(null);

  const handleAction = async (payoutId: string, action: "approve" | "reject" | "process" | "complete") => {
    try {
      setProcessingId(payoutId);
      if (action === "approve") {
        const notes = prompt("Enter approval notes (optional):") || "";
        await payoutsApi.approve(payoutId, { admin_notes: notes });
      } else if (action === "reject") {
        const reason = prompt("Enter rejection reason:") || "";
        if (!reason) return; // reason is required for rejection
        await payoutsApi.reject(payoutId, { rejection_reason: reason });
      } else if (action === "process") {
        await payoutsApi.process(payoutId, { gateway_type: "mock", account_reference: "admin_triggered" });
      } else if (action === "complete") {
        await payoutsApi.complete(payoutId, { transfer_reference: "tx_" + Date.now() });
      }
      queryClient.invalidateQueries({ queryKey: ["payouts"] });
      queryClient.invalidateQueries({ queryKey: ["admin-dashboard"] });
    } catch (err) {
      alert(`Failed to ${action} payout. Please try again.`);
    } finally {
      setProcessingId(null);
    }
  };

  const columns: DataTableColumn<Payout>[] = [
    {
      key: "campaign",
      header: "Campaign",
      render: (p) => (
        <div>
          <Link to={`/causes/${p.campaign}`} className="font-bold text-primary hover:underline">
            {p.campaign_title || `Campaign ${p.campaign.slice(0, 8)}`}
          </Link>
          <div className="text-sm text-gray-500">{p.ngo_email || "Unknown NGO"}</div>
        </div>
      ),
    },
    {
      key: "amount",
      header: "Amount",
      render: (p) => (
        <span className="font-medium text-gray-900">
          {formatCurrency(Number(p.requested_amount), p.currency)}
        </span>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (p) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          p.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
          p.status === 'approved' ? 'bg-blue-100 text-blue-800' :
          p.status === 'processing' ? 'bg-indigo-100 text-indigo-800' :
          p.status === 'completed' ? 'bg-green-100 text-green-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {p.status}
        </span>
      ),
    },
    {
      key: "created_at",
      header: "Requested On",
      render: (p) => <span className="text-sm text-gray-500">{formatDate(p.created_at)}</span>,
    },
    {
      key: "actions",
      header: "Actions",
      render: (p) => (
        <div className="flex gap-2 justify-end">
          {p.status === "pending" && (
            <>
              <button
                onClick={() => handleAction(p.id, "approve")}
                disabled={processingId === p.id}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
              >
                {processingId === p.id ? <Spinner size={14} /> : <CheckCircle size={16} />}
                Approve
              </button>
              <button
                onClick={() => handleAction(p.id, "reject")}
                disabled={processingId === p.id}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
              >
                {processingId === p.id ? <Spinner size={14} /> : <XCircle size={16} />}
                Reject
              </button>
            </>
          )}
          {p.status === "approved" && (
            <button
              onClick={() => handleAction(p.id, "process")}
              disabled={processingId === p.id}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
            >
              {processingId === p.id ? <Spinner size={14} /> : <RefreshCw size={16} />}
              Process
            </button>
          )}
          {p.status === "processing" && (
            <button
              onClick={() => handleAction(p.id, "complete")}
              disabled={processingId === p.id}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 hover:bg-green-100 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
            >
              {processingId === p.id ? <Spinner size={14} /> : <Send size={16} />}
              Complete
            </button>
          )}
        </div>
      ),
    },
  ];

  if (error) {
    return (
      <ErrorBanner
        kind="unknown"
        message="There was an error loading the payout management queue."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payout Management</h1>
          <p className="text-gray-500 mt-1">Review, approve, and process NGO fund withdrawals.</p>
        </div>

        <div className="flex items-center gap-2">
          <ListFilter className="text-gray-400 w-5 h-5" />
          <select
            value={filters.status || ""}
            onChange={(e) => setFilters({ ...filters, status: e.target.value as any, page: 1 })}
            className="border-gray-300 rounded-md text-sm focus:ring-primary focus:border-primary"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
        <DataTable
          columns={columns as any}
          rows={data?.results ?? []}
          rowKey={(p: any) => p.id}
          emptyMessage={`No payouts found matching status "${filters.status || "all"}".`}
        />
        
        {data && data.count > (filters.pageSize || 10) && (
          <Pagination
            page={filters.page || 1}
            pageSize={filters.pageSize || 10}
            totalCount={data.count}
            onPageChange={(p) => setFilters((prev) => ({ ...prev, page: p }))}
          />
        )}
      </div>
    </div>
  );
}
