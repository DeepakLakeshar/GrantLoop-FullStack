import { useAdminDashboard } from "@/hooks/useAdminDashboard";
import { MetricCard } from "@/components/shared/MetricCard";
import { Spinner } from "@/components/shared/Spinner";
import { ErrorBanner } from "@/components/shared/ErrorBanner";
import { formatCurrency } from "@/lib/format";
import { Users, FileText, DollarSign, Wallet, Activity } from "lucide-react";

export function AdminDashboardOverview() {
  const { data, isLoading, error } = useAdminDashboard();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size={32} className="text-primary" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <ErrorBanner
        title="Failed to load dashboard metrics"
        message="There was an error loading the admin overview. Please try again later."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Platform Overview</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Users"
          value={data.total_users}
          icon={Users}
          color="blue"
        />
        <MetricCard
          title="Total NGOs"
          value={data.total_ngos}
          icon={Activity}
          color="indigo"
        />
        <MetricCard
          title="Live Campaigns"
          value={data.live_campaigns}
          icon={FileText}
          color="green"
        />
        <MetricCard
          title="Pending Approvals"
          value={data.pending_campaigns}
          icon={FileText}
          color="yellow"
        />
        <MetricCard
          title="Total Donations"
          value={data.total_donations}
          icon={HeartIcon}
          color="pink"
        />
        <MetricCard
          title="Total Volume"
          value={formatCurrency(Number(data.total_donation_amount))}
          icon={DollarSign}
          color="green"
        />
        <MetricCard
          title="Pending Payouts"
          value={data.pending_payouts}
          icon={Wallet}
          color="yellow"
        />
        <MetricCard
          title="Platform Balance"
          value={formatCurrency(Number(data.platform_balance))}
          icon={Wallet}
          color="blue"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Campaigns</h2>
          {data.recent_campaigns.length > 0 ? (
            <div className="space-y-4">
              {data.recent_campaigns.map((c) => (
                <div key={c.id} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="font-medium text-gray-900">{c.title}</p>
                    <p className="text-sm text-gray-500">{c.creator_email}</p>
                  </div>
                  <div className="text-right">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      c.status === 'live' ? 'bg-green-100 text-green-800' :
                      c.status === 'pending_verification' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {c.status.replace("_", " ")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No recent campaigns.</p>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Payout Requests</h2>
          {data.recent_payout_requests.length > 0 ? (
            <div className="space-y-4">
              {data.recent_payout_requests.map((p) => (
                <div key={p.id} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="font-medium text-gray-900">{p.campaign_title}</p>
                    <p className="text-sm text-gray-500">{p.ngo_email}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">{formatCurrency(Number(p.requested_amount))}</p>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      p.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      p.status === 'approved' ? 'bg-blue-100 text-blue-800' :
                      p.status === 'completed' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {p.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No recent payout requests.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function HeartIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
    </svg>
  );
}
