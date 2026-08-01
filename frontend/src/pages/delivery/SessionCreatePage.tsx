import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import { SHIFTS } from "../../lib/constants";
import { useCreateSession } from "../../hooks/useDeliverySessions";
import { useRoutes } from "../../hooks/useRoutes";
import { useEmployees } from "../../hooks/useEmployees";

export default function SessionCreatePage() {
  const navigate = useNavigate();
  const { data: routes } = useRoutes();
  const { data: employees } = useEmployees();
  const createSession = useCreateSession();

  const [form, setForm] = useState({
    route_id: "",
    delivery_date: "",
    shift: "MORNING",
    delivery_partner_id: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const partnerOptions = employees?.filter((e) => e.role === "DELIVERY_PARTNER");
  const partnerList = partnerOptions && partnerOptions.length > 0 ? partnerOptions : employees || [];

  function validate() {
    const e: Record<string, string> = {};
    if (!form.route_id) e.route_id = "Route is required";
    if (!form.delivery_date) e.delivery_date = "Delivery date is required";
    if (!form.delivery_partner_id) e.delivery_partner_id = "Delivery partner is required";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      const session = await createSession.mutateAsync({
        route_id: Number(form.route_id),
        delivery_date: form.delivery_date,
        shift: form.shift as "MORNING" | "EVENING",
        delivery_partner_id: Number(form.delivery_partner_id),
      });
      navigate(`/delivery/sessions/${session.id}`);
    } catch {}
  }

  const submitError = (createSession.error as any)?.response?.data?.detail as string | undefined;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">Create Delivery Session</h1>
      <form onSubmit={handleSubmit} noValidate className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Select
          label="Route"
          required
          options={(routes || []).map((r) => ({ value: r.id, label: `${r.route_code} - ${r.route_name}` }))}
          placeholder="Select a route"
          value={form.route_id}
          onChange={(e) => setForm({ ...form, route_id: e.target.value })}
          error={errors.route_id}
        />
        <Input
          label="Delivery Date"
          type="date"
          required
          value={form.delivery_date}
          onChange={(e) => setForm({ ...form, delivery_date: e.target.value })}
          error={errors.delivery_date}
        />
        <Select
          label="Shift"
          required
          options={SHIFTS.map((s) => ({ value: s, label: s }))}
          value={form.shift}
          onChange={(e) => setForm({ ...form, shift: e.target.value })}
        />
        <Select
          label="Delivery Partner"
          required
          options={partnerList.map((emp) => ({ value: emp.id, label: `${emp.employee_code} - ${emp.name}` }))}
          placeholder="Select a delivery partner"
          value={form.delivery_partner_id}
          onChange={(e) => setForm({ ...form, delivery_partner_id: e.target.value })}
          error={errors.delivery_partner_id}
        />
        {submitError && <p className="text-sm text-red-600">{submitError}</p>}
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/delivery/sessions")}>Cancel</Button>
          <Button type="submit" loading={createSession.isPending}>Create Session</Button>
        </div>
      </form>
    </div>
  );
}
