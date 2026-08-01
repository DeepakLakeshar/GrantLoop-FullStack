import type { CampaignUpdate } from "@/types/entities";
import { formatDate } from "@/lib/format";

interface CampaignUpdateCardProps {
  update: CampaignUpdate;
}

export function CampaignUpdateCard({ update }: CampaignUpdateCardProps) {
  return (
    <div className="bg-white p-6 rounded-xl border border-outline-variant shadow-sm">
      <div className="flex justify-between items-start mb-3">
        <span className="font-label-caps text-label-caps text-on-surface-variant">{formatDate(update.created_at)}</span>
        <span className="text-[10px] font-label-caps text-on-secondary-container bg-secondary-container px-2 py-0.5 rounded font-bold uppercase">
          {update.posted_by.role.replace(/_/g, " ")}
        </span>
      </div>
      {update.image_url && (
        <div className="aspect-video rounded-lg overflow-hidden mb-4 bg-surface-container-high">
          <img src={update.image_url} alt="" className="w-full h-full object-cover" />
        </div>
      )}
      <p className="text-body-md text-on-surface-variant">{update.content}</p>
    </div>
  );
}
