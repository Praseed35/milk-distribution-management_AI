import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/deliveries";
import type { DailyDeliveryEditRequest, DailyDeliveryUpdate, UnplannedDeliveryCreate } from "../types/delivery";
import type { TokenRegistrationRequest, TokenValidationRequest } from "../types/delivery";

export function useSessionDeliveries(sessionId: number) {
  return useQuery({
    queryKey: ["session-deliveries", sessionId],
    queryFn: () => api.getSessionDeliveries(sessionId),
    enabled: !!sessionId,
  });
}

export function useDeliveryWarnings(id: number) {
  return useQuery({
    queryKey: ["delivery-warnings", id],
    queryFn: () => api.getDeliveryWarnings(id),
    enabled: !!id,
  });
}

export function useCustomerTokenStatus(customerId: number) {
  return useQuery({
    queryKey: ["customer-token-status", customerId],
    queryFn: () => api.getCustomerTokenStatus(customerId),
    enabled: !!customerId,
  });
}

function invalidateDeliveryQueries(qc: any, sessionId?: number) {
  if (sessionId) {
    qc.invalidateQueries({ queryKey: ["session-deliveries", sessionId] });
    qc.invalidateQueries({ queryKey: ["session-checklist", sessionId] });
    qc.invalidateQueries({ queryKey: ["reconciliation", sessionId] });
    qc.invalidateQueries({ queryKey: ["reconciliation-summary", sessionId] });
    qc.invalidateQueries({ queryKey: ["reconciliation-customers", sessionId] });
    qc.invalidateQueries({ queryKey: ["session-detail", sessionId] });
    qc.invalidateQueries({ queryKey: ["session-report", sessionId] });
    qc.invalidateQueries({ queryKey: ["session-edit-history", sessionId] });
  }
  qc.invalidateQueries({ queryKey: ["delivery-sessions"] });
}

export function useUpdateDelivery() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, sessionId: _s, data }: { id: number; sessionId: number; data: DailyDeliveryUpdate }) =>
      api.updateDelivery(id, data),
    onSuccess: (_data, vars) => {
      invalidateDeliveryQueries(qc, vars.sessionId);
      toast.success("Delivery updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update delivery");
    },
  });
}

export function useRegisterToken() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, sessionId: _s, data }: { id: number; sessionId: number; data: TokenRegistrationRequest }) =>
      api.registerToken(id, data),
    onSuccess: (_data, vars) => {
      invalidateDeliveryQueries(qc, vars.sessionId);
      toast.success("Token sheet registered");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to register token sheet");
    },
  });
}

export function useValidateToken() {
  return useMutation({
    mutationFn: (data: TokenValidationRequest) => api.validateToken(data),
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Token validation failed");
    },
  });
}

export function useAddUnplannedDelivery() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: UnplannedDeliveryCreate) => api.addUnplannedDelivery(data),
    onSuccess: (_data, vars) => {
      invalidateDeliveryQueries(qc, vars.session_id);
      toast.success("Unplanned delivery added");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to add unplanned delivery");
    },
  });
}

export function useEditDelivery() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, sessionId: _s, data }: { id: number; sessionId: number; data: DailyDeliveryEditRequest }) =>
      api.editDelivery(id, data),
    onSuccess: (_data, vars) => {
      invalidateDeliveryQueries(qc, vars.sessionId);
      toast.success("Delivery edited");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to edit delivery");
    },
  });
}

export function useReopenSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: number; reason: string }) => api.reopenSession(id, { reason }),
    onSuccess: (session) => {
      invalidateDeliveryQueries(qc, session.id);
      toast.success("Session reopened");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to reopen session");
    },
  });
}

export function useEditHistory(sessionId: number) {
  return useQuery({
    queryKey: ["session-edit-history", sessionId],
    queryFn: () => api.getEditHistory(sessionId),
    enabled: !!sessionId,
  });
}
