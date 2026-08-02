export const SESSION_STATUS = {
  PLANNED: { label: "Planned", color: "slate" },
  STARTED: { label: "Started", color: "sky" },
  COMPLETED: { label: "Completed", color: "indigo" },
  CLOSED: { label: "Closed", color: "emerald" },
} as const;

export const DELIVERY_STATUS = {
  DELIVERED: { label: "Delivered", color: "emerald" },
  PENDING_TOKEN: { label: "Pending Token", color: "amber" },
  CASH_SALE: { label: "Cash Sale", color: "sky" },
  NOT_DELIVERED: { label: "Not Delivered", color: "red" },
  CANCELLED: { label: "Cancelled", color: "red" },
} as const;

export const PAYMENT_STATUS = {
  PAID: { label: "Paid", color: "emerald" },
  PARTIAL: { label: "Partial", color: "amber" },
  PENDING: { label: "Pending", color: "slate" },
} as const;

export const BOOK_ISSUE_STATUS = {
  WAITING: { label: "Waiting", color: "amber" },
  ACTIVE: { label: "Active", color: "emerald" },
  COMPLETED: { label: "Completed", color: "indigo" },
} as const;

export const RECONCILIATION_STATUS = {
  BALANCED: { label: "Balanced", color: "emerald" },
  UNBALANCED: { label: "Unbalanced", color: "red" },
  PENDING: { label: "Pending", color: "amber" },
} as const;

export const BILL_STATUS = {
  PENDING: { label: "Pending", color: "slate" },
  PARTIAL: { label: "Partial", color: "amber" },
  PAID: { label: "Paid", color: "emerald" },
  OVERDUE: { label: "Overdue", color: "red" },
  CANCELLED: { label: "Cancelled", color: "red" },
} as const;

export const STATUS_BADGE_MAP: Record<string, { label: string; color: string }> = {
  ...SESSION_STATUS,
  ...DELIVERY_STATUS,
  ...PAYMENT_STATUS,
  ...BOOK_ISSUE_STATUS,
  ...RECONCILIATION_STATUS,
  ...BILL_STATUS,
  ACTIVE: { label: "Active", color: "emerald" },
  INACTIVE: { label: "Inactive", color: "slate" },
};

export const PAGE_SIZE = 50;

export const ROLES = ["OWNER", "ADMIN", "CHECKER", "DELIVERY_PARTNER", "EMPLOYEE"] as const;

export const SHIFTS = ["MORNING", "EVENING"] as const;

export const EXCEPTION_TYPES = ["VACATION", "NO_MILK", "HOLIDAY"] as const;

export const PAYMENT_MODES = ["CASH", "UPI", "CARD", "CHEQUE", "BANK_TRANSFER"] as const;

export const PAYMENT_TYPES = ["ADVANCE", "BILL_PAYMENT"] as const;

export const TOKEN_PAYMENT_MODES = ["PREPAID", "POSTPAID"] as const;

export const REPORT_PRESETS = [
  { value: "today", label: "Today" },
  { value: "yesterday", label: "Yesterday" },
  { value: "this_week", label: "This Week" },
  { value: "last_week", label: "Last Week" },
  { value: "this_month", label: "This Month" },
  { value: "last_month", label: "Last Month" },
  { value: "this_year", label: "This Year" },
] as const;
