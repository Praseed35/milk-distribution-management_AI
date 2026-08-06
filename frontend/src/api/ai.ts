import client from "./client";
import type {
  AIInsightsResponse,
  AnomalyParams,
  AnomalyReport,
  ChatRequest,
  ChatResponse,
  ChurnRiskParams,
  ChurnRiskReport,
  DemandForecast,
  ForecastParams,
  InsightsParams,
} from "../types/ai";

export async function getForecast(params?: ForecastParams): Promise<DemandForecast> {
  const response = await client.get<DemandForecast>("/ai/forecast", { params });
  return response.data;
}

export async function getAnomalies(params?: AnomalyParams): Promise<AnomalyReport> {
  const response = await client.get<AnomalyReport>("/ai/anomalies", { params });
  return response.data;
}

export async function getChurnRisk(params?: ChurnRiskParams): Promise<ChurnRiskReport> {
  const response = await client.get<ChurnRiskReport>("/ai/churn-risk", { params });
  return response.data;
}

export async function getInsights(params?: InsightsParams): Promise<AIInsightsResponse> {
  const response = await client.get<AIInsightsResponse>("/ai/insights", { params });
  return response.data;
}

export async function sendChatMessage(body: ChatRequest): Promise<ChatResponse> {
  const response = await client.post<ChatResponse>("/ai/chat", body);
  return response.data;
}
