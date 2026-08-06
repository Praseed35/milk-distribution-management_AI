import { test, expect, type APIRequestContext, type Page } from "@playwright/test";

test.describe.configure({ mode: "serial" });

const ROUTE_OPTION = "R001 - Downtown Route";
const DELIVERY_PARTNER_OPTION = "E00002 - Suresh Babu";

function yesterdayIso(): string {
  const d = new Date(Date.now() - 86_400_000);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

async function loginAsOwner(request: APIRequestContext): Promise<string> {
  const res = await request.post("/api/v1/auth/login", {
    data: { username: "owner", password: "owner123" },
  });
  expect(res.ok()).toBeTruthy();
  return (await res.json()).access_token as string;
}

async function checklistQuantities(
  request: APIRequestContext,
  token: string,
  sessionId: number
): Promise<number[]> {
  const res = await request.get(`/api/v1/deliveries/sessions/${sessionId}/checklist`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(res.ok()).toBeTruthy();
  return (await res.json()).customers.map((c: { quantity: number }) => Number(c.quantity));
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

/** Creates a completed delivery session on route R001 for `date` so the AI stats have history. */
async function createCompletedSession(
  page: Page,
  request: APIRequestContext,
  date: string
): Promise<number> {
  const token = await loginAsOwner(request);

  await page.goto("/delivery/sessions/new");
  await page.getByLabel("Route").selectOption({ label: ROUTE_OPTION });
  await page.getByLabel("Delivery Date").fill(date);
  await page.getByLabel("Shift").selectOption({ label: "MORNING" });
  await page.getByLabel("Delivery Partner").selectOption({ label: DELIVERY_PARTNER_OPTION });
  await page.getByRole("button", { name: "Create Session" }).click();
  await expect(page).toHaveURL(/\/delivery\/sessions\/\d+$/);

  const sessionId = Number(page.url().match(/\/delivery\/sessions\/(\d+)$/)![1]);
  const quantities = await checklistQuantities(request, token, sessionId);
  expect(quantities.length).toBeGreaterThan(0);
  const loaded = quantities.reduce((sum, q) => sum + q, 0);

  await page.getByLabel("Total Milk Loaded (L)").fill(String(loaded));
  await page.getByRole("button", { name: "Record Dispatch" }).click();
  await page.getByRole("button", { name: "Confirm" }).click();

  await markAllDelivered(request, token, sessionId);

  await page.getByRole("button", { name: "Complete Session" }).click();
  await page.getByRole("button", { name: "Confirm" }).click();
  await expect(page.getByText("COMPLETED").first()).toBeVisible();

  return loaded;
}

async function login(page: Page, username: string, password: string) {
  await page.goto("/login");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/reports\/dashboard/);
}

test.describe("ai insights", () => {
  test("forecast renders seeded bars and anomalies/churn sections render", async ({ page, request }) => {
    await createCompletedSession(page, request, yesterdayIso());

    await page.goto("/reports/ai");
    await expect(page).toHaveURL(/\/reports\/ai$/);
    await expect(page.getByText("AI Insights")).toBeVisible();

    const forecast = page.locator("#forecast-section");
    await expect(forecast).toBeVisible();
    await expect(forecast.locator("li")).toHaveCount(7);
    await expect(forecast.getByText("Total Expected")).toBeVisible();
    const totalText = await forecast.locator("p.text-2xl.font-semibold").first().innerText();
    expect(parseFloat(totalText)).toBeGreaterThan(0);

    const anomalies = page.locator("#anomalies-section");
    await expect(anomalies).toBeVisible();
    await expect(
      anomalies.getByText("No anomalies detected").or(anomalies.locator("li").first())
    ).toBeVisible();

    const churn = page.locator("#churn-section");
    await expect(churn).toBeVisible();
    await expect(churn.getByRole("table")).toBeVisible();
    await expect(churn.getByRole("table")).toContainText("Rajesh Kumar");
    await expect(churn.getByRole("table")).toContainText("Risk Score");
  });

  test("narrative section shows the stats-only notice when the LLM is disabled", async ({ page }) => {
    await page.goto("/reports/ai");
    await expect(page.locator("#insight-narrative")).toContainText(
      "AI explanations unavailable - showing statistics"
    );
  });

  test("chat shows the 503 error state when the LLM is unavailable", async ({ page }) => {
    await page.goto("/reports/ai");
    await page.getByPlaceholder("Type your question...").fill("Which route collected the most cash?");
    await page.getByRole("button", { name: "Send" }).click();
    await expect(
      page.getByText("AI service is currently unavailable. Please try again later.")
    ).toBeVisible();
  });

  test("CHECKER sees no AI Insights nav item and is denied at /reports/ai", async ({ browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await login(page, "checker1", "checker123");

    await page.getByRole("button", { name: "Reports" }).click();
    await expect(page.getByText("AI Insights")).toHaveCount(0);

    await page.goto("/reports/ai");
    await expect(page.getByText("You do not have permission to access this page.")).toBeVisible();
    await context.close();
  });

  test("forecast horizon control clamps to [1, 30] and drives the bar count", async ({ page }) => {
    await page.goto("/reports/ai");
    await expect(page.locator("#forecast-section")).toBeVisible();

    const bars = page.locator("#forecast-section li");
    await expect(bars).toHaveCount(7);

    await page.getByLabel("Horizon (days)").fill("1");
    await expect(bars).toHaveCount(1);

    await page.getByLabel("Horizon (days)").fill("30");
    await expect(bars).toHaveCount(30, { timeout: 15000 });

    await page.getByLabel("Horizon (days)").fill("45");
    await expect(bars).toHaveCount(30, { timeout: 15000 });

    await page.getByLabel("Horizon (days)").fill("0");
    await expect(bars).toHaveCount(7, { timeout: 15000 });
  });

  test("Refresh button re-fetches the forecast", async ({ page }) => {
    await page.goto("/reports/ai");
    const forecast = page.locator("#forecast-section");
    await expect(forecast.locator("li")).toHaveCount(7);

    await forecast.getByRole("button", { name: "Refresh" }).click();
    await expect(forecast.locator("li")).toHaveCount(7, { timeout: 15000 });
    const totalText = await forecast.locator("p.text-2xl.font-semibold").first().innerText();
    expect(parseFloat(totalText)).toBeGreaterThan(0);
  });

  test("chat Send is disabled for empty and whitespace-only input", async ({ page }) => {
    await page.goto("/reports/ai");
    await expect(page.locator("#chat-section")).toBeVisible();

    const send = page.getByRole("button", { name: "Send" });
    await expect(send).toBeDisabled();

    await page.getByPlaceholder("Type your question...").fill("   ");
    await expect(send).toBeDisabled();

    await page.getByPlaceholder("Type your question...").fill("Which route collected the most?");
    await expect(send).toBeEnabled();
  });
});
