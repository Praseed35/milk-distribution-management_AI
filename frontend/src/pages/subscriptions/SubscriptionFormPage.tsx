import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import {
  useSubscription,
  useCreateSubscription,
  useUpdateSubscription,
} from "../../hooks/useSubscriptions";
import { useCustomers } from "../../hooks/useCustomers";
import { useMilkTypes } from "../../hooks/useMilkTypes";

export default function SubscriptionFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { data: subscription, isLoading } = useSubscription(Number(id));
  const { data: customers } = useCustomers();
  const { data: milkTypes } = useMilkTypes();
  const createSubscription = useCreateSubscription();
  const updateSubscription = useUpdateSubscription();

  const [form, setForm] = useState({
    customer_id: "",
    milk_type_id: "",
    morning_quantity: "",
    evening_quantity: "",
    status: "ACTIVE",
    remarks: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (subscription) {
      setForm({
        customer_id: String(subscription.customer.id),
        milk_type_id: String(subscription.milk_type.id),
        morning_quantity: String(subscription.morning_quantity),
        evening_quantity: String(subscription.evening_quantity),
        status: subscription.status,
        remarks: subscription.remarks || "",
      });
    }
  }, [subscription]);

  function validate() {
    const e: Record<string, string> = {};
    if (!form.customer_id || form.customer_id === "0") e.customer_id = "Customer is required";
    if (!form.milk_type_id || form.milk_type_id === "0") e.milk_type_id = "Milk type is required";
    const morning = Number(form.morning_quantity);
    const evening = Number(form.evening_quantity);
    if (form.morning_quantity === "" || isNaN(morning) || morning < 0) e.morning_quantity = "Quantity must be 0 or more";
    if (form.evening_quantity === "" || isNaN(evening) || evening < 0) e.evening_quantity = "Quantity must be 0 or more";
    if (morning === 0 && evening === 0) e.morning_quantity = "At least one quantity must be greater than 0";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      if (isEdit) {
        await updateSubscription.mutateAsync({
          id: Number(id),
          data: {
            morning_quantity: Number(form.morning_quantity),
            evening_quantity: Number(form.evening_quantity),
            status: form.status,
            remarks: form.remarks || null,
          },
        });
      } else {
        await createSubscription.mutateAsync({
          customer_id: Number(form.customer_id),
          milk_type_id: Number(form.milk_type_id),
          morning_quantity: Number(form.morning_quantity),
          evening_quantity: Number(form.evening_quantity),
          status: form.status,
          remarks: form.remarks || null,
        });
      }
      navigate("/subscriptions");
    } catch {}
  }

  if (isEdit && isLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">{isEdit ? "Edit Subscription" : "Create Subscription"}</h1>
      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Select
          label="Customer"
          required
          options={customers?.map((c) => ({ value: c.id, label: `${c.customer_code} - ${c.customer_name}` })) || []}
          placeholder="Select a customer"
          value={form.customer_id}
          onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
          disabled={isEdit}
          error={errors.customer_id}
        />
        <Select
          label="Milk Type"
          required
          options={milkTypes?.map((m) => ({ value: m.id, label: `${m.milk_name} (${m.volume_ml} ml)` })) || []}
          placeholder="Select a milk type"
          value={form.milk_type_id}
          onChange={(e) => setForm({ ...form, milk_type_id: e.target.value })}
          disabled={isEdit}
          error={errors.milk_type_id}
        />
        <Input
          label="Morning Quantity"
          required
          type="number"
          min={0}
          step="any"
          value={form.morning_quantity}
          onChange={(e) => setForm({ ...form, morning_quantity: e.target.value })}
          error={errors.morning_quantity}
        />
        <Input
          label="Evening Quantity"
          required
          type="number"
          min={0}
          step="any"
          value={form.evening_quantity}
          onChange={(e) => setForm({ ...form, evening_quantity: e.target.value })}
          error={errors.evening_quantity}
        />
        <Select
          label="Status"
          options={[
            { value: "ACTIVE", label: "Active" },
            { value: "INACTIVE", label: "Inactive" },
          ]}
          value={form.status}
          onChange={(e) => setForm({ ...form, status: e.target.value })}
        />
        <Input label="Remarks" value={form.remarks ?? ""} onChange={(e) => setForm({ ...form, remarks: e.target.value })} />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/subscriptions")}>Cancel</Button>
          <Button type="submit" loading={createSubscription.isPending || updateSubscription.isPending}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}
