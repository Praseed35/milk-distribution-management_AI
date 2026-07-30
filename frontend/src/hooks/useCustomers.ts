import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/customers";
import type { CustomerCreate, CustomerUpdate } from "../types/customer";

export function useCustomers() {
  return useQuery({
    queryKey: ["customers"],
    queryFn: api.getCustomers,
  });
}

export function useCustomer(id: number) {
  return useQuery({
    queryKey: ["customers", id],
    queryFn: () => api.getCustomer(id),
    enabled: !!id,
  });
}

export function useCreateCustomer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CustomerCreate) => api.createCustomer(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["customers"] });
      toast.success("Customer created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create customer");
    },
  });
}

export function useUpdateCustomer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CustomerUpdate }) => api.updateCustomer(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["customers"] });
      toast.success("Customer updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update customer");
    },
  });
}

export function useDeleteCustomer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteCustomer(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["customers"] });
      toast.success("Customer deleted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete customer");
    },
  });
}
