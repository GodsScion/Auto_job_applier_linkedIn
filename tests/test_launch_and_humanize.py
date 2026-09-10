'''
Unit tests for the Chrome launch path and the human-paced typing helpers.

Covers the Windows "--user-data-dir=--user-data-dir=..." launch failure, the
per-character typing added to the text inputs, and the visible-element picker that
skips LinkedIn's hidden 0x0 duplicate nodes.

License: MIT  (https://opensource.org/license/mit)
'''

import pathlib
import sys

import pytest

from modules.helpers import get_default_temp_profile, human_type
from modules.clickers_and_finders import pick_first_displayed, text_xpath, try_xp


# ---------------------------- get_default_temp_profile ---------------------
@pytest.fixture
def fake_home(monkeypatch, tmp_path):
    '''Point Path.home() at a temp dir and stop mkdir from touching the real disk.'''
    monkeypatch.setattr(pathlib.Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setattr(pathlib.Path, "mkdir", lambda self, **kwargs: None)
    return tmp_path


@pytest.mark.parametrize("platform", ["win32", "linux", "darwin"])
def test_temp_profile_is_a_bare_path_on_every_platform(monkeypatch, fake_home, platform):
    monkeypatch.setattr(sys, "platform", platform)
    path = get_default_temp_profile()
    # The callers add "--user-data-dir=" themselves, baking it in here doubled the flag.
    assert "--user-data-dir" not in path
    assert not path.startswith("-")
    assert "auto-job-apply-profile" in path


def test_temp_profile_is_usable_as_a_chrome_flag(monkeypatch, fake_home):
    monkeypatch.setattr(sys, "platform", "win32")
    assert f"--user-data-dir={get_default_temp_profile()}" == "--user-data-dir=C:\\temp\\auto-job-apply-profile"


def test_temp_profile_directory_gets_created(monkeypatch, tmp_path):
    monkeypatch.setattr(pathlib.Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setattr(sys, "platform", "linux")        # so the path stays inside tmp_path
    path = pathlib.Path(get_default_temp_profile())
    assert path.is_dir()                                 # a missing folder is its own Chrome error


def test_temp_profile_survives_an_uncreatable_directory(monkeypatch, fake_home):
    monkeypatch.setattr(sys, "platform", "linux")
    def boom(self, **kwargs): raise PermissionError("read-only file system")
    monkeypatch.setattr(pathlib.Path, "mkdir", boom)
    assert get_default_temp_profile()                    # must not raise, Chrome reports it instead


# ---------------------------------- human_type -----------------------------
class FakeElement:
    '''Records every send_keys call, like a Selenium WebElement without a browser.'''
    def __init__(self):
        self.keys = []
    def send_keys(self, value):
        self.keys.append(value)


class FakeActions(FakeElement):
    '''An ActionChains stand-in: has perform(), which must be called per character.'''
    def __init__(self):
        super().__init__()
        self.performs = 0
    def perform(self):
        self.performs += 1


@pytest.fixture
def slept(monkeypatch):
    '''Collects every sleep duration human_type asks for, without actually sleeping.'''
    durations = []
    monkeypatch.setattr("modules.helpers.sleep", durations.append)
    return durations


def test_human_type_sends_every_character_in_order(slept):
    element = FakeElement()
    human_type(element, "Hello World")
    assert element.keys == list("Hello World")
    assert "".join(element.keys) == "Hello World"


def test_human_type_waits_between_every_keystroke(slept):
    text = "a cover letter"
    human_type(FakeElement(), text)
    # One delay per character at minimum (plus the occasional longer "think" pause).
    assert len(slept) >= len(text)
    assert all(0.04 <= d <= 1.0 for d in slept)


def test_human_type_is_slower_than_a_one_shot_send_keys(slept):
    text = "This is roughly a sentence of an answer."
    one_shot = FakeElement()
    one_shot.send_keys(text)                             # what the code used to do
    assert slept == []                                   # a single send_keys costs no time

    human_type(FakeElement(), text)
    assert sum(slept) >= len(text) * 0.04                # ~40ms per key floor


def test_human_type_performs_once_per_character_for_actionchains(slept):
    actions = FakeActions()
    human_type(actions, "abcd")
    assert actions.keys == ["a", "b", "c", "d"]          # never the whole string at once
    assert actions.performs == 4                         # perform() empties the queue each time


def test_human_type_ignores_empty_and_none(slept):
    element = FakeElement()
    human_type(element, "")
    human_type(element, None)
    assert element.keys == []
    assert slept == []


# ------------------------------ pick_first_displayed -----------------------
class FakeNode:
    def __init__(self, displayed=True, stale=False):
        self._displayed, self._stale = displayed, stale
    def is_displayed(self):
        if self._stale:
            from selenium.common.exceptions import StaleElementReferenceException
            raise StaleElementReferenceException("gone")
        return self._displayed


def test_pick_first_displayed_skips_hidden_duplicates():
    hidden, visible = FakeNode(displayed=False), FakeNode(displayed=True)
    # LinkedIn renders the hidden 0x0 copy first, find_element would return that one.
    assert pick_first_displayed([hidden, visible]) is visible


def test_pick_first_displayed_skips_stale_elements():
    visible = FakeNode(displayed=True)
    assert pick_first_displayed([FakeNode(stale=True), visible]) is visible


def test_pick_first_displayed_returns_none_when_all_hidden():
    assert pick_first_displayed([FakeNode(displayed=False), FakeNode(displayed=False)]) is None
    assert pick_first_displayed([]) is None


# --------------------------------- text_xpath ------------------------------
def test_text_xpath_matches_case_and_space_insensitively():
    xpath = text_xpath("span", "  Easy Apply ")
    assert '"easy apply"' in xpath                       # lowercased and stripped
    assert "normalize-space" in xpath and "contains" in xpath
    assert xpath.startswith(".//span[")


# ----------------------------------- try_xp --------------------------------
class FakeDriver:
    def __init__(self, element=None, error=None):
        self.element, self.error = element, error
    def find_element(self, by, value):
        if self.error: raise self.error
        return self.element


class FakeClickable:
    def __init__(self): self.clicked = False
    def click(self): self.clicked = True


def test_try_xp_pauses_after_clicking(monkeypatch):
    waited = []
    monkeypatch.setattr("modules.clickers_and_finders.buffer", waited.append)
    element = FakeClickable()
    assert try_xp(FakeDriver(element), "//button") is True
    assert element.clicked
    assert waited, "clicks must go through buffer(), gapless clicking is what gets flagged"


def test_try_xp_is_quiet_when_the_element_is_simply_absent(monkeypatch):
    from selenium.common.exceptions import NoSuchElementException
    logged = []
    monkeypatch.setattr("modules.clickers_and_finders.print_lg", lambda *a, **k: logged.append(a))
    assert try_xp(FakeDriver(error=NoSuchElementException("nope")), "//button") is False
    assert logged == []


def test_try_xp_reports_unexpected_failures(monkeypatch):
    from selenium.common.exceptions import ElementClickInterceptedException
    logged = []
    monkeypatch.setattr("modules.clickers_and_finders.print_lg", lambda *a, **k: logged.append(a))
    assert try_xp(FakeDriver(error=ElementClickInterceptedException("covered")), "//button") is False
    assert logged, "an intercepted click must not look the same as a missing element"
