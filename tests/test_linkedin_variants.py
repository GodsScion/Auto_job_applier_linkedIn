'''
Regression tests for LinkedIn's 2026 job-card layout.

The search page moved from `li[data-occludable-job-id]` to
`[componentkey="job-card-component-ref-<jobId>"]`, removed per-card links and made
clicking a card a no-op. These tests pin the replacement discovery/extraction path.

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


class FakeCard:
    def __init__(self, attrs=None, text="", displayed=True, tag_name="div", children=None):
        self.attrs = attrs or {}
        self.text = text
        self.displayed = displayed
        self.tag_name = tag_name
        self.children = children or {}
        self.clicked = False

    def get_attribute(self, name):
        return self.attrs.get(name)

    def find_elements(self, by, locator):
        return self.children.get(locator, [])

    def is_displayed(self):
        return self.displayed

    def click(self):
        self.clicked = True


class FakeDriver:
    def __init__(self, results=None):
        self.results = results or {}
        self.requests = []

    def find_elements(self, by, locator):
        self.requests.append(locator)
        return self.results.get(locator, [])


# ------------------------------ ID extraction -------------------------------------

def test_react_card_id_comes_from_componentkey(bot):
    card = FakeCard({"componentkey": "job-card-component-ref-4481055232"})
    assert bot.get_job_id(card) == "4481055232"


@pytest.mark.parametrize("attrs, expected", [
    ({"data-occludable-job-id": "4460606885"}, "4460606885"),
    ({"data-job-id": "4452814679"}, "4452814679"),
    ({"data-entity-urn": "urn:li:jobPosting:4464813353"}, "4464813353"),
])
def test_legacy_and_guest_id_markers_still_work(bot, attrs, expected):
    assert bot.get_job_id(FakeCard(attrs)) == expected


def test_id_can_be_read_from_a_job_link(bot):
    link = FakeCard({"href": "https://www.linkedin.com/jobs/view/4481055232/?trk=x"})
    card = FakeCard(children={".//a[@href]": [link]})
    assert bot.get_job_id(card) == "4481055232"


def test_id_can_be_read_from_a_slugged_job_link(bot):
    link = FakeCard({"href": "/jobs/view/java-developer-at-charles-schwab-4481055232/"})
    card = FakeCard(children={".//a[@href]": [link]})
    assert bot.get_job_id(card) == "4481055232"


# ------------------------------ card discovery ------------------------------------

def test_find_job_cards_prefers_componentkey_variant(bot):
    card = FakeCard({"componentkey": "job-card-component-ref-4481055232"})
    driver = FakeDriver({bot.JOB_CARD_XPATHS[0]: [card]})
    assert bot.find_job_cards(driver) == [card]
    assert driver.requests == [bot.JOB_CARD_XPATHS[0]]


def test_find_job_cards_falls_back_to_occludable(bot):
    card = FakeCard({"data-occludable-job-id": "4460606885"})
    driver = FakeDriver({bot.JOB_CARD_XPATHS[1]: [card]})
    assert bot.find_job_cards(driver) == [card]


def test_find_job_cards_ignores_hidden_and_duplicate_cards(bot):
    first = FakeCard({"componentkey": "job-card-component-ref-1"})
    duplicate = FakeCard({"componentkey": "job-card-component-ref-1"})
    hidden = FakeCard({"componentkey": "job-card-component-ref-2"}, displayed=False)
    driver = FakeDriver({bot.JOB_CARD_XPATHS[0]: [first, duplicate, hidden]})
    assert bot.find_job_cards(driver) == [first]


# ------------------------------ text fallbacks ------------------------------------

def test_react_card_details_are_parsed_from_lines(bot):
    lines = [
        "Java Developer - Workplace Services Engineering",
        "Charles Schwab",
        "Austin, Texas, United States (Hybrid)",
    ]
    company, location, work_style = bot._card_details_from_lines(lines, lines[0])
    assert company == "Charles Schwab"
    assert location == "Austin, Texas, United States (Hybrid)"
    assert work_style == "Unknown"       # "(Hybrid)" is split out by get_job_main_details


def test_get_job_main_details_reads_a_react_card(bot, monkeypatch):
    card = FakeCard(
        {"componentkey": "job-card-component-ref-4481055232"},
        text=("Java Developer - Workplace Services Engineering\n"
              "Charles Schwab\n"
              "Austin, Texas, United States (Hybrid)\n"
              "Easy Apply"),
    )
    opened = []
    monkeypatch.setattr(bot, "driver", object())
    monkeypatch.setattr(bot, "scroll_to_view", lambda *a, **k: None)
    monkeypatch.setattr(bot, "open_job_details",
                        lambda job, job_id, clickable: opened.append((job_id, clickable)))
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: None)

    job_id, title, company, location, style, skip = bot.get_job_main_details(card, set(), set())

    assert job_id == "4481055232"
    assert title == "Java Developer - Workplace Services Engineering"
    assert company == "Charles Schwab"
    assert location == "Austin, Texas, United States"
    assert style == "Hybrid"
    assert skip is False
    assert opened == [("4481055232", None)]     # React cards open by URL, not click


def test_company_and_location_on_one_line_are_split(bot):
    company, location, _ = bot._card_details_from_lines(
        ["Backend Engineer", "Acme · Berlin, Germany (Remote)"], "Backend Engineer")
    assert company == "Acme"
    assert location == "Berlin, Germany (Remote)"


def test_react_card_has_no_click_target(bot):
    card = FakeCard(
        {"componentkey": "job-card-component-ref-4481055232"},
        text="Java Developer\nCharles Schwab\nAustin, Texas, United States (Hybrid)",
    )
    assert bot._first_displayed_in(card, bot.JOB_TITLE_XPATHS) is None
    assert bot._is_react_job_card(card) is True


def test_decorative_link_does_not_override_react_card_url_opening(bot):
    '''Even if a render includes an <a>, the React card must still be opened by URL.'''
    card = FakeCard({"componentkey": "job-card-component-ref-4481055232"})
    assert bot._is_react_job_card(card) is True
    assert bot._is_react_job_card(FakeCard({"data-occludable-job-id": "4460606885"})) is False


# ------------------------------ opening by URL ------------------------------------

def test_react_card_is_opened_with_current_job_id(bot, monkeypatch):
    class UrlDriver:
        current_url = "https://www.linkedin.com/jobs/search/?keywords=Java&f_AL=true"

        def __init__(self):
            self.got = None

        def get(self, url):
            self.got = url

    fake_driver = UrlDriver()
    monkeypatch.setattr(bot, "driver", fake_driver)
    monkeypatch.setattr(bot, "wait_for_job_details_ready", lambda *a, **k: True)

    bot.open_job_by_id("4481055232")

    assert fake_driver.got.startswith("https://www.linkedin.com/jobs/search/?")
    assert "currentJobId=4481055232" in fake_driver.got
    assert "keywords=Java" in fake_driver.got       # filters/query survive
    assert "f_AL=true" in fake_driver.got


def test_open_job_details_falls_back_to_url_when_card_has_no_link(bot, monkeypatch):
    opened = []
    monkeypatch.setattr(bot, "open_job_by_id", opened.append)

    bot.open_job_details(FakeCard(), "4481055232", None)

    assert opened == ["4481055232"]
