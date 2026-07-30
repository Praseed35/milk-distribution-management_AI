import { useParams, useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import Badge from "../../components/ui/Badge";
import { useCustomer } from "../../hooks/useCustomers";

export default function CustomerDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: customer, isLoading, error } = useCustomer(Number(id));

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error || !customer) return <div className="text-center text-slate-500 mt-20">Customer not found</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-slate-800">{customer.customer_name}</h1>
          <p className="text-sm text-slate-500">{customer.customer_code}</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" onClick={() => navigate(`/customers/${id}/edit`)}>Edit</Button>
          <Button variant="secondary" onClick={() => navigate("/customers")}>Back</Button>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow p-6 space-y-3">
        <div className="grid grid-cols-2 gap-4">
          <div><span className="text-sm text-slate-500">Phone</span><p className="text-slate-800">{customer.primary_phone}</p></div>
          <div><span className="text-sm text-slate-500">Alternate Phone</span><p className="text-slate-800">{customer.alternate_phone || "—"}</p></div>
          <div><span className="text-sm text-slate-500">Address</span><p className="text-slate-800">{customer.address || "—"}</p></div>
          <div><span className="text-sm text-slate-500">Route ID</span><p className="text-slate-800">{customer.route_id}</p></div>
          <div><span className="text-sm text-slate-500">Status</span><div><Badge status={customer.is_active ? "Active" : "Inactive"} /></div></div>
          <div><span className="text-sm text-slate-500">Remarks</span><p className="text-slate-800">{customer.remarks || "—"}</p></div>
        </div>
      </div>
    </div>
  );
}
