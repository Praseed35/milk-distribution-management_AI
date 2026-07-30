import client from "./client";
import type { MilkTypeCreate, MilkTypeUpdate, MilkTypeResponse } from "../types/milk-type";

export async function getMilkTypes(): Promise<MilkTypeResponse[]> {
  const response = await client.get<MilkTypeResponse[]>("/milk-types");
  return response.data;
}

export async function getMilkType(id: number): Promise<MilkTypeResponse> {
  const response = await client.get<MilkTypeResponse>(`/milk-types/${id}`);
  return response.data;
}

export async function createMilkType(data: MilkTypeCreate): Promise<MilkTypeResponse> {
  const response = await client.post<MilkTypeResponse>("/milk-types", data);
  return response.data;
}

export async function updateMilkType(id: number, data: MilkTypeUpdate): Promise<MilkTypeResponse> {
  const response = await client.put<MilkTypeResponse>(`/milk-types/${id}`, data);
  return response.data;
}

export async function deleteMilkType(id: number): Promise<MilkTypeResponse> {
  const response = await client.delete<MilkTypeResponse>(`/milk-types/${id}`);
  return response.data;
}
