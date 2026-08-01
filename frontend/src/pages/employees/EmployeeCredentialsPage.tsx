import { useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import { useEmployee, useUpdateEmployeeCredentials } from "../../hooks/useEmployees";
import type { EmployeeCredentialsUpdate } from "../../types/employee";

export default function EmployeeCredentialsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: employee, isLoading } = useEmployee(Number(id));
  const updateCredentials = useUpdateEmployeeCredentials();

  const [form, setForm] = useState<EmployeeCredentialsUpdate & { confirm_password: string }>({
    username: "", password: "", confirm_password: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  function validate() {
    const e: Record<string, string> = {};
    const hasUsername = !!form.username;
    const hasPassword = !!form.password;
    if (hasUsername && hasPassword && (form.password ?? "").length < 6) e.password = "Password must be at least 6 characters";
    if (form.password !== form.confirm_password) e.confirm_password = "Passwords do not match";
    if (!hasUsername && !hasPassword) e.username = "Provide at least username or password";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      await updateCredentials.mutateAsync({
        id: Number(id),
        data: { username: form.username || null, password: form.password || null, confirm_password: form.confirm_password || null },
      });
      navigate("/employees");
    } catch {}
  }

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (!employee) return <div className="text-center text-slate-500 mt-20">Employee not found</div>;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-2">Credentials</h1>
      <p className="text-sm text-slate-500 mb-6">{employee.employee_code} — {employee.name}</p>
      <form onSubmit={handleSubmit} noValidate className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Input label="Username" value={form.username ?? ""} onChange={(e) => setForm({ ...form, username: e.target.value })} error={errors.username} />
        <Input label="Password" type="password" value={form.password ?? ""} onChange={(e) => setForm({ ...form, password: e.target.value })} error={errors.password} />
        <Input label="Confirm Password" type="password" value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} error={errors.confirm_password} />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/employees")}>Cancel</Button>
          <Button type="submit" loading={updateCredentials.isPending}>Update Credentials</Button>
        </div>
      </form>
    </div>
  );
}
