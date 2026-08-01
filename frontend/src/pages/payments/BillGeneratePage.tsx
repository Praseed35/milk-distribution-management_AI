import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Textarea from "../../components/ui/Textarea";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import { useGenerateBill, useBills } from "../../hooks/usePayments";
import { useCustomers } from "../../hooks/useCustomers";
import { formatCurrency } from "../../lib/utils";

interface GenerateResult {
  customerId: number;
  customerName: string;
  ok: boolean;
  message: string;
}

export default function BillGeneratePage() {
  const navigate = useNavigate();
  const { data: customers, isLoading: customersLoading } = useCustomers();
  const generateBill = useGenerateBill();

  const [selected, setSelected] = useState<number[]>([]);
  const [form, setForm] = useState({
    period_start: "",
    period_end: "",
    due_date: "",
    remarks: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [results, setResults] = useState<GenerateResult[] | null>(null);
  const [running, setRunning] = useState(false);

  const { data: existingBills } = useBills({
    from_date: form.period_start || undefined,
    to_date: form.period_end || undefined,
  });
  const existingCustomerIds = new Set((existingBills || []).map((b) => b.customer_id));
  const conflictingCustomers = (customers || []).filter((c) => existingCustomerIds.has(c.id) && selected.includes(c.id));

  function toggleCustomer(id: number) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  function validate() {
    const e: Record<string, string> = {};
    if (!selected.length) e.selected = "Select at least one customer";
    if (!form.period_start) e.period_start = "Start date is required";
    if (!form.period_end) e.period_end = "End date is required";
    if (form.period_start && form.period_end && form.period_end < form.period_start) {
      e.period_end = "End date must be on or after start date";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleGenerate(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setRunning(true);
    setResults([]);
    const out: GenerateResult[] = [];
    for (const customerId of selected) {
      const customer = customers?.find((c) => c.id === customerId);
      try {
        const bill = await generateBill.mutateAsync({
          customer_id: customerId,
          bill_period_start: form.period_start,
          bill_period_end: form.period_end,
          due_date: form.due_date || null,
          remarks: form.remarks || null,
        });
        out.push({
          customerId,
          customerName: customer?.customer_name || `#${customerId}`,
          ok: true,
          message: `Bill #${bill.id} created — total ${formatCurrency(bill.total_amount)}`,
        });
      } catch (err: any) {
        out.push({
          customerId,
          customerName: customer?.customer_name || `#${customerId}`,
          ok: false,
          message: err?.response?.data?.detail || "Failed to generate bill (no deliveries in period?)",
        });
      }
    }
    setResults(out);
    setRunning(false);
  }

  if (customersLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">Generate Bills</h1>
      <form onSubmit={handleGenerate} noValidate className="space-y-4 bg-white p-6 rounded-lg shadow">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Customers <span className="text-red-500">*</span>
          </label>
          <div className="border border-slate-300 rounded-md max-h-56 overflow-y-auto p-2">
            {customers?.map((c) => (
              <label key={c.id} className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selected.includes(c.id)}
                  onChange={() => toggleCustomer(c.id)}
                  className="h-4 w-4 text-indigo-600"
                />
                <span className="text-sm text-slate-700">
                  {c.customer_code} - {c.customer_name}
                </span>
              </label>
            ))}
            {!customers?.length && <p className="text-sm text-slate-500 p-2">No customers available</p>}
          </div>
          {errors.selected && <p className="mt-1 text-sm text-red-600">{errors.selected}</p>}
          {conflictingCustomers.length > 0 && (
            <p className="mt-2 text-sm text-amber-600">
              Warning: the following customers already have a bill in this period and will generate duplicates:{" "}
              {conflictingCustomers.map((c) => c.customer_name).join(", ")}
            </p>
          )}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Period Start"
            required
            type="date"
            value={form.period_start}
            onChange={(e) => setForm({ ...form, period_start: e.target.value })}
            error={errors.period_start}
          />
          <Input
            label="Period End"
            required
            type="date"
            value={form.period_end}
            onChange={(e) => setForm({ ...form, period_end: e.target.value })}
            error={errors.period_end}
          />
        </div>
        <Input
          label="Due Date"
          type="date"
          value={form.due_date}
          onChange={(e) => setForm({ ...form, due_date: e.target.value })}
        />
        <Textarea label="Remarks" value={form.remarks} onChange={(e) => setForm({ ...form, remarks: e.target.value })} />
        {results && results.length > 0 && (
          <div className="bg-slate-50 border border-slate-200 rounded-md p-4 space-y-2">
            <p className="text-sm font-medium text-slate-700">Generation results</p>
            {results.map((r) => (
              <p key={r.customerId} className={`text-sm ${r.ok ? "text-emerald-700" : "text-red-600"}`}>
                {r.customerName}: {r.message}
              </p>
            ))}
          </div>
        )}
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/payments/bills")}>
            Cancel
          </Button>
          <Button type="submit" loading={running}>
            Generate Bills
          </Button>
        </div>
      </form>
    </div>
  );
}
