'''
Regression tests for the runAiBot.py fixes. Selenium can't drive a real browser here,
so the browser session is stubbed out at import time and the DOM is faked with small
objects that answer find_element / find_elements.

Each test fails if the specific bug it covers comes back.

License: MIT  (https://opensource.org/license/mit)
'''

import os
import sys
import types

import pytest
from selenium.common.exceptions import NoSuchElementException


@pytest.fixture(scope="module")
def bot():
    '''Import runAiBot with a stubbed browser session, so importing it never opens Chrome.'''
    fake_chrome = types.ModuleType("modules.open_chrome")
    fake_chrome.options = fake_chrome.driver = fake_chrome.actions = fake_chrome.wait = None
    sys.modules["modules.open_chrome"] = fake_chrome
    import runAiBot
    return runAiBot


class FakeElement:
    '''Stand-in for a WebElement: `children` maps an XPath/class to what it resolves to.'''

    def __init__(self, text="", value="", children=None):
        self.text = text
        self.value = value
        self.children = children or {}
        self.cleared = False

    def clear(self):
        self.cleared = True
        self.value = ""

    def send_keys(self, keys):
        self.value += str(keys)

    def get_attribute(self, name):
        return self.value if name == "value" else None

    def is_selected(self):
        return False

    def find_element(self, by, locator):
        if locator in self.children:
            return self.children[locator]
        raise NoSuchElementException(locator)

    def find_elements(self, by, locator):
        found = self.children.get(locator)
        if isinstance(found, list):
            return found
        return [found] if found else []


# --------------------------- A: the do_actions UnboundLocalError -------------------
def test_textarea_question_without_an_earlier_text_input(bot, monkeypatch):
    '''A cover-letter textarea used to read do_actions, which only the text branch set.'''
    typed = []
    monkeypatch.setattr(bot, "human_type", lambda target, text: typed.append((target, text)), raising=False)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)

    textarea = FakeElement()
    question = FakeElement(children={
        ".//textarea": textarea,
        ".//label[@for]": FakeElement(text="Cover letter"),
    })
    modal = FakeElement(children={".//div[@data-test-form-element]": [question]})

    answered = bot.answer_questions(modal, set(), "Remote")   # used to raise UnboundLocalError

    assert len(answered) == 1
    assert textarea.cleared
    assert typed and typed[0][0] is textarea       # L: typed through human_type, not send_keys


def test_text_question_is_typed_through_human_type(bot, monkeypatch):
    typed = []
    monkeypatch.setattr(bot, "human_type", lambda target, text: typed.append((target, text)), raising=False)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)

    text_input = FakeElement()
    question = FakeElement(children={
        ".//input[@type='text']": text_input,
        ".//label[@for]": FakeElement(text="First name"),
    })
    modal = FakeElement(children={".//div[@data-test-form-element]": [question]})

    bot.answer_questions(modal, set(), "Remote")

    assert typed == [(text_input, bot.first_name)]


# ------------------------------ K: whole-word bad words ----------------------------
@pytest.mark.parametrize("text, words, expected", [
    ("Senior JavaScript Engineer", ["java"], None),          # the #95 bug: java != javascript
    ("Strong Java and Spring experience", ["java"], "java"),
    ("Backend role, ASP.NET Core", [".NET"], ".NET"),        # leading dot must still match
    ("We use .NETWORKING gear", [".NET"], None),
    ("No C2C please", ["No C2C"], "No C2C"),                 # multi-word phrases still work
    ("Must be a US Citizen", ["us citizen"], "us citizen"),  # case insensitive
    ("Rubyists welcome", ["Ruby"], None),
])
def test_find_bad_word_matches_whole_words_only(bot, text, words, expected):
    assert bot.find_bad_word(text, words) == expected


def test_a_javascript_job_is_not_skipped_by_the_bad_word_java(bot, monkeypatch):
    monkeypatch.setattr(bot, "bad_words", ["java"])
    monkeypatch.setattr(bot, "security_clearance", True)     # keep the clearance scan out of it
    monkeypatch.setattr(bot, "current_experience", -1)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    monkeypatch.setattr(bot, "find_by_class",
                        lambda *a, **k: FakeElement(text="Senior JavaScript engineer, React and Node."))

    description, experience, skip, reason, message = bot.get_job_description()

    assert skip is False
    assert description.startswith("Senior JavaScript")


# ------------------------- F: recommended_wait was inverted ------------------------
def test_recommended_filter_wait_is_not_inverted(bot):
    assert bot.recommended_filter_wait(1) == 1    # the default click_gap must still pause
    assert bot.recommended_filter_wait(3) == 1
    assert bot.recommended_filter_wait(0) == 0    # only "no click gap" means no pause


# -------------------- B: an unreadable job description must skip -------------------
def test_unreadable_job_description_skips_the_job(bot, monkeypatch):
    def boom(*args, **kwargs):
        raise NoSuchElementException("jobs-box__html-content")

    monkeypatch.setattr(bot, "find_by_class", boom)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)

    description, experience, skip, reason, message = bot.get_job_description()

    assert description == "Unknown"
    assert skip is True          # never apply to a job whose description we never read
    assert reason and message


# ------------------ H: a run where nothing applied must not report zeros -----------
def test_non_easy_apply_job_is_counted_as_skipped(bot, monkeypatch):
    monkeypatch.setattr(bot, "easy_apply_only", True)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    monkeypatch.setattr(bot, "skip_count", 0)

    skip, link, tabs = bot.external_apply(object(), "1", "link", "resume", None, "Easy Applied", "shot")

    assert skip is True
    assert bot.skip_count == 1


# --------------------------- C: resilient Easy Apply detection ---------------------
def test_easy_apply_detection_is_an_ordered_fallback_list(bot):
    xpaths = [xpath for _, xpath in bot.easy_apply_locators]
    assert len(xpaths) > 1                                   # fallbacks, not one brittle locator
    # Measured 2026-09-09: `id="jobs-apply-button-id"` is on the real button and is the most
    # stable anchor there is, so it leads. The openSDUIApplyFlow flag was NOT in the captured
    # DOM, so it is kept only as one of the fallbacks.
    assert "jobs-apply-button-id" in xpaths[0]
    assert any("openSDUIApplyFlow=true" in xpath for xpath in xpaths)
    assert not any("artdeco-button--3" in xpath for xpath in xpaths)

    source = open(os.path.join(os.path.dirname(__file__), os.pardir, "runAiBot.py"), encoding="utf-8").read()
    assert "artdeco-button--3" not in source                 # the size token is gone everywhere


# ------------------------------- M: the no-submit flag -----------------------------
def test_stop_before_submit_setting_is_always_defined(bot):
    assert isinstance(bot.stop_before_submit, bool)
