import { test, expect } from "@playwright/test";
import { unique, uniquePhone } from "./helpers";

test.describe("master data (owner)", () => {
  test("creates a route and shows it in the list", async ({ page }) => {
    const code = unique("R").toUpperCase().slice(0, 8);
    const name = unique("Downtown Test");

    await page.goto("/routes/new");
    await page.getByLabel("Route Code").fill(code);
    await page.getByLabel("Route Name").fill(name);
    await page.getByLabel("Description").fill("Created by E2E");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/routes$/);
    await expect(page.getByRole("cell", { name: code })).toBeVisible();
    await expect(page.getByRole("cell", { name })).toBeVisible();
  });

  test("route form shows validation errors for short values", async ({ page }) => {
    await page.goto("/routes/new");
    await page.getByLabel("Route Code").fill("A");
    await page.getByLabel("Route Name").fill("B");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText("Code must be at least 2 characters")).toBeVisible();
    await expect(page.getByText("Name must be at least 2 characters")).toBeVisible();
    await expect(page).toHaveURL(/\/routes\/new/);
  });

  test("edits an existing route", async ({ page }) => {
    const code = unique("R").toUpperCase().slice(0, 8);
    const name = unique("Edit Me");
    const renamed = `${name}_renamed`;

    await page.goto("/routes/new");
    await page.getByLabel("Route Code").fill(code);
    await page.getByLabel("Route Name").fill(name);
    await page.getByRole("button", { name: "Create" }).click();
    await expect(page.getByRole("cell", { name: code })).toBeVisible();

    const row = page.locator("tr", { hasText: code });
    await row.getByRole("button", { name: "Edit" }).click();
    await expect(page).toHaveURL(/\/routes\/\d+\/edit/);

    await page.getByLabel("Route Name").fill(renamed);
    await page.getByRole("button", { name: "Update" }).click();
    await expect(page).toHaveURL(/\/routes$/);
    await expect(page.getByRole("cell", { name: renamed })).toBeVisible();
  });

  test("creates a customer with a route", async ({ page }) => {
    const name = unique("Customer");
    const phone = uniquePhone();

    await page.goto("/customers/new");
    await page.getByLabel("Customer Name").fill(name);
    await page.getByLabel("Primary Phone").fill(phone);
    await page.getByLabel("Address").fill("12 Test Street");
    await page.getByLabel("Route").selectOption({ label: "R001 - Downtown Route" });
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/customers$/);
    await expect(page.getByRole("cell", { name })).toBeVisible();
  });

  test("customer form rejects a phone that is not 10 digits", async ({ page }) => {
    await page.goto("/customers/new");
    await page.getByLabel("Customer Name").fill("Invalid Phone");
    await page.getByLabel("Primary Phone").fill("123");
    await page.getByLabel("Route").selectOption({ label: "R001 - Downtown Route" });
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText("Phone must be 10 digits")).toBeVisible();
    await expect(page).toHaveURL(/\/customers\/new/);
  });

  test("creates a milk type with a unit price", async ({ page }) => {
    const name = unique("E2E Milk");

    await page.goto("/milk-types/new");
    await page.getByLabel("Milk Name").fill(name);
    await page.getByLabel("Volume (ml)").fill("500");
    await page.getByLabel("Unit Price").fill("45.50");
    await page.getByLabel("Description").fill("Created by E2E");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/milk-types$/);
    await expect(page.getByRole("cell", { name })).toBeVisible();
  });

  test("milk type form rejects a negative price", async ({ page }) => {
    await page.goto("/milk-types/new");
    await page.getByLabel("Milk Name").fill("Neg Price Milk");
    await page.getByLabel("Volume (ml)").fill("500");
    await page.getByLabel("Unit Price").fill("-5");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText("Price cannot be negative")).toBeVisible();
    await expect(page).toHaveURL(/\/milk-types\/new/);
  });

  test("creates an employee", async ({ page }) => {
    const name = unique("Employee");
    const phone = uniquePhone();

    await page.goto("/employees/new");
    await page.getByLabel(/^Name/).fill(name);
    await page.getByLabel("Phone").fill(phone);
    await page.getByLabel("Address").fill("Staff Quarters");
    await page.getByLabel("Role").selectOption({ label: "Delivery Partner" });
    await page.getByLabel("Route").selectOption({ label: "R001 - Downtown Route" });
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/employees$/);
    await expect(page.getByRole("cell", { name })).toBeVisible();
  });

  test("creates a user", async ({ page }) => {
    const username = unique("e2euser").slice(0, 20);
    const password = "secret123";

    await page.goto("/users/new");
    await page.getByLabel("Username").fill(username);
    await page.getByLabel(/^Password/).fill(password);
    await page.getByLabel("Confirm Password").fill(password);
    await page.getByLabel("Role").selectOption({ label: "Checker" });
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/users$/);
    await expect(page.getByText(username)).toBeVisible();
  });

  test("user form rejects mismatched passwords", async ({ page }) => {
    await page.goto("/users/new");
    await page.getByLabel("Username").fill("mismatchuser");
    await page.getByLabel(/^Password/).fill("secret123");
    await page.getByLabel("Confirm Password").fill("different");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText("Passwords do not match")).toBeVisible();
    await expect(page).toHaveURL(/\/users\/new/);
  });
});
