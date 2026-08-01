import { useParams } from "react-router-dom";
import { MapPin, Calendar } from "lucide-react";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { Footer } from "@/components/layout/Footer";
import { VerificationBadge } from "@/components/shared/VerificationBadge";
import { ProgressBar } from "@/components/shared/ProgressBar";
import { Spinner } from "@/components/shared/Spinner";
import { MilestoneCard } from "@/components/feature/MilestoneCard";
import { BeneficiaryList } from "@/components/feature/BeneficiaryList";
import { DocumentGallery, DocumentList } from "@/components/feature/DocumentGallery";
import { FundAllocationChart } from "@/components/feature/FundAllocationChart";
import { CampaignUpdateCard } from "@/components/feature/CampaignUpdateCard";
import { TransparencyTimeline } from "@/components/feature/TransparencyTimeline";
import { DonationWidget } from "@/components/feature/DonationWidget";
import { RelatedCampaigns } from "@/components/feature/RelatedCampaigns";
import { useCampaignDetail, useRelatedCampaigns } from "@/hooks/useCampaigns";
import { formatCurrency, formatLocation } from "@/lib/format";

// Campaign.description is a single field in the frozen schema — per
// instruction, no redesign of the database. This splits the one field
// into Problem / Why Funding Is Needed / Expected Impact by paragraph
// position, a presentation-only convention (double-newline-separated),
// not a new schema field. If an NGO writes fewer than 3 paragraphs, the
// remaining sections simply don't render — no fabricated content.
function splitStory(description: string): { problem?: string; why?: string; impact?: string } {
  const paragraphs = description.split(/\n\n+/).filter(Boolean);
  return { problem: paragraphs[0], why: paragraphs[1], impact: paragraphs[2] };
}

export function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, isError } = useCampaignDetail(id);
  const { data: related } = useRelatedCampaigns(id, data?.campaign.category?.slug);

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <TopNavBar />
        <main className="flex-1 flex items-center justify-center"><Spinner size={32} /></main>
        <Footer />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="min-h-screen flex flex-col">
        <TopNavBar />
        <main className="flex-1 flex items-center justify-center text-on-surface-variant">Campaign not found.</main>
        <Footer />
      </div>
    );
  }

  const { campaign, beneficiaries, milestones, fundAllocation, updates, transparencyLog, documents, donorCount } = data;
  const story = splitStory(campaign.description);
  const location = formatLocation(campaign.location_city, campaign.location_country);

  return (
    <div className="min-h-screen flex flex-col">
      <TopNavBar />
      <main className="flex-1 max-w-container-max mx-auto px-margin-desktop py-12 w-full">
        <div className="grid grid-cols-12 gap-gutter items-start">
          {/* Main column */}
          <div className="col-span-12 lg:col-span-8 space-y-12">
            {/* Hero */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                {campaign.category && (
                  <span className="font-label-caps text-label-caps text-secondary uppercase tracking-widest bg-secondary-container px-2 py-1 rounded">
                    {campaign.category.name}
                  </span>
                )}
              </div>
              <h1 className="font-headline-lg text-headline-lg text-primary mb-4">{campaign.title}</h1>
              <div className="flex flex-wrap items-center gap-4 text-on-surface-variant mb-6">
                <VerificationBadge label={`Verified · ${campaign.created_by.username}`} />
                {location && (
                  <span className="flex items-center gap-1"><MapPin className="w-4 h-4" />{location}</span>
                )}
                {campaign.start_date && (
                  <span className="flex items-center gap-1"><Calendar className="w-4 h-4" />Launched {campaign.start_date}</span>
                )}
              </div>
              <ProgressBar
                percentage={campaign.funding_percentage}
                label={formatCurrency(campaign.raised_amount, campaign.campaign_currency)}
                sublabel={`raised of ${formatCurrency(campaign.goal_amount, campaign.campaign_currency)} · ${donorCount.toLocaleString()} donors`}
                height="md"
              />
            </section>

            {/* Story */}
            <section className="prose prose-slate max-w-none space-y-8">
              {story.problem && (
                <div>
                  <h2 className="font-headline-md text-headline-md text-primary mb-3">The Problem</h2>
                  <p className="font-body-lg text-body-lg text-on-surface-variant leading-relaxed">{story.problem}</p>
                </div>
              )}
              {story.why && (
                <div>
                  <h2 className="font-headline-md text-headline-md text-primary mb-3">Why Funding Is Needed</h2>
                  <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">{story.why}</p>
                </div>
              )}
              {story.impact && (
                <div>
                  <h2 className="font-headline-md text-headline-md text-primary mb-3">Expected Impact</h2>
                  <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">{story.impact}</p>
                </div>
              )}
            </section>

            {/* Gallery */}
            <section>
              <h2 className="font-headline-md text-headline-md text-primary mb-6">Gallery</h2>
              <DocumentGallery documents={documents} />
            </section>

            {/* Documents */}
            <section>
              <h2 className="font-headline-md text-headline-md text-primary mb-6">Supporting Documents</h2>
              <DocumentList documents={documents} />
            </section>

            {/* Beneficiaries */}
            {beneficiaries.length > 0 && (
              <section>
                <h2 className="font-headline-md text-headline-md text-primary mb-6">Beneficiaries</h2>
                <BeneficiaryList beneficiaries={beneficiaries} />
              </section>
            )}

            {/* Milestones */}
            {milestones.length > 0 && (
              <section>
                <h2 className="font-headline-md text-headline-md text-primary mb-6">Milestones</h2>
                <div className="space-y-4">
                  {milestones.map((m) => (
                    <MilestoneCard key={m.id} milestone={m} currency={campaign.campaign_currency} />
                  ))}
                </div>
              </section>
            )}

            {/* Campaign updates */}
            {updates.length > 0 && (
              <section>
                <h2 className="font-headline-md text-headline-md text-primary mb-6">Campaign Updates</h2>
                <div className="space-y-6">
                  {updates.map((u) => <CampaignUpdateCard key={u.id} update={u} />)}
                </div>
              </section>
            )}

            {/* Transparency timeline */}
            <section>
              <h2 className="font-headline-md text-headline-md text-primary mb-6">Transparency Timeline</h2>
              <TransparencyTimeline entries={transparencyLog} />
            </section>

            {/* Fund allocation */}
            {fundAllocation && (
              <section>
                <h2 className="font-headline-md text-headline-md text-primary mb-8">Fund Allocation</h2>
                <FundAllocationChart allocation={fundAllocation} />
              </section>
            )}
          </div>

          {/* Sidebar */}
          <aside className="col-span-12 lg:col-span-4 sticky top-24 space-y-6">
            <DonationWidget campaign={campaign} />
          </aside>
        </div>

        {/* Related campaigns */}
        {related && related.length > 0 && (
          <div className="mt-20">
            <RelatedCampaigns campaigns={related} />
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
