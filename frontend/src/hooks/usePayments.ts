import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/payments";
import type { BillGenerateRequest, BillListParams, CustomerPaymentCreate, PaymentListParams } from "../types/payment";

export function usePayments(params?: PaymentListParams) {
  return useQuery({
    queryKey: ["payments", params],
    queryFn: () => api.listPayments(params),
  });
}

export function useBills(params?: BillListParams) {
  return useQuery({
    queryKey: ["bills", params],
    queryFn: () => api.listBills(params),
  });
}

export function useBill(id: number) {
  return useQuery({
    queryKey: ["bills", id],
    queryFn: () => api.getBill(id),
    enabled: !!id,
  });
}

export function useOutstanding(customerId: number) {
  return useQuery({
    queryKey: ["outstanding", customerId],
    queryFn: () => api.getOutstanding(customerId),
    enabled: !!customerId,
  });
}

export function useCreatePayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CustomerPaymentCreate) => api.createPayment(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["payments"] });
      qc.invalidateQueries({ queryKey: ["bills"] });
      qc.invalidateQueries({ queryKey: ["outstanding"] });
      toast.success("Payment recorded");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to record payment");
    },
  });
}

export function useGenerateBill() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: BillGenerateRequest) => api.generateBill(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bills"] });
      toast.success("Bill generated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to generate bill");
    },
  });
}

export function useUpdateBillStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => api.updateBillStatus(id, status),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ["bills"] });
      qc.invalidateQueries({ queryKey: ["bills", variables.id] });
      qc.invalidateQueries({ queryKey: ["outstanding"] });
      toast.success("Bill status updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update bill status");
    },
  });
}
