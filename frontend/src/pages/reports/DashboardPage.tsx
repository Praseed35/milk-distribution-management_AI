import PageHeader from "../../components/ui/PageHeader";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import KpiCard from "../../components/reports/KpiCard";
import { useDashboard } from "../../hooks/useReports";
import { DELIVERY_STATUS } from "../../lib/constants";
import { formatCurrency, formatDate, formatQuantity, getStatusColor } from "../../lib/utils";
import type { DeliveryStatusKey } from "../../types/reports";

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error || !data) return <EmptyState message="Failed to load dashboard" />;

  const statusKeys = Object.keys(data.deliveries_by_status) as DeliveryStatusKey[];

  return (
    <div>
      <PageHeader
        title="Operational Dashboard"
        description={`Report date: ${formatDate(data.report_date)}`}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard title="Sessions Today" value={data.total_sessions} />
        <KpiCard title="Milk Loaded" value={`${formatQuantity(data.total_milk_loaded)} L`} />
        <KpiCard title="Milk Delivered" value={`${formatQuantity(data.total_milk_delivered)} L`} />
        <KpiCard title="Cash Collected" value={formatCurrency(data.total_cash_collected)} />
        <KpiCard title="Pending Tokens" value={data.pending_token_count} />
        <KpiCard title="Unclosed Sessions" value={data.unclosed_sessions} sub="Before today" />
        <KpiCard title="Unbalanced Sessions" value={data.unbalanced_sessions} sub="Today" />
        <KpiCard title="Completed, Not Closed" value={data.completed_not_closed} sub="Today" />
      </div>

      <div className="bg-white rounded-lg shadow p-5">
        <h2 className="text-sm font-medium text-slate-700 mb-3">Deliveries by Status</h2>
        <div className="flex flex-wrap gap-2">
          {statusKeys.map((status) => (
            <span
              key={status}
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                status
              )}`}
            >
              {DELIVERY_STATUS[status]?.label ?? status}: {data.deliveries_by_status[status]}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
