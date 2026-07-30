import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../providers/AuthProvider";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/change-password": "Change Password",
  "/routes": "Routes",
  "/customers": "Customers",
  "/milk-types": "Milk Types",
  "/employees": "Employees",
  "/users": "Users",
  "/subscriptions": "Subscriptions",
  "/delivery-exceptions": "Delivery Exceptions",
  "/token-identities": "Token Identities",
  "/token-book-issues": "Token Book Issues",
  "/token-book-payments": "Token Book Payments",
  "/delivery/sessions": "Delivery Sessions",
  "/payments": "Payments",
  "/payments/bills": "Bills",
  "/payments/outstanding": "Outstanding",
  "/reports/dashboard": "Dashboard",
  "/reports/route-delivery": "Route Delivery Report",
  "/reports/revenue": "Revenue Report",
  "/reports/consumption": "Customer Consumption",
  "/reports/token-utilization": "Token Utilization",
  "/reports/collection-efficiency": "Collection Efficiency",
};

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const title = Object.entries(pageTitles).find(([path]) =>
    location.pathname === path || location.pathname.startsWith(path + "/")
  )?.[1] || "Milk Management";

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
      <h1 className="text-xl font-semibold text-slate-800">{title}</h1>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-600">
          {user?.username} ({user?.role})
        </span>
        <button
          onClick={() => navigate("/change-password")}
          className="text-sm text-indigo-600 hover:text-indigo-800"
        >
          Change Password
        </button>
        <button
          onClick={() => {
            logout();
            navigate("/login");
          }}
          className="text-sm text-red-600 hover:text-red-800"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
