import { cn } from "../../lib/utils";

interface KpiCardProps {
  title: string;
  value: React.ReactNode;
  sub?: React.ReactNode;
  className?: string;
}

export default function KpiCard({ title, value, sub, className }: KpiCardProps) {
  return (
    <div className={cn("bg-white rounded-lg shadow p-5", className)}>
      <p className="text-sm text-slate-500">{title}</p>
      <p className="mt-1 text-2xl font-bold text-slate-800">{value}</p>
      {sub && <p className="mt-1 text-sm text-slate-500">{sub}</p>}
    </div>
  );
}
