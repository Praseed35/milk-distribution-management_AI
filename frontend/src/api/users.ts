import client from "./client";

export interface UserCreateRequest {
  username: string;
  password: string;
  role: string;
}

export interface UserResponse {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export async function getUsers(): Promise<UserResponse[]> {
  const response = await client.get<UserResponse[]>("/users");
  return response.data;
}

export async function createUser(data: UserCreateRequest): Promise<UserResponse> {
  const response = await client.post<UserResponse>("/users", data);
  return response.data;
}
