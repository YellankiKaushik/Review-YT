import logging
import os

from dotenv import load_dotenv
from review_api import ROOT, create_application
from waitress import serve

logging.basicConfig(level=logging.WARNING, format="%(message)s")
logging.getLogger("review.http").setLevel(logging.INFO)


def configured_application():
    load_dotenv(ROOT / ".env", override=False)
    # A public listener must not look ready while its required backend settings
    # are absent. The message identifies names only, never configured values.
    if os.getenv("HOST", "127.0.0.1") not in ("127.0.0.1", "localhost", "::1"):
        missing = [name for name in ("YOUTUBE_API_KEY", "BACKEND_API_TOKEN") if not os.getenv(name)]
        if missing:
            raise RuntimeError("Public backend requires: " + ", ".join(missing))
    return create_application()


application = configured_application()
if __name__ == "__main__":
    serve(
        application,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5100")),
        threads=4,
        channel_timeout=100,
        max_request_body_size=4096,
        expose_tracebacks=False,
    )
