import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import Badge from "../../components/ui/Badge";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useSubscriptions, useDeleteSubscription } from "../../hooks/useSubscriptions";
import { useCustomers } from "../../hooks/useCustomers";
import { useAuth } from "../../providers/AuthProvider";
import type { SubscriptionListResponse } from "../../types/subscription";

export default function SubscriptionListPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const isChecker = user?.role === "CHECKER";
  const { data: subscriptions, isLoading, error } = useSubscriptions();
  const { data: customers } = useCustomers();
  const deleteSubscription = useDeleteSubscription();
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [customerFilter, setCustomerFilter] = useState("");

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load subscriptions" />;
  if (!subscriptions?.length)
    return <EmptyState message="No subscriptions found" actionLabel="Create Subscription" onAction={() => navigate("/subscriptions/new")} />;

  const filtered = customerFilter
    ? subscriptions.filter((s) => s.customer_id === Number(customerFilter))
    : subscriptions;

  return (
    <div>
      <PageHeader
        title="Subscriptions"
        description="Manage customer subscriptions"
        actionLabel={isChecker ? undefined : "Create Subscription"}
        onAction={() => navigate("/subscriptions/new")}
      />
      <div className="mb-4 max-w-xs">
        <Select
          label="Filter by Customer"
          placeholder="All customers"
          options={customers?.map((c) => ({ value: c.id, label: `${c.customer_code} - ${c.customer_name}` })) || []}
          value={customerFilter}
          onChange={(e) => setCustomerFilter(e.target.value)}
        />
      </div>
      <DataTable
        columns={[
          { key: "customer_code", header: "Customer Code", sortable: true },
          { key: "customer_name", header: "Customer", sortable: true },
          { key: "route_name", header: "Route" },
          {
            key: "milk_type",
            header: "Milk Type",
            render: (s: SubscriptionListResponse) => `${s.milk_type_name} (${s.milk_type_volume} ml)`,
          },
          { key: "morning_quantity", header: "Morning" },
          { key: "evening_quantity", header: "Evening" },
          { key: "status", header: "Status", render: (s: SubscriptionListResponse) => <Badge status={s.status} /> },
          ...(isChecker
            ? []
            : [
                {
                  key: "id",
                  header: "Actions",
                  render: (s: SubscriptionListResponse) => (
                    <div className="flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/subscriptions/${s.id}/edit`);
                        }}
                        className="text-indigo-600 hover:text-indigo-800 text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteId(s.id);
                        }}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  ),
                },
              ]),
        ]}
        data={filtered}
        keyExtractor={(s) => s.id}
      />
      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Subscription"
        message="Are you sure you want to delete this subscription?"
        variant="danger"
        loading={deleteSubscription.isPending}
        onConfirm={() => {
          if (deleteId) deleteSubscription.mutate(deleteId, { onSettled: () => setDeleteId(null) });
        }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
