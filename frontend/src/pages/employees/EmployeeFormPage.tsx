import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import { useEmployee, useCreateEmployee, useUpdateEmployee } from "../../hooks/useEmployees";
import { useRoutes } from "../../hooks/useRoutes";
import type { EmployeeCreate, EmployeeUpdate } from "../../types/employee";

export default function EmployeeFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { data: employee, isLoading } = useEmployee(Number(id));
  const { data: routes } = useRoutes();
  const createEmployee = useCreateEmployee();
  const updateEmployee = useUpdateEmployee();

  const [form, setForm] = useState<EmployeeCreate & { confirm_password: string }>({
    name: "", phone: "", address: "", role: "DELIVERY_PARTNER", route_id: null, username: "", password: "", confirm_password: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (employee) {
      setForm({
        name: employee.name,
        phone: employee.phone,
        address: employee.address || "",
        role: employee.role,
        route_id: employee.route_id ?? null,
        username: "", password: "", confirm_password: "",
      });
    }
  }, [employee]);

  function validate() {
    const e: Record<string, string> = {};
    if (!form.name || form.name.length < 2) e.name = "Name must be at least 2 characters";
    if (!form.phone || form.phone.length < 10) e.phone = "Phone must be at least 10 characters";
    if (!isEdit) {
      if (form.username && (!form.password || form.password.length < 6)) e.password = "Password must be at least 6 characters";
      if (form.password !== form.confirm_password) e.confirm_password = "Passwords do not match";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      const payload: EmployeeCreate = {
        name: form.name, phone: form.phone, address: form.address || null,
        role: form.role, route_id: form.route_id,
        username: form.username || null, password: form.password || null, confirm_password: form.confirm_password || null,
      };
      if (isEdit) {
        const updatePayload: EmployeeUpdate = { name: form.name, phone: form.phone, address: form.address || null, role: form.role, route_id: form.route_id };
        await updateEmployee.mutateAsync({ id: Number(id), data: updatePayload });
      } else {
        await createEmployee.mutateAsync(payload);
      }
      navigate("/employees");
    } catch {}
  }

  if (isEdit && isLoading) return <LoadingSpinner className="mt-20" />;

  const roleOptions = [
    { value: "CHECKER", label: "Checker" },
    { value: "DELIVERY_PARTNER", label: "Delivery Partner" },
  ];

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">{isEdit ? "Edit Employee" : "Create Employee"}</h1>
      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Input label="Name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} error={errors.name} />
        <Input label="Phone" required value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} error={errors.phone} />
        <Input label="Address" value={form.address ?? ""} onChange={(e) => setForm({ ...form, address: e.target.value })} />
        <Select label="Role" required options={roleOptions} value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
        <Select label="Route" options={routes?.map((r) => ({ value: r.id, label: `${r.route_code} - ${r.route_name}` })) || []} placeholder="Select a route" value={form.route_id ?? ""} onChange={(e) => setForm({ ...form, route_id: e.target.value ? Number(e.target.value) : null })} />
        {!isEdit && (
          <>
            <Input label="Username (optional)" value={form.username ?? ""} onChange={(e) => setForm({ ...form, username: e.target.value })} />
            <Input label="Password (optional)" type="password" value={form.password ?? ""} onChange={(e) => setForm({ ...form, password: e.target.value })} error={errors.password} />
            <Input label="Confirm Password" type="password" value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} error={errors.confirm_password} />
          </>
        )}
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/employees")}>Cancel</Button>
          <Button type="submit" loading={createEmployee.isPending || updateEmployee.isPending}>{isEdit ? "Update" : "Create"}</Button>
        </div>
      </form>
    </div>
  );
}
