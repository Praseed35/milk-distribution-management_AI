import { test, expect } from "@playwright/test";
import { futureDate, unique } from "./helpers";

test.describe("operations: subscriptions & exceptions (owner)", () => {
  test("creates a subscription", async ({ page }) => {
    const remarks = unique("sub");

    await page.goto("/subscriptions/new");
    await page.getByLabel("Customer").selectOption({ label: "C00001 - Rajesh Kumar" });
    await page.getByLabel("Milk Type").selectOption({ label: "Double Toned Milk (500 ml)" });
    await page.getByLabel("Morning Quantity").fill("2");
    await page.getByLabel("Evening Quantity").fill("1");
    await page.getByLabel("Status").selectOption({ label: "Active" });
    await page.getByLabel("Remarks").fill(remarks);
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/subscriptions$/);
    await expect(page.getByRole("table")).toContainText("Rajesh Kumar");
    await expect(page.getByRole("table")).toContainText("Double Toned Milk (500 ml)");
  });

  test("subscription form validates quantities", async ({ page }) => {
    await page.goto("/subscriptions/new");
    await page.getByLabel("Customer").selectOption({ label: "C00001 - Rajesh Kumar" });
    await page.getByLabel("Milk Type").selectOption({ label: "Double Toned Milk (500 ml)" });
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText("Quantity must be 0 or more")).toBeVisible();
    await expect(page).toHaveURL(/\/subscriptions\/new/);
  });

  test("creates a delivery exception", async ({ page }) => {
    const reason = unique("vacation");
    const start = futureDate(45);
    const end = futureDate(47);

    await page.goto("/delivery-exceptions/new");
    await page.getByLabel("Subscription").selectOption({ label: "C00001 - Rajesh Kumar" });
    await page.getByLabel("Exception Type").selectOption({ label: "VACATION" });
    await page.getByLabel("Shift").selectOption({ label: "Whole Day" });
    await page.getByLabel("Start Date").fill(start);
    await page.getByLabel("End Date").fill(end);
    await page.getByLabel("Reason").fill(reason);
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/delivery-exceptions$/);
    await expect(page.getByRole("table")).toContainText("VACATION");
  });

  test("delivery exception form requires a start date", async ({ page }) => {
    await page.goto("/delivery-exceptions/new");
    await page.getByLabel("Subscription").selectOption({ label: "C00001 - Rajesh Kumar" });
    await page.getByLabel("Start Date").fill("");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText("Start date is required")).toBeVisible();
    await expect(page).toHaveURL(/\/delivery-exceptions\/new/);
  });
});
