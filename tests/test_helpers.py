'''
Unit tests for modules/helpers.py — the pure helpers reimplemented for the MIT
relicense. These exercise real parsing/formatting logic, not trivial getters.

License: MIT  (https://opensource.org/license/mit)
'''

from datetime import datetime, timedelta

import pytest

from modules.helpers import (
    calculate_date_posted,
    truncate_for_csv,
    make_directories,
    convert_to_json,
)


# ----------------------------- calculate_date_posted -----------------------
def _seconds_ago(dt):
    return (datetime.now() - dt).total_seconds()


@pytest.mark.parametrize("text, expected_seconds", [
    ("10 seconds ago", 10),
    ("5 minutes ago", 5 * 60),
    ("2 hours ago", 2 * 3600),
    ("3 days ago", 3 * 86400),
    ("1 week ago", 7 * 86400),
    ("1 month ago", 30 * 86400),
    ("1 year ago", 365 * 86400),
])
def test_calculate_date_posted_units(text, expected_seconds):
    result = calculate_date_posted(text)
    assert result is not None
    assert abs(_seconds_ago(result) - expected_seconds) < 120  # within 2 minutes


def test_calculate_date_posted_is_case_insensitive():
    assert calculate_date_posted("15 MINUTES AGO") is not None


def test_calculate_date_posted_singular_and_plural_agree():
    one = calculate_date_posted("1 hour ago")
    assert one is not None
    assert abs(_seconds_ago(one) - 3600) < 120


def test_calculate_date_posted_unparseable_returns_none():
    assert calculate_date_posted("just now") is None
    assert calculate_date_posted("banana") is None
    assert calculate_date_posted("") is None


# ------------------------------- truncate_for_csv --------------------------
def test_truncate_for_csv_passes_short_values_through():
    assert truncate_for_csv("hello") == "hello"


def test_truncate_for_csv_none_becomes_empty_string():
    assert truncate_for_csv(None) == ""


def test_truncate_for_csv_shortens_long_values_with_suffix():
    out = truncate_for_csv("x" * 500, max_length=50, suffix="...CUT")
    assert len(out) == 50
    assert out.endswith("...CUT")


def test_truncate_for_csv_coerces_non_strings():
    assert truncate_for_csv(1234) == "1234"
    assert truncate_for_csv(["a", "b"]) == "['a', 'b']"


# ------------------------------- make_directories --------------------------
def test_make_directories_creates_missing_dirs(tmp_path):
    target = tmp_path / "a" / "b" / "c"
    make_directories([str(target)])
    assert target.is_dir()


def test_make_directories_uses_parent_for_file_paths(tmp_path):
    file_path = tmp_path / "logs" / "run.txt"
    make_directories([str(file_path)])
    assert file_path.parent.is_dir()
    assert not file_path.exists()  # only the folder is created, not the file


def test_make_directories_ignores_empty_paths_without_raising():
    make_directories([""])  # must not raise


# --------------------------------- convert_to_json -------------------------
def test_convert_to_json_parses_valid_json():
    assert convert_to_json('{"a": 1, "b": [2, 3]}') == {"a": 1, "b": [2, 3]}


def test_convert_to_json_reports_error_on_bad_json():
    result = convert_to_json("not json at all")
    assert isinstance(result, dict)
    assert "error" in result
    assert result["data"] == "not json at all"
