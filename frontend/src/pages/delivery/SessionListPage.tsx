import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import Badge from "../../components/ui/Badge";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { PAGE_SIZE, SESSION_STATUS } from "../../lib/constants";
import { formatDate } from "../../lib/utils";
import { useDeliverySessions } from "../../hooks/useDeliverySessions";
import { useRoutes } from "../../hooks/useRoutes";
import { useEmployees } from "../../hooks/useEmployees";
import type { DeliverySessionResponse } from "../../types/delivery-session";

export default function SessionListPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [dateFilter, setDateFilter] = useState("");
  const [routeFilter, setRouteFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const { data: routes } = useRoutes();
  const { data: employees } = useEmployees();
  const { data, isLoading, error } = useDeliverySessions({
    skip: (page - 1) * PAGE_SIZE,
    limit: PAGE_SIZE,
    delivery_date: dateFilter || undefined,
    route_id: routeFilter ? Number(routeFilter) : undefined,
    status: statusFilter || undefined,
  });

  const routeNames = new Map((routes || []).map((r) => [r.id, r.route_name]));
  const partnerNames = new Map((employees || [])
    .filter((e) => e.role === "DELIVERY_PARTNER")
    .map((e) => [e.id, e.name]));

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load sessions" />;
  if (!data?.sessions?.length)
    return (
      <EmptyState
        message="No delivery sessions found"
        actionLabel="New Session"
        onAction={() => navigate("/delivery/sessions/new")}
      />
    );

  const sessions = data.sessions as DeliverySessionResponse[];

  return (
    <div>
      <PageHeader
        title="Delivery Sessions"
        description="Manage daily delivery sessions"
        actionLabel="New Session"
        onAction={() => navigate("/delivery/sessions/new")}
      />
      <div className="bg-white rounded-lg shadow p-4 mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input label="Delivery Date" type="date" value={dateFilter} onChange={(e) => { setDateFilter(e.target.value); setPage(1); }} />
        <Select
          label="Route"
          placeholder="All routes"
          options={(routes || []).map((r) => ({ value: r.id, label: `${r.route_code} - ${r.route_name}` }))}
          value={routeFilter}
          onChange={(e) => { setRouteFilter(e.target.value); setPage(1); }}
        />
        <Select
          label="Status"
          placeholder="All statuses"
          options={Object.entries(SESSION_STATUS).map(([value, meta]) => ({ value, label: meta.label }))}
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
        />
      </div>
      <DataTable
        columns={[
          {
            key: "route",
            header: "Route",
            sortable: true,
            render: (s: DeliverySessionResponse) => s.route_name || routeNames.get(s.route_id) || `Route #${s.route_id}`,
          },
          {
            key: "delivery_date",
            header: "Date",
            sortable: true,
            render: (s: DeliverySessionResponse) => formatDate(s.delivery_date),
          },
          {
            key: "shift",
            header: "Shift",
            render: (s: DeliverySessionResponse) => s.shift,
          },
          {
            key: "delivery_partner",
            header: "Partner",
            render: (s: DeliverySessionResponse) => s.delivery_partner_name || partnerNames.get(s.delivery_partner_id) || "—",
          },
          { key: "status", header: "Status", render: (s: DeliverySessionResponse) => <Badge status={s.status} /> },
          {
            key: "reconciliation_status",
            header: "Reconciliation",
            render: (s: DeliverySessionResponse) => <Badge status={s.reconciliation_status} />,
          },
          {
            key: "total_milk_loaded",
            header: "Loaded (L)",
            render: (s: DeliverySessionResponse) => (s.total_milk_loaded ? Number(s.total_milk_loaded).toFixed(2) : "—"),
          },
        ]}
        data={sessions}
        keyExtractor={(s) => s.id}
        page={page}
        pageSize={PAGE_SIZE}
        total={data.total}
        onPageChange={setPage}
        onRowClick={(s) => navigate(`/delivery/sessions/${s.id}`)}
      />
    </div>
  );
}
