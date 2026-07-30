export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
}

export interface PaginatedResponse<T> {
  data?: T[];
  sessions?: T[];
  deliveries?: T[];
  total: number;
  page?: number;
  page_size?: number;
  generated_at?: string;
}

export interface ApiError {
  detail: string;
  errors?: Record<string, string[]>;
}

export interface DateRangeParams {
  from_date?: string;
  to_date?: string;
  preset?: "today" | "yesterday" | "this_week" | "last_week" | "this_month" | "last_month" | "this_year";
}
