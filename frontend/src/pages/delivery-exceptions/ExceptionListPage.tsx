import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import Badge from "../../components/ui/Badge";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useDeliveryExceptions, useDeleteDeliveryException } from "../../hooks/useDeliveryExceptions";
import { useSubscriptions } from "../../hooks/useSubscriptions";
import { useAuth } from "../../providers/AuthProvider";
import { formatDate } from "../../lib/utils";
import type { DeliveryExceptionListResponse } from "../../types/delivery-exception";

export default function ExceptionListPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const isChecker = user?.role === "CHECKER";
  const { data: exceptions, isLoading, error } = useDeliveryExceptions();
  const { data: subscriptions } = useSubscriptions();
  const deleteException = useDeleteDeliveryException();
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [subscriptionFilter, setSubscriptionFilter] = useState("");

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load delivery exceptions" />;
  if (!exceptions?.length)
    return (
      <EmptyState
        message="No delivery exceptions found"
        actionLabel="Create Exception"
        onAction={() => navigate("/delivery-exceptions/new")}
      />
    );

  const filtered = subscriptionFilter
    ? exceptions.filter((e) => e.subscription_id === Number(subscriptionFilter))
    : exceptions;

  return (
    <div>
      <PageHeader
        title="Delivery Exceptions"
        description="Manage delivery exceptions"
        actionLabel={isChecker ? undefined : "Create Exception"}
        onAction={() => navigate("/delivery-exceptions/new")}
      />
      <div className="mb-4 max-w-xs">
        <Select
          label="Filter by Subscription"
          placeholder="All subscriptions"
          options={
            subscriptions?.map((s) => ({
              value: s.id,
              label: `${s.customer_code} - ${s.customer_name}`,
            })) || []
          }
          value={subscriptionFilter}
          onChange={(e) => setSubscriptionFilter(e.target.value)}
        />
      </div>
      <DataTable
        columns={[
          { key: "customer_code", header: "Customer Code", sortable: true },
          { key: "customer_name", header: "Customer", sortable: true },
          { key: "route_name", header: "Route" },
          { key: "exception_type", header: "Type", sortable: true },
          { key: "shift", header: "Shift", render: (e: DeliveryExceptionListResponse) => e.shift || "Whole Day" },
          { key: "start_date", header: "Start Date", render: (e: DeliveryExceptionListResponse) => formatDate(e.start_date) },
          { key: "end_date", header: "End Date", render: (e: DeliveryExceptionListResponse) => (e.end_date ? formatDate(e.end_date) : "-") },
          { key: "status", header: "Status", render: (e: DeliveryExceptionListResponse) => <Badge status={e.status} /> },
          ...(isChecker
            ? []
            : [
                {
                  key: "id",
                  header: "Actions",
                  render: (e: DeliveryExceptionListResponse) => (
                    <div className="flex gap-2">
                      <button
                        onClick={(ev) => {
                          ev.stopPropagation();
                          navigate(`/delivery-exceptions/${e.id}/edit`);
                        }}
                        className="text-indigo-600 hover:text-indigo-800 text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={(ev) => {
                          ev.stopPropagation();
                          setDeleteId(e.id);
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
        keyExtractor={(e) => e.id}
      />
      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Delivery Exception"
        message="Are you sure you want to delete this delivery exception?"
        variant="danger"
        loading={deleteException.isPending}
        onConfirm={() => {
          if (deleteId) deleteException.mutate(deleteId, { onSettled: () => setDeleteId(null) });
        }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
