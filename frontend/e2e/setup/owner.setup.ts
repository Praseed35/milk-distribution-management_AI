import { test as setup, expect } from "@playwright/test";

const OWNER_AUTH_FILE = "e2e/.auth/owner.json";

setup("authenticate as owner", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Username").fill("owner");
  await page.getByLabel("Password").fill("owner123");
  await page.getByRole("button", { name: "Sign In" }).click();

  await expect(page).toHaveURL(/\/reports\/dashboard/);
  await page.getByText("owner (OWNER)").waitFor();

  await page.context().storageState({ path: OWNER_AUTH_FILE });
});
