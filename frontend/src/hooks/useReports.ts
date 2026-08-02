import { useQuery } from "@tanstack/react-query";
import * as api from "../api/reports";
import type {
  CollectionEfficiencyParams,
  ConsumptionParams,
  RevenueParams,
  RouteDeliveryParams,
  TokenUtilizationParams,
} from "../types/reports";

export function useDashboard(refresh?: boolean) {
  return useQuery({
    queryKey: ["reports", "dashboard", refresh],
    queryFn: () => api.getDashboard(refresh),
  });
}

export function useRouteDelivery(params?: RouteDeliveryParams) {
  return useQuery({
    queryKey: ["reports", "route-delivery", params],
    queryFn: () => api.getRouteDelivery(params),
  });
}

export function useRevenue(params?: RevenueParams) {
  return useQuery({
    queryKey: ["reports", "revenue", params],
    queryFn: () => api.getRevenue(params),
  });
}

export function useConsumption(customerId: number | null, params?: ConsumptionParams) {
  return useQuery({
    queryKey: ["reports", "consumption", customerId, params],
    queryFn: () => api.getConsumption(customerId as number, params),
    enabled: !!customerId,
  });
}

export function useTokenUtilization(params?: TokenUtilizationParams) {
  return useQuery({
    queryKey: ["reports", "token-utilization", params],
    queryFn: () => api.getTokenUtilization(params),
  });
}

export function useCollectionEfficiency(params?: CollectionEfficiencyParams) {
  return useQuery({
    queryKey: ["reports", "collection-efficiency", params],
    queryFn: () => api.getCollectionEfficiency(params),
  });
}
