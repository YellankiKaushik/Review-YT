import logging
import os

from review_api import create_application
from waitress import serve

logging.basicConfig(level=logging.WARNING, format="%(message)s")
logging.getLogger("review.http").setLevel(logging.INFO)
application = create_application()
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
