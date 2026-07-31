import client from "./client";
import type {
  SubscriptionCreate,
  SubscriptionDetailResponse,
  SubscriptionListResponse,
  SubscriptionResponse,
  SubscriptionUpdate,
} from "../types/subscription";

export async function getSubscriptions() {
  const response = await client.get<SubscriptionListResponse[]>("/subscriptions");
  return response.data;
}

export async function getSubscription(id: number) {
  const response = await client.get<SubscriptionDetailResponse>(`/subscriptions/${id}`);
  return response.data;
}

export async function getSubscriptionsByCustomer(customerId: number) {
  const response = await client.get<SubscriptionListResponse[]>(`/subscriptions/customer/${customerId}`);
  return response.data;
}

export async function getSubscriptionsByMilkType(milkTypeId: number) {
  const response = await client.get<SubscriptionListResponse[]>(`/subscriptions/milk-type/${milkTypeId}`);
  return response.data;
}

export async function createSubscription(data: SubscriptionCreate) {
  const response = await client.post<SubscriptionResponse>("/subscriptions", data);
  return response.data;
}

export async function updateSubscription(id: number, data: SubscriptionUpdate) {
  const response = await client.put<SubscriptionResponse>(`/subscriptions/${id}`, data);
  return response.data;
}

export async function deleteSubscription(id: number) {
  await client.delete(`/subscriptions/${id}`);
}
