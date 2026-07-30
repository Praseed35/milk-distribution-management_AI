import { useAuth } from "../../providers/AuthProvider";
import ForbiddenPage from "../../pages/ForbiddenPage";
import type { UserRole } from "../../types/auth";

interface RoleGuardProps {
  roles: UserRole[];
  children: React.ReactNode;
}

export default function RoleGuard({ roles, children }: RoleGuardProps) {
  const { user } = useAuth();

  if (!user || !roles.includes(user.role)) {
    return <ForbiddenPage />;
  }

  return <>{children}</>;
}
