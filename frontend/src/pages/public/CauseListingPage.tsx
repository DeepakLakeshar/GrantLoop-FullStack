import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { Footer } from "@/components/layout/Footer";
import { FilterSidebar } from "@/components/feature/FilterSidebar";
import { CampaignCard } from "@/components/feature/CampaignCard";
import { SearchBar } from "@/components/shared/SearchBar";
import { Pagination } from "@/components/shared/Pagination";
import { Spinner } from "@/components/shared/Spinner";
import { useCampaignList, useCategories } from "@/hooks/useCampaigns";
import type { CampaignFilters } from "@/lib/mock/campaignsApi";

export function CauseListingPage() {
  const [searchParams] = useSearchParams();
  const [filters, setFilters] = useState<CampaignFilters>({
    categorySlug: searchParams.get("category") ?? undefined,
    sort: "newest",
    page: 1,
    pageSize: 12,
  });

  const { data: categories } = useCategories();
  const { data, isLoading, isError } = useCampaignList(filters);

  return (
    <div className="min-h-screen flex flex-col">
      <TopNavBar />
      <main className="flex-1 max-w-container-max mx-auto px-margin-desktop py-12 flex flex-col md:flex-row gap-gutter w-full">
        <FilterSidebar categories={categories ?? []} filters={filters} onChange={setFilters} />

        <div className="flex-1">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div>
              <h1 className="font-headline-lg text-headline-lg text-primary">Active Causes</h1>
              <p className="text-on-surface-variant font-body-lg">
                {isLoading ? "Loading…" : `Showing ${data?.count ?? 0} verified campaigns`}
              </p>
            </div>
            <div className="w-full md:w-72">
              <SearchBar value={filters.search ?? ""} onChange={(v) => setFilters((f) => ({ ...f, search: v || undefined, page: 1 }))} />
            </div>
          </div>

          {isLoading && (
            <div className="flex justify-center py-24">
              <Spinner size={32} />
            </div>
          )}

          {isError && (
            <p className="text-center text-on-surface-variant py-24">
              Something went wrong loading campaigns. Please try again.
            </p>
          )}

          {data && data.results.length === 0 && (
            <p className="text-center text-on-surface-variant py-24">No campaigns match these filters.</p>
          )}

          {data && data.results.length > 0 && (
            <>
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-gutter" role="list">
                {data.results.map((campaign) => (
                  <div role="listitem" key={campaign.id}>
                    <CampaignCard campaign={campaign} />
                  </div>
                ))}
              </div>
              <Pagination
                page={filters.page ?? 1}
                pageSize={filters.pageSize ?? 12}
                totalCount={data.count}
                onPageChange={(page) => setFilters((f) => ({ ...f, page }))}
              />
            </>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
