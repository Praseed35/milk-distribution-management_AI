import { cn } from "../../lib/utils";

interface UtilizationBarProps {
  percentage: number;
  lowThreshold?: number;
  className?: string;
}

export default function UtilizationBar({ percentage, lowThreshold = 20, className }: UtilizationBarProps) {
  const clamped = Math.max(0, Math.min(100, percentage));
  const isLow = percentage < lowThreshold;
  const barColor = isLow ? "bg-amber-500" : "bg-emerald-500";

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="flex-1 h-2 rounded-full bg-slate-200 overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all", barColor)}
          style={{ width: `${clamped}%` }}
        />
      </div>
      <span className="text-sm text-slate-600 tabular-nums w-12 text-right">
        {percentage.toFixed(1)}%
      </span>
    </div>
  );
}
