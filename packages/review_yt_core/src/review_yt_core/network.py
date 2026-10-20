import json
import time

import httpx

from .domain import Failure


def exchange(
    method,
    url,
    *,
    headers=None,
    params=None,
    payload=None,
    timeout=12,
    client=None,
    maximum=4000000,
):
    owned = client is None
    session = client or httpx.Client(trust_env=False, follow_redirects=False)
    deadline = time.monotonic() + timeout
    try:
        with session.stream(
            method,
            url,
            headers=headers,
            params=params,
            json=payload,
            timeout=timeout,
            follow_redirects=False,
        ) as response:
            parts, size = [], 0
            for part in response.iter_bytes():
                size += len(part)
                if size > maximum or time.monotonic() > deadline:
                    raise Failure(
                        "upstream_limit", "The upstream response exceeded its safety budget."
                    )
                parts.append(part)
            try:
                data = json.loads(b"".join(parts))
                if not isinstance(data, dict):
                    raise ValueError()
            except (ValueError, UnicodeError):
                raise Failure(
                    "upstream_format", "The upstream service returned an unreadable response."
                ) from None
            return response.status_code, data
    except httpx.TimeoutException:
        raise Failure("upstream_timeout", "The upstream service timed out.", 504) from None
    except httpx.HTTPError:
        raise Failure(
            "upstream_connection", "The upstream service could not be contacted."
        ) from None
    finally:
        if owned:
            session.close()
