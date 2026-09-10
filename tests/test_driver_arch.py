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

import os
import subprocess
import sys
from unittest import mock

import pytest

import undetected_chromedriver as uc
from selenium.webdriver.common.selenium_manager import SeleniumManager

import modules.open_chrome as oc          # importing this must NOT open a browser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _FakeChrome:
    def __init__(self, **kwargs):
        _chrome_kwargs.append(kwargs)

    def maximize_window(self):
        pass


_chrome_kwargs = []


def test_importing_the_module_starts_nothing(tmp_path):
    '''The launch used to run at module scope, so `import runAiBot` opened Chrome.
    A real check, not a mock: import it in a clean interpreter in an empty folder and
    see that nothing createChromeSession() makes ever appears.'''
    probe = ("import modules.open_chrome as oc\n"
             "assert (oc.options, oc.driver, oc.actions, oc.wait) == (None, None, None, None)\n")
    done = subprocess.run([sys.executable, "-c", probe], cwd=tmp_path, capture_output=True,
                          text=True, timeout=300, env=dict(os.environ, PYTHONPATH=ROOT))
    assert done.returncode == 0, done.stderr
    # Only createChromeSession() makes these, and a driver download would land under ~/.
    for evidence_of_a_launch in ("all excels", "all resumes", "logs/screenshots"):
        assert not (tmp_path / evidence_of_a_launch).exists(), evidence_of_a_launch


def test_launch_falls_back_to_ucs_own_download(monkeypatch):
    '''With Selenium Manager broken, the launch must still happen the old way.'''
    _chrome_kwargs.clear()
    monkeypatch.setattr(oc.uc, "Chrome", _FakeChrome)
    monkeypatch.setattr(oc, "make_directories", lambda paths: None)
    monkeypatch.setattr(oc, "get_default_temp_profile", lambda: "/tmp/not-a-real-profile")
    monkeypatch.setattr(SeleniumManager, "binary_paths", mock.Mock(side_effect=OSError("no selenium manager")))

    assert oc.start_browser()[1] is oc.driver          # returns what it publishes
    assert _chrome_kwargs, "start_browser() never constructed a driver"
    assert "driver_executable_path" not in _chrome_kwargs[0]
    monkeypatch.setattr(oc, "driver", None)            # leave the module as we found it


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
