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


def _chat(system: str, user: str, schema: dict, tier: int):
    '''
    One OpenAI-compatible chat completion under a JSON-schema grammar.
    Returns the parsed object, or None on ANY failure.

    `system` is a static per-tier prefix and `user` starts with the equally static
    profile block, so LM Studio's prompt prefix cache skips re-prefilling both
    across calls. Never interpolate variable text into `system`.
    '''
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
