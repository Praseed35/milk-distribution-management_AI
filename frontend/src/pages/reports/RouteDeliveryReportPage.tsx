import { useState } from "react";
import toast from "react-hot-toast";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import Select from "../../components/ui/Select";
import Button from "../../components/ui/Button";
import PresetFilter from "../../components/reports/PresetFilter";
import { useRouteDelivery } from "../../hooks/useReports";
import { useRoutes } from "../../hooks/useRoutes";
import { downloadReportCsv } from "../../api/reports";
import { formatCurrency, formatQuantity, getStatusColor } from "../../lib/utils";
import type { ReportPreset, RouteDeliveryItem } from "../../types/reports";

export default function RouteDeliveryReportPage() {
  const { data: routes } = useRoutes();
  const [filters, setFilters] = useState({ preset: "", from_date: "", to_date: "", route_id: "" });
  const [refreshTick, setRefreshTick] = useState(0);

  const params = {
    preset: (filters.preset || undefined) as ReportPreset | undefined,
    from_date: filters.from_date || undefined,
    to_date: filters.to_date || undefined,
    route_id: filters.route_id ? Number(filters.route_id) : undefined,
    refresh: refreshTick > 0 ? true : undefined,
  };

  const { data, isLoading, error } = useRouteDelivery(params);
  const items = data?.data ?? [];

  function handlePresetChange(value: string) {
    setFilters({ ...filters, preset: value, from_date: "", to_date: "" });
  }

  function handleDownloadCsv() {
    downloadReportCsv(
      "/reports/route-delivery",
      params,
      `route-delivery-report-${new Date().toISOString().slice(0, 10)}.csv`
    ).catch(() => toast.error("Failed to download CSV"));
  }

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load route delivery report" />;

  const totals = items.reduce(
    (acc, item) => ({
      session_count: acc.session_count + item.session_count,
      delivery_count: acc.delivery_count + item.delivery_count,
      total_loaded_quantity: acc.total_loaded_quantity + item.total_loaded_quantity,
      total_delivered_quantity: acc.total_delivered_quantity + item.total_delivered_quantity,
      total_cash_collected: acc.total_cash_collected + item.total_cash_collected,
      total_token_registered: acc.total_token_registered + item.total_token_registered,
      total_returned_quantity: acc.total_returned_quantity + item.total_returned_quantity,
      shortage_surplus: acc.shortage_surplus + item.shortage_surplus,
    }),
    {
      session_count: 0,
      delivery_count: 0,
      total_loaded_quantity: 0,
      total_delivered_quantity: 0,
      total_cash_collected: 0,
      total_token_registered: 0,
      total_returned_quantity: 0,
      shortage_surplus: 0,
    }
  );

  return (
    <div>
      <PageHeader title="Route Delivery Report" description="Delivery performance by route" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 items-end">
        <Select
          label="Route"
          options={routes?.map((r) => ({ value: r.id, label: r.route_name })) || []}
          placeholder="All routes"
          value={filters.route_id}
          onChange={(e) => setFilters({ ...filters, route_id: e.target.value })}
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

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-slate-500">Total Loaded</p>
          <p className="text-lg font-bold text-slate-800">{formatQuantity(totals.total_loaded_quantity)} L</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-slate-500">Total Delivered</p>
          <p className="text-lg font-bold text-slate-800">{formatQuantity(totals.total_delivered_quantity)} L</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-slate-500">Total Cash</p>
          <p className="text-lg font-bold text-slate-800">{formatCurrency(totals.total_cash_collected)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-slate-500">Shortage / Surplus</p>
          <p className="text-lg font-bold text-slate-800">{formatQuantity(totals.shortage_surplus)} L</p>
        </div>
      </div>

      {!items.length ? (
        <EmptyState message="No route delivery data found for the selected period" />
      ) : (
        <DataTable
          columns={[
            {
              key: "route_name",
              header: "Route",
              sortable: true,
              render: (r: RouteDeliveryItem) => `${r.route_code} - ${r.route_name}`,
            },
            { key: "session_count", header: "Sessions", sortable: true },
            { key: "delivery_count", header: "Deliveries", sortable: true },
            {
              key: "total_loaded_quantity",
              header: "Loaded",
              sortable: true,
              render: (r: RouteDeliveryItem) => formatQuantity(r.total_loaded_quantity),
            },
            {
              key: "total_delivered_quantity",
              header: "Delivered",
              sortable: true,
              render: (r: RouteDeliveryItem) => formatQuantity(r.total_delivered_quantity),
            },
            {
              key: "total_token_registered",
              header: "Tokens",
              sortable: true,
              render: (r: RouteDeliveryItem) => formatQuantity(r.total_token_registered),
            },
            {
              key: "total_cash_collected",
              header: "Cash",
              sortable: true,
              render: (r: RouteDeliveryItem) => formatCurrency(r.total_cash_collected),
            },
            {
              key: "total_returned_quantity",
              header: "Returned",
              sortable: true,
              render: (r: RouteDeliveryItem) => formatQuantity(r.total_returned_quantity),
            },
            {
              key: "shortage_surplus",
              header: "Shortage/Surplus",
              sortable: true,
              render: (r: RouteDeliveryItem) => formatQuantity(r.shortage_surplus),
            },
            {
              key: "is_balanced",
              header: "Status",
              render: (r: RouteDeliveryItem) => (
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                    r.is_balanced ? "BALANCED" : "UNBALANCED"
                  )}`}
                >
                  {r.is_balanced ? "Balanced" : "Unbalanced"}
                </span>
              ),
            },
          ]}
          data={items}
          keyExtractor={(r) => r.route_id}
        />
      )}
    </div>
  );
}
