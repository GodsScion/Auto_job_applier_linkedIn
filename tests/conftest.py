'''
Author:   Sai Vignesh Golla
License:  MIT License  (https://opensource.org/license/mit)
GitHub:   https://github.com/GodsScion/Auto_job_applier_linkedIn

Shared fixtures and a custom test-summary printed after every run:
failing tests first, then counts (ran / passed / failed / skipped), then an
overall verdict line.
'''

import pytest


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
