export interface MilkTypeBase {
  milk_name: string;
  volume_ml: number;
  unit_price: number;
  description?: string | null;
}

export interface MilkTypeCreate extends MilkTypeBase {}

export interface MilkTypeUpdate extends MilkTypeBase {}

export interface MilkTypeResponse extends MilkTypeBase {
  id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MilkTypeSummaryResponse {
  id: number;
  milk_name: string;
  volume_ml: number;
  unit_price: number;
}
