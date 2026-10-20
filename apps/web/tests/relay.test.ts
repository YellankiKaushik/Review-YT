import { it, expect, vi } from "vitest";
vi.mock("server-only", () => ({}));
import { relay } from "../lib/relay";
function environment() {
  vi.stubEnv("BACKEND_URL", "https://backend.example");
  vi.stubEnv("BACKEND_API_TOKEN", "test-server-token");
}
it("keeps credentials in upstream headers, not client output", async () => {
  environment();
  const network = vi.fn().mockResolvedValue(Response.json({ safe: true }));
  vi.stubGlobal("fetch", network);
  const response = await relay(
    new Request("https://app.example/api/providers"),
    "providers",
  );
  expect(response.status).toBe(200);
  expect(await response.text()).not.toContain("test-server-token");
  expect(network.mock.calls[0][1].headers.Authorization).toBe(
    "Bearer test-server-token",
  );
});
it("rejects arbitrary operations before contacting a service", async () => {
  environment();
  const network = vi.fn();
  vi.stubGlobal("fetch", network);
  expect(
    (await relay(new Request("https://app.example/api/secrets"), "secrets"))
      .status,
  ).toBe(404);
  expect(network).not.toHaveBeenCalled();
});
it("requires HTTPS for a deployed backend", async () => {
  environment();
  vi.stubEnv("NODE_ENV", "production");
  vi.stubEnv("REVIEW_LOCAL_TEST", "");
  vi.stubEnv("BACKEND_URL", "http://127.0.0.1:5100");
  expect(
    (await relay(new Request("https://app.example/api/providers"), "providers"))
      .status,
  ).toBe(503);
});
it("bounds request bodies before forwarding", async () => {
  environment();
  const network = vi.fn();
  vi.stubGlobal("fetch", network);
  const request = new Request("https://app.example/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video: "x".repeat(5000) }),
  });
  expect((await relay(request, "analyze")).status).toBe(413);
  expect(network).not.toHaveBeenCalled();
});
it("reports a cold/unreachable backend without exposing exception text", async () => {
  environment();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockRejectedValue(new Error("private-internal-url")),
  );
  const response = await relay(
    new Request("https://app.example/api/providers"),
    "providers",
  );
  expect(response.status).toBe(503);
  expect(await response.text()).not.toContain("private-internal-url");
});
