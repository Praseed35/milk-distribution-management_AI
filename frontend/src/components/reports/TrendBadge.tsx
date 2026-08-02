import { cn } from "../../lib/utils";

const STABLE_THRESHOLD = 5;

interface TrendBadgeProps {
  changePercentage: number | null;
  className?: string;
}

export default function TrendBadge({ changePercentage, className }: TrendBadgeProps) {
  if (changePercentage === null || changePercentage === undefined) {
    return <span className="text-sm text-slate-500">No trend data</span>;
  }

  const stable = Math.abs(changePercentage) < STABLE_THRESHOLD;
  const label = stable ? "Stable" : changePercentage > 0 ? "Increasing" : "Declining";
  const color = stable
    ? "bg-slate-100 text-slate-700"
    : changePercentage > 0
      ? "bg-emerald-100 text-emerald-800"
      : "bg-red-100 text-red-800";

  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        color,
        className
      )}
    >
      {label} ({changePercentage > 0 ? "+" : ""}
      {changePercentage.toFixed(1)}%)
    </span>
  );
}
