"""Optional Playwright recorder/replayer for the local draft page."""

from __future__ import annotations

import argparse
import runpy
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit


def is_local_draft_url(value: str) -> bool:
    """Allow recorder startup only on this app's localhost draft route."""
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme == "http"
            and parsed.hostname in {"127.0.0.1", "localhost"}
            and parsed.port is not None
            and parsed.path.rstrip("/") == "/draft-application"
            and not parsed.username
            and not parsed.password
            and not parsed.query
            and not parsed.fragment
        )
    except ValueError:
        return False


def is_http_url(value: str) -> bool:
    """Allow a user-supplied web page URL for a visible, manual browser session."""
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)
    record = subparsers.add_parser("record", help="record the local draft-page workflow")
    record.add_argument("url", help="local panel URL ending in /draft-application")
    assist = subparsers.add_parser("assist", help="open a job page in a visible browser for manual use")
    assist.add_argument("url", help="http(s) job page URL")
    play = subparsers.add_parser("play", help="replay a reviewed local recording")
    play.add_argument("recording", nargs="?", default="work/playwright-recording.py")
    args = parser.parse_args(argv)

    if args.mode == "record":
        if not is_local_draft_url(args.url):
            parser.error("recording is restricted to http://localhost:PORT/draft-application")
        output = Path("work/playwright-recording.py")
        output.parent.mkdir(parents=True, exist_ok=True)
        print(f"Recording local draft-page interactions to {output}")
        return subprocess.call([
            sys.executable, "-m", "playwright", "codegen", "--target", "python",
            "--output", str(output), args.url,
        ])

    if args.mode == "assist":
        if not is_http_url(args.url):
            parser.error("assist requires an http(s) URL without embedded credentials")
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            parser.error("install Playwright and Chromium first (see README.md)")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(args.url, wait_until="domcontentloaded")
            print("Browser is under your control. The helper will not interact with or submit the page.")
            browser.wait_for_event("disconnected")
        return 0

    recording = Path(args.recording)
    if not recording.is_file():
        parser.error(f"recording not found: {recording}")
    print(f"Replaying {recording}. Review the script before running it.")
    runpy.run_path(str(recording), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
