import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import { useCreateUser } from "../../hooks/useUsers";

export default function UserCreatePage() {
  const navigate = useNavigate();
  const createUser = useCreateUser();
  const [form, setForm] = useState({ username: "", password: "", confirmPassword: "", role: "OWNER" });
  const [errors, setErrors] = useState<Record<string, string>>({});

  function validate() {
    const e: Record<string, string> = {};
    if (!form.username || form.username.length < 3) e.username = "Username must be at least 3 characters";
    if (!form.password || form.password.length < 6) e.password = "Password must be at least 6 characters";
    if (form.password !== form.confirmPassword) e.confirmPassword = "Passwords do not match";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      await createUser.mutateAsync({ username: form.username, password: form.password, role: form.role });
      navigate("/users");
    } catch {}
  }

  const roleOptions = [
    { value: "OWNER", label: "Owner" },
    { value: "ADMIN", label: "Admin" },
    { value: "CHECKER", label: "Checker" },
    { value: "DELIVERY_PARTNER", label: "Delivery Partner" },
    { value: "EMPLOYEE", label: "Employee" },
  ];

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">Create User</h1>
      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Input label="Username" required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} error={errors.username} />
        <Input label="Password" required type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} error={errors.password} />
        <Input label="Confirm Password" required type="password" value={form.confirmPassword} onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })} error={errors.confirmPassword} />
        <Select label="Role" required options={roleOptions} value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/users")}>Cancel</Button>
          <Button type="submit" loading={createUser.isPending}>Create</Button>
        </div>
      </form>
    </div>
  );
}
