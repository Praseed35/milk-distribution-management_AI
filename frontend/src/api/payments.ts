import client from "./client";
import type {
  BillGenerateRequest,
  BillListParams,
  CustomerBillListResponse,
  CustomerBillResponse,
  CustomerPaymentCreate,
  CustomerPaymentListResponse,
  CustomerPaymentResponse,
  OutstandingBalanceResponse,
  PaymentListParams,
} from "../types/payment";

export async function listPayments(params?: PaymentListParams): Promise<CustomerPaymentListResponse[]> {
  const response = await client.get<CustomerPaymentListResponse[]>("/payments/", { params });
  return response.data;
}

export async function createPayment(data: CustomerPaymentCreate): Promise<CustomerPaymentResponse> {
  const response = await client.post<CustomerPaymentResponse>("/payments/", data);
  return response.data;
}

export async function generateBill(data: BillGenerateRequest): Promise<CustomerBillResponse> {
  const response = await client.post<CustomerBillResponse>("/payments/bills/generate", data);
  return response.data;
}

export async function listBills(params?: BillListParams): Promise<CustomerBillListResponse[]> {
  const response = await client.get<CustomerBillListResponse[]>("/payments/bills/", { params });
  return response.data;
}

export async function getBill(id: number): Promise<CustomerBillResponse> {
  const response = await client.get<CustomerBillResponse>(`/payments/bills/${id}`);
  return response.data;
}

export async function updateBillStatus(id: number, status: string): Promise<CustomerBillResponse> {
  const response = await client.put<CustomerBillResponse>(`/payments/bills/${id}/status`, { status });
  return response.data;
}

export async function getOutstanding(customerId: number): Promise<OutstandingBalanceResponse> {
  const response = await client.get<OutstandingBalanceResponse>(`/payments/outstanding/${customerId}`);
  return response.data;
}
