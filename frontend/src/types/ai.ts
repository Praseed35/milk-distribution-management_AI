import type { ReportPreset } from "./reports";

export interface DataRange {
  from: string;
  to: string;
}

export interface ForecastDay {
  date: string;
  predicted_quantity: number;
  low: number;
  high: number;
  actual_quantity: number | null;
  is_sufficient_history: boolean;
}

export interface DemandForecast {
  route_id: number | null;
  milk_type_id: number | null;
  horizon_days: number;
  date_from: string;
  date_to: string;
  method: string;
  is_sufficient_history: boolean;
  message: string | null;
  total_expected: number | null;
  low_range: number | null;
  high_range: number | null;
  items: ForecastDay[];
}

export type AnomalySeverity = "HIGH" | "MEDIUM" | "LOW";

export interface AnomalyItem {
  type: string;
  severity: AnomalySeverity;
  title: string;
  description: string;
  entity_type: "session" | "route" | "customer" | "payment";
  entity_id: number;
  entity_name: string;
  metric: string;
  expected: number;
  actual: number;
  deviation: number;
  occurred_on: string;
  suggested_action: string;
}

export interface AnomalyReport {
  generated_at: string;
  count: number;
  items: AnomalyItem[];
}

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

export interface ChurnFactor {
  factor: string;
  weight: number;
  contribution: number;
}

export interface ChurnRiskItem {
  customer_id: number;
  customer_code: string;
  customer_name: string;
  route_name: string;
  risk_score: number;
  risk_level: RiskLevel;
  factors: ChurnFactor[];
  suggested_action: string;
}

export interface ChurnRiskReport {
  generated_at: string;
  count: number;
  items: ChurnRiskItem[];
}

export interface AIInsightsResponse {
  generated_at: string;
  stats_only: boolean;
  data_range: DataRange;
  narrative: string | null;
  operational: Record<string, unknown>;
  forecast: DemandForecast;
  anomalies: AnomalyReport;
  churn_risk: ChurnRiskReport;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  reply: string;
  data_range: DataRange;
  sources: string[];
  stats_only: boolean;
}

export interface ForecastParams {
  route_id?: number;
  milk_type_id?: number;
  horizon_days?: number;
  refresh?: boolean;
}

export interface AnomalyParams {
  route_id?: number;
  days_back?: number;
  refresh?: boolean;
}

export interface ChurnRiskParams {
  route_id?: number;
  limit?: number;
  refresh?: boolean;
}

export interface InsightsParams {
  preset?: ReportPreset;
  from_date?: string;
  to_date?: string;
  refresh?: boolean;
}
