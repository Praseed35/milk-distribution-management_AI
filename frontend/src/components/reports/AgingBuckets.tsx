import { formatCurrency } from "../../lib/utils";

interface AgingBucketsProps {
  agingCurrent: number;
  aging31to60: number;
  aging61to90: number;
  aging90Plus: number;
}

const buckets = [
  { key: "aging_current", label: "Current", color: "bg-emerald-100 text-emerald-800" },
  { key: "aging_31_60", label: "31–60d", color: "bg-amber-100 text-amber-800" },
  { key: "aging_61_90", label: "61–90d", color: "bg-orange-100 text-orange-800" },
  { key: "aging_90_plus", label: "90d+", color: "bg-red-100 text-red-800" },
] as const;

export default function AgingBuckets({ agingCurrent, aging31to60, aging61to90, aging90Plus }: AgingBucketsProps) {
  const values = {
    aging_current: agingCurrent,
    aging_31_60: aging31to60,
    aging_61_90: aging61to90,
    aging_90_plus: aging90Plus,
  };

  return (
    <div className="flex flex-wrap gap-1.5">
      {buckets.map((b) => (
        <span
          key={b.key}
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${b.color}`}
        >
          {b.label}: {formatCurrency(values[b.key])}
        </span>
      ))}
    </div>
  );
}
