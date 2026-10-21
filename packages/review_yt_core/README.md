# review-yt-core

A standalone Python toolkit for retrieving actual YouTube comments, applying the VADER lexicon baseline, and requesting optional structured research notes. Flask and Next.js are not dependencies of this package.

Install locally with `pip install ./packages/review_yt_core`. The optional `captions` extra adds public transcript retrieval. Configure process environment variables, then run `review-yt VIDEO_ID --sample 10 --provider disabled`. Missing YouTube credentials fail with a clear message; optional AI never supplies synthetic evidence.

Eligible new package material is MIT-licensed; see LICENSE and NOTICE for scope. Third-party dependencies retain their own rights and notices. The maintainer has authorized source publication to the existing Review-YT GitHub repository. No PyPI or npm publication is part of this release.
