export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  role: UserRole;
}

export type UserRole = "OWNER" | "ADMIN" | "CHECKER" | "DELIVERY_PARTNER" | "EMPLOYEE";

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}
