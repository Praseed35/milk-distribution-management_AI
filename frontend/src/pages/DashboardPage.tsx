import { useAuth } from "../providers/AuthProvider";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-2">
          Welcome, {user?.username}
        </h2>
        <p className="text-slate-600">
          You are logged in as <span className="font-medium">{user?.role}</span>.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-slate-500">Active Routes</p>
          <p className="text-2xl font-bold text-slate-800">—</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-slate-500">Active Customers</p>
          <p className="text-2xl font-bold text-slate-800">—</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-slate-500">Today's Sessions</p>
          <p className="text-2xl font-bold text-slate-800">—</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-slate-500">Pending Tokens</p>
          <p className="text-2xl font-bold text-slate-800">—</p>
        </div>
      </div>
    </div>
  );
}
