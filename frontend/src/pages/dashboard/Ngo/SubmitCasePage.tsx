import { FeatureUnavailablePage } from "@/components/shared/FeatureUnavailablePage";

export function SubmitCasePage() {
  return (
    <FeatureUnavailablePage 
      title="Submit Case"
      featureName="Case submission"
      reason="because the case submission workflow has been deferred from the v1.0.0 milestone."
    />
  );
}
