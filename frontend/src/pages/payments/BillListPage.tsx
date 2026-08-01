import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import Select from "../../components/ui/Select";
import Input from "../../components/ui/Input";
import Badge from "../../components/ui/Badge";
import { useBills } from "../../hooks/usePayments";
import { useCustomers } from "../../hooks/useCustomers";
import { BILL_STATUS } from "../../lib/constants";
import { formatCurrency, formatDate } from "../../lib/utils";
import type { CustomerBillListResponse } from "../../types/payment";

export default function BillListPage() {
  const navigate = useNavigate();
  const { data: customers } = useCustomers();
  const [filters, setFilters] = useState({ customer_id: "", status: "", from_date: "", to_date: "" });

  const params = {
    customer_id: filters.customer_id ? Number(filters.customer_id) : undefined,
    status: filters.status || undefined,
    from_date: filters.from_date || undefined,
    to_date: filters.to_date || undefined,
  };

  const { data: bills, isLoading, error } = useBills(params);

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load bills" />;

  return (
    <div>
      <PageHeader
        title="Bills"
        description="Customer bills generated from delivered milk"
        actionLabel="Generate Bill"
        onAction={() => navigate("/payments/bills/generate")}
      />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <Select
          label="Customer"
          options={customers?.map((c) => ({ value: c.id, label: `${c.customer_code} - ${c.customer_name}` })) || []}
          placeholder="All customers"
          value={filters.customer_id}
          onChange={(e) => setFilters({ ...filters, customer_id: e.target.value })}
        />
        <Select
          label="Status"
          options={Object.entries(BILL_STATUS).map(([key, v]) => ({ value: key, label: v.label }))}
          placeholder="All statuses"
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
        />
        <Input
          label="From"
          type="date"
          value={filters.from_date}
          onChange={(e) => setFilters({ ...filters, from_date: e.target.value })}
        />
        <Input
          label="To"
          type="date"
          value={filters.to_date}
          onChange={(e) => setFilters({ ...filters, to_date: e.target.value })}
        />
      </div>
      {!bills?.length ? (
        <EmptyState
          message="No bills found"
          actionLabel="Generate Bill"
          onAction={() => navigate("/payments/bills/generate")}
        />
      ) : (
        <DataTable
          columns={[
            {
              key: "customer",
              header: "Customer",
              sortable: true,
              render: (b: CustomerBillListResponse) => `${b.customer_code} - ${b.customer_name}`,
            },
            { key: "bill_date", header: "Bill Date", render: (b: CustomerBillListResponse) => formatDate(b.bill_date) },
            {
              key: "period",
              header: "Period",
              render: (b: CustomerBillListResponse) => `${formatDate(b.bill_period_start)} – ${formatDate(b.bill_period_end)}`,
            },
            {
              key: "total_amount",
              header: "Total",
              render: (b: CustomerBillListResponse) => formatCurrency(b.total_amount),
            },
            {
              key: "paid_amount",
              header: "Paid",
              render: (b: CustomerBillListResponse) => formatCurrency(b.paid_amount),
            },
            {
              key: "balance_amount",
              header: "Balance",
              render: (b: CustomerBillListResponse) => formatCurrency(b.balance_amount),
            },
            { key: "status", header: "Status", render: (b: CustomerBillListResponse) => <Badge status={b.status} /> },
            { key: "due_date", header: "Due Date", render: (b: CustomerBillListResponse) => (b.due_date ? formatDate(b.due_date) : "—") },
          ]}
          data={bills}
          keyExtractor={(b) => b.id}
          onRowClick={(b) => navigate(`/payments/bills/${b.id}`)}
        />
      )}
    </div>
  );
}
