import { CampaignCard } from "@/components/feature/CampaignCard";
import type { Campaign } from "@/types/entities";

interface RelatedCampaignsProps {
  campaigns: Campaign[];
}

export function RelatedCampaigns({ campaigns }: RelatedCampaignsProps) {
  if (campaigns.length === 0) return null;

  return (
    <section>
      <h2 className="font-headline-md text-headline-md text-primary mb-8">Related Causes</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
        {campaigns.map((c) => (
          <CampaignCard key={c.id} campaign={c} />
        ))}
      </div>
    </section>
  );
}
