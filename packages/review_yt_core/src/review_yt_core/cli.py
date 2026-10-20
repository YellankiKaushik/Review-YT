import argparse
import json
import os

from .domain import Failure
from .engine import Reviewer
from .providers import AIConfig
from .youtube import extract_id


def main():
    parser = argparse.ArgumentParser(
        description="Analyze actual YouTube comments; credentials come from the process environment."
    )
    parser.add_argument("video")
    parser.add_argument("--sample", type=int, default=10)
    parser.add_argument("--provider", default=None)
    args = parser.parse_args()
    try:
        config = AIConfig.read(os.environ)
        engine = Reviewer(os.getenv("YOUTUBE_API_KEY", ""), config)
        result = engine.review(
            engine.collect(extract_id(args.video), args.sample), args.provider or config.selected
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (Failure, ValueError) as error:
        parser.exit(
            1, (error.message if isinstance(error, Failure) else "Configuration is invalid.") + "\n"
        )
