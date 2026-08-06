import { useQuery, useMutation } from "@tanstack/react-query";
import * as api from "../api/ai";
import type {
  AnomalyParams,
  ChurnRiskParams,
  ChatRequest,
  ChatResponse,
  ForecastParams,
  InsightsParams,
} from "../types/ai";

export function useForecast(params?: ForecastParams) {
  return useQuery({
    queryKey: ["ai", "forecast", params],
    queryFn: () => api.getForecast(params),
  });
}

export function useAnomalies(params?: AnomalyParams) {
  return useQuery({
    queryKey: ["ai", "anomalies", params],
    queryFn: () => api.getAnomalies(params),
  });
}

export function useChurnRisk(params?: ChurnRiskParams) {
  return useQuery({
    queryKey: ["ai", "churn-risk", params],
    queryFn: () => api.getChurnRisk(params),
  });
}

export function useInsights(params?: InsightsParams) {
  return useQuery({
    queryKey: ["ai", "insights", params],
    queryFn: () => api.getInsights(params),
  });
}

export function useChat() {
  return useMutation({
    mutationFn: (body: ChatRequest): Promise<ChatResponse> => api.sendChatMessage(body),
  });
}
