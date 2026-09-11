'''
Author:     Sai Vignesh Golla
License:    MIT License  (https://opensource.org/license/mit)
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Local-model answer layer for Easy Apply questions.

WHY THIS IS NOT modules/ai/connections.py
-----------------------------------------
`connections.py` is the provider-agnostic cloud path (LangChain -> OpenAI /
Gemini / anything OpenAI-compatible) and it stays exactly as it is. This module
is the latency-critical LOCAL path, and it needs three things on the wire that
LangChain would have us fight its abstraction for:

  * `chat_template_kwargs: {"enable_thinking": false}` - Qwen3.5 thinks by
    default. Measured 2026-09-10: with thinking ON the model burned all 300
    tokens without finishing its JSON; OFF it finished in 250. It is a token
    COUNT problem, not a speed one.
  * a raw `response_format: {"type": "json_schema", ...}` - constrained
    decoding, which LangChain reaches only through its tool-calling
    `with_structured_output` path. A 4B asked nicely for JSON drifts; a 4B under
    a grammar cannot. Shape is enforced by the schema, not by prompt wording.
  * `max_retries = 0` and a hard per-call timeout. LangChain's ChatOpenAI
    retries twice by default, which TRIPLES the worst case against a server that
    is down - on a live job application, with the browser sitting idle.

All three are one dict key each with `urllib.request`, which is also what
`check_local_llm.py` speaks. So: stdlib, ~40 lines, no new dependency, and the
request shape is readable at a glance.

THE COST MODEL THAT SHAPES EVERY TIER
-------------------------------------
Qwen3.5-4B 4-bit on an M4 16GB, measured: ~158 tok/s prefill, ~20.6 tok/s
generation. GENERATED tokens are the bill. So each question is pushed down to
the cheapest tier that can answer it:

  Tier 0  free      the deterministic ladder in runAiBot.py already answers it,
                    or the cache has it. No model call. This is the common case.
  Tier 1  ~7 tok    constrained choice for select/radio: an option number or
                    NONE, under an enum grammar.  ~0.4s + prefill.
  Tier 2  ~30-80    short free text.               ~2-4s + prefill.
  Tier 3  ~200-500  long form, cached once per company. ~10-25s.

NOTHING HERE IS ALLOWED TO RAISE INTO THE APPLY LOOP. Every failure - server
down, timeout, garbage, schema refusal - returns None, and the caller falls
through to the bot's existing never-guess behaviour.
'''

import json
import urllib.request

from modules.helpers import logger
from modules.ai import cache
from modules.ai.prompts import (local_select_system, local_text_system,
                                local_long_system, local_fit_system)

try:
    import config.secrets as _cfg
except Exception:                                   # importable without a configured checkout
    _cfg = None


def _cfg_get(name: str, default: str) -> str:
    return (getattr(_cfg, name, "") or "").strip() or default


# tier -> (max_tokens, timeout_seconds). The timeouts are hang guards, not latency
# targets: they are sized for a cold start, where LM Studio just-in-time loads the
# 2.85 GB model on the first request.
TIERS = {1: (8, 30), 2: (128, 60), 3: (512, 120)}

_down = False       # set once the server proves unreachable; see `_chat`


def _chat(system: str, user: str, schema: dict, tier: int):
    '''
    One OpenAI-compatible chat completion under a JSON-schema grammar.
    Returns the parsed object, or None on ANY failure.

    `system` is a static per-tier prefix and `user` starts with the equally static
    profile block, so LM Studio's prompt prefix cache skips re-prefilling both
    across calls. Never interpolate variable text into `system`.
    '''
    global _down
    # Nothing is listening and nothing in a run will change that, so the first refusal
    # ends it. Without this every question of every job pays another connect attempt, and
    # a DNS miss or a firewalled host pays it in seconds rather than microseconds.
    if _down:
        return None
    max_tokens, timeout = TIERS[tier]
    body = {
        "model": _cfg_get("local_llm_model", "qwen/qwen3.5-4b"),
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "answer", "strict": True, "schema": schema}},
        "chat_template_kwargs": {"enable_thinking": False},
        "max_tokens": max_tokens,
        "temperature": 0,
    }
    url = _cfg_get("local_llm_api_url", "http://127.0.0.1:1234/v1").rstrip("/") + "/chat/completions"
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + _cfg_get("llm_api_key", "not-needed")})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            parsed = json.loads(json.load(response)["choices"][0]["message"]["content"])
        return parsed if isinstance(parsed, dict) else None
    except Exception as e:
        # Down, hung, or talking nonsense - all the same to the caller: no answer.
        # A connect-level OSError (refused, unreachable, DNS) means there is no server;
        # a TimeoutError does NOT - LM Studio just-in-time loads the model, so the first
        # call against a working server can legitimately run long.
        _down = isinstance(getattr(e, "reason", None), OSError) and not isinstance(e.reason, TimeoutError)
        logger.warning("Local AI tier %s call failed, falling through to no answer. %s", tier, e)
        return None


def profile_block(facts: dict) -> str:
    '''
    The compact fact block. Deliberately NOT the whole profile: no cover letter, no
    LinkedIn summary, no job description. Those are tier 3's problem.

    It is fixed for a whole run on purpose. Selecting fields per question would save
    ~50 prefill tokens (~0.3s) but change the prefix on every call, which costs the
    LM Studio prefix cache - far more than it saves. See the report.
    '''
    return "\n".join(f"{k}: {v}" for k, v in facts.items() if v not in (None, "", "Unknown"))


def default_facts() -> dict:
    '''
    Facts read LITERALLY from config, never inferred by a model. Four of five model
    configs invented an email, a LinkedIn URL and the wrong city when the contact
    block was absent from the prompt, so it is always present and always literal.
    '''
    import config.personals as p
    import config.questions as q
    return {
        "Name": f"{p.first_name} {p.last_name}",
        "Location": f"{p.current_city or ''} {p.state}, {p.country}".strip(),
        "Total years of professional experience": q.years_of_experience,
        "Needs visa sponsorship": q.require_visa,
        "Legally authorized to work here": q.legally_authorized,
        "Citizenship status": q.us_citizenship,
        "Notice period (days)": q.notice_period,
        "Desired salary": q.desired_salary,
        "Headline": q.linkedin_headline,
        "Gender": p.gender, "Ethnicity": p.ethnicity,
        "Disability status": p.disability_status, "Veteran status": p.veteran_status,
    }


# --------------------------------------------------------------------------- #
# Tier 1 - constrained choice.  AI proposes, the deterministic validator disposes.
# --------------------------------------------------------------------------- #
def answer_select(question: str, option_texts: list, validator, facts: str, ask=_chat):
    '''
    Index into `option_texts`, or None to LEAVE THE CONTROL UNTOUCHED.

    `validator` is runAiBot's `match_answer_to_option`, passed in rather than imported
    (importing runAiBot opens Chrome). It runs on EVERY proposal, including a cache
    hit, so the AI can never write a value the deterministic matcher would have
    rejected and a hand-edited cache cannot smuggle one in either. None here is the
    same None the config ladder produces, and takes the same never-guess path.
    '''
    if not question or not option_texts:
        return None

    proposal = cache.get(question, option_texts)
    if proposal is cache.MISS:
        numbered = "\n".join(f"{i}. {text}" for i, text in enumerate(option_texts, 1))
        # Variable tail only; the static rules live in the system prompt.
        result = ask(local_select_system,
                     f"{facts}\n\nQuestion: {question}\n\nOptions:\n{numbered}",
                     {"type": "object", "additionalProperties": False, "required": ["o"],
                      "properties": {"o": {"type": "string",
                                           "enum": [str(i) for i in range(1, len(option_texts) + 1)] + ["NONE"]}}},
                     1)
        choice = (result or {}).get("o")
        # The enum makes anything else impossible, but a non-conforming server is not.
        proposal = option_texts[int(choice) - 1] if str(choice).isdigit() and 0 < int(choice) <= len(option_texts) else None
        cache.put(question, proposal, option_texts)

    matched = validator(proposal, option_texts)
    if matched is None and proposal:
        logger.warning('AI proposed "%s" for "%s", which matches no real option. Leaving it untouched.',
                       proposal, question)
    return matched


# --------------------------------------------------------------------------- #
# Tier 2 - short free text.
# --------------------------------------------------------------------------- #
def answer_text(question: str, facts: str, ask=_chat):
    '''The answer string, or None to leave the field empty and report it.'''
    if not question:
        return None
    answer = cache.get(question)
    if answer is cache.MISS:
        result = ask(local_text_system, f"{facts}\n\nQuestion: {question}",
                     {"type": "object", "additionalProperties": False, "required": ["a"],
                      "properties": {"a": {"type": "string"}}}, 2)
        answer = str((result or {}).get("a") or "").strip()
        answer = None if not answer or answer.upper() == "NONE" else answer
        cache.put(question, answer)
    return answer


# --------------------------------------------------------------------------- #
# Tier 3 - long form. Expensive, so cached once per company, not per question.
# --------------------------------------------------------------------------- #
def answer_long(kind: str, company: str, facts: str, job_description: str = "", ask=_chat):
    '''Cover letter / summary text for one company, or None. ~10-25s on a miss.'''
    entry = f"{kind} @ {company}"
    answer = cache.get(entry)
    if answer is cache.MISS:
        # Truncated: prefill is 158 tok/s, so a full 1200-token JD is ~8s before the
        # first output token. The first 2000 characters carry the role and the asks.
        result = ask(local_long_system,
                     f"{facts}\n\nWrite: {kind}\n\nRole at {company}:\n{(job_description or '')[:2000]}",
                     {"type": "object", "additionalProperties": False, "required": ["t"],
                      "properties": {"t": {"type": "string"}}}, 3)
        answer = str((result or {}).get("t") or "").strip() or None
        cache.put(entry, answer)
    return answer


# --------------------------------------------------------------------------- #
# Fit score.  Kept here so `fit.py` stays about the skip decision, not transport.
# --------------------------------------------------------------------------- #
def score_fit(job_description: str, facts: str, ask=_chat):
    '''
    `(score 0-100, one-line reason)`, or None. A parse failure is None, never a score.

    Tier 2, not tier 1: the reason string pushes this to ~20 output tokens and tier 1's
    8-token cap would truncate the JSON mid-object. max_tokens is a ceiling, not a
    target - the grammar closes the object as soon as "r" ends, so the wider cap costs
    nothing on a well-behaved reply.
    '''
    result = ask(local_fit_system, f"{facts}\n\nRole:\n{(job_description or '')[:2000]}",
                 {"type": "object", "additionalProperties": False, "required": ["s", "r"],
                  "properties": {"s": {"type": "integer", "minimum": 0, "maximum": 100},
                                 "r": {"type": "string"}}}, 2)
    score = (result or {}).get("s")
    if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 100:
        return None
    return score, str(result.get("r") or "").strip()


# --------------------------------------------------------------------------- #
# Startup nudge.  Most users never switch AI on because they assume it costs
# money, and a local model does not. Shown once per run and by the control panel.
# --------------------------------------------------------------------------- #
# Both speak the OpenAI-compatible /v1 API, so one probe shape covers the pair.
LOCAL_SERVERS = (("LM Studio", "http://127.0.0.1:1234/v1"),
                 ("Ollama", "http://127.0.0.1:11434/v1"))

_READY = ('{name} is already running on this computer, but "Use AI" is switched off, so '
          'the tool is not using it.\n\n'
          'Turn "Use AI" on (use_AI = True in config/secrets.py) and set "Local AI server '
          'URL" to {url}. It then answers the application questions your config does not '
          'cover, and it costs nothing - the model runs on your own machine.')

_OFF = ('AI is switched off, so the tool can only answer the application questions your '
        'config already covers. Anything else is left blank and reported.\n\n'
        'If the worry is cost, it does not have to cost anything. Install LM Studio '
        '(https://lmstudio.ai) or Ollama (https://ollama.com), download a small model - a '
        '4B-class one is plenty and runs on a normal laptop - and turn "Use AI" on.')

_BROKEN = ('"Use AI" is on, but no local model server answered and no API key is set, so '
           'every question your config does not cover will be left unanswered.\n\n'
           'Start LM Studio (https://lmstudio.ai) or Ollama (https://ollama.com) and point '
           '"Local AI server URL" at it, or paste a real key into "AI API key".')


def local_server_running(timeout: float = 0.5):
    '''
    `(name, base url)` of the first local model server that answers, or None.

    Runs on the startup path, so it NEVER raises and never costs more than
    `timeout` per port: a port nothing is listening on refuses immediately, and
    the timeout caps a firewalled or black-holed one. Two ports, ~1s worst case.
    '''
    for name, url in LOCAL_SERVERS:
        try:
            urllib.request.urlopen(url + "/models", timeout=timeout).close()
            return name, url
        except Exception:
            pass                    # not there, not ours, or too slow to be worth waiting on
    return None


def ai_suggestion(use_ai: bool, api_key: str = "", probe=local_server_running):
    '''
    `(state, message)` for the "you could be using AI" nudge, or None when there is
    nothing worth saying. `probe` is injected so tests never open a socket.

      "ready"   a local server is up and `use_AI` is simply off - one flip away.
      "off"     nothing configured at all, and it could be free.
      "broken"  `use_AI` is on but nothing answers, so answers silently fall through.

    A configured API key with `use_AI` off says nothing: that user already knows what
    AI costs and turned it off on purpose. The pitch here is only that it can be free.
    '''
    server = probe()
    has_key = (api_key or "").strip().lower() not in ("", "not-needed")
    if use_ai:
        return None if (server or has_key) else ("broken", _BROKEN)
    if server:
        return "ready", _READY.format(name=server[0], url=server[1])
    return None if has_key else ("off", _OFF)
