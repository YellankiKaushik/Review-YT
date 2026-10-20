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
