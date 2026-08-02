export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
  }).format(amount);
}

export function formatQuantity(quantity: number): string {
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 2,
  }).format(quantity);
}

export function formatPercent(value: number): string {
  return `${new Intl.NumberFormat("en-IN", { maximumFractionDigits: 1 }).format(value)}%`;
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    ACTIVE: "bg-emerald-100 text-emerald-800",
    INACTIVE: "bg-slate-100 text-slate-600",
    DELIVERED: "bg-emerald-100 text-emerald-800",
    PENDING_TOKEN: "bg-amber-100 text-amber-800",
    CASH_SALE: "bg-sky-100 text-sky-800",
    NOT_DELIVERED: "bg-red-100 text-red-800",
    CANCELLED: "bg-red-100 text-red-800",
    PLANNED: "bg-slate-100 text-slate-600",
    STARTED: "bg-sky-100 text-sky-800",
    COMPLETED: "bg-indigo-100 text-indigo-800",
    CLOSED: "bg-emerald-100 text-emerald-800",
    BALANCED: "bg-emerald-100 text-emerald-800",
    UNBALANCED: "bg-red-100 text-red-800",
    PENDING: "bg-amber-100 text-amber-800",
    PAID: "bg-emerald-100 text-emerald-800",
    PARTIAL: "bg-amber-100 text-amber-800",
    WAITING: "bg-amber-100 text-amber-800",
    PREPAID: "bg-indigo-100 text-indigo-800",
    POSTPAID: "bg-amber-100 text-amber-800",
    OVERDUE: "bg-red-100 text-red-800",
  };
  return colors[status] || "bg-slate-100 text-slate-600";
}
