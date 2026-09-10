'''
Unit tests for modules/updater.py - the version check and the one-button
`git pull`. Two guarantees are worth pinning down, because breaking either one
is silent:

  * the check NEVER raises and NEVER hangs. A user with no internet, behind a
    captive portal, or on a broken DNS must see "no update", not a traceback.
  * a failed `git pull --ff-only` puts the stash back. Leaving a user's edits
    parked in a stash they do not know about is data loss in practice.

No test touches the real network or runs a real git command.

License: MIT  (https://opensource.org/license/mit)
'''

import io
import socket
import subprocess
import urllib.error
import urllib.request

import pytest

from modules import updater


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------
class _Response:
    '''Minimal stand-in for the object urlopen() returns.'''

    def __init__(self, body):
        self._body = body

    def read(self, size=None):
        return self._body[:size] if size else self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _serve(monkeypatch, body=None, error=None, calls=None):
    '''Point urlopen at a canned body or a canned exception.'''
    def fake_urlopen(url, timeout=None):
        if calls is not None:
            calls.append({"url": url, "timeout": timeout})
        if error is not None:
            raise error
        return _Response(body)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)


def _fake_git(monkeypatch, results, calls):
    '''
    Replace subprocess.run with a table lookup on the git subcommand.
    `results` maps subcommand ("remote"/"stash"/"pull") -> (returncode, stdout),
    or -> (0, SomeException) to make that call blow up. Anything missing is a
    clean success. Every invocation is recorded in `calls` as "stash push" etc.
    '''
    def fake_run(argv, **kwargs):
        tail = argv[argv.index("core.autocrlf=false") + 1:]
        calls.append(" ".join(tail[:2]))
        code, out = results.get(tail[0], (0, ""))
        if isinstance(out, BaseException):
            raise out
        return subprocess.CompletedProcess(argv, code, stdout=out, stderr="")
    monkeypatch.setattr(updater.subprocess, "run", fake_run)


# ---------------------------------------------------------------------------
# Version comparison
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("latest, current, expected", [
    ("26.01.20.5.09", "26.01.20.5.08", True),    # newer
    ("26.01.20.5.08", "26.01.20.5.08", False),   # identical - not an update
    ("26.01.20.5.07", "26.01.20.5.08", False),   # older - never offer a downgrade
    ("26.02.01.0.00", "26.01.20.5.08", True),    # leading zeros compare numerically
    ("26.01.20.5.8", "26.01.20.5.08", False),    # 08 == 8, still not an update
    ("26.01.21", "26.01.20.5.08", True),         # shorter but newer
    (None, "26.01.20.5.08", False),              # failed check
    ("not-a-version", "26.01.20.5.08", False),   # garbage
    ("26.01.20.5.09", "", False),                # no local VERSION file
])
def test_is_newer(latest, current, expected):
    assert updater.is_newer(latest, current) is expected


def test_current_version_reads_the_file(monkeypatch, tmp_path):
    version_file = tmp_path / "VERSION"
    version_file.write_text("26.01.20.5.08\n", encoding="utf-8")
    monkeypatch.setattr(updater, "VERSION_FILE", version_file)
    assert updater.current_version() == "26.01.20.5.08"


def test_current_version_missing_file_is_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(updater, "VERSION_FILE", tmp_path / "nope")
    assert updater.current_version() == ""


def test_update_available_is_false_when_the_check_fails(monkeypatch):
    monkeypatch.setattr(updater, "latest_version", lambda: None)
    monkeypatch.setattr(updater, "current_version", lambda: "26.01.20.5.08")
    assert updater.update_available() is False


# ---------------------------------------------------------------------------
# latest_version() must never raise
# ---------------------------------------------------------------------------
def test_latest_version_happy_path(monkeypatch):
    _serve(monkeypatch, body=b"26.01.20.5.09\n")
    assert updater.latest_version() == "26.01.20.5.09"


@pytest.mark.parametrize("error", [
    socket.timeout("timed out"),
    TimeoutError("timed out"),
    urllib.error.HTTPError("u", 404, "Not Found", {}, io.BytesIO(b"")),
    urllib.error.HTTPError("u", 500, "Server Error", {}, io.BytesIO(b"")),
    urllib.error.URLError(socket.gaierror(8, "nodename nor servname provided")),
    ConnectionResetError("connection reset"),
], ids=["timeout", "TimeoutError", "http404", "http500", "dns", "reset"])
def test_latest_version_returns_none_on_network_failure(monkeypatch, error):
    _serve(monkeypatch, error=error)
    assert updater.latest_version() is None


@pytest.mark.parametrize("body", [
    b"<!DOCTYPE html><html><body>Sign in to the wifi</body></html>",   # captive portal
    b"404: Not Found",
    b"",
    b"\xff\xfe\x00garbage",
], ids=["html", "notfound-text", "empty", "binary"])
def test_latest_version_returns_none_on_garbage_body(monkeypatch, body):
    _serve(monkeypatch, body=body)
    assert updater.latest_version() is None


def test_latest_version_enforces_the_timeout(monkeypatch):
    calls = []
    _serve(monkeypatch, body=b"26.01.20.5.09", calls=calls)
    updater.latest_version()
    updater.latest_version(timeout=1)
    assert [c["timeout"] for c in calls] == [5, 1]
    assert calls[0]["url"].startswith("https://raw.githubusercontent.com/")


# ---------------------------------------------------------------------------
# self_update()
# ---------------------------------------------------------------------------
_ORIGIN = "https://github.com/GodsScion/Auto_job_applier_linkedIn.git\n"


def test_self_update_restores_the_stash_when_the_pull_fails(monkeypatch):
    calls = []
    _fake_git(monkeypatch, {
        "remote": (0, _ORIGIN),
        "stash": (0, "Saved working directory"),
        "pull": (1, "fatal: Not possible to fast-forward, aborting."),
    }, calls)

    result = updater.self_update()

    assert result["ok"] is False
    assert "fast-forward" in result["message"]
    assert "git pull" in result["message"]          # told how to update by hand
    assert calls.count("stash push") == 1
    assert calls.count("stash pop") == 1            # edits put straight back


def test_self_update_restores_the_stash_when_git_blows_up(monkeypatch):
    calls = []
    _fake_git(monkeypatch, {
        "remote": (0, _ORIGIN),
        "stash": (0, "Saved working directory"),
        "pull": (0, subprocess.TimeoutExpired("git", 180)),
    }, calls)

    result = updater.self_update()

    assert result["ok"] is False
    assert calls.count("stash pop") == 1             # not left half-stashed


def test_self_update_does_not_stash_when_there_was_nothing_to_stash(monkeypatch):
    calls = []
    _fake_git(monkeypatch, {
        "remote": (0, _ORIGIN),
        "stash": (0, "No local changes to save"),
        "pull": (1, "fatal: refusing to merge unrelated histories"),
    }, calls)

    assert updater.self_update()["ok"] is False
    assert calls.count("stash pop") == 0             # nothing was parked, nothing to pop


def test_self_update_refuses_a_foreign_or_missing_remote(monkeypatch):
    calls = []
    _fake_git(monkeypatch, {"remote": (128, "")}, calls)

    result = updater.self_update()

    assert result["ok"] is False
    assert "not a git clone" in result["message"]
    assert calls == ["remote get-url"]                     # the tree was never touched


def test_self_update_success_clears_the_deps_marker(monkeypatch, tmp_path):
    marker = tmp_path / ".venv" / ".deps_installed"
    marker.parent.mkdir(parents=True)
    marker.write_text("done", encoding="utf-8")
    monkeypatch.setattr(updater, "ROOT", tmp_path)
    calls = []
    _fake_git(monkeypatch, {
        "remote": (0, _ORIGIN),
        "stash": (0, "No local changes to save"),
        "pull": (0, "Updating a1b2c3d..e4f5g6h\nFast-forward\n"),
    }, calls)

    result = updater.self_update()

    assert result["ok"] is True
    assert not marker.exists()                      # start.* reinstalls next launch
    assert calls.count("stash pop") == 0            # never popped over a fresh pull
