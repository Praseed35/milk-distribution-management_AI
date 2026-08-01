import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import { useCustomer, useCreateCustomer, useUpdateCustomer } from "../../hooks/useCustomers";
import { useRoutes } from "../../hooks/useRoutes";



export default function CustomerFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { data: customer, isLoading } = useCustomer(Number(id));
  const { data: routes } = useRoutes();
  const createCustomer = useCreateCustomer();
  const updateCustomer = useUpdateCustomer();

  const [form, setForm] = useState({
    customer_name: "", primary_phone: "", alternate_phone: "", address: "", route_id: "", remarks: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (customer) {
      setForm({
        customer_name: customer.customer_name,
        primary_phone: customer.primary_phone,
        alternate_phone: customer.alternate_phone || "",
        address: customer.address || "",
        route_id: String(customer.route_id),
        remarks: customer.remarks || "",
      });
    }
  }, [customer]);

  function validate() {
    const e: Record<string, string> = {};
    if (!form.customer_name || form.customer_name.length < 2) e.customer_name = "Name must be at least 2 characters";
    if (!form.primary_phone || form.primary_phone.length !== 10) e.primary_phone = "Phone must be 10 digits";
    if (form.alternate_phone && form.alternate_phone.length !== 10) e.alternate_phone = "Phone must be 10 digits";
    if (!form.route_id || form.route_id === "0") e.route_id = "Route is required";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      if (isEdit) {
        await updateCustomer.mutateAsync({
          id: Number(id),
          data: {
            customer_name: form.customer_name,
            primary_phone: form.primary_phone,
            alternate_phone: form.alternate_phone || null,
            address: form.address || null,
            route_id: Number(form.route_id),
            remarks: form.remarks || null,
          },
        });
      } else {
        await createCustomer.mutateAsync({
          customer_name: form.customer_name,
          primary_phone: form.primary_phone,
          alternate_phone: form.alternate_phone || null,
          address: form.address || null,
          route_id: Number(form.route_id),
          remarks: form.remarks || null,
        });
      }
      navigate("/customers");
    } catch {}
  }

  if (isEdit && isLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">{isEdit ? "Edit Customer" : "Create Customer"}</h1>
      <form onSubmit={handleSubmit} noValidate className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Input label="Customer Name" required value={form.customer_name} onChange={(e) => setForm({ ...form, customer_name: e.target.value })} error={errors.customer_name} />
        <Input label="Primary Phone" required value={form.primary_phone} onChange={(e) => setForm({ ...form, primary_phone: e.target.value })} error={errors.primary_phone} maxLength={10} />
        <Input label="Alternate Phone" value={form.alternate_phone ?? ""} onChange={(e) => setForm({ ...form, alternate_phone: e.target.value })} error={errors.alternate_phone} maxLength={10} />
        <Input label="Address" value={form.address ?? ""} onChange={(e) => setForm({ ...form, address: e.target.value })} />
        <Select label="Route" required options={routes?.map((r) => ({ value: r.id, label: `${r.route_code} - ${r.route_name}` })) || []} placeholder="Select a route" value={form.route_id} onChange={(e) => setForm({ ...form, route_id: e.target.value })} />
        <Input label="Remarks" value={form.remarks ?? ""} onChange={(e) => setForm({ ...form, remarks: e.target.value })} />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/customers")}>Cancel</Button>
          <Button type="submit" loading={createCustomer.isPending || updateCustomer.isPending}>{isEdit ? "Update" : "Create"}</Button>
        </div>
      </form>
    </div>
  );
}
