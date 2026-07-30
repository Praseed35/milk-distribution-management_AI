export interface CustomerBase {
  customer_name: string;
  primary_phone: string;
  alternate_phone?: string | null;
  address?: string | null;
  route_id: number;
  remarks?: string | null;
}

export interface CustomerCreate extends CustomerBase {}

export interface CustomerUpdate extends CustomerBase {}

export interface CustomerResponse extends CustomerBase {
  id: number;
  customer_code: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CustomerSummaryResponse {
  id: number;
  customer_code: string;
  customer_name: string;
  primary_phone: string;
}
