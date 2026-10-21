import html
import re
import time
from urllib.parse import parse_qs, urlparse

from .domain import Evidence, Failure
from .network import exchange

_ID = re.compile(r"[A-Za-z0-9_-]{11}\Z")


def extract_id(value):
    if not isinstance(value, str) or len(value) > 2048:
        raise Failure("video_input", "Provide a public YouTube URL or video ID.", 400)
    value = value.strip()
    if _ID.fullmatch(value):
        return value
    try:
        parsed = urlparse(value)
        _ = parsed.port
    except ValueError:
        raise Failure("video_input", "This is not a supported YouTube URL.", 400) from None
    if (
        parsed.scheme not in ("http", "https")
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 80, 443)
    ):
        raise Failure("video_input", "This is not a supported YouTube URL.", 400)
    host = (parsed.hostname or "").lower()
    bits = parsed.path.strip("/").split("/")
    candidate = ""
    if host == "youtu.be" and len(bits) == 1:
        candidate = bits[0]
    elif host in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif len(bits) == 2 and bits[0] in ("shorts", "embed", "live"):
            candidate = bits[1]
    if not _ID.fullmatch(candidate):
        raise Failure("video_input", "This is not a supported YouTube URL.", 400)
    return candidate


def normalize_comment(value):
    return " ".join(html.unescape(value).split()) if isinstance(value, str) else ""


class YouTube:
    origin = "https://www.googleapis.com/youtube/v3/"

    def __init__(self, key, client=None):
        self.key, self.client = key, client

    def query(self, resource, _seconds=12, **parameters):
        if not self.key:
            raise Failure(
                "youtube_not_configured",
                "YouTube access has not been configured on the server.",
                503,
            )
        status, body = exchange(
            "GET",
            self.origin + resource,
            params={**parameters, "key": self.key},
            client=self.client,
            timeout=_seconds,
        )
        if status >= 300:
            error = body.get("error")
            errors = error.get("errors", []) if isinstance(error, dict) else []
            if not isinstance(errors, list):
                errors = []
            reasons = {
                e["reason"]
                for e in errors
                if isinstance(e, dict) and isinstance(e.get("reason"), str)
            }
            if "commentsDisabled" in reasons:
                raise Failure(
                    "comments_disabled", "Public comments are disabled for this video.", 409
                )
            if reasons & {"quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded"}:
                raise Failure(
                    "youtube_quota",
                    "YouTube quota is currently unavailable. Try again after it resets.",
                    429,
                )
            raise Failure(
                "youtube_rejected",
                "YouTube could not return this resource.",
                404 if status == 404 else 502,
            )
        if not isinstance(body.get("items"), list):
            raise Failure("youtube_format", "YouTube returned an unexpected resource format.")
        return body

    def collect(self, video_id, limit):
        if type(limit) is not int or not 1 <= limit <= 500:
            raise Failure("sample_input", "Choose between 1 and 500 comments.", 400)
        deadline = time.monotonic() + 25
        videos = self.query("videos", part="snippet,statistics", id=video_id)["items"]
        if not videos:
            raise Failure("video_unavailable", "That video is unavailable or is not public.", 404)
        first = videos[0]
        snippet = first.get("snippet", {}) if isinstance(first, dict) else {}
        if not isinstance(snippet, dict) or not isinstance(snippet.get("title"), str):
            raise Failure("youtube_format", "Video metadata is incomplete.")
        video = {
            "id": video_id,
            "title": snippet["title"],
            "channel": snippet.get("channelTitle", ""),
            "published": snippet.get("publishedAt"),
            "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        }
        comments, seen, tokens, notices = [], set(), set(), []
        token = None
        while len(comments) < limit:
            parameters = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": min(100, limit - len(comments)),
                "order": "relevance",
                "textFormat": "plainText",
            }
            if token:
                parameters["pageToken"] = token
            try:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise Failure(
                        "youtube_timeout", "YouTube retrieval exhausted its time budget.", 504
                    )
                page = self.query("commentThreads", _seconds=min(12, remaining), **parameters)
            except Failure as error:
                if error.code != "comments_disabled":
                    raise
                notices.append(error.code)
                break
            for item in page["items"]:
                snippet = item.get("snippet") if isinstance(item, dict) else None
                top = snippet.get("topLevelComment") if isinstance(snippet, dict) else None
                detail = top.get("snippet") if isinstance(top, dict) else None
                if not isinstance(detail, dict):
                    raise Failure(
                        "youtube_format", "YouTube returned an unexpected comment format."
                    )
                identity = top.get("id")
                if identity is not None and not isinstance(identity, str):
                    raise Failure(
                        "youtube_format", "YouTube returned an unexpected comment format."
                    )
                text = normalize_comment(detail.get("textOriginal"))
                if identity and identity not in seen and text:
                    seen.add(identity)
                    comments.append(text)
            token = page.get("nextPageToken")
            if token is not None and not isinstance(token, str):
                raise Failure("youtube_format", "YouTube returned an unexpected pagination format.")
            if not token or token in tokens or len(comments) >= limit or len(tokens) >= 9:
                break
            tokens.add(token)
        if not comments and not notices:
            notices.append("comments_empty")
        return Evidence(video, comments[:limit], notices=notices)


def fetch_captions(video_id):
    # Optional public captions only; no authentication, download or access bypass.
    try:
        import requests
        from youtube_transcript_api import YouTubeTranscriptApi

        class TimedSession(requests.Session):
            def request(self, *args, **kwargs):
                kwargs["timeout"] = 8
                return super().request(*args, **kwargs)

        with TimedSession() as session:
            session.trust_env = False
            transcript = YouTubeTranscriptApi(http_client=session).fetch(video_id, languages=["en"])
            return " ".join(s.text for s in transcript.snippets)[:20000]
    except Exception:
        return None
