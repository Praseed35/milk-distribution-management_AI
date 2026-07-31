import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/token-books";
import type { TokenIdentityCreate, TokenIdentityUpdate } from "../types/token-identity";
import type {
  TokenBookIssueCreate,
  TokenBookIssueUpdate,
  TokenBookPaymentCreate,
  TokenBookPaymentUpdate,
} from "../types/token-book";

export function useTokenIdentities() {
  return useQuery({
    queryKey: ["token-identities"],
    queryFn: api.getTokenIdentities,
  });
}

export function useTokenIdentity(id: number) {
  return useQuery({
    queryKey: ["token-identities", id],
    queryFn: () => api.getTokenIdentity(id),
    enabled: !!id,
  });
}

export function useCreateTokenIdentity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: TokenIdentityCreate) => api.createTokenIdentity(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["token-identities"] });
      toast.success("Token identity created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create token identity");
    },
  });
}

export function useUpdateTokenIdentity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TokenIdentityUpdate }) => api.updateTokenIdentity(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["token-identities"] });
      toast.success("Token identity updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update token identity");
    },
  });
}

export function useDeleteTokenIdentity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteTokenIdentity(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["token-identities"] });
      toast.success("Token identity deleted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete token identity");
    },
  });
}

export function useTokenBookIssues() {
  return useQuery({
    queryKey: ["token-book-issues"],
    queryFn: api.getTokenBookIssues,
  });
}

export function useTokenBookIssue(id: number) {
  return useQuery({
    queryKey: ["token-book-issues", id],
    queryFn: () => api.getTokenBookIssue(id),
    enabled: !!id,
  });
}

export function useCreateTokenBookIssue() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: TokenBookIssueCreate) => api.createTokenBookIssue(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["token-book-issues"] });
      toast.success("Token book issue created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create token book issue");
    },
  });
}

export function useUpdateTokenBookIssue() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TokenBookIssueUpdate }) => api.updateTokenBookIssue(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["token-book-issues"] });
      toast.success("Token book issue updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update token book issue");
    },
  });
}

export function useDeleteTokenBookIssue() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteTokenBookIssue(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["token-book-issues"] });
      toast.success("Token book issue deleted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete token book issue");
    },
  });
}

export function useTokenBookPayments() {
  return useQuery({
    queryKey: ["token-book-payments"],
    queryFn: api.getTokenBookPayments,
  });
}

export function useTokenBookPayment(id: number) {
  return useQuery({
    queryKey: ["token-book-payments", id],
    queryFn: () => api.getTokenBookPayment(id),
    enabled: !!id,
  });
}

export function useCreateTokenBookPayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: TokenBookPaymentCreate) => api.createTokenBookPayment(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["token-book-payments"] });
      toast.success("Token book payment created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create token book payment");
    },
  });
}

export function useUpdateTokenBookPayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TokenBookPaymentUpdate }) => api.updateTokenBookPayment(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["token-book-payments"] });
      toast.success("Token book payment updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update token book payment");
    },
  });
}

export function useDeleteTokenBookPayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteTokenBookPayment(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["token-book-payments"] });
      toast.success("Token book payment deleted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete token book payment");
    },
  });
}
