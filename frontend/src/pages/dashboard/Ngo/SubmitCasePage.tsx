import { UnsupportedFeaturePage } from "@/components/shared/UnsupportedFeaturePage";

export function SubmitCasePage() {
  return (
    <UnsupportedFeaturePage 
      title="Submit Case"
      featureName="Case submission"
      reason="because the case submission workflow has been deferred from the v1.0.0 milestone."
    />
  );
}
