import { test, expect, type APIRequestContext, type Page } from "@playwright/test";
import { futureDate } from "./helpers";

const ROUTE_OPTION = "R001 - Downtown Route";

async function loginAsOwner(request: APIRequestContext): Promise<string> {
  const res = await request.post("/api/v1/auth/login", {
    data: { username: "owner", password: "owner123" },
  });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  return body.access_token as string;
}

async function createSession(page: Page, shift: "MORNING" | "EVENING", date?: string) {
  await page.goto("/delivery/sessions/new");
  await page.getByLabel("Route").selectOption({ label: ROUTE_OPTION });
  await page.getByLabel("Delivery Date").fill(date ?? futureDate(30));
  await page.getByLabel("Shift").selectOption({ label: shift });
  await page.getByLabel("Delivery Partner").selectOption({ label: "E00002 - Suresh Babu" });
  await page.getByRole("button", { name: "Create Session" }).click();
  await expect(page).toHaveURL(/\/delivery\/sessions\/\d+$/);
}

function sessionIdFromUrl(page: Page): number {
  const match = page.url().match(/\/delivery\/sessions\/(\d+)$/);
  return Number(match![1]);
}

async function checklistQuantities(
  request: APIRequestContext,
  token: string,
  sessionId: number
): Promise<{ name: string; quantity: number }[]> {
  const res = await request.get(`/api/v1/deliveries/sessions/${sessionId}/checklist`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  return body.customers.map((c: { customer_name: string; quantity: number }) => ({
    name: c.customer_name,
    quantity: Number(c.quantity),
  }));
}

test.describe("delivery sessions (owner)", () => {
  test("creating a session generates the morning checklist for the route", async ({ page }) => {
    await createSession(page, "MORNING");

    const table = page.locator("table").first();
    await expect(table.locator("tbody tr")).toHaveCount(3);
    await expect(table).toContainText("Rajesh Kumar");
    await expect(table).toContainText("Priya Sharma");
    await expect(table).toContainText("Karthik Rao");
    await expect(page.getByText("PLANNED").first()).toBeVisible();
  });

  test("creating an evening session only includes evening subscriptions", async ({ page }) => {
    await createSession(page, "EVENING", futureDate(31));

    const table = page.locator("table").first();
    await expect(table.locator("tbody tr")).toHaveCount(2);
    await expect(table).toContainText("Rajesh Kumar");
    await expect(table).toContainText("Karthik Rao");
    await expect(table).not.toContainText("Priya Sharma");
  });

  test("create session validates required fields", async ({ page }) => {
    await page.goto("/delivery/sessions/new");
    await page.getByRole("button", { name: "Create Session" }).click();

    await expect(page.getByText("Route is required")).toBeVisible();
    await expect(page.getByText("Delivery date is required")).toBeVisible();
    await expect(page.getByText("Delivery partner is required")).toBeVisible();
    await expect(page).toHaveURL(/\/delivery\/sessions\/new$/);
  });

  test("session lifecycle: dispatch, deliver all, complete, and close when balanced", async ({
    page,
    request,
  }) => {
    await createSession(page, "MORNING", futureDate(35));
    const sessionId = sessionIdFromUrl(page);
    const token = await loginAsOwner(request);
    const checklist = await checklistQuantities(request, token, sessionId);
    expect(checklist).toHaveLength(3);
    const loaded = checklist.reduce((sum, c) => sum + c.quantity, 0);

    await page.getByLabel("Total Milk Loaded (L)").fill(String(loaded));
    await page.getByRole("button", { name: "Record Dispatch" }).click();
    await page.getByRole("button", { name: "Confirm" }).click();
    await expect(page.getByText("STARTED").first()).toBeVisible();

    const rows = page.locator("table").first().locator("tbody tr");
    await expect(rows).toHaveCount(3);
    for (const customer of ["Rajesh Kumar", "Priya Sharma", "Karthik Rao"]) {
      const row = page.locator("table").first().locator("tbody tr", { hasText: customer });
      await row.getByRole("combobox").selectOption({ label: "Delivered" });
      await expect(row).toContainText("DELIVERED");
    }

    await page.getByRole("button", { name: "Complete Session" }).click();
    await page.getByRole("button", { name: "Confirm" }).click();
    await expect(page.getByText("COMPLETED").first()).toBeVisible();

    await page.getByRole("button", { name: "Close Session" }).click();
    await page.getByRole("button", { name: "Confirm" }).click();
    await expect(page.getByText("CLOSED").first()).toBeVisible();

    await expect(page.getByRole("button", { name: "Edit Deliveries" })).toBeVisible();
  });
});
