import { useState } from "react";
import Select from "../ui/Select";
import Button from "../ui/Button";
import LoadingSpinner from "../ui/LoadingSpinner";
import EmptyState from "../ui/EmptyState";
import UtilizationBar from "../reports/UtilizationBar";
import { useChurnRisk } from "../../hooks/useAI";
import { useRoutes } from "../../hooks/useRoutes";
import { getStatusColor } from "../../lib/utils";
import type { ChurnRiskItem } from "../../types/ai";

export default function ChurnRiskTable() {
  const { data: routes } = useRoutes();
  const [routeId, setRouteId] = useState("");
  const [refreshTick, setRefreshTick] = useState(0);

  const params = {
    route_id: routeId ? Number(routeId) : undefined,
    refresh: refreshTick > 0 ? true : undefined,
  };

  const { data, isLoading, error } = useChurnRisk(params);
  const items = data?.items ?? [];

  if (isLoading) return <LoadingSpinner className="py-10" />;
  if (error) return <EmptyState message="Failed to load churn risk" />;

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex flex-wrap items-end gap-3 mb-4">
        <div className="w-56">
          <Select
            label="Route"
            options={routes?.map((r) => ({ value: r.id, label: r.route_name })) || []}
            placeholder="All routes"
            value={routeId}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setRouteId(e.target.value)}
          />
        </div>
        <Button variant="secondary" onClick={() => setRefreshTick(Date.now())}>
          Refresh
        </Button>
      </div>

      {!items.length ? (
        <p className="text-sm text-slate-500 py-4">No customers at risk</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Customer</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Route</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Risk Score</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Level</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Factors</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Suggested Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {items.map((item: ChurnRiskItem) => (
                <tr key={item.customer_id}>
                  <td className="px-3 py-2">
                    <div className="font-medium text-slate-800">{item.customer_name}</div>
                    <div className="text-xs text-slate-400">{item.customer_code}</div>
                  </td>
                  <td className="px-3 py-2 text-slate-600">{item.route_name}</td>
                  <td className="px-3 py-2 w-40">
                    <UtilizationBar percentage={item.risk_score} lowThreshold={40} />
                  </td>
                  <td className="px-3 py-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.risk_level)}`}
                    >
                      {item.risk_level}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <ul className="text-xs text-slate-600">
                      {item.factors.map((f) => (
                        <li key={f.factor}>
                          {f.factor.replace(/_/g, " ")} (+{f.contribution})
                        </li>
                      ))}
                    </ul>
                  </td>
                  <td className="px-3 py-2 text-xs text-indigo-600">{item.suggested_action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
