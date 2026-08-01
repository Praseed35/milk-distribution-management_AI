export type DeliveryStatus =
  | "DELIVERED"
  | "PENDING_TOKEN"
  | "CASH_SALE"
  | "NOT_DELIVERED"
  | "CANCELLED"
  | "PLANNED";

export type DeliverySource = "PLANNED" | "UNPLANNED";

export interface DailyDeliveryResponse {
  id: number;
  session_id: number;
  customer_id: number;
  customer_name: string | null;
  milk_type_id: number;
  milk_type_name: string | null;
  planned_quantity: number;
  delivered_quantity: number;
  delivery_status: string;
  delivery_source: string;
  token_sheet_number: number | null;
  token_book_issue_id: number | null;
  cash_amount: number | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface SessionDeliveriesResponse {
  session_id: number;
  deliveries: DailyDeliveryResponse[];
  total: number;
}

export interface ChecklistCustomer {
  customer_id: number;
  customer_name: string;
  address: string | null;
  phone: string | null;
  milk_type: string;
  quantity: number;
}

export interface DeliveryChecklistResponse {
  session_id: number;
  route_name: string | null;
  delivery_date: string;
  shift: string;
  total_expected: number;
  customers: ChecklistCustomer[];
}

export interface DailyDeliveryUpdate {
  delivery_status?: string | null;
  delivered_quantity?: number | null;
  token_sheet_number?: number | null;
  cash_amount?: number | null;
  remarks?: string | null;
  version?: number | null;
}

export interface UnplannedDeliveryCreate {
  session_id: number;
  customer_id: number;
  milk_type_id: number;
  delivered_quantity: number;
  delivery_status: string;
  registration_method: "TOKEN_SHEET" | "CASH" | "PENDING";
  token_sheet_number?: number | null;
  reason: string;
}

export interface TokenValidationRequest {
  customer_id: number;
  milk_type_id: number;
  sheet_number: number;
  token_book_issue_id?: number | null;
}

export interface TokenValidationWarning {
  code: string;
  message: string;
  severity: string;
  expected_sheet: number | null;
}

export interface TokenValidationResponse {
  is_valid: boolean;
  warnings: TokenValidationWarning[];
  can_proceed: boolean;
  requires_acknowledgment: boolean;
}

export interface TokenRegistrationRequest {
  token_sheet_number: number;
  acknowledged_warnings: string[];
  acknowledgment_reason?: string | null;
}

export interface TokenRegistrationResponse {
  delivery_id: number;
  sheet_registered: boolean;
  token_book_issue_id: number | null;
  new_current_sheet: number | null;
  warnings_logged: number;
  message: string;
}

export interface DeliveryWarning {
  id: number;
  warning_code: string;
  warning_message: string;
  sheet_number: number;
  expected_sheet: number | null;
  acknowledged_by: number | null;
  acknowledged_at: string | null;
}

export interface DeliveryWarningsResponse {
  delivery_id: number;
  warnings: DeliveryWarning[];
}

export interface DailyDeliveryEditRequest {
  delivery_status?: string | null;
  return_token_sheet: boolean;
  reason: string;
  version?: number | null;
}

export interface DailyDeliveryEditResponse {
  delivery_id: number;
  old_status: string;
  new_status: string;
  token_sheet_returned: boolean;
  token_book_issue_id: number | null;
  sheet_number: number | null;
  new_current_sheet: number | null;
  message: string;
}

export interface SessionEditResponse {
  edit_id: number;
  delivery_id: number | null;
  customer_name: string | null;
  edit_type: string;
  old_value: Record<string, unknown>;
  new_value: Record<string, unknown>;
  reason: string;
  edited_by: string | null;
  edited_at: string;
}

export interface TokenBookStatus {
  book_issue_id: number;
  book_number: string;
  milk_type: string;
  issue_date: string;
  status: string;
  sheets_used: number;
  sheets_remaining: number;
  is_old_book: boolean;
}

export interface CustomerTokenStatusResponse {
  customer_id: number;
  customer_name: string | null;
  token_books: TokenBookStatus[];
  has_old_book_with_remaining: boolean;
  old_book_remaining: number;
}

export interface CashSaleCreate {
  customer_name: string;
  customer_phone?: string | null;
  milk_type_id: number;
  quantity: number;
  amount: number;
  payment_method?: string;
}

export interface CashSaleResponse {
  id: number;
  session_id: number;
  customer_name: string;
  milk_type_name: string | null;
  quantity: number;
  amount: number;
  payment_method: string;
  created_at: string;
}
