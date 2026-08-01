import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import Badge from "../../components/ui/Badge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useEmployees, useDeleteEmployee } from "../../hooks/useEmployees";
import { useAuth } from "../../providers/AuthProvider";
import type { EmployeeResponse } from "../../types/employee";

export default function EmployeeListPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const isOwner = user?.role === "OWNER";
  const { data: employees, isLoading, error } = useEmployees();
  const deleteEmployee = useDeleteEmployee();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load employees" />;
  if (!employees?.length) {
    if (!isOwner) return <EmptyState message="No employees found" />;
    return <EmptyState message="No employees found" actionLabel="Create Employee" onAction={() => navigate("/employees/new")} />;
  }

  return (
    <div>
      <PageHeader title="Employees" description="Manage employees" actionLabel={isOwner ? "Create Employee" : undefined} onAction={() => navigate("/employees/new")} />
      <DataTable
        data={employees}
        keyExtractor={(e: EmployeeResponse) => e.id}
        columns={[
          { key: "employee_code", header: "Code", sortable: true },
          { key: "name", header: "Name", sortable: true },
          { key: "phone", header: "Phone" },
          { key: "role", header: "Role", sortable: true, render: (e: EmployeeResponse) => <Badge status={e.role} /> },
          { key: "route_id", header: "Route" },
          { key: "is_active", header: "Status", render: (e: EmployeeResponse) => <Badge status={e.is_active ? "Active" : "Inactive"} /> },
          ...(isOwner ? [{ key: "id", header: "Actions", render: (e: EmployeeResponse) => (
            <div className="flex gap-2">
              <button onClick={(ev) => { ev.stopPropagation(); navigate(`/employees/${e.id}/credentials`); }} className="text-indigo-600 hover:text-indigo-800 text-sm">Credentials</button>
              <button onClick={(ev) => { ev.stopPropagation(); navigate(`/employees/${e.id}/edit`); }} className="text-indigo-600 hover:text-indigo-800 text-sm">Edit</button>
              <button onClick={(ev) => { ev.stopPropagation(); setDeleteId(e.id); }} className="text-red-600 hover:text-red-800 text-sm">Delete</button>
            </div>
          )} ] : []),
        ]}
      />
      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Employee"
        message="Are you sure you want to delete this employee?"
        variant="danger"
        loading={deleteEmployee.isPending}
        onConfirm={() => {
          if (deleteId) deleteEmployee.mutate(deleteId, { onSettled: () => setDeleteId(null) });
        }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
