import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/delivery-exceptions";
import type { DeliveryExceptionCreate, DeliveryExceptionUpdate } from "../types/delivery-exception";

export function useDeliveryExceptions() {
  return useQuery({
    queryKey: ["delivery-exceptions"],
    queryFn: api.getDeliveryExceptions,
  });
}

export function useDeliveryException(id: number) {
  return useQuery({
    queryKey: ["delivery-exceptions", id],
    queryFn: () => api.getDeliveryException(id),
    enabled: !!id,
  });
}

export function useCreateDeliveryException() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: DeliveryExceptionCreate) => api.createDeliveryException(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["delivery-exceptions"] });
      toast.success("Delivery exception created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create delivery exception");
    },
  });
}

export function useUpdateDeliveryException() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: DeliveryExceptionUpdate }) => api.updateDeliveryException(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["delivery-exceptions"] });
      toast.success("Delivery exception updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update delivery exception");
    },
  });
}

export function useDeleteDeliveryException() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteDeliveryException(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["delivery-exceptions"] });
      toast.success("Delivery exception deleted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete delivery exception");
    },
  });
}
