"""Report only non-secret configuration and local HTTP status; never generate AI."""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def configuration():
    root = {**dotenv_values(ROOT / ".env"), **os.environ}
    web = {**dotenv_values(ROOT / "apps/web/.env.local"), **os.environ}
    token = root.get("BACKEND_API_TOKEN", "")
    report = {
        "rootEnvironmentExists": (ROOT / ".env").is_file(),
        "webEnvironmentExists": (ROOT / "apps/web/.env.local").is_file(),
        "youtubePresent": bool(root.get("YOUTUBE_API_KEY")),
        "openrouterPresent": bool(root.get("OPENROUTER_API_KEY")),
        "backendTokenPresent": bool(token),
        "tokensMatch": bool(token) and token == web.get("BACKEND_API_TOKEN"),
        "frontendBackendIsExpectedLoopback": web.get("BACKEND_URL") == "http://127.0.0.1:5100",
        "paidDisabled": root.get("SUMMARY_ALLOW_PAID", "false").lower() == "false",
        "fallbackDisabled": root.get("SUMMARY_FALLBACK_ENABLED", "false").lower() == "false",
    }
    good = all(value for key, value in report.items() if key != "openrouterPresent")
    return report, token, good


def main():
    report, token, good = configuration()
    if "--configuration-only" not in sys.argv:
        results = []
        with httpx.Client(timeout=12, trust_env=False) as client:
            for label, url, auth in (
                ("health", "http://127.0.0.1:5100/health", False),
                ("homepage", "http://127.0.0.1:3200/", False),
                ("authenticatedInventory", "http://127.0.0.1:5100/api/providers", True),
                ("frontendProxy", "http://127.0.0.1:3200/api/providers", False),
            ):
                item = {"check": label}
                try:
                    response = client.get(
                        url, headers={"Authorization": "Bearer " + token} if auth else {}
                    )
                    item["http"] = response.status_code
                    good = good and response.status_code == 200
                    if "Inventory" in label or label == "frontendProxy":
                        data = response.json()
                        item["constraints"] = data.get("constraints")
                        item["providers"] = [
                            {key: option[key] for key in ("id", "configured", "model", "execution")}
                            for option in data.get("options", [])
                        ]
                        good = good and data.get("constraints") == {
                            "paid": False,
                            "automaticFallback": False,
                        }
                except (httpx.HTTPError, ValueError, KeyError) as error:
                    item["errorType"] = type(error).__name__
                    good = False
                results.append(item)
        report["checks"] = results
    print(json.dumps(report))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
