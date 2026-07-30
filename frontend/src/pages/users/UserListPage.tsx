import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/ui/PageHeader";
import DataTable from "../../components/ui/DataTable";
import Badge from "../../components/ui/Badge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import EmptyState from "../../components/ui/EmptyState";
import { useUsers } from "../../hooks/useUsers";
import type { UserResponse } from "../../api/users";

export default function UserListPage() {
  const navigate = useNavigate();
  const { data: users, isLoading, error } = useUsers();

  if (isLoading) return <LoadingSpinner className="mt-20" />;
  if (error) return <EmptyState message="Failed to load users" />;
  if (!users?.length) return <EmptyState message="No users found" actionLabel="Create User" onAction={() => navigate("/users/new")} />;

  return (
    <div>
      <PageHeader title="Users" description="Manage system users" actionLabel="Create User" onAction={() => navigate("/users/new")} />
      <DataTable
        columns={[
          { key: "username", header: "Username", sortable: true },
          { key: "role", header: "Role", sortable: true, render: (u: UserResponse) => <Badge status={u.role} /> },
          { key: "is_active", header: "Status", render: (u: UserResponse) => <Badge status={u.is_active ? "Active" : "Inactive"} /> },
        ]}
        data={users}
        keyExtractor={(u) => u.id}
      />
    </div>
  );
}
