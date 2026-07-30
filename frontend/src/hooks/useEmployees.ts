import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "../api/employees";
import type { EmployeeCreate, EmployeeUpdate, EmployeeCredentialsUpdate } from "../types/employee";

export function useEmployees() {
  return useQuery({
    queryKey: ["employees"],
    queryFn: api.getEmployees,
  });
}

export function useEmployee(id: number) {
  return useQuery({
    queryKey: ["employees", id],
    queryFn: () => api.getEmployee(id),
    enabled: !!id,
  });
}

export function useCreateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: EmployeeCreate) => api.createEmployee(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["employees"] });
      toast.success("Employee created");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create employee");
    },
  });
}

export function useUpdateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: EmployeeUpdate }) => api.updateEmployee(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["employees"] });
      toast.success("Employee updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update employee");
    },
  });
}

export function useUpdateEmployeeCredentials() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: EmployeeCredentialsUpdate }) => api.updateEmployeeCredentials(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["employees"] });
      toast.success("Credentials updated");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update credentials");
    },
  });
}

export function useDeleteEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteEmployee(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["employees"] });
      toast.success("Employee deleted");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete employee");
    },
  });
}
