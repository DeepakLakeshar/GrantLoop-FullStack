import { FeatureUnavailablePage } from "@/components/shared/FeatureUnavailablePage";

export function InstitutionFundReleasePage() {
  return (
    <FeatureUnavailablePage
      title="Fund Releases"
      featureName="Fund release management"
      reason="because fund release workflows are deferred from the v1.0.0 milestone."
    />
  );
}