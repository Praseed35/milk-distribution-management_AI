import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/routes";
import type { RouteCreate, RouteUpdate } from "../types/route";

export function useRoutes() {
  return useQuery({
    queryKey: ["routes"],
    queryFn: api.getRoutes,
  });
}

export function useRoute(id: number) {
  return useQuery({
    queryKey: ["routes", id],
    queryFn: () => api.getRoute(id),
    enabled: !!id,
  });
}

export function useCreateRoute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: RouteCreate) => api.createRoute(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["routes"] });
      toast.success("Route created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create route");
    },
  });
}

export function useUpdateRoute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: RouteUpdate }) => api.updateRoute(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["routes"] });
      toast.success("Route updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update route");
    },
  });
}

export function useDeleteRoute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteRoute(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["routes"] });
      toast.success("Route deleted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete route");
    },
  });
}
