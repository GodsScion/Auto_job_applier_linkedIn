'''
Unit tests for config/_overrides.py — the non-breaking layer that lets the
control panel override config/*.py defaults via user_config.json. A regression
here silently breaks configuration, so the guarantees are worth pinning down:

  * only keys that ALREADY exist as module globals are overridden,
  * unknown keys are never introduced,
  * a missing / invalid user_config.json is a clean no-op.

License: MIT  (https://opensource.org/license/mit)
'''

import config._overrides as overrides


def test_apply_overrides_only_existing_globals(monkeypatch):
    monkeypatch.setattr(overrides, "load_user_config",
                        lambda: {"settings": {"existing": 2, "brand_new": 99}})
    module_globals = {"existing": 1, "untouched": 5}
    overrides.apply("config.settings", module_globals)

    assert module_globals["existing"] == 2       # overridden
    assert module_globals["untouched"] == 5      # left alone
    assert "brand_new" not in module_globals     # never introduced


def test_apply_is_noop_when_section_missing(monkeypatch):
    monkeypatch.setattr(overrides, "load_user_config", lambda: {"other": {"x": 1}})
    module_globals = {"a": 1}
    overrides.apply("config.settings", module_globals)
    assert module_globals == {"a": 1}


def test_apply_ignores_non_dict_section(monkeypatch):
    monkeypatch.setattr(overrides, "load_user_config", lambda: {"settings": "oops"})
    module_globals = {"a": 1}
    overrides.apply("config.settings", module_globals)
    assert module_globals == {"a": 1}


def test_apply_uses_last_dotted_part_as_section(monkeypatch):
    monkeypatch.setattr(overrides, "load_user_config",
                        lambda: {"secrets": {"use_AI": True}})
    module_globals = {"use_AI": False}
    overrides.apply("config.secrets", module_globals)
    assert module_globals["use_AI"] is True


def test_load_user_config_missing_file_returns_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(overrides, "USER_CONFIG_PATH", str(tmp_path / "nope.json"))
    assert overrides.load_user_config() == {}


def test_load_user_config_invalid_json_returns_empty(monkeypatch, tmp_path):
    bad = tmp_path / "user_config.json"
    bad.write_text("{ this is not valid json", encoding="utf-8")
    monkeypatch.setattr(overrides, "USER_CONFIG_PATH", str(bad))
    assert overrides.load_user_config() == {}


def test_load_user_config_reads_valid_json(monkeypatch, tmp_path):
    good = tmp_path / "user_config.json"
    good.write_text('{"secrets": {"use_AI": true}}', encoding="utf-8")
    monkeypatch.setattr(overrides, "USER_CONFIG_PATH", str(good))
    assert overrides.load_user_config() == {"secrets": {"use_AI": True}}


# ---------------------------------------------------------------------------
# The control panel derives its fields from config/*.py, and docs/config-*.md
# describes the same settings in prose. Both used to be hand-synced and both
# drifted: 24 settings had no panel field while the docs claimed 3, and the docs
# named two settings that do not exist. These turn that drift into a red test.
# ---------------------------------------------------------------------------
import importlib
import pathlib
import re

import config_schema

_ROOT = pathlib.Path(__file__).resolve().parent.parent
# Its default is None, which no form control can express - see docs/configuration.md.
_NOT_IN_PANEL = {"llm_temperature"}


def _config_keys():
    '''Every setting name defined in config/*.py.'''
    return {key for name in config_schema.MODULES
            for key in vars(importlib.import_module("config." + name))
            if not key.startswith("_")}


def test_panel_has_a_field_for_every_setting():
    fields = {field["key"] for field in config_schema.iter_fields()}
    assert _config_keys() - fields == _NOT_IN_PANEL
    assert fields - _config_keys() == set()      # and never invents one


def test_docs_and_config_name_the_same_settings():
    docs = "\n".join(page.read_text(encoding="utf-8")
                     for page in sorted((_ROOT / "docs").glob("config-*.md")))
    named = set(re.findall(r"`([a-z][a-z0-9]*(?:_[a-zA-Z0-9]+)+)`", docs))
    keys = _config_keys()
    invented = sorted(named - keys)
    undocumented = sorted(keys - set(re.findall(r"`(\w+)`", docs)))
    assert not invented, f"docs name settings config/*.py does not have: {invented}"
    assert not undocumented, f"settings no docs page mentions: {undocumented}"


def test_field_types_come_from_the_config_file():
    '''The parser is the only thing standing between a config comment and the form.'''
    fields = {field["key"]: field for field in config_schema.iter_fields()}
    assert fields["require_visa"]["type"] == "select"          # trailing `# "Yes" or "No"`
    assert fields["require_visa"]["options"] == ["Yes", "No"]
    assert fields["on_site"]["type"] == "list"                 # `# (multiple select) ...`
    assert fields["on_site"]["options"] == ["On-site", "Remote", "Hybrid"]
    assert fields["companies"].get("options") is None          # dynamic: any value goes
    assert fields["recent_employer"]["type"] == "text"         # its `Eg:` is not a vocabulary
    assert fields["cover_letter"]["type"] == "textarea"        # a default with line breaks
    assert fields["password"]["type"] == "password"
    assert fields["click_gap"]["step"] == 1                    # a whole-number setting
    assert "sponsorship" in fields["skip_non_sponsoring_jobs"]["help"]
    assert "lakhs" in fields["desired_salary"]["help"]         # the triple-quoted note below
