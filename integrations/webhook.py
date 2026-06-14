#!/usr/bin/env python3
"""Minimal, dependency-free webhook forwarder for Cognis findings.

Reads JSON findings on stdin and POSTs them to a URL (SIEM/Slack/Jira bridge).
Usage:  <tool> scan . --format json | python integrations/webhook.py --url URL
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


def _die(msg: str, code: int = 2) -> int:
    """Print *msg* to stderr and return *code*."""
    print(f"error: {msg}", file=sys.stderr)
    return code


def _validate_url(url: str) -> str | None:
    """Return None if *url* is acceptable, otherwise an error string."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as exc:  # pragma: no cover
        return str(exc)
    if parsed.scheme not in ("http", "https"):
        return f"URL scheme must be http or https, got {parsed.scheme!r}"
    if not parsed.netloc:
        return "URL is missing a host"
    return None


def _parse_headers(raw: list[str]) -> dict[str, str] | str:
    """Parse ``Key: Value`` header strings.

    Returns a dict on success, or an error message string on failure.
    """
    headers: dict[str, str] = {}
    for h in raw:
        if ":" not in h:
            return (
                f"header {h!r} is not in 'Key: Value' format (missing ':')"
            )
        k, _, v = h.partition(":")
        k = k.strip()
        v = v.strip()
        if not k:
            return f"header {h!r} has an empty key"
        headers[k] = v
    return headers


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Forward JSON findings to a webhook endpoint."
    )
    ap.add_argument("--url", required=True, help="Destination URL (http/https)")
    ap.add_argument(
        "--header",
        action="append",
        default=[],
        help="Extra header in 'Key: Value' format (repeatable)",
    )
    ap.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        metavar="SECONDS",
        help="HTTP request timeout in seconds (default: 15)",
    )

    args = ap.parse_args(argv)

    # --- validate URL ---
    url_err = _validate_url(args.url)
    if url_err:
        return _die(f"invalid --url: {url_err}")

    # --- validate timeout ---
    if args.timeout <= 0:
        return _die("--timeout must be a positive number")

    # --- validate / parse headers ---
    headers_result = _parse_headers(args.header)
    if isinstance(headers_result, str):
        return _die(f"invalid --header: {headers_result}")
    extra_headers: dict[str, str] = headers_result

    # --- read + validate stdin JSON ---
    raw = sys.stdin.read()
    if not raw.strip():
        return _die("no input received on stdin (expected JSON)")
    try:
        json.loads(raw)  # validate; we still POST the original bytes
    except json.JSONDecodeError as exc:
        return _die(f"stdin is not valid JSON: {exc}")

    payload = raw.encode("utf-8")

    # --- build request ---
    req = urllib.request.Request(args.url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in extra_headers.items():
        req.add_header(k, v)

    # --- send ---
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as r:
            print(f"posted {len(payload)} bytes -> {r.status}")
        return 0
    except urllib.error.HTTPError as exc:
        return _die(f"HTTP {exc.code} from server: {exc.reason}", code=1)
    except urllib.error.URLError as exc:
        return _die(f"network error: {exc.reason}", code=1)
    except OSError as exc:
        return _die(f"connection error: {exc}", code=1)


if __name__ == "__main__":
    sys.exit(main())
