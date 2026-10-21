"""Bounded opt-in HTTP/browser checks. Credentials are read only from process env."""

import argparse
import ipaddress
import json
import os
import re
import ssl
import subprocess
import time
from pathlib import Path
from urllib.parse import urlsplit

import httpx


def origin(value, local=False):
    parsed = urlsplit(value)
    try:
        port = parsed.port
    except ValueError:
        raise ValueError("Invalid origin port") from None
    loopback = parsed.hostname in ("127.0.0.1", "localhost", "::1")
    try:
        nonpublic = not ipaddress.ip_address(parsed.hostname or "").is_global
    except ValueError:
        nonpublic = loopback or bool(
            parsed.hostname and parsed.hostname.endswith((".localhost", ".local"))
        )
    if (
        not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or port == 0
        or (local and not loopback)
        or (not local and nonpublic)
        or parsed.scheme != "https"
        and not (local and parsed.scheme == "http")
    ):
        raise ValueError("Use HTTPS origins; --local permits loopback origins only")
    return value.rstrip("/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontend", required=True)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--ca-file")
    parser.add_argument("--live-video", help="Opt in to ONE fresh ten-comment sentiment-only POST")
    parser.add_argument(
        "--browser", action="store_true", help="Needs installed Node/Playwright Chromium"
    )
    parser.add_argument("--output", default="artifacts/public-smoke.json")
    args = parser.parse_args()
    try:
        frontend, backend = origin(args.frontend, args.local), origin(args.backend, args.local)
        if args.ca_file and not args.local:
            raise ValueError("Custom CA is supported only for explicitly local verification")
        if args.live_video and not re.fullmatch(r"[A-Za-z0-9_-]{11}", args.live_video):
            raise ValueError("--live-video requires an eleven-character public video ID")
    except ValueError as error:
        parser.error(str(error))
    secrets = [
        os.environ.get(k, "")
        for k in (
            "BACKEND_API_TOKEN",
            "YOUTUBE_API_KEY",
            "OPENROUTER_API_KEY",
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "GROQ_API_KEY",
        )
    ]
    token = os.environ.get("BACKEND_API_TOKEN", "")
    records = []
    report = {
        "scope": "LOCAL HTTP verification" if args.local else "PUBLIC HTTPS verification",
        "frontend": frontend,
        "backend": backend,
        "liveOptIn": bool(args.live_video),
        "negativeValidationPosts": 2,
        "maxLiveAnalysisPosts": 2
        if args.live_video and args.browser
        else 1
        if args.live_video
        else 0,
        "checks": records,
        "pass": False,
    }
    verify = ssl.create_default_context(cafile=args.ca_file) if args.ca_file else True
    result = None
    response_limit = 16000000 if args.local else 4000000
    report["responseByteLimit"] = response_limit
    try:
        with httpx.Client(
            timeout=httpx.Timeout(125, connect=15),
            verify=verify,
            trust_env=False,
            follow_redirects=False,
        ) as client:

            def call(label, method, url, expected, **kwargs):
                start = time.monotonic()
                item = {"check": label, "method": method}
                records.append(item)
                try:
                    with client.stream(method, url, **kwargs) as incoming:
                        item["http"] = incoming.status_code
                        parts, size = [], 0
                        for part in incoming.iter_bytes():
                            size += len(part)
                            if size > response_limit:
                                raise AssertionError("response_size_budget")
                            parts.append(part)
                        response = httpx.Response(
                            incoming.status_code,
                            headers={
                                k: v
                                for k, v in incoming.headers.items()
                                if k.lower()
                                not in ("content-encoding", "content-length", "transfer-encoding")
                            },
                            content=b"".join(parts),
                            request=incoming.request,
                        )
                    item.update(
                        http=response.status_code, ms=round((time.monotonic() - start) * 1000)
                    )
                    if any(
                        value and len(value) >= 12 and value in response.text for value in secrets
                    ):
                        raise AssertionError("private_value_in_response")
                    if response.status_code != expected:
                        try:
                            body = response.json()
                            detail = body.get("error") if isinstance(body, dict) else None
                            code = detail.get("code") if isinstance(detail, dict) else None
                            item["errorCode"] = (
                                code
                                if isinstance(code, str)
                                and re.fullmatch(r"[a-zA-Z0-9_]{1,80}", code)
                                else None
                            )
                        except ValueError:
                            pass
                        raise AssertionError("unexpected_http_status")
                    item["pass"] = True
                    return response
                except (httpx.HTTPError, AssertionError) as error:
                    item["failure"] = (
                        type(error).__name__ if isinstance(error, httpx.HTTPError) else str(error)
                    )
                    raise
                finally:
                    item.setdefault("ms", round((time.monotonic() - start) * 1000))

            call("backend health", "GET", backend + "/health", 200)
            home = call("frontend homepage", "GET", frontend + "/", 200)
            inventory = call("frontend proxy", "GET", frontend + "/api/providers", 200).json()
            assert inventory["constraints"] == {"paid": False, "automaticFallback": False}, (
                "unsafe_provider_policy"
            )
            assert any(x["id"] == "disabled" and x["configured"] for x in inventory["options"]), (
                "baseline_missing"
            )
            report["providers"] = [
                {k: x[k] for k in ("id", "configured", "model", "execution")}
                for x in inventory["options"]
            ]
            call("backend rejects no auth", "GET", backend + "/api/providers", 401)
            call(
                "backend rejects wrong auth",
                "GET",
                backend + "/api/providers",
                401,
                headers={"Authorization": "Bearer smoke-invalid-token"},
            )
            if token:
                call(
                    "backend accepts secure-env auth",
                    "GET",
                    backend + "/api/providers",
                    200,
                    headers={"Authorization": "Bearer " + token},
                )
            call(
                "invalid input",
                "POST",
                frontend + "/api/analyze",
                400,
                json={"video": "invalid", "sample": 10, "provider": "disabled"},
            )
            call(
                "unsupported provider",
                "POST",
                frontend + "/api/analyze",
                400,
                json={"video": "rfscVS0vtbw", "sample": 10, "provider": "not-supported"},
            )
            miss = call(
                "cache-only miss",
                "GET",
                frontend + "/api/results?video=___________&provider=disabled",
                404,
            ).json()
            assert miss["error"]["code"] == "cache_miss"
            assets = list(
                dict.fromkeys(re.findall(r'(?:src|href)="([^"<>]+\.js(?:\?[^"<>]*)?)"', home.text))
            )
            for path in assets[:20]:
                if path.startswith("/_next/"):
                    call(
                        "browser bundle disclosure check",
                        "GET",
                        frontend + path.replace("&amp;", "&"),
                        200,
                    )
            report["browserAssetsChecked"] = min(len(assets), 20)
            if args.live_video:
                result = call(
                    "live ten-comment baseline",
                    "POST",
                    frontend + "/api/analyze",
                    200,
                    json={"video": args.live_video, "sample": 10, "provider": "disabled"},
                ).json()
                assert result["schema"] == "review-yt/v1" and 0 <= result["sampled"] <= 10
                assert result["video"]["id"] == args.live_video
                assert (
                    result["ai"]["status"] == "disabled"
                    and result["ai"]["provider"] == "disabled"
                    and result["ai"]["attempts"] == 0
                )
                totals, shares = result["sentiment"]["totals"], result["sentiment"]["shares"]
                assert sum(totals.values()) == result["sampled"]
                for key in ("positive", "neutral", "negative"):
                    assert (
                        abs(
                            shares[key]
                            - (100 * totals[key] / result["sampled"] if result["sampled"] else 0)
                        )
                        <= 0.02
                    )
                cached = call(
                    "cache-only hit",
                    "GET",
                    frontend + "/api/results?video=" + args.live_video + "&provider=disabled",
                    200,
                ).json()
                assert (
                    cached["caching"]["reused"] and cached["sourceDigest"] == result["sourceDigest"]
                )
                assert cached["sentiment"] == result["sentiment"] and cached["ai"] == result["ai"]
                call(
                    "direct results HTML",
                    "GET",
                    frontend + "/review/" + args.live_video + "?via=disabled",
                    200,
                )
                report["live"] = {
                    k: result[k]
                    for k in ("video", "sampled", "sentiment", "sourceDigest", "ai", "caching")
                }
        if args.browser:
            proc = subprocess.run(
                ["node", str(Path(__file__).with_name("smoke-browser.cjs"))],
                input=json.dumps({"frontend": frontend, "review": result}),
                text=True,
                encoding="utf-8",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=150,
                env={**os.environ, "SMOKE_EXPECT_BASELINE": "1"},
            )
            try:
                report["browser"] = json.loads(proc.stdout)
            except ValueError:
                report["browser"] = {"pass": False, "failure": "browser_process_output"}
            assert proc.returncode == 0 and report["browser"].get("pass"), (
                "browser_verification_failed"
            )
        report["pass"] = True
    except (
        httpx.HTTPError,
        AssertionError,
        ValueError,
        KeyError,
        TypeError,
        OSError,
        subprocess.TimeoutExpired,
    ) as error:
        report["failure"] = (
            str(error) if isinstance(error, AssertionError) else type(error).__name__
        )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
