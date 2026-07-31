import type { CustomerSummaryResponse } from "./customer";

export type ExceptionType = "VACATION" | "NO_MILK" | "HOLIDAY";

export interface SubscriptionSummaryResponse {
  id: number;
  customer: CustomerSummaryResponse;
  morning_quantity: number;
  evening_quantity: number;
}

export interface DeliveryExceptionCreate {
  subscription_id: number;
  exception_type: string;
  shift?: string | null;
  start_date: string;
  end_date?: string | null;
  reason?: string | null;
}

export interface DeliveryExceptionUpdate {
  exception_type?: string;
  shift?: string | null;
  start_date?: string;
  end_date?: string | null;
  reason?: string | null;
  status?: string;
}

export interface DeliveryExceptionListResponse {
  id: number;
  subscription_id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  route_name: string;
  exception_type: string;
  shift: string | null;
  start_date: string;
  end_date: string | null;
  status: string;
  is_active: boolean;
}

export interface DeliveryExceptionResponse {
  id: number;
  subscription_id: number;
  exception_type: string;
  shift: string | null;
  start_date: string;
  end_date: string | null;
  reason: string | null;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DeliveryExceptionDetailResponse {
  id: number;
  subscription: SubscriptionSummaryResponse;
  exception_type: string;
  shift: string | null;
  start_date: string;
  end_date: string | null;
  reason: string | null;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
