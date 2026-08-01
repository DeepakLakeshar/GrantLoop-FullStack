import { Link } from "react-router-dom";
import { ShieldCheck, Eye, FileCheck2, ArrowRight, Verified } from "lucide-react";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { Footer } from "@/components/layout/Footer";
import { MetricCard } from "@/components/shared/MetricCard";
import { CampaignCard } from "@/components/feature/CampaignCard";
import { Spinner } from "@/components/shared/Spinner";
import { useCampaignList, useCategories } from "@/hooks/useCampaigns";

const PROTOCOL_STEPS = [
  { step: "01", title: "Donor Commitment", body: "Select a verified cause and commit funds via a secure gateway." },
  { step: "02", title: "Milestone Tranching", body: "Funds are held and released against completed, verified milestones." },
  { step: "03", title: "Evidence Submission", body: "Execution partners submit receipts, photos, and progress reports." },
  { step: "04", title: "Institutional Verification", body: "An independent institution reviews evidence before release." },
  { step: "05", title: "Fund Release", body: "Verified releases move directly to the NGO's connected account." },
  { step: "06", title: "Impact Reflection", body: "Donors receive the full evidence trail, completing the loop." },
];

export function LandingPage() {
  const { data: featured, isLoading } = useCampaignList({ sort: "most_funded", pageSize: 3 });
  const { data: categories } = useCategories();

  return (
    <div className="min-h-screen flex flex-col">
      <TopNavBar />
      <main className="flex-1">
        {/* Hero */}
        <section className="max-w-container-max mx-auto px-margin-desktop py-24 grid grid-cols-1 lg:grid-cols-12 gap-gutter items-center">
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-surface-container-high border border-outline-variant rounded-full">
              <ShieldCheck className="w-4 h-4 text-primary" />
              <span className="font-label-caps text-label-caps text-primary uppercase tracking-widest">
                Institutional Grade Accountability
              </span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-primary max-w-2xl">
              Milestone-verified giving. Full transparency, every step.
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-xl">
              GrantLoop connects donors with verified causes and shows exactly where the money goes, who
              verified the need, and what's been accomplished — before the next release of funds.
            </p>
            <div className="flex flex-wrap gap-4 pt-2">
              <Link to="/causes" className="bg-primary text-white px-8 py-4 rounded-lg font-bold text-lg hover:opacity-90 transition-all flex items-center gap-2">
                Explore Verified Causes <ArrowRight className="w-5 h-5" />
              </Link>
              <Link to="/pricing" className="border border-outline text-primary px-8 py-4 rounded-lg font-bold text-lg hover:bg-surface-container-low transition-all">
                See How Fees Work
              </Link>
            </div>
          </div>
        </section>

        {/* Trust strip / Why GrantLoop */}
        <section className="py-16 px-margin-desktop max-w-container-max mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
            <div className="p-8 bg-surface-container-lowest border border-outline-variant rounded-xl">
              <ShieldCheck className="w-8 h-8 text-primary mb-4" />
              <h3 className="font-headline-sm text-headline-sm text-primary mb-2">Rigorous Verification</h3>
              <p className="text-body-md text-on-surface-variant">
                Every organization is reviewed for financial and operational legitimacy before listing.
              </p>
            </div>
            <div className="p-8 bg-surface-container-lowest border border-outline-variant rounded-xl">
              <Eye className="w-8 h-8 text-primary mb-4" />
              <h3 className="font-headline-sm text-headline-sm text-primary mb-2">Real-Time Transparency</h3>
              <p className="text-body-md text-on-surface-variant">
                See exactly when and how a contribution moves from the platform to the field.
              </p>
            </div>
            <div className="p-8 bg-surface-container-lowest border border-outline-variant rounded-xl">
              <FileCheck2 className="w-8 h-8 text-primary mb-4" />
              <h3 className="font-headline-sm text-headline-sm text-primary mb-2">Evidence of Execution</h3>
              <p className="text-body-md text-on-surface-variant">
                Milestone completion requires receipts, photos, and reports before the next release.
              </p>
            </div>
          </div>
        </section>

        {/* Statistics */}
        <section className="py-16 px-margin-desktop max-w-container-max mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
            <MetricCard label="Verified Campaigns" value="42" />
            <MetricCard label="Funds Disbursed" value="$1.2M+" />
            <MetricCard label="Milestones Completed" value="128" />
          </div>
        </section>

        {/* Categories */}
        {categories && categories.length > 0 && (
          <section className="py-16 px-margin-desktop max-w-container-max mx-auto">
            <h2 className="font-headline-md text-headline-md text-primary mb-8 text-center">Browse by Category</h2>
            <div className="flex flex-wrap justify-center gap-4">
              {categories.map((cat) => (
                <Link
                  key={cat.id}
                  to={`/causes?category=${cat.slug}`}
                  className="px-6 py-3 bg-surface-container-low border border-outline-variant rounded-full font-body-md font-medium hover:border-primary hover:text-primary transition-colors"
                >
                  {cat.name}
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Featured campaigns */}
        <section className="py-16 px-margin-desktop max-w-container-max mx-auto">
          <div className="flex justify-between items-end mb-8">
            <h2 className="font-headline-md text-headline-md text-primary">Featured Verified Causes</h2>
            <Link to="/causes" className="text-primary font-bold hover:underline">View all</Link>
          </div>
          {isLoading ? (
            <div className="flex justify-center py-12"><Spinner size={28} /></div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
              {featured?.results.map((c) => <CampaignCard key={c.id} campaign={c} />)}
            </div>
          )}
        </section>

        {/* How GrantLoop Works */}
        <section className="py-24 bg-surface-container-low">
          <div className="max-w-container-max mx-auto px-margin-desktop">
            <h2 className="font-headline-lg text-headline-lg text-primary mb-4">The GrantLoop Protocol</h2>
            <p className="text-body-lg text-on-surface-variant mb-16 max-w-2xl">
              A six-step framework ensuring accountability from donation to delivery.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
              {PROTOCOL_STEPS.map((s) => (
                <div key={s.step} className="relative group">
                  <div className="absolute -top-4 -left-4 w-12 h-12 bg-primary text-white flex items-center justify-center font-bold text-xl rounded-lg shadow-lg z-10">
                    {s.step}
                  </div>
                  <div className="bg-surface-container-lowest p-8 border border-outline-variant h-full pt-12 hover:border-primary transition-colors">
                    <h4 className="font-headline-sm text-headline-sm text-primary mb-4">{s.title}</h4>
                    <p className="text-body-md text-on-surface-variant">{s.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Success stories (transparency section) */}
        <section className="py-24 px-margin-desktop max-w-container-max mx-auto">
          <div className="bg-primary text-white rounded-2xl p-12 flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-4">
              <Verified className="w-10 h-10" />
              <div>
                <h3 className="font-headline-md text-headline-md">Community Health Outreach: Naivasha</h3>
                <p className="opacity-80 mt-1">Fully funded and completed — 8 communities served, evidence on file.</p>
              </div>
            </div>
            <Link to="/causes/c3" className="bg-white text-primary px-6 py-3 rounded-lg font-bold hover:opacity-90 transition-all">
              Read the story
            </Link>
          </div>
        </section>

        {/* CTA */}
        <section className="py-24 px-margin-desktop max-w-container-max mx-auto text-center">
          <h2 className="font-headline-lg text-headline-lg text-primary mb-4">Ready to fund verified impact?</h2>
          <Link to="/causes" className="inline-block bg-primary text-white px-8 py-4 rounded-lg font-bold text-lg hover:opacity-90 transition-all">
            Explore Verified Causes
          </Link>
        </section>
      </main>
      <Footer />
    </div>
  );
}
