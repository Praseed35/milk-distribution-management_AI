import { useMemo, useState } from "react";
import Select from "../ui/Select";
import Input from "../ui/Input";
import Button from "../ui/Button";
import LoadingSpinner from "../ui/LoadingSpinner";
import EmptyState from "../ui/EmptyState";
import { useForecast } from "../../hooks/useAI";
import { useRoutes } from "../../hooks/useRoutes";
import type { ForecastDay } from "../../types/ai";

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

export default function ForecastSection() {
  const { data: routes } = useRoutes();
  const [routeId, setRouteId] = useState("");
  const [horizon, setHorizon] = useState("7");
  const [refreshTick, setRefreshTick] = useState(0);

  const horizonDays = Math.min(30, Math.max(1, Number(horizon) || 7));

  const params = {
    route_id: routeId ? Number(routeId) : undefined,
    horizon_days: horizonDays,
    refresh: refreshTick > 0 ? true : undefined,
  };

  const { data, isLoading, error } = useForecast(params);

  const maxPrediction = useMemo(() => {
    if (!data?.items?.length) return 0;
    return Math.max(...data.items.map((i) => i.predicted_quantity), 1);
  }, [data]);

  if (isLoading) return <LoadingSpinner className="py-10" />;
  if (error || !data) return <EmptyState message="Failed to load demand forecast" />;

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
        <div className="w-40">
          <Input
            label="Horizon (days)"
            type="number"
            min={1}
            max={30}
            value={horizon}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setHorizon(e.target.value)}
          />
        </div>
        <Button variant="secondary" onClick={() => setRefreshTick(Date.now())}>
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <p className="text-sm text-slate-500">Total Expected</p>
          <p className="text-2xl font-semibold text-slate-900 tabular-nums">
            {data.total_expected != null ? data.total_expected.toFixed(1) : "—"} L
          </p>
        </div>
        <div>
          <p className="text-sm text-slate-500">Low Range</p>
          <p className="text-2xl font-semibold text-slate-900 tabular-nums">
            {data.low_range != null ? data.low_range.toFixed(1) : "—"} L
          </p>
        </div>
        <div>
          <p className="text-sm text-slate-500">High Range</p>
          <p className="text-2xl font-semibold text-slate-900 tabular-nums">
            {data.high_range != null ? data.high_range.toFixed(1) : "—"} L
          </p>
        </div>
      </div>

      {!data.is_sufficient_history && (
        <div className="mb-4 rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-sm text-amber-800">
          {data.message || "Insufficient history for a full forecast."}
        </div>
      )}

      <ul className="space-y-2">
        {data.items.map((item: ForecastDay) => (
          <li key={item.date} className="flex items-center gap-3">
            <span className="w-28 text-sm text-slate-600">{formatDate(item.date)}</span>
            <div className="flex-1 h-3 rounded-full bg-slate-200 overflow-hidden">
              <div
                className="h-full rounded-full bg-indigo-500"
                style={{ width: `${(item.predicted_quantity / maxPrediction) * 100}%` }}
              />
            </div>
            <span className="w-20 text-sm text-slate-700 tabular-nums text-right">
              {item.predicted_quantity.toFixed(1)} L
            </span>
            <span className="w-24 text-xs text-slate-400 tabular-nums text-right">
              {item.low.toFixed(1)}–{item.high.toFixed(1)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
