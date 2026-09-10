'''
Regression tests for the H-1B sponsorship filter (tier 1: the job-description text scan).

What it must get right, and why each case is here:

* The negation trap. Real postings say both things - "we do not require you to have
  sponsorship... we will sponsor H-1B transfers". Matching the refusal alone skips a job
  that actually sponsors, so the OFFER phrases are checked first and an offer always wins.
* No substring matching. This codebase has shipped five naive-substring bugs already
  ('state' in "United States", 'no' in "Non-citizen", 'java' in "JavaScript"). Matching
  goes through find_bad_word, so "sponsorship of our annual conference" is not a refusal.
* Silence means APPLY. Most postings say nothing about sponsorship. Absence of evidence is
  never a skip: a wrong skip costs a real job, a wrong apply costs thirty seconds.
* Inert unless asked for. require_visa != "Yes" or skip_non_sponsoring_jobs = False must
  change nothing at all.

This is a JD-text signal only. It says nothing about whether the employer has ever
sponsored anyone - that question is deliberately not answered here.

Every config value an assertion depends on is monkeypatched: the tests pin down the code's
behaviour, not the user's own config/search.py.

License: MIT  (https://opensource.org/license/mit)
'''

import sys
import types

import pytest


@pytest.fixture(scope="module")
def bot():
    '''Import runAiBot with a stubbed browser session, so importing it never opens Chrome.'''
    fake_chrome = types.ModuleType("modules.open_chrome")
    fake_chrome.options = fake_chrome.driver = fake_chrome.actions = fake_chrome.wait = None
    sys.modules["modules.open_chrome"] = fake_chrome
    import runAiBot
    return runAiBot


class FakeDescription:
    '''Stand-in for the "jobs-box__html-content" WebElement: it only needs `.text`.'''

    def __init__(self, text):
        self.text = text


OFFERED = ["visa sponsorship available", "sponsorship available", "sponsorship is available",
           "we sponsor", "we do sponsor", "will sponsor", "open to sponsorship",
           "h-1b transfer", "h1b transfer", "cap-exempt", "cap exempt"]

UNAVAILABLE = ["will not sponsor", "do not sponsor", "does not sponsor", "cannot sponsor",
               "unable to sponsor", "not able to sponsor", "not offer sponsorship",
               "not provide sponsorship", "does not provide immigration", "no visa sponsorship",
               "without sponsorship", "without the need for sponsorship",
               "sponsorship not available", "sponsorship is not available",
               "not eligible for visa sponsorship", "must be a us citizen",
               "must be a u.s. citizen"]


@pytest.fixture(autouse=True)
def pinned_config(bot, monkeypatch):
    '''Pin every setting the assertions depend on, and keep the other filters out of it.'''
    monkeypatch.setattr(bot, "require_visa", "Yes")
    monkeypatch.setattr(bot, "skip_non_sponsoring_jobs", True)
    monkeypatch.setattr(bot, "sponsorship_offered_phrases", OFFERED)
    monkeypatch.setattr(bot, "sponsorship_unavailable_phrases", UNAVAILABLE)
    monkeypatch.setattr(bot, "bad_words", [])                 # no bad-word skip
    monkeypatch.setattr(bot, "security_clearance", True)      # no clearance skip
    monkeypatch.setattr(bot, "current_experience", -1)        # no experience skip
    monkeypatch.setattr(bot, "did_masters", False)
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)


def scan(bot, monkeypatch, description):
    '''Run the real get_job_description over one faked job description.'''
    monkeypatch.setattr(bot, "find_by_class", lambda *a, **k: FakeDescription(description))
    _description, _experience, skip, reason, message = bot.get_job_description()
    return skip, reason, message


# --------------------------- postings that refuse sponsorship ----------------------------
@pytest.mark.parametrize("description, phrase", [
    ("This role is not eligible for visa sponsorship.",
     "not eligible for visa sponsorship"),
    ("Applicants must be authorized to work in the United States without sponsorship now "
     "or in the future.", "without sponsorship"),
    ("We are unable to sponsor or take over sponsorship of an employment visa at this time.",
     "unable to sponsor"),
    ("Sponsorship is not available for this position.", "sponsorship is not available"),
    ("GM DOES NOT PROVIDE IMMIGRATION-RELATED SPONSORSHIP FOR THIS ROLE.",
     "does not provide immigration"),
])
def test_a_posting_that_refuses_sponsorship_is_skipped(bot, monkeypatch, description, phrase):
    skip, reason, message = scan(bot, monkeypatch, description)

    assert skip is True
    # The matched phrase has to be in the logged reason, or a false positive is untunable.
    assert phrase in reason
    assert message


# ------------------- the negation trap: an offer beats a refusal, always ------------------
@pytest.mark.parametrize("description", [
    # The refusal reading of this one is a phrase-list failure: "do not ... sponsorship"
    # is not a refusal, and no refusal phrase may be loose enough to match it.
    "We do not require you to have sponsorship. We will sponsor H-1B transfers.",
    # This one really does contain a refusal phrase ("unable to sponsor") next to an offer
    # ("will sponsor"), which is how cap-subject-but-transfer-friendly postings are worded.
    # It is the case that pins the ordering: refusal-first would skip a job that sponsors.
    "We are unable to sponsor new cap-subject H-1B petitions at this time, however we "
    "will sponsor H-1B transfers for candidates already holding status.",
])
def test_an_offer_of_sponsorship_wins_over_a_refusal_phrase(bot, monkeypatch, description):
    skip, reason, _message = scan(bot, monkeypatch, description)

    assert skip is False, "offer phrases must be checked before refusal phrases"
    assert reason is None


@pytest.mark.parametrize("description", [
    "Visa sponsorship available for exceptional candidates.",
    "This role is cap-exempt and we sponsor H-1B transfers.",
    "We are open to sponsorship for the right person.",
])
def test_a_posting_that_offers_sponsorship_is_applied_to(bot, monkeypatch, description):
    skip, _reason, _message = scan(bot, monkeypatch, description)

    assert skip is False


# ------------------------- silence is never treated as a refusal -------------------------
def test_a_posting_with_no_sponsorship_language_is_applied_to(bot, monkeypatch):
    skip, reason, _message = scan(bot, monkeypatch,
        "Senior Python engineer. You will own our data pipeline and mentor two juniors.")

    assert skip is False
    assert reason is None


# ---------------- no substring false positives (the sixth one stops here) ----------------
@pytest.mark.parametrize("description", [
    "We are proud to fund the sponsorship of our annual conference for the community.",
    "The marketing team produces sponsored content and partner newsletters.",
    "You will manage sponsorships across our developer events.",
])
def test_unrelated_uses_of_the_word_sponsorship_do_not_skip(bot, monkeypatch, description):
    skip, _reason, _message = scan(bot, monkeypatch, description)

    assert skip is False


# ------------------------------- inert unless switched on --------------------------------
REFUSAL = "This role is not eligible for visa sponsorship."


def test_nothing_is_skipped_when_the_user_does_not_need_sponsorship(bot, monkeypatch):
    monkeypatch.setattr(bot, "require_visa", "No")

    skip, reason, _message = scan(bot, monkeypatch, REFUSAL)

    assert skip is False
    assert reason is None


def test_nothing_is_skipped_while_the_setting_is_off(bot, monkeypatch):
    monkeypatch.setattr(bot, "skip_non_sponsoring_jobs", False)

    skip, reason, _message = scan(bot, monkeypatch, REFUSAL)

    assert skip is False
    assert reason is None


# --------------- the settings must exist and be tunable without editing code -------------
def test_the_settings_exist_in_the_config_file(bot):
    '''Existence only. The user's own values are his to set, so nothing here asserts them -
    reading the live config is what used to break this suite whenever he corrected it.'''
    import config.search as search

    assert isinstance(search.skip_non_sponsoring_jobs, bool)
    assert search.sponsorship_offered_phrases          # tunable without editing code
    assert search.sponsorship_unavailable_phrases
