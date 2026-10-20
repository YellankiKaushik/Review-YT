# review-yt-core

A standalone Python toolkit for retrieving actual YouTube comments, applying the VADER lexicon baseline, and requesting optional structured research notes. Flask and Next.js are not dependencies of this package.

Install locally with `pip install ./packages/review_yt_core`. The optional `captions` extra adds public transcript retrieval. Configure process environment variables, then run `review-yt VIDEO_ID --sample 10 --provider disabled`. Missing YouTube credentials fail with a clear message; optional AI never supplies synthetic evidence.

Distribution is blocked pending the workspace provenance/license review. Do not upload this local build to PyPI.
