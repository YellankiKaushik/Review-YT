import httpx
import pytest
from review_yt_core import Failure, extract_id
from review_yt_core.youtube import YouTube, normalize_comment

ID = "aB3_dE5-fG7"


@pytest.mark.parametrize(
    "value",
    [
        ID,
        f"https://youtube.com/watch?v={ID}&t=2",
        f"https://www.youtube.com/shorts/{ID}",
        f"https://youtu.be/{ID}?si=x",
        f"https://m.youtube.com/watch?v={ID}",
        f"https://youtube.com/embed/{ID}",
        f"https://youtube.com/live/{ID}",
    ],
)
def test_supported_video_forms(value):
    assert extract_id(value) == ID


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "a" * 3000,
        "http://youtube.com.evil/watch?v=" + ID,
        "file:///watch?v=" + ID,
        "https://youtu.be/a/b",
        "https://youtube.com/watch?v=short",
        "https://user:pass@youtube.com/watch?v=" + ID,
        "https://youtube.com:abc/watch?v=" + ID,
        "https://youtube.com:8443/watch?v=" + ID,
        "https://[broken",
    ],
)
def test_non_youtube_and_malformed_input_is_rejected(value):
    with pytest.raises(Failure) as error:
        extract_id(value)
    assert error.value.status == 400


def test_normalization_keeps_sentiment_cues():
    assert normalize_comment("  GREAT! &amp; useful.\n Not bad! ") == "GREAT! & useful. Not bad!"


def video():
    return {
        "id": ID,
        "snippet": {"title": "Independent fixture video", "channelTitle": "Fixture channel"},
    }


def comment(number, text):
    return {"snippet": {"topLevelComment": {"id": str(number), "snippet": {"textOriginal": text}}}}


def test_real_protocol_pagination_deduplicates_ids_not_equal_text():
    seen = []

    def handler(request):
        seen.append(request)
        if request.url.path.endswith("/videos"):
            return httpx.Response(200, json={"items": [video()]})
        if "pageToken" not in request.url.params:
            return httpx.Response(
                200,
                json={
                    "items": [comment(1, "Excellent!"), comment(2, "Excellent!")],
                    "nextPageToken": "next",
                },
            )
        return httpx.Response(
            200, json={"items": [comment(2, "Excellent!"), comment(3, "Informational.")]}
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        source = YouTube("fixture-key", client).collect(ID, 3)
    assert source.comments == ["Excellent!", "Excellent!", "Informational."]
    assert len(seen) == 3
    assert seen[2].url.params["pageToken"] == "next"
    assert "author" not in str(source.dump())


@pytest.mark.parametrize(
    "reason,code",
    [
        ("quotaExceeded", "youtube_quota"),
        ("dailyLimitExceeded", "youtube_quota"),
        ("forbidden", "youtube_rejected"),
    ],
)
def test_upstream_quota_and_forbidden(reason, code):
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(403, json={"error": {"errors": [{"reason": reason}]}})
        )
    ) as c:
        with pytest.raises(Failure) as error:
            YouTube("fixture", c).collect(ID, 10)
    assert error.value.code == code


def test_disabled_comments_preserve_metadata():
    def handler(r):
        return (
            httpx.Response(200, json={"items": [video()]})
            if r.url.path.endswith("videos")
            else httpx.Response(403, json={"error": {"errors": [{"reason": "commentsDisabled"}]}})
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as c:
        source = YouTube("fixture", c).collect(ID, 10)
    assert (
        source.video["title"] == "Independent fixture video"
        and source.comments == []
        and source.notices == ["comments_disabled"]
    )


def test_unavailable_video_is_not_fabricated():
    with httpx.Client(
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"items": []}))
    ) as c:
        with pytest.raises(Failure) as error:
            YouTube("fixture", c).collect(ID, 10)
    assert error.value.code == "video_unavailable"


def test_missing_key_makes_no_request():
    with pytest.raises(Failure) as error:
        YouTube("").collect(ID, 10)
    assert error.value.code == "youtube_not_configured"


def test_caption_fetch_unavailability_is_normal(monkeypatch):
    from review_yt_core.youtube import fetch_captions
    from youtube_transcript_api import YouTubeTranscriptApi

    def blocked(*args, **kwargs):
        raise RuntimeError("offline fixture public captions unavailable")

    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", blocked)
    assert fetch_captions(ID) is None


def test_caption_fetch_uses_public_text_and_bounds_it(monkeypatch):
    from types import SimpleNamespace

    from review_yt_core.youtube import fetch_captions
    from youtube_transcript_api import YouTubeTranscriptApi

    monkeypatch.setattr(
        YouTubeTranscriptApi,
        "fetch",
        lambda *args, **kwargs: SimpleNamespace(snippets=[SimpleNamespace(text="caption " * 5000)]),
    )
    text = fetch_captions(ID)
    assert len(text) == 20000 and text.startswith("caption ")
