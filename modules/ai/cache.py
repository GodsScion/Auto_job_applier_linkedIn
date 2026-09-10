'''
Author:     Sai Vignesh Golla
License:    MIT License  (https://opensource.org/license/mit)
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Persistent answer cache for the local AI layer.

LinkedIn Easy Apply asks the same ~50 questions across every job, so the cheapest
model call is the one never made: a hit costs zero model time and turns a whole
job into free work. Plain JSON at the project root, stdlib only.

The file is meant to be HAND-EDITED, which is why keys carry the readable
question and not just a digest, and why a "no truthful answer" result is stored
as `null` rather than dropped. Those null entries are the worklist: `record()`
writes one for every question the bot could not answer, with its control type
and options, and typing an answer in beside it answers that question on the next
run with no model call. It is where the user teaches the bot.

It holds the user's own answers, so it is gitignored and written 0600.
'''

import hashlib
import json
import os
import re

# modules/ai/cache.py -> modules/ai -> modules -> project root
PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    ".ai_answer_cache.json")

MISS = object()     # distinct from a stored `None`, which means "asked, no truthful answer"

_data = None
_whitespace = re.compile(r"\s+")


def _norm(text) -> str:
    '''Lowercase, collapse whitespace, drop LinkedIn's required-field decoration.'''
    return _whitespace.sub(" ", str(text or "").strip().lower()).strip(" \t*?:.")


def key(question: str, options=None) -> str:
    '''
    `<readable question>#<digest>`. The digest covers the normalised question AND the
    normalised option list, so the same wording with a different option set is a
    different entry - answering "Yes/No" is not the same as answering "0-1/2-5/5+".
    '''
    question = _norm(question)
    digest = hashlib.sha1(json.dumps([question, [_norm(o) for o in (options or [])]]).encode()).hexdigest()[:8]
    return f"{question[:70]}#{digest}"


def _load() -> dict:
    global _data
    if _data is None:
        try:
            with open(PATH, encoding="utf-8") as f:
                loaded = json.load(f)
            _data = loaded if isinstance(loaded, dict) else {}
        except Exception:
            _data = {}                      # absent, empty or hand-edited into invalid JSON
    return _data


def get(question: str, options=None):
    '''Stored answer, or `MISS`. A stored `None` is a real result: asked, no truthful answer.'''
    entry = _load().get(key(question, options), MISS)
    # A question `record()`ed for the user carries its type and options alongside the
    # answer, so the file shows him WHAT he is answering. Everything else is a bare value.
    return entry.get("answer") if isinstance(entry, dict) else entry


def put(question: str, answer, options=None) -> None:
    '''Store an answer. Written via a temp file chmod-ed before the rename, so the
    real answers are never briefly world-readable.'''
    _load()[key(question, options)] = answer
    tmp = PATH + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(_data, f, indent=1, sort_keys=True, ensure_ascii=False)
        os.chmod(tmp, 0o600)
        os.replace(tmp, PATH)
    except Exception:
        pass                                # a cache we cannot write is a slow bot, not a broken one


def record(question: str, kind: str, options=None) -> bool:
    '''
    Add a question nothing could answer to the file as a worklist entry, and say whether
    it was new. Type and options ride along because a bare question is not enough to
    answer one by hand - "Yes" is the wrong shape for a "0-1 / 2-5 / 5+" dropdown.

    An entry that already carries an answer is left alone: the user's own edit is never
    overwritten by a later run that got blocked on the same question.
    '''
    if get(question, options) not in (MISS, None):
        return False
    put(question, {"answer": None, "type": kind, "options": list(options or [])}, options)
    return True
