import client from "./client";
import type {
  DeliverySessionCreate,
  DeliverySessionDetailResponse,
  DeliverySessionListResponse,
  DeliverySessionResponse,
  ReconciliationResponse,
  ReconciliationValidationResponse,
  SessionReportResponse,
} from "../types/delivery-session";
import type { DeliveryChecklistResponse } from "../types/delivery";

export interface SessionListParams {
  route_id?: number;
  delivery_date?: string;
  shift?: string;
  status?: string;
  skip?: number;
  limit?: number;
}

export async function createSession(data: DeliverySessionCreate): Promise<DeliverySessionResponse> {
  const response = await client.post<DeliverySessionResponse>("/deliveries/sessions/", data);
  return response.data;
}

export async function listSessions(params?: SessionListParams): Promise<DeliverySessionListResponse> {
  const response = await client.get<DeliverySessionListResponse>("/deliveries/sessions/", { params });
  return response.data;
}

export async function getSession(id: number): Promise<DeliverySessionDetailResponse> {
  const response = await client.get<DeliverySessionDetailResponse>(`/deliveries/sessions/${id}`);
  return response.data;
}

export async function startSession(id: number, totalMilkLoaded: number): Promise<DeliverySessionResponse> {
  const response = await client.post<DeliverySessionResponse>(`/deliveries/sessions/${id}/start`, {
    total_milk_loaded: totalMilkLoaded,
  });
  return response.data;
}

export async function dispatchSession(id: number, totalMilkLoaded: number): Promise<DeliverySessionResponse> {
  const response = await client.post<DeliverySessionResponse>(`/deliveries/sessions/${id}/dispatch`, {
    total_milk_loaded: totalMilkLoaded,
  });
  return response.data;
}

export async function completeSession(id: number): Promise<DeliverySessionResponse> {
  const response = await client.post<DeliverySessionResponse>(`/deliveries/sessions/${id}/complete`);
  return response.data;
}

export async function closeSession(id: number): Promise<DeliverySessionResponse> {
  const response = await client.post<DeliverySessionResponse>(`/deliveries/sessions/${id}/close`);
  return response.data;
}

export async function getSessionChecklist(id: number): Promise<DeliveryChecklistResponse> {
  const response = await client.get<DeliveryChecklistResponse>(`/deliveries/sessions/${id}/checklist`);
  return response.data;
}

export async function getReconciliation(id: number): Promise<ReconciliationResponse> {
  const response = await client.get<ReconciliationResponse>(`/deliveries/sessions/${id}/reconciliation`);
  return response.data;
}

export async function getReconciliationSummary(id: number): Promise<Record<string, unknown>> {
  const response = await client.get<Record<string, unknown>>(`/deliveries/sessions/${id}/reconciliation/summary`);
  return response.data;
}

export async function getReconciliationCustomers(id: number): Promise<Record<string, unknown>> {
  const response = await client.get<Record<string, unknown>>(`/deliveries/sessions/${id}/reconciliation/customers`);
  return response.data;
}

export async function validateReconciliation(id: number): Promise<ReconciliationValidationResponse> {
  const response = await client.post<ReconciliationValidationResponse>(`/deliveries/sessions/${id}/reconciliation/validate`);
  return response.data;
}

export interface SubmitReconciliationParams {
  total_cash_collected: number;
  cash_sales?: Record<string, unknown>[];
  returned_milk: number;
  returned_reasons?: Record<string, unknown>[];
  token_sheets_collected?: Record<string, unknown>[];
  remarks?: string;
}

export async function submitReconciliation(id: number, params: SubmitReconciliationParams): Promise<ReconciliationResponse> {
  const response = await client.post<ReconciliationResponse>(`/deliveries/sessions/${id}/reconciliation/submit`, null, { params });
  return response.data;
}

export interface AddCashSaleParams {
  customer_name: string;
  customer_phone?: string | null;
  milk_type_id: number;
  quantity: number;
  amount: number;
  payment_method?: string;
}

export async function addCashSale(id: number, params: AddCashSaleParams): Promise<Record<string, unknown>> {
  const response = await client.post<Record<string, unknown>>(`/deliveries/sessions/${id}/reconciliation/cash-sales`, null, { params });
  return response.data;
}

export async function removeCashSale(id: number, cashSaleId: number): Promise<Record<string, unknown>> {
  const response = await client.delete<Record<string, unknown>>(`/deliveries/sessions/${id}/reconciliation/cash-sales/${cashSaleId}`);
  return response.data;
}

export async function getSessionReport(id: number): Promise<SessionReportResponse> {
  const response = await client.get<SessionReportResponse>(`/deliveries/sessions/${id}/report`);
  return response.data;
}
