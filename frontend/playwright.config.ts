import { defineConfig, devices } from "@playwright/test";

/**
 * E2E test configuration.
 *
 * Two web servers are started automatically:
 *   1. Backend  - `python scripts/e2e_backend.py` (resets + seeds the isolated
 *                 `milk_management_e2e` database, then serves the API on :8001)
 *   2. Frontend - Vite dev server on :5174, proxying `/api` to :8001
 *
 * Run with: `npm run test:e2e`
 */
const BACKEND_PORT = 8001;
const FRONTEND_PORT = 5174;
const BASE_URL = `http://localhost:${FRONTEND_PORT}`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: process.env.CI ? "github" : "list",
  timeout: 60_000,
  expect: {
    timeout: 15_000,
  },
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },

  projects: [
    {
      name: "setup-owner",
      testMatch: /owner\.setup\.ts/,
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: "e2e/.auth/owner.json",
      },
      dependencies: ["setup-owner"],
    },
  ],

  webServer: [
    {
      command: "python scripts/e2e_backend.py",
      cwd: "..",
      url: `http://localhost:${BACKEND_PORT}/api/v1/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: `npm run dev -- --port ${FRONTEND_PORT} --strictPort`,
      url: BASE_URL,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: {
        VITE_API_PROXY_TARGET: `http://localhost:${BACKEND_PORT}`,
      },
    },
  ],
});
