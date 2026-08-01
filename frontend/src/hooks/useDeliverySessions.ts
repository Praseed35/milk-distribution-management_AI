import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/delivery-sessions";
import type { DeliverySessionCreate } from "../types/delivery-session";
import type { AddCashSaleParams, SessionListParams, SubmitReconciliationParams } from "../api/delivery-sessions";

export function useDeliverySessions(params?: SessionListParams) {
  return useQuery({
    queryKey: ["delivery-sessions", params],
    queryFn: () => api.listSessions(params),
  });
}

export function useDeliverySession(id: number) {
  return useQuery({
    queryKey: ["session-detail", id],
    queryFn: () => api.getSession(id),
    enabled: !!id,
  });
}

export function useSessionChecklist(id: number) {
  return useQuery({
    queryKey: ["session-checklist", id],
    queryFn: () => api.getSessionChecklist(id),
    enabled: !!id,
  });
}

export function useReconciliation(id: number) {
  return useQuery({
    queryKey: ["reconciliation", id],
    queryFn: () => api.getReconciliation(id),
    enabled: !!id,
  });
}

export function useReconciliationSummary(id: number) {
  return useQuery({
    queryKey: ["reconciliation-summary", id],
    queryFn: () => api.getReconciliationSummary(id),
    enabled: !!id,
  });
}

export function useReconciliationCustomers(id: number) {
  return useQuery({
    queryKey: ["reconciliation-customers", id],
    queryFn: () => api.getReconciliationCustomers(id),
    enabled: !!id,
  });
}

export function useSessionReport(id: number) {
  return useQuery({
    queryKey: ["session-report", id],
    queryFn: () => api.getSessionReport(id),
    enabled: !!id,
  });
}

export function useValidateReconciliation() {
  return useMutation({
    mutationFn: (id: number) => api.validateReconciliation(id),
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Validation failed");
    },
  });
}

function invalidateSessionQueries(qc: any, id?: number) {
  qc.invalidateQueries({ queryKey: ["delivery-sessions"] });
  if (id) {
    qc.invalidateQueries({ queryKey: ["session-detail", id] });
    qc.invalidateQueries({ queryKey: ["session-checklist", id] });
    qc.invalidateQueries({ queryKey: ["session-deliveries", id] });
    qc.invalidateQueries({ queryKey: ["session-edit-history", id] });
    qc.invalidateQueries({ queryKey: ["reconciliation", id] });
    qc.invalidateQueries({ queryKey: ["reconciliation-summary", id] });
    qc.invalidateQueries({ queryKey: ["reconciliation-customers", id] });
    qc.invalidateQueries({ queryKey: ["session-report", id] });
  }
}

export function useCreateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: DeliverySessionCreate) => api.createSession(data),
    onSuccess: (session) => {
      invalidateSessionQueries(qc, session.id);
      toast.success("Session created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create session");
    },
  });
}

export function useStartSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, total }: { id: number; total: number }) => api.startSession(id, total),
    onSuccess: (session) => {
      invalidateSessionQueries(qc, session.id);
      toast.success("Dispatch recorded");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to start session");
    },
  });
}

export function useCompleteSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.completeSession(id),
    onSuccess: (session) => {
      invalidateSessionQueries(qc, session.id);
      toast.success("Session completed");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to complete session");
    },
  });
}

export function useCloseSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.closeSession(id),
    onSuccess: (session) => {
      invalidateSessionQueries(qc, session.id);
      toast.success("Session closed");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to close session");
    },
  });
}

export function useSubmitReconciliation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, params }: { id: number; params: SubmitReconciliationParams }) =>
      api.submitReconciliation(id, params),
    onSuccess: (_data, vars) => {
      invalidateSessionQueries(qc, vars.id);
      toast.success("Reconciliation submitted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to submit reconciliation");
    },
  });
}

export function useAddCashSale() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, params }: { id: number; params: AddCashSaleParams }) => api.addCashSale(id, params),
    onSuccess: (_data, vars) => {
      invalidateSessionQueries(qc, vars.id);
      toast.success("Cash sale added");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to add cash sale");
    },
  });
}

export function useRemoveCashSale() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, cashSaleId }: { id: number; cashSaleId: number }) => api.removeCashSale(id, cashSaleId),
    onSuccess: (_data, vars) => {
      invalidateSessionQueries(qc, vars.id);
      toast.success("Cash sale removed");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to remove cash sale");
    },
  });
}
