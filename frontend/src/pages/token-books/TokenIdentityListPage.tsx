import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useTokenIdentities, useDeleteTokenIdentity } from "../../hooks/useTokenBooks";
import { useCustomers } from "../../hooks/useCustomers";
import { useMilkTypes } from "../../hooks/useMilkTypes";
import type { TokenIdentityListResponse } from "../../types/token-identity";

export default function TokenIdentityListPage() {
  const navigate = useNavigate();
  const { data: identities, isLoading, error } = useTokenIdentities();
  const { data: customers } = useCustomers();
  const { data: milkTypes } = useMilkTypes();
  const deleteIdentity = useDeleteTokenIdentity();
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [customerFilter, setCustomerFilter] = useState("");
  const [milkTypeFilter, setMilkTypeFilter] = useState("");

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load token identities" />;
  if (!identities?.length)
    return (
      <EmptyState
        message="No token identities found"
        actionLabel="Create Identity"
        onAction={() => navigate("/token-identities/new")}
      />
    );

  const filtered = identities.filter((i) => {
    if (customerFilter && i.customer_id !== Number(customerFilter)) return false;
    if (milkTypeFilter && i.milk_type_id !== Number(milkTypeFilter)) return false;
    return true;
  });

  return (
    <div>
      <PageHeader
        title="Token Identities"
        description="Manage token numbers assigned to customers"
        actionLabel="Create Identity"
        onAction={() => navigate("/token-identities/new")}
      />
      <div className="mb-4 grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-xl">
        <Select
          label="Filter by Customer"
          placeholder="All customers"
          options={customers?.map((c) => ({ value: c.id, label: `${c.customer_code} - ${c.customer_name}` })) || []}
          value={customerFilter}
          onChange={(e) => setCustomerFilter(e.target.value)}
        />
        <Select
          label="Filter by Milk Type"
          placeholder="All milk types"
          options={milkTypes?.map((m) => ({ value: m.id, label: `${m.milk_name} (${m.volume_ml} ml)` })) || []}
          value={milkTypeFilter}
          onChange={(e) => setMilkTypeFilter(e.target.value)}
        />
      </div>
      <DataTable
        columns={[
          { key: "customer_code", header: "Customer Code", sortable: true },
          { key: "customer_name", header: "Customer", sortable: true },
          {
            key: "milk_type",
            header: "Milk Type",
            render: (i: TokenIdentityListResponse) => `${i.milk_type_name} (${i.milk_type_volume} ml)`,
          },
          { key: "token_number", header: "Token Number" },
          {
            key: "id",
            header: "Actions",
            render: (i: TokenIdentityListResponse) => (
              <div className="flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/token-identities/${i.id}/edit`);
                  }}
                  className="text-indigo-600 hover:text-indigo-800 text-sm"
                >
                  Edit
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteId(i.id);
                  }}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Delete
                </button>
              </div>
            ),
          },
        ]}
        data={filtered}
        keyExtractor={(i) => i.id}
      />
      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Token Identity"
        message="Are you sure you want to delete this token identity?"
        variant="danger"
        loading={deleteIdentity.isPending}
        onConfirm={() => {
          if (deleteId) deleteIdentity.mutate(deleteId, { onSettled: () => setDeleteId(null) });
        }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
