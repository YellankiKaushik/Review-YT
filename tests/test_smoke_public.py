"""Offline protocol checks for the post-deployment verifier; no live API calls."""

import importlib.util
import json
import sys
from pathlib import Path

import httpx
import pytest

spec = importlib.util.spec_from_file_location(
    "smoke_public", Path(__file__).parents[1] / "scripts/smoke-public.py"
)
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)

FRONTEND = "https://frontend.example"
BACKEND = "https://backend.example"
ID = "aB3_dE5-fG7"
INVENTORY = {
    "constraints": {"paid": False, "automaticFallback": False},
    "options": [{"id": "disabled", "configured": True, "model": "", "execution": "none"}],
}
REVIEW = {
    "schema": "review-yt/v1",
    "video": {
        "id": ID,
        "title": "Offline test fixture",
        "channel": "Tests only",
        "thumbnail": "https://i.ytimg.com/vi/" + ID + "/hqdefault.jpg",
        "published": None,
    },
    "sampled": 1,
    "sentiment": {
        "totals": {"positive": 1, "neutral": 0, "negative": 0},
        "shares": {"positive": 100, "neutral": 0, "negative": 0},
    },
    "sourceDigest": "offline-test-digest",
    "ai": {"status": "disabled", "provider": "disabled", "attempts": 0, "sections": {}},
    "caching": {"reused": False},
}


@pytest.mark.parametrize(
    "url",
    [
        "http://public.example",
        "https://user:private@public.example",
        "https://public.example/path",
        "https://public.example?key=private",
        "https://public.example/#fragment",
        "https://public.example:0",
        "https://public.example:wrong",
        "https://[broken",
    ],
)
def test_unsafe_or_non_origin_urls_are_rejected(url):
    with pytest.raises(ValueError):
        smoke.origin(url)


@pytest.mark.parametrize("url", ["https://localhost", "https://127.0.0.1", "https://[::1]"])
def test_loopback_cannot_be_labeled_public_verification(url):
    with pytest.raises(ValueError):
        smoke.origin(url)


def test_explicit_local_scope_accepts_only_loopback():
    assert smoke.origin("http://127.0.0.1:3202/", True) == "http://127.0.0.1:3202"
    assert smoke.origin("https://localhost:5103", True) == "https://localhost:5103"
    with pytest.raises(ValueError):
        smoke.origin("https://public.example", True)


@pytest.fixture
def runner(tmp_path, monkeypatch):
    for name in (
        "BACKEND_API_TOKEN",
        "YOUTUBE_API_KEY",
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    actual_client = httpx.Client
    output = tmp_path / "result.json"
    requests = []
    options = []

    def run(fault=None, extra=()):
        def handler(request):
            requests.append(request)
            if fault:
                response = fault(request)
                if response is not None:
                    return response
            path = request.url.path
            if path == "/health":
                return httpx.Response(200, json={"status": "ok"})
            if path in ("/", "/_next/static/smoke.js") or path.startswith("/review/"):
                return httpx.Response(200, text="<!doctype html><p>Offline fixture homepage</p>")
            if path == "/api/providers":
                authorized = (
                    request.url.host == "frontend.example"
                    or request.headers.get("authorization") == "Bearer verifier-private-test-token"
                )
                return httpx.Response(
                    200 if authorized else 401,
                    json=INVENTORY if authorized else {"error": {"code": "not_authorized"}},
                )
            if path == "/api/analyze":
                body = json.loads(request.content)
                if body.get("video") == "invalid" or body.get("provider") != "disabled":
                    return httpx.Response(400, json={"error": {"code": "request_shape"}})
                assert body == {"video": ID, "sample": 10, "provider": "disabled"}
                return httpx.Response(200, json=REVIEW)
            if path == "/api/results":
                if request.url.params.get("video") == ID:
                    return httpx.Response(200, json={**REVIEW, "caching": {"reused": True}})
                return httpx.Response(404, json={"error": {"code": "cache_miss"}})
            raise AssertionError("Verifier made an unexpected fixture request")

        def client(**kwargs):
            options.append(kwargs)
            return actual_client(transport=httpx.MockTransport(handler))

        monkeypatch.setattr(smoke.httpx, "Client", client)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "smoke-public.py",
                "--frontend",
                FRONTEND,
                "--backend",
                BACKEND,
                "--output",
                str(output),
                *extra,
            ],
        )
        code = smoke.main()
        return code, json.loads(output.read_text(encoding="utf-8")), requests, options

    return run


def test_default_smoke_never_posts_real_analysis_and_auth_is_backend_only(runner, monkeypatch):
    monkeypatch.setenv("BACKEND_API_TOKEN", "verifier-private-test-token")
    code, report, requests, options = runner()
    assert code == 0 and report["pass"] and not report["liveOptIn"]
    assert report["maxLiveAnalysisPosts"] == 0 and "live" not in report
    posts = [json.loads(request.content) for request in requests if request.method == "POST"]
    assert len(posts) == 2 and all(
        body["video"] == "invalid" or body["provider"] != "disabled" for body in posts
    )
    for request in requests:
        if request.headers.get("authorization") == "Bearer verifier-private-test-token":
            assert request.url.host == "backend.example" and request.url.path == "/api/providers"
    assert options[0]["trust_env"] is False and options[0]["follow_redirects"] is False


def test_explicit_live_opt_in_is_one_bounded_baseline_post(runner):
    code, report, requests, _ = runner(extra=("--live-video", ID))
    real_posts = [
        request
        for request in requests
        if request.method == "POST" and json.loads(request.content).get("video") == ID
    ]
    assert code == 0 and report["pass"] and report["liveOptIn"]
    assert len(real_posts) == 1 and json.loads(real_posts[0].content)["sample"] == 10
    assert report["maxLiveAnalysisPosts"] == 1 and report["live"]["ai"]["attempts"] == 0


def test_disclosed_private_response_fails_without_echoing_secret(runner, monkeypatch, capsys):
    private = "verifier-private-youtube-value"
    monkeypatch.setenv("YOUTUBE_API_KEY", private)
    code, report, _, _ = runner(lambda request: httpx.Response(200, text=private))
    assert code == 1 and not report["pass"] and report["failure"] == "private_value_in_response"
    assert private not in json.dumps(report) and private not in capsys.readouterr().out


def test_transport_failure_is_reported_without_exception_details(runner, capsys):
    def timeout(request):
        raise httpx.ReadTimeout("private-url-and-credential", request=request)

    code, report, _, _ = runner(timeout)
    assert code == 1 and report["failure"] == "ReadTimeout"
    assert report["checks"][0]["failure"] == "ReadTimeout"
    assert "private-url" not in capsys.readouterr().out


@pytest.mark.parametrize("body", [[], {"error": []}, {"error": "private-untrusted-error"}])
def test_non_object_http_error_is_still_a_recorded_failure(runner, body):
    code, report, _, _ = runner(lambda request: httpx.Response(503, json=body))
    assert code == 1 and not report["pass"]
    assert report["checks"][0]["http"] == 503
    assert report["failure"] == "unexpected_http_status"
    assert "private-untrusted-error" not in json.dumps(report)


def test_invalid_live_id_never_reaches_network(monkeypatch, tmp_path):
    def forbidden(**kwargs):
        raise AssertionError("No client may be created for rejected input")

    monkeypatch.setattr(smoke.httpx, "Client", forbidden)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "smoke-public.py",
            "--frontend",
            FRONTEND,
            "--backend",
            BACKEND,
            "--live-video",
            "bad",
            "--output",
            str(tmp_path / "unused.json"),
        ],
    )
    with pytest.raises(SystemExit) as error:
        smoke.main()
    assert error.value.code == 2


def test_custom_ca_cannot_be_used_for_public_scope(monkeypatch, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "smoke-public.py",
            "--frontend",
            FRONTEND,
            "--backend",
            BACKEND,
            "--ca-file",
            str(tmp_path / "not-a-real-cert"),
        ],
    )
    with pytest.raises(SystemExit) as error:
        smoke.main()
    assert error.value.code == 2


def test_response_budget_stops_stream_before_reading_more(runner):
    class OversizedStream(httpx.SyncByteStream):
        def __iter__(self):
            yield b"x" * 4000001
            raise AssertionError("read_past_response_size_budget")

    code, report, _, _ = runner(lambda request: httpx.Response(200, stream=OversizedStream()))
    assert code == 1 and not report["pass"]
    assert report["failure"] == "response_size_budget"


def test_compressed_http_response_is_decoded_once(runner):
    import gzip

    def compressed_home(request):
        if request.url.host == "frontend.example" and request.url.path == "/":
            return httpx.Response(
                200,
                content=gzip.compress(b"<!doctype html><p>Compressed fixture</p>"),
                headers={"Content-Encoding": "gzip", "Content-Type": "text/html"},
            )

    code, report, _, _ = runner(compressed_home)
    assert code == 0 and report["pass"]
