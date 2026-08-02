import { useState } from "react";
import toast from "react-hot-toast";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import Select from "../../components/ui/Select";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import PresetFilter from "../../components/reports/PresetFilter";
import AgingBuckets from "../../components/reports/AgingBuckets";
import KpiCard from "../../components/reports/KpiCard";
import { useCollectionEfficiency } from "../../hooks/useReports";
import { useRoutes } from "../../hooks/useRoutes";
import { downloadReportCsv } from "../../api/reports";
import { formatCurrency, formatDate, formatPercent } from "../../lib/utils";
import type { CustomerCollectionItem, ReportPreset } from "../../types/reports";

export default function CollectionEfficiencyPage() {
  const { data: routes } = useRoutes();
  const [filters, setFilters] = useState({ preset: "", from_date: "", to_date: "", route_id: "", min_outstanding: "" });
  const [refreshTick, setRefreshTick] = useState(0);

  const params = {
    preset: (filters.preset || undefined) as ReportPreset | undefined,
    from_date: filters.from_date || undefined,
    to_date: filters.to_date || undefined,
    route_id: filters.route_id ? Number(filters.route_id) : undefined,
    min_outstanding: filters.min_outstanding ? Number(filters.min_outstanding) : undefined,
    refresh: refreshTick > 0 ? true : undefined,
  };

  const { data, isLoading, error } = useCollectionEfficiency(params);
  const items = data?.data ?? [];

  function handlePresetChange(value: string) {
    setFilters({ ...filters, preset: value, from_date: "", to_date: "" });
  }

  function handleDownloadCsv() {
    downloadReportCsv(
      "/reports/collection-efficiency",
      params,
      `collection-efficiency-report-${new Date().toISOString().slice(0, 10)}.csv`
    ).catch(() => toast.error("Failed to download CSV"));
  }

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load collection efficiency report" />;

  const totalBilled = items.reduce((sum, i) => sum + i.total_billed, 0);
  const totalPaid = items.reduce((sum, i) => sum + i.total_paid, 0);
  const totalBalance = items.reduce((sum, i) => sum + i.balance, 0);
  const overall = totalBilled > 0 ? (totalPaid / totalBilled) * 100 : 0;

  return (
    <div>
      <PageHeader title="Collection Efficiency" description="Billed vs paid with aging analysis" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 items-end">
        <Select
          label="Route"
          options={routes?.map((r) => ({ value: r.id, label: r.route_name })) || []}
          placeholder="All routes"
          value={filters.route_id}
          onChange={(e) => setFilters({ ...filters, route_id: e.target.value })}
        />
        <Input
          label="Min Outstanding"
          type="number"
          min={0}
          placeholder="0"
          value={filters.min_outstanding}
          onChange={(e) => setFilters({ ...filters, min_outstanding: e.target.value })}
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
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <KpiCard title="Total Billed" value={formatCurrency(totalBilled)} />
        <KpiCard title="Total Paid" value={formatCurrency(totalPaid)} />
        <KpiCard title="Total Balance" value={formatCurrency(totalBalance)} />
        <KpiCard title="Overall Collection" value={formatPercent(overall)} />
      </div>

      {!items.length ? (
        <EmptyState message="No collection data found for the selected filters" />
      ) : (
        <DataTable
          columns={[
            {
              key: "customer_name",
              header: "Customer",
              sortable: true,
              render: (c: CustomerCollectionItem) => `${c.customer_code} - ${c.customer_name}`,
            },
            { key: "route_name", header: "Route", sortable: true },
            {
              key: "total_billed",
              header: "Billed",
              sortable: true,
              render: (c: CustomerCollectionItem) => formatCurrency(c.total_billed),
            },
            {
              key: "total_paid",
              header: "Paid",
              sortable: true,
              render: (c: CustomerCollectionItem) => formatCurrency(c.total_paid),
            },
            {
              key: "balance",
              header: "Balance",
              sortable: true,
              render: (c: CustomerCollectionItem) => formatCurrency(c.balance),
            },
            {
              key: "collection_percentage",
              header: "Collection %",
              sortable: true,
              render: (c: CustomerCollectionItem) => formatPercent(c.collection_percentage),
            },
            {
              key: "last_bill_date",
              header: "Last Bill",
              render: (c: CustomerCollectionItem) => (c.last_bill_date ? formatDate(c.last_bill_date) : "—"),
            },
            {
              key: "last_payment_date",
              header: "Last Payment",
              render: (c: CustomerCollectionItem) => (c.last_payment_date ? formatDate(c.last_payment_date) : "—"),
            },
            {
              key: "aging",
              header: "Aging",
              render: (c: CustomerCollectionItem) => (
                <AgingBuckets
                  agingCurrent={c.aging_current}
                  aging31to60={c.aging_31_60}
                  aging61to90={c.aging_61_90}
                  aging90Plus={c.aging_90_plus}
                />
              ),
            },
          ]}
          data={items}
          keyExtractor={(c) => c.customer_id}
        />
      )}

      <div className="mt-4 flex justify-end">
        <Button variant="secondary" onClick={handleDownloadCsv}>
          Download CSV
        </Button>
      </div>
    </div>
  );
}
