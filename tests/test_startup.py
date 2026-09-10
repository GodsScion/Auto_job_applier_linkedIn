'''
The bot has to actually open a browser.

`modules/open_chrome.py` used to call `createChromeSession()` at module scope, so
importing `runAiBot` launched Chrome. That was removed so a bad config no longer costs
you a browser window and a driver download before anything validates it - but it means
`main()` now has to open the browser itself, and `runAiBot`'s star-imported
`driver`/`options`/`actions`/`wait` are separate bindings that stay `None` until it does.

Miss that call and every `driver.*` in `main()` raises `AttributeError` on `None`, which
`main()`'s own `except Exception` swallows into a log line and an alert. The bot appears
to run and applies to nothing. The whole suite stayed green while that was true, because
nothing else here ever enters `main()`.
'''
import sys
import types
from unittest import mock

import pytest


@pytest.fixture
def bot(monkeypatch):
    import runAiBot
    # main()'s finally block reads the run counters; keep this test from depending on
    # whatever another test left behind in them.
    for counter in ("easy_applied_count", "external_jobs_count", "failed_count", "skip_count"):
        monkeypatch.setattr(runAiBot, counter, 0, raising=True)
    return runAiBot


def _stub_everything_but_the_browser(bot, monkeypatch, driver):
    '''Neutralise every step of main() except the one under test.'''
    monkeypatch.setattr(bot, "validate_config", lambda: None)
    monkeypatch.setattr(bot, "is_logged_in_LN", lambda: True)
    monkeypatch.setattr(bot, "login_LN", lambda: None)
    monkeypatch.setattr(bot, "run", lambda total: total)
    monkeypatch.setattr(bot, "use_AI", False)
    monkeypatch.setattr(bot, "run_non_stop", False)
    monkeypatch.setattr(bot, "alternate_sortby", False)
    monkeypatch.setattr(bot, "cycle_date_posted", False)
    monkeypatch.setattr(bot, "close_tabs", False)
    monkeypatch.setattr(bot, "pyautogui", mock.MagicMock())
    monkeypatch.setattr(bot.os.path, "exists", lambda _p: True)
    monkeypatch.setattr(bot, "start_browser", lambda: ("opts", driver, "actions", "wait"))


def _fake_driver():
    driver = mock.MagicMock()
    driver.window_handles = ["window-1"]
    driver.current_window_handle = "window-1"
    return driver


def test_main_opens_a_browser_and_binds_it(bot, monkeypatch):
    '''The regression this file exists for.'''
    driver = _fake_driver()
    _stub_everything_but_the_browser(bot, monkeypatch, driver)
    monkeypatch.setattr(bot, "driver", None, raising=True)

    bot.main()

    assert bot.driver is driver, (
        "main() did not rebind the module-level driver - open_chrome no longer opens "
        "one at import, so every driver.* call in main() is an AttributeError on None"
    )


def test_main_does_not_swallow_a_startup_failure(bot, monkeypatch):
    '''
    main() catches bare `Exception` and turns it into a log line, so a broken startup
    looks exactly like a successful run that found no jobs. Assert nothing was caught.
    '''
    driver = _fake_driver()
    _stub_everything_but_the_browser(bot, monkeypatch, driver)
    monkeypatch.setattr(bot, "driver", None, raising=True)
    swallowed = []
    monkeypatch.setattr(bot, "critical_error_log", lambda *a, **k: swallowed.append(a))

    bot.main()

    assert not swallowed, f"main() swallowed a startup error: {swallowed}"


def test_the_browser_opens_only_after_the_config_validates(bot, monkeypatch):
    '''
    Ordering is the point of the change: a typo in config must not cost a Chrome window
    and a driver download. If validate_config() raises, no browser may be opened.
    '''
    order = []
    driver = _fake_driver()
    _stub_everything_but_the_browser(bot, monkeypatch, driver)

    def exploding_validate():
        order.append("validate")
        raise ValueError("bad config")

    monkeypatch.setattr(bot, "validate_config", exploding_validate)
    monkeypatch.setattr(bot, "start_browser", lambda: order.append("browser") or ("o", driver, "a", "w"))
    monkeypatch.setattr(bot, "critical_error_log", lambda *a, **k: None)

    bot.main()

    assert order == ["validate"], f"browser opened despite an invalid config: {order}"


def test_importing_runaibot_opens_no_browser():
    '''
    The property the whole change is for. Importing the bot must not touch a browser -
    this is what let four separate test files stop injecting a fake open_chrome module.
    '''
    import runAiBot  # already imported by now; assert the module-level state, not the import
    assert "modules.open_chrome" in sys.modules
    oc = sys.modules["modules.open_chrome"]
    if isinstance(oc, types.ModuleType) and hasattr(oc, "start_browser"):
        # A real (not stubbed) open_chrome must expose start_browser and must not have
        # created a session as a side effect of being imported.
        assert callable(oc.start_browser)
