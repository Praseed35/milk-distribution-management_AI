import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import Badge from "../../components/ui/Badge";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useTokenBookPayments, useDeleteTokenBookPayment, useTokenBookIssues } from "../../hooks/useTokenBooks";
import { useAuth } from "../../providers/AuthProvider";
import { formatDate, formatCurrency } from "../../lib/utils";
import { STATUS_BADGE_MAP } from "../../lib/constants";
import type { TokenBookPaymentListResponse } from "../../types/token-book";

export default function TokenBookPaymentListPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const isChecker = user?.role === "CHECKER";
  const { data: payments, isLoading, error } = useTokenBookPayments();
  const { data: issues } = useTokenBookIssues();
  const deletePayment = useDeleteTokenBookPayment();
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [issueFilter, setIssueFilter] = useState("");

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load token book payments" />;
  if (!payments?.length)
    return (
      <EmptyState
        message="No token book payments found"
        actionLabel={isChecker ? undefined : "Create Payment"}
        onAction={() => navigate("/token-book-payments/new")}
      />
    );

  const filtered = payments.filter((p) => {
    if (issueFilter && p.token_book_issue_id !== Number(issueFilter)) return false;
    return true;
  });

  return (
    <div>
      <PageHeader
        title="Token Book Payments"
        description="Record and manage token book payments"
        actionLabel={isChecker ? undefined : "Create Payment"}
        onAction={() => navigate("/token-book-payments/new")}
      />
      <div className="mb-4 grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-xl">
        <Select
          label="Filter by Issue"
          placeholder="All issues"
          options={
            issues?.map((i) => ({
              value: i.id,
              label: `Issue #${i.issue_number} - ${i.customer_name}`,
            })) || []
          }
          value={issueFilter}
          onChange={(e) => setIssueFilter(e.target.value)}
        />
      </div>
      <DataTable
        columns={[
          { key: "customer_code", header: "Customer Code", sortable: true },
          { key: "customer_name", header: "Customer", sortable: true },
          { key: "payment_mode", header: "Mode" },
          { key: "book_price", header: "Book Price", render: (p: TokenBookPaymentListResponse) => formatCurrency(p.book_price) },
          { key: "amount_paid", header: "Amount Paid", render: (p: TokenBookPaymentListResponse) => formatCurrency(p.amount_paid) },
          { key: "balance_amount", header: "Balance", render: (p: TokenBookPaymentListResponse) => formatCurrency(p.balance_amount) },
          {
            key: "payment_status",
            header: "Status",
            render: (p: TokenBookPaymentListResponse) => (
              <Badge status={STATUS_BADGE_MAP[p.payment_status]?.label ?? p.payment_status} />
            ),
          },
          { key: "payment_date", header: "Payment Date", render: (p: TokenBookPaymentListResponse) => formatDate(p.payment_date) },
          ...(isChecker
            ? []
            : [
                {
                  key: "id",
                  header: "Actions",
                  render: (p: TokenBookPaymentListResponse) => (
                    <div className="flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/token-book-payments/${p.id}/edit`);
                        }}
                        className="text-indigo-600 hover:text-indigo-800 text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteId(p.id);
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
        keyExtractor={(p) => p.id}
      />
      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Token Book Payment"
        message="Are you sure you want to delete this token book payment?"
        variant="danger"
        loading={deletePayment.isPending}
        onConfirm={() => {
          if (deleteId) deletePayment.mutate(deleteId, { onSettled: () => setDeleteId(null) });
        }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
