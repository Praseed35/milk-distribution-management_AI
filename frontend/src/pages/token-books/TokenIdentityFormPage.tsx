import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import {
  useTokenIdentity,
  useCreateTokenIdentity,
  useUpdateTokenIdentity,
} from "../../hooks/useTokenBooks";
import { useCustomers } from "../../hooks/useCustomers";
import { useMilkTypes } from "../../hooks/useMilkTypes";

export default function TokenIdentityFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { data: identity, isLoading } = useTokenIdentity(Number(id));
  const { data: customers } = useCustomers();
  const { data: milkTypes } = useMilkTypes();
  const createIdentity = useCreateTokenIdentity();
  const updateIdentity = useUpdateTokenIdentity();

  const [form, setForm] = useState({
    customer_id: "",
    milk_type_id: "",
    token_number: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (identity) {
      setForm({
        customer_id: String(identity.customer.id),
        milk_type_id: String(identity.milk_type.id),
        token_number: String(identity.token_number),
      });
    }
  }, [identity]);

  function validate() {
    const e: Record<string, string> = {};
    if (!form.customer_id || form.customer_id === "0") e.customer_id = "Customer is required";
    if (!form.milk_type_id || form.milk_type_id === "0") e.milk_type_id = "Milk type is required";
    const token = Number(form.token_number);
    if (form.token_number === "" || isNaN(token) || token <= 0 || !Number.isInteger(token)) {
      e.token_number = "Token number must be a positive whole number";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      if (isEdit) {
        await updateIdentity.mutateAsync({
          id: Number(id),
          data: { token_number: Number(form.token_number) },
        });
      } else {
        await createIdentity.mutateAsync({
          customer_id: Number(form.customer_id),
          milk_type_id: Number(form.milk_type_id),
          token_number: Number(form.token_number),
        });
      }
      navigate("/token-identities");
    } catch {}
  }

  if (isEdit && isLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">
        {isEdit ? "Edit Token Identity" : "Create Token Identity"}
      </h1>
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
          label="Token Number"
          required
          type="number"
          min={1}
          step={1}
          value={form.token_number}
          onChange={(e) => setForm({ ...form, token_number: e.target.value })}
          error={errors.token_number}
        />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/token-identities")}>
            Cancel
          </Button>
          <Button type="submit" loading={createIdentity.isPending || updateIdentity.isPending}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}
