import "server-only";
const failure = (code: string, message: string, status: number) =>
  Response.json(
    { error: { code, message } },
    { status, headers: { "Cache-Control": "no-store" } },
  );
export async function relay(
  request: Request,
  operation: string,
): Promise<Response> {
  if (!["analyze", "results", "providers"].includes(operation))
    return failure("route", "Unknown API operation.", 404);
  if ((operation === "analyze") !== (request.method === "POST"))
    return failure(
      "method",
      "This operation uses a different HTTP method.",
      405,
    );
  const raw = process.env.BACKEND_URL;
  const token = process.env.BACKEND_API_TOKEN;
  if (!raw || !token)
    return failure(
      "configuration",
      "The review backend has not been connected yet.",
      503,
    );
  try {
    const origin = new URL(raw);
    const local = ["localhost", "127.0.0.1", "[::1]"].includes(origin.hostname);
    const testLocal =
      process.env.NODE_ENV !== "production" ||
      process.env.REVIEW_LOCAL_TEST === "true";
    if (
      origin.username ||
      origin.password ||
      origin.pathname !== "/" ||
      origin.search ||
      origin.hash ||
      !(
        origin.protocol === "https:" ||
        (local && origin.protocol === "http:" && testLocal)
      )
    )
      return failure(
        "configuration",
        "Backend must be a trusted HTTPS origin in production.",
        503,
      );
    let payload: string | undefined;
    if (request.method === "POST") {
      if (!request.headers.get("content-type")?.includes("application/json"))
        return failure("json_required", "Use JSON for analysis requests.", 415);
      const declared = Number(request.headers.get("content-length") || 0);
      if (declared > 4096)
        return failure("request_size", "This request is too large.", 413);
      const reader = request.body?.getReader();
      let size = 0;
      const chunks: Uint8Array[] = [];
      if (reader)
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          size += value.byteLength;
          if (size > 4096) {
            await reader.cancel();
            return failure("request_size", "This request is too large.", 413);
          }
          chunks.push(value);
        }
      const bytes = new Uint8Array(size);
      let offset = 0;
      for (const chunk of chunks) {
        bytes.set(chunk, offset);
        offset += chunk.length;
      }
      payload = new TextDecoder().decode(bytes);
      try {
        JSON.parse(payload);
      } catch {
        return failure("json_invalid", "Send a valid JSON request.", 400);
      }
    }
    const target = new URL("/api/" + operation, origin);
    if (operation === "results")
      for (const field of ["video", "provider"]) {
        const value = new URL(request.url).searchParams.get(field);
        if (value) target.searchParams.set(field, value);
      }
    const upstream = await fetch(target, {
      method: request.method,
      body: payload,
      headers: {
        Authorization: "Bearer " + token,
        ...(payload ? { "Content-Type": "application/json" } : {}),
      },
      cache: "no-store",
      signal: AbortSignal.timeout(115000),
      redirect: "error",
    });
    const text = await upstream.text();
    if (text.length > 200000)
      return failure(
        "upstream_size",
        "The review response exceeded its limit.",
        502,
      );
    let body: unknown;
    try {
      body = JSON.parse(text);
    } catch {
      return failure(
        "upstream_format",
        "The backend returned an unreadable response.",
        502,
      );
    }
    return Response.json(body, {
      status: upstream.status,
      headers: {
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      },
    });
  } catch {
    return failure(
      "connection",
      "The backend did not respond. A free service may be waking up; please wait and try again.",
      503,
    );
  }
}
