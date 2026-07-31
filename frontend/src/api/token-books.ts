import client from "./client";
import type {
  TokenIdentityCreate,
  TokenIdentityDetailResponse,
  TokenIdentityListResponse,
  TokenIdentityResponse,
  TokenIdentityUpdate,
} from "../types/token-identity";
import type {
  TokenBookIssueCreate,
  TokenBookIssueDetailResponse,
  TokenBookIssueListResponse,
  TokenBookIssueResponse,
  TokenBookIssueUpdate,
} from "../types/token-book";
import type {
  TokenBookPaymentCreate,
  TokenBookPaymentDetailResponse,
  TokenBookPaymentListResponse,
  TokenBookPaymentResponse,
  TokenBookPaymentUpdate,
} from "../types/token-book";

export async function getTokenIdentities() {
  const response = await client.get<TokenIdentityListResponse[]>("/token-books/identities");
  return response.data;
}

export async function getTokenIdentity(id: number) {
  const response = await client.get<TokenIdentityDetailResponse>(`/token-books/identities/${id}`);
  return response.data;
}

export async function createTokenIdentity(data: TokenIdentityCreate) {
  const response = await client.post<TokenIdentityResponse>("/token-books/identities", data);
  return response.data;
}

export async function updateTokenIdentity(id: number, data: TokenIdentityUpdate) {
  const response = await client.put<TokenIdentityResponse>(`/token-books/identities/${id}`, data);
  return response.data;
}

export async function deleteTokenIdentity(id: number) {
  await client.delete(`/token-books/identities/${id}`);
}

export async function getTokenBookIssues() {
  const response = await client.get<TokenBookIssueListResponse[]>("/token-books/issues");
  return response.data;
}

export async function getTokenBookIssue(id: number) {
  const response = await client.get<TokenBookIssueDetailResponse>(`/token-books/issues/${id}`);
  return response.data;
}

export async function createTokenBookIssue(data: TokenBookIssueCreate) {
  const response = await client.post<TokenBookIssueResponse>("/token-books/issues", data);
  return response.data;
}

export async function updateTokenBookIssue(id: number, data: TokenBookIssueUpdate) {
  const response = await client.put<TokenBookIssueResponse>(`/token-books/issues/${id}`, data);
  return response.data;
}

export async function deleteTokenBookIssue(id: number) {
  await client.delete(`/token-books/issues/${id}`);
}

export async function getTokenBookPayments() {
  const response = await client.get<TokenBookPaymentListResponse[]>("/token-books/payments");
  return response.data;
}

export async function getTokenBookPayment(id: number) {
  const response = await client.get<TokenBookPaymentDetailResponse>(`/token-books/payments/${id}`);
  return response.data;
}

export async function createTokenBookPayment(data: TokenBookPaymentCreate) {
  const response = await client.post<TokenBookPaymentResponse>("/token-books/payments", data);
  return response.data;
}

export async function updateTokenBookPayment(id: number, data: TokenBookPaymentUpdate) {
  const response = await client.put<TokenBookPaymentResponse>(`/token-books/payments/${id}`, data);
  return response.data;
}

export async function deleteTokenBookPayment(id: number) {
  await client.delete(`/token-books/payments/${id}`);
}
