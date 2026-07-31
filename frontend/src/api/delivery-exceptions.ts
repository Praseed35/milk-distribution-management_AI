import client from "./client";
import type {
  DeliveryExceptionCreate,
  DeliveryExceptionDetailResponse,
  DeliveryExceptionListResponse,
  DeliveryExceptionResponse,
  DeliveryExceptionUpdate,
} from "../types/delivery-exception";

export async function getDeliveryExceptions() {
  const response = await client.get<DeliveryExceptionListResponse[]>("/delivery-exceptions");
  return response.data;
}

export async function getDeliveryException(id: number) {
  const response = await client.get<DeliveryExceptionDetailResponse>(`/delivery-exceptions/${id}`);
  return response.data;
}

export async function getDeliveryExceptionsBySubscription(subscriptionId: number) {
  const response = await client.get<DeliveryExceptionListResponse[]>(`/delivery-exceptions/subscription/${subscriptionId}`);
  return response.data;
}

export async function createDeliveryException(data: DeliveryExceptionCreate) {
  const response = await client.post<DeliveryExceptionResponse>("/delivery-exceptions", data);
  return response.data;
}

export async function updateDeliveryException(id: number, data: DeliveryExceptionUpdate) {
  const response = await client.put<DeliveryExceptionResponse>(`/delivery-exceptions/${id}`, data);
  return response.data;
}

export async function deleteDeliveryException(id: number) {
  await client.delete(`/delivery-exceptions/${id}`);
}
