import { Link } from "react-router-dom";
import { MapPin, Users, Clock } from "lucide-react";
import { VerificationBadge } from "@/components/shared/VerificationBadge";
import { ProgressBar } from "@/components/shared/ProgressBar";
import type { Campaign } from "@/types/entities";
import { getDaysRemaining } from "@/types/entities";
import { formatCurrency, formatLocation } from "@/lib/format";
import { getDonorCount } from "@/lib/mock/mockData";

interface CampaignCardProps {
  campaign: Campaign;
}

/** The single most-reused component in the app — Cause Listing, Landing's
 * featured campaigns, and Related Campaigns all render this exact card. */
export function CampaignCard({ campaign }: CampaignCardProps) {
  const daysRemaining = getDaysRemaining(campaign);
  const donorCount = getDonorCount(campaign.id); // becomes campaign.donor_count from the API later
  const location = formatLocation(campaign.location_city, campaign.location_country);

  return (
    <div className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden flex flex-col group hover:border-primary transition-all">
      <div className="h-48 bg-surface-container-high relative overflow-hidden">
        <div className="absolute top-4 left-4 flex gap-2">
          {campaign.category && (
            <span className="px-3 py-1 bg-surface-container-highest text-on-surface-variant text-label-caps font-label-caps rounded-full text-[10px]">
              {campaign.category.name}
            </span>
          )}
        </div>
      </div>
      <div className="p-6 flex-1 flex flex-col">
        <VerificationBadge label={`Verified by ${campaign.created_by.username}`} />
        <h3 className="font-headline-sm text-headline-sm mt-3 mb-2 group-hover:text-primary transition-colors">
          {campaign.title}
        </h3>
        {location && (
          <div className="flex items-center gap-1 text-on-surface-variant text-data-table mb-4">
            <MapPin className="w-3.5 h-3.5" />
            <span>{location}</span>
          </div>
        )}
        <div className="mt-auto space-y-4">
          <ProgressBar
            percentage={campaign.funding_percentage}
            label={formatCurrency(campaign.raised_amount, campaign.campaign_currency)}
            sublabel={`${campaign.funding_percentage.toFixed(0)}% of ${formatCurrency(campaign.goal_amount, campaign.campaign_currency)}`}
          />
          <div className="flex items-center justify-between text-label-caps font-label-caps text-on-surface-variant">
            <span className="flex items-center gap-1">
              <Users className="w-3.5 h-3.5" /> {donorCount.toLocaleString()} donors
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {daysRemaining === null ? "Ongoing" : `${daysRemaining}d left`}
            </span>
          </div>
          <Link
            to={`/causes/${campaign.id}`}
            className="block text-center px-6 py-2 border border-primary text-primary font-body-md font-bold rounded hover:bg-primary-fixed transition-colors"
          >
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
}
