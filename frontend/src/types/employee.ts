export interface EmployeeBase {
  name: string;
  phone: string;
  address?: string | null;
  role: string;
  route_id?: number | null;
}

export interface EmployeeCreate extends EmployeeBase {
  username?: string | null;
  password?: string | null;
  confirm_password?: string | null;
}

export interface EmployeeUpdate {
  name?: string | null;
  phone?: string | null;
  address?: string | null;
  role?: string | null;
  route_id?: number | null;
}

export interface EmployeeCredentialsUpdate {
  username?: string | null;
  password?: string | null;
  confirm_password?: string | null;
}

export interface EmployeeResponse extends EmployeeBase {
  id: number;
  employee_code: string;
  is_active: boolean;
  username?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmployeeSummaryResponse {
  id: number;
  employee_code: string;
  name: string;
  phone: string;
  role: string;
}
