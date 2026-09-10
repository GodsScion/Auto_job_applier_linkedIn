'''
The AI answer layer wired into `answer_questions`, and the answer memory.

Two properties are under test and neither needs a model server - :1234 being down is
the normal case, not the exception:

  * the LADDER. config/questions.py is tier 0 and must stay the common case; the answer
    file, then the local model, then the existing cloud client are only reached where
    that ladder produced nothing. AI proposes, `match_answer_to_option` disposes, and a
    proposal it rejects leaves the control untouched exactly as before.
  * the ANSWER MEMORY. Every question nothing could answer is written to
    .ai_answer_cache.json with its type and options; answering it there by hand answers
    it on the next run with no model call, through the same validator.

The never-guess invariant itself is pinned in tests/test_question_matching.py. This file
is about not having broken it while adding a path above it.

License: MIT  (https://opensource.org/license/mit)
'''

import json

import pytest

from modules.ai import cache, local
# The fake DOM these branches are driven through already exists; rebuilding it here would
# be a second copy to keep in step with LinkedIn's markup.
from test_question_matching import (bot, dropdown, radio_group, text_question,
                                    textarea_question, checkbox_question)


class Model:
    '''Stands in for `local._chat`: a scripted reply, and a count of what it cost.'''

    def __init__(self, reply=None):
        self.reply, self.calls = reply, []

    def __call__(self, system, user, schema, tier):
        self.calls.append(user)
        return self.reply


@pytest.fixture
def model(bot, monkeypatch):
    '''AI on, with the local server replaced by a stub that answers nothing.'''
    monkeypatch.setattr(bot, "use_AI", True)
    stub = Model()
    monkeypatch.setattr(local, "_chat", stub)
    return stub


def use(model, reply):
    model.reply = reply
    return model


# --------------------------------------------------------------- tier 0 stays tier 0
@pytest.mark.parametrize("question, options", [
    ("Are you currently legally authorized to work in the United States?",
     ["Select an option", "Yes", "No"]),
    ("What is your citizenship status?",
     ["Select an option", "U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer"]),
])
def test_a_question_config_answers_never_reaches_the_model(bot, monkeypatch, model,
                                                           question, options):
    '''The whole cost model. Every question the deterministic ladder answers has to cost
    zero model time, or a form of 20 questions is 20 generations on every job.'''
    monkeypatch.setattr(bot, "legally_authorized", "Yes")
    monkeypatch.setattr(bot, "us_citizenship", "Non-citizen allowed to work for any employer")
    modal, select = dropdown(bot, monkeypatch, question, options)

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked is not None
    assert model.calls == [], f'paid a model call for "{question}", which config answers'


def test_a_configured_text_answer_never_reaches_the_model(bot, monkeypatch, model):
    monkeypatch.setattr(bot, "phone_number", "5551234567")
    monkeypatch.setattr(bot, "use_AI", True)        # text_question() turns it off
    modal, field = text_question(bot, monkeypatch, "What is your phone number?")
    monkeypatch.setattr(bot, "use_AI", True)

    bot.answer_questions(modal, set(), "Remote")

    assert field.value == "5551234567" and model.calls == []


def test_the_fact_block_is_built_once_per_run_not_per_question(bot, monkeypatch, model):
    '''It is the static prefix of every prompt: rebuilding it per question would cost
    LM Studio's prefix cache far more than it could save.'''
    monkeypatch.setattr(local, "default_facts",
                        lambda: pytest.fail("facts rebuilt during the run"))
    use(model, {"o": "1"})
    modal, _, _ = radio_group(bot, monkeypatch, "Do you hold an active clearance?", ["Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert bot.FACTS and model.calls[0].startswith(bot.FACTS)


# ------------------------------------------------------- AI proposes, the validator disposes
def test_the_model_answers_a_dropdown_config_cannot(bot, monkeypatch, model):
    use(model, {"o": "1"})          # first REAL option: the placeholder is not offered
    modal, select = dropdown(bot, monkeypatch, "Do you have an active security clearance?",
                             ["Select an option", "Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked == "Yes"
    assert not bot.unanswered_questions


def test_the_model_is_never_offered_linkedins_placeholder(bot, monkeypatch, model):
    '''A 4B will pick "Select an option" if you let it, and a picked placeholder reads
    as answered while the form stays blocked.'''
    use(model, {"o": "1"})
    modal, select = dropdown(bot, monkeypatch, "Do you have an active security clearance?",
                             ["Select an option", "Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert "Select an option" not in model.calls[0]
    assert select.picked != "Select an option"


@pytest.mark.parametrize("reply", [
    {"o": "NONE"},                  # the model refuses, which is the honest answer
    {"o": "Maybe, it depends"},     # a server that ignores the enum
    {"o": "9"},                     # past the end of the option list
    None,                           # down, hung, or unparseable
])
def test_a_proposal_the_validator_rejects_leaves_the_dropdown_untouched(bot, monkeypatch,
                                                                        model, reply):
    '''The invariant, through the real apply path: AI may only ever propose. Anything
    `match_answer_to_option` will not confirm leaves the control alone and is reported.'''
    use(model, reply)
    modal, select = dropdown(bot, monkeypatch, "Do you have an active security clearance?",
                             ["Select an option", "Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked is None and select.selected == "Select an option"
    assert bot.unanswered_questions, "and it still has to be reported so the job is skipped"


def test_a_rejected_radio_proposal_clicks_nothing(bot, monkeypatch, model):
    use(model, {"o": "Yes please"})
    modal, mouse, _ = radio_group(bot, monkeypatch, "Do you hold an active clearance?",
                                  ["Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert mouse.clicked is None
    assert bot.unanswered_questions


def test_the_radio_question_the_model_sees_is_the_question_not_the_option_dump(bot, monkeypatch,
                                                                              model):
    '''`label_org` has the option list appended to it before the matcher runs, so the
    naive wiring asks the model \'Do you hold a clearance? [ "Yes"<urn..>, "No"<urn..>,\'
    and caches the answer under it.'''
    use(model, {"o": "NONE"})
    modal, _, _ = radio_group(bot, monkeypatch, "Do you hold an active clearance?", ["Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    asked = model.calls[0]
    assert "Question: Do you hold an active clearance?" in asked
    assert "urn" not in asked and "[ " not in asked.split("Options:")[0]


# ------------------------------------------------------------------ the down server
def test_a_down_server_costs_one_connection_for_the_whole_run(bot, monkeypatch):
    ''':1234 is normally not running. Without the short-circuit every question of every
    job pays another connect attempt, and a firewalled host pays it in seconds.'''
    attempts = []

    def refuse(request, timeout=None):
        attempts.append(request.full_url)
        raise local.urllib.error.URLError(ConnectionRefusedError(61, "Connection refused"))

    monkeypatch.setattr(bot, "use_AI", True)
    monkeypatch.setattr(local.urllib.request, "urlopen", refuse)

    for i in range(5):
        modal, select = dropdown(bot, monkeypatch, f"Unclassifiable question {i}?",
                                 ["Select an option", "Yes", "No"])
        bot.answer_questions(modal, set(), "Remote")
        assert select.picked is None, "a down server must never produce an answer"
        assert bot.unanswered_questions

    assert len(attempts) == 1, f"{len(attempts)} connection attempts for a server that is down"


def test_a_timeout_does_not_mark_the_server_down(bot, monkeypatch):
    '''LM Studio just-in-time loads the model, so the FIRST call against a perfectly
    good server can run long. Only a connect-level failure means "there is no server".'''
    attempts = []

    def hang(request, timeout=None):
        attempts.append(request.full_url)
        raise local.urllib.error.URLError(TimeoutError("timed out"))

    monkeypatch.setattr(bot, "use_AI", True)
    monkeypatch.setattr(local.urllib.request, "urlopen", hang)

    for i in range(3):
        modal, _ = dropdown(bot, monkeypatch, f"Unclassifiable question {i}?",
                            ["Select an option", "Yes", "No"])
        bot.answer_questions(modal, set(), "Remote")

    assert len(attempts) == 3


def test_ai_off_opens_no_socket_at_all(bot, monkeypatch):
    '''`use_AI` gates the MODEL. Off means off - no connect attempt, and exactly the
    behaviour of the bot before this layer existed.'''
    monkeypatch.setattr(bot, "use_AI", False)
    monkeypatch.setattr(local.urllib.request, "urlopen",
                        lambda *a, **k: pytest.fail("opened a socket with use_AI off"))
    modal, select = dropdown(bot, monkeypatch, "Do you have an active security clearance?",
                             ["Select an option", "Yes", "No"])

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked is None and bot.unanswered_questions


# ------------------------------------------------------------- the existing cloud path
def test_the_cloud_client_still_answers_what_the_local_layer_declines(bot, monkeypatch, model):
    '''Local first because it is cheaper and more private, but the cloud path is not
    replaced - a user who configured one keeps it.'''
    use(model, {"a": "NONE"})
    asked = []
    monkeypatch.setattr(bot, "aiClient", object(), raising=False)
    monkeypatch.setattr(bot, "answer_question",
                        lambda client, q, **kw: asked.append(q) or "Six years", raising=False)
    modal, field = text_question(bot, monkeypatch, "How many people did you manage?")
    monkeypatch.setattr(bot, "use_AI", True)

    bot.answer_questions(modal, set(), "Remote")

    assert field.value == "Six years" and asked == ["How many people did you manage?"]


def test_the_local_answer_wins_and_the_cloud_is_not_called(bot, monkeypatch, model):
    use(model, {"a": "Four"})
    monkeypatch.setattr(bot, "aiClient", object(), raising=False)
    monkeypatch.setattr(bot, "answer_question",
                        lambda *a, **kw: pytest.fail("cloud called although local answered"),
                        raising=False)
    modal, field = text_question(bot, monkeypatch, "How many people did you manage?")
    monkeypatch.setattr(bot, "use_AI", True)

    bot.answer_questions(modal, set(), "Remote")

    assert field.value == "Four"


# ---------------------------------------------------------------- the answer memory
def stored():
    return json.load(open(cache.PATH, encoding="utf-8"))


def test_an_unanswerable_dropdown_is_recorded_with_its_type_and_options(bot, monkeypatch):
    '''A bare question is not enough to answer one by hand: "Yes" is the wrong shape for
    a "0-1 / 2-5 / 5+" dropdown.'''
    question = "How many years of Kubernetes experience do you have?"
    options = ["Select an option", "0-1", "2-5", "5+"]
    modal, _ = dropdown(bot, monkeypatch, question, options)

    bot.answer_questions(modal, set(), "Remote")

    entry = next(iter(stored().values()))
    # The placeholder is not one of the answers he can give, and leaving it out keeps the
    # recorded key identical to the one the read-back looks the answer up under.
    assert entry == {"answer": None, "type": "select", "options": ["0-1", "2-5", "5+"]}
    assert "kubernetes" in next(iter(stored()))          # greppable by question text


@pytest.mark.parametrize("build, kind", [
    (lambda bot, mp: radio_group(bot, mp, "Do you hold an active clearance?", ["Yes", "No"])[0],
     "radio"),
    (lambda bot, mp: text_question(bot, mp, "How many people did you manage?")[0], "text"),
    (lambda bot, mp: textarea_question(bot, mp, "Describe a conflict you resolved.")[0],
     "textarea"),
    (lambda bot, mp: checkbox_question(bot, mp, "I certify that I am a U.S. citizen")[0],
     "checkbox"),
])
def test_every_control_type_records_what_blocked_the_job(bot, monkeypatch, build, kind):
    bot.answer_questions(build(bot, monkeypatch), set(), "Remote")

    assert [e["type"] for e in stored().values()] == [kind]


def test_recording_a_question_names_the_file_to_edit(bot, monkeypatch):
    '''The feature is only useful if the user knows where it is.'''
    printed = []
    modal, _ = text_question(bot, monkeypatch, "How many people did you manage?")
    monkeypatch.setattr(bot, "print_lg", lambda *a, **k: printed.append(" ".join(map(str, a))))

    bot.answer_questions(modal, set(), "Remote")

    assert any(cache.PATH in line and "answer" in line for line in printed), printed


def test_a_hand_written_answer_answers_the_question_with_no_model_call(bot, monkeypatch, model):
    '''The product feature: answer it once in the file, never be blocked by it again.'''
    question = "How many years of Kubernetes experience do you have?"
    options = ["Select an option", "0-1", "2-5", "5+"]
    modal, select = dropdown(bot, monkeypatch, question, options)
    bot.answer_questions(modal, set(), "Remote")             # run 1: blocked, recorded

    # Exactly what the user does: open the file, type the answer in, save. Re-read from
    # disk rather than poked in memory - the round trip through the file IS the feature.
    on_disk = stored()
    on_disk[next(iter(on_disk))]["answer"] = "2-5"
    open(cache.PATH, "w", encoding="utf-8").write(json.dumps(on_disk))
    cache._data = None
    model.calls.clear()

    modal, select = dropdown(bot, monkeypatch, question, options)
    bot.answer_questions(modal, set(), "Remote")             # run 2

    assert select.picked == "2-5"
    assert model.calls == [], "a remembered answer must not cost a model call"
    assert not bot.unanswered_questions


def test_a_hand_written_answer_still_goes_through_the_validator(bot, monkeypatch, model):
    '''The file is hand-edited, so it is an input to police, not a store to trust. An
    answer that matches no real option leaves the control untouched - it is not forced in.'''
    question = "What is your citizenship status?"
    options = ["U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer"]
    cache.put(question, "Klingon Citizen", options)
    monkeypatch.setattr(bot, "us_citizenship", "")
    modal, select = dropdown(bot, monkeypatch, question, ["Select an option"] + options)

    bot.answer_questions(modal, set(), "Remote")

    assert select.picked is None
    assert model.calls == []
    assert bot.unanswered_questions


def test_a_hand_written_text_answer_is_used_verbatim(bot, monkeypatch, model):
    question = "How many people did you manage?"
    cache.put(question, "7")
    modal, field = text_question(bot, monkeypatch, question)
    monkeypatch.setattr(bot, "use_AI", True)

    bot.answer_questions(modal, set(), "Remote")

    assert field.value == "7" and model.calls == []
    assert not bot.unanswered_questions


def test_the_users_own_answer_is_never_overwritten_by_a_later_blocked_run(bot, monkeypatch):
    question = "How many people did you manage?"
    cache.put(question, "7")
    assert cache.record(question, "text") is False
    assert cache.get(question) == "7"


def test_a_remembered_answer_works_with_ai_off(bot, monkeypatch):
    '''What the user typed into the file is his own configuration, not an AI guess, so
    the master AI switch must not hide it from him.'''
    question = "How many people did you manage?"
    cache.put(question, "7")
    monkeypatch.setattr(local, "_chat", lambda *a: pytest.fail("model called with AI off"))
    modal, field = text_question(bot, monkeypatch, question)       # sets use_AI False

    bot.answer_questions(modal, set(), "Remote")

    assert field.value == "7"
