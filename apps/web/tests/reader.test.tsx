import { render, screen, waitFor, act } from "@testing-library/react";
import { it, expect, vi } from "vitest";
import { ReviewReader } from "../ui/review-reader";
import { remember } from "../lib/tab-cache";
import { sample } from "./sample";

it("does not show an earlier provider result when the next provider has no cached review", async () => {
  sessionStorage.clear();
  remember(sample);
  const fetcher = vi
    .fn()
    .mockResolvedValue(
      Response.json(
        { error: { message: "No saved review is available." } },
        { status: 404 },
      ),
    );
  vi.stubGlobal("fetch", fetcher);
  const view = render(
    <ReviewReader video={sample.video.id} provider="disabled" />,
  );
  await screen.findByRole("heading", { name: sample.video.title });
  view.rerender(<ReviewReader video={sample.video.id} provider="ollama" />);
  expect(
    screen.queryByRole("heading", { name: sample.video.title }),
  ).toBeNull();
  await screen.findByRole("heading", {
    name: "This page has no saved review.",
  });
  expect(fetcher).toHaveBeenCalledTimes(1);
  expect(fetcher.mock.calls[0][0]).toContain("provider=ollama");
});

it("does not leave an earlier video visible while a different video is loading", async () => {
  sessionStorage.clear();
  remember(sample);
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(() => new Promise(() => {})),
  );
  const view = render(
    <ReviewReader video={sample.video.id} provider="disabled" />,
  );
  await screen.findByRole("heading", { name: sample.video.title });
  view.rerender(<ReviewReader video="zY8_xW6-vU4" provider="disabled" />);
  expect(
    screen.queryByRole("heading", { name: sample.video.title }),
  ).toBeNull();
  expect(
    screen.getByRole("heading", { name: "Opening your notebook…" }),
  ).toBeVisible();
});

it("does not automatically POST when stored result is expired and the API has lost it", async () => {
  sessionStorage.clear();
  remember({
    ...sample,
    caching: { ...sample.caching, validUntil: "2000-01-01T00:00:00Z" },
  });
  const fetcher = vi
    .fn()
    .mockResolvedValue(
      Response.json(
        { error: { message: "No saved review is available." } },
        { status: 404 },
      ),
    );
  vi.stubGlobal("fetch", fetcher);
  render(<ReviewReader video={sample.video.id} provider="disabled" />);
  await screen.findByRole("heading", {
    name: "This page has no saved review.",
  });
  expect(
    screen.getByRole("link", { name: /Start a new review/ }),
  ).toBeVisible();
  await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(1));
  expect(fetcher.mock.calls[0][1]).not.toHaveProperty("method", "POST");
});

it("refuses a different video's coherent result returned for a direct URL", async () => {
  sessionStorage.clear();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      Response.json({
        ...sample,
        video: { ...sample.video, id: "zY8_xW6-vU4" },
      }),
    ),
  );
  render(<ReviewReader video={sample.video.id} provider="disabled" />);
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "did not match the requested video and provider",
  );
  expect(
    screen.queryByRole("heading", { name: sample.video.title }),
  ).toBeNull();
});

it("bounds a stalled saved-result request and offers a manual retry", async () => {
  sessionStorage.clear();
  vi.useFakeTimers();
  const fetcher = vi
    .fn()
    .mockImplementation(
      (_url, options) =>
        new Promise((_resolve, reject) =>
          options.signal.addEventListener("abort", () =>
            reject(options.signal.reason),
          ),
        ),
    );
  vi.stubGlobal("fetch", fetcher);
  try {
    render(<ReviewReader video={sample.video.id} provider="disabled" />);
    await act(async () => {
      vi.advanceTimersByTime(120000);
    });
    expect(screen.getByRole("alert")).toHaveTextContent("timed out");
    expect(
      screen.getByRole("button", { name: "Check saved review again" }),
    ).toBeEnabled();
    expect(fetcher).toHaveBeenCalledTimes(1);
  } finally {
    vi.useRealTimers();
  }
});
