'''
The startup "you could be using AI" nudge: modules/ai/local.py, runAiBot.suggest_ai,
and the control panel's /api/ai-suggestion.

NOTHING HERE OPENS A SOCKET. Either the probe is injected or `urlopen` is replaced,
because the state this feature exists for is "no server running", and a test that
touched a real port would pass or fail on whatever the developer has listening.

License: MIT  (https://opensource.org/license/mit)
'''

import os

import pytest

from modules.ai import local


def _no_server():
    return None


def _lm_studio():
    return "LM Studio", "http://127.0.0.1:1234/v1"


class _FakeResponse:
    def close(self):
        pass


def _urlopen(monkeypatch, behaviour):
    '''Replace the ONLY call that could reach a real server.'''
    monkeypatch.setattr(local.urllib.request, "urlopen", behaviour)


def _refused(url, timeout=None):
    raise OSError("Connection refused")


def _must_not_run(url, timeout=None):
    raise AssertionError("the probe opened a connection while the nudge was switched off")


# ------------------------------- the three states ---------------------------
def test_local_server_running_says_which_one_and_where():
    state, message = local.ai_suggestion(False, "not-needed", probe=_lm_studio)
    assert state == "ready"
    assert "LM Studio is already running" in message
    assert "http://127.0.0.1:1234/v1" in message
    assert "use_AI = True" in message


def test_nothing_configured_pitches_a_free_local_model():
    state, message = local.ai_suggestion(False, "not-needed", probe=_no_server)
    assert state == "off"
    assert "https://lmstudio.ai" in message and "https://ollama.com" in message
    assert "4B-class" in message                    # a small model is the recommendation


def test_ai_on_but_nothing_reachable_is_a_warning():
    state, message = local.ai_suggestion(True, "", probe=_no_server)
    assert state == "broken"
    assert "left unanswered" in message


def test_nothing_to_say_when_ai_is_actually_working():
    assert local.ai_suggestion(True, "not-needed", probe=_lm_studio) is None
    assert local.ai_suggestion(True, "sk-real-key", probe=_no_server) is None
    # A key with AI off is a deliberate choice, not someone who thinks AI costs money.
    assert local.ai_suggestion(False, "sk-real-key", probe=_no_server) is None


# ------------------------------- the probe ----------------------------------
def test_probe_never_raises_and_bounds_its_own_wait(monkeypatch):
    '''A refused port, a DNS failure and a hang all have to look the same: no server.'''
    waits = []
    _urlopen(monkeypatch, lambda url, timeout=None: waits.append(timeout) or _refused(url))
    assert local.local_server_running() is None
    assert len(waits) == len(local.LOCAL_SERVERS)   # both tried, neither retried
    assert sum(waits) <= 1.0                        # ~1s total, on the startup path


def test_probe_finds_the_first_server_that_answers(monkeypatch):
    _urlopen(monkeypatch, lambda url, timeout=None: _FakeResponse())
    assert local.local_server_running() == local.LOCAL_SERVERS[0]
