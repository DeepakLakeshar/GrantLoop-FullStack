import { UnsupportedFeaturePage } from "@/components/shared/UnsupportedFeaturePage";
import { TopNavBar } from "@/components/layout/TopNavBar";

export function HelpCenterPage() {
  return (
    <div className="min-h-screen bg-surface">
      <TopNavBar />
      <main className="p-margin-desktop max-w-container-max mx-auto space-y-8 mt-10">
        <UnsupportedFeaturePage 
          title="Help Center"
          featureName="The Help Center"
          reason="because support documentation is currently being finalized."
        />
      </main>
    </div>
  );
}
