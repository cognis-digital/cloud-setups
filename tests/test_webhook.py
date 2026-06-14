"""Tests for integrations/webhook.py hardening — edge cases and error paths."""
from __future__ import annotations

import io
import sys
import unittest.mock as mock


# Allow importing from the integrations package without installing
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from integrations.webhook import _parse_headers, _validate_url, main


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

class TestValidateUrl:
    def test_valid_https(self):
        assert _validate_url("https://example.com/hook") is None

    def test_valid_http(self):
        assert _validate_url("http://localhost:9000/events") is None

    def test_rejects_ftp(self):
        err = _validate_url("ftp://example.com/")
        assert err is not None
        assert "http" in err.lower() or "scheme" in err.lower()

    def test_rejects_missing_host(self):
        err = _validate_url("https://")
        assert err is not None

    def test_rejects_empty_string(self):
        err = _validate_url("")
        assert err is not None


class TestParseHeaders:
    def test_single_header(self):
        result = _parse_headers(["Authorization: Bearer tok"])
        assert result == {"Authorization": "Bearer tok"}

    def test_multiple_headers(self):
        result = _parse_headers(["X-A: 1", "X-B: 2"])
        assert result == {"X-A": "1", "X-B": "2"}

    def test_empty_list(self):
        assert _parse_headers([]) == {}

    def test_missing_colon_returns_error(self):
        result = _parse_headers(["BadHeader"])
        assert isinstance(result, str)

    def test_value_with_colon_preserved(self):
        """A value that contains ':' should not be split further."""
        result = _parse_headers(["X-Ts: 2026-06-14T12:00:00Z"])
        assert isinstance(result, dict)
        assert result["X-Ts"] == "2026-06-14T12:00:00Z"

    def test_empty_key_returns_error(self):
        result = _parse_headers([": value"])
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Integration-style tests for main() using monkeypatching
# ---------------------------------------------------------------------------

def _run_main(args, stdin_text):
    """Run main() with stdin replaced by *stdin_text*, return exit code."""
    with mock.patch("sys.stdin", io.StringIO(stdin_text)):
        return main(args)


class TestMainValidation:
    def test_empty_stdin_returns_error(self, capsys):
        code = _run_main(["--url", "https://example.com/hook"], "")
        assert code != 0
        captured = capsys.readouterr()
        assert "stdin" in captured.err.lower() or "input" in captured.err.lower()

    def test_whitespace_only_stdin_returns_error(self, capsys):
        code = _run_main(["--url", "https://example.com/hook"], "   \n  ")
        assert code != 0
        captured = capsys.readouterr()
        assert captured.err.strip() != ""

    def test_malformed_json_returns_error(self, capsys):
        code = _run_main(["--url", "https://example.com/hook"], "{not json}")
        assert code != 0
        captured = capsys.readouterr()
        assert "json" in captured.err.lower()

    def test_bad_url_scheme_returns_error(self, capsys):
        code = _run_main(["--url", "ftp://evil.com/"], '{"a":1}')
        assert code != 0
        captured = capsys.readouterr()
        assert "url" in captured.err.lower() or "scheme" in captured.err.lower()

    def test_bad_header_format_returns_error(self, capsys):
        code = _run_main(
            ["--url", "https://example.com/hook", "--header", "BadHeader"],
            '{"a":1}',
        )
        assert code != 0
        captured = capsys.readouterr()
        assert "header" in captured.err.lower()

    def test_invalid_timeout_returns_error(self, capsys):
        code = _run_main(
            ["--url", "https://example.com/hook", "--timeout", "-5"],
            '{"a":1}',
        )
        assert code != 0
        captured = capsys.readouterr()
        assert "timeout" in captured.err.lower()

    def test_http_error_returns_nonzero(self, capsys):
        """A 4xx/5xx from the server should exit non-zero with a clear message."""
        import urllib.error

        http_err = urllib.error.HTTPError(
            url="https://example.com/hook",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=None,
        )
        with mock.patch("urllib.request.urlopen", side_effect=http_err):
            code = _run_main(
                ["--url", "https://example.com/hook"],
                '{"findings": []}',
            )
        assert code != 0
        captured = capsys.readouterr()
        assert "403" in captured.err

    def test_network_error_returns_nonzero(self, capsys):
        """A connection failure should exit non-zero with a clear message."""
        import urllib.error

        net_err = urllib.error.URLError(reason="Name or service not known")
        with mock.patch("urllib.request.urlopen", side_effect=net_err):
            code = _run_main(
                ["--url", "https://example.com/hook"],
                '{"findings": []}',
            )
        assert code != 0
        captured = capsys.readouterr()
        assert "network" in captured.err.lower() or "error" in captured.err.lower()

    def test_success_posts_and_returns_zero(self, capsys):
        """Valid JSON + reachable URL should return 0 and print confirmation."""
        fake_response = mock.MagicMock()
        fake_response.status = 200
        fake_response.__enter__ = lambda s: s
        fake_response.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("urllib.request.urlopen", return_value=fake_response):
            code = _run_main(
                ["--url", "https://example.com/hook"],
                '{"findings": [{"id": 1}]}',
            )
        assert code == 0
        captured = capsys.readouterr()
        assert "posted" in captured.out.lower()
