import { useState } from "react";
import { Download } from "lucide-react";
import { reportsApi } from "@/lib/api/reports";
import { Spinner } from "@/components/shared/Spinner";

export function AdminReports() {
  const [downloading, setDownloading] = useState<string | null>(null);

  const reports = [
    {
      id: "donations",
      title: "Donations Report",
      description: "Complete ledger of all platform donations including status and amounts.",
      action: () => reportsApi.exportDonationsReport("csv"),
    },
    {
      id: "campaigns",
      title: "Campaigns Report",
      description: "Listing of all campaigns, goals, raised amounts, and their creators.",
      action: () => reportsApi.exportCampaignsReport("csv"),
    },
    {
      id: "ngos",
      title: "NGOs Report",
      description: "Details of registered NGOs, their verification status, and contact information.",
      action: () => reportsApi.exportNgosReport("csv"),
    },
    {
      id: "beneficiaries",
      title: "Beneficiaries Report",
      description: "Export of all beneficiaries linked to campaigns across the platform.",
      action: () => reportsApi.exportBeneficiariesReport("csv"),
    },
    {
      id: "payouts",
      title: "Payouts Report",
      description: "Detailed logs of requested, approved, and completed fund transfers.",
      action: () => reportsApi.exportPayoutsReport("csv"),
    },
    {
      id: "financial",
      title: "Financial Reconciliation",
      description: "High-level aggregation of platform balance, total inflow, and outflow.",
      action: () => reportsApi.exportFinancialReport("csv"),
    },
    {
      id: "audit-logs",
      title: "System Audit Logs",
      description: "Comprehensive trail of administrative and automated system actions.",
      action: () => reportsApi.exportAuditLogsReport("csv"),
    },
  ];

  const handleDownload = async (reportId: string, action: () => Promise<any>) => {
    try {
      setDownloading(reportId);
      const res = await action();
      if (res.file_url) {
        // Mocking the download since it's just a URL
        window.open(res.file_url, "_blank");
      } else {
        alert("Report generation started. Check your email or notifications when it's ready.");
      }
    } catch (err) {
      alert("Failed to export report. Please try again.");
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Platform Reports</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((r) => (
          <div key={r.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">{r.title}</h2>
            <p className="text-sm text-gray-500 flex-1 mb-6">{r.description}</p>
            <button
              onClick={() => handleDownload(r.id, r.action)}
              disabled={downloading === r.id}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-primary text-white rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {downloading === r.id ? (
                <>
                  <Spinner size={16} /> Generating...
                </>
              ) : (
                <>
                  <Download size={16} /> Export CSV
                </>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
