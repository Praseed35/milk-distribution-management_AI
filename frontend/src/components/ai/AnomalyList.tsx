import { useState } from "react";
import Select from "../ui/Select";
import Button from "../ui/Button";
import LoadingSpinner from "../ui/LoadingSpinner";
import EmptyState from "../ui/EmptyState";
import { useAnomalies } from "../../hooks/useAI";
import { useRoutes } from "../../hooks/useRoutes";
import { formatDate } from "../../lib/utils";
import type { AnomalyItem } from "../../types/ai";

function severityClass(severity: string): string {
  if (severity === "HIGH") return "bg-red-100 text-red-800";
  if (severity === "MEDIUM") return "bg-amber-100 text-amber-800";
  return "bg-sky-100 text-sky-800";
}

export default function AnomalyList() {
  const { data: routes } = useRoutes();
  const [routeId, setRouteId] = useState("");
  const [refreshTick, setRefreshTick] = useState(0);

  const params = {
    route_id: routeId ? Number(routeId) : undefined,
    refresh: refreshTick > 0 ? true : undefined,
  };

  const { data, isLoading, error } = useAnomalies(params);
  const items = data?.items ?? [];

  if (isLoading) return <LoadingSpinner className="py-10" />;
  if (error) return <EmptyState message="Failed to load anomaly alerts" />;

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
        <p className="text-sm text-slate-500 py-4">No anomalies detected</p>
      ) : (
        <ul className="space-y-3">
          {items.map((item: AnomalyItem) => (
            <li key={`${item.type}-${item.entity_id}-${item.occurred_on}`} className="rounded-md border border-slate-200 p-3">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityClass(item.severity)}`}
                >
                  {item.severity}
                </span>
                <span className="text-sm font-medium text-slate-800">{item.title}</span>
                <span className="ml-auto text-xs text-slate-400">{formatDate(item.occurred_on)}</span>
              </div>
              <p className="text-sm text-slate-600">{item.description}</p>
              <p className="mt-1 text-xs text-slate-500 tabular-nums">
                Expected: {item.expected.toFixed(1)} &middot; Actual: {item.actual.toFixed(1)} &middot;
                Deviation: {item.deviation > 0 ? "+" : ""}{item.deviation.toFixed(1)}
              </p>
              <p className="mt-1 text-xs text-indigo-600">{item.suggested_action}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
