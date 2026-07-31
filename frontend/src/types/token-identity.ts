import type { CustomerSummaryResponse } from "./customer";
import type { MilkTypeSummaryResponse } from "./milk-type";

export interface TokenIdentityCreate {
  customer_id: number;
  milk_type_id: number;
  token_number: number;
}

export interface TokenIdentityUpdate {
  token_number?: number;
}

export interface TokenIdentityListResponse {
  id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  milk_type_id: number;
  milk_type_name: string;
  milk_type_volume: number;
  token_number: number;
  is_active: boolean;
}

export interface TokenIdentityDetailResponse {
  id: number;
  customer: CustomerSummaryResponse;
  milk_type: MilkTypeSummaryResponse;
  token_number: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenIdentityResponse {
  id: number;
  customer_id: number;
  milk_type_id: number;
  token_number: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenIdentitySummaryResponse {
  id: number;
  customer: CustomerSummaryResponse;
  milk_type: MilkTypeSummaryResponse;
  token_number: number;
}
