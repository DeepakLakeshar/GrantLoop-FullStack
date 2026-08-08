interface FeatureUnavailablePageProps {
  title: string;
  featureName: string;
  reason?: string;
}

export function FeatureUnavailablePage({ title, featureName, reason }: FeatureUnavailablePageProps) {
  const defaultReason = `because the backend does not currently expose ${featureName.toLowerCase()} endpoints.`;
  const message = `${featureName} is not available in GrantLoop v1.0.0 ${reason || defaultReason} It will automatically become available when backend support is added.`;

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="font-headline-lg text-headline-lg text-primary">{title}</h1>
      </div>
      <div className="bg-surface-container-lowest p-8 rounded-lg border border-outline-variant text-center max-w-2xl mx-auto mt-12">
        <h2 className="text-headline-sm font-bold text-on-surface mb-4">Feature Unavailable</h2>
        <p className="text-body-lg text-on-surface-variant">
          {message}
        </p>
      </div>
    </div>
  );
}
