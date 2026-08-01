import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import { useMilkType, useCreateMilkType, useUpdateMilkType } from "../../hooks/useMilkTypes";
import type { MilkTypeCreate, MilkTypeUpdate } from "../../types/milk-type";

export default function MilkTypeFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { data: milkType, isLoading } = useMilkType(Number(id));
  const createMilkType = useCreateMilkType();
  const updateMilkType = useUpdateMilkType();

  const [form, setForm] = useState({ milk_name: "", volume_ml: "", unit_price: "", description: "" });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (milkType) {
      setForm({
        milk_name: milkType.milk_name,
        volume_ml: String(milkType.volume_ml),
        unit_price: String(milkType.unit_price),
        description: milkType.description || "",
      });
    }
  }, [milkType]);

  function validate() {
    const e: Record<string, string> = {};
    if (!form.milk_name || form.milk_name.length < 2) e.milk_name = "Name must be at least 2 characters";
    if (!form.volume_ml || Number(form.volume_ml) <= 0) e.volume_ml = "Volume must be greater than 0";
    if (Number(form.unit_price) < 0) e.unit_price = "Price cannot be negative";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    const payload: MilkTypeCreate = {
      milk_name: form.milk_name,
      volume_ml: Number(form.volume_ml),
      unit_price: Number(form.unit_price),
      description: form.description || null,
    };
    try {
      if (isEdit) {
        await updateMilkType.mutateAsync({ id: Number(id), data: payload as MilkTypeUpdate });
      } else {
        await createMilkType.mutateAsync(payload);
      }
      navigate("/milk-types");
    } catch {}
  }

  if (isEdit && isLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">{isEdit ? "Edit Milk Type" : "Create Milk Type"}</h1>
      <form onSubmit={handleSubmit} noValidate className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Input label="Milk Name" required value={form.milk_name} onChange={(e) => setForm({ ...form, milk_name: e.target.value })} error={errors.milk_name} />
        <Input label="Volume (ml)" required type="number" value={form.volume_ml} onChange={(e) => setForm({ ...form, volume_ml: e.target.value })} error={errors.volume_ml} />
        <Input label="Unit Price" required type="number" step="0.01" value={form.unit_price} onChange={(e) => setForm({ ...form, unit_price: e.target.value })} error={errors.unit_price} />
        <Input label="Description" value={form.description ?? ""} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/milk-types")}>Cancel</Button>
          <Button type="submit" loading={createMilkType.isPending || updateMilkType.isPending}>{isEdit ? "Update" : "Create"}</Button>
        </div>
      </form>
    </div>
  );
}
