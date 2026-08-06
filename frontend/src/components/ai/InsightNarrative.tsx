import { useState } from "react";
import PresetFilter from "../reports/PresetFilter";
import LoadingSpinner from "../ui/LoadingSpinner";
import EmptyState from "../ui/EmptyState";
import { useInsights } from "../../hooks/useAI";
import { formatDate } from "../../lib/utils";
import type { ReportPreset } from "../../types/reports";

export default function InsightNarrative() {
  const [preset, setPreset] = useState("this_month");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [refreshTick, setRefreshTick] = useState(0);

  const params = {
    preset: (preset || undefined) as ReportPreset | undefined,
    from_date: preset ? undefined : fromDate || undefined,
    to_date: preset ? undefined : toDate || undefined,
    refresh: refreshTick > 0 ? true : undefined,
  };

  const { data, isLoading, error } = useInsights(params);

  if (isLoading) return <LoadingSpinner className="py-10" />;
  if (error) return <EmptyState message="Failed to load AI narrative" />;

  const range = data?.data_range;
  const rangeLabel =
    range && range.from && range.to
      ? `${formatDate(range.from)} - ${formatDate(range.to)}`
      : "";

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <PresetFilter
        preset={preset}
        fromDate={fromDate}
        toDate={toDate}
        onPresetChange={setPreset}
        onFromDateChange={setFromDate}
        onToDateChange={setToDate}
        onRefresh={() => setRefreshTick(Date.now())}
      />

      {rangeLabel && (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 mb-3">
          {rangeLabel}
        </span>
      )}

      {data?.stats_only ? (
        <div className="mt-2 rounded-md bg-slate-50 border border-slate-200 px-3 py-4 text-sm text-slate-600">
          AI explanations unavailable - showing statistics
        </div>
      ) : (
        <div className="mt-2 space-y-2 text-sm text-slate-700">
          {(data?.narrative || "")
            .split("\n")
            .map((line, idx) => line.trim() && <p key={idx}>{line.trim()}</p>)}
        </div>
      )}
    </div>
  );
}
