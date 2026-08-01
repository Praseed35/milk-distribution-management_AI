import { useState, type FormEvent, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import Textarea from "../../components/ui/Textarea";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import ConfirmDialog from "../../components/ui/ConfirmDialog";
import { useAuth } from "../../providers/AuthProvider";
import { DELIVERY_STATUS } from "../../lib/constants";
import { formatCurrency, formatDateTime } from "../../lib/utils";
import {
  useCloseSession,
  useCompleteSession,
  useDeliverySession,
  useReconciliation,
  useSessionChecklist,
  useSessionReport,
  useStartSession,
  useSubmitReconciliation,
  useValidateReconciliation,
  useAddCashSale,
  useRemoveCashSale,
} from "../../hooks/useDeliverySessions";
import {
  useAddUnplannedDelivery,
  useEditHistory,
  useRegisterToken,
  useReopenSession,
  useSessionDeliveries,
  useUpdateDelivery,
  useValidateToken,
} from "../../hooks/useDeliveries";
import { useRoutes } from "../../hooks/useRoutes";
import { useEmployees } from "../../hooks/useEmployees";
import { useMilkTypes } from "../../hooks/useMilkTypes";
import { useCustomers } from "../../hooks/useCustomers";
import type {
  ChecklistCustomer,
  DailyDeliveryResponse,
  SessionEditResponse,
  TokenValidationResponse,
} from "../../types/delivery";

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-lg font-semibold text-slate-800 mb-4">{title}</h2>
      {children}
    </section>
  );
}

function TokenRegisterModal({
  delivery,
  sessionId,
  onClose,
}: {
  delivery: DailyDeliveryResponse;
  sessionId: number;
  onClose: () => void;
}) {
  const [sheet, setSheet] = useState("");
  const [validation, setValidation] = useState<TokenValidationResponse | null>(null);
  const [ack, setAck] = useState(false);
  const [ackReason, setAckReason] = useState("");
  const validateToken = useValidateToken();
  const registerToken = useRegisterToken();

  async function handleValidate() {
    if (!sheet || Number(sheet) <= 0) return;
    try {
      const res = await validateToken.mutateAsync({
        customer_id: delivery.customer_id,
        milk_type_id: delivery.milk_type_id,
        sheet_number: Number(sheet),
      });
      setValidation(res);
    } catch {}
  }

  async function handleRegister() {
    if (!validation) return;
    try {
      await registerToken.mutateAsync({
        id: delivery.id,
        sessionId,
        data: {
          token_sheet_number: Number(sheet),
          acknowledged_warnings: validation.requires_acknowledgment ? validation.warnings.map((w) => w.code) : [],
          acknowledgment_reason: ackReason || null,
        },
      });
      onClose();
    } catch {}
  }

  const needsAck = validation?.requires_acknowledgment ?? false;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-2">Register Token Sheet</h3>
        <p className="text-sm text-slate-600 mb-4">
          Customer: {delivery.customer_name || `#${delivery.customer_id}`}
        </p>
        <div className="space-y-4">
          <Input
            label="Sheet Number"
            type="number"
            required
            min={1}
            value={sheet}
            onChange={(e) => {
              setSheet(e.target.value);
              setValidation(null);
            }}
            error={validation && !validation.is_valid && validation.requires_acknowledgment ? undefined : undefined}
          />
          <div className="flex gap-3">
            <Button variant="secondary" onClick={handleValidate} loading={validateToken.isPending}>
              Validate
            </Button>
            {validation && (
              <Button onClick={handleRegister} disabled={needsAck && !ack} loading={registerToken.isPending}>
                Register
              </Button>
            )}
          </div>
          {validation && !needsAck && (
            <p className="text-sm text-emerald-600">Token sheet valid — ready to register.</p>
          )}
          {needsAck && (
            <div className="bg-amber-50 border border-amber-200 rounded-md p-4 space-y-3">
              <p className="text-sm font-medium text-amber-800">Warnings require acknowledgment</p>
              <ul className="text-sm text-amber-800 space-y-1">
                {(validation?.warnings || []).map((w) => (
                  <li key={w.code}>
                    <strong>{w.code}</strong> — {w.message}
                  </li>
                ))}
              </ul>
              <label className="flex items-start gap-2 text-sm text-slate-700">
                <input type="checkbox" checked={ack} onChange={(e) => setAck(e.target.checked)} className="mt-1" />
                I acknowledge these warnings and want to proceed.
              </label>
              <Textarea
                label="Acknowledgment Reason (optional)"
                value={ackReason}
                onChange={(e) => setAckReason(e.target.value)}
              />
            </div>
          )}
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={onClose}>Close</Button>
        </div>
      </div>
    </div>
  );
}

function UnplannedForm({ sessionId }: { sessionId: number }) {
  const { data: milkTypes } = useMilkTypes();
  const { data: customers } = useCustomers();
  const addUnplanned = useAddUnplannedDelivery();
  const addCashSale = useAddCashSale();

  const [form, setForm] = useState({
    mode: "existing" as "existing" | "walkin",
    customer_id: "",
    walkin_name: "",
    walkin_phone: "",
    milk_type_id: "",
    quantity: "",
    delivery_status: "DELIVERED",
    registration_method: "TOKEN_SHEET",
    token_sheet_number: "",
    amount: "",
    reason: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  function validate() {
    const e: Record<string, string> = {};
    if (form.mode === "walkin") {
      if (!form.walkin_name) e.walkin_name = "Name is required";
      if (!form.walkin_phone || form.walkin_phone.length !== 10) e.walkin_phone = "Phone must be 10 digits";
    } else if (!form.customer_id) {
      e.customer_id = "Customer is required";
    }
    if (!form.milk_type_id) e.milk_type_id = "Milk type is required";
    if (!form.quantity || Number(form.quantity) <= 0) e.quantity = "Quantity must be greater than 0";
    if (form.registration_method === "TOKEN_SHEET" && !form.token_sheet_number) e.token_sheet_number = "Token sheet is required";
    if (form.delivery_status === "CASH_SALE" && (!form.amount || Number(form.amount) <= 0)) e.amount = "Amount must be greater than 0";
    if (!form.reason) e.reason = "Reason is required";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      if (form.mode === "walkin") {
        await addCashSale.mutateAsync({
          id: sessionId,
          params: {
            customer_name: form.walkin_name,
            customer_phone: form.walkin_phone,
            milk_type_id: Number(form.milk_type_id),
            quantity: Number(form.quantity),
            amount: Number(form.amount),
          },
        });
      } else {
        await addUnplanned.mutateAsync({
          session_id: sessionId,
          customer_id: Number(form.customer_id),
          milk_type_id: Number(form.milk_type_id),
          delivered_quantity: Number(form.quantity),
          delivery_status: form.delivery_status,
          registration_method: form.registration_method as "TOKEN_SHEET" | "CASH" | "PENDING",
          token_sheet_number: form.token_sheet_number ? Number(form.token_sheet_number) : null,
          reason: form.reason,
        });
      }
      setForm({
        mode: "existing", customer_id: "", walkin_name: "", walkin_phone: "",
        milk_type_id: "", quantity: "", delivery_status: "DELIVERED",
        registration_method: "TOKEN_SHEET", token_sheet_number: "", amount: "", reason: "",
      });
      setErrors({});
    } catch {}
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 border-t border-slate-200 pt-4">
      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Customer Type"
          options={[
            { value: "existing", label: "Existing customer" },
            { value: "walkin", label: "Walk-in (cash)" },
          ]}
          value={form.mode}
          onChange={(e) => setForm({ ...form, mode: e.target.value as "existing" | "walkin" })}
        />
        {form.mode === "existing" ? (
          <Select
            label="Customer"
            required
            options={(customers || []).map((c) => ({ value: c.id, label: `${c.customer_name} (${c.primary_phone})` }))}
            placeholder="Select a customer"
            value={form.customer_id}
            onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
            error={errors.customer_id}
          />
        ) : (
          <>
            <Input label="Name" required value={form.walkin_name} onChange={(e) => setForm({ ...form, walkin_name: e.target.value })} error={errors.walkin_name} />
            <Input label="Phone" required value={form.walkin_phone} onChange={(e) => setForm({ ...form, walkin_phone: e.target.value })} error={errors.walkin_phone} />
          </>
        )}
      </div>
      <div className="grid grid-cols-3 gap-4">
        <Select
          label="Milk Type"
          required
          options={(milkTypes || []).map((m) => ({ value: m.id, label: `${m.milk_name} (${m.volume_ml}ml)` }))}
          placeholder="Select milk type"
          value={form.milk_type_id}
          onChange={(e) => setForm({ ...form, milk_type_id: e.target.value })}
          error={errors.milk_type_id}
        />
        <Input label="Quantity (L)" type="number" required min={0} value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} error={errors.quantity} />
        <Select
          label="Delivery Status"
          required
          options={DELIVERY_STATUS_OPTIONS.filter((o) => o.value !== "NOT_DELIVERED" && o.value !== "CANCELLED")}
          value={form.delivery_status}
          onChange={(e) => setForm({ ...form, delivery_status: e.target.value })}
        />
      </div>
      <div className="grid grid-cols-3 gap-4">
        <Select
          label="Registration Method"
          required
          options={[
            { value: "TOKEN_SHEET", label: "Token Sheet" },
            { value: "CASH", label: "Cash" },
            { value: "PENDING", label: "Pending" },
          ]}
          value={form.registration_method}
          onChange={(e) => setForm({ ...form, registration_method: e.target.value })}
        />
        {form.registration_method === "TOKEN_SHEET" && (
          <Input label="Token Sheet #" type="number" min={1} required value={form.token_sheet_number} onChange={(e) => setForm({ ...form, token_sheet_number: e.target.value })} error={errors.token_sheet_number} />
        )}
        {form.delivery_status === "CASH_SALE" && (
          <Input label="Amount (Rs)" type="number" min={0} required value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} error={errors.amount} />
        )}
      </div>
      <Textarea label="Reason" required value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} error={errors.reason} />
      <div className="flex justify-end">
        <Button type="submit" loading={addUnplanned.isPending || addCashSale.isPending}>Add Delivery</Button>
      </div>
    </form>
  );
}

function CashSalesSection({ sessionId, canEdit }: { sessionId: number; canEdit: boolean }) {
  const { data: milkTypes } = useMilkTypes();
  const { data: deliveriesData } = useSessionDeliveries(sessionId);
  const addCashSale = useAddCashSale();
  const removeCashSale = useRemoveCashSale();

  const [form, setForm] = useState({ customer_name: "", customer_phone: "", milk_type_id: "", quantity: "", amount: "" });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [removeId, setRemoveId] = useState<number | null>(null);

  const cashSales = (deliveriesData?.deliveries || []).filter((d) => d.delivery_status === "CASH_SALE");
  const milkNames = new Map((milkTypes || []).map((m) => [m.id, m.milk_name]));

  function validate() {
    const e: Record<string, string> = {};
    if (!form.customer_name) e.customer_name = "Name is required";
    if (form.customer_phone && form.customer_phone.length !== 10) e.customer_phone = "Phone must be 10 digits";
    if (!form.milk_type_id) e.milk_type_id = "Milk type is required";
    if (!form.quantity || Number(form.quantity) <= 0) e.quantity = "Quantity must be greater than 0";
    if (!form.amount || Number(form.amount) <= 0) e.amount = "Amount must be greater than 0";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      await addCashSale.mutateAsync({
        id: sessionId,
        params: {
          customer_name: form.customer_name,
          customer_phone: form.customer_phone || null,
          milk_type_id: Number(form.milk_type_id),
          quantity: Number(form.quantity),
          amount: Number(form.amount),
        },
      });
      setForm({ customer_name: "", customer_phone: "", milk_type_id: "", quantity: "", amount: "" });
      setErrors({});
    } catch {}
  }

  return (
    <div className="space-y-4">
      {canEdit && (
        <form onSubmit={handleSubmit} className="grid grid-cols-2 md:grid-cols-6 gap-4 items-end">
          <Input label="Customer Name" required value={form.customer_name} onChange={(e) => setForm({ ...form, customer_name: e.target.value })} error={errors.customer_name} />
          <Input label="Phone" value={form.customer_phone} onChange={(e) => setForm({ ...form, customer_phone: e.target.value })} error={errors.customer_phone} />
          <Select
            label="Milk Type"
            required
            options={(milkTypes || []).map((m) => ({ value: m.id, label: m.milk_name }))}
            placeholder="Milk type"
            value={form.milk_type_id}
            onChange={(e) => setForm({ ...form, milk_type_id: e.target.value })}
            error={errors.milk_type_id}
          />
          <Input label="Quantity (L)" type="number" min={0} required value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} error={errors.quantity} />
          <Input label="Amount (Rs)" type="number" min={0} required value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} error={errors.amount} />
          <Button type="submit" loading={addCashSale.isPending}>Add</Button>
        </form>
      )}
      {cashSales.length === 0 ? (
        <p className="text-sm text-slate-500">No cash sales recorded.</p>
      ) : (
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-4 py-2 text-left font-medium text-slate-600">Name</th>
              <th className="px-4 py-2 text-left font-medium text-slate-600">Milk Type</th>
              <th className="px-4 py-2 text-left font-medium text-slate-600">Qty (L)</th>
              <th className="px-4 py-2 text-left font-medium text-slate-600">Amount</th>
              {canEdit && <th className="px-4 py-2 text-left font-medium text-slate-600">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {cashSales.map((cs) => (
              <tr key={cs.id}>
                <td className="px-4 py-2 text-slate-700">{cs.customer_name || "Cash Customer"}</td>
                <td className="px-4 py-2 text-slate-700">{cs.milk_type_name || milkNames.get(cs.milk_type_id) || "—"}</td>
                <td className="px-4 py-2 text-slate-700">{cs.delivered_quantity}</td>
                <td className="px-4 py-2 text-slate-700">{cs.cash_amount ? formatCurrency(Number(cs.cash_amount)) : "—"}</td>
                {canEdit && (
                  <td className="px-4 py-2">
                    <button onClick={() => setRemoveId(cs.id)} className="text-red-600 hover:text-red-800 text-sm">Remove</button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <ConfirmDialog
        open={removeId !== null}
        title="Remove Cash Sale"
        message="Are you sure you want to remove this cash sale?"
        variant="danger"
        loading={removeCashSale.isPending}
        onConfirm={() => {
          if (removeId) removeCashSale.mutate({ id: sessionId, cashSaleId: removeId }, { onSettled: () => setRemoveId(null) });
        }}
        onCancel={() => setRemoveId(null)}
      />
    </div>
  );
}

function EditHistorySection({ history }: { history: SessionEditResponse[] }) {
  if (!history.length) return <p className="text-sm text-slate-500">No edit history yet.</p>;
  return (
    <ul className="space-y-3">
      {history.map((h) => (
        <li key={h.edit_id} className="border border-slate-200 rounded-md p-3 text-sm">
          <div className="flex justify-between items-start gap-4">
            <div>
              <span className="font-medium text-slate-800">{h.edit_type}</span>
              {h.customer_name && <span className="text-slate-600"> — {h.customer_name}</span>}
            </div>
            <span className="text-xs text-slate-400">{h.edited_at ? formatDateTime(h.edited_at) : ""}</span>
          </div>
          <p className="text-slate-600 mt-1">
            From <code className="text-slate-800">{JSON.stringify(h.old_value)}</code> to{" "}
            <code className="text-slate-800">{JSON.stringify(h.new_value)}</code>
          </p>
          {h.reason && <p className="text-slate-500 mt-1">Reason: {h.reason}</p>}
          {h.edited_by && <p className="text-xs text-slate-400 mt-1">Edited by {h.edited_by}</p>}
        </li>
      ))}
    </ul>
  );
}

const DELIVERY_STATUS_OPTIONS = Object.entries(DELIVERY_STATUS).map(([value, meta]) => ({ value, label: meta.label }));

export default function SessionDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const sessionId = Number(id);
  const { user } = useAuth();
  const isOwner = user?.role === "OWNER";

  const { data: routes } = useRoutes();
  const { data: employees } = useEmployees();
  const { data: milkTypes } = useMilkTypes();

  const { data: session, isLoading, error } = useDeliverySession(sessionId);
  const { data: checklist } = useSessionChecklist(sessionId);
  const { data: reconciliation } = useReconciliation(sessionId);
  const { data: deliveriesData } = useSessionDeliveries(sessionId);
  const { data: report } = useSessionReport(sessionId);
  const { data: editHistory } = useEditHistory(sessionId);

  const startSession = useStartSession();
  const completeSession = useCompleteSession();
  const closeSession = useCloseSession();
  const updateDelivery = useUpdateDelivery();
  const validateReconciliation = useValidateReconciliation();
  const submitReconciliation = useSubmitReconciliation();
  const reopenSession = useReopenSession();

  const [loaded, setLoaded] = useState("");
  const [dispatchOpen, setDispatchOpen] = useState(false);
  const [completeOpen, setCompleteOpen] = useState(false);
  const [closeOpen, setCloseOpen] = useState(false);
  const [reopenOpen, setReopenOpen] = useState(false);
  const [reopenReason, setReopenReason] = useState("");
  const [tokenDelivery, setTokenDelivery] = useState<DailyDeliveryResponse | null>(null);
  const [cashInputs, setCashInputs] = useState<Record<number, string>>({});
  const [pendingCashId, setPendingCashId] = useState<number | null>(null);
  const [returnedMilk, setReturnedMilk] = useState("");
  const [totalCash, setTotalCash] = useState("");
  const [remarks, setRemarks] = useState("");
  const [validationIssues, setValidationIssues] = useState<{ code: string; message: string; severity: string }[] | null>(null);

  const routeNames = new Map((routes || []).map((r) => [r.id, r.route_name]));
  const partnerNames = new Map((employees || []).map((e) => [e.id, e.name]));
  const milkNames = new Map((milkTypes || []).map((m) => [m.id, m.milk_name]));
  const checklistByCustomer = new Map<number, ChecklistCustomer>((checklist?.customers || []).map((c) => [c.customer_id, c]));

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error || !session) return <EmptyState message="Session not found" />;

  const deliveries = deliveriesData?.deliveries || [];
  const cashSales = deliveries.filter((d) => d.delivery_status === "CASH_SALE");
  const computedCashTotal = cashSales.reduce((sum, d) => sum + Number(d.cash_amount || 0), 0);
  const canEdit = session.status === "STARTED" || session.status === "COMPLETED";
  const isClosed = session.status === "CLOSED";

  function handleStatusChange(d: DailyDeliveryResponse, status: string) {
    if (status === "CASH_SALE") {
      setPendingCashId(d.id);
      return;
    }
    const data: Record<string, unknown> = { delivery_status: status, version: d.version };
    if (status === "DELIVERED") data.delivered_quantity = d.planned_quantity;
    if (status === "NOT_DELIVERED" || status === "CANCELLED") data.delivered_quantity = 0;
    updateDelivery.mutate({ id: d.id, sessionId, data: data as any });
  }

  function handleSaveCash(d: DailyDeliveryResponse) {
    const amount = cashInputs[d.id];
    if (!amount || Number(amount) <= 0) return;
    updateDelivery.mutate(
      { id: d.id, sessionId, data: { delivery_status: "CASH_SALE", cash_amount: Number(amount), delivered_quantity: d.planned_quantity, version: d.version } as any },
      { onSettled: () => setPendingCashId(null) }
    );
  }

  async function handleValidate() {
    try {
      const res = await validateReconciliation.mutateAsync(sessionId);
      setValidationIssues(res.issues || []);
    } catch {}
  }

  async function handleSubmitReconciliation() {
    try {
      await submitReconciliation.mutateAsync({
        id: sessionId,
        params: {
          total_cash_collected: Number(totalCash || computedCashTotal || 0),
          cash_sales: cashSales.map((d) => ({ id: d.id, amount: Number(d.cash_amount || 0), quantity: d.delivered_quantity })),
          returned_milk: Number(returnedMilk || 0),
          returned_reasons: [],
          token_sheets_collected: [],
          remarks: remarks || undefined,
        },
      });
    } catch {}
  }

  function handleReopen() {
    if (!reopenReason.trim()) return;
    reopenSession.mutate({ id: sessionId, reason: reopenReason }, { onSettled: () => { setReopenOpen(false); setReopenReason(""); } });
  }

  const partnerName = session.delivery_partner_name || partnerNames.get(session.delivery_partner_id) || "—";

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-slate-800">
            {session.route_name || routeNames.get(session.route_id) || `Route #${session.route_id}`}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            {formatDateTime(session.delivery_date)} · {session.shift} · Partner: {partnerName}
            {session.reopen_count > 0 && <span className="ml-2 text-amber-600">Reopened {session.reopen_count}x</span>}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge status={session.status} />
          <Button variant="secondary" onClick={() => navigate("/delivery/sessions")}>Back</Button>
          {isOwner && (session.status === "COMPLETED" || session.status === "CLOSED") && (
            <Button variant="secondary" onClick={() => navigate(`/delivery/sessions/${sessionId}/edit`)}>Edit Deliveries</Button>
          )}
          {isOwner && isClosed && (
            <Button variant="secondary" onClick={() => setReopenOpen(true)}>Reopen</Button>
          )}
        </div>
      </div>

      {!isClosed && session.status === "PLANNED" && (
        <Section title="Dispatch">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <Input label="Total Milk Loaded (L)" type="number" min={0} required value={loaded} onChange={(e) => setLoaded(e.target.value)} />
            <Button onClick={() => setDispatchOpen(true)}>Record Dispatch</Button>
          </div>
        </Section>
      )}

      <Section title="Checklist & Registration">
        {deliveries.length === 0 ? (
          <EmptyState message="No deliveries for this session yet." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Customer</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Phone</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Milk Type</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Planned (L)</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Status</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Token Sheet</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {deliveries.map((d) => {
                  const checklistCustomer = checklistByCustomer.get(d.customer_id);
                  const customerName = d.customer_name || checklistCustomer?.customer_name || `Customer #${d.customer_id}`;
                  const phone = checklistCustomer?.phone || "—";
                  const milkTypeName = d.milk_type_name || milkNames.get(d.milk_type_id) || "—";
                  const isRegistered = d.delivery_status !== "PLANNED";
                  return (
                    <tr key={d.id}>
                      <td className="px-4 py-2 text-slate-700">{customerName}</td>
                      <td className="px-4 py-2 text-slate-700">{phone}</td>
                      <td className="px-4 py-2 text-slate-700">{milkTypeName}</td>
                      <td className="px-4 py-2 text-slate-700">{d.planned_quantity}</td>
                      <td className="px-4 py-2">
                        {isRegistered ? <Badge status={d.delivery_status} /> : <span className="text-xs text-slate-400">Unregistered</span>}
                      </td>
                      <td className="px-4 py-2 text-slate-700">{d.token_sheet_number || "—"}</td>
                      <td className="px-4 py-2">
                        {canEdit && (
                          <div className="flex flex-wrap gap-2 items-center">
                            <Select
                              options={DELIVERY_STATUS_OPTIONS}
                              value={d.delivery_status === "PLANNED" ? "" : d.delivery_status}
                              placeholder="Set status"
                              onChange={(e) => handleStatusChange(d, e.target.value)}
                              className="w-40"
                            />
                            {pendingCashId === d.id && (
                              <div className="flex gap-2 items-center">
                                <Input type="number" min={0} placeholder="Amount" className="w-28" value={cashInputs[d.id] || ""} onChange={(e) => setCashInputs({ ...cashInputs, [d.id]: e.target.value })} />
                                <Button size="sm" onClick={() => handleSaveCash(d)} loading={updateDelivery.isPending}>Save</Button>
                              </div>
                            )}
                            {d.delivery_status === "DELIVERED" || d.delivery_status === "PENDING_TOKEN" ? (
                              <Button size="sm" variant="secondary" onClick={() => setTokenDelivery(d)}>
                                {d.token_sheet_number ? "Change Sheet" : "Register Sheet"}
                              </Button>
                            ) : null}
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        {canEdit && (
          <div className="mt-6">
            <h3 className="text-md font-medium text-slate-800 mb-3">Add Unplanned Delivery</h3>
            <UnplannedForm sessionId={sessionId} />
          </div>
        )}
      </Section>

      {session.status !== "PLANNED" && (
        <Section title="Reconciliation">
          {reconciliation && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <StatCard label="Loaded Milk" value={`${Number(reconciliation.loaded_milk).toFixed(2)} L`} />
              <StatCard label="Token Registered" value={`${Number(reconciliation.token_registered).toFixed(2)} L`} />
              <StatCard label="Cash Sales" value={`${Number(reconciliation.cash_sales).toFixed(2)} L`} />
              <StatCard label="Returned Milk" value={`${Number(reconciliation.returned_milk).toFixed(2)} L`} />
              <StatCard label="Total Accounted" value={`${Number(reconciliation.total_accounted).toFixed(2)} L`} />
              <StatCard label="Difference" value={`${Number(reconciliation.difference).toFixed(2)} L`} />
              <div className="bg-slate-50 rounded-lg p-4">
                <p className="text-sm text-slate-500">Balance Status</p>
                <div className="mt-1"><Badge status={reconciliation.status} /></div>
              </div>
            </div>
          )}
          {validationIssues && validationIssues.length > 0 && (
            <div className="mb-6 space-y-2">
              {validationIssues.map((issue) => (
                <div
                  key={issue.code}
                  className={
                    issue.severity === "ERROR"
                      ? "bg-red-50 border border-red-200 text-red-800 rounded-md p-3 text-sm"
                      : "bg-amber-50 border border-amber-200 text-amber-800 rounded-md p-3 text-sm"
                  }
                >
                  <strong>{issue.code}</strong> — {issue.message}
                </div>
              ))}
            </div>
          )}
          {canEdit && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Input label="Returned Milk (L)" type="number" min={0} value={returnedMilk} onChange={(e) => setReturnedMilk(e.target.value)} />
                <Input label="Total Cash Collected (Rs)" type="number" min={0} value={totalCash} placeholder={String(computedCashTotal || "")} onChange={(e) => setTotalCash(e.target.value)} />
                <Input label="Remarks" value={remarks} onChange={(e) => setRemarks(e.target.value)} />
              </div>
              <div className="flex gap-3">
                <Button variant="secondary" onClick={handleValidate} loading={validateReconciliation.isPending}>Validate</Button>
                <Button onClick={handleSubmitReconciliation} loading={submitReconciliation.isPending}>Submit Reconciliation</Button>
              </div>
            </div>
          )}
        </Section>
      )}

      {session.status !== "PLANNED" && (
        <Section title="Cash Sales">
          <CashSalesSection sessionId={sessionId} canEdit={canEdit} />
        </Section>
      )}

      {session.status === "STARTED" && (
        <Section title="Complete Session">
          <p className="text-sm text-slate-600 mb-4">
            Mark this session as completed before it can be closed. You can still register deliveries after completing.
          </p>
          <Button onClick={() => setCompleteOpen(true)}>Complete Session</Button>
        </Section>
      )}

      {session.status === "COMPLETED" && (
        <Section title="Close Session">
          <p className="text-sm text-slate-600 mb-4">
            The session will be closed only if reconciliation is balanced. Any difference will be shown on failure.
          </p>
          <Button onClick={() => setCloseOpen(true)}>Close Session</Button>
        </Section>
      )}

      {isClosed && (
        <Section title="Session Summary">
          {report ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <StatCard label="Total Customers" value={String(report.summary.total_customers)} />
              <StatCard label="Delivered" value={String(report.summary.delivered)} />
              <StatCard label="Pending Token" value={String(report.summary.pending_token)} />
              <StatCard label="Cash Sales" value={String(report.summary.cash_sale)} />
              <StatCard label="Not Delivered" value={String(report.summary.not_delivered)} />
              <StatCard label="Loaded Milk" value={`${Number(report.milk_summary.loaded).toFixed(2)} L`} />
              <StatCard label="Token Registered" value={`${Number(report.milk_summary.token_registered).toFixed(2)} L`} />
              <StatCard label="Cash (Rs)" value={formatCurrency(Number(report.milk_summary.cash_sales))} />
              <StatCard label="Returned" value={`${Number(report.milk_summary.returned).toFixed(2)} L`} />
            </div>
          ) : (
            <p className="text-sm text-slate-500">No report available.</p>
          )}
        </Section>
      )}

      {isOwner && (
        <Section title="Edit History">
          <EditHistorySection history={editHistory || []} />
        </Section>
      )}

      <ConfirmDialog
        open={dispatchOpen}
        title="Record Dispatch"
        message="This records the total milk loaded and starts the session. This cannot be changed after dispatch."
        loading={startSession.isPending}
        onConfirm={() => {
          if (!loaded || Number(loaded) <= 0) return;
          startSession.mutate({ id: sessionId, total: Number(loaded) }, { onSettled: () => setDispatchOpen(false) });
        }}
        onCancel={() => setDispatchOpen(false)}
      />
      <ConfirmDialog
        open={completeOpen}
        title="Complete Session"
        message="Are you sure you want to complete this session?"
        loading={completeSession.isPending}
        onConfirm={() => completeSession.mutate(sessionId, { onSettled: () => setCompleteOpen(false) })}
        onCancel={() => setCompleteOpen(false)}
      />
      <ConfirmDialog
        open={closeOpen}
        title="Close Session"
        message="The session will be closed only if reconciliation is balanced. Continue?"
        variant="danger"
        loading={closeSession.isPending}
        onConfirm={() => closeSession.mutate(sessionId, { onSettled: () => setCloseOpen(false) })}
        onCancel={() => setCloseOpen(false)}
      />
      <ConfirmDialog
        open={reopenOpen}
        title="Reopen Session"
        message="You are reopening a closed session. A reason is required and the edit will be logged."
        loading={reopenSession.isPending}
        onConfirm={handleReopen}
        onCancel={() => setReopenOpen(false)}
      >
        <div className="mb-4">
          <Textarea label="Reason" required value={reopenReason} onChange={(e) => setReopenReason(e.target.value)} />
        </div>
      </ConfirmDialog>

      {tokenDelivery && <TokenRegisterModal delivery={tokenDelivery} sessionId={sessionId} onClose={() => setTokenDelivery(null)} />}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-50 rounded-lg p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-lg font-semibold text-slate-800 mt-1">{value}</p>
    </div>
  );
}
