import client from "./client";
import type { RouteCreate, RouteUpdate, RouteResponse } from "../types/route";

export async function getRoutes(): Promise<RouteResponse[]> {
  const response = await client.get<RouteResponse[]>("/routes");
  return response.data;
}

export async function getRoute(id: number): Promise<RouteResponse> {
  const response = await client.get<RouteResponse>(`/routes/${id}`);
  return response.data;
}

export async function createRoute(data: RouteCreate): Promise<RouteResponse> {
  const response = await client.post<RouteResponse>("/routes", data);
  return response.data;
}

export async function updateRoute(id: number, data: RouteUpdate): Promise<RouteResponse> {
  const response = await client.put<RouteResponse>(`/routes/${id}`, data);
  return response.data;
}

export async function deleteRoute(id: number): Promise<RouteResponse> {
  const response = await client.delete<RouteResponse>(`/routes/${id}`);
  return response.data;
}
