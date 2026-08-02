import { useState } from "react";
import { useParams } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import Select from "../../components/ui/Select";
import PresetFilter from "../../components/reports/PresetFilter";
import KpiCard from "../../components/reports/KpiCard";
import TrendBadge from "../../components/reports/TrendBadge";
import { useConsumption } from "../../hooks/useReports";
import { useCustomers } from "../../hooks/useCustomers";
import { formatDate, formatQuantity } from "../../lib/utils";
import type { ConsumptionDay, ReportPreset } from "../../types/reports";

export default function ConsumptionReportPage() {
  const { customerId: routeCustomerId } = useParams();
  const { data: customers } = useCustomers();
  const [customerId, setCustomerId] = useState(routeCustomerId || "");
  const [filters, setFilters] = useState({ preset: "", from_date: "", to_date: "" });
  const [refreshTick, setRefreshTick] = useState(0);

  const params = {
    preset: (filters.preset || undefined) as ReportPreset | undefined,
    from_date: filters.from_date || undefined,
    to_date: filters.to_date || undefined,
    refresh: refreshTick > 0 ? true : undefined,
  };

  const selectedId = customerId ? Number(customerId) : null;
  const { data, isLoading, error } = useConsumption(selectedId, params);

  function handlePresetChange(value: string) {
    setFilters({ ...filters, preset: value, from_date: "", to_date: "" });
  }

  if (!selectedId) {
    return (
      <div>
        <PageHeader title="Customer Consumption" description="Daily consumption trend for a customer" />
        <CustomerSelect customers={customers} value={customerId} onChange={setCustomerId} />
        <EmptyState message="Select a customer to view their consumption trend" />
      </div>
    );
  }

  const is404 = (error as any)?.response?.status === 404;

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error || !data) {
    return (
      <div>
        <PageHeader title="Customer Consumption" description="Daily consumption trend for a customer" />
        <CustomerSelect customers={customers} value={customerId} onChange={setCustomerId} />
        <EmptyState message={is404 ? "Customer not found" : "Failed to load consumption report"} />
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="Customer Consumption" description={`${data.customer_name} consumption trend`} />
      <CustomerSelect customers={customers} value={customerId} onChange={setCustomerId} />
      <PresetFilter
        preset={filters.preset}
        fromDate={filters.from_date}
        toDate={filters.to_date}
        onPresetChange={handlePresetChange}
        onFromDateChange={(v) => setFilters({ ...filters, from_date: v, preset: "" })}
        onToDateChange={(v) => setFilters({ ...filters, to_date: v, preset: "" })}
        onRefresh={() => setRefreshTick(Date.now())}
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <KpiCard title="Total Consumption" value={`${formatQuantity(data.total_consumption)} L`} />
        <KpiCard title="Average Daily" value={`${formatQuantity(data.average_daily)} L`} />
        <KpiCard title="Days With Data" value={data.days_with_data} sub={<TrendBadge changePercentage={data.trend.change_percentage} />} />
      </div>

      {!data.items.length ? (
        <EmptyState message="No consumption data found for the selected period" />
      ) : (
        <DataTable
          columns={[
            {
              key: "date",
              header: "Date",
              sortable: true,
              render: (d: ConsumptionDay) => formatDate(d.date),
            },
            {
              key: "total_quantity",
              header: "Total Quantity",
              sortable: true,
              render: (d: ConsumptionDay) => formatQuantity(d.total_quantity),
            },
            {
              key: "by_milk_type",
              header: "By Milk Type",
              render: (d: ConsumptionDay) =>
                d.by_milk_type.length
                  ? d.by_milk_type.map((m) => `${m.milk_type}: ${formatQuantity(m.quantity)} L`).join(", ")
                  : "—",
            },
          ]}
          data={data.items}
          keyExtractor={(d) => d.date}
        />
      )}
    </div>
  );
}

function CustomerSelect({
  customers,
  value,
  onChange,
}: {
  customers: { id: number; customer_code: string; customer_name: string }[] | undefined;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="max-w-sm mb-4">
      <Select
        label="Customer"
        options={customers?.map((c) => ({ value: c.id, label: `${c.customer_code} - ${c.customer_name}` })) || []}
        placeholder="Select a customer"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
