import json

import pytest
from review_api import create_application
from review_api.store import Store
from review_yt_core import Evidence, Failure
from review_yt_core.engine import Reviewer
from review_yt_core.providers import AIConfig, Generation

ID = "aB3_dE5-fG7"
HEAD = {"Authorization": "Bearer test-backend-token"}


class Source:
    calls = 0

    def collect(self, video, sample):
        self.calls += 1
        return Evidence(
            {
                "id": video,
                "title": "Independent offline fixture",
                "channel": "Testing only",
                "published": None,
                "thumbnail": f"https://i.ytimg.com/vi/{video}/hqdefault.jpg",
            },
            ["Helpful and excellent!", "Awful waste of time.", "Recorded yesterday."][:sample],
        )


class Adapter:
    def __init__(self, provider, calls):
        self.provider, self.calls = provider, calls

    def generate(self, *args):
        self.calls.append(self.provider)
        if self.provider == "openrouter":
            raise Failure("ai_rate_limited", "Fixture free model is rate limited.", 503)
        return Generation(
            json.dumps(
                {
                    "commentDigest": "Fixture feedback is mixed.",
                    "captionDigest": "",
                    "creatorNotes": "Suggestion: gather more feedback.",
                }
            ),
            "local-fixture-model",
            {"inputTokens": 12},
            True,
            5,
        )


@pytest.fixture
def service(tmp_path, monkeypatch):
    config = AIConfig(
        allowed=("disabled", "ollama", "openrouter"),
        model={"ollama": "local-fixture-model", "openrouter": "fixture/free"},
        credentials={"openrouter": "not-live"},
    )
    source, calls = Source(), []
    reviewer = Reviewer(ai=config, youtube=source, provider_factory=lambda p: Adapter(p, calls))
    cache = Store(tmp_path / "test.sqlite")
    app = create_application(
        {"TESTING": True, "API_TOKEN": "test-backend-token", "AI_CONFIG": config}, reviewer, cache
    )
    monkeypatch.setattr(
        "review_api.TextProvider.discover", lambda self: [{"name": "local-fixture-model"}]
    )
    return app.test_client(), source, calls, cache, app


def post(client, provider="disabled", **extra):
    return client.post(
        "/api/analyze",
        headers=HEAD,
        json={"video": ID, "sample": 10, "provider": provider, **extra},
    )


def test_health_auth_and_secret_exclusions(service):
    c, *_ = service
    assert c.get("/health").status_code == 200
    assert c.get("/api/providers").status_code == 401
    inventory = c.get("/api/providers", headers=HEAD)
    assert (
        inventory.status_code == 200
        and b"not-live" not in inventory.data
        and b"test-backend-token" not in inventory.data
    )
    assert inventory.json["constraints"] == {"paid": False, "automaticFallback": False}
    assert inventory.headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize(
    "extra",
    [
        {"sample": True},
        {"sample": 501},
        {"sample": 0},
        {"sample": "10"},
        {"provider": "unknown"},
        {"provider": []},
        {"key": "not-allowed"},
        {"video": "invalid"},
    ],
)
def test_request_schema(service, extra):
    assert post(service[0], **extra).status_code == 400


def test_request_sizes_and_methods(service):
    c = service[0]
    assert c.post("/api/analyze", headers=HEAD, data="x").status_code == 415
    assert (
        c.post(
            "/api/analyze", headers={**HEAD, "Content-Type": "application/json"}, data="x" * 5000
        ).status_code
        == 413
    )
    assert c.get("/api/analyze", headers=HEAD).status_code == 405


def test_cache_only_get_never_collects(service):
    c, source, calls, *_ = service
    assert c.get(f"/api/results?video={ID}&provider=disabled", headers=HEAD).status_code == 404
    assert source.calls == 0 and calls == []
    first = post(c).json
    second = post(c).json
    assert not first["caching"]["reused"] and second["caching"]["reused"]
    assert source.calls == 1
    assert c.get(f"/api/results?video={ID}&provider=disabled", headers=HEAD).json["caching"][
        "reused"
    ]


def test_provider_isolation_and_failure_preserves_local_result(service):
    c, source, calls, *_ = service
    gemma = post(c, "ollama").json
    failed = post(c, "openrouter").json
    again = post(c, "ollama").json
    assert source.calls == 1 and calls == ["ollama", "openrouter"]
    assert (
        gemma["ai"]["status"] == "complete"
        and failed["ai"]["status"] == "unavailable"
        and failed["sampled"] == 3
    )
    assert (
        gemma["sourceDigest"] == failed["sourceDigest"]
        and again["ai"] == gemma["ai"]
        and again["caching"]["reused"]
    )
    assert c.get(f"/api/results?video={ID}&provider=openrouter", headers=HEAD).status_code == 404


def test_cache_expiry_and_provider_lookup(tmp_path):
    now = [100.0]
    cache = Store(tmp_path / "expiry.sqlite", lambda: now[0])
    cache.write("source", "s", ID, "", {"comments": ["fixture"]}, 5)
    cache.write("review", "r", ID, "ollama", {"sampled": 1}, 20)
    assert cache.latest(ID, "openrouter") is None
    now[0] = 106
    assert cache.read("source", "s") is None and cache.latest(ID, "ollama")
    now[0] = 121
    assert cache.latest(ID, "ollama") is None


def test_post_rate_limit(service):
    c, source, calls, cache, app = service
    app.config["RATE_REQUESTS"] = 1
    assert post(c).status_code == 200 and post(c).status_code == 429


def test_missing_server_token_fails_closed(service):
    c, source, calls, cache, app = service
    app.config["API_TOKEN"] = ""
    assert c.get("/api/providers", headers=HEAD).status_code == 503


def test_wrong_and_non_ascii_auth_are_rejected_not_server_errors(service):
    client = service[0]
    for value in ("Bearer incorrect", "Bearer wrong-☃"):
        response = client.get("/api/providers", headers={"Authorization": value})
        assert response.status_code == 401
        assert response.json["error"]["code"] == "not_authorized"


@pytest.mark.parametrize("operation", ["read", "write"])
def test_unavailable_sqlite_preserves_baseline_and_sanitizes_details(
    service, monkeypatch, caplog, operation
):
    import sqlite3

    client, source, _, cache, _ = service

    def fail(*args):
        raise sqlite3.OperationalError("private-file-path-and-secret-must-not-leak")

    monkeypatch.setattr(cache, operation, fail)
    caplog.set_level("INFO", logger="review.http")
    response = post(client)
    assert response.status_code == 200 and response.json["sampled"] == 3
    assert any("caching is unavailable" in message for message in response.json["warnings"])
    assert b"private-file-path" not in response.data
    assert "private-file-path" not in caplog.text and source.calls == 1


def test_cache_only_failure_is_explicit_and_never_collects(service, monkeypatch):
    import sqlite3

    client, source, calls, cache, _ = service

    def fail(*args):
        raise sqlite3.OperationalError("not-safe-to-reflect")

    monkeypatch.setattr(cache, "latest", fail)
    response = client.get(f"/api/results?video={ID}&provider=disabled", headers=HEAD)
    assert response.status_code == 503
    assert response.json["error"]["code"] == "cache_unavailable"
    assert source.calls == 0 and calls == [] and b"not-safe" not in response.data


def test_cache_initialization_failure_still_allows_real_baseline(service, monkeypatch):
    import sqlite3

    _, source, calls, _, original = service

    def fail(*args):
        raise sqlite3.OperationalError("unwritable-private-path")

    monkeypatch.setattr("review_api.Store", fail)
    app = create_application(
        {"API_TOKEN": "test-backend-token", "AI_CONFIG": original.config["AI_CONFIG"]},
        original.extensions["review_engine"],
    )
    with app.test_client() as client:
        assert post(client).status_code == 200
        response = client.get(f"/api/results?video={ID}&provider=disabled", headers=HEAD)
        assert response.status_code == 503
    assert source.calls == 1 and calls == []


def test_concurrent_duplicate_requests_collect_once(service, monkeypatch):
    import time
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    _, source, _, _, app = service
    original = source.collect

    def slow(*args):
        time.sleep(0.05)
        return original(*args)

    monkeypatch.setattr(source, "collect", slow)
    barrier = Barrier(4)

    def call(_):
        barrier.wait(timeout=5)
        with app.test_client() as client:
            response = post(client)
            return response.status_code, response.json

    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(call, range(4)))
    assert all(status == 200 for status, _ in responses)
    assert source.calls == 1
    assert sum(not body["caching"]["reused"] for _, body in responses) == 1


def test_restart_reads_persisted_review_without_collecting(service):
    client, source, calls, cache, old = service
    first = post(client).json
    restarted = create_application(
        {"API_TOKEN": "test-backend-token", "AI_CONFIG": old.config["AI_CONFIG"]},
        old.extensions["review_engine"],
        Store(cache.filename),
    )
    with restarted.test_client() as client:
        response = client.get(f"/api/results?video={ID}&provider=disabled", headers=HEAD)
    assert response.status_code == 200 and response.json["sourceDigest"] == first["sourceDigest"]
    assert response.json["caching"]["reused"] and source.calls == 1 and calls == []


def test_expired_result_get_never_reanalyzes(service):
    client, source, calls, cache, _ = service
    now = [100.0]
    cache.clock = lambda: now[0]
    assert post(client).status_code == 200
    now[0] += 1801
    response = client.get(f"/api/results?video={ID}&provider=disabled", headers=HEAD)
    assert response.status_code == 404 and source.calls == 1 and calls == []


def test_public_wsgi_missing_required_settings_fails_before_binding(monkeypatch):
    import runpy
    from pathlib import Path

    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("YOUTUBE_API_KEY", "")
    monkeypatch.setenv("BACKEND_API_TOKEN", "")
    with pytest.raises(
        RuntimeError, match="Public backend requires: YOUTUBE_API_KEY, BACKEND_API_TOKEN"
    ):
        runpy.run_path(str(Path(__file__).parents[1] / "serve.py"))


@pytest.mark.parametrize("offline", [False, True])
def test_ollama_inventory_reports_missing_model_or_offline(service, monkeypatch, offline):
    def discover(self):
        if offline:
            raise Failure("upstream_connection", "Private fixture details must not escape.")
        return [{"name": "different-installed-fixture"}]

    monkeypatch.setattr("review_api.TextProvider.discover", discover)
    response = service[0].get("/api/providers", headers=HEAD)
    option = next(item for item in response.json["options"] if item["id"] == "ollama")
    assert response.status_code == 200 and option["configured"] is False
    assert "Private" not in option["description"]
