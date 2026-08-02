import client from "./client";
import type {
  CollectionEfficiencyParams,
  ConsumptionParams,
  CustomerCollectionItem,
  CustomerConsumptionReport,
  OperationalDashboard,
  ReportEnvelope,
  RevenueParams,
  RevenueReport,
  RouteDeliveryItem,
  RouteDeliveryParams,
  TokenUtilizationItem,
  TokenUtilizationParams,
} from "../types/reports";

export async function getDashboard(refresh?: boolean): Promise<OperationalDashboard> {
  const response = await client.get<OperationalDashboard>("/reports/dashboard", {
    params: refresh ? { refresh: true } : undefined,
  });
  return response.data;
}

export async function getRouteDelivery(params?: RouteDeliveryParams): Promise<ReportEnvelope<RouteDeliveryItem>> {
  const response = await client.get<ReportEnvelope<RouteDeliveryItem>>("/reports/route-delivery", { params });
  return response.data;
}

export async function getRevenue(params?: RevenueParams): Promise<RevenueReport> {
  const response = await client.get<RevenueReport>("/reports/revenue", { params });
  return response.data;
}

export async function getConsumption(
  customerId: number,
  params?: ConsumptionParams
): Promise<CustomerConsumptionReport> {
  const response = await client.get<CustomerConsumptionReport>(`/reports/customer/${customerId}/consumption`, {
    params,
  });
  return response.data;
}

export async function getTokenUtilization(
  params?: TokenUtilizationParams
): Promise<ReportEnvelope<TokenUtilizationItem>> {
  const response = await client.get<ReportEnvelope<TokenUtilizationItem>>("/reports/token-utilization", { params });
  return response.data;
}

export async function getCollectionEfficiency(
  params?: CollectionEfficiencyParams
): Promise<ReportEnvelope<CustomerCollectionItem>> {
  const response = await client.get<ReportEnvelope<CustomerCollectionItem>>("/reports/collection-efficiency", {
    params,
  });
  return response.data;
}

export async function downloadReportCsv(
  path: string,
  params: Record<string, unknown>,
  filename: string
): Promise<void> {
  const response = await client.get(path, {
    params: { ...params, format: "csv" },
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(response.data as Blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  window.URL.revokeObjectURL(url);
}
