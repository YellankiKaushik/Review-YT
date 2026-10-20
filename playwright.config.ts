import { defineConfig, devices } from "@playwright/test";
import path from "node:path";
const python = path.resolve(
  ".venv",
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);
export default defineConfig({
  testDir: "tests/e2e",
  workers: 1,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:3201",
    trace: "off",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
  webServer: [
    {
      command: `"${python}" tests/e2e/offline_api.py`,
      url: "http://127.0.0.1:5101/health",
      reuseExistingServer: false,
      timeout: 30000,
    },
    {
      command:
        "node node_modules/next/dist/bin/next dev apps/web --webpack --port 3201",
      url: "http://127.0.0.1:3201",
      env: {
        BACKEND_URL: "http://127.0.0.1:5101",
        BACKEND_API_TOKEN: "e2e-fixture-shared",
        REVIEW_DIST: ".next-e2e",
        NEXT_TELEMETRY_DISABLED: "1",
      },
      reuseExistingServer: false,
      timeout: 60000,
    },
  ],
});
