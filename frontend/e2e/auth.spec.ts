import { test, expect } from "@playwright/test";

// These tests manage their own session, so start every test logged out.
test.use({ storageState: { cookies: [], origins: [] } });

async function login(page: import("@playwright/test").Page, username: string, password: string) {
  await page.goto("/login");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign In" }).click();
}

test.describe("authentication", () => {
  test("redirects unauthenticated visitors to the login page", async ({ page }) => {
    await page.goto("/routes");
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole("button", { name: "Sign In" })).toBeVisible();
  });

  test("login redirects back to the originally requested page", async ({ page }) => {
    await page.goto("/routes");
    await expect(page).toHaveURL(/\/login/);
    await login(page, "owner", "owner123");
    await expect(page).toHaveURL(/\/routes/);
    await expect(page.getByRole("button", { name: "Create Route" })).toBeVisible();
  });

  test("rejects invalid credentials", async ({ page }) => {
    await login(page, "owner", "wrong-password");
    await expect(page.getByText("Invalid username or password")).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });

  test("owner can access the routes page", async ({ page }) => {
    await login(page, "owner", "owner123");
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByText("owner (OWNER)")).toBeVisible();
    await page.goto("/routes");
    await expect(page.getByRole("button", { name: "Create Route" })).toBeVisible();
  });

  test("checker is blocked from owner-only pages", async ({ page }) => {
    await login(page, "checker1", "checker123");
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByText("checker1 (CHECKER)")).toBeVisible();
    await page.goto("/routes");
    await expect(page.getByText("403")).toBeVisible();
    await expect(page.getByText("You do not have permission to access this page.")).toBeVisible();
  });

  test("checker can access shared pages like customers", async ({ page }) => {
    await login(page, "checker1", "checker123");
    await expect(page.getByText("checker1 (CHECKER)")).toBeVisible();
    await page.goto("/customers");
    await expect(page.getByRole("button", { name: "Create Customer" })).toBeVisible();
  });

  test("logout returns to the login page", async ({ page }) => {
    await login(page, "owner", "owner123");
    await expect(page).toHaveURL(/\/$/);
    await page.getByRole("button", { name: "Logout" }).click();
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole("button", { name: "Sign In" })).toBeVisible();
  });
});
