import client from "./client";
import type { DeliverySessionResponse } from "../types/delivery-session";
import type {
  CustomerTokenStatusResponse,
  DailyDeliveryEditRequest,
  DailyDeliveryEditResponse,
  DailyDeliveryResponse,
  DailyDeliveryUpdate,
  DeliveryWarningsResponse,
  SessionDeliveriesResponse,
  SessionEditResponse,
  TokenRegistrationRequest,
  TokenRegistrationResponse,
  TokenValidationRequest,
  TokenValidationResponse,
  UnplannedDeliveryCreate,
} from "../types/delivery";

export async function updateDelivery(id: number, data: DailyDeliveryUpdate): Promise<DailyDeliveryResponse> {
  const response = await client.put<DailyDeliveryResponse>(`/deliveries/${id}`, data);
  return response.data;
}

export async function addUnplannedDelivery(data: UnplannedDeliveryCreate): Promise<DailyDeliveryResponse> {
  const response = await client.post<DailyDeliveryResponse>("/deliveries/unplanned", data);
  return response.data;
}

export async function registerToken(id: number, data: TokenRegistrationRequest): Promise<TokenRegistrationResponse> {
  const response = await client.post<TokenRegistrationResponse>(`/deliveries/${id}/register-token`, data);
  return response.data;
}

export async function validateToken(data: TokenValidationRequest): Promise<TokenValidationResponse> {
  const response = await client.post<TokenValidationResponse>("/deliveries/validate-token", data);
  return response.data;
}

export async function getDeliveryWarnings(id: number): Promise<DeliveryWarningsResponse> {
  const response = await client.get<DeliveryWarningsResponse>(`/deliveries/${id}/warnings`);
  return response.data;
}

export interface SessionDeliveriesParams {
  status?: string;
  skip?: number;
  limit?: number;
}

export async function getSessionDeliveries(sessionId: number, params?: SessionDeliveriesParams): Promise<SessionDeliveriesResponse> {
  const response = await client.get<SessionDeliveriesResponse>(`/deliveries/session/${sessionId}`, { params });
  return response.data;
}

export async function getCustomerTokenStatus(customerId: number): Promise<CustomerTokenStatusResponse> {
  const response = await client.get<CustomerTokenStatusResponse>(`/deliveries/customer/${customerId}/token-status`);
  return response.data;
}

export async function reopenSession(sessionId: number, data: { reason: string }): Promise<DeliverySessionResponse> {
  const response = await client.post<DeliverySessionResponse>(`/deliveries/session/${sessionId}/reopen`, data);
  return response.data;
}

export async function editDelivery(id: number, data: DailyDeliveryEditRequest): Promise<DailyDeliveryEditResponse> {
  const response = await client.put<DailyDeliveryEditResponse>(`/deliveries/${id}/edit`, data);
  return response.data;
}

export async function getEditHistory(sessionId: number): Promise<SessionEditResponse[]> {
  const response = await client.get<SessionEditResponse[]>(`/deliveries/session/${sessionId}/edit-history`);
  return response.data;
}
