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
as `null` rather than dropped - the null entries are the worklist of questions
worth answering yourself in config/questions.py.

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
    return _load().get(key(question, options), MISS)


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
