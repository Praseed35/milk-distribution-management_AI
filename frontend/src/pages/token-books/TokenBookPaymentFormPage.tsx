import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import Textarea from "../../components/ui/Textarea";
import Badge from "../../components/ui/Badge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import {
  useTokenBookPayment,
  useCreateTokenBookPayment,
  useUpdateTokenBookPayment,
  useTokenBookIssues,
} from "../../hooks/useTokenBooks";
import { TOKEN_PAYMENT_MODES, STATUS_BADGE_MAP } from "../../lib/constants";
import { formatCurrency } from "../../lib/utils";

export default function TokenBookPaymentFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { data: payment, isLoading } = useTokenBookPayment(Number(id));
  const { data: issues } = useTokenBookIssues();
  const createPayment = useCreateTokenBookPayment();
  const updatePayment = useUpdateTokenBookPayment();

  const [form, setForm] = useState({
    token_book_issue_id: "",
    payment_mode: "PREPAID",
    book_price: "",
    amount_paid: "",
    remarks: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (payment) {
      setForm({
        token_book_issue_id: String(payment.token_book_issue.id),
        payment_mode: payment.payment_mode,
        book_price: String(payment.book_price),
        amount_paid: String(payment.amount_paid),
        remarks: payment.remarks ?? "",
      });
    }
  }, [payment]);

  function validate() {
    const e: Record<string, string> = {};
    if (!form.token_book_issue_id || form.token_book_issue_id === "0") {
      e.token_book_issue_id = "Issue is required";
    }
    const price = Number(form.book_price);
    if (form.book_price === "" || isNaN(price) || price <= 0) {
      e.book_price = "Book price must be greater than 0";
    }
    const amount = Number(form.amount_paid);
    if (form.amount_paid === "" || isNaN(amount) || amount < 0) {
      e.amount_paid = "Amount paid must be 0 or more";
    } else if (!isNaN(price) && amount > price) {
      e.amount_paid = "Amount paid cannot exceed book price";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      if (isEdit) {
        await updatePayment.mutateAsync({
          id: Number(id),
          data: {
            payment_mode: form.payment_mode as any,
            book_price: Number(form.book_price),
            amount_paid: Number(form.amount_paid),
            remarks: form.remarks || null,
          },
        });
      } else {
        await createPayment.mutateAsync({
          token_book_issue_id: Number(form.token_book_issue_id),
          payment_mode: form.payment_mode as any,
          book_price: Number(form.book_price),
          amount_paid: Number(form.amount_paid),
          remarks: form.remarks || null,
        });
      }
      navigate("/token-book-payments");
    } catch {}
  }

  if (isEdit && isLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">
        {isEdit ? "Edit Token Book Payment" : "Create Token Book Payment"}
      </h1>
      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Select
          label="Issue"
          required
          options={
            issues?.map((i) => ({
              value: i.id,
              label: `Issue #${i.issue_number} - ${i.customer_name}`,
            })) || []
          }
          placeholder="Select an issue"
          value={form.token_book_issue_id}
          onChange={(e) => setForm({ ...form, token_book_issue_id: e.target.value })}
          disabled={isEdit}
          error={errors.token_book_issue_id}
        />
        {isEdit && payment && (
          <div className="flex gap-6 text-sm">
            <div>
              <span className="text-slate-500">Payment Status: </span>
              <Badge status={STATUS_BADGE_MAP[payment.payment_status]?.label ?? payment.payment_status} />
            </div>
            <div>
              <span className="text-slate-500">Balance: </span>
              <span className="font-medium text-slate-800">{formatCurrency(payment.balance_amount)}</span>
            </div>
          </div>
        )}
        <Select
          label="Payment Mode"
          options={TOKEN_PAYMENT_MODES.map((mode) => ({ value: mode, label: mode }))}
          value={form.payment_mode}
          onChange={(e) => setForm({ ...form, payment_mode: e.target.value })}
        />
        <Input
          label="Book Price"
          required
          type="number"
          min={0.01}
          step="0.01"
          value={form.book_price}
          onChange={(e) => setForm({ ...form, book_price: e.target.value })}
          error={errors.book_price}
        />
        <Input
          label="Amount Paid"
          required
          type="number"
          min={0}
          step="0.01"
          value={form.amount_paid}
          onChange={(e) => setForm({ ...form, amount_paid: e.target.value })}
          error={errors.amount_paid}
        />
        <Textarea
          label="Remarks"
          value={form.remarks}
          onChange={(e) => setForm({ ...form, remarks: e.target.value })}
        />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/token-book-payments")}>
            Cancel
          </Button>
          <Button type="submit" loading={createPayment.isPending || updatePayment.isPending}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}
