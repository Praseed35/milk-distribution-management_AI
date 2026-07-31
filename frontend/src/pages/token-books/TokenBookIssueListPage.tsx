import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import Badge from "../../components/ui/Badge";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useTokenBookIssues, useDeleteTokenBookIssue, useTokenIdentities } from "../../hooks/useTokenBooks";
import { useCustomers } from "../../hooks/useCustomers";
import { formatDate } from "../../lib/utils";
import { STATUS_BADGE_MAP } from "../../lib/constants";
import type { TokenBookIssueListResponse } from "../../types/token-book";

export default function TokenBookIssueListPage() {
  const navigate = useNavigate();
  const { data: issues, isLoading, error } = useTokenBookIssues();
  const { data: customers } = useCustomers();
  const { data: identities } = useTokenIdentities();
  const deleteIssue = useDeleteTokenBookIssue();
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [customerFilter, setCustomerFilter] = useState("");
  const [identityFilter, setIdentityFilter] = useState("");

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load token book issues" />;
  if (!issues?.length)
    return (
      <EmptyState
        message="No token book issues found"
        actionLabel="Create Issue"
        onAction={() => navigate("/token-book-issues/new")}
      />
    );

  const filtered = issues.filter((i) => {
    if (customerFilter && i.customer_id !== Number(customerFilter)) return false;
    if (identityFilter && i.token_identity_id !== Number(identityFilter)) return false;
    return true;
  });

  return (
    <div>
      <PageHeader
        title="Token Book Issues"
        description="Manage token book issues assigned to identities"
        actionLabel="Create Issue"
        onAction={() => navigate("/token-book-issues/new")}
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
          label="Filter by Identity"
          placeholder="All identities"
          options={identities?.map((i) => ({ value: i.id, label: `#${i.token_number} - ${i.customer_name} (${i.milk_type_name})` })) || []}
          value={identityFilter}
          onChange={(e) => setIdentityFilter(e.target.value)}
        />
      </div>
      <DataTable
        columns={[
          { key: "customer_code", header: "Customer Code", sortable: true },
          { key: "customer_name", header: "Customer", sortable: true },
          { key: "milk_type_name", header: "Milk Type" },
          { key: "token_number", header: "Token" },
          { key: "issue_number", header: "Issue No" },
          { key: "issue_date", header: "Issue Date", render: (i: TokenBookIssueListResponse) => formatDate(i.issue_date) },
          { key: "current_sheet", header: "Current Sheet" },
          {
            key: "status",
            header: "Status",
            render: (i: TokenBookIssueListResponse) => (
              <Badge status={STATUS_BADGE_MAP[i.status]?.label ?? i.status} />
            ),
          },
          {
            key: "id",
            header: "Actions",
            render: (i: TokenBookIssueListResponse) => (
              <div className="flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/token-book-issues/${i.id}/edit`);
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
        title="Delete Token Book Issue"
        message="Are you sure you want to delete this token book issue?"
        variant="danger"
        loading={deleteIssue.isPending}
        onConfirm={() => {
          if (deleteId) deleteIssue.mutate(deleteId, { onSettled: () => setDeleteId(null) });
        }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
