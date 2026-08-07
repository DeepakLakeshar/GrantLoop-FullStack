export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  page: number;
  pageSize: number;
}

export interface DrfPaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
