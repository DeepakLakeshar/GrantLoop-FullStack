import { useQuery } from "@tanstack/react-query";
import { donationsApi } from "@/lib/api/donations";
import { Spinner } from "@/components/shared/Spinner";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { formatCurrency, formatDate } from "@/lib/format";
import { X } from "lucide-react";

interface DonationDetailModalProps {
  donationId: string;
  onClose: () => void;
}

export function DonationDetailModal({ donationId, onClose }: DonationDetailModalProps) {
  const { data: donation, isLoading } = useQuery({
    queryKey: ["donations", donationId],
    queryFn: () => donationsApi.get(donationId),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-surface-container-lowest w-full max-w-lg rounded-xl shadow-2xl border border-outline-variant flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-outline-variant flex justify-between items-center">
          <h2 className="font-headline-sm text-headline-sm text-primary">Donation Details</h2>
          <button onClick={onClose} className="p-2 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {isLoading ? (
            <div className="py-16 flex justify-center">
              <Spinner size={32} />
            </div>
          ) : !donation ? (
            <p className="text-error py-8 text-center">Donation not found.</p>
          ) : (
            <>
              <div>
                <label className="text-label-caps font-label-caps text-on-surface-variant mb-1 block">Campaign ID</label>
                <p className="font-body-lg text-primary font-bold">Campaign #{donation.campaign}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-label-caps font-label-caps text-on-surface-variant mb-1 block">Amount</label>
                  <p className="font-body-lg text-primary">{formatCurrency(donation.settled_amount || donation.original_amount, donation.settled_currency || donation.original_currency || "INR")}</p>
                </div>
                <div>
                  <label className="text-label-caps font-label-caps text-on-surface-variant mb-1 block">Status</label>
                  <StatusBadge status={donation.status} />
                </div>
              </div>

              <div>
                <label className="text-label-caps font-label-caps text-on-surface-variant mb-1 block">Timeline</label>
                <div className="text-body-md text-on-surface-variant space-y-1">
                  <p>Initiated: {formatDate(donation.timestamp)}</p>
                </div>
              </div>

              {donation.receipt_url && (
                <div>
                  <label className="text-label-caps font-label-caps text-on-surface-variant mb-1 block">Receipt</label>
                  <a href={donation.receipt_url} target="_blank" rel="noreferrer" className="text-primary font-bold hover:underline">
                    Download Receipt
                  </a>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
