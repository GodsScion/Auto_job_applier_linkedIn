"""Browser smoke tests for this application's local-only import flow."""

import json
import threading
from pathlib import Path

import pytest


def test_playwright_imports_strict_json_into_editable_review(tmp_path, monkeypatch):
    playwright_sync = pytest.importorskip("playwright.sync_api")
    from werkzeug.serving import make_server
    import app
    import config._overrides as overrides

    config_path = str(tmp_path / "user_config.json")
    monkeypatch.setattr(app, "USER_CONFIG_PATH", config_path)
    monkeypatch.setattr(overrides, "USER_CONFIG_PATH", config_path)

    source = tmp_path / "candidate.json"
    source.write_text(json.dumps({
        "personals": {"first_name": "Ada", "last_name": "Lovelace"},
        "questions": {"years_of_experience": "5"},
    }), encoding="utf-8")

    server = make_server("127.0.0.1", 0, app.app, threaded=True)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    try:
        with playwright_sync.sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(headless=True)
            except Exception as exc:
                pytest.skip(f"Playwright Chromium is unavailable: {exc}")
            try:
                page = browser.new_page()
                page.goto(f"http://127.0.0.1:{server.server_port}/import-profile")
                page.locator("#profileFile").set_input_files(str(source))
                page.get_by_role("button", name="Parse for review").click()
                assert page.get_by_label("First name").input_value() == "Ada"
                assert page.get_by_label("Last name").input_value() == "Lovelace"
                assert page.get_by_text("fields not found are left unchanged").is_visible()
                assert page.locator("#review").is_visible()
                assert not Path(config_path).exists()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server_thread.join(timeout=2)
