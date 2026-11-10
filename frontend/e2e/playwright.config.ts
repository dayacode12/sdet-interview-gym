import { defineConfig } from "@playwright/test";

// E2E tests expect the backend on :8000 and the frontend on :3000.
// Start both before running: `npm run e2e` from frontend/e2e.
export default defineConfig({
  testDir: ".",
  testMatch: "*.spec.ts",
  timeout: 60_000,
  retries: 0,
  use: {
    baseURL: process.env.FRONTEND_URL || "http://localhost:3000",
    headless: true,
  },
  reporter: [["list"]],
  projects: [{ name: "chromium", use: { browserName: "chromium" } }],
});
