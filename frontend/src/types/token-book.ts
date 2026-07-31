import type { TokenIdentitySummaryResponse } from "./token-identity";

export type BookIssueStatus = "WAITING" | "ACTIVE" | "COMPLETED";
export type BookPaymentStatus = "PAID" | "PARTIAL" | "PENDING";
export type TokenPaymentMode = "PREPAID" | "POSTPAID";

export interface TokenBookIssueCreate {
  token_identity_id: number;
  issue_number: number;
  remarks?: string | null;
}

export interface TokenBookIssueUpdate {
  status?: BookIssueStatus;
  current_sheet?: number;
  completion_date?: string | null;
  remarks?: string | null;
}

export interface TokenBookIssueListResponse {
  id: number;
  token_identity_id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  milk_type_name: string;
  token_number: number;
  issue_number: number;
  issue_date: string;
  status: string;
  current_sheet: number;
  is_active: boolean;
}

export interface TokenBookIssueDetailResponse {
  id: number;
  token_identity: TokenIdentitySummaryResponse;
  issue_number: number;
  issue_date: string;
  completion_date: string | null;
  current_sheet: number;
  status: string;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenBookIssueResponse {
  id: number;
  token_identity_id: number;
  issue_number: number;
  issue_date: string;
  completion_date: string | null;
  current_sheet: number;
  status: string;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenBookIssueSummaryResponse {
  id: number;
  token_identity: TokenIdentitySummaryResponse;
  issue_number: number;
  status: string;
}

export interface TokenBookPaymentCreate {
  token_book_issue_id: number;
  payment_mode: TokenPaymentMode;
  book_price: number;
  amount_paid: number;
  remarks?: string | null;
}

export interface TokenBookPaymentUpdate {
  payment_mode?: TokenPaymentMode;
  book_price?: number;
  amount_paid?: number;
  remarks?: string | null;
}

export interface TokenBookPaymentListResponse {
  id: number;
  token_book_issue_id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  payment_mode: string;
  payment_status: string;
  book_price: number;
  amount_paid: number;
  balance_amount: number;
  payment_date: string;
  is_active: boolean;
}

export interface TokenBookPaymentDetailResponse {
  id: number;
  token_book_issue: TokenBookIssueSummaryResponse;
  payment_mode: string;
  payment_status: string;
  book_price: number;
  amount_paid: number;
  balance_amount: number;
  payment_date: string;
  collected_by: number | null;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenBookPaymentResponse {
  id: number;
  token_book_issue_id: number;
  payment_mode: string;
  payment_status: string;
  book_price: number;
  amount_paid: number;
  balance_amount: number;
  payment_date: string;
  collected_by: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
