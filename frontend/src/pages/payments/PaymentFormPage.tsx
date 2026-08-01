import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import Textarea from "../../components/ui/Textarea";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import { useCreatePayment, useBills } from "../../hooks/usePayments";
import { useCustomers } from "../../hooks/useCustomers";
import { PAYMENT_MODES, PAYMENT_TYPES } from "../../lib/constants";
import { formatCurrency } from "../../lib/utils";

export default function PaymentFormPage() {
  const navigate = useNavigate();
  const { data: customers, isLoading: customersLoading } = useCustomers();
  const createPayment = useCreatePayment();

  const [form, setForm] = useState({
    customer_id: "",
    payment_type: "ADVANCE",
    amount: "",
    payment_mode: "CASH",
    reference_number: "",
    bill_id: "",
    remarks: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const customerId = form.customer_id ? Number(form.customer_id) : 0;
  const isBillPayment = form.payment_type === "BILL_PAYMENT";
  const { data: allBills, isLoading: billsLoading } = useBills(
    isBillPayment && customerId ? { customer_id: customerId } : undefined
  );
  const payableBills = (allBills || []).filter((b) => b.status !== "PAID" && b.status !== "CANCELLED");
  const selectedBill = payableBills.find((b) => b.id === Number(form.bill_id));

  function validate() {
    const e: Record<string, string> = {};
    if (!form.customer_id || form.customer_id === "0") {
      e.customer_id = "Customer is required";
    }
    const amount = Number(form.amount);
    if (form.amount === "" || isNaN(amount) || amount <= 0) {
      e.amount = "Amount must be greater than 0";
    }
    if (isBillPayment && (!form.bill_id || form.bill_id === "0")) {
      e.bill_id = "A bill is required for bill payments";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      await createPayment.mutateAsync({
        customer_id: Number(form.customer_id),
        amount: Number(form.amount),
        payment_mode: form.payment_mode as any,
        payment_type: form.payment_type as any,
        reference_number: form.reference_number || null,
        bill_id: isBillPayment && form.bill_id ? Number(form.bill_id) : null,
        remarks: form.remarks || null,
      });
      navigate("/payments");
    } catch {}
  }

  if (customersLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">Record Payment</h1>
      <form onSubmit={handleSubmit} noValidate className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Select
          label="Customer"
          required
          options={
            customers?.map((c) => ({
              value: c.id,
              label: `${c.customer_code} - ${c.customer_name}`,
            })) || []
          }
          placeholder="Select a customer"
          value={form.customer_id}
          onChange={(e) => setForm({ ...form, customer_id: e.target.value, bill_id: "" })}
          error={errors.customer_id}
        />
        <Select
          label="Payment Type"
          options={PAYMENT_TYPES.map((t) => ({ value: t, label: t === "ADVANCE" ? "Advance" : "Bill Payment" }))}
          value={form.payment_type}
          onChange={(e) => setForm({ ...form, payment_type: e.target.value, bill_id: "" })}
        />
        <Input
          label="Amount"
          required
          type="number"
          min={0.01}
          step="0.01"
          value={form.amount}
          onChange={(e) => setForm({ ...form, amount: e.target.value })}
          error={errors.amount}
        />
        <Select
          label="Payment Mode"
          required
          options={PAYMENT_MODES.map((m) => ({ value: m, label: m }))}
          value={form.payment_mode}
          onChange={(e) => setForm({ ...form, payment_mode: e.target.value })}
        />
        {isBillPayment && (
          <div>
            <Select
              label="Bill"
              required
              options={payableBills.map((b) => ({
                value: b.id,
                label: `Bill #${b.id} - ${b.customer_name} (${formatCurrency(b.balance_amount)} balance)`,
              }))}
              placeholder="Select an unpaid bill"
              value={form.bill_id}
              onChange={(e) => setForm({ ...form, bill_id: e.target.value })}
              error={errors.bill_id}
            />
            {billsLoading && <p className="mt-1 text-sm text-slate-500">Loading bills...</p>}
            {!billsLoading && selectedBill && (
              <p className="mt-1 text-sm text-slate-600">
                Bill balance: {formatCurrency(selectedBill.balance_amount)}
              </p>
            )}
          </div>
        )}
        <Input
          label="Reference Number"
          value={form.reference_number}
          onChange={(e) => setForm({ ...form, reference_number: e.target.value })}
        />
        <Textarea
          label="Remarks"
          value={form.remarks}
          onChange={(e) => setForm({ ...form, remarks: e.target.value })}
        />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/payments")}>
            Cancel
          </Button>
          <Button type="submit" loading={createPayment.isPending}>
            Record Payment
          </Button>
        </div>
      </form>
    </div>
  );
}
