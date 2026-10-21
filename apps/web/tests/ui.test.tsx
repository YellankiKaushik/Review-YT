import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { it, expect, vi } from "vitest";
import { ReviewSheet } from "../ui/review-sheet";
import { ReviewForm } from "../ui/review-form";
import { sample, inventory } from "./sample";
const { push } = vi.hoisted(() => ({ push: vi.fn() }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
it("renders the true sample, accessible chart and classifier", () => {
  render(<ReviewSheet review={sample} />);
  expect(
    screen.getByRole("heading", { name: sample.video.title }),
  ).toBeVisible();
  expect(
    screen.getByRole("img", {
      name: "Sample sentiment: 50% positive, 25% neutral, 25% negative",
    }),
  ).toBeVisible();
  expect(screen.getByText(sample.sentiment.classifier)).toBeVisible();
  expect(
    screen.getByRole("heading", { name: "Sentiment-only review" }),
  ).toBeVisible();
});
it("shows rate-limited AI separately from usable sentiment", () => {
  render(
    <ReviewSheet
      review={{
        ...sample,
        ai: {
          ...sample.ai,
          provider: "openrouter",
          status: "unavailable",
          requestedModel: "fixture/free",
          notice: {
            code: "ai_rate_limited",
            message: "Free model rate limited.",
          },
          attempts: 1,
        },
      }}
    />,
  );
  expect(screen.getByRole("status")).toHaveTextContent(
    "Free model rate limited.",
  );
  expect(
    screen.getByRole("heading", { name: "Notes are unavailable" }),
  ).toBeVisible();
  expect(screen.getByRole("img", { name: /Sample sentiment/ })).toBeVisible();
});
it("uses actual model identity for a routed response", () => {
  render(
    <ReviewSheet
      review={{
        ...sample,
        ai: {
          ...sample.ai,
          status: "complete",
          provider: "openrouter",
          requestedModel: "router/free",
          actualModel: "actual/free",
          sections: { commentDigest: "The sample has mixed reactions." },
        },
      }}
    />,
  );
  expect(screen.getByText(/actual\/free/)).toBeVisible();
  expect(screen.getByText("Requested: router/free")).toBeVisible();
});
it("does not draw invented percentages for an empty sample", () => {
  render(
    <ReviewSheet
      review={{
        ...sample,
        sampled: 0,
        sentiment: {
          ...sample.sentiment,
          totals: { positive: 0, neutral: 0, negative: 0 },
          shares: { positive: 0, neutral: 0, negative: 0 },
        },
      }}
    />,
  );
  expect(screen.getByText(/No public comments were returned/)).toBeVisible();
  expect(screen.queryByRole("img", { name: /Sample sentiment/ })).toBeNull();
});
it("submits the visible ten-comment selection and navigates", async () => {
  push.mockClear();
  const fetcher = vi
    .fn()
    .mockResolvedValueOnce(Response.json(inventory))
    .mockResolvedValueOnce(Response.json(sample));
  vi.stubGlobal("fetch", fetcher);
  render(<ReviewForm />);
  await waitFor(() =>
    expect(
      screen.getByRole("button", { name: /Review this video/ }),
    ).toBeEnabled(),
  );
  fireEvent.change(screen.getByLabelText("YouTube video"), {
    target: { value: sample.video.id },
  });
  expect(screen.getByLabelText("Comment sample")).toHaveValue("10");
  fireEvent.click(screen.getByRole("button", { name: /Review this video/ }));
  await waitFor(() =>
    expect(push).toHaveBeenCalledWith(
      `/review/${sample.video.id}?via=disabled`,
    ),
  );
  expect(JSON.parse(fetcher.mock.calls[1][1].body)).toEqual({
    video: sample.video.id,
    sample: 10,
    provider: "disabled",
  });
});
it("keeps errors on the form", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValueOnce(Response.json(inventory))
      .mockResolvedValueOnce(
        Response.json(
          { error: { message: "YouTube quota unavailable." } },
          { status: 429 },
        ),
      ),
  );
  render(<ReviewForm />);
  await waitFor(() =>
    expect(
      screen.getByRole("button", { name: /Review this video/ }),
    ).toBeEnabled(),
  );
  fireEvent.change(screen.getByLabelText("YouTube video"), {
    target: { value: "example" },
  });
  fireEvent.click(screen.getByRole("button", { name: /Review this video/ }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "YouTube quota unavailable.",
  );
});

it("starts with usable sentiment when the configured cloud default lacks credentials", async () => {
  const unavailable = {
    ...inventory,
    selectionDefault: "openrouter",
    options: inventory.options.map((p) =>
      p.id === "openrouter" ? { ...p, configured: false } : p,
    ),
  };
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(unavailable)));
  render(<ReviewForm />);
  await waitFor(() =>
    expect(screen.getByLabelText("Research notes")).toHaveValue("disabled"),
  );
  await waitFor(() =>
    expect(
      screen.getByRole("button", { name: /Review this video/ }),
    ).toBeEnabled(),
  );
});

it("keeps slow analysis busy and suppresses duplicate submissions", async () => {
  push.mockClear();
  let finish!: (value: Response) => void;
  const pending = new Promise<Response>((resolve) => {
    finish = resolve;
  });
  const fetcher = vi
    .fn()
    .mockResolvedValueOnce(Response.json(inventory))
    .mockReturnValueOnce(pending);
  vi.stubGlobal("fetch", fetcher);
  render(<ReviewForm />);
  const field = screen.getByLabelText("YouTube video");
  await waitFor(() => expect(field).toBeEnabled());
  fireEvent.change(field, { target: { value: sample.video.id } });
  const button = screen.getByRole("button", { name: /Review this video/ });
  fireEvent.click(button);
  fireEvent.click(button);
  expect(screen.getByRole("status")).toHaveTextContent("Retrieving the sample");
  expect(button).toBeDisabled();
  expect(fetcher).toHaveBeenCalledTimes(2);
  finish(Response.json(sample));
  await waitFor(() => expect(push).toHaveBeenCalledTimes(1));
});
it("explains client request timeout without automatically retrying", async () => {
  const fetcher = vi
    .fn()
    .mockResolvedValueOnce(Response.json(inventory))
    .mockRejectedValueOnce(
      new DOMException("private-timeout-details", "TimeoutError"),
    );
  vi.stubGlobal("fetch", fetcher);
  render(<ReviewForm />);
  await waitFor(() =>
    expect(screen.getByLabelText("YouTube video")).toBeEnabled(),
  );
  fireEvent.change(screen.getByLabelText("YouTube video"), {
    target: { value: sample.video.id },
  });
  fireEvent.click(screen.getByRole("button", { name: /Review this video/ }));
  expect(await screen.findByRole("alert")).toHaveTextContent("timed out");
  expect(screen.getByRole("alert")).not.toHaveTextContent(
    "private-timeout-details",
  );
  expect(fetcher).toHaveBeenCalledTimes(2);
  expect(
    screen.getByRole("button", { name: /Review this video/ }),
  ).toBeEnabled();
});
it("refuses a coherent result attributed to a different selected provider", async () => {
  push.mockClear();
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValueOnce(Response.json(inventory))
      .mockResolvedValueOnce(
        Response.json({ ...sample, ai: { ...sample.ai, provider: "ollama" } }),
      ),
  );
  render(<ReviewForm />);
  await waitFor(() =>
    expect(screen.getByLabelText("YouTube video")).toBeEnabled(),
  );
  fireEvent.change(screen.getByLabelText("YouTube video"), {
    target: { value: sample.video.id },
  });
  fireEvent.click(screen.getByRole("button", { name: /Review this video/ }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "different summary provider",
  );
  expect(push).not.toHaveBeenCalled();
});

it.each([
  [10, 0, 0],
  [0, 10, 0],
  [0, 0, 10],
  [1, 1, 1],
  [2, 1, 0],
])(
  "renders boundary and fractional counts %s/%s/%s without changing their meaning",
  (positive, neutral, negative) => {
    const total = positive + neutral + negative;
    const totals = { positive, neutral, negative };
    const shares = {
      positive: (positive / total) * 100,
      neutral: (neutral / total) * 100,
      negative: (negative / total) * 100,
    };
    render(
      <ReviewSheet
        review={{
          ...sample,
          sampled: total,
          sentiment: { ...sample.sentiment, totals, shares },
        }}
      />,
    );
    expect(
      screen.getByRole("img", {
        name: `Sample sentiment: ${shares.positive}% positive, ${shares.neutral}% neutral, ${shares.negative}% negative`,
      }),
    ).toBeVisible();
    for (const key of ["positive", "neutral", "negative"] as const) {
      const rows = document.querySelector(`.sentiment-line.${key}`);
      expect(rows).toHaveTextContent(`${shares[key].toFixed(1)}%`);
      expect(rows).toHaveTextContent(`${totals[key]} comments`);
    }
  },
);
it("focuses the empty video field and associates the visible validation error", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(inventory)));
  render(<ReviewForm />);
  const input = screen.getByLabelText("YouTube video");
  await waitFor(() => expect(input).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: /Review this video/ }));
  expect(input).toHaveFocus();
  expect(input).toHaveAttribute("aria-invalid", "true");
  expect(input).toHaveAccessibleDescription(/Paste a YouTube video link/);
});
it("discloses inventory failure without leaking transport errors or disabling the baseline", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockRejectedValue(new TypeError("private-inventory-detail")),
  );
  render(<ReviewForm />);
  expect(
    await screen.findByText(/Provider status is unavailable/),
  ).toBeVisible();
  expect(screen.queryByText(/private-inventory-detail/)).toBeNull();
  expect(
    screen.getByRole("button", { name: /Review this video/ }),
  ).toBeEnabled();
});
