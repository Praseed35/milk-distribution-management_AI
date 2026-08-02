export type ReportPreset =
  | "today"
  | "yesterday"
  | "this_week"
  | "last_week"
  | "this_month"
  | "last_month"
  | "this_year";

export interface ReportEnvelope<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  generated_at: string;
}

export interface ReportDateParams {
  preset?: ReportPreset;
  from_date?: string;
  to_date?: string;
  refresh?: boolean;
}

export interface RouteDeliveryParams extends ReportDateParams {
  route_id?: number;
  shift?: string;
}

export interface RevenueParams extends ReportDateParams {
  route_id?: number;
  milk_type_id?: number;
  payment_mode?: string;
  group_by?: string;
}

export interface ConsumptionParams extends ReportDateParams {
  group_by?: string;
}

export interface TokenUtilizationParams {
  route_id?: number;
  customer_id?: number;
  low_threshold?: number;
  refresh?: boolean;
}

export interface CollectionEfficiencyParams extends ReportDateParams {
  route_id?: number;
  min_outstanding?: number;
}

export type DeliveryStatusKey =
  | "DELIVERED"
  | "PENDING_TOKEN"
  | "CASH_SALE"
  | "NOT_DELIVERED"
  | "CANCELLED";

export interface OperationalDashboard {
  report_date: string;
  total_sessions: number;
  total_milk_loaded: number;
  total_milk_delivered: number;
  total_cash_collected: number;
  deliveries_by_status: Record<DeliveryStatusKey, number>;
  pending_token_count: number;
  unclosed_sessions: number;
  unbalanced_sessions: number;
  completed_not_closed: number;
}

export interface RouteDeliveryItem {
  route_id: number;
  route_name: string;
  route_code: string;
  session_count: number;
  delivery_count: number;
  total_loaded_quantity: number;
  total_delivered_quantity: number;
  total_cash_collected: number;
  total_token_registered: number;
  total_returned_quantity: number;
  shortage_surplus: number;
  is_balanced: boolean;
}

export interface RevenueBreakdown {
  source: string;
  payment_mode: string | null;
  route_name: string | null;
  milk_type_name: string | null;
  amount: number;
  percentage: number;
}

export interface RevenueReport {
  date_from: string;
  date_to: string;
  total_revenue: number;
  token_book_revenue: number;
  customer_bill_revenue: number;
  by_source: RevenueBreakdown[];
  by_payment_mode: RevenueBreakdown[];
  by_route: RevenueBreakdown[];
  by_milk_type: RevenueBreakdown[];
}

export interface ConsumptionDay {
  date: string;
  total_quantity: number;
  by_milk_type: { milk_type: string; quantity: number }[];
}

export interface ConsumptionTrend {
  period: string;
  recent_7day_avg: number | null;
  preceding_21day_avg: number | null;
  change_percentage: number | null;
}

export interface CustomerConsumptionReport {
  customer_id: number;
  customer_name: string;
  date_from: string;
  date_to: string;
  group_by: string;
  total_consumption: number;
  average_daily: number;
  days_with_data: number;
  trend: ConsumptionTrend;
  items: ConsumptionDay[];
}

export interface TokenUtilizationItem {
  customer_id: number;
  customer_name: string;
  route_name: string;
  token_number: number;
  milk_type_name: string;
  total_books_issued: number;
  active_books: number;
  completed_books: number;
  total_sheets_used: number;
  total_sheets_remaining: number;
  utilization_percentage: number;
  books_below_20_percent: number;
}

export interface CustomerCollectionItem {
  customer_id: number;
  customer_code: string;
  customer_name: string;
  route_name: string;
  total_billed: number;
  total_paid: number;
  balance: number;
  collection_percentage: number;
  last_bill_date: string | null;
  last_payment_date: string | null;
  aging_current: number;
  aging_31_60: number;
  aging_61_90: number;
  aging_90_plus: number;
}
