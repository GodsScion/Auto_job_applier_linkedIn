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


# ------------------- N: the React dialog and missing top-card regressions -----------
from selenium.common.exceptions import ElementClickInterceptedException


class _EmptyDriver:
    '''A page on which every lookup misses - the 2026 React render without a top card.'''
    def find_element(self, by, locator):
        raise NoSuchElementException(locator)

    def find_elements(self, by, locator):
        return []

    def execute_script(self, *args, **kwargs):
        return False


def test_check_blacklist_tolerates_missing_top_card_and_company(bot, monkeypatch):
    '''Used to raise ValueError("Failed to find an element with given classes").'''
    monkeypatch.setattr(bot, "driver", _EmptyDriver())
    monkeypatch.setattr(bot, "about_company_bad_words", [])
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    monkeypatch.setattr(bot, "sleep", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(bot, "_scroll_job_details_to_bottom", lambda: None, raising=False)

    rejected, companies, top_card = bot.check_blacklist(set(), "1", "Acme", set())

    assert rejected == set()
    assert companies == set()
    assert top_card is None


def test_blacklist_still_checks_the_company_name_when_the_section_is_missing(bot, monkeypatch):
    '''about_company_bad_words also lists company names; the section is not required.'''
    monkeypatch.setattr(bot, "driver", _EmptyDriver())
    monkeypatch.setattr(bot, "about_company_bad_words", ["Crossover"])
    monkeypatch.setattr(bot, "about_company_good_words", [])
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    monkeypatch.setattr(bot, "sleep", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(bot, "_scroll_job_details_to_bottom", lambda: None, raising=False)

    with pytest.raises(ValueError, match="Crossover"):
        bot.check_blacklist(set(), "1", "Crossover", set())


class _AboutCompanyDriver(_EmptyDriver):
    '''Only the data-testid anchor matches - the 2026 render has no legacy classes.'''

    def __init__(self, section):
        self.section = section

    def find_elements(self, by, locator):
        if "about-company" in locator:
            return [self.section]
        return []

    def execute_script(self, *args, **kwargs):
        return None


def test_check_blacklist_finds_about_company_by_test_id_when_classes_are_gone(bot, monkeypatch):
    section = FakeElement(text="We build useful things with a very long description.")
    section.is_displayed = lambda: True
    monkeypatch.setattr(bot, "driver", _AboutCompanyDriver(section))
    monkeypatch.setattr(bot, "about_company_bad_words", [])
    monkeypatch.setattr(bot, "about_company_good_words", [])
    monkeypatch.setattr(bot, "scroll_to_view", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(bot, "buffer", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)

    rejected, companies, top_card = bot.check_blacklist(set(), "1", "Acme", set())

    assert rejected == set()
    assert companies == set()
    assert top_card is None


class _CloseButton:
    def __init__(self, dialog):
        self.dialog = dialog

    def is_displayed(self):
        return not self.dialog.closed

    def click(self):
        self.dialog.closed = True


class _Dialog:
    id = "dialog-1"

    def __init__(self):
        self.closed = False

    def is_displayed(self):
        return not self.closed

    def get_attribute(self, name):
        return ""

    def find_element(self, by, locator):
        if not self.closed and "button" in locator:
            return _CloseButton(self)
        raise NoSuchElementException(locator)

    def find_elements(self, by, locator):
        return []


class _DialogDriver(_EmptyDriver):
    def __init__(self, dialog):
        self.dialog = dialog

    def find_elements(self, by, locator):
        return [] if self.dialog.closed else [self.dialog]


def test_dismiss_open_dialogs_closes_the_covering_sheet(bot, monkeypatch):
    dialog = _Dialog()
    monkeypatch.setattr(bot, "driver", _DialogDriver(dialog))
    monkeypatch.setattr(bot, "sleep", lambda *_: None, raising=False)

    assert bot.dismiss_open_dialogs() is True
    assert dialog.closed is True


class _InterceptedOnceButton:
    def __init__(self):
        self.clicks = 0

    def click(self):
        self.clicks += 1
        if self.clicks == 1:
            raise ElementClickInterceptedException("dialog covers the button")


def test_click_apply_button_dismisses_an_intercepting_dialog_and_retries(bot, monkeypatch):
    button = _InterceptedOnceButton()
    dismissed = []
    monkeypatch.setattr(bot, "scroll_to_view", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(bot, "dismiss_open_dialogs", lambda **k: dismissed.append(k) or True, raising=False)

    assert bot.click_apply_button(button) is True
    assert button.clicks == 2          # one intercepted click, one retry after dismissal
    assert dismissed and dismissed[0].get("keep") is button


class _AlwaysInterceptedButton(_InterceptedOnceButton):
    def click(self):
        self.clicks += 1
        raise ElementClickInterceptedException("dialog never goes away")


class _ScriptDriver(_EmptyDriver):
    def __init__(self):
        self.script_clicks = 0

    def execute_script(self, script, *args):
        self.script_clicks += 1
        return None


def test_click_apply_button_falls_back_to_a_script_click(bot, monkeypatch):
    button = _AlwaysInterceptedButton()
    driver = _ScriptDriver()
    monkeypatch.setattr(bot, "driver", driver)
    monkeypatch.setattr(bot, "scroll_to_view", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(bot, "dismiss_open_dialogs", lambda **k: True, raising=False)

    assert bot.click_apply_button(button) is True
    assert driver.script_clicks == 1


class _Scope:
    def __init__(self, button):
        self.button = button

    def find_element(self, by, locator):
        return self.button


class _LookupDriver(_EmptyDriver):
    def __init__(self, document_button):
        self.document_button = document_button

    def find_element(self, by, locator):
        return self.document_button


def test_apply_button_is_read_from_the_top_card_not_the_search_list(bot, monkeypatch):
    top_button, list_button = FakeElement(), FakeElement()
    monkeypatch.setattr(bot, "driver", _LookupDriver(list_button))
    for element in (top_button, list_button):
        element.is_displayed = lambda: True

    found = bot.find_apply_button(".//button", top_card=_Scope(top_button))

    assert found is top_button


def test_time_posted_is_read_without_a_top_card(bot, monkeypatch):
    span = FakeElement(text="3 days ago")
    span.is_displayed = lambda: True
    monkeypatch.setattr(bot, "driver", _LookupDriver(span))

    assert bot.get_time_posted_text(None) == "3 days ago"


def test_easy_apply_detection_recovers_instead_of_clicking_blindly(bot):
    import inspect
    src = inspect.getsource(bot.apply_to_jobs)
    assert "find_apply_button(xpath" in src
    assert "click_apply_button(apply_button)" in src
    assert "easy_apply_button_seen" in src
    assert 'apply_button = try_xp(driver, xpath, False)' not in src


class _ModalDriver(_EmptyDriver):
    def __init__(self, modal):
        self.modal = modal

    def find_elements(self, by, locator):
        if "data-testid='dialog'" in locator or "@role='dialog'" in locator:
            return [self.modal]
        return []


def test_easy_apply_modal_is_recognised_inside_a_native_dialog(bot, monkeypatch):
    '''The 2026 apply sheet is a native <dialog>, so class-only detection missed it.'''
    modal = _TextModal("Submit application")
    monkeypatch.setattr(bot, "driver", _ModalDriver(modal))

    assert bot.easy_apply_modal_is_open() is True
    assert bot._open_dialogs() == []      # never treated as an obstruction to close


class _Confirmation:
    id = "confirmation-1"

    def __init__(self, text):
        self.text = text
        self.closed = False

    def is_displayed(self):
        return not self.closed

    def get_attribute(self, name):
        return ""

    def find_element(self, by, locator):
        if not self.closed and "button" in locator:
            return _CloseButton(self)
        raise NoSuchElementException(locator)

    def find_elements(self, by, locator):
        return []


class _ConfirmationDriver(_EmptyDriver):
    def __init__(self, dialog):
        self.dialog = dialog

    def find_elements(self, by, locator):
        if self.dialog.closed:
            return []
        if "dialog" in locator or "artdeco-modal" in locator:
            return [self.dialog]
        return []


def test_application_sent_confirmation_is_found_and_closed(bot, monkeypatch):
    confirmation = _Confirmation("Your application was sent to Acme Corp.")
    monkeypatch.setattr(bot, "driver", _ConfirmationDriver(confirmation))
    monkeypatch.setattr(bot, "sleep", lambda *_: None, raising=False)

    assert bot.application_sent_confirmation() is confirmation
    assert bot.close_application_confirmation(timeout=0.1) is True
    assert confirmation.closed is True


def test_other_dialogs_are_not_mistaken_for_a_success_confirmation(bot, monkeypatch):
    dialog = _Confirmation("All filters\nEasy Apply\nShow results")
    monkeypatch.setattr(bot, "driver", _ConfirmationDriver(dialog))

    assert bot.application_sent_confirmation() is None
    assert dialog.closed is False


def test_submit_path_waits_for_and_closes_the_confirmation(bot):
    import inspect
    src = inspect.getsource(bot.apply_to_jobs)
    assert "close_application_confirmation()" in src
    assert 'wait_span_click(driver, "Done", 2)' not in src


class _TextModal:
    '''The 2026 apply sheet: no usable class, controls identified by their text only.'''
    id = "text-apply-modal"

    def __init__(self, step_text="Next"):
        self.step_text = step_text

    def is_displayed(self):
        return True

    def get_attribute(self, name):
        return ""       # notably NOT jobs-easy-apply-modal

    def find_elements(self, by, locator):
        visible = lambda element: (setattr(element, "is_displayed", lambda: True) or element)
        if "@aria-label='Submit application'" in locator:
            return [visible(FakeElement())] if self.step_text == "Submit application" else []
        if "normalize-space(.)='Submit application'" in locator:
            return [visible(FakeElement(text="Submit application"))] if self.step_text == "Submit application" else []
        if "starts-with(normalize-space(.), 'Apply to')" in locator:
            return []
        if "Your job application progress" in locator:
            return []
        if "normalize-space(.)='Next'" in locator:
            return [visible(FakeElement(text=self.step_text))] if self.step_text in ("Next", "Review") else []
        if locator in (".//form", ".//input", ".//select", ".//textarea"):
            return [visible(FakeElement())] if locator == ".//form" else []
        return []


def test_apply_sheet_is_recognised_by_next_text_without_any_class(bot, monkeypatch):
    modal = _TextModal("Next")
    monkeypatch.setattr(bot, "driver", _ModalDriver(modal))

    assert bot.easy_apply_modal_is_open() is True
    assert bot._open_dialogs() == []      # it must not be dismissed as an obstruction


def test_submit_application_text_alone_identifies_the_apply_sheet(bot, monkeypatch):
    modal = _TextModal("Submit application")
    monkeypatch.setattr(bot, "driver", _ModalDriver(modal))

    assert bot._is_easy_apply_dialog(modal) is True


def test_intercept_by_the_open_apply_sheet_does_not_dismiss_it(bot, monkeypatch):
    button = _AlwaysInterceptedButton()
    dismissed = []
    monkeypatch.setattr(bot, "scroll_to_view", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(bot, "easy_apply_modal_is_open", lambda: True)
    monkeypatch.setattr(bot, "dismiss_open_dialogs", lambda **k: dismissed.append(k) or True, raising=False)

    assert bot.click_apply_button(button) is True
    assert button.clicks == 1
    assert dismissed == []


def test_find_easy_apply_modal_returns_the_new_text_only_sheet(bot, monkeypatch):
    modal = _TextModal("Next")
    monkeypatch.setattr(bot, "driver", _ModalDriver(modal))
    monkeypatch.setattr(bot, "sleep", lambda *_: None, raising=False)

    assert bot.find_easy_apply_modal(timeout=0.1) is modal


def test_apply_flow_binds_the_detected_modal_not_the_old_class(bot):
    import inspect
    src = inspect.getsource(bot.apply_to_jobs)
    assert "modal = find_easy_apply_modal(" in src
    assert 'modal = find_by_class(driver, "jobs-easy-apply-modal")' not in src
    assert "if modal is None:" in src or "modal is None" in src


# ------------------- O: About Company detection on the 2026 detail pane ------------
class _Node(FakeElement):
    '''A faked DOM node with a parent, for the heading -> container climb.'''

    def __init__(self, text="", parent=None):
        super().__init__(text=text)
        self.parent = parent

    def is_displayed(self):
        return True

    def find_element(self, by, locator):
        if locator == ".." and self.parent is not None:
            return self.parent
        raise NoSuchElementException(locator)


class _FragmentDriver(_EmptyDriver):
    '''Returns elements whose XPath contains a given fragment; everything else misses.'''

    def __init__(self, fragments, script_result=None):
        self.fragments = fragments
        self.script_result = script_result

    def find_elements(self, by, locator):
        for fragment, elements in self.fragments:
            if fragment in locator:
                return elements
        return []

    def execute_script(self, *args, **kwargs):
        return self.script_result


def test_about_company_is_found_by_the_2026_componentkey_anchor(bot, monkeypatch):
    section = _Node("About the company\nWe build useful things for people.")
    monkeypatch.setattr(bot, "driver", _FragmentDriver(
        [("aboutthecompany", [section])]))

    assert bot.find_about_company_section() is section


def test_about_company_climbs_from_a_plain_heading_to_its_description(bot, monkeypatch):
    heading = _Node("About the company")
    box = _Node("About the company\nWe build useful things for people.", parent=None)
    outer = _Node("About the job\nBuild things.\nAbout the company\n"
                  "We build useful things for people.", parent=None)
    heading.parent, box.parent = box, outer
    monkeypatch.setattr(bot, "driver", _FragmentDriver([("self::h1", [heading])]))
    monkeypatch.setattr(bot, "scroll_to_view", lambda *a, **k: None, raising=False)

    section = bot.find_about_company_section()

    assert section is box
    assert "about the job" not in section.text.lower()   # never the whole details pane


def test_about_company_climb_never_absorbs_the_job_description(bot, monkeypatch):
    heading = _Node("About the company")
    pane = _Node("About the job\nBuild things.\nAbout the company\nFollow", parent=None)
    heading.parent = pane
    monkeypatch.setattr(bot, "driver", _FragmentDriver([("self::h1", [heading])]))

    section = bot.find_about_company_section()

    assert section is not pane
    assert "about the job" not in section.text.lower()


def test_about_company_text_falls_back_to_raw_dom_text(bot, monkeypatch):
    monkeypatch.setattr(bot, "driver", _FragmentDriver(
        [], script_result="We build useful things for people."))

    assert bot._read_about_company() == "We build useful things for people."


def test_blacklist_can_reject_from_the_dom_text_fallback(bot, monkeypatch):
    monkeypatch.setattr(bot, "driver", _FragmentDriver(
        [], script_result="Crossover builds useful things."))
    monkeypatch.setattr(bot, "about_company_bad_words", ["Crossover"])
    monkeypatch.setattr(bot, "about_company_good_words", [])
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    monkeypatch.setattr(bot, "buffer", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(bot, "scroll_to_view", lambda *a, **k: None, raising=False)

    with pytest.raises(ValueError, match="Crossover"):
        bot.check_blacklist(set(), "1", "Acme", set())
