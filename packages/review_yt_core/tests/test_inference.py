import json
from dataclasses import replace

import httpx
import pytest
from review_yt_core.domain import Evidence, Failure
from review_yt_core.engine import Reviewer
from review_yt_core.providers import AIConfig, Generation, TextProvider, zero_price


@pytest.mark.parametrize(
    "env",
    [
        {"SUMMARY_PROVIDER": "unknown"},
        {"OLLAMA_BASE_URL": "http://10.0.0.1:11434"},
        {"OLLAMA_BASE_URL": "http://127.0.0.1:invalid"},
        {"OLLAMA_BASE_URL": "https://127.0.0.1:11434"},
        {"SUMMARY_FALLBACK_ENABLED": "true"},
        {"OPENROUTER_MODEL": "../../secret"},
        {"SUMMARY_ALLOW_PAID": "yes"},
    ],
)
def test_configuration_fails_closed(env):
    with pytest.raises(ValueError):
        AIConfig.read(env)


@pytest.mark.parametrize(
    "pricing,free",
    [
        ({"prompt": "0", "completion": "0"}, True),
        ({"prompt": "0", "completion": "0", "request": "0.01"}, False),
        ({"prompt": "NaN", "completion": "0"}, False),
        ({"prompt": "0"}, False),
        ({"prompt": "Infinity", "completion": "0"}, False),
    ],
)
def test_price_verification(pricing, free):
    assert zero_price({"pricing": pricing}) is free


def cloud():
    return AIConfig(
        model={"openrouter": "fixture/free"}, credentials={"openrouter": "not-a-live-key"}
    )


@pytest.mark.parametrize(
    "status,code",
    [
        (401, "ai_unauthorized"),
        (402, "ai_payment_required"),
        (429, "ai_rate_limited"),
        (503, "ai_provider_error"),
    ],
)
def test_cloud_errors_never_retry_or_fallback(status, code):
    requests = []

    def handler(r):
        requests.append(r)
        if r.method == "GET":
            return httpx.Response(
                200,
                json={
                    "data": [{"id": "fixture/free", "pricing": {"prompt": "0", "completion": "0"}}]
                },
            )
        return httpx.Response(
            status, json={"error": {"message": "private upstream details must not be reflected"}}
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as c:
        with pytest.raises(Failure) as error:
            TextProvider(cloud(), "openrouter", c).generate("task", "evidence")
    assert error.value.code == code and len(requests) == 2
    assert "private" not in error.value.message
    sent = json.loads(requests[1].content)
    assert sent["provider"] == {
        "allow_fallbacks": False,
        "max_price": {"prompt": 0, "completion": 0},
    }


def test_unknown_prices_block_before_generation():
    calls = []

    def handler(r):
        calls.append(r)
        return httpx.Response(
            200,
            json={"data": [{"id": "fixture/free", "pricing": {"prompt": "1", "completion": "0"}}]},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as c:
        with pytest.raises(Failure) as error:
            TextProvider(cloud(), "openrouter", c).generate("task", "evidence")
    assert error.value.code == "ai_price_unverified" and len(calls) == 1


@pytest.mark.parametrize("identity", ["gemini", "groq", "openai", "openrouter"])
def test_optional_cloud_missing_credentials(identity):
    assert not TextProvider(AIConfig(model={identity: "example"}), identity).availability()[0]


def test_actual_returned_router_model_and_usage():
    def handler(r):
        if r.method == "GET":
            return httpx.Response(
                200,
                json={
                    "data": [{"id": "fixture/free", "pricing": {"prompt": "0", "completion": "0"}}]
                },
            )
        return httpx.Response(
            200,
            json={
                "model": "actual/free",
                "choices": [{"message": {"content": "A note"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 12, "total_tokens": 19, "hidden": "private"},
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as c:
        result = TextProvider(cloud(), "openrouter", c).generate("task", "data")
    assert (
        result.model == "actual/free"
        and result.usage == {"prompt_tokens": 12, "total_tokens": 19}
        and result.complete
    )


@pytest.mark.parametrize(
    "identity,body",
    [
        (
            "openai",
            {
                "model": "response-model",
                "status": "completed",
                "output": [
                    {"type": "message", "content": [{"type": "output_text", "text": "note"}]}
                ],
            },
        ),
        (
            "gemini",
            {
                "modelVersion": "gemini-actual",
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "hidden", "thought": True}, {"text": "note"}]
                        },
                        "finishReason": "STOP",
                    }
                ],
            },
        ),
        (
            "groq",
            {
                "model": "groq-actual",
                "choices": [{"message": {"content": "note"}, "finish_reason": "stop"}],
            },
        ),
    ],
)
def test_optional_provider_protocols(identity, body):
    config = AIConfig(
        model={identity: "fixture"},
        credentials={identity: "not-live"},
        paid=identity == "openai",
        confirmed=(identity,),
    )
    with httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=body))) as c:
        result = TextProvider(config, identity, c).generate("task", "data")
    assert result.text == "note" and result.complete


def source(comments=None):
    return Evidence(
        {
            "id": "aB3_dE5-fG7",
            "title": "Fixture",
            "channel": "QA",
            "published": None,
            "thumbnail": "https://i.ytimg.com/vi/aB3_dE5-fG7/hqdefault.jpg",
        },
        comments
        if comments is not None
        else [
            "Excellent and helpful!",
            "Awful waste of time.",
            "The video was uploaded yesterday.",
        ],
    )


def test_baseline_totals_and_empty_sample():
    r = Reviewer().review(source(), "disabled")
    assert r["sampled"] == 3 and r["sentiment"]["totals"] == {
        "positive": 1,
        "neutral": 1,
        "negative": 1,
    }
    assert r["ai"]["status"] == "disabled"
    assert Reviewer().review(source([]), "disabled")["sentiment"]["shares"] == {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
    }


@pytest.mark.parametrize(
    "complete,text,notice",
    [
        (False, '{"commentDigest":"unfinished"}', "ai_incomplete"),
        (True, "not JSON", "ai_note_format"),
        (True, '{"commentDigest":4}', "ai_note_format"),
    ],
)
def test_incomplete_and_invalid_notes_keep_baseline(complete, text, notice):
    class Adapter:
        def generate(self, *args):
            return Generation(text, "fixture-model", {}, complete, 15)

    r = Reviewer(provider_factory=lambda p: Adapter()).review(source(), "ollama")
    assert (
        r["sampled"] == 3
        and r["ai"]["status"] == "unavailable"
        and r["ai"]["notice"]["code"] == notice
        and not r["ai"]["sections"]
    )


def test_valid_grounded_sections_and_attribution():
    class Adapter:
        def generate(self, *args):
            return Generation(
                json.dumps(
                    {
                        "commentDigest": "The small sample contains praise and criticism.",
                        "captionDigest": "invented captions must be suppressed",
                        "creatorNotes": "Suggestion: check a larger sample before changing content.",
                    }
                ),
                "fixture-model",
                {"inputTokens": 20},
                True,
                12,
            )

    r = Reviewer(provider_factory=lambda p: Adapter()).review(source(), "ollama")
    assert (
        r["ai"]["status"] == "complete"
        and r["ai"]["sections"]["captionDigest"] == ""
        and r["ai"]["actualModel"] == "fixture-model"
    )


def test_long_input_is_bounded_and_disclosed_without_changing_sentiment():
    captured = []

    class Adapter:
        def generate(self, instructions, evidence):
            captured.append(evidence)
            return Generation(
                json.dumps(
                    {
                        "commentDigest": "Only the included excerpt was considered.",
                        "captionDigest": "A short excerpt.",
                        "creatorNotes": "Suggestion: inspect the full sample.",
                    }
                ),
                "test",
                {},
                True,
                10,
            )

    evidence = replace(source(["Excellent! " + '"' * 20000]), captions="x" * 20000)
    result = Reviewer(provider_factory=lambda p: Adapter()).review(evidence, "ollama")
    assert len(captured[0]) < 14000
    assert result["sampled"] == 1 and any("shortened" in n for n in result["warnings"])
    assert json.loads(captured[0])["includedCount"] == 1


def test_broken_code_fence_is_a_safe_model_format_failure():
    class Adapter:
        def generate(self, *args):
            return Generation("```", "test", {}, True, 1)

    result = Reviewer(provider_factory=lambda p: Adapter()).review(source(), "ollama")
    assert (
        result["ai"]["status"] == "unavailable"
        and result["ai"]["notice"]["code"] == "ai_note_format"
    )
