import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";
import Select from "../../components/ui/Select";
import Badge from "../../components/ui/Badge";
import DataTable from "../../components/ui/DataTable";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useBill, usePayments, useUpdateBillStatus } from "../../hooks/usePayments";
import { useCustomers } from "../../hooks/useCustomers";
import { BILL_STATUS } from "../../lib/constants";
import { formatCurrency, formatDate } from "../../lib/utils";
import type { CustomerBillItemResponse } from "../../types/payment";

export default function BillDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const billId = Number(id);
  const { data: bill, isLoading, error } = useBill(billId);
  const { data: payments } = usePayments();
  const { data: customers } = useCustomers();
  const updateStatus = useUpdateBillStatus();

  const [status, setStatus] = useState("");
  const [confirmOpen, setConfirmOpen] = useState(false);

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error || !bill) return <EmptyState message="Bill not found" />;

  const appliedPayments = (payments || []).filter((p) => p.bill_id === billId);
  const cancellingWithPayments = status === "CANCELLED" && appliedPayments.length > 0;
  const customer = customers?.find((c) => c.id === bill.customer_id);

  function handleConfirmUpdate() {
    if (!status) return;
    updateStatus.mutate(
      { id: billId, status },
      {
        onSuccess: () => setConfirmOpen(false),
      }
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Button variant="ghost" onClick={() => navigate("/payments/bills")} className="mb-4">
        ← Back to Bills
      </Button>
      <div className="bg-white rounded-lg shadow p-6 mb-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-xl font-semibold text-slate-800">Bill #{bill.id}</h1>
            <p className="text-sm text-slate-500">
              {customer ? `${customer.customer_code} - ${customer.customer_name}` : `Customer #${bill.customer_id}`}
            </p>
          </div>
          <Badge status={bill.status} />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-slate-500">Bill Date</p>
            <p className="font-medium text-slate-800">{formatDate(bill.bill_date)}</p>
          </div>
          <div>
            <p className="text-slate-500">Period</p>
            <p className="font-medium text-slate-800">
              {formatDate(bill.bill_period_start)} – {formatDate(bill.bill_period_end)}
            </p>
          </div>
          <div>
            <p className="text-slate-500">Due Date</p>
            <p className="font-medium text-slate-800">{bill.due_date ? formatDate(bill.due_date) : "—"}</p>
          </div>
          <div>
            <p className="text-slate-500">Remarks</p>
            <p className="font-medium text-slate-800">{bill.remarks || "—"}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-4">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Line Items</h2>
        {bill.items.length ? (
          <>
            <DataTable
              columns={[
                { key: "milk_name", header: "Milk" },
                { key: "quantity", header: "Quantity" },
                {
                  key: "unit_price",
                  header: "Unit Price",
                  render: (i: CustomerBillItemResponse) => formatCurrency(i.unit_price),
                },
                {
                  key: "amount",
                  header: "Amount",
                  render: (i: CustomerBillItemResponse) => formatCurrency(i.amount),
                },
              ]}
              data={bill.items}
              keyExtractor={(i) => i.id}
            />
            <div className="mt-4 space-y-1 border-t border-slate-200 pt-4 text-sm">
              <p className="flex justify-between text-slate-600">
                <span>Total</span>
                <span className="font-medium">{formatCurrency(bill.total_amount)}</span>
              </p>
              <p className="flex justify-between text-slate-600">
                <span>Paid</span>
                <span className="font-medium text-emerald-700">{formatCurrency(bill.paid_amount)}</span>
              </p>
              <p className="flex justify-between text-slate-800 font-semibold">
                <span>Balance</span>
                <span>{formatCurrency(bill.balance_amount)}</span>
              </p>
            </div>
          </>
        ) : (
          <p className="text-sm text-slate-500">No line items on this bill</p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-4">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Applied Payments</h2>
        {appliedPayments.length ? (
          <DataTable
            columns={[
              {
                key: "payment_date",
                header: "Date",
                render: (p: (typeof appliedPayments)[number]) => formatDate(p.payment_date),
              },
              {
                key: "amount",
                header: "Amount",
                render: (p: (typeof appliedPayments)[number]) => formatCurrency(p.amount),
              },
              { key: "payment_mode", header: "Mode" },
              {
                key: "reference_number",
                header: "Reference",
                render: (p: (typeof appliedPayments)[number]) => p.reference_number || "—",
              },
            ]}
            data={appliedPayments}
            keyExtractor={(p) => p.id}
          />
        ) : (
          <p className="text-sm text-slate-500">No payments applied to this bill</p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Update Status</h2>
        <div className="flex items-end gap-3">
          <Select
            label="Status"
            options={Object.entries(BILL_STATUS).map(([key, v]) => ({ value: key, label: v.label }))}
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            placeholder={bill.status}
          />
          <Button
            onClick={() => setConfirmOpen(true)}
            disabled={!status || status === bill.status}
            loading={updateStatus.isPending}
          >
            Update Status
          </Button>
        </div>
        {cancellingWithPayments && (
          <p className="mt-3 text-sm text-amber-600">
            Warning: this bill has {appliedPayments.length} recorded payment(s). Cancelling the bill does not remove the
            recorded payments.
          </p>
        )}
      </div>

      <ConfirmDialog
        open={confirmOpen}
        title="Update Bill Status"
        message={`Change bill #${bill.id} status to ${status}?`}
        confirmLabel="Update Status"
        loading={updateStatus.isPending}
        onConfirm={handleConfirmUpdate}
        onCancel={() => setConfirmOpen(false)}
      >
        {cancellingWithPayments && (
          <p className="text-sm text-amber-700">
            This bill has recorded payments. They will remain on file even after cancellation. Continue?
          </p>
        )}
      </ConfirmDialog>
    </div>
  );
}
