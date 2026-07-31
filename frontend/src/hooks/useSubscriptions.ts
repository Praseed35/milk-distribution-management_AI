import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/subscriptions";
import type { SubscriptionCreate, SubscriptionUpdate } from "../types/subscription";

export function useSubscriptions() {
  return useQuery({
    queryKey: ["subscriptions"],
    queryFn: api.getSubscriptions,
  });
}

export function useSubscription(id: number) {
  return useQuery({
    queryKey: ["subscriptions", id],
    queryFn: () => api.getSubscription(id),
    enabled: !!id,
  });
}

export function useCreateSubscription() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SubscriptionCreate) => api.createSubscription(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["subscriptions"] });
      toast.success("Subscription created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create subscription");
    },
  });
}

export function useUpdateSubscription() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: SubscriptionUpdate }) => api.updateSubscription(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["subscriptions"] });
      toast.success("Subscription updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update subscription");
    },
  });
}

export function useDeleteSubscription() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteSubscription(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["subscriptions"] });
      toast.success("Subscription deleted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete subscription");
    },
  });
}
