import type { UserRole } from "../types/auth";

interface NavItem {
  label: string;
  path: string;
  roles: UserRole[];
  children?: NavItem[];
}

export const navigation: NavItem[] = [
  {
    label: "Dashboard",
    path: "/",
    roles: ["OWNER", "ADMIN", "CHECKER", "DELIVERY_PARTNER"],
  },
  {
    label: "Master Data",
    path: "#",
    roles: ["OWNER", "ADMIN", "CHECKER"],
    children: [
      { label: "Routes", path: "/routes", roles: ["OWNER", "ADMIN"] },
      { label: "Customers", path: "/customers", roles: ["OWNER", "ADMIN", "CHECKER"] },
      { label: "Milk Types", path: "/milk-types", roles: ["OWNER", "ADMIN", "CHECKER"] },
      { label: "Employees", path: "/employees", roles: ["OWNER", "ADMIN"] },
      { label: "Users", path: "/users", roles: ["OWNER", "ADMIN"] },
    ],
  },
  {
    label: "Operations",
    path: "#",
    roles: ["OWNER", "ADMIN", "CHECKER"],
    children: [
      { label: "Subscriptions", path: "/subscriptions", roles: ["OWNER", "ADMIN", "CHECKER"] },
      { label: "Exceptions", path: "/delivery-exceptions", roles: ["OWNER", "ADMIN", "CHECKER"] },
      { label: "Token Identities", path: "/token-identities", roles: ["OWNER", "ADMIN"] },
      { label: "Token Book Issues", path: "/token-book-issues", roles: ["OWNER", "ADMIN"] },
      { label: "Token Payments", path: "/token-book-payments", roles: ["OWNER", "ADMIN", "CHECKER"] },
    ],
  },
  {
    label: "Delivery",
    path: "#",
    roles: ["OWNER", "ADMIN", "CHECKER", "DELIVERY_PARTNER"],
    children: [
      { label: "Sessions", path: "/delivery/sessions", roles: ["OWNER", "ADMIN", "CHECKER"] },
    ],
  },
  {
    label: "Finance",
    path: "#",
    roles: ["OWNER", "ADMIN"],
    children: [
      { label: "Payments", path: "/payments", roles: ["OWNER", "ADMIN"] },
      { label: "Bills", path: "/payments/bills", roles: ["OWNER", "ADMIN"] },
      { label: "Outstanding", path: "/payments/outstanding", roles: ["OWNER", "ADMIN"] },
    ],
  },
  {
    label: "Reports",
    path: "#",
    roles: ["OWNER", "ADMIN", "CHECKER"],
    children: [
      { label: "Dashboard", path: "/reports/dashboard", roles: ["OWNER", "ADMIN", "CHECKER"] },
      { label: "Route Delivery", path: "/reports/route-delivery", roles: ["OWNER", "ADMIN"] },
      { label: "Revenue", path: "/reports/revenue", roles: ["OWNER"] },
      { label: "Consumption", path: "/reports/consumption", roles: ["OWNER", "ADMIN", "CHECKER"] },
      { label: "Token Utilization", path: "/reports/token-utilization", roles: ["OWNER", "ADMIN"] },
      { label: "Collection Efficiency", path: "/reports/collection-efficiency", roles: ["OWNER", "ADMIN"] },
    ],
  },
];

export function filterNavByRole(items: NavItem[], role: UserRole): NavItem[] {
  return items
    .filter((item) => item.roles.includes(role))
    .map((item) => ({
      ...item,
      children: item.children ? filterNavByRole(item.children, role) : undefined,
    }));
}
