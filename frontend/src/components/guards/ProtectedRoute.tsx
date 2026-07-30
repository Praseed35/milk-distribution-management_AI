import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../providers/AuthProvider";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!isAuthenticated) {
    sessionStorage.setItem("return_url", location.pathname + location.search);
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
