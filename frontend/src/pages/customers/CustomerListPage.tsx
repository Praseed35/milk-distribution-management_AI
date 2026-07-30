import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import Badge from "../../components/ui/Badge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useCustomers, useDeleteCustomer } from "../../hooks/useCustomers";
import type { CustomerResponse } from "../../types/customer";

export default function CustomerListPage() {
  const navigate = useNavigate();
  const { data: customers, isLoading, error } = useCustomers();
  const deleteCustomer = useDeleteCustomer();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load customers" />;
  if (!customers?.length) return <EmptyState message="No customers found" actionLabel="Create Customer" onAction={() => navigate("/customers/new")} />;

  return (
    <div>
      <PageHeader title="Customers" description="Manage customer accounts" actionLabel="Create Customer" onAction={() => navigate("/customers/new")} />
      <DataTable
        columns={[
          { key: "customer_code", header: "Code", sortable: true },
          { key: "customer_name", header: "Name", sortable: true },
          { key: "primary_phone", header: "Phone" },
          { key: "route_id", header: "Route ID" },
          { key: "is_active", header: "Status", render: (c: CustomerResponse) => <Badge status={c.is_active ? "Active" : "Inactive"} /> },
          { key: "id", header: "Actions", render: (c: CustomerResponse) => (
            <div className="flex gap-2">
              <button onClick={(e) => { e.stopPropagation(); navigate(`/customers/${c.id}`); }} className="text-indigo-600 hover:text-indigo-800 text-sm">View</button>
              <button onClick={(e) => { e.stopPropagation(); navigate(`/customers/${c.id}/edit`); }} className="text-indigo-600 hover:text-indigo-800 text-sm">Edit</button>
              <button onClick={(e) => { e.stopPropagation(); setDeleteId(c.id); }} className="text-red-600 hover:text-red-800 text-sm">Delete</button>
            </div>
          )},
        ]}
        data={customers}
        keyExtractor={(c) => c.id}
        onRowClick={(c) => navigate(`/customers/${c.id}`)}
      />
      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Customer"
        message="Are you sure you want to delete this customer?"
        variant="danger"
        loading={deleteCustomer.isPending}
        onConfirm={() => {
          if (deleteId) deleteCustomer.mutate(deleteId, { onSettled: () => setDeleteId(null) });
        }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
