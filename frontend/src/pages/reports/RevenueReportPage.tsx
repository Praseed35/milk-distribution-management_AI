import { useState } from "react";
import toast from "react-hot-toast";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import Select from "../../components/ui/Select";
import Button from "../../components/ui/Button";
import PresetFilter from "../../components/reports/PresetFilter";
import KpiCard from "../../components/reports/KpiCard";
import { useRevenue } from "../../hooks/useReports";
import { useRoutes } from "../../hooks/useRoutes";
import { useMilkTypes } from "../../hooks/useMilkTypes";
import { downloadReportCsv } from "../../api/reports";
import { formatCurrency, formatPercent } from "../../lib/utils";
import type { ReportPreset, RevenueBreakdown } from "../../types/reports";

export default function RevenueReportPage() {
  const { data: routes } = useRoutes();
  const { data: milkTypes } = useMilkTypes();
  const [filters, setFilters] = useState({
    preset: "",
    from_date: "",
    to_date: "",
    route_id: "",
    milk_type_id: "",
  });
  const [refreshTick, setRefreshTick] = useState(0);

  const params = {
    preset: (filters.preset || undefined) as ReportPreset | undefined,
    from_date: filters.from_date || undefined,
    to_date: filters.to_date || undefined,
    route_id: filters.route_id ? Number(filters.route_id) : undefined,
    milk_type_id: filters.milk_type_id ? Number(filters.milk_type_id) : undefined,
    refresh: refreshTick > 0 ? true : undefined,
  };

  const { data, isLoading, error } = useRevenue(params);

  function handlePresetChange(value: string) {
    setFilters({ ...filters, preset: value, from_date: "", to_date: "" });
  }

  function handleDownloadCsv() {
    downloadReportCsv(
      "/reports/revenue",
      params,
      `revenue-report-${new Date().toISOString().slice(0, 10)}.csv`
    ).catch(() => toast.error("Failed to download CSV"));
  }

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error || !data) return <EmptyState message="Failed to load revenue report" />;

  return (
    <div>
      <PageHeader title="Revenue Report" description="Revenue breakdown by source, mode, route and milk type" />
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4 items-end">
        <Select
          label="Route"
          options={routes?.map((r) => ({ value: r.id, label: r.route_name })) || []}
          placeholder="All routes"
          value={filters.route_id}
          onChange={(e) => setFilters({ ...filters, route_id: e.target.value })}
        />
        <Select
          label="Milk Type"
          options={milkTypes?.map((m) => ({ value: m.id, label: m.milk_name })) || []}
          placeholder="All milk types"
          value={filters.milk_type_id}
          onChange={(e) => setFilters({ ...filters, milk_type_id: e.target.value })}
        />
        <div className="col-span-2">
          <PresetFilter
            preset={filters.preset}
            fromDate={filters.from_date}
            toDate={filters.to_date}
            onPresetChange={handlePresetChange}
            onFromDateChange={(v) => setFilters({ ...filters, from_date: v, preset: "" })}
            onToDateChange={(v) => setFilters({ ...filters, to_date: v, preset: "" })}
            onRefresh={() => setRefreshTick(Date.now())}
          />
        </div>
        <Button variant="secondary" onClick={handleDownloadCsv}>
          Download CSV
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <KpiCard title="Total Revenue" value={formatCurrency(data.total_revenue)} />
        <KpiCard title="Token Book Revenue" value={formatCurrency(data.token_book_revenue)} />
        <KpiCard title="Customer Bill Revenue" value={formatCurrency(data.customer_bill_revenue)} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <BreakdownTable title="By Source" items={data.by_source} nameField="source" />
        <BreakdownTable title="By Payment Mode" items={data.by_payment_mode} nameField="payment_mode" />
        <BreakdownTable title="By Route" items={data.by_route} nameField="route_name" />
        <BreakdownTable title="By Milk Type" items={data.by_milk_type} nameField="milk_type_name" />
      </div>
    </div>
  );
}

function BreakdownTable({ title, items, nameField }: { title: string; items: RevenueBreakdown[]; nameField: keyof RevenueBreakdown }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-sm font-medium text-slate-700 mb-3">{title}</h2>
      <DataTable
        columns={[
          {
            key: nameField as string,
            header: "Name",
            render: (r: RevenueBreakdown) => String(r[nameField] ?? "—"),
          },
          {
            key: "amount",
            header: "Amount",
            sortable: true,
            render: (r: RevenueBreakdown) => formatCurrency(r.amount),
          },
          {
            key: "percentage",
            header: "Share",
            sortable: true,
            render: (r: RevenueBreakdown) => formatPercent(r.percentage),
          },
        ]}
        data={items}
        keyExtractor={(r) => `${String(r[nameField] ?? "unknown")}-${title}`}
        emptyMessage="No revenue data"
      />
    </div>
  );
}
