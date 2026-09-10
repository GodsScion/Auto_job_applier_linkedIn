'''
Regression tests for how Easy Apply question labels are classified.

The bug these pin down: every check was a naive substring test, so
"Are you currently legally authorized to work in the United States?" matched `'state'`
(inside "States") and a work-authorization question was answered with the user's state
of residence. Matching is whole-word now, and work authorization is classified before
location everywhere it is asked.

Same bug class on the answer side: `'no' in lower_answer` fired inside "**No**n-citizen
allowed to work...", so "are you legally authorized to work here?" was answered "No" -
telling every employer the applicant is not authorized to work. And the three questions
(sponsorship / authorization / citizenship status) are three separate answers now.

Every config value an assertion depends on is monkeypatched below. These tests used to
read the live `config/questions.py`, so correcting the user's own config broke the suite;
what is under test is the code's routing, not his answers.

Also covers the exit from an unanswerable required question: not guessing is correct,
but it needs a bounded number of attempts or the form loops forever.

License: MIT  (https://opensource.org/license/mit)
'''

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


STATE = "Teststate"
CITIZENSHIP = "Non-citizen allowed to work for any employer"
CITIZENSHIP_OPTIONS = ["Select an option", "U.S. Citizen/Permanent Resident",
                       "Non-citizen allowed to work for any employer", CITIZENSHIP,
                       "Non-citizen seeking work authorization", "Other"]


@pytest.fixture(autouse=True)
def pinned_config(bot, monkeypatch):
    '''Pin the config the assertions depend on, so they hold whatever the user configured.'''
    monkeypatch.setattr(bot, "require_visa", "Yes")
    monkeypatch.setattr(bot, "legally_authorized", "Yes")
    monkeypatch.setattr(bot, "us_citizenship", CITIZENSHIP)
    monkeypatch.setattr(bot, "state", STATE)


class FakeElement:
    '''Stand-in for a WebElement: `children` maps an XPath/tag/class to what it resolves to.'''

    def __init__(self, text="", children=None):
        self.text = text
        self.children = children or {}

    def find_element(self, by, locator):
        if locator in self.children:
            return self.children[locator]
        raise NoSuchElementException(locator)

    def find_elements(self, by, locator):
        found = self.children.get(locator)
        if isinstance(found, list):
            return found
        return [found] if found else []

    def click(self):
        pass


class FakeSelect:
    '''Enough of selenium's `Select` to drive the dropdown branch of answer_questions.'''

    def __init__(self, option_texts, selected="Select an option"):
        self.options = [FakeElement(text=text) for text in option_texts]
        self.selected = selected
        self.picked = None

    @property
    def first_selected_option(self):
        return FakeElement(text=self.selected)

    def select_by_visible_text(self, text):
        for option in self.options:
            if option.text == text:
                self.picked = self.selected = text
                return
        raise NoSuchElementException(text)


def dropdown(bot, monkeypatch, question_text, option_texts):
    '''Builds a modal holding one <select> question and returns (modal, FakeSelect).'''
    fake_select = FakeSelect(option_texts)
    monkeypatch.setattr(bot, "Select", lambda element: fake_select)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    question = FakeElement(children={
        ".//select": FakeElement(),
        "label": FakeElement(children={"span": FakeElement(text=question_text)}),
    })
    return FakeElement(children={".//div[@data-test-form-element]": [question]}), fake_select


# --------------------------- the substring bug itself ------------------------------
def test_label_has_matches_whole_words_only(bot):
    assert not bot.label_has("are you legally authorized to work in the united states?", 'state')
    assert bot.label_has("what state do you live in?", 'state')
    assert not bot.label_has("what is your linkedin profile?", 'link')     # 'link' vs "linkedin"
    assert not bot.label_has("sexual orientation", 'sex')


def test_work_authorization_beats_location(bot):
    '''The live failure: "...United States?" was routed to the location branch.'''
    assert bot.work_authorization_answer(
        "are you currently legally authorized to work in the united states?") == bot.legally_authorized
    assert bot.work_authorization_answer("what state do you live in?") is None


def test_the_three_questions_get_three_different_answers(bot, monkeypatch):
    '''Sponsorship, authorization and citizenship status are not the same question.'''
    monkeypatch.setattr(bot, "require_visa", "SPONSORSHIP")
    monkeypatch.setattr(bot, "legally_authorized", "AUTHORIZED")
    assert bot.work_authorization_answer(
        "will you now or in the future require sponsorship for employment visa status?") == "SPONSORSHIP"
    assert bot.work_authorization_answer(
        "are you currently legally authorized to work in the united states?") == "AUTHORIZED"
    assert bot.work_authorization_answer("what is your citizenship status?") == CITIZENSHIP
    # Ordering: "...work visa or work authorization" is a sponsorship question, not an
    # authorization one, and it contains the wording of both.
    assert bot.work_authorization_answer(
        "would you need your next employer to sponsor a new u.s. work visa or work "
        "authorization that you do not currently hold?") == "SPONSORSHIP"


def test_authorization_yes_no_question_is_answered_yes(bot, monkeypatch):
    '''He holds a valid H-1B: the honest answer is Yes. It used to submit "No".'''
    modal, select = dropdown(
        bot, monkeypatch,
        "Are you currently legally authorized to work in the United States?",
        ["Select an option", "Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked == "Yes"


def test_authorization_question_is_not_answered_with_the_state(bot, monkeypatch):
    '''Both halves at once: the state value IS on offer and must NOT be the one picked.'''
    modal, select = dropdown(
        bot, monkeypatch,
        "Are you currently legally authorized to work in the United States?",
        ["Select an option", STATE, "Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked == "Yes"


def test_citizenship_status_question_gets_the_status(bot, monkeypatch):
    modal, select = dropdown(bot, monkeypatch, "What is your citizenship status?",
                             CITIZENSHIP_OPTIONS)

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked == CITIZENSHIP
    assert select.picked != "No"


def test_an_answer_containing_no_as_a_substring_never_selects_the_option_no(bot, monkeypatch):
    '''"**No**n-citizen ..." carries the substring "no". Yes/No is the wrong dropdown for
    it, so the honest outcome is unanswered - never the option "No".'''
    modal, select = dropdown(bot, monkeypatch, "What is your citizenship status?",
                             ["Select an option", "Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked is None
    assert select.selected == "Select an option"
    assert bot.unanswered_questions


@pytest.mark.parametrize("configured, expected", [("Yes", "Yes"), ("No", "No")])
def test_a_configured_yes_or_no_still_maps_onto_a_worded_option(bot, monkeypatch, configured, expected):
    '''Whole-word matching must not break the plain case it was protecting.'''
    monkeypatch.setattr(bot, "require_visa", configured)
    modal, select = dropdown(
        bot, monkeypatch,
        "Will you now or in the future require sponsorship for employment visa status?",
        ["Select an option", "Yes, I will require sponsorship", "No, I will not"])

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked.startswith(expected)


@pytest.mark.parametrize("configured", ["Decline", "I do not wish to disclose"])
def test_decline_answers_still_reach_a_decline_option(bot, monkeypatch, configured):
    '''"I do not wish to disclose" holds no whole-word "no", and must not become "No".'''
    monkeypatch.setattr(bot, "disability_status", configured)
    modal, select = dropdown(bot, monkeypatch, "Do you have a disability?",
                             ["Select an option", "Yes", "No", "I don't wish to answer"])

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked == "I don't wish to answer"


def test_a_real_state_question_still_answers_with_the_state(bot, monkeypatch):
    modal, select = dropdown(bot, monkeypatch, "What state do you live in?",
                             ["Select an option", STATE])

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked == STATE


@pytest.mark.parametrize("question", [
    "Will you now or in the future require sponsorship for employment visa status?",
    "Would you need your next employer to sponsor a new U.S. work visa or work authorization "
    "that you do not currently hold? (e.g. new H-1B, or TN work status)",
    "Would you need your next employer to transfer or continue an existing U.S. work visa or "
    "work authorization? (e.g. H-1B transfer, OPT/STEM OPT employer change)",
])
def test_visa_questions_classify_as_sponsorship_not_location(bot, monkeypatch, question):
    '''Verbatim from the live run. Both contain "U.S." and neither is a location question.'''
    assert bot.work_authorization_answer(question.lower()) == bot.require_visa

    modal, select = dropdown(bot, monkeypatch, question, ["Select an option", "Yes", "No"])
    bot.answer_questions(modal, set(), "Remote")

    assert select.picked == "Yes"


# --------------------------- the infinite loop -------------------------------------
def test_unanswerable_required_question_terminates_instead_of_looping(bot, monkeypatch):
    '''
    Mirrors the Easy Apply loop in apply_to_jobs. The live run retried the same question
    13 times before the attempt ceiling tripped; the stall guard has to beat that ceiling.
    '''
    modal, _ = dropdown(bot, monkeypatch, "What is your citizenship status?",
                        ["Select an option", "Yes", "No"])   # no honest option exists

    previous_blocked, attempts, questions = None, 0, set()
    while attempts < 15:                      # 15 is the bot's own ceiling, not the fix
        attempts += 1
        questions = bot.answer_questions(modal, questions, "Remote")
        if bot.questions_are_stalled(previous_blocked):
            break
        previous_blocked = set(bot.unanswered_questions)

    assert attempts == 2, "the guard must stop the second identical pass, not run to the ceiling"
    assert bot.unanswered_questions, "and it has to report what blocked it"


def test_progress_is_not_mistaken_for_a_stall(bot):
    '''A pass that blocked on something new is progress through a multi-page form.'''
    bot.unanswered_questions.clear()
    bot.unanswered_questions.add("Which office?")
    assert not bot.questions_are_stalled(None)
    assert not bot.questions_are_stalled({"Something else"})
    assert bot.questions_are_stalled({"Which office?"})
    bot.unanswered_questions.clear()
    assert not bot.questions_are_stalled(set())


# --------------------------- discard leaves no modal behind ------------------------
class FakeActions:
    def __init__(self): self.keys = []
    def send_keys(self, key): self.keys.append(key); return self
    def perform(self): pass


def stub_discard(bot, monkeypatch, modal_states):
    '''Records the locators discard_job clicks; `modal_states` is what each check returns.'''
    clicked, states = [], iter(modal_states)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    monkeypatch.setattr(bot, "actions", FakeActions())
    monkeypatch.setattr(bot, "try_xp", lambda d, xpath, click=True: clicked.append(xpath) or True)
    monkeypatch.setattr(bot, "wait_xp_click", lambda d, xpath, time=5.0, **kw: clicked.append(xpath) or True)
    monkeypatch.setattr(bot, "easy_apply_modal_is_open", lambda: next(states))
    return clicked


def test_discard_job_uses_the_close_button_then_the_confirmation(bot, monkeypatch):
    '''ESCAPE alone did not raise the "Save this application?" dialog.'''
    clicked = stub_discard(bot, monkeypatch, [False])

    bot.discard_job()

    assert clicked == [".//button[@data-test-modal-close-btn]", bot.discard_button_xpath]


def test_discard_job_falls_back_to_escape_when_the_modal_survives(bot, monkeypatch):
    '''A modal left open intercepts every later click, which killed the whole run.'''
    clicked = stub_discard(bot, monkeypatch, [True, False])

    bot.discard_job()

    assert clicked.count(bot.discard_button_xpath) == 2      # button path, then ESCAPE path
    assert bot.actions.keys, "ESCAPE fallback was never tried"


# --------------------------- the radio branch --------------------------------------
class FakeRadio(FakeElement):
    '''One <input type="radio">: the branch reads its id, value and selected state.'''

    def __init__(self, id, label, selected=False):
        super().__init__(text=label)
        self.id, self.label, self.selected = id, label, selected

    def get_attribute(self, name):
        return {"id": self.id, "value": self.label}[name]

    def is_selected(self):
        return self.selected


class FakeMouse:
    '''`actions.move_to_element(x).click().perform()` - records what x was, if anything.'''

    def __init__(self): self.clicked = None
    def move_to_element(self, element): self.clicked = element; return self
    def click(self): return self
    def perform(self): pass


def radio_group(bot, monkeypatch, question_text, option_labels):
    '''Builds a modal holding one radio fieldset; returns (modal, FakeMouse, options).'''
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    mouse = FakeMouse()
    monkeypatch.setattr(bot, "actions", mouse)
    options = [FakeRadio(f"opt{i}", text) for i, text in enumerate(option_labels)]
    # Both paths - the exact-label XPath and the option inputs - end up clicking an element
    # whose `.text` is the option label, so one assertion covers both.
    children = {
        './/span[@data-test-form-builder-radio-button-form-component__title]':
            FakeElement(children={"visually-hidden": FakeElement(text=question_text)}),
        'input': options,
    }
    for option in options:
        children[f'.//label[@for="{option.id}"]'] = FakeElement(text=option.label)
        children[f".//label[normalize-space()='{option.label}']"] = FakeElement(text=option.label)
    radio = FakeElement(children=children)
    question = FakeElement(children={
        './/fieldset[@data-test-form-builder-radio-button-form-component="true"]': radio})
    return FakeElement(children={".//div[@data-test-form-element]": [question]}), mouse, options


@pytest.mark.parametrize("question", [
    "Do you have an active security clearance?",
    "Do you have 10+ years of experience?",
])
def test_an_unrecognised_radio_question_is_left_unanswered(bot, monkeypatch, question):
    '''It defaulted to `answer = 'Yes'` and, failing that, clicked `options[0]`. Both
    submitted a false answer on a real application.'''
    modal, mouse, options = radio_group(bot, monkeypatch, question, ["Yes", "No"])

    questions_list = bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked is None, "an unclassified question must not click anything"
    assert bot.unanswered_questions, "and it has to be reported so the job is skipped"
    recorded = next(iter(bot.unanswered_questions))
    assert question in recorded and '"Yes"' in recorded and '"No"' in recorded
    answers = {answer for _, answer, kind, _ in questions_list if kind == "radio"}
    assert answers == {None}                       # not 'Yes', not options[0]
    assert options[0].label not in {str(a) for a in answers}


def test_a_configured_veteran_status_still_selects_its_radio(bot, monkeypatch):
    monkeypatch.setattr(bot, "veteran_status", "I am not a protected veteran")
    modal, mouse, _ = radio_group(
        bot, monkeypatch, "Please select your veteran status",
        ["I identify as one or more of the classifications of a protected veteran",
         "I am not a protected veteran", "I don't wish to answer"])

    bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked.text == "I am not a protected veteran"
    assert not bot.unanswered_questions


def test_a_configured_disability_answer_reaches_the_worded_option(bot, monkeypatch):
    '''Configured "No", option worded "No, I don't have a disability" - the mapper, not luck.'''
    monkeypatch.setattr(bot, "disability_status", "No")
    modal, mouse, _ = radio_group(
        bot, monkeypatch, "Do you have a disability?",
        ["Yes, I have a disability", "No, I don't have a disability", "I don't wish to answer"])

    bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked.text == "No, I don't have a disability"


@pytest.mark.parametrize("configured", ["Decline", "I do not wish to disclose"])
def test_decline_answers_still_reach_a_decline_radio(bot, monkeypatch, configured):
    monkeypatch.setattr(bot, "disability_status", configured)
    modal, mouse, _ = radio_group(bot, monkeypatch, "Do you have a disability?",
                                  ["Yes", "No", "I don't wish to answer"])

    bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked.text == "I don't wish to answer"


@pytest.mark.parametrize("question", [
    "Are you currently legally authorized to work in the United States?",
    "Will you now or in the future require sponsorship for employment visa status?",
])
def test_work_authorization_radios_match_the_dropdown_routing(bot, monkeypatch, question):
    '''Same routing the <select> branch got: both are honest Yes answers on an H-1B.'''
    modal, mouse, _ = radio_group(bot, monkeypatch, question, ["Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked.text == "Yes"


def test_a_radio_answer_containing_no_as_a_substring_never_selects_no(bot, monkeypatch):
    '''"**No**n-citizen ..." into a Yes/No radio group: the honest outcome is unanswered.'''
    modal, mouse, _ = radio_group(bot, monkeypatch, "Are you a US citizen?", ["Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked is None, f'clicked "{mouse.clicked and mouse.clicked.text}"'
    assert bot.unanswered_questions


# --------------------------- the checkbox branch -----------------------------------
class FakeCheckbox(FakeElement):
    '''One <input type="checkbox">: the branch reads its id and its selected state.'''

    def __init__(self, id=None, selected=False):
        super().__init__()
        self.id, self.selected = id, selected

    def get_attribute(self, name):
        return {"id": self.id}[name]

    def is_selected(self):
        return self.selected


def checkbox_question(bot, monkeypatch, visible_label, id=None, hidden_label=None):
    '''Builds a modal holding one checkbox question; returns (modal, FakeMouse, checkbox).'''
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    mouse = FakeMouse()
    monkeypatch.setattr(bot, "actions", mouse)
    box = FakeCheckbox(id)
    children = {".//input[@type='checkbox']": box,
                ".//label[@for]": FakeElement(text=visible_label)}
    if hidden_label is not None:
        children[".//span[@class='visually-hidden']"] = FakeElement(text=hidden_label)
    question = FakeElement(children=children)
    return FakeElement(children={".//div[@data-test-form-element]": [question]}), mouse, box


@pytest.mark.parametrize("attestation", [
    "I certify that I am a U.S. citizen",
    "I consent to a background check",
    "I agree to the terms and conditions",
    "I certify that the information provided is accurate",
])
def test_an_attestation_checkbox_is_never_ticked(bot, monkeypatch, attestation):
    '''It ticked ANY unchecked box, which silently agreed to legal attestations the user
    never saw. There is no honest default for these.'''
    modal, mouse, box = checkbox_question(bot, monkeypatch, attestation)

    questions_list = bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked is None, "an attestation must not be auto-agreed to"
    assert not box.selected
    assert bot.unanswered_questions, "and it has to be reported so the job is skipped"
    assert attestation in next(iter(bot.unanswered_questions))   # the exact label, verbatim
    assert {checked for _, checked, kind, _ in questions_list if kind == "checkbox"} == {False}


def test_an_unclassifiable_checkbox_is_not_ticked_either(bot, monkeypatch):
    '''Cannot classify it -> it is unsafe. Never guess.'''
    modal, mouse, box = checkbox_question(bot, monkeypatch, "Please tick this box")

    bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked is None and not box.selected
    assert bot.unanswered_questions


def test_an_already_ticked_checkbox_is_left_alone(bot, monkeypatch):
    '''Whatever the user ticked himself is his answer, and it is not a blocker.'''
    modal, mouse, box = checkbox_question(bot, monkeypatch, "I agree to the terms")
    box.selected = True

    bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked is None
    assert not bot.unanswered_questions


def test_the_follow_company_checkbox_is_left_to_follow_company(bot, monkeypatch):
    '''It has an owner already - `follow_company()` - so this branch must not touch it,
    and must not report it as a question that blocked the application.'''
    modal, mouse, box = checkbox_question(
        bot, monkeypatch, "Follow Acme Corp to stay up to date with their page.",
        id="follow-company-checkbox")

    questions_list = bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked is None and not box.selected
    assert not bot.unanswered_questions
    assert not [question for question in questions_list if question[2] == "checkbox"]


@pytest.mark.parametrize("follow_companies, already_ticked, expect_click", [
    (True, False, True),        # wants to follow, box is off -> click it
    (False, True, True),        # does not want to follow, box is on -> click it off
    (True, True, False),        # already matches the setting -> leave it
])
def test_follow_company_still_sets_the_box(bot, monkeypatch, follow_companies,
                                           already_ticked, expect_click):
    monkeypatch.setattr(bot, "follow_companies", follow_companies)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    box, clicked = FakeCheckbox("follow-company-checkbox", already_ticked), []
    monkeypatch.setattr(bot, "try_xp",
                        lambda driver, xpath, click=True: clicked.append(xpath) or True if click else box)

    bot.follow_company(FakeElement())

    assert bool(clicked) == expect_click


# --------------------------- the text branch ---------------------------------------
class FakeTextInput(FakeElement):
    '''One <input type="text">: reads/writes `value`, and `clear()` empties it.'''

    def __init__(self, value=""):
        super().__init__()
        self.value = value

    def get_attribute(self, name):
        return self.value if name == "value" else None

    def clear(self):
        self.value = ""


def text_question(bot, monkeypatch, label_text, value=""):
    '''Builds a modal holding one text question; returns (modal, FakeTextInput).'''
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)
    monkeypatch.setattr(bot, "use_AI", False)
    # Real human_type sleeps between keystrokes, and does nothing at all for "".
    monkeypatch.setattr(bot, "human_type",
                        lambda target, text: setattr(target, "value", target.value + (text or "")))
    field = FakeTextInput(value)
    question = FakeElement(children={".//input[@type='text']": field,
                                     ".//label[@for]": FakeElement(text=label_text)})
    return FakeElement(children={".//div[@data-test-form-element]": [question]}), field


@pytest.mark.parametrize("question", [
    "How many years of Kubernetes experience do you have?",
    "How many years of experience do you have with Python?",
    "How many people did you manage?",
    "What is your expected bonus?",
])
def test_an_unclassified_text_question_is_not_answered_with_a_number(bot, monkeypatch, question):
    '''Every unmatched text question fell back to `years_of_experience`, so the user's
    total years of experience was submitted as the answer to whatever was asked.'''
    monkeypatch.setattr(bot, "years_of_experience", "6")
    modal, field = text_question(bot, monkeypatch, question)

    bot.answer_questions(modal, set(), "Remote")

    assert field.value == "", f'answered "{field.value}" to "{question}"'
    assert bot.unanswered_questions, "and it has to be reported so the job is skipped"
    assert question in next(iter(bot.unanswered_questions))


@pytest.mark.parametrize("question, setting, value", [
    ("What is your phone number?", "phone_number", "5551234567"),
    ("What is your notice period in months?", "notice_period_months", "2"),
    ("What is your expected salary?", "desired_salary", "250000"),
    ("LinkedIn profile URL", "linkedIn", "https://linkedin.com/in/example"),
    ("What is your zip code?", "zipcode", "12345"),
    ("How many years of work experience do you have?", "years_of_experience", "6"),
    ("Please type your signature", "full_name", "Jane Q Applicant"),
])
def test_the_text_classifications_that_were_right_still_answer(bot, monkeypatch, question,
                                                               setting, value):
    '''Guard against over-correcting: removing the fallback must not silence the branches
    that were classifying correctly.'''
    monkeypatch.setattr(bot, setting, value)
    modal, field = text_question(bot, monkeypatch, question)

    bot.answer_questions(modal, set(), "Remote")

    assert field.value == value
    assert not bot.unanswered_questions


def test_an_unrecognised_dropdown_question_is_left_unanswered(bot, monkeypatch):
    '''The <select> twin of the radio default: `answer = 'Yes'` answered every
    unclassified dropdown - "Do you have an active security clearance?" - with a Yes.'''
    modal, select = dropdown(bot, monkeypatch, "Do you have an active security clearance?",
                             ["Select an option", "Yes", "No"])

    questions_list = bot.answer_questions(modal, set(), "Remote")

    assert select.picked is None, f'picked "{select.picked}"'
    assert select.selected == "Select an option"
    assert bot.unanswered_questions
    assert {answer for _, answer, kind, _ in questions_list if kind == "select"} == {"Select an option"}
