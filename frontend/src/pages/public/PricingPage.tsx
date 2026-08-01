import { useState } from "react";
import { ShieldCheck, Landmark, Percent, ChevronDown } from "lucide-react";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { Footer } from "@/components/layout/Footer";
import { MetricCard } from "@/components/shared/MetricCard";

// Approved decision #1 (Frontend Architecture Review): GrantLoop is not
// permanently fee-free. platform_percentage is a real, configurable
// FundAllocation field that may legitimately be 0% for some campaigns —
// this page describes that, replacing the original mockup's "0% forever"
// claim. Same visual layout as approved, corrected copy only.

const FAQS = [
  {
    q: "Does GrantLoop take a cut of my donation?",
    a: "GrantLoop's platform fee is set per campaign by the verifying institution as part of that campaign's Fund Allocation, alongside the beneficiary and execution percentages. Many campaigns run at or near 0%, subsidized by institutional partners — but this is configured per campaign, not a fixed platform-wide promise.",
  },
  {
    q: "Where can I see the exact split for a campaign?",
    a: "Every Campaign Detail page shows the live Beneficiary / Execution / Platform breakdown for that specific campaign, sourced directly from its Fund Allocation record — not a marketing estimate.",
  },
  {
    q: "Are payment processing fees separate from the platform fee?",
    a: "Yes. Payment gateway costs (Razorpay or Stripe, selected automatically by your currency) are a separate pass-through cost of the underlying payment rails, distinct from GrantLoop's own platform percentage.",
  },
  {
    q: "Can I see exactly who received my funds?",
    a: "Yes — every campaign's Transparency Timeline and Fund Release history show verified disbursements as they happen.",
  },
];

export function PricingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <div className="min-h-screen flex flex-col">
      <TopNavBar />
      <main className="flex-1 max-w-container-max mx-auto px-margin-desktop py-16 space-y-24">
        {/* Hero */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-secondary-container text-on-secondary-container rounded-full">
              <ShieldCheck className="w-[18px] h-[18px]" />
              <span className="font-label-caps text-[10px] tracking-widest uppercase">
                Institutional Integrity Standard
              </span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-primary max-w-xl">
              Every fee is configured per campaign. Every split is visible before you give.
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg">
              GrantLoop doesn't charge a fixed platform-wide fee. Each campaign's institution sets a Beneficiary /
              Execution / Platform split as part of verification — you always see the real number for the specific
              campaign you're supporting.
            </p>
          </div>
          <div className="bg-surface-container-lowest border border-outline-variant p-8 rounded-2xl shadow-sm space-y-6">
            <div className="flex items-center gap-3">
              <Percent className="w-5 h-5 text-primary" />
              <span className="font-label-caps text-label-caps text-primary uppercase">Example campaign split</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-body-md">
                <span>Beneficiary</span>
                <span className="font-bold text-secondary">80%</span>
              </div>
              <div className="flex justify-between text-body-md">
                <span>Execution</span>
                <span className="font-bold text-primary">15%</span>
              </div>
              <div className="flex justify-between text-body-md">
                <span>Platform</span>
                <span className="font-bold text-on-surface-variant">5%</span>
              </div>
            </div>
            <p className="text-data-table text-on-surface-variant italic">
              Illustrative only — the real split for any campaign is shown on its own Campaign Detail page.
            </p>
          </div>
        </section>

        {/* How fees are set */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
          <MetricCard label="Set per campaign" value="Not fixed" trend="Institution-approved at verification" />
          <MetricCard label="Can be as low as" value="0%" trend="When subsidized by a partner" />
          <MetricCard label="Always visible" value="Before you give" trend="On every Campaign Detail page" />
        </section>

        {/* How we fund operations */}
        <section className="bg-surface-container-low border border-outline-variant rounded-xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <Landmark className="w-6 h-6 text-primary" />
            <h2 className="font-headline-md text-headline-md text-primary">How the platform percentage is used</h2>
          </div>
          <p className="text-body-md text-on-surface-variant max-w-3xl">
            The platform percentage set on a campaign's Fund Allocation covers GrantLoop's operating costs —
            verification infrastructure, evidence storage, and institutional review tooling. It is set by the
            verifying institution during the review process, disclosed on the campaign itself, and never changed
            after a campaign goes live.
          </p>
        </section>

        {/* FAQ */}
        <section className="max-w-3xl mx-auto">
          <h2 className="font-headline-md text-headline-md text-primary mb-8 text-center">Fee &amp; Transparency FAQ</h2>
          <div className="space-y-3">
            {FAQS.map((faq, i) => (
              <div key={faq.q} className="border border-outline-variant rounded-lg bg-surface-container-lowest overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex justify-between items-center p-6 text-left font-headline-sm text-primary hover:bg-surface-container-low transition-colors"
                  aria-expanded={openFaq === i}
                >
                  {faq.q}
                  <ChevronDown className={`w-5 h-5 transition-transform ${openFaq === i ? "rotate-180" : ""}`} />
                </button>
                {openFaq === i && (
                  <div className="px-6 pb-6 text-on-surface-variant border-t border-outline-variant pt-4">{faq.a}</div>
                )}
              </div>
            ))}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
