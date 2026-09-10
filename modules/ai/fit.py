'''
Author:     Sai Vignesh Golla
License:    MIT License  (https://opensource.org/license/mit)
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Job-fit scoring, and the ONE way AI is allowed near the skip decision.

THE INVARIANT
-------------
`get_job_description` in runAiBot.py skips jobs on citizenship, clearance,
sponsorship and experience grounds. Those filters are deterministic, they are
the reason a CV did not go to a role the applicant is not legally allowed to
hold, and a 4B local model must NEVER be able to un-skip one.

So the combination is `deterministic_skip or ai_skip`. Never `and`, never a
model vote that outranks a rule. The AI's whole power here is to skip MORE.
`should_skip` is the only function that combines them and it is pinned by test.
'''

from modules.helpers import logger
from modules.ai.local import score_fit


def should_skip(deterministic_skip: bool, job_description: str, facts: str,
                min_score: int = 0, scorer=score_fit) -> tuple:
    '''
    `(skip, reason)` for one job.

    `skip` is `deterministic_skip or ai_skip` - the AI may only ADD a skip.
    A deterministic skip short-circuits, so the common rejection path stays free
    of model time. `min_score` of 0 disables AI skipping entirely (the default:
    scoring is advisory until the user opts in). A scorer that returns None -
    server down, timeout, unparseable - contributes no skip.
    '''
    if deterministic_skip:
        return True, None                       # already skipped; a model call would change nothing
    if min_score <= 0 or not job_description:
        return False, None
    scored = scorer(job_description, facts)
    if scored is None:
        return False, None                      # no score is not a reason to skip
    score, why = scored
    if score >= min_score:
        return False, None
    logger.warning("AI fit score %s < %s: %s", score, min_score, why)
    return True, f"AI fit score {score}/100 below {min_score} ({why})"
