import { useAuth } from "@/context/AuthContext";
import { useQuery } from "@tanstack/react-query";
import { Spinner } from "@/components/shared/Spinner";
import { ErrorBanner } from "@/components/shared/ErrorBanner";

// Placeholder hook – replace with real API when available
function useAssignedMilestones() {
  return useQuery({
    queryKey: ["assignedMilestones"],
    queryFn: async () => {
      // No backend endpoint yet – return empty array
      return [];
    },
    placeholderData: [],
    refetchOnWindowFocus: false,
  });
}

export function AssignedMilestonesPage() {
  const { status, user } = useAuth();
  const { data: milestones = [], isLoading, isError } = useAssignedMilestones();

  if (status !== "authenticated" || !user) {
    // This page should be protected by a route guard, but render a fallback just in case
    return null;
  }

  return (
    <div className="space-y-8">
      <h1 className="font-headline-lg text-headline-lg text-primary">Assigned Milestones</h1>
      {isLoading ? (
        <Spinner size={32} className="text-primary" />
      ) : isError ? (
        <ErrorBanner kind="unknown" message="Failed to load milestones." />
      ) : milestones.length === 0 ? (
        <p className="text-body-md text-on-surface-variant">No milestones assigned yet.</p>
      ) : (
        <ul className="list-disc pl-6 space-y-2">
          {milestones.map((m, i) => (
            <li key={i} className="text-body-md text-on-surface">{JSON.stringify(m)}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
