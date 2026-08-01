import { useState } from "react";
import { useQueries } from "@tanstack/react-query";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import Select from "../../components/ui/Select";
import { useCustomers } from "../../hooks/useCustomers";
import { getOutstanding } from "../../api/payments";
import { formatCurrency, formatDate } from "../../lib/utils";

interface OutstandingRow {
  customer_id: number;
  customer_code: string;
  customer_name: string;
  total_billed: number;
  total_paid: number;
  balance: number;
  last_bill_date: string | null;
  last_payment_date: string | null;
}

export default function OutstandingPage() {
  const { data: customers, isLoading: customersLoading } = useCustomers();
  const [customerFilter, setCustomerFilter] = useState("");

  const activeCustomers = (customers || []).filter((c) => c.is_active !== false);

  const queries = useQueries({
    queries: activeCustomers.map((c) => ({
      queryKey: ["outstanding", c.id] as const,
      queryFn: () => getOutstanding(c.id),
      enabled: !!c.id,
    })),
  });

  if (customersLoading) return <LoadingSpinner className="mt-20" />;

  const rows: OutstandingRow[] = activeCustomers.map((c, i) => {
    const q = queries[i];
    const data = q?.data;
    return {
      customer_id: c.id,
      customer_code: c.customer_code,
      customer_name: c.customer_name,
      total_billed: data?.total_billed ?? 0,
      total_paid: data?.total_paid ?? 0,
      balance: data?.balance ?? 0,
      last_bill_date: data?.last_bill_date ?? null,
      last_payment_date: data?.last_payment_date ?? null,
    };
  });

  const filtered = customerFilter
    ? rows.filter((r) => r.customer_id === Number(customerFilter))
    : rows;

  const loading = queries.some((q) => q.isPending);
  const hasError = queries.some((q) => q.isError);

  return (
    <div>
      <PageHeader title="Outstanding Balances" description="Billed, paid, and balance per customer" />
      {hasError && <p className="text-sm text-red-600 mb-4">Failed to load some customer balances</p>}
      <div className="max-w-xs mb-4">
        <Select
          label="Customer"
          options={customers?.map((c) => ({ value: c.id, label: `${c.customer_code} - ${c.customer_name}` })) || []}
          placeholder="All customers"
          value={customerFilter}
          onChange={(e) => setCustomerFilter(e.target.value)}
        />
      </div>
      {loading ? (
        <LoadingSpinner className="mt-10" />
      ) : !filtered.length ? (
        <EmptyState message="No customers found" />
      ) : (
        <DataTable
          columns={[
            {
              key: "customer",
              header: "Customer",
              sortable: true,
              render: (r: OutstandingRow) => `${r.customer_code} - ${r.customer_name}`,
            },
            {
              key: "total_billed",
              header: "Total Billed",
              sortable: true,
              render: (r: OutstandingRow) => formatCurrency(r.total_billed),
            },
            {
              key: "total_paid",
              header: "Total Paid",
              sortable: true,
              render: (r: OutstandingRow) => formatCurrency(r.total_paid),
            },
            {
              key: "balance",
              header: "Balance",
              sortable: true,
              render: (r: OutstandingRow) => formatCurrency(r.balance),
            },
            {
              key: "last_bill_date",
              header: "Last Bill",
              render: (r: OutstandingRow) => (r.last_bill_date ? formatDate(r.last_bill_date) : "—"),
            },
            {
              key: "last_payment_date",
              header: "Last Payment",
              render: (r: OutstandingRow) => (r.last_payment_date ? formatDate(r.last_payment_date) : "—"),
            },
          ]}
          data={filtered}
          keyExtractor={(r) => r.customer_id}
        />
      )}
    </div>
  );
}
