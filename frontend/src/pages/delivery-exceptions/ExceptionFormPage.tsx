import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import {
  useDeliveryException,
  useCreateDeliveryException,
  useUpdateDeliveryException,
} from "../../hooks/useDeliveryExceptions";
import { useSubscriptions } from "../../hooks/useSubscriptions";
import { EXCEPTION_TYPES } from "../../lib/constants";

function toDateInput(value: string) {
  return value.slice(0, 10);
}

export default function ExceptionFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { data: exception, isLoading } = useDeliveryException(Number(id));
  const { data: subscriptions } = useSubscriptions();
  const createException = useCreateDeliveryException();
  const updateException = useUpdateDeliveryException();

  const [form, setForm] = useState({
    subscription_id: "",
    exception_type: "VACATION",
    shift: "",
    start_date: "",
    end_date: "",
    reason: "",
    status: "ACTIVE",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (exception) {
      setForm({
        subscription_id: String(exception.subscription.id),
        exception_type: exception.exception_type,
        shift: exception.shift || "",
        start_date: toDateInput(exception.start_date),
        end_date: exception.end_date ? toDateInput(exception.end_date) : "",
        reason: exception.reason || "",
        status: exception.status,
      });
    }
  }, [exception]);

  function validate() {
    const e: Record<string, string> = {};
    if (!form.subscription_id || form.subscription_id === "0") e.subscription_id = "Subscription is required";
    if (!form.exception_type) e.exception_type = "Exception type is required";
    if (!form.start_date) e.start_date = "Start date is required";
    if (form.end_date && form.start_date && form.end_date < form.start_date) {
      e.end_date = "End date must be on or after start date";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      if (isEdit) {
        await updateException.mutateAsync({
          id: Number(id),
          data: {
            exception_type: form.exception_type,
            shift: form.shift || null,
            start_date: form.start_date,
            end_date: form.end_date || null,
            reason: form.reason || null,
            status: form.status,
          },
        });
      } else {
        await createException.mutateAsync({
          subscription_id: Number(form.subscription_id),
          exception_type: form.exception_type,
          shift: form.shift || null,
          start_date: form.start_date,
          end_date: form.end_date || null,
          reason: form.reason || null,
        });
      }
      navigate("/delivery-exceptions");
    } catch {}
  }

  if (isEdit && isLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">{isEdit ? "Edit Delivery Exception" : "Create Delivery Exception"}</h1>
      <form onSubmit={handleSubmit} noValidate className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Select
          label="Subscription"
          required
          options={
            subscriptions?.map((s) => ({
              value: s.id,
              label: `${s.customer_code} - ${s.customer_name}`,
            })) || []
          }
          placeholder="Select a subscription"
          value={form.subscription_id}
          onChange={(e) => setForm({ ...form, subscription_id: e.target.value })}
          disabled={isEdit}
          error={errors.subscription_id}
        />
        <Select
          label="Exception Type"
          required
          options={EXCEPTION_TYPES.map((t) => ({ value: t, label: t.replace(/_/g, " ") }))}
          value={form.exception_type}
          onChange={(e) => setForm({ ...form, exception_type: e.target.value })}
          error={errors.exception_type}
        />
        <Select
          label="Shift"
          options={[
            { value: "", label: "Whole Day" },
            { value: "MORNING", label: "Morning" },
            { value: "EVENING", label: "Evening" },
          ]}
          value={form.shift}
          onChange={(e) => setForm({ ...form, shift: e.target.value })}
        />
        <Input label="Start Date" required type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} error={errors.start_date} />
        <Input label="End Date" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} error={errors.end_date} />
        <Input label="Reason" value={form.reason ?? ""} onChange={(e) => setForm({ ...form, reason: e.target.value })} />
        {isEdit && (
          <Select
            label="Status"
            options={[
              { value: "ACTIVE", label: "Active" },
              { value: "INACTIVE", label: "Inactive" },
            ]}
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value })}
          />
        )}
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/delivery-exceptions")}>Cancel</Button>
          <Button type="submit" loading={createException.isPending || updateException.isPending}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}
