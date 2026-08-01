export type DeliverySessionStatus = "PLANNED" | "STARTED" | "COMPLETED" | "CLOSED";

export type Shift = "MORNING" | "EVENING";

export type ReconciliationStatus = "BALANCED" | "UNBALANCED" | "PENDING";

export interface DeliverySessionCreate {
  route_id: number;
  delivery_date: string;
  shift: Shift;
  delivery_partner_id: number;
}

export interface DeliverySessionDispatch {
  total_milk_loaded: number;
}

export interface DeliverySessionReopen {
  reason: string;
}

export interface DeliverySessionResponse {
  id: number;
  route_id: number;
  route_name: string | null;
  delivery_date: string;
  shift: Shift;
  delivery_partner_id: number;
  delivery_partner_name: string | null;
  status: DeliverySessionStatus;
  total_milk_loaded: number;
  total_token_registered: number;
  total_cash_sales: number;
  total_returned_milk: number;
  reconciliation_status: ReconciliationStatus;
  reopen_count: number;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface DeliverySessionDeliverySummary {
  id: number;
  customer_id: number;
  customer_name: string | null;
  milk_type_name: string | null;
  planned_quantity: number;
  delivered_quantity: number;
  delivery_status: string;
  delivery_source: string;
  token_sheet_number: number | null;
}

export interface DeliverySessionDetailResponse extends DeliverySessionResponse {
  deliveries: DeliverySessionDeliverySummary[];
}

export interface DeliverySessionListResponse {
  sessions: DeliverySessionResponse[];
  total: number;
}

export interface ReconciliationResponse {
  session_id: number;
  loaded_milk: number;
  token_registered: number;
  cash_sales: number;
  returned_milk: number;
  total_accounted: number;
  difference: number;
  is_balanced: boolean;
  status: ReconciliationStatus;
}

export interface ReconciliationValidationIssue {
  code: string;
  message: string;
  severity: string;
}

export interface ReconciliationValidationResponse {
  can_close: boolean;
  is_balanced: boolean;
  issues: ReconciliationValidationIssue[];
}

export interface SessionReportSummary {
  total_customers: number;
  delivered: number;
  pending_token: number;
  cash_sale: number;
  not_delivered: number;
}

export interface SessionReportMilkSummary {
  loaded: number;
  token_registered: number;
  cash_sales: number;
  returned: number;
}

export interface SessionReportResponse {
  session_id: number;
  route_name: string | null;
  delivery_date: string;
  shift: Shift;
  summary: SessionReportSummary;
  milk_summary: SessionReportMilkSummary;
}
