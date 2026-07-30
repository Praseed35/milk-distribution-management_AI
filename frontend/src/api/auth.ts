import client from "./client";
import type { LoginRequest, LoginResponse, User, ChangePasswordRequest } from "../types/auth";

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await client.post<LoginResponse>("/auth/login", data);
  return response.data;
}

export async function getMe(): Promise<User> {
  const response = await client.get<User>("/auth/me");
  return response.data;
}

export async function changePassword(data: ChangePasswordRequest): Promise<void> {
  await client.put("/auth/change-password", data);
}
