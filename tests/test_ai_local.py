'''
Tests for the local AI answer layer: modules/ai/local.py, cache.py, fit.py.

Everything here runs against a STUB - no network, no server, no model. That is
not a convenience, it is the specification: the layer has to behave correctly
with nothing listening on :1234, because that is its normal state.

What is pinned here:
  * the wire shape (enable_thinking off, json_schema constrained decoding,
    per-tier max_tokens) - it is a request body, so it is testable offline;
  * graceful degradation - every way a server can fail returns None, never raises;
  * the SAFETY INVARIANT - an AI proposal that the deterministic validator
    rejects leaves the control untouched, and AI may only ADD job skips;
  * the never-guess property across the whole golden set.

The golden set is also replayed against the REAL model by the __main__ block at
the bottom, which pytest never runs:  python tests/test_ai_local.py

License: MIT  (https://opensource.org/license/mit)
'''

import io
import json
import os
import sys
import types
import urllib.error

import pytest

from modules.ai import cache, fit, local


GOLDEN_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "07_easy_apply_questions.json")
GOLDEN = json.load(open(GOLDEN_PATH, encoding="utf-8"))
QUESTIONS = GOLDEN["questions"]
FACTS = local.profile_block(GOLDEN["persona"])
CHOOSABLE = [q for q in QUESTIONS if q["type"] in ("select", "radio")]


@pytest.fixture(scope="module")
def validator():
    '''runAiBot's real `match_answer_to_option`, with a stubbed browser session so
    importing it never opens Chrome. The AI layer is tested against the REAL
    validator: a stub one would prove nothing about the invariant.'''
    fake_chrome = types.ModuleType("modules.open_chrome")
    fake_chrome.options = fake_chrome.driver = fake_chrome.actions = fake_chrome.wait = None
    sys.modules.setdefault("modules.open_chrome", fake_chrome)
    import runAiBot
    return runAiBot.match_answer_to_option


@pytest.fixture(autouse=True)
def temp_cache(tmp_path, monkeypatch):
    '''Never touch the real .ai_answer_cache.json.'''
    monkeypatch.setattr(cache, "PATH", str(tmp_path / "answers.json"))
    monkeypatch.setattr(cache, "_data", None)
    yield
    monkeypatch.setattr(cache, "_data", None)


class Ask:
    '''Stub for `local._chat`. Returns a scripted reply and counts calls.'''
    def __init__(self, reply=None):
        self.reply, self.calls = reply, []

    def __call__(self, system, user, schema, tier):
        self.calls.append({"system": system, "user": user, "schema": schema, "tier": tier})
        return self.reply(self.calls[-1]) if callable(self.reply) else self.reply


# ----------------------------------------------------------------- golden set
def test_golden_set_is_well_formed():
    assert len(QUESTIONS) >= 25
    assert sum(1 for q in QUESTIONS if q["expect"] is None) >= 5, "need several must-not-answer cases"
    assert {q["type"] for q in QUESTIONS} == {"select", "radio", "text", "textarea", "checkbox"}
    for q in QUESTIONS:
        assert q["q"] and q["why"], q
        if q["type"] in ("select", "radio"):
            assert len(q["options"]) >= 2, q
            assert q["expect"] is None or q["expect"] in q["options"], q


def test_golden_set_carries_no_real_personal_data():
    '''LM Studio logs prompts to disk and this repo is public. The fixture persona
    is fictional; a real name or address leaking in here would ship publicly.'''
    blob = json.dumps(GOLDEN).lower()
    for real in ("sai", "golla", "vignesh", "fremont", "savign", "h-1b", "h1b"):
        assert real not in blob, f"real personal data {real!r} in the golden fixture"


# ------------------------------------------------------------------ wire shape
def _capture(monkeypatch, response=None, error=None):
    '''Intercept the single urlopen call and hand back the Request that was built.'''
    seen = {}

    def fake_urlopen(request, timeout=None):
        seen["request"] = request
        seen["timeout"] = timeout
        seen["body"] = json.loads(request.data.decode())
        if error:
            raise error
        return io.BytesIO(json.dumps(response).encode())

    monkeypatch.setattr(local.urllib.request, "urlopen", fake_urlopen)
    return seen


def _ok(content):
    return {"choices": [{"message": {"content": json.dumps(content)}}]}


def test_request_disables_thinking_and_constrains_decoding(monkeypatch):
    seen = _capture(monkeypatch, _ok({"o": "1"}))
    local.answer_select("Authorized to work?", ["Yes", "No"], lambda a, o: 0 if a else None, FACTS)
    body = seen["body"]
    # Measured: thinking ON burned all 300 tokens without finishing the JSON.
    assert body["chat_template_kwargs"] == {"enable_thinking": False}
    # Constrained decoding, not politeness - a 4B asked nicely for JSON drifts.
    assert body["response_format"]["type"] == "json_schema"
    assert body["response_format"]["json_schema"]["strict"] is True
    assert body["temperature"] == 0
    assert seen["request"].full_url.endswith("/v1/chat/completions")


def test_tier1_caps_tokens_and_enumerates_the_real_options(monkeypatch):
    seen = _capture(monkeypatch, _ok({"o": "2"}))
    local.answer_select("Pick one", ["Alpha", "Beta", "Gamma"], lambda a, o: o.index(a) if a in o else None, FACTS)
    assert seen["body"]["max_tokens"] == local.TIERS[1][0] == 8      # ~1-5 generated tokens
    assert seen["timeout"] == local.TIERS[1][1]
    # The grammar itself makes an out-of-range or free-text answer impossible.
    assert seen["body"]["response_format"]["json_schema"]["schema"]["properties"]["o"]["enum"] \
        == ["1", "2", "3", "NONE"]


def test_tier2_and_tier3_have_their_own_caps(monkeypatch):
    seen = _capture(monkeypatch, _ok({"a": "6"}))
    local.answer_text("Years of experience?", FACTS)
    assert seen["body"]["max_tokens"] == local.TIERS[2][0]

    seen = _capture(monkeypatch, _ok({"t": "letter"}))
    local.answer_long("cover letter", "Acme", FACTS, "a" * 9000)
    assert seen["body"]["max_tokens"] == local.TIERS[3][0]
    assert len(seen["body"]["messages"][1]["content"]) < 3000, "job description must be truncated"


def test_static_prefix_is_identical_across_calls():
    '''LM Studio caches repeated prompt PREFIXES. The per-tier system prompt must be
    byte-identical every call and the variable tail must come last, or the saving
    is destroyed and every call pays full prefill.'''
    ask = Ask({"o": "NONE"})
    for q in CHOOSABLE:
        local.answer_select(q["q"], q["options"], lambda a, o: None, FACTS, ask=ask)
    assert len({c["system"] for c in ask.calls}) == 1, "system prompt varies between calls"
    for call in ask.calls:
        assert call["user"].startswith(FACTS), "variable text must follow the static profile block"
        assert "Options:" in call["user"] and call["user"].index("Question:") < call["user"].index("Options:")


def test_prompts_carry_no_format_boilerplate():
    '''The json_schema grammar enforces shape, so paying prompt tokens to ask for it
    would be paying twice. Prefill is ~158 tok/s; every prompt token is billed on
    every call.'''
    for prompt in (local.local_select_system, local.local_text_system, local.local_long_system):
        low = prompt.lower()
        for wasted in ("json", "markdown", "```", "do not restate", "step by step", "think"):
            assert wasted not in low, f"{wasted!r} is dead prompt weight under a grammar"
    assert "truthful" in local.local_select_system.lower()
    assert "truthful" in local.local_text_system.lower()


# --------------------------------------------------------- graceful degradation
@pytest.mark.parametrize("kind, response, error", [
    ("server down",      None, urllib.error.URLError("connection refused")),
    ("timeout",          None, TimeoutError("timed out")),
    ("http 500",         None, urllib.error.HTTPError("u", 500, "boom", {}, None)),
    ("not json",         {"choices": [{"message": {"content": "I think the answer is Yes!"}}]}, None),
    ("json but a list",  {"choices": [{"message": {"content": "[1,2]"}}]}, None),
    ("empty content",    {"choices": [{"message": {"content": None}}]}, None),
    ("no choices",       {"error": "model not loaded"}, None),
])
def test_every_failure_degrades_to_no_answer(monkeypatch, kind, response, error, validator):
    '''A down server, a hang, or garbage must all become "no answer" and never an
    exception into the apply loop, and never a guess.'''
    _capture(monkeypatch, response, error)
    assert local.answer_select("Authorized?", ["Yes", "No"], validator, FACTS) is None, kind
    assert local.answer_text("Years?", FACTS) is None, kind
    assert local.answer_long("cover letter", "Acme", FACTS) is None, kind
    assert local.score_fit("a job", FACTS) is None, kind


def test_a_broken_cache_file_is_not_a_broken_bot(monkeypatch, tmp_path):
    path = tmp_path / "answers.json"
    path.write_text("{ this is not json")
    monkeypatch.setattr(cache, "PATH", str(path))
    monkeypatch.setattr(cache, "_data", None)
    assert cache.get("anything") is cache.MISS


def test_an_unwritable_cache_is_not_a_broken_bot(monkeypatch):
    monkeypatch.setattr(cache, "PATH", "/nonexistent-dir/answers.json")
    monkeypatch.setattr(cache, "_data", None)
    cache.put("q", "a")                      # must not raise
    assert cache.get("q") == "a"             # still served from memory this run


# ------------------------------------------------------- THE SAFETY INVARIANT
def test_ai_proposal_the_validator_rejects_leaves_the_control_untouched(validator):
    '''AI proposes, the deterministic validator disposes. A proposal that maps to no
    real option must return None - the same None the config ladder produces, which
    the apply loop already handles by leaving the control alone and reporting it.'''
    options = ["Yes", "No"]
    assert local.answer_select("Authorized?", options, validator, FACTS,
                               ask=Ask({"o": "1"})) == 0
    # Distinct questions per case on purpose: one question reused here would be served
    # by the cache from the first call and never reach the validator at all.
    # A server that ignores the enum and invents a value: rejected, not written.
    for label, reply in [("free text", "Maybe, it depends"), ("past the end", "7"),
                         ("off by one", "0"), ("empty", ""), ("not a string", None)]:
        assert local.answer_select(f"Authorized? ({label})", options, validator, FACTS,
                                   ask=Ask({"o": reply})) is None, label


def test_the_validator_also_guards_a_hand_edited_cache(validator):
    '''The cache file is meant to be edited by hand, so it is an input the validator
    must police too - not a trusted store that bypasses it.'''
    question = "What is your citizenship status?"
    options = ["U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer"]
    cache.put(question, "Klingon Citizen", options)          # a human typo, or a bad edit
    ask = Ask({"o": "1"})
    assert local.answer_select(question, options, validator, FACTS, ask=ask) is None
    assert ask.calls == [], "a cache hit must not cost a model call, even a rejected one"


def test_none_from_the_model_never_becomes_a_guess(validator):
    '''The whole golden set under a model that refuses: every control untouched.'''
    for q in CHOOSABLE:
        assert local.answer_select(q["q"], q["options"], validator, FACTS,
                                   ask=Ask({"o": "NONE"})) is None, q["q"]
    for q in QUESTIONS:
        if q["type"] in ("text", "textarea"):
            assert local.answer_text(q["q"], FACTS, ask=Ask({"a": "NONE"})) is None, q["q"]
            assert local.answer_text(q["q"], FACTS, ask=Ask({"a": "  "})) is None, q["q"]


def test_a_correct_model_maps_onto_the_real_option_text(validator):
    '''The other half: when the model does pick the expected option, the validator
    passes it through and the index points at the right option.'''
    for q in CHOOSABLE:
        if q["expect"] is None:
            continue
        wanted = q["options"].index(q["expect"])
        got = local.answer_select(q["q"], q["options"], validator, FACTS,
                                  ask=Ask({"o": str(wanted + 1)}))
        assert got is not None and q["options"][got] == q["expect"], q["q"]


@pytest.mark.parametrize("deterministic, ai_score, expected", [
    (True,  100, True),    # deterministic skip stands even on a perfect AI score
    (True,    0, True),
    (False,   0, True),    # AI may ADD a skip
    (False, 100, False),
])
def test_ai_can_only_add_skips_never_remove_one(deterministic, ai_score, expected):
    '''`skip = deterministic_skip or ai_skip`. Never `and`. A 4B local model must not
    be able to un-skip a job the citizenship / clearance / sponsorship filters
    rejected - that is the failure that sent a CV to a role requiring US
    citizenship.'''
    skip, _ = fit.should_skip(deterministic, "a job description", FACTS,
                              min_score=50, scorer=lambda jd, f: (ai_score, "because"))
    assert skip is expected


def test_a_deterministic_skip_costs_no_model_time():
    calls = []
    skip, _ = fit.should_skip(True, "jd", FACTS, min_score=50,
                              scorer=lambda jd, f: calls.append(1) or (0, ""))
    assert skip is True and calls == []


@pytest.mark.parametrize("scorer", [
    lambda jd, f: None,                       # server down / unparseable
    lambda jd, f: (0, "terrible"),            # a real low score, but scoring is off
])
def test_scoring_is_off_by_default(scorer):
    '''min_score defaults to 0: fit scoring is advisory until the user opts in, so
    adding this module changes no existing behaviour.'''
    assert fit.should_skip(False, "jd", FACTS, scorer=scorer)[0] is False


def test_an_unscoreable_job_is_never_skipped_on_that_basis():
    assert fit.should_skip(False, "jd", FACTS, min_score=90, scorer=lambda jd, f: None)[0] is False


@pytest.mark.parametrize("reply", [
    {"s": "eighty", "r": "x"}, {"s": 101, "r": "x"}, {"s": -1, "r": "x"},
    {"s": True, "r": "x"}, {"r": "no score at all"}, {},
])
def test_a_fit_parse_failure_is_none_not_a_wrong_score(reply):
    assert local.score_fit("jd", FACTS, ask=Ask(reply)) is None


def test_a_valid_fit_score_parses():
    assert local.score_fit("jd", FACTS, ask=Ask({"s": 82, "r": "python and distributed systems"})) \
        == (82, "python and distributed systems")


# ------------------------------------------------------------------- the cache
def test_a_cache_hit_costs_zero_model_time(validator):
    ask = Ask({"o": "1"})
    assert local.answer_select("Authorized?", ["Yes", "No"], validator, FACTS, ask=ask) == 0
    assert len(ask.calls) == 1
    assert local.answer_select("Authorized?", ["Yes", "No"], validator, FACTS, ask=ask) == 0
    assert len(ask.calls) == 1, "the second identical question must not reach the model"


def test_the_same_question_with_different_options_is_a_different_entry():
    ask = Ask({"a": "6"})
    local.answer_text("Years of experience?", FACTS, ask=ask)
    assert cache.get("Years of experience?", ["0-1", "2-5"]) is cache.MISS
    assert cache.get("Years of experience?") == "6"


def test_question_text_is_normalised_but_not_conflated():
    '''LinkedIn decorates required labels with * and varies whitespace.'''
    assert cache.key("How many years?  *") == cache.key("how many   YEARS?")
    assert cache.key("How many years?") != cache.key("How many months?")


def test_a_no_answer_result_is_cached_and_stays_readable(validator):
    '''Stored as null, not dropped: it stops the bot re-asking an unanswerable
    question on every job, and the null entries are the worklist of questions
    worth answering in config/questions.py.'''
    ask = Ask({"o": "NONE"})
    local.answer_select("Do you hold a clearance?", ["Yes", "No"], validator, FACTS, ask=ask)
    local.answer_select("Do you hold a clearance?", ["Yes", "No"], validator, FACTS, ask=ask)
    assert len(ask.calls) == 1
    stored = json.load(open(cache.PATH, encoding="utf-8"))
    key = next(iter(stored))
    assert stored[key] is None
    assert "do you hold a clearance" in key, "keys must stay greppable by question text"


def test_the_cache_file_is_not_world_readable():
    '''It holds the user's own answers: salary, visa status, EEO responses.'''
    local.answer_text("Expected salary?", FACTS, ask=Ask({"a": "185000"}))
    assert oct(os.stat(cache.PATH).st_mode)[-3:] == "600"


def test_the_cache_is_gitignored():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert ".ai_answer_cache.json" in open(os.path.join(root, ".gitignore"), encoding="utf-8").read()


# --------------------------------------------------------------- profile block
def test_the_profile_block_is_compact_and_literal():
    '''Contact facts are passed literally, never left for the model to recall - four
    of five model configs invented an email and the wrong city when the block was
    missing. And it stays small: every token is paid on every call.'''
    assert "Jordan Mercer" in FACTS and "Portland" in FACTS
    assert len(FACTS) < 700, "the profile block is prefill paid on every single call"
    assert "cover" not in FACTS.lower() and "summary" not in FACTS.lower()


def test_the_profile_block_drops_empty_fields():
    assert local.profile_block({"A": "1", "B": "", "C": None, "D": "Unknown"}) == "A: 1"


# =========================================================================== #
# Replay the golden set against the REAL model. pytest never runs this.
#     python tests/test_ai_local.py [base_url]
# =========================================================================== #
def _replay(base_url=None):
    import tempfile, time
    if base_url:
        local._cfg_get = lambda name, default: base_url if name == "local_llm_api_url" else default
    cache.PATH = os.path.join(tempfile.mkdtemp(), "replay.json")   # a cold cache, or we grade the cache
    cache._data = None

    fake_chrome = types.ModuleType("modules.open_chrome")
    fake_chrome.options = fake_chrome.driver = fake_chrome.actions = fake_chrome.wait = None
    sys.modules.setdefault("modules.open_chrome", fake_chrome)
    import runAiBot

    right = wrong = 0
    started = time.time()
    for q in QUESTIONS:
        began = time.time()
        if q["type"] in ("select", "radio"):
            index = local.answer_select(q["q"], q["options"], runAiBot.match_answer_to_option, FACTS)
            got = q["options"][index] if index is not None else None
            ok = got == q["expect"]
        elif q["type"] == "checkbox":
            got, ok = None, q["expect"] is None      # checkboxes are never auto-ticked, no model involved
        else:
            got = local.answer_text(q["q"], FACTS)
            ok = (got is None) if q["expect"] is None else bool(got and q["expect"].lower() in got.lower())
        right, wrong = right + ok, wrong + (not ok)
        print(f'{"PASS" if ok else "FAIL"}  {time.time()-began:5.1f}s  {q["q"][:58]:<58}  '
              f'got={str(got)[:34]!r:<36} want={str(q["expect"])[:26]!r}')
    total = len(QUESTIONS)
    print(f"\n{right}/{total} correct ({100*right//total}%), {wrong} wrong, {time.time()-started:.0f}s total")
    print("The NONE cases are the ones that matter: a wrong answer there is a lie on a real application.")


if __name__ == "__main__":
    _replay(sys.argv[1] if len(sys.argv) > 1 else None)
