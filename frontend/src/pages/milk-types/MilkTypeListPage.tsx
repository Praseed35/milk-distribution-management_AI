import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import Badge from "../../components/ui/Badge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useMilkTypes, useDeleteMilkType } from "../../hooks/useMilkTypes";
import type { MilkTypeResponse } from "../../types/milk-type";

export default function MilkTypeListPage() {
  const navigate = useNavigate();
  const { data: milkTypes, isLoading, error } = useMilkTypes();
  const deleteMilkType = useDeleteMilkType();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load milk types" />;
  if (!milkTypes?.length) return <EmptyState message="No milk types found" actionLabel="Create Milk Type" onAction={() => navigate("/milk-types/new")} />;

  return (
    <div>
      <PageHeader title="Milk Types" description="Manage milk product types" actionLabel="Create Milk Type" onAction={() => navigate("/milk-types/new")} />
      <DataTable
        columns={[
          { key: "milk_name", header: "Name", sortable: true },
          { key: "volume_ml", header: "Volume (ml)", sortable: true },
          { key: "unit_price", header: "Unit Price" },
          { key: "description", header: "Description" },
          { key: "is_active", header: "Status", render: (m: MilkTypeResponse) => <Badge status={m.is_active ? "Active" : "Inactive"} /> },
          { key: "id", header: "Actions", render: (m: MilkTypeResponse) => (
            <div className="flex gap-2">
              <button onClick={(e) => { e.stopPropagation(); navigate(`/milk-types/${m.id}/edit`); }} className="text-indigo-600 hover:text-indigo-800 text-sm">Edit</button>
              <button onClick={(e) => { e.stopPropagation(); setDeleteId(m.id); }} className="text-red-600 hover:text-red-800 text-sm">Delete</button>
            </div>
          )},
        ]}
        data={milkTypes}
        keyExtractor={(m) => m.id}
        onRowClick={(m) => navigate(`/milk-types/${m.id}/edit`)}
      />
      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Milk Type"
        message="Are you sure you want to delete this milk type?"
        variant="danger"
        loading={deleteMilkType.isPending}
        onConfirm={() => {
          if (deleteId) deleteMilkType.mutate(deleteId, { onSettled: () => setDeleteId(null) });
        }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
