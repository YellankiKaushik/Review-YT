import hashlib
import hmac
import json
import logging
import os
import sqlite3
import time
import uuid
from collections import OrderedDict, deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from review_yt_core import Evidence, Failure, Reviewer, extract_id
from review_yt_core.engine import NOTE_REVISION
from review_yt_core.providers import AIConfig, TextProvider
from werkzeug.exceptions import HTTPException

from .store import Store

ROOT = Path(__file__).resolve().parents[3]


def create_application(config=None, reviewer=None, store=None):
    load_dotenv(ROOT / ".env", override=False)
    app = Flask(__name__)
    app.config.update(
        MAX_CONTENT_LENGTH=4096,
        API_TOKEN=os.getenv("BACKEND_API_TOKEN", ""),
        TESTING=False,
        RATE_REQUESTS=20,
        RATE_SECONDS=60,
    )
    if config:
        app.config.update(config)
    settings = app.config.get("AI_CONFIG") or AIConfig.read(os.environ)
    engine = reviewer or Reviewer(
        os.getenv("YOUTUBE_API_KEY", ""),
        settings,
        captions=os.getenv("TRANSCRIPTS_ENABLED", "false").lower() == "true",
    )
    if store is not None:
        cache = store
    else:
        try:
            cache = Store(os.getenv("CACHE_PATH", str(ROOT / ".cache/reviews.sqlite")))
        except (OSError, sqlite3.Error):
            cache = None

    def cache_call(operation, *args):
        try:
            if cache is None:
                raise sqlite3.OperationalError()
            return getattr(cache, operation)(*args)
        except (OSError, sqlite3.Error, ValueError):
            # The cache is an optimization: never discard a real baseline because
            # ephemeral storage is unavailable. Do not log exception paths/content.
            g.cache_unavailable = True
            return None

    locks = [Lock() for _ in range(24)]
    arrivals, arrival_lock = OrderedDict(), Lock()
    app.extensions.update(review_engine=engine, review_store=cache)

    def respond_review(saved, reused):
        body, expiry = saved
        if getattr(g, "cache_unavailable", False):
            body = {
                **body,
                "warnings": body.get("warnings", [])
                + [
                    "Server caching is unavailable; this result is temporary and may need reanalysis."
                ],
            }
        return jsonify(
            {
                **body,
                "caching": {
                    "reused": reused,
                    "validUntil": datetime.fromtimestamp(expiry, timezone.utc).isoformat(),
                },
            }
        )

    @app.before_request
    def guard():
        g.started = time.monotonic()
        g.trace = uuid.uuid4().hex
        if request.path == "/health":
            return None
        token = app.config["API_TOKEN"]
        if not token:
            raise Failure(
                "backend_not_configured", "Backend authentication must be configured.", 503
            )
        if not hmac.compare_digest(
            request.headers.get("Authorization", "").encode("utf-8"),
            ("Bearer " + token).encode("utf-8"),
        ):
            raise Failure("not_authorized", "Backend authentication failed.", 401)
        if request.method == "POST":
            now = time.monotonic()
            identity = request.remote_addr or "unknown"
            with arrival_lock:
                history = arrivals.setdefault(identity, deque())
                arrivals.move_to_end(identity)
                while history and history[0] <= now - app.config["RATE_SECONDS"]:
                    history.popleft()
                if len(history) >= app.config["RATE_REQUESTS"]:
                    raise Failure(
                        "request_limit", "Analysis is temporarily rate limited. Please wait.", 429
                    )
                history.append(now)
                while len(arrivals) > 1024:
                    arrivals.popitem(last=False)

    @app.after_request
    def finish(response):
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "X-Request-ID": getattr(g, "trace", ""),
            }
        )
        logging.getLogger("review.http").info(
            json.dumps(
                {
                    "method": request.method,
                    "route": request.path,
                    "status": response.status_code,
                    "ms": round(
                        (time.monotonic() - getattr(g, "started", time.monotonic())) * 1000
                    ),
                }
            )
        )
        return response

    @app.errorhandler(Failure)
    def known(error):
        return jsonify({"error": {"code": error.code, "message": error.message}}), error.status

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(
            {
                "error": {
                    "code": "request_rejected",
                    "message": "The request method, body or route is not supported.",
                }
            }
        ), error.code

    @app.errorhandler(Exception)
    def unknown(error):
        # Never serialize exception text: upstream URLs can contain credentials.
        return jsonify(
            {
                "error": {
                    "code": "internal_error",
                    "message": "The request could not be completed safely.",
                }
            }
        ), 500

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "application": "Review-YT", "contract": "review-yt/v1"})

    @app.get("/api/providers")
    def providers():
        options = []
        for identity in settings.allowed:
            adapter = TextProvider(settings, identity)
            ready, description = adapter.availability()
            if identity == "ollama" and ready:
                try:
                    installed = adapter.discover()
                    ready = any(m.get("name") == adapter.model for m in installed)
                    description = (
                        "Installed local model; no generation performed."
                        if ready
                        else "Configured model is not installed."
                    )
                except Failure:
                    ready, description = False, "Local Ollama is not reachable."
            options.append(
                {
                    "id": identity,
                    "configured": ready,
                    "model": adapter.model,
                    "execution": "local"
                    if identity == "ollama"
                    else "none"
                    if identity == "disabled"
                    else "cloud",
                    "description": description,
                }
            )
        return jsonify(
            {
                "selectionDefault": settings.selected,
                "options": options,
                "constraints": {"paid": settings.paid, "automaticFallback": False},
            }
        )

    @app.post("/api/analyze")
    def analyze():
        if not request.is_json:
            raise Failure("json_required", "Send an application/json request.", 415)
        body = request.get_json()
        if not isinstance(body, dict) or set(body) - {"video", "sample", "provider"}:
            raise Failure("request_shape", "Expected video, sample and provider fields only.", 400)
        video = extract_id(body.get("video"))
        sample = body.get("sample", 10)
        provider = body.get("provider", settings.selected)
        if (
            type(sample) is not int
            or not 1 <= sample <= 500
            or not isinstance(provider, str)
            or provider not in settings.allowed
        ):
            raise Failure("request_shape", "Choose an allowed provider and 1–500 comments.", 400)
        source_key = hashlib.sha256(
            json.dumps([video, sample, engine.captions]).encode()
        ).hexdigest()
        with locks[int(source_key[:6], 16) % len(locks)]:
            cached_source = cache_call("read", "source", source_key)
            if cached_source:
                evidence = Evidence(**cached_source[0])
            else:
                evidence = engine.collect(video, sample)
                cache_call("write", "source", source_key, video, "", evidence.dump(), 600)
            fingerprint = [
                evidence.signature(),
                provider,
                settings.model.get(provider, ""),
                NOTE_REVISION,
                settings.output_limit,
                settings.paid,
            ]
            key = hashlib.sha256(json.dumps(fingerprint).encode()).hexdigest()
            saved = cache_call("read", "review", key)
            if saved:
                return respond_review(saved, True)
            result = engine.review(evidence, provider)
            if result["ai"]["status"] in ("disabled", "complete"):
                expiry = cache_call("write", "review", key, video, provider, result, 1800)
                return respond_review((result, expiry or time.time() + 30), False)
            return respond_review((result, time.time() + 45), False)

    @app.get("/api/results")
    def results():
        video = extract_id(request.args.get("video"))
        provider = request.args.get("provider", settings.selected)
        if provider not in settings.allowed:
            raise Failure("provider_input", "Unknown summary provider.", 400)
        saved = cache_call("latest", video, provider)
        if getattr(g, "cache_unavailable", False):
            raise Failure(
                "cache_unavailable",
                "Saved reviews are temporarily unavailable. Start a new analysis when the service recovers.",
                503,
            )
        if not saved:
            raise Failure("cache_miss", "No saved review is available. Start a new analysis.", 404)
        return respond_review(saved, True)

    return app
