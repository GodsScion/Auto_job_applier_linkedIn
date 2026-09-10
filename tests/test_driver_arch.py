'''
Unit tests for the CPU-architecture / code-signing shim in modules/open_chrome.py.

undetected-chromedriver 3.5.5 has no "mac-arm64" branch in Patcher._set_platform_name(),
so on Apple Silicon it downloads an x86_64 chromedriver and Chrome never launches
("[Errno 86] Bad CPU type in executable"). The shim resolves the driver through Selenium
Manager instead, then re-signs it because UC's cdc_ patch rewrites the binary in place and
macOS Gatekeeper SIGKILLs (-9) a binary whose signature no longer matches.

No browser, no network: everything the shim touches outside the process is stubbed.

License: MIT  (https://opensource.org/license/mit)
'''

import subprocess
import sys
from unittest import mock

import pytest

import undetected_chromedriver as uc
import modules.helpers as helpers
from selenium.webdriver.common.selenium_manager import SeleniumManager


# ---------------------------------------------------------------------------
# modules/open_chrome.py opens a real browser at import time. Stub the four things
# that reach outside the process, import it once, then every test works on the real
# module. binary_paths raising also makes the import exercise the fallback path.
# ---------------------------------------------------------------------------
_chrome_kwargs = []


class _FakeChrome:
    def __init__(self, **kwargs):
        _chrome_kwargs.append(kwargs)

    def maximize_window(self):
        pass


with mock.patch.object(uc, "Chrome", _FakeChrome), \
     mock.patch.object(helpers, "make_directories", lambda paths: None), \
     mock.patch.object(helpers, "get_default_temp_profile", lambda: "/tmp/not-a-real-profile"), \
     mock.patch.object(SeleniumManager, "binary_paths", side_effect=OSError("no selenium manager")):
    import modules.open_chrome as oc


def test_import_time_launch_fell_back_to_ucs_own_download():
    '''With Selenium Manager broken, the launch must still happen the old way.'''
    assert _chrome_kwargs, "modules.open_chrome never constructed a driver"
    assert "driver_executable_path" not in _chrome_kwargs[0]


def test_selenium_manager_failure_returns_none(monkeypatch):
    '''Anything Selenium Manager throws means "fall back", never "crash".'''
    monkeypatch.setattr(SeleniumManager, "binary_paths", mock.Mock(side_effect=OSError("boom")))
    assert oc.get_managed_driver_path() is None


def test_selenium_manager_returning_junk_returns_none(monkeypatch):
    '''A result without driver_path is a KeyError, and that is still a fallback.'''
    monkeypatch.setattr(SeleniumManager, "binary_paths", mock.Mock(return_value={"code": 1}))
    assert oc.get_managed_driver_path() is None


@pytest.mark.parametrize("platform", ["win32", "linux", "linux2"])
def test_non_darwin_never_shells_out_to_codesign(monkeypatch, platform):
    monkeypatch.setattr(sys, "platform", platform)
    run = mock.Mock()
    monkeypatch.setattr(oc.subprocess, "run", run)
    oc._adhoc_sign("/some/chromedriver")
    run.assert_not_called()


@pytest.mark.parametrize("boom", [
    FileNotFoundError("codesign"),                                  # no Xcode command line tools
    subprocess.CalledProcessError(1, "codesign"),                   # signing itself failed
])
def test_codesign_failure_is_logged_not_raised(monkeypatch, boom, log_records):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(oc.subprocess, "run", mock.Mock(side_effect=boom))
    oc._adhoc_sign("/some/chromedriver")                            # must not raise
    assert any("-9" in r.getMessage() for r in log_records), log_records


def test_patch_happens_before_signing_and_never_on_the_selenium_cache(monkeypatch, tmp_path):
    '''The whole point of the ordering: UC's patch invalidates the signature, so
    copy -> patch -> sign -> hand to uc.Chrome(). Signing first would be undone.'''
    order = []
    cached = str(tmp_path / "selenium-cache" / "chromedriver")

    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(SeleniumManager, "binary_paths", mock.Mock(return_value={"driver_path": cached}))
    monkeypatch.setattr(oc.shutil, "copy2", lambda s, d: order.append(("copy", s, d)))
    monkeypatch.setattr(oc.subprocess, "run", lambda cmd, **kw: order.append(("codesign", cmd[-1])))

    class _FakePatcher:
        data_path = str(tmp_path / "app-dir")

        def __init__(self, executable_path=None, **kw):
            self.executable_path = executable_path

        def auto(self):
            order.append(("patch", self.executable_path))

    monkeypatch.setattr(oc.uc, "Patcher", _FakePatcher)

    path = oc.get_managed_driver_path()

    assert [step[0] for step in order] == ["copy", "patch", "codesign"]
    assert order[0][1] == cached and order[0][2] == path         # copied OUT of the shared cache
    assert order[1][1] == path and order[2][1] == path           # patched and signed our copy only
    assert cached not in (order[1][1], order[2][1])              # the shared cache is never patched
