import client from "./client";
import type { EmployeeCreate, EmployeeUpdate, EmployeeCredentialsUpdate, EmployeeResponse } from "../types/employee";

export async function getEmployees(): Promise<EmployeeResponse[]> {
  const response = await client.get<EmployeeResponse[]>("/employees");
  return response.data;
}

export async function getEmployee(id: number): Promise<EmployeeResponse> {
  const response = await client.get<EmployeeResponse>(`/employees/${id}`);
  return response.data;
}

export async function createEmployee(data: EmployeeCreate): Promise<EmployeeResponse> {
  const response = await client.post<EmployeeResponse>("/employees", data);
  return response.data;
}

export async function updateEmployee(id: number, data: EmployeeUpdate): Promise<EmployeeResponse> {
  const response = await client.put<EmployeeResponse>(`/employees/${id}`, data);
  return response.data;
}

export async function updateEmployeeCredentials(id: number, data: EmployeeCredentialsUpdate): Promise<EmployeeResponse> {
  const response = await client.put<EmployeeResponse>(`/employees/${id}/credentials`, data);
  return response.data;
}

export async function deleteEmployee(id: number): Promise<EmployeeResponse> {
  const response = await client.delete<EmployeeResponse>(`/employees/${id}`);
  return response.data;
}
