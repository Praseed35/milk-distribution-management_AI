/** Returns a unique string for a given prefix, e.g. `route_20260731_abc12`. */
export function unique(prefix: string): string {
  const rand = Math.floor(Math.random() * 0xffff).toString(36);
  return `${prefix}_${Date.now().toString(36)}_${rand}`;
}

/** Returns an ISO date string `days` days from today. */
export function futureDate(days = 30): string {
  return new Date(Date.now() + days * 86_400_000).toISOString().slice(0, 10);
}

/** Uniquely-suffixed, always-valid 10-digit phone number. */
export function uniquePhone(): string {
  const digits = String(Date.now()).slice(-9);
  return `9${digits.padStart(9, "0")}`;
}
