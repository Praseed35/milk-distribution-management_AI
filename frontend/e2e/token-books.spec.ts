import { test, expect, type APIRequestContext } from "@playwright/test";
import { unique } from "./helpers";

async function ownerToken(request: APIRequestContext): Promise<string> {
  const res = await request.post("/api/v1/auth/login", {
    data: { username: "owner", password: "owner123" },
  });
  expect(res.ok()).toBeTruthy();
  return (await res.json()).access_token as string;
}

async function createIdentityViaApi(request: APIRequestContext, token: string, tokenNumber: number): Promise<number> {
  const res = await request.post("/api/v1/token-books/identities", {
    headers: { Authorization: `Bearer ${token}` },
    data: { customer_id: 2, milk_type_id: 5, token_number: tokenNumber },
  });
  expect(res.ok()).toBeTruthy();
  return (await res.json()).id as number;
}

async function createIssueViaApi(request: APIRequestContext, token: string, identityId: number, issueNumber: number): Promise<number> {
  const res = await request.post("/api/v1/token-books/issues", {
    headers: { Authorization: `Bearer ${token}` },
    data: { token_identity_id: identityId, issue_number: issueNumber, remarks: "e2e setup" },
  });
  expect(res.ok()).toBeTruthy();
  return (await res.json()).id as number;
}

function tokenNumber(): number {
  return 2000 + Math.floor(Math.random() * 7000);
}

function issueNumber(): number {
  return 500 + Math.floor(Math.random() * 400);
}

test.describe("token books (owner)", () => {
  test("creates a token identity", async ({ page }) => {
    const tn = tokenNumber();

    await page.goto("/token-identities/new");
    await page.getByLabel("Customer").selectOption({ label: "C00002 - Priya Sharma" });
    await page.getByLabel("Milk Type").selectOption({ label: "Small Pack Milk (250 ml)" });
    await page.getByLabel("Token Number").fill(String(tn));
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/token-identities$/);
    await expect(page.getByRole("table")).toContainText("Priya Sharma");
    await expect(page.getByRole("table")).toContainText(String(tn));
  });

  test("token identity form validates the token number", async ({ page }) => {
    await page.goto("/token-identities/new");
    await page.getByLabel("Customer").selectOption({ label: "C00002 - Priya Sharma" });
    await page.getByLabel("Milk Type").selectOption({ label: "Small Pack Milk (250 ml)" });
    await page.getByLabel("Token Number").fill("0");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText("Token number must be a positive whole number")).toBeVisible();
    await expect(page).toHaveURL(/\/token-identities\/new$/);
  });

  test("creates a token book issue", async ({ page, request }) => {
    const token = await ownerToken(request);
    const tn = tokenNumber();
    const identityId = await createIdentityViaApi(request, token, tn);
    const ino = issueNumber();

    await page.goto("/token-book-issues/new");
    await page.getByLabel("Identity").selectOption({ value: String(identityId) });
    await page.getByLabel("Issue Number").fill(String(ino));
    await page.getByLabel("Remarks").fill(unique("issue"));
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/token-book-issues$/);
    await expect(page.getByRole("table")).toContainText("Priya Sharma");
  });

  test("token book issue form validates required fields", async ({ page }) => {
    await page.goto("/token-book-issues/new");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText("Identity is required")).toBeVisible();
    await expect(page.getByText("Issue number must be a positive whole number")).toBeVisible();
    await expect(page).toHaveURL(/\/token-book-issues\/new$/);
  });

  test("creates a token book payment", async ({ page, request }) => {
    const token = await ownerToken(request);
    const identityId = await createIdentityViaApi(request, token, tokenNumber());
    const ino = issueNumber();
    const issueId = await createIssueViaApi(request, token, identityId, ino);

    await page.goto("/token-book-payments/new");
    await page.getByLabel("Issue").selectOption({ value: String(issueId) });
    await page.getByLabel("Book Price").fill("100");
    await page.getByLabel("Amount Paid").fill("100");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page).toHaveURL(/\/token-book-payments$/);
    await expect(page.getByRole("table")).toContainText("Priya Sharma");
  });

  test("payment form rejects an amount above the book price", async ({ page, request }) => {
    const token = await ownerToken(request);
    const identityId = await createIdentityViaApi(request, token, tokenNumber());
    const ino = issueNumber();
    const issueId = await createIssueViaApi(request, token, identityId, ino);

    await page.goto("/token-book-payments/new");
    await page.getByLabel("Issue").selectOption({ value: String(issueId) });
    await page.getByLabel("Book Price").fill("100");
    await page.getByLabel("Amount Paid").fill("150");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText("Amount paid cannot exceed book price")).toBeVisible();
    await expect(page).toHaveURL(/\/token-book-payments\/new$/);
  });
});
