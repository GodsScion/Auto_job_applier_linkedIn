'''
Author:   Sai Vignesh Golla
License:  MIT License  (https://opensource.org/license/mit)
GitHub:   https://github.com/GodsScion/Auto_job_applier_linkedIn

Shared fixtures and a custom test-summary printed after every run:
failing tests first, then counts (ran / passed / failed / skipped), then an
overall verdict line.
'''

import logging

import pytest


class _CaptureHandler(logging.Handler):
    '''Collects LogRecords so tests can assert on level as well as text.'''
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture
def log_records():
    '''
    Records emitted by the tool's logger. It deliberately does not propagate to the
    root logger (so a stray basicConfig can never double-print for a user), which is
    why pytest's built-in `caplog` cannot see it.
    '''
    from modules.helpers import logger
    handler = _CaptureHandler()
    previous_level = logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    yield handler.records
    logger.removeHandler(handler)
    logger.setLevel(previous_level)


@pytest.fixture(autouse=True)
def isolated_answer_file(tmp_path, monkeypatch):
    '''
    The answer file is read by the question branches now, so a developer who has actually
    run the bot has real answers sitting at the project root. Without this every test that
    drives `answer_questions` would be graded against his cache instead of the code, and
    would write null entries into it. Every test gets an empty one.
    '''
    from modules.ai import cache, local
    monkeypatch.setattr(cache, "PATH", str(tmp_path / "answers.json"))
    monkeypatch.setattr(cache, "_data", None)
    monkeypatch.setattr(local, "_down", False)      # the short-circuit is per-run, not per-suite


@pytest.fixture
def client():
    '''Flask test client for the local control panel (app.py).'''
    import app
    app.app.config.update(TESTING=True)
    return app.app.test_client()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    tr = terminalreporter
    passed = tr.stats.get("passed", [])
    skipped = tr.stats.get("skipped", [])
    failed = tr.stats.get("failed", [])
    errors = tr.stats.get("error", [])
    fails = failed + errors                      # collection/fixture errors count as failing
    total = len(passed) + len(fails) + len(skipped)

    tr.write_line("")
    tr.write_sep("=", "TEST SUMMARY", bold=True)

    # Failing tests first, at the top of the summary.
    if fails:
        tr.write_line("")
        tr.write_line("These tests are FAILING:", red=True, bold=True)
        for rep in fails:
            reason = ""
            longrepr = getattr(rep, "longrepr", None)
            crash = getattr(longrepr, "reprcrash", None)
            if crash is not None and getattr(crash, "message", None):
                reason = "  ->  " + str(crash.message).splitlines()[0]
            tr.write_line("  ✗ %s%s" % (rep.nodeid, reason), red=True)
    else:
        tr.write_line("")
        tr.write_line("No failing tests ✔", green=True, bold=True)

    # Counts.
    tr.write_line("")
    tr.write_line("  Total tests ran : %d" % total)
    tr.write_line("  Passed          : %d" % len(passed), green=len(passed) > 0)
    tr.write_line("  Failed          : %d" % len(fails), red=len(fails) > 0)
    tr.write_line("  Skipped         : %d" % len(skipped), yellow=len(skipped) > 0)
    tr.write_line("")

    # Overall verdict at the end.
    verdict = "FAILED" if fails else "PASSED"
    tr.write_sep(
        "=",
        "OVERALL: %s  (%d passed, %d failed, %d skipped of %d)"
        % (verdict, len(passed), len(fails), len(skipped), total),
        bold=True,
        red=bool(fails),
        green=not fails,
    )
