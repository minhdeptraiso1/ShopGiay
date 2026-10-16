export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ListQuery {
  page?: number;
  search?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  today?: boolean;
}
