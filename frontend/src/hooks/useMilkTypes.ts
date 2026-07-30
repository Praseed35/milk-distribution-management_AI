import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/milk-types";
import type { MilkTypeCreate, MilkTypeUpdate } from "../types/milk-type";

export function useMilkTypes() {
  return useQuery({
    queryKey: ["milk-types"],
    queryFn: api.getMilkTypes,
  });
}

export function useMilkType(id: number) {
  return useQuery({
    queryKey: ["milk-types", id],
    queryFn: () => api.getMilkType(id),
    enabled: !!id,
  });
}

export function useCreateMilkType() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: MilkTypeCreate) => api.createMilkType(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["milk-types"] });
      toast.success("Milk type created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create milk type");
    },
  });
}

export function useUpdateMilkType() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: MilkTypeUpdate }) => api.updateMilkType(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["milk-types"] });
      toast.success("Milk type updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update milk type");
    },
  });
}

export function useDeleteMilkType() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteMilkType(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["milk-types"] });
      toast.success("Milk type deleted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete milk type");
    },
  });
}
