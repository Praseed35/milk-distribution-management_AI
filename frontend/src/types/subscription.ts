import type { CustomerSummaryResponse } from "./customer";
import type { MilkTypeSummaryResponse } from "./milk-type";

export interface SubscriptionCreate {
  customer_id: number;
  milk_type_id: number;
  morning_quantity: number;
  evening_quantity: number;
  status?: string;
  remarks?: string | null;
}

export interface SubscriptionUpdate {
  morning_quantity?: number;
  evening_quantity?: number;
  status?: string;
  remarks?: string | null;
}

export interface SubscriptionListResponse {
  id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  route_name: string;
  milk_type_name: string;
  milk_type_volume: number;
  morning_quantity: number;
  evening_quantity: number;
  status: string;
  is_active: boolean;
}

export interface SubscriptionDetailResponse {
  id: number;
  customer: CustomerSummaryResponse;
  milk_type: MilkTypeSummaryResponse;
  morning_quantity: number;
  evening_quantity: number;
  status: string;
  start_date: string;
  end_date: string | null;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionResponse {
  id: number;
  customer_id: number;
  milk_type_id: number;
  morning_quantity: number;
  evening_quantity: number;
  status: string;
  remarks: string | null;
  start_date: string;
  end_date: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
