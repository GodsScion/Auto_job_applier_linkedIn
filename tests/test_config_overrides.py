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
