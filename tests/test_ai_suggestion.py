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


# ------------------------------- the two gates ------------------------------
@pytest.fixture
def bot(monkeypatch):
    import runAiBot
    monkeypatch.setattr(runAiBot, "use_AI", False)
    monkeypatch.setattr(runAiBot, "llm_api_key", "not-needed")
    monkeypatch.setattr(runAiBot, "show_ai_suggestion", True)
    monkeypatch.setattr(runAiBot, "interactive_session", True)
    shown = []
    monkeypatch.setattr(runAiBot.pyautogui, "alert", lambda *a, **k: shown.append(a))
    return runAiBot, shown


def test_suggestion_is_shown_at_startup(bot, monkeypatch):
    runAiBot, shown = bot
    _urlopen(monkeypatch, _refused)
    runAiBot.suggest_ai()
    assert len(shown) == 1 and "https://lmstudio.ai" in shown[0][0]


def test_setting_suppresses_it_entirely(bot, monkeypatch):
    runAiBot, shown = bot
    monkeypatch.setattr(runAiBot, "show_ai_suggestion", False)
    _urlopen(monkeypatch, _must_not_run)             # off means the probe never runs
    runAiBot.suggest_ai()
    assert shown == []


def test_it_cannot_fire_in_a_non_interactive_run(bot, monkeypatch):
    '''A headless run and the control panel's Popen must not stop on a modal dialog.'''
    runAiBot, shown = bot
    monkeypatch.setattr(runAiBot, "interactive_session", False)
    _urlopen(monkeypatch, _must_not_run)             # nor pay a second of sockets for it
    runAiBot.suggest_ai()
    assert shown == []


def test_a_piped_run_cannot_reach_a_modal_at_all():
    '''
    The backstop behind the gate above, proved the only way that means anything: a
    real child process with stdout on a pipe - which is exactly how app.py Popens the
    bot. `interactive_session` must come out False there, and `pyautogui.alert` must
    already be the no-op print, so a dialog cannot block a run nobody can click.
    The subprocess timeout is the assertion: a modal would never return.
    '''
    import subprocess
    import sys
    probe = ("import runAiBot, pyautogui;"
             "print(runAiBot.interactive_session, pyautogui.alert('t', 'x', 'ok'))")
    out = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                         timeout=120, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip().endswith("False None")


# ------------------------------- the control panel --------------------------
def _panel_config(monkeypatch, use_ai=False, key="not-needed", show=True):
    '''Pin the effective config, so the test does not read the developer's own.'''
    import app
    monkeypatch.setattr(app, "_effective_config",
                        lambda: {"secrets": {"use_AI": use_ai, "llm_api_key": key},
                                 "settings": {"show_ai_suggestion": show}})


def test_panel_endpoint_reports_the_state(client, monkeypatch):
    _panel_config(monkeypatch)
    _urlopen(monkeypatch, lambda url, timeout=None: _FakeResponse())
    body = client.get("/api/ai-suggestion").get_json()
    assert body["state"] == "ready" and "LM Studio" in body["message"]


def test_panel_endpoint_is_silent_when_the_setting_is_off(client, monkeypatch):
    _panel_config(monkeypatch, show=False)
    _urlopen(monkeypatch, _must_not_run)
    assert client.get("/api/ai-suggestion").get_json() == {}
