import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import { useRoute, useCreateRoute, useUpdateRoute } from "../../hooks/useRoutes";
import type { RouteCreate, RouteUpdate } from "../../types/route";

export default function RouteFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { data: route, isLoading } = useRoute(Number(id));
  const createRoute = useCreateRoute();
  const updateRoute = useUpdateRoute();

  const [form, setForm] = useState<RouteCreate>({ route_code: "", route_name: "", description: "" });
  const [errors, setErrors] = useState<Partial<RouteCreate>>({});

  useEffect(() => {
    if (route) {
      setForm({ route_code: route.route_code, route_name: route.route_name, description: route.description || "" });
    }
  }, [route]);

  function validate() {
    const e: Partial<RouteCreate> = {};
    if (!form.route_code || form.route_code.length < 2) e.route_code = "Code must be at least 2 characters";
    if (!form.route_name || form.route_name.length < 2) e.route_name = "Name must be at least 2 characters";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      if (isEdit) {
        await updateRoute.mutateAsync({ id: Number(id), data: form as RouteUpdate });
      } else {
        await createRoute.mutateAsync(form);
      }
      navigate("/routes");
    } catch {}
  }

  if (isEdit && isLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">{isEdit ? "Edit Route" : "Create Route"}</h1>
      <form onSubmit={handleSubmit} noValidate className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Input label="Route Code" required value={form.route_code} onChange={(e) => setForm({ ...form, route_code: e.target.value })} error={errors.route_code} disabled={isEdit} />
        <Input label="Route Name" required value={form.route_name} onChange={(e) => setForm({ ...form, route_name: e.target.value })} error={errors.route_name} />
        <Input label="Description" value={form.description ?? ""} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/routes")}>Cancel</Button>
          <Button type="submit" loading={createRoute.isPending || updateRoute.isPending}>{isEdit ? "Update" : "Create"}</Button>
        </div>
      </form>
    </div>
  );
}
