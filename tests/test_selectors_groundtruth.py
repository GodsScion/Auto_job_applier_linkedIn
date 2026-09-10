'''
Selector regression net, checked against LinkedIn markup captured from a live logged-in
session on 2026-09-09 (`tests/fixtures/*.html`).

Every assertion here is "the locator the bot uses today matches the real page", or "a
locator we know is dead has not crept back into the source". When LinkedIn moves again,
recapture the fixtures and this file tells you exactly which locators died.

Stdlib only - `html.parser`. lxml and bs4 are not dependencies of this project.

License: MIT  (https://opensource.org/license/mit)
'''

import inspect
import os
import sys
import tokenize
import types
from html.parser import HTMLParser

import pytest


FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}


# --- the smallest DOM that can answer "does this locator match?" -------------------

class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.kids, self.texts = tag, dict(attrs), parent, [], []

    def attr(self, name):
        return self.attrs.get(name)

    def classes(self):
        '''Class *tokens*. CSS/`By.CLASS_NAME` matching is exact-token, not substring.'''
        return set((self.attrs.get("class") or "").split())

    def text(self):
        '''XPath `normalize-space(.)`: this node's text plus every descendant's.'''
        return " ".join("".join(self._raw()).split())

    def _raw(self):
        out = list(self.texts)
        for k in self.kids:
            out += k._raw()
        return out

    def walk(self):
        for k in self.kids:
            yield k
            yield from k.walk()


class _Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#document", {}, None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.kids.append(node)
        if tag not in VOID_TAGS:
            self.cur = node

    def handle_endtag(self, tag):
        node = self.cur
        while node.parent is not None and node.tag != tag:
            node = node.parent
        if node.parent is not None:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.texts.append(data)


def parse(name):
    tree = _Tree()
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        tree.feed(f.read())
    return tree.root


def find(root, tag=None, **preds):
    '''Nodes matching `tag` and every predicate. Predicates are callables on the node.'''
    hits = []
    for n in root.walk():
        if tag and n.tag != tag:
            continue
        if all(p(n) for p in preds.values()):
            hits.append(n)
    return hits


# `By.CLASS_NAME` / CSS `.x` - exact token.
def cls(token):
    return lambda n: token in n.classes()


# XPath `contains(@class, 'x')` - substring, matches partial tokens too.
def cls_contains(sub):
    return lambda n: sub in (n.attrs.get("class") or "")


def attr(name, value=None):
    return lambda n: name in n.attrs and (value is None or n.attrs[name] == value)


@pytest.fixture(scope="module")
def bot():
    '''runAiBot with a stubbed browser session, so importing it never opens Chrome.'''
    fake_chrome = types.ModuleType("modules.open_chrome")
    fake_chrome.options = fake_chrome.driver = fake_chrome.actions = fake_chrome.wait = None
    sys.modules["modules.open_chrome"] = fake_chrome
    import runAiBot
    return runAiBot


@pytest.fixture(scope="module")
def sources():
    '''
    Source of the two selector-carrying modules with `#` comments stripped, so a dead
    selector *named in a comment* (this file's own history is full of them) doesn't
    fail the "it never came back" tests. String literals are kept - that is where
    locators live.
    '''
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = {}
    for rel in ("runAiBot.py", os.path.join("modules", "clickers_and_finders.py")):
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            # untokenize() rebuilds from the original positions, so the remaining code
            # keeps its exact spelling - the "did it come back" checks stay meaningful.
            kept = [t for t in tokenize.generate_tokens(f.readline) if t.type != tokenize.COMMENT]
        out[rel] = tokenize.untokenize(kept)
    return out


def test_source_fixture_is_not_vacuous(sources):
    '''Guard for every `not in sources[...]` assertion below: code text must survive.'''
    assert "By.CSS_SELECTOR, login_email_css" in sources["runAiBot.py"]
    assert "def pick_first_displayed" in sources[os.path.join("modules", "clickers_and_finders.py")]


# =================================================================================
# 1. LOGIN  (05_login_page.html) - the React rewrite that broke login outright
# =================================================================================

@pytest.fixture(scope="module")
def login():
    return parse("05_login_page.html")


def test_login_dead_locators_are_really_dead(login):
    '''Everything the bot used to log in with returns nothing on the real page.'''
    assert find(login, "input", i=attr("id", "username")) == []
    assert find(login, "input", i=attr("id", "password")) == []
    assert find(login, "input", n=attr("name", "session_key")) == []
    assert find(login, "form") == []
    assert find(login, "button", t=attr("type", "submit")) == []
    # ids are React useId() values, regenerated every render - never usable.
    ids = [n.attr("id") for n in find(login, "input") if n.attr("id")]
    assert ids and all("«" in i for i in ids), ids
    assert all(not n.attr("name") for n in find(login, "input"))


def test_login_field_locators_match(login):
    '''`input[type=email]` / `input[type=password]`, with the hidden duplicate set.'''
    emails = find(login, "input", t=attr("type", "email"))
    passwords = find(login, "input", t=attr("type", "password"))
    assert len(emails) == 2 and len(passwords) == 2      # 1 real + 1 hidden duplicate each
    assert len(find(login, "input")) == 6                # + 2 checkboxes


def test_sign_in_button_needs_an_exact_text_match(login):
    '''
    The whole point of the exact match: "Sign in with Apple" sits ABOVE the real button,
    so `contains(., "Sign in")` picks the Apple SSO button and login never happens.
    '''
    contains = [n for n in find(login, "button") if "Sign in" in n.text()]
    exact = [n for n in find(login, "button") if n.text() == "Sign in"]
    assert len(contains) == 4 and len(exact) == 2
    assert contains[0].text() == "Sign in with Apple"    # <- what contains() would click
    assert all(n.attr("type") == "button" for n in exact)


def test_forgot_password_link_still_gates_the_login_wait(login):
    '''login_LN() waits on this LINK_TEXT before typing.'''
    assert [n for n in find(login, "a") if n.text() == "Forgot password?"]


def test_login_code_uses_the_measured_locators(bot):
    assert bot.login_email_css == "input[type='email']"
    assert bot.login_password_css == "input[type='password']"
    assert 'normalize-space(.)="Sign in"' in bot.sign_in_button_xpath
    assert "contains" not in bot.sign_in_button_xpath    # would grab "Sign in with Apple"
    assert 'type="submit"' not in bot.sign_in_button_xpath
    src = inspect.getsource(bot.fill_visible_input)
    assert "pick_first_displayed" in src                 # 4 of 6 inputs are hidden
    assert "human_type" in src


def test_login_source_has_no_dead_id_locators(sources):
    for name, src in sources.items():
        assert 'By.ID, "username"' not in src, name
        assert 'By.ID, "password"' not in src, name
        assert "session_key" not in src, name


# =================================================================================
# 2. JOB CARD  (01_job_card.html) - randomized class names
# =================================================================================

@pytest.fixture(scope="module")
def card():
    return parse("01_job_card.html")


def test_job_card_dead_classes_are_really_dead(card):
    assert find(card, c=cls("job-card-container__primary-description")) == []
    assert find(card, c=cls("job-card-container__metadata-item")) == []
    # Only `job-card-list__title--link` survives, and it is a different token.
    assert find(card, c=cls("job-card-list__title")) == []
    assert find(card, c=cls("job-card-list__title--link")) != []


def test_job_card_class_names_are_randomized(card):
    '''Proof that nothing may key off a class that is not semantic.'''
    company_span = find(card, "span", d=attr("dir", "ltr"), t=lambda n: n.text() == "TechNovaTime")
    assert len(company_span) == 1
    assert company_span[0].classes() == {"pkXTSOjuybKaxMNVefkdwtUQOqEFHJfJW"}


def test_job_card_title_anchor_matches(card):
    '''`.//div[contains(@class,'artdeco-entity-lockup__title')]//a`'''
    titles = find(card, c=cls_contains("artdeco-entity-lockup__title"))
    links = [a for t in titles for a in find(t, "a")]
    assert len(links) == 1
    aria = links[0].attr("aria-label")
    assert aria == "Forward Deployed Engineer with verification"
    # Exactly what get_job_main_details() does with it.
    assert aria.split("\n")[0].removesuffix(" with verification").strip() == "Forward Deployed Engineer"


def test_job_card_company_and_location_anchors_match(card):
    subtitles = find(card, c=cls_contains("artdeco-entity-lockup__subtitle"))
    assert len(subtitles) == 1 and subtitles[0].text() == "TechNovaTime"
    # The subtitle no longer carries "Company · Location (Style)" - the old split is dead.
    assert " · " not in subtitles[0].text()

    wrappers = find(card, "ul", c=cls_contains("job-card-container__metadata-wrapper"))
    assert len(wrappers) == 1
    spans = find(wrappers[0], "span", d=attr("dir", "ltr"))
    assert spans and spans[0].text() == "New York, United States (Hybrid)"

    work_location = spans[0].text()
    work_style = work_location[work_location.rfind("(") + 1:work_location.rfind(")")]
    assert work_style == "Hybrid"
    assert work_location[:work_location.rfind("(")].strip() == "New York, United States"


def test_job_card_stable_anchors_still_present(card):
    assert find(card, "li", d=attr("data-occludable-job-id")) != []
    assert find(card, c=cls("job-card-container__footer-job-state")) != []
    # The card-level Easy Apply flag, for the cheap pre-filter.
    footers = find(card, "ul", c=cls_contains("footer-wrapper"))
    assert [s for f in footers for s in find(f, "span") if s.text() == "Easy Apply"]


def test_job_card_source_has_no_dead_classes(sources):
    for name, src in sources.items():
        assert "job-card-container__primary-description" not in src, name
        assert "job-card-container__metadata-item" not in src, name
        assert "job-card-list__title" not in src, name


# =================================================================================
# 3. APPLY BUTTON  (04_apply_button.html) - "Easy" was never dropped
# =================================================================================

@pytest.fixture(scope="module")
def apply_btn():
    return find(parse("04_apply_button.html"), "button")[0]


def test_apply_button_still_says_easy_apply(apply_btn):
    '''The widely repeated "LinkedIn dropped Easy from the aria-label" claim is FALSE.'''
    assert apply_btn.attr("aria-label") == "Easy Apply to Forward Deployed Engineer at TechNovaTime"
    assert "Easy Apply" in apply_btn.attr("aria-label")
    assert apply_btn.text() == "Easy Apply"


def test_apply_button_carries_every_anchor_the_locator_list_uses(apply_btn):
    assert apply_btn.attr("id") == "jobs-apply-button-id"
    assert "jobs-apply-button" in apply_btn.classes()
    assert "artdeco-button--3" in apply_btn.classes()     # present, but a SIZE token - unused


def test_easy_apply_locator_order(bot):
    anchors = [xp for _, xp in bot.easy_apply_locators]
    assert "jobs-apply-button-id" in anchors[0] or "jobs-apply-button-id" in anchors[1]
    assert any("Easy Apply" in xp for xp in anchors)
    assert all("artdeco-button--3" not in xp for xp in anchors)
    assert "jobs-apply-button-id" in bot.apply_button_xpath
    assert "artdeco-button--3" not in bot.apply_button_xpath


def test_no_selector_keys_off_the_button_size_token(sources):
    for name, src in sources.items():
        assert "artdeco-button--3" not in src, name


# =================================================================================
# 4/5. EASY APPLY MODAL  (06_easy_apply_modal.html)
# =================================================================================

@pytest.fixture(scope="module")
def modal():
    return parse("06_easy_apply_modal.html")


def test_modal_container_anchors(modal):
    dialogs = find(modal, "div", r=attr("role", "dialog"))
    assert len(dialogs) == 1
    assert "jobs-easy-apply-modal" in dialogs[0].classes()
    assert "data-test-modal" in dialogs[0].attrs
    assert find(modal, d=attr("data-test-modal-close-btn")) != []


def test_form_element_anchor_replaced_the_dead_class(modal):
    assert find(modal, c=cls("jobs-easy-apply-form-element")) == []
    assert find(modal, c=cls("fb-dash-form-element")) != []      # ...but paired with a random class
    assert len(find(modal, "div", f=attr("data-test-form-element"))) == 3


def test_question_component_anchors_still_work(modal):
    assert len(find(modal, d=attr("data-test-text-entity-list-form-component"))) == 2
    assert len(find(modal, d=attr("data-test-single-line-text-form-component"))) == 1
    assert len(find(modal, "input", n=attr("name", "file"))) == 1
    assert find(modal, "input", i=attr("id", "follow-company-checkbox")) != []


def test_submit_button_is_type_button_not_submit(modal):
    submits = find(modal, "button", a=attr("aria-label", "Submit application"))
    assert len(submits) == 1
    assert submits[0].attr("type") == "button"        # button[type=submit] finds nothing
    assert submits[0].text() == "Submit application"


def test_next_and_review_lookups_are_scoped_to_the_dialog(bot, modal):
    '''
    The captured application was single page: no Next, no Review inside the modal. A
    document-wide search for "Next" matched the pagination control instead, so every
    Next/Review/Submit lookup must be scoped to the dialog element.
    '''
    assert [n for n in find(modal, "button") if "Next" in n.text()] == []
    assert [n for n in find(modal, "button") if "Review" in n.text()] == []

    src = inspect.getsource(bot.apply_to_jobs)
    for xpath in (bot.next_button_xpath, bot.review_button_xpath, bot.submit_button_xpath):
        assert xpath.startswith(".//")                        # relative, not document-wide
    for const in ("next_button_xpath", "review_button_xpath", "submit_button_xpath"):
        for call in ("wait_xp_click(modal, %s" % const, "modal.find_element(By.XPATH, %s" % const):
            if call in src:
                break
        else:
            pytest.fail("%s is not scoped to the modal" % const)
    assert 'wait_span_click(driver, "Submit application"' not in src
    assert 'wait_span_click(driver, "Review"' not in src


def test_modal_source_has_no_dead_form_class(sources):
    for name, src in sources.items():
        assert "jobs-easy-apply-form-element" not in src, name


# =================================================================================
# 6. Radio / textarea handling is untouched: absence of evidence, not removal
# =================================================================================

def test_radio_and_textarea_handling_is_left_alone(sources, modal):
    '''
    The captured form held 2 selects and 1 text input - no radios, no textarea. That is
    not evidence LinkedIn removed them, so their handling must stay in the code.
    '''
    assert find(modal, "textarea") == []
    assert find(modal, d=attr("data-test-form-builder-radio-button-form-component")) == []
    src = sources["runAiBot.py"]
    assert "data-test-form-builder-radio-button-form-component" in src
    assert ".//textarea" in src
