import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import Badge from "../../components/ui/Badge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useRoutes, useDeleteRoute } from "../../hooks/useRoutes";
import type { RouteResponse } from "../../types/route";

export default function RouteListPage() {
  const navigate = useNavigate();
  const { data: routes, isLoading, error } = useRoutes();
  const deleteRoute = useDeleteRoute();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load routes" />;
  if (!routes?.length) return <EmptyState message="No routes found" actionLabel="Create Route" onAction={() => navigate("/routes/new")} />;

  return (
    <div>
      <PageHeader title="Routes" description="Manage delivery routes" actionLabel="Create Route" onAction={() => navigate("/routes/new")} />
      <DataTable
        columns={[
          { key: "route_code", header: "Code", sortable: true },
          { key: "route_name", header: "Name", sortable: true },
          { key: "description", header: "Description" },
          { key: "is_active", header: "Status", render: (r: RouteResponse) => <Badge status={r.is_active ? "Active" : "Inactive"} /> },
          { key: "id", header: "Actions", render: (r: RouteResponse) => (
            <div className="flex gap-2">
              <button onClick={(e) => { e.stopPropagation(); navigate(`/routes/${r.id}/edit`); }} className="text-indigo-600 hover:text-indigo-800 text-sm">Edit</button>
              <button onClick={(e) => { e.stopPropagation(); setDeleteId(r.id); }} className="text-red-600 hover:text-red-800 text-sm">Delete</button>
            </div>
          )},
        ]}
        data={routes}
        keyExtractor={(r) => r.id}
        onRowClick={(r) => navigate(`/routes/${r.id}/edit`)}
      />
      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Route"
        message="Are you sure you want to delete this route?"
        variant="danger"
        loading={deleteRoute.isPending}
        onConfirm={() => {
          if (deleteId) deleteRoute.mutate(deleteId, { onSettled: () => setDeleteId(null) });
        }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
