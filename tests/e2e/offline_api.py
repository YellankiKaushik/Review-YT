"""Explicit offline CI server. Never imported by the production entry point."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from review_yt_core import Evidence, Failure, Reviewer
from review_yt_core.providers import AIConfig, Generation, TextProvider
from waitress import serve

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps/api"))
import review_api
from review_api.store import Store


class OfflineYouTube:
    def collect(self, video, sample):
        texts = [
            "A superb and useful walkthrough!",
            "Clear and excellent explanation.",
            "I loved these examples.",
            "Really helpful, thank you!",
            "A fantastic lesson!",
            "Uploaded on Monday.",
            "I watched the second half.",
            "This is episode one.",
            "Terrible audio and confusing editing.",
            "I hated this waste of time.",
        ]
        return Evidence(
            {
                "id": video,
                "title": "Offline notebook test video",
                "channel": "Independent CI fixture",
                "published": None,
                "thumbnail": f"https://i.ytimg.com/vi/{video}/hqdefault.jpg",
            },
            texts[:sample],
        )


class OfflineModel:
    def __init__(self, identity):
        self.identity = identity

    def generate(self, *args):
        if self.identity == "openrouter":
            raise Failure("ai_rate_limited", "Offline fixture: free provider is rate limited.", 503)
        return Generation(
            json.dumps(
                {
                    "commentDigest": "Offline fixture: positive and negative feedback are both present.",
                    "captionDigest": "",
                    "creatorNotes": "Offline fixture suggestion: check the sample before acting.",
                }
            ),
            "offline-fixture-gemma",
            {"inputTokens": 30, "outputTokens": 24},
            True,
            8,
        )


class Inventory(TextProvider):
    def discover(self):
        return [{"name": "offline-fixture-gemma"}]


review_api.TextProvider = Inventory
config = AIConfig(
    allowed=("disabled", "ollama", "openrouter"),
    model={"ollama": "offline-fixture-gemma", "openrouter": "offline/free"},
    credentials={"openrouter": "not-a-live-key"},
)
with TemporaryDirectory(prefix="review-yt-offline-") as temp:
    app = review_api.create_application(
        {"API_TOKEN": "e2e-fixture-shared", "AI_CONFIG": config, "RATE_REQUESTS": 500},
        Reviewer(ai=config, youtube=OfflineYouTube(), provider_factory=OfflineModel),
        Store(Path(temp) / "ci.sqlite"),
    )
    serve(app, host="127.0.0.1", port=5101)
