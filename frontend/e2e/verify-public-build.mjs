/**
 * Manual check of the PUBLISHED (public) build, with the real password gate on.
 *
 * Not part of `npm test`: the normal suite runs against `next dev`, where both
 * private features are on. This script serves the static export instead.
 *
 *   1. cd backend && PRIVATE_AREA_PASSWORD=... uvicorn app.main:app --port 8000
 *   2. cd frontend/out && python -m http.server 3100
 *   3. node e2e/verify-public-build.mjs
 */
import assert from "node:assert/strict";
import { chromium } from "playwright";

const BASE = process.env.PUBLIC_SITE_URL || "http://127.0.0.1:3100";
const API = process.env.PUBLIC_API_URL || "http://127.0.0.1:8000";
const PASSWORD = process.env.PRIVATE_AREA_PASSWORD || "gym-test-pass";
const AUTH_KEY = "sdet-gym-auth";
const AUTH_TOKEN = "c85e4b23455aeaee349c8e0a57347644f7c99ebb134d72a5284a864f9ee39166";

const browser = await chromium.launch();
const context = await browser.newContext();
await context.addInitScript(
  ([key, token]) => window.localStorage.setItem(key, token),
  [AUTH_KEY, AUTH_TOKEN],
);
const page = await context.newPage();

const step = (label) => console.log(`• ${label}`);

// 1. The API refuses the private endpoints without a token.
const locked = await fetch(`${API}/api/admiral`);
assert.equal(locked.status, 401, "admiral must be 401 while locked");
const body = await locked.text();
assert.ok(!body.includes("Saviynt"), "401 body must not contain brief content");
step("API: /api/admiral is 401 and leaks nothing");

assert.equal((await fetch(`${API}/api/assistant/status`)).status, 401);
step("API: /api/assistant/status is 401");

// 2. The public build has no Admiral nav entry and no assistant launcher.
await page.goto(`${BASE}/`);
await page.waitForLoadState("networkidle");
assert.equal(
  await page.getByRole("link", { name: "Admiral IGA Playbook" }).count(),
  0,
  "Admiral nav entry must be absent",
);
assert.equal(
  await page.getByRole("button", { name: /Open interview assistant/i }).count(),
  0,
  "assistant launcher must be absent",
);
step("Public UI: no Admiral nav, no assistant launcher");

// 3. The nav entry leads to the unlock prompt, and so does the page itself.
await page.getByRole("link", { name: "Private Area" }).click();
await page.getByLabel("Access password").waitFor();
assert.equal(await page.getByText("From the Admiral IGA role brief").count(), 0);
step("Public UI: Private Area nav opens the password prompt");

await page.goto(`${BASE}/admiral-iga/`);
await page.waitForLoadState("networkidle");
assert.equal(await page.getByText("Private area", { exact: false }).count() > 0, true);
assert.equal(await page.getByText("From the Admiral IGA role brief").count(), 0);
step("Public UI: /admiral-iga shows the password gate, no brief");

// 4. A wrong password is rejected by the server.
await page.getByLabel("Access password").fill("definitely-wrong");
await page.getByRole("button", { name: "Unlock" }).click();
await page.getByRole("alert").first().waitFor();
assert.match(await page.getByRole("alert").first().innerText(), /not right/i);
step("Gate: wrong password rejected with the server's message");

// 5. The right password unlocks the brief and the assistant.
await page.getByLabel("Access password").fill(PASSWORD);
await page.getByRole("button", { name: "Unlock" }).click();
await page.getByRole("heading", { name: "Admiral IGA Playbook" }).waitFor();
await page.waitForLoadState("networkidle");
assert.ok(
  (await page.locator("body").innerText()).length > 2000,
  "unlocked page should render the brief",
);
step("Gate: correct password renders the brief");

await page.goto(`${BASE}/`);
await page.waitForLoadState("networkidle");
await page
  .getByRole("button", { name: /Open interview assistant/i })
  .waitFor({ timeout: 15_000 });
step("Gate: assistant appears after unlock");

// 6. Locking again hides it.
await page.evaluate(() => window.sessionStorage.removeItem("sdet-gym-private-token"));
await page.reload();
await page.waitForLoadState("networkidle");
assert.equal(
  await page.getByRole("button", { name: /Open interview assistant/i }).count(),
  0,
  "assistant must disappear when the token is dropped",
);
step("Gate: dropping the token re-locks the assistant");

await browser.close();
console.log("\nPublic build verified.");
