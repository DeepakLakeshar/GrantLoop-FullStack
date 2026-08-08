import { FeatureUnavailablePage } from "@/components/shared/FeatureUnavailablePage";

export function HelpCenterPage() {
  return (
    <FeatureUnavailablePage 
      title="Help Center"
      featureName="Help Center"
      reason="because the backend currently does not expose the required APIs"
    />
  );
}
