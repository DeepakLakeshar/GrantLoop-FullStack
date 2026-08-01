import type { Category } from "@/types/entities";
import type { CampaignFilters } from "@/lib/mock/campaignsApi";

interface FilterSidebarProps {
  categories: Category[];
  filters: CampaignFilters;
  onChange: (filters: CampaignFilters) => void;
}

// Country list kept short and explicit rather than a full ISO 3166 list —
// expand as real campaign data warrants it.
const COUNTRIES = [
  { code: "KE", name: "Kenya" },
  { code: "PE", name: "Peru" },
  { code: "IN", name: "India" },
];

export function FilterSidebar({ categories, filters, onChange }: FilterSidebarProps) {
  function update(patch: Partial<CampaignFilters>) {
    onChange({ ...filters, ...patch, page: 1 });
  }

  return (
    <aside className="w-full md:w-72 shrink-0 space-y-8">
      <div className="space-y-6">
        <h2 className="font-label-caps text-label-caps text-on-surface-variant mb-2 uppercase tracking-widest">
          Filters
        </h2>

        <div className="space-y-2">
          <label htmlFor="status-filter" className="text-headline-sm font-headline-sm block">
            Status
          </label>
          <select
            id="status-filter"
            value={filters.status ?? ""}
            onChange={(e) => update({ status: (e.target.value || undefined) as CampaignFilters["status"] })}
            className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-body-md focus:ring-primary focus:border-primary"
          >
            <option value="">All Active Causes</option>
            <option value="live">Currently Funding</option>
            <option value="completed">Successfully Funded</option>
          </select>
        </div>

        <div className="space-y-2">
          <label htmlFor="category-filter" className="text-headline-sm font-headline-sm block">
            Category
          </label>
          <select
            id="category-filter"
            value={filters.categorySlug ?? ""}
            onChange={(e) => update({ categorySlug: e.target.value || undefined })}
            className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-body-md focus:ring-primary focus:border-primary"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.slug}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label htmlFor="location-filter" className="text-headline-sm font-headline-sm block">
            Location
          </label>
          <select
            id="location-filter"
            value={filters.countryCode ?? ""}
            onChange={(e) => update({ countryCode: e.target.value || undefined })}
            className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-body-md focus:ring-primary focus:border-primary"
          >
            <option value="">Any Country</option>
            {COUNTRIES.map((c) => (
              <option key={c.code} value={c.code}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-headline-sm font-headline-sm block">Goal Amount</label>
          <div className="flex gap-2">
            <input
              type="number"
              min={0}
              placeholder="Min"
              aria-label="Minimum goal amount"
              value={filters.minGoal ?? ""}
              onChange={(e) => update({ minGoal: e.target.value ? Number(e.target.value) : undefined })}
              className="w-1/2 bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-body-md focus:ring-primary focus:border-primary"
            />
            <input
              type="number"
              min={0}
              placeholder="Max"
              aria-label="Maximum goal amount"
              value={filters.maxGoal ?? ""}
              onChange={(e) => update({ maxGoal: e.target.value ? Number(e.target.value) : undefined })}
              className="w-1/2 bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-body-md focus:ring-primary focus:border-primary"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="sort-filter" className="text-headline-sm font-headline-sm block">
            Sort by
          </label>
          <select
            id="sort-filter"
            value={filters.sort ?? "newest"}
            onChange={(e) => update({ sort: e.target.value as CampaignFilters["sort"] })}
            className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-body-md focus:ring-primary focus:border-primary"
          >
            <option value="newest">Newest</option>
            <option value="most_funded">Highest Impact</option>
            <option value="ending_soon">Ending Soon</option>
            <option value="goal_high_low">Goal: High to Low</option>
          </select>
        </div>
      </div>
    </aside>
  );
}
