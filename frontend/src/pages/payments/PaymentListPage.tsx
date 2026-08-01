import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import Select from "../../components/ui/Select";
import Input from "../../components/ui/Input";
import { usePayments } from "../../hooks/usePayments";
import { useCustomers } from "../../hooks/useCustomers";
import { PAYMENT_MODES, PAYMENT_TYPES } from "../../lib/constants";
import { formatCurrency, formatDate } from "../../lib/utils";
import type { CustomerPaymentListResponse } from "../../types/payment";

export default function PaymentListPage() {
  const navigate = useNavigate();
  const { data: customers } = useCustomers();
  const [filters, setFilters] = useState({
    customer_id: "",
    payment_mode: "",
    payment_type: "",
    from_date: "",
    to_date: "",
  });

  const params = {
    customer_id: filters.customer_id ? Number(filters.customer_id) : undefined,
    payment_mode: filters.payment_mode || undefined,
    payment_type: filters.payment_type || undefined,
    from_date: filters.from_date || undefined,
    to_date: filters.to_date || undefined,
  };

  const { data: payments, isLoading, error } = usePayments(params);

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load payments" />;

  return (
    <div>
      <PageHeader
        title="Payments"
        description="Recorded customer payments (history is immutable)"
        actionLabel="Record Payment"
        onAction={() => navigate("/payments/new")}
      />
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
        <Select
          label="Customer"
          options={customers?.map((c) => ({ value: c.id, label: `${c.customer_code} - ${c.customer_name}` })) || []}
          placeholder="All customers"
          value={filters.customer_id}
          onChange={(e) => setFilters({ ...filters, customer_id: e.target.value })}
        />
        <Select
          label="Payment Mode"
          options={PAYMENT_MODES.map((m) => ({ value: m, label: m }))}
          placeholder="All modes"
          value={filters.payment_mode}
          onChange={(e) => setFilters({ ...filters, payment_mode: e.target.value })}
        />
        <Select
          label="Payment Type"
          options={PAYMENT_TYPES.map((t) => ({ value: t, label: t === "ADVANCE" ? "Advance" : "Bill Payment" }))}
          placeholder="All types"
          value={filters.payment_type}
          onChange={(e) => setFilters({ ...filters, payment_type: e.target.value })}
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
      {!payments?.length ? (
        <EmptyState
          message="No payments found"
          actionLabel="Record Payment"
          onAction={() => navigate("/payments/new")}
        />
      ) : (
        <DataTable
          columns={[
            {
              key: "customer",
              header: "Customer",
              sortable: true,
              render: (p: CustomerPaymentListResponse) => `${p.customer_code} - ${p.customer_name}`,
            },
            {
              key: "payment_date",
              header: "Payment Date",
              sortable: true,
              render: (p: CustomerPaymentListResponse) => formatDate(p.payment_date),
            },
            {
              key: "amount",
              header: "Amount",
              sortable: true,
              render: (p: CustomerPaymentListResponse) => formatCurrency(p.amount),
            },
            { key: "payment_mode", header: "Mode" },
            { key: "payment_type", header: "Type" },
            {
              key: "reference_number",
              header: "Reference",
              render: (p: CustomerPaymentListResponse) => p.reference_number || "—",
            },
            {
              key: "bill_id",
              header: "Bill",
              render: (p: CustomerPaymentListResponse) => (p.bill_id ? `#${p.bill_id}` : "—"),
            },
          ]}
          data={payments}
          keyExtractor={(p) => p.id}
        />
      )}
    </div>
  );
}
