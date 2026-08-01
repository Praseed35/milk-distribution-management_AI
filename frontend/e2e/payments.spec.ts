import { test, expect, type APIRequestContext, type Page } from "@playwright/test";
import { futureDate } from "./helpers";

const CUSTOMER_OPTION = "C00002 - Priya Sharma";
const BILL_CUSTOMER_ID = 1;
const BILL_CUSTOMER_NAME = "Rajesh Kumar";
const BILL_CUSTOMER_OPTION = "C00001 - Rajesh Kumar";
const ROUTE_OPTION = "R001 - Downtown Route";
const TEST_UNIT_PRICE = 50;

async function loginAsOwner(request: APIRequestContext): Promise<string> {
  const res = await request.post("/api/v1/auth/login", {
    data: { username: "owner", password: "owner123" },
  });
  expect(res.ok()).toBeTruthy();
  return (await res.json()).access_token as string;
}

interface SessionDelivery {
  id: number;
  customer_id: number;
  milk_type_id: number;
  delivered_quantity: number;
  planned_quantity: number;
  delivery_status: string;
}

async function checklistTotal(request: APIRequestContext, token: string, sessionId: number): Promise<number> {
  const res = await request.get(`/api/v1/deliveries/sessions/${sessionId}/checklist`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  return body.customers.reduce((sum: number, c: { quantity: number }) => sum + Number(c.quantity), 0);
}

/** Seeds unit prices on the session's milk types so generated bills have non-zero totals. */
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

/** Creates + dispatches a morning session, marks all deliveries DELIVERED, completes it, and prices the milk. */
async function setupDeliveredSession(page: Page, request: APIRequestContext): Promise<{ date: string; expectedTotal: number }> {
  const date = futureDate(40);
  await page.goto("/delivery/sessions/new");
  await page.getByLabel("Route").selectOption({ label: ROUTE_OPTION });
  await page.getByLabel("Delivery Date").fill(date);
  await page.getByLabel("Shift").selectOption({ label: "MORNING" });
  await page.getByLabel("Delivery Partner").selectOption({ label: "E00002 - Suresh Babu" });
  await page.getByRole("button", { name: "Create Session" }).click();
  await expect(page).toHaveURL(/\/delivery\/sessions\/\d+$/);

  const sessionId = Number(page.url().match(/\/delivery\/sessions\/(\d+)$/)![1]);
  const token = await loginAsOwner(request);
  const loaded = await checklistTotal(request, token, sessionId);

  await page.getByLabel("Total Milk Loaded (L)").fill(String(loaded));
  await page.getByRole("button", { name: "Record Dispatch" }).click();
  await page.getByRole("button", { name: "Confirm" }).click();

  const rows = page.locator("table").first().locator("tbody tr");
  const rowCount = await rows.count();
  expect(rowCount).toBeGreaterThan(0);
  for (let i = 0; i < rowCount; i++) {
    await rows.nth(i).getByRole("combobox").selectOption({ label: "Delivered" });
    await expect(rows.nth(i)).toContainText("DELIVERED");
  }

  await page.getByRole("button", { name: "Complete Session" }).click();
  await page.getByRole("button", { name: "Confirm" }).click();
  await expect(page.getByText("COMPLETED").first()).toBeVisible();

  const dlRes = await request.get(`/api/v1/deliveries/session/${sessionId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(dlRes.ok()).toBeTruthy();
  const deliveries: SessionDelivery[] = (await dlRes.json()).deliveries;
  await setMilkPrices(request, token, deliveries);

  const expectedTotal = deliveries
    .filter((d) => d.customer_id === BILL_CUSTOMER_ID)
    .reduce((sum, d) => sum + Number(d.delivered_quantity || d.planned_quantity) * TEST_UNIT_PRICE, 0);
  expect(expectedTotal).toBeGreaterThan(0);

  return { date, expectedTotal };
}

async function recordBillPayment(page: Page, amount: number, billId: number) {
  await page.goto("/payments/new");
  await page.getByLabel("Customer").selectOption({ label: BILL_CUSTOMER_OPTION });
  await page.getByLabel("Payment Type").selectOption({ label: "Bill Payment" });
  await page.getByLabel("Amount").fill(String(amount));
  await page.getByLabel("Bill").selectOption({ value: String(billId) });
  await page.getByRole("button", { name: "Record Payment" }).click();
  await expect(page).toHaveURL(/\/payments$/);
}

test.describe("payments (owner)", () => {
  test("records an advance payment and shows it in history", async ({ page }) => {
    await page.goto("/payments/new");
    await page.getByLabel("Customer").selectOption({ label: CUSTOMER_OPTION });
    await page.getByLabel("Amount").fill("150.00");
    await page.getByRole("button", { name: "Record Payment" }).click();

    await expect(page).toHaveURL(/\/payments$/);
    await expect(page.getByRole("table")).toContainText("Priya Sharma");
    await expect(page.getByRole("table")).toContainText("150.00");
  });

  test("advance payment form validates required fields", async ({ page }) => {
    await page.goto("/payments/new");
    await page.getByRole("button", { name: "Record Payment" }).click();

    await expect(page.getByText("Customer is required")).toBeVisible();
    await expect(page.getByText("Amount must be greater than 0")).toBeVisible();
    await expect(page).toHaveURL(/\/payments\/new$/);
  });

  test("bill payment without selecting a bill is blocked", async ({ page }) => {
    await page.goto("/payments/new");
    await page.getByLabel("Customer").selectOption({ label: CUSTOMER_OPTION });
    await page.getByLabel("Payment Type").selectOption({ label: "Bill Payment" });
    await page.getByLabel("Amount").fill("50");
    await page.getByRole("button", { name: "Record Payment" }).click();

    await expect(page.getByText("A bill is required for bill payments")).toBeVisible();
    await expect(page).toHaveURL(/\/payments\/new$/);
  });

  test("generates a bill, records a bill payment, and manages status", async ({ page, request }) => {
    const { date, expectedTotal } = await setupDeliveredSession(page, request);
    const token = await loginAsOwner(request);

    await page.goto("/payments/bills/generate");
    await page.getByText(BILL_CUSTOMER_OPTION).click();
    await page.getByLabel("Period Start").fill(date);
    await page.getByLabel("Period End").fill(date);
    await page.getByRole("button", { name: "Generate Bills" }).click();
    await expect(page.getByText(/Bill #\d+ created/)).toBeVisible();

    const res = await request.get("/api/v1/payments/bills/", {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const bills = await res.json();
    const bill = bills.find((b: { bill_period_start: string }) => b.bill_period_start === date);
    expect(bill).toBeDefined();
    expect(Number(bill.total_amount)).toBe(expectedTotal);

    await page.goto("/payments/bills");
    await expect(page.getByRole("table")).toContainText(BILL_CUSTOMER_NAME);

    const partial = Math.round(expectedTotal * 60) / 100;
    const remainder = Math.round((expectedTotal - partial) * 100) / 100;

    await recordBillPayment(page, partial, bill.id);

    const outRes = await request.get(`/api/v1/payments/outstanding/${BILL_CUSTOMER_ID}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(outRes.ok()).toBeTruthy();
    const outstanding = await outRes.json();
    expect(Number(outstanding.total_billed)).toBe(expectedTotal);
    expect(Number(outstanding.total_paid)).toBe(partial);
    expect(Number(outstanding.balance)).toBe(Number(outstanding.total_billed) - Number(outstanding.total_paid));

    const billRes = await request.get(`/api/v1/payments/bills/${bill.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(billRes.ok()).toBeTruthy();
    expect((await billRes.json()).status).toBe("PARTIAL");

    await recordBillPayment(page, remainder, bill.id);

    const paidRes = await request.get(`/api/v1/payments/bills/${bill.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(paidRes.ok()).toBeTruthy();
    expect((await paidRes.json()).status).toBe("PAID");

    await page.goto(`/payments/bills/${bill.id}`);
    await expect(page.getByText("PAID").first()).toBeVisible();
    await page.getByLabel("Status").selectOption({ label: "Overdue" });
    await page.getByRole("button", { name: "Update Status" }).first().click();
    await page.getByRole("button", { name: "Update Status" }).last().click();
    await expect(page.getByText("OVERDUE").first()).toBeVisible();
  });

  test("generating a bill for a period with no deliveries explains why none was created", async ({ page }) => {
    await page.goto("/payments/bills/generate");
    await page.getByText(CUSTOMER_OPTION).click();
    const future = futureDate(400);
    await page.getByLabel("Period Start").fill(future);
    await page.getByLabel("Period End").fill(future);
    await page.getByRole("button", { name: "Generate Bills" }).click();

    await expect(page.getByText("No deliveries found for the given period.").first()).toBeVisible();
  });

  test("CHECKER cannot access the payments pages", async ({ browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto("/login");
    await page.getByLabel("Username").fill("checker1");
    await page.getByLabel("Password").fill("checker123");
    await page.getByRole("button", { name: "Sign In" }).click();
    await expect(page).toHaveURL(/\/$/);

    await page.goto("/payments");
    await expect(page.getByText("You do not have permission to access this page.")).toBeVisible();

    await page.goto("/payments/bills");
    await expect(page.getByText("You do not have permission to access this page.")).toBeVisible();

    await page.goto("/payments/outstanding");
    await expect(page.getByText("You do not have permission to access this page.")).toBeVisible();

    await context.close();
  });
});
