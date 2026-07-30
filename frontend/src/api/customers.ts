import client from "./client";
import type { CustomerCreate, CustomerUpdate, CustomerResponse } from "../types/customer";

export async function getCustomers(): Promise<CustomerResponse[]> {
  const response = await client.get<CustomerResponse[]>("/customers");
  return response.data;
}

export async function getCustomer(id: number): Promise<CustomerResponse> {
  const response = await client.get<CustomerResponse>(`/customers/${id}`);
  return response.data;
}

export async function createCustomer(data: CustomerCreate): Promise<CustomerResponse> {
  const response = await client.post<CustomerResponse>("/customers", data);
  return response.data;
}

export async function updateCustomer(id: number, data: CustomerUpdate): Promise<CustomerResponse> {
  const response = await client.put<CustomerResponse>(`/customers/${id}`, data);
  return response.data;
}

export async function deleteCustomer(id: number): Promise<CustomerResponse> {
  const response = await client.delete<CustomerResponse>(`/customers/${id}`);
  return response.data;
}
