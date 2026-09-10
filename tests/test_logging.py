'''
Unit tests for the stdlib-logging setup in modules/helpers.py.

`print_lg` is now a compatibility shim over a real logger, so these pin the bits
that ~130 existing call sites and every user watching the console depend on:
console output is unchanged, the file gets timestamps and levels, the level
actually filters, a locked log file never blocks, and log.txt rotates.

License: MIT  (https://opensource.org/license/mit)
'''

import logging
import re

import pytest

from modules.helpers import critical_error_log, logger, print_lg, setup_logging


LINE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})  (\w+) +(.*)$")

# capsys works because the console handler resolves sys.stdout at write time rather
# than caching it - see _StdoutHandler in modules/helpers.py.


@pytest.fixture
def log_file(tmp_path):
    '''Repoints the logger at a throwaway log.txt, and restores the real one after.'''
    path = tmp_path / "log.txt"
    setup_logging(str(path))
    yield path
    setup_logging()


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


# ------------------------------- print_lg compatibility --------------------
def test_print_lg_writes_to_both_the_console_and_the_file(log_file, capsys):
    print_lg("hello world")
    assert capsys.readouterr().out == "hello world\n"
    assert "hello world" in read(log_file)


def test_print_lg_still_prints_every_message_on_its_own_line(log_file, capsys):
    print_lg("one", "two")
    assert capsys.readouterr().out == "one\ntwo\n"


def test_print_lg_end_keeps_the_console_on_one_line(log_file, capsys):
    print_lg("progress", end="")
    print_lg("...done")
    assert capsys.readouterr().out == "progress...done\n"


def test_print_lg_end_does_not_leak_into_the_next_call(log_file, capsys):
    print_lg("a", end="")
    capsys.readouterr()
    print_lg("b")
    assert capsys.readouterr().out == "b\n"


def test_print_lg_flush_is_accepted_and_still_prints(log_file, capsys):
    print_lg("flushed", flush=True)
    assert capsys.readouterr().out == "flushed\n"


def test_print_lg_pretty_uses_pprint_formatting(log_file, capsys):
    print_lg({"b": 2, "a": 1}, pretty=True)
    out = capsys.readouterr().out
    assert out == "{'a': 1, 'b': 2}\n"          # pprint sorts keys, plain print does not


def test_print_lg_pretty_ignores_end_as_documented(log_file, capsys):
    print_lg("x", pretty=True, end="")
    assert capsys.readouterr().out.endswith("\n")


# ---------------------------------- levels ---------------------------------
def test_print_lg_logs_at_info(log_records):
    print_lg("routine progress")
    assert [r.levelno for r in log_records] == [logging.INFO]


def test_print_lg_from_critical_logs_at_error(log_records):
    print_lg("something broke", from_critical=True)
    assert [r.levelno for r in log_records] == [logging.ERROR]


def test_critical_error_log_records_error_with_the_exception_attached(log_records):
    try:
        raise ValueError("boom")
    except ValueError as error:
        critical_error_log("While doing the thing", error)

    record, = log_records
    assert record.levelno == logging.ERROR
    assert record.getMessage() == "While doing the thing"
    assert record.exc_info is not None
    assert record.exc_info[1].args == ("boom",)


def test_critical_error_log_writes_the_traceback_to_the_file(log_file):
    try:
        raise ValueError("boom")
    except ValueError as error:
        critical_error_log("While doing the thing", error)

    contents = read(log_file)
    assert "ERROR" in contents
    assert "Traceback (most recent call last)" in contents
    assert "ValueError: boom" in contents


def test_file_lines_carry_a_timestamp_and_a_level(log_file):
    print_lg("a line")
    logger.warning("a warning")

    matches = [LINE.match(line) for line in read(log_file).splitlines()]
    assert [m.group(2) for m in matches if m] == ["INFO", "WARNING"]
    assert [m.group(3) for m in matches if m] == ["a line", "a warning"]


# ------------------------------- log_level filtering -----------------------
def test_log_level_filters_info_out_of_the_file(tmp_path, capsys):
    path = tmp_path / "log.txt"
    try:
        setup_logging(str(path), level="WARNING")
        print_lg("routine progress")
        logger.warning("something odd")
    finally:
        setup_logging()

    contents = read(path)
    assert "routine progress" not in contents
    assert "something odd" in contents
    assert "routine progress" not in capsys.readouterr().out   # console is filtered too


def test_an_unrecognised_log_level_falls_back_to_info(tmp_path):
    try:
        setup_logging(str(tmp_path / "log.txt"), level="LOUD")
        assert logger.level == logging.INFO
    finally:
        setup_logging()


def test_missing_log_level_setting_does_not_crash(tmp_path, monkeypatch):
    '''A config written before `log_level` existed must still run.'''
    import modules.helpers as helpers
    monkeypatch.delattr(helpers._settings, "log_level", raising=False)
    try:
        setup_logging(str(tmp_path / "log.txt"))
        assert logger.level == logging.INFO
    finally:
        setup_logging()


# ------------------------------- degraded / locked file --------------------
def test_an_unwritable_log_file_neither_raises_nor_blocks(tmp_path, capsys):
    '''
    A locked log.txt used to pop a blocking pyautogui alert() mid-run, which
    deadlocked unattended runs. It must now degrade to console-only output.
    '''
    blocked = tmp_path / "log.txt"
    blocked.mkdir()                       # a directory can never be opened for writing
    try:
        setup_logging(str(blocked))
        print_lg("still visible")         # must not raise, must not block
        print_lg("also visible")
    finally:
        setup_logging()

    captured = capsys.readouterr()
    assert "still visible" in captured.out
    assert "also visible" in captured.out
    assert captured.err.count("Could not write to") == 1   # warned once, not per message


def test_the_alert_dialog_is_gone_from_the_logging_path():
    '''The old failure mode was `from pyautogui import alert` at module scope.'''
    import modules.helpers as helpers
    assert not hasattr(helpers, "alert")


# ---------------------------------- rotation -------------------------------
def test_the_file_handler_rotates(log_file):
    from logging.handlers import RotatingFileHandler

    handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
    assert len(handlers) == 1
    assert handlers[0].maxBytes > 0
    assert handlers[0].backupCount > 0


def test_setup_logging_replaces_handlers_instead_of_stacking_them(log_file, capsys):
    before = len(logger.handlers)
    setup_logging(str(log_file))
    assert len(logger.handlers) == before
    print_lg("once")
    assert capsys.readouterr().out == "once\n"
