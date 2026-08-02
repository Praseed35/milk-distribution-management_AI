import { test, expect, type APIRequestContext, type Page } from "@playwright/test";
import { futureDate } from "./helpers";

test.describe.configure({ mode: "serial" });

const ROUTE_OPTION = "R001 - Downtown Route";
const DELIVERY_PARTNER_OPTION = "E00002 - Suresh Babu";
const BILL_CUSTOMER_OPTION = "C00011 - Karthik Rao";
const TEST_UNIT_PRICE = 50;
const TOKEN_CUSTOMER_ID = 2;
const TOKEN_MILK_TYPE_ID = 5;

function formatQuantity(n: number): string {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(n);
}

function todayIso(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

function tokenNumber(): number {
  return 2000 + Math.floor(Math.random() * 7000);
}

function issueNumber(): number {
  return 500 + Math.floor(Math.random() * 400);
}

function parseCurrency(text: string): number[] {
  return [...text.matchAll(/₹([\d,]+(?:\.\d{1,2})?)/g)].map((m) => Number(m[1].replace(/,/g, "")));
}

async function loginAsOwner(request: APIRequestContext): Promise<string> {
  const res = await request.post("/api/v1/auth/login", {
    data: { username: "owner", password: "owner123" },
  });
  expect(res.ok()).toBeTruthy();
  return (await res.json()).access_token as string;
}

interface ChecklistRow {
  customer_name: string;
  quantity: number;
}

interface SessionDelivery {
  milk_type_id: number;
}

async function checklistQuantities(
  request: APIRequestContext,
  token: string,
  sessionId: number
): Promise<ChecklistRow[]> {
  const res = await request.get(`/api/v1/deliveries/sessions/${sessionId}/checklist`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(res.ok()).toBeTruthy();
  return (await res.json()).customers.map((c: { customer_name: string; quantity: number }) => ({
    customer_name: c.customer_name,
    quantity: Number(c.quantity),
  }));
}

/** Prices the session's milk types so generated bills have non-zero totals. */
async function setMilkPrices(request: APIRequestContext, token: string, deliveries: SessionDelivery[]): Promise<void> {
  const mtRes = await request.get("/api/v1/milk-types", { headers: { Authorization: `Bearer ${token}` } });
  expect(mtRes.ok()).toBeTruthy();
  const milkTypes = await mtRes.json();
  const priced = new Set<number>();
  for (const d of deliveries) {
    if (priced.has(d.milk_type_id)) continue;
    priced.add(d.milk_type_id);
    const mt = milkTypes.find((m: { id: number }) => m.id === d.milk_type_id);
    expect(mt).toBeDefined();
    const put = await request.put(`/api/v1/milk-types/${d.milk_type_id}`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        milk_name: mt.milk_name,
        volume_ml: mt.volume_ml,
        unit_price: TEST_UNIT_PRICE,
        description: mt.description ?? null,
      },
    });
    expect(put.ok()).toBeTruthy();
  }
}

/** Marks every delivery in `sessionId` as DELIVERED via the API (retrying on optimistic-lock conflicts). */
async function markAllDelivered(request: APIRequestContext, token: string, sessionId: number): Promise<void> {
  await expect
    .poll(
      async () => {
        const res = await request.get(`/api/v1/deliveries/session/${sessionId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        expect(res.ok()).toBeTruthy();
        const data = await res.json();
        for (const d of data.deliveries) {
          if (d.delivery_status === "DELIVERED") continue;
          const put = await request.put(`/api/v1/deliveries/${d.id}`, {
            headers: { Authorization: `Bearer ${token}` },
            data: {
              delivery_status: "DELIVERED",
              delivered_quantity: d.planned_quantity,
              version: d.version,
            },
          });
          if (!put.ok()) return -1;
        }
        return data.deliveries.filter((d: { delivery_status: string }) => d.delivery_status === "DELIVERED").length;
      },
      { timeout: 30000 }
    )
    .toBeGreaterThan(0);
}

/** Creates a session on route R001, dispatches, marks all deliveries DELIVERED and completes it. */
async function createCompletedSession(
  page: Page,
  request: APIRequestContext,
  date: string,
  shift = "MORNING"
): Promise<{ date: string; sessionId: number; checklist: ChecklistRow[]; loaded: number }> {
  const token = await loginAsOwner(request);

  await page.goto("/delivery/sessions/new");
  await page.getByLabel("Route").selectOption({ label: ROUTE_OPTION });
  await page.getByLabel("Delivery Date").fill(date);
  await page.getByLabel("Shift").selectOption({ label: shift });
  await page.getByLabel("Delivery Partner").selectOption({ label: DELIVERY_PARTNER_OPTION });
  await page.getByRole("button", { name: "Create Session" }).click();
  await expect(page).toHaveURL(/\/delivery\/sessions\/\d+$/);

  const sessionId = Number(page.url().match(/\/delivery\/sessions\/(\d+)$/)![1]);
  const checklist = await checklistQuantities(request, token, sessionId);
  expect(checklist.length).toBeGreaterThan(0);
  const loaded = checklist.reduce((sum, c) => sum + c.quantity, 0);

  await page.getByLabel("Total Milk Loaded (L)").fill(String(loaded));
  await page.getByRole("button", { name: "Record Dispatch" }).click();
  await page.getByRole("button", { name: "Confirm" }).click();

  await markAllDelivered(request, token, sessionId);

  await page.getByRole("button", { name: "Complete Session" }).click();
  await page.getByRole("button", { name: "Confirm" }).click();
  await expect(page.getByText("COMPLETED").first()).toBeVisible();

  const dlRes = await request.get(`/api/v1/deliveries/session/${sessionId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(dlRes.ok()).toBeTruthy();
  await setMilkPrices(request, token, (await dlRes.json()).deliveries);

  return { date, sessionId, checklist, loaded };
}

/** Generates a bill for Karthik Rao for `date` and records a partial bill payment. */
async function generateBillAndPay(
  page: Page,
  request: APIRequestContext,
  date: string
): Promise<{ billed: number; partial: number }> {
  const token = await loginAsOwner(request);

  await page.goto("/payments/bills/generate");
  await page.getByText(BILL_CUSTOMER_OPTION).click();
  await page.getByLabel("Period Start").fill(date);
  await page.getByLabel("Period End").fill(date);
  await page.getByLabel("Due Date").fill(date);
  await page.getByRole("button", { name: "Generate Bills" }).click();
  await expect(page.getByText(/Bill #\d+ created/)).toBeVisible();

  const res = await request.get("/api/v1/payments/bills/", { headers: { Authorization: `Bearer ${token}` } });
  expect(res.ok()).toBeTruthy();
  const bills = await res.json();
  const bill = bills.find((b: { bill_period_start: string }) => b.bill_period_start === date);
  expect(bill).toBeDefined();
  const billed = Number(bill.total_amount);
  expect(billed).toBeGreaterThan(0);
  const partial = Math.round(billed * 60) / 100;

  await page.goto("/payments/new");
  await page.getByLabel("Customer").selectOption({ label: BILL_CUSTOMER_OPTION });
  await page.getByLabel("Payment Type").selectOption({ label: "Bill Payment" });
  await page.getByLabel("Amount").fill(String(partial));
  await page.getByLabel("Bill").selectOption({ value: String(bill.id) });
  await page.getByRole("button", { name: "Record Payment" }).click();
  await expect(page).toHaveURL(/\/payments$/);

  return { billed, partial };
}

async function setReportDates(page: Page, from: string, to: string) {
  await page.getByLabel("From", { exact: true }).fill(from);
  await page.getByLabel("To", { exact: true }).fill(to);
  await page.getByRole("button", { name: "Refresh" }).click();
}

async function login(page: Page, username: string, password: string) {
  await page.goto("/login");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/reports\/dashboard/);
}

test.describe("reports", () => {
  test("dashboard is the landing page and reflects today's completed session", async ({ page, request }) => {
    const { loaded } = await createCompletedSession(page, request, todayIso());

    await page.goto("/");
    await expect(page).toHaveURL(/\/reports\/dashboard/);
    await expect(page.getByText("Operational Dashboard")).toBeVisible();

    const sessionsCard = page.locator("div.bg-white.rounded-lg.shadow.p-5", { hasText: "Sessions Today" });
    const sessionsText = await sessionsCard.innerText();
    expect(Number((sessionsText.match(/\d+/) || ["0"])[0])).toBeGreaterThanOrEqual(1);

    await expect(page.getByText(/Delivered: [1-9]/)).toBeVisible();

    const deliveredCard = page.locator("div.bg-white.rounded-lg.shadow.p-5", { hasText: "Milk Delivered" });
    await expect(deliveredCard).toContainText(`${formatQuantity(loaded)} L`);
  });

  test("route delivery report aggregates totals and exports CSV", async ({ page, request }) => {
    const date = futureDate(80);
    const { loaded, checklist } = await createCompletedSession(page, request, date);

    await page.goto("/reports/route-delivery");
    await setReportDates(page, date, date);

    const row = page.getByRole("table").locator("tbody tr", { hasText: ROUTE_OPTION });
    await expect(row).toContainText("Balanced");
    await expect(row).toContainText("1");
    await expect(row).toContainText(String(checklist.length));
    await expect(row).toContainText(formatQuantity(loaded));

    const totalLoaded = page.locator("div.bg-white.rounded-lg.shadow.p-4", { hasText: "Total Loaded" });
    await expect(totalLoaded).toContainText(`${formatQuantity(loaded)} L`);
    const totalDelivered = page.locator("div.bg-white.rounded-lg.shadow.p-4", { hasText: "Total Delivered" });
    await expect(totalDelivered).toContainText(`${formatQuantity(loaded)} L`);

    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: "Download CSV" }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/^route-delivery-report-.*\.csv$/);
  });

  test("consumption report shows the customer's daily delivery and milk type breakdown", async ({ page, request }) => {
    const date = futureDate(90);
    const { checklist } = await createCompletedSession(page, request, date);
    const rajeshRows = checklist.filter((c) => c.customer_name === "Rajesh Kumar");
    expect(rajeshRows.length).toBeGreaterThan(0);
    const rajeshTotal = rajeshRows.reduce((sum, c) => sum + c.quantity, 0);

    await page.goto("/reports/consumption/1");
    await expect(page).toHaveURL(/\/reports\/consumption\/1$/);
    await setReportDates(page, date, date);

    const totalCard = page.locator("div.bg-white.rounded-lg.shadow.p-5", { hasText: "Total Consumption" });
    await expect(totalCard).toContainText(`${formatQuantity(rajeshTotal)} L`);

    const table = page.getByRole("table");
    const formattedDate = new Date(date).toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
    await expect(table).toContainText(formattedDate);
    await expect(table).toContainText(formatQuantity(rajeshTotal));
    await expect(page.getByText("undefined")).toHaveCount(0);
  });

  test("revenue report shows bill payment revenue and collection efficiency shows aging", async ({ page, request }) => {
    const date = todayIso();
    await createCompletedSession(page, request, date, "EVENING");
    await generateBillAndPay(page, request, date);

    await page.goto("/reports/revenue");
    await setReportDates(page, date, date);

    const totalCard = page.locator("div.bg-white.rounded-lg.shadow.p-5", { hasText: "Total Revenue" });
    const revenueText = await totalCard.innerText();
    const revenue = parseCurrency(revenueText)[0] ?? 0;
    expect(revenue).toBeGreaterThan(0);

    const bySource = page.locator("div.bg-white.rounded-lg.shadow.p-4", { hasText: "By Source" });
    await expect(bySource).toContainText("customer_bill_payments");

    await page.goto("/reports/collection-efficiency");
    await setReportDates(page, date, date);

    const row = page.getByRole("table").locator("tbody tr", { hasText: BILL_CUSTOMER_OPTION });
    await expect(row).toContainText("Current:");
    await expect(row).toContainText("31–60d");
    await expect(row).toContainText("61–90d");
    await expect(row).toContainText("90d+");

    const amounts = parseCurrency(await row.innerText());
    const balance = amounts[2];
    const agingSum = amounts.slice(3).reduce((sum, n) => sum + n, 0);
    expect(Math.abs(agingSum - balance)).toBeLessThan(0.01);
  });

  test("token utilization flags books below the low threshold", async ({ page, request }) => {
    const token = await loginAsOwner(request);

    const identRes = await request.post("/api/v1/token-books/identities", {
      headers: { Authorization: `Bearer ${token}` },
      data: { customer_id: TOKEN_CUSTOMER_ID, milk_type_id: TOKEN_MILK_TYPE_ID, token_number: tokenNumber() },
    });
    expect(identRes.ok()).toBeTruthy();
    const identityId = (await identRes.json()).id as number;

    const issueRes = await request.post("/api/v1/token-books/issues", {
      headers: { Authorization: `Bearer ${token}` },
      data: { token_identity_id: identityId, issue_number: issueNumber(), remarks: "reports e2e" },
    });
    expect(issueRes.ok()).toBeTruthy();
    const issueId = (await issueRes.json()).id as number;

    const patchRes = await request.put(`/api/v1/token-books/issues/${issueId}`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { current_sheet: 27 },
    });
    expect(patchRes.ok()).toBeTruthy();

    await page.goto("/reports/token-utilization");
    await expect(page.getByRole("table")).toContainText("Priya Sharma");

    const belowCard = page.locator("div.bg-white.rounded-lg.shadow.p-5", { hasText: "Books Below Threshold" });
    await expect(belowCard).toContainText("1");

    await page.getByLabel("Low Threshold (%)", { exact: true }).fill("5");
    await expect(belowCard).toContainText("0");
  });

  test("report pages are role-restricted", async ({ browser }) => {
    const checker = await browser.newContext();
    const checkerPage = await checker.newPage();
    await login(checkerPage, "checker1", "checker123");
    await checkerPage.goto("/reports/token-utilization");
    await expect(checkerPage.getByText("You do not have permission to access this page.")).toBeVisible();
    await checkerPage.goto("/reports/collection-efficiency");
    await expect(checkerPage.getByText("You do not have permission to access this page.")).toBeVisible();
    await checkerPage.goto("/reports/revenue");
    await expect(checkerPage.getByText("You do not have permission to access this page.")).toBeVisible();
    await checker.close();

    const employee = await browser.newContext();
    const employeePage = await employee.newPage();
    await login(employeePage, "employee1", "emp123");
    await expect(employeePage.getByText("You do not have permission to access this page.")).toBeVisible();
    await employee.close();
  });

  test("delivery partner sees their own route scope", async ({ browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await login(page, "delivery1", "delivery123");

    await page.goto("/");
    await expect(page).toHaveURL(/\/reports\/dashboard/);
    await expect(page.getByText("Operational Dashboard")).toBeVisible();

    await page.goto("/reports/route-delivery");
    await expect(page.getByText("Route Delivery Report")).toBeVisible();

    await page.goto("/reports/revenue");
    await expect(page.getByText("You do not have permission to access this page.")).toBeVisible();
    await context.close();
  });
});
