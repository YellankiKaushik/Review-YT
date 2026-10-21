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

it("returns malformed client JSON as 400 before contacting the backend", async () => {
  environment();
  const network = vi.fn();
  vi.stubGlobal("fetch", network);
  const response = await relay(
    new Request("https://app.example/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{broken",
    }),
    "analyze",
  );
  expect(response.status).toBe(400);
  expect((await response.json()).error.code).toBe("json_invalid");
  expect(network).not.toHaveBeenCalled();
});

it.each([401, 429, 502])(
  "forwards backend status %i and keeps error responses uncached",
  async (status) => {
    environment();
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          Response.json(
            { error: { message: "Safe upstream message" } },
            { status },
          ),
        ),
    );
    const response = await relay(
      new Request("https://app.example/api/providers"),
      "providers",
    );
    expect(response.status).toBe(status);
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect((await response.json()).error.message).toBe("Safe upstream message");
  },
);
it("rejects unexpected backend HTML without echoing its private content", async () => {
  environment();
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue(
        new Response("<html>private-internal-content</html>", { status: 502 }),
      ),
  );
  const response = await relay(
    new Request("https://app.example/api/providers"),
    "providers",
  );
  expect(response.status).toBe(502);
  const text = await response.text();
  expect(text).toContain("upstream_format");
  expect(text).not.toContain("private-internal-content");
});
it("bounds unexpected large backend bodies", async () => {
  environment();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(new Response("x".repeat(200001))),
  );
  expect(
    (await relay(new Request("https://app.example/api/providers"), "providers"))
      .status,
  ).toBe(502);
});
it("sanitizes an expired backend timeout", async () => {
  environment();
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockRejectedValue(
        new DOMException("private-server-name", "TimeoutError"),
      ),
  );
  const response = await relay(
    new Request("https://app.example/api/providers"),
    "providers",
  );
  expect(response.status).toBe(503);
  expect(await response.text()).not.toContain("private-server-name");
});
it.each([
  "https://user:password@backend.example",
  "https://backend.example/path",
  "https://backend.example?secret=value",
])("rejects unsafe backend origin configuration %s", async (origin) => {
  environment();
  vi.stubEnv("BACKEND_URL", origin);
  const network = vi.fn();
  vi.stubGlobal("fetch", network);
  expect(
    (await relay(new Request("https://app.example/api/providers"), "providers"))
      .status,
  ).toBe(503);
  expect(network).not.toHaveBeenCalled();
});
it("forwards only allowlisted result query fields and no client-selected target", async () => {
  environment();
  const network = vi.fn().mockResolvedValue(Response.json({ safe: true }));
  vi.stubGlobal("fetch", network);
  await relay(
    new Request(
      "https://app.example/api/results?video=aB3_dE5-fG7&provider=disabled&url=https://private.example&key=ignored",
    ),
    "results",
  );
  const target = new URL(network.mock.calls[0][0]);
  expect(target.origin).toBe("https://backend.example");
  expect([...target.searchParams.keys()]).toEqual(["video", "provider"]);
  expect(network.mock.calls[0][1].redirect).toBe("error");
});

it.each(["BACKEND_URL", "BACKEND_API_TOKEN"])(
  "fails safely when %s is missing",
  async (name) => {
    environment();
    vi.stubEnv(name, "");
    const network = vi.fn();
    vi.stubGlobal("fetch", network);
    const response = await relay(
      new Request("https://app.example/api/providers"),
      "providers",
    );
    expect(response.status).toBe(503);
    expect((await response.json()).error.code).toBe("configuration");
    expect(network).not.toHaveBeenCalled();
  },
);
