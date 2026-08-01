import { useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import Select from "../../components/ui/Select";
import Textarea from "../../components/ui/Textarea";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useDeliverySession, useSessionChecklist } from "../../hooks/useDeliverySessions";
import { useEditDelivery, useEditHistory, useSessionDeliveries } from "../../hooks/useDeliveries";
import { useRoutes } from "../../hooks/useRoutes";
import { useEmployees } from "../../hooks/useEmployees";
import { useMilkTypes } from "../../hooks/useMilkTypes";
import { DELIVERY_STATUS } from "../../lib/constants";
import { formatDateTime } from "../../lib/utils";
import type { DailyDeliveryEditResponse, DailyDeliveryResponse } from "../../types/delivery";

const DELIVERY_STATUS_OPTIONS = Object.entries(DELIVERY_STATUS).map(([value, meta]) => ({ value, label: meta.label }));

export default function DeliveryEditPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const sessionId = Number(id);

  const { data: session, isLoading: sessionLoading, error } = useDeliverySession(sessionId);
  const { data: deliveriesData, isLoading: deliveriesLoading } = useSessionDeliveries(sessionId);
  const { data: checklist } = useSessionChecklist(sessionId);
  const { data: routes } = useRoutes();
  const { data: employees } = useEmployees();
  const { data: milkTypes } = useMilkTypes();
  const { data: editHistory, refetch: refetchHistory } = useEditHistory(sessionId);

  const editDelivery = useEditDelivery();

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [status, setStatus] = useState("");
  const [returnSheet, setReturnSheet] = useState(false);
  const [reason, setReason] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [result, setResult] = useState<DailyDeliveryEditResponse | null>(null);

  const routeNames = new Map((routes || []).map((r) => [r.id, r.route_name]));
  const partnerNames = new Map((employees || []).map((e) => [e.id, e.name]));
  const milkNames = new Map((milkTypes || []).map((m) => [m.id, m.milk_name]));
  const checklistByCustomer = new Map((checklist?.customers || []).map((c) => [c.customer_id, c]));

  if (sessionLoading) return <LoadingSpinner className="mt-20" />;
  if (error || !session) return <EmptyState message="Session not found" />;

  if (session.status !== "COMPLETED" && session.status !== "CLOSED") {
    return <EmptyState message="Deliveries can only be edited after the session is completed or closed." />;
  }

  const deliveries = deliveriesData?.deliveries || [];
  const selected = selectedId !== null ? deliveries.find((d) => d.id === selectedId) : null;

  function selectDelivery(d: DailyDeliveryResponse) {
    setSelectedId(d.id);
    setStatus(d.delivery_status === "PLANNED" ? "" : d.delivery_status);
    setReturnSheet(false);
    setReason("");
    setErrors({});
    setResult(null);
  }

  function validate() {
    const e: Record<string, string> = {};
    if (!selected) {
      e.selected = "Select a delivery first";
    } else {
      if (!status) e.status = "Status is required";
      if (!reason.trim()) e.reason = "Reason is required";
      else if (reason.trim().length > 500) e.reason = "Reason must be at most 500 characters";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!selected || !validate()) return;
    try {
      const res = await editDelivery.mutateAsync({
        id: selected.id,
        sessionId,
        data: {
          delivery_status: status,
          return_token_sheet: returnSheet,
          reason: reason.trim(),
          version: selected.version,
        },
      });
      setResult(res);
      setReason("");
      setReturnSheet(false);
      refetchHistory();
    } catch {}
  }

  const partnerName = session.delivery_partner_name || partnerNames.get(session.delivery_partner_id) || "—";

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-slate-800">Edit Deliveries</h1>
          <p className="text-sm text-slate-500 mt-1">
            {session.route_name || routeNames.get(session.route_id) || `Route #${session.route_id}`} ·{" "}
            {formatDateTime(session.delivery_date)} · {session.shift} · Partner: {partnerName}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge status={session.status} />
          <Button variant="secondary" onClick={() => navigate(`/delivery/sessions/${sessionId}`)}>Back</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Select Delivery</h2>
          {deliveriesLoading ? (
            <LoadingSpinner />
          ) : deliveries.length === 0 ? (
            <EmptyState message="No deliveries for this session." />
          ) : (
            <div className="overflow-x-auto max-h-[32rem] overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 border-b border-slate-200 sticky top-0">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium text-slate-600">Customer</th>
                    <th className="px-4 py-2 text-left font-medium text-slate-600">Milk</th>
                    <th className="px-4 py-2 text-left font-medium text-slate-600">Status</th>
                    <th className="px-4 py-2 text-left font-medium text-slate-600">Sheet</th>
                    <th className="px-4 py-2 text-left font-medium text-slate-600">Version</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {deliveries.map((d) => {
                    const checklistCustomer = checklistByCustomer.get(d.customer_id);
                    const customerName = d.customer_name || checklistCustomer?.customer_name || `Customer #${d.customer_id}`;
                    const isSelected = d.id === selectedId;
                    return (
                      <tr
                        key={d.id}
                        onClick={() => selectDelivery(d)}
                        className={`cursor-pointer ${isSelected ? "bg-indigo-50" : "hover:bg-slate-50"}`}
                      >
                        <td className="px-4 py-2 text-slate-700">{customerName}</td>
                        <td className="px-4 py-2 text-slate-700">{d.milk_type_name || milkNames.get(d.milk_type_id) || "—"}</td>
                        <td className="px-4 py-2">
                          {d.delivery_status === "PLANNED" ? (
                            <span className="text-xs text-slate-400">Unregistered</span>
                          ) : (
                            <Badge status={d.delivery_status} />
                          )}
                        </td>
                        <td className="px-4 py-2 text-slate-700">{d.token_sheet_number || "—"}</td>
                        <td className="px-4 py-2 text-slate-700">{d.version}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Change Status</h2>
          {!selected ? (
            <p className="text-sm text-slate-500">Select a delivery on the left to edit it.</p>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="bg-slate-50 rounded-md p-3 text-sm text-slate-700">
                Editing delivery for{" "}
                <span className="font-medium">
                  {selected.customer_name ||
                    checklistByCustomer.get(selected.customer_id)?.customer_name ||
                    `Customer #${selected.customer_id}`}
                </span>{" "}
                — current status: {selected.delivery_status}
                {selected.token_sheet_number ? ` (sheet #${selected.token_sheet_number})` : ""}.
              </div>
              <Select
                label="New Status"
                required
                options={DELIVERY_STATUS_OPTIONS}
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                error={errors.status}
              />
              {selected.token_sheet_number && (
                <label className="flex items-start gap-2 text-sm text-slate-700">
                  <input
                    type="checkbox"
                    checked={returnSheet}
                    onChange={(e) => setReturnSheet(e.target.checked)}
                    className="mt-1"
                  />
                  Return token sheet (decrements the book's current sheet and clears this delivery's sheet)
                </label>
              )}
              <Textarea
                label="Reason"
                required
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                error={errors.reason}
                placeholder="Required (1-500 characters)"
              />
              {result && (
                <div className="bg-emerald-50 border border-emerald-200 rounded-md p-3 text-sm text-emerald-800 space-y-1">
                  <p>
                    <strong>Updated:</strong> {result.old_status} → {result.new_status}
                  </p>
                  {result.token_sheet_returned && (
                    <p>
                      Token sheet #<strong>{result.sheet_number}</strong> returned from book #{result.token_book_issue_id}{" "}
                      (new current sheet: {result.new_current_sheet}).
                    </p>
                  )}
                </div>
              )}
              <div className="flex justify-end gap-3">
                <Button type="submit" loading={editDelivery.isPending}>Save Change</Button>
              </div>
            </form>
          )}

          <h3 className="text-md font-medium text-slate-800 mt-8 mb-3">Recent Edit History</h3>
          {!editHistory || editHistory.length === 0 ? (
            <p className="text-sm text-slate-500">No edits logged yet.</p>
          ) : (
            <ul className="space-y-2">
              {editHistory.slice(0, 10).map((h) => (
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
          )}
        </section>
      </div>
    </div>
  );
}
