export type PaymentMode = "CASH" | "UPI" | "CARD" | "CHEQUE" | "BANK_TRANSFER";

export type PaymentType = "ADVANCE" | "BILL_PAYMENT";

export type BillStatus = "PENDING" | "PARTIAL" | "PAID" | "OVERDUE" | "CANCELLED";

export interface CustomerPaymentCreate {
  customer_id: number;
  amount: number;
  payment_mode: PaymentMode;
  payment_type: PaymentType;
  reference_number?: string | null;
  bill_id?: number | null;
  remarks?: string | null;
}

export interface CustomerPaymentResponse {
  id: number;
  customer_id: number;
  amount: number;
  payment_mode: string;
  payment_type: string;
  reference_number: string | null;
  bill_id: number | null;
  payment_date: string;
  collected_by: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CustomerPaymentListResponse {
  id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  payment_date: string;
  amount: number;
  payment_mode: string;
  payment_type: string;
  reference_number: string | null;
  bill_id: number | null;
  is_active: boolean;
}

export interface BillGenerateRequest {
  customer_id: number;
  bill_period_start: string;
  bill_period_end: string;
  due_date?: string | null;
  remarks?: string | null;
}

export interface CustomerBillItemResponse {
  id: number;
  milk_type_id: number;
  milk_name: string;
  quantity: number;
  unit_price: number;
  amount: number;
}

export interface CustomerBillResponse {
  id: number;
  customer_id: number;
  bill_date: string;
  bill_period_start: string;
  bill_period_end: string;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  status: string;
  due_date: string | null;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  items: CustomerBillItemResponse[];
}

export interface CustomerBillListResponse {
  id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  bill_date: string;
  bill_period_start: string;
  bill_period_end: string;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  status: string;
  due_date: string | null;
  is_active: boolean;
}

export interface OutstandingBalanceResponse {
  customer_id: number;
  customer_code: string;
  customer_name: string;
  total_billed: number;
  total_paid: number;
  balance: number;
  last_bill_date: string | null;
  last_payment_date: string | null;
}

export interface PaymentListParams {
  customer_id?: number;
  payment_mode?: string;
  payment_type?: string;
  from_date?: string;
  to_date?: string;
}

export interface BillListParams {
  customer_id?: number;
  status?: string;
  from_date?: string;
  to_date?: string;
}
