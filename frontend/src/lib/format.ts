export function formatCurrency(amount: number, currencyCode: string): string {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: currencyCode,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

const COUNTRY_NAMES = new Intl.DisplayNames(undefined, { type: "region" });
export function formatLocation(city: string, countryCode: string): string {
  if (!city && !countryCode) return "";
  const country = countryCode ? COUNTRY_NAMES.of(countryCode) : "";
  return [city, country].filter(Boolean).join(", ");
}
