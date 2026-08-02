import { useState } from "react";
import toast from "react-hot-toast";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import Select from "../../components/ui/Select";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import UtilizationBar from "../../components/reports/UtilizationBar";
import KpiCard from "../../components/reports/KpiCard";
import { useTokenUtilization } from "../../hooks/useReports";
import { useRoutes } from "../../hooks/useRoutes";
import { downloadReportCsv } from "../../api/reports";
import { formatPercent } from "../../lib/utils";
import type { TokenUtilizationItem } from "../../types/reports";

export default function TokenUtilizationPage() {
  const { data: routes } = useRoutes();
  const [filters, setFilters] = useState({ route_id: "", low_threshold: "20" });
  const [refreshTick, setRefreshTick] = useState(0);

  const threshold = Math.min(100, Math.max(1, Number(filters.low_threshold) || 20));

  const params = {
    route_id: filters.route_id ? Number(filters.route_id) : undefined,
    low_threshold: threshold,
    refresh: refreshTick > 0 ? true : undefined,
  };

  const { data, isLoading, error } = useTokenUtilization(params);
  const items = data?.data ?? [];

  function handleDownloadCsv() {
    downloadReportCsv(
      "/reports/token-utilization",
      params,
      `token-utilization-report-${new Date().toISOString().slice(0, 10)}.csv`
    ).catch(() => toast.error("Failed to download CSV"));
  }

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load token utilization report" />;

  const totalUsed = items.reduce((sum, i) => sum + i.total_sheets_used, 0);
  const totalRemaining = items.reduce((sum, i) => sum + i.total_sheets_remaining, 0);
  const overall = totalUsed + totalRemaining > 0 ? (totalUsed / (totalUsed + totalRemaining)) * 100 : 0;
  const flagged = items.reduce((sum, i) => sum + i.books_below_20_percent, 0);

  return (
    <div>
      <PageHeader title="Token Utilization" description="Token book usage by customer" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 items-end">
        <Select
          label="Route"
          options={routes?.map((r) => ({ value: r.id, label: r.route_name })) || []}
          placeholder="All routes"
          value={filters.route_id}
          onChange={(e) => setFilters({ ...filters, route_id: e.target.value })}
        />
        <Input
          label="Low Threshold (%)"
          type="number"
          min={1}
          max={100}
          value={filters.low_threshold}
          onChange={(e) => setFilters({ ...filters, low_threshold: e.target.value })}
        />
        <Button variant="secondary" onClick={() => setRefreshTick(Date.now())}>
          Refresh
        </Button>
        <Button variant="secondary" onClick={handleDownloadCsv}>
          Download CSV
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <KpiCard title="Overall Utilization" value={formatPercent(overall)} />
        <KpiCard title="Sheets Used" value={totalUsed} />
        <KpiCard title="Books Below Threshold" value={flagged} sub={`Threshold: ${threshold}%`} />
      </div>

      {!items.length ? (
        <EmptyState message="No token books found for the selected filters" />
      ) : (
        <DataTable
          columns={[
            {
              key: "customer_name",
              header: "Customer",
              sortable: true,
              render: (t: TokenUtilizationItem) => t.customer_name,
            },
            { key: "route_name", header: "Route", sortable: true },
            { key: "token_number", header: "Token #", sortable: true },
            { key: "milk_type_name", header: "Milk Type" },
            { key: "total_books_issued", header: "Books Issued", sortable: true },
            { key: "active_books", header: "Active" },
            { key: "completed_books", header: "Completed" },
            { key: "total_sheets_used", header: "Sheets Used", sortable: true },
            { key: "total_sheets_remaining", header: "Sheets Left", sortable: true },
            {
              key: "utilization_percentage",
              header: "Utilization",
              sortable: true,
              render: (t: TokenUtilizationItem) => (
                <UtilizationBar percentage={t.utilization_percentage} lowThreshold={threshold} />
              ),
            },
            {
              key: "books_below_20_percent",
              header: "Low Books",
              render: (t: TokenUtilizationItem) => (t.books_below_20_percent > 0 ? t.books_below_20_percent : "—"),
            },
          ]}
          data={items}
          keyExtractor={(t) => t.customer_id}
        />
      )}
    </div>
  );
}
