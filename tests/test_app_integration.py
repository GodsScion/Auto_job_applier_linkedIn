'''
Integration tests for app.py (the local control panel) via Flask's test client.
These exercise real request/response behaviour: schema exposure, config save
coercion + round-trip, unknown-key rejection, and the applied-jobs history
CSV -> JSON mapping and mark-applied flow.

All tests isolate their writes to a tmp_path, so the user's real user_config.json
and "all excels/" folder are never touched.

License: MIT  (https://opensource.org/license/mit)
'''

import csv
import json
import os
import stat


# --------------------------------- schema -----------------------------------
def test_schema_endpoint_returns_nonempty_list(client):
    resp = client.get("/api/schema")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list) and len(data) > 0
    assert "section" in data[0] and "fields" in data[0]


# ------------------------------- config save/get ----------------------------
def test_config_save_coerces_and_roundtrips(client, tmp_path, monkeypatch):
    import app
    import config._overrides as overrides
    cfg_path = str(tmp_path / "user_config.json")
    monkeypatch.setattr(app, "USER_CONFIG_PATH", cfg_path)
    monkeypatch.setattr(overrides, "USER_CONFIG_PATH", cfg_path)

    # "true" (string) must be coerced to a real bool for the use_AI field.
    resp = client.post("/api/config", json={"secrets": {"use_AI": "true"}})
    assert resp.status_code == 200

    with open(cfg_path, encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["secrets"]["use_AI"] is True

    # GET reflects the saved value.
    got = client.get("/api/config").get_json()
    assert got["secrets"]["use_AI"] is True


def _isolate(tmp_path, monkeypatch):
    '''Point app.py and config/_overrides at a throwaway user_config.json.'''
    import app
    import config._overrides as overrides
    cfg_path = str(tmp_path / "user_config.json")
    monkeypatch.setattr(app, "USER_CONFIG_PATH", cfg_path)
    monkeypatch.setattr(overrides, "USER_CONFIG_PATH", cfg_path)
    return app, cfg_path


# ------------------------------- secret handling ----------------------------
def test_api_responses_carry_no_wildcard_cors_header(client):
    '''A bare CORS(app) put Access-Control-Allow-Origin: * on every route, so any page
    open in the user's browser could read the LinkedIn password off 127.0.0.1. The panel
    serves its own HTML from the same origin and never needed CORS.'''
    for route in ("/api/schema", "/api/config", "/api/status"):
        assert "Access-Control-Allow-Origin" not in client.get(route).headers, route


def test_stored_password_survives_a_form_round_trip(client, tmp_path, monkeypatch):
    '''The one that must not regress: the UI can only send back the placeholder it was
    given, so treating it as a real value would blank the password on the next save.'''
    app, cfg_path = _isolate(tmp_path, monkeypatch)

    client.post("/api/config", json={"secrets": {"password": "hunter2", "llm_api_key": "sk-real"}})

    got = client.get("/api/config").get_json()
    assert got["secrets"]["password"] == app.SECRET_PLACEHOLDER      # never sent in cleartext
    assert got["secrets"]["llm_api_key"] == app.SECRET_PLACEHOLDER

    # The user edits an unrelated field and saves the whole form back.
    resp = client.post("/api/config", json={"secrets": {
        "password": got["secrets"]["password"],
        "llm_api_key": got["secrets"]["llm_api_key"],
        "username": "me@example.com",
    }})
    assert resp.status_code == 200
    assert resp.get_json()["secrets"]["password"] == app.SECRET_PLACEHOLDER   # not echoed back either

    with open(cfg_path, encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["secrets"]["password"] == "hunter2"                  # still there
    assert saved["secrets"]["llm_api_key"] == "sk-real"
    assert saved["secrets"]["username"] == "me@example.com"


def test_password_can_still_be_changed_and_cleared(client, tmp_path, monkeypatch):
    '''Redaction must not make the field read-only: a real value and "" both land.'''
    app, cfg_path = _isolate(tmp_path, monkeypatch)

    client.post("/api/config", json={"secrets": {"password": "hunter2"}})
    client.post("/api/config", json={"secrets": {"password": "newpass"}})
    with open(cfg_path, encoding="utf-8") as f:
        assert json.load(f)["secrets"]["password"] == "newpass"

    client.post("/api/config", json={"secrets": {"password": ""}})
    with open(cfg_path, encoding="utf-8") as f:
        assert json.load(f)["secrets"]["password"] == ""
    assert client.get("/api/config").get_json()["secrets"]["password"] == ""  # empty, not masked


def test_user_config_is_written_owner_only(client, tmp_path, monkeypatch):
    '''It holds the LinkedIn password, the API key, the phone and the EEO answers;
    a plain json.dump leaves it 0644.'''
    app, cfg_path = _isolate(tmp_path, monkeypatch)

    client.post("/api/config", json={"secrets": {"password": "hunter2"}})
    assert stat.S_IMODE(os.stat(cfg_path).st_mode) == 0o600

    os.chmod(cfg_path, 0o644)               # the update path writes it too
    app._freeze_config()
    assert stat.S_IMODE(os.stat(cfg_path).st_mode) == 0o600


def test_freeze_pins_settings_the_panel_never_shows(client, tmp_path, monkeypatch):
    '''The update runs `git stash` + `git pull` and deliberately never pops the stash,
    so anything _freeze_config misses comes back as the shipped default. It used to
    pin only the schema keys, silently reverting the 24 settings that had no field.'''
    app, cfg_path = _isolate(tmp_path, monkeypatch)

    app._freeze_config()

    with open(cfg_path, encoding="utf-8") as f:
        frozen = json.load(f)
    for module, keys in app.DEFAULTS.items():
        assert set(frozen[module]) == set(keys), module
    assert "stop_before_submit" in frozen["settings"]      # had no panel field
    assert "llm_temperature" in frozen["secrets"]          # still has none


def test_config_save_refuses_a_value_the_bot_would_reject_at_startup(client, tmp_path, monkeypatch):
    '''modules/validator.py raises on these when the bot starts, which is far too late
    to tell someone their run will not start.'''
    _isolate(tmp_path, monkeypatch)

    bad = [("search", "on_site", ["Remote", "Mars"]),        # not a LinkedIn option
           ("search", "date_posted", "Yesterday"),
           ("questions", "notice_period", 1.5)]             # check_int raises on a float
    for section, key, value in bad:
        resp = client.post("/api/config", json={section: {key: value}})
        assert resp.status_code == 400, (key, resp.get_json())

    assert client.post("/api/config", json={"questions": {"notice_period": 30.0}}).status_code == 200


def test_config_save_rejects_unknown_key(client, tmp_path, monkeypatch):
    import app
    import config._overrides as overrides
    cfg_path = str(tmp_path / "user_config.json")
    monkeypatch.setattr(app, "USER_CONFIG_PATH", cfg_path)
    monkeypatch.setattr(overrides, "USER_CONFIG_PATH", cfg_path)

    resp = client.post("/api/config", json={"secrets": {"definitely_not_a_field": 1}})
    assert resp.status_code == 400
    assert not os.path.exists(cfg_path)  # nothing written on rejection


def test_config_save_rejects_unknown_section(client, tmp_path, monkeypatch):
    import app
    import config._overrides as overrides
    cfg_path = str(tmp_path / "user_config.json")
    monkeypatch.setattr(app, "USER_CONFIG_PATH", cfg_path)
    monkeypatch.setattr(overrides, "USER_CONFIG_PATH", cfg_path)

    resp = client.post("/api/config", json={"not_a_section": {"x": 1}})
    assert resp.status_code == 400


# ------------------------------ applied-jobs CSV ----------------------------
_CSV_COLUMNS = ['Job ID', 'Title', 'Company', 'HR Name', 'HR Link',
                'Job Link', 'External Job link', 'Date Applied']


def _write_history_csv(folder):
    path = os.path.join(folder, "all_applied_applications_history.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_COLUMNS)
        writer.writeheader()
        writer.writerow({
            'Job ID': 'J1', 'Title': 'Engineer', 'Company': 'Acme',
            'HR Name': 'Unknown', 'HR Link': '', 'Job Link': 'http://x',
            'External Job link': 'http://ext', 'Date Applied': 'Pending',
        })
    return path


def test_applied_jobs_get_maps_columns_to_json_keys(client, tmp_path, monkeypatch):
    import app
    monkeypatch.setattr(app, "PATH", str(tmp_path) + os.sep)
    _write_history_csv(str(tmp_path))

    resp = client.get("/applied-jobs")
    assert resp.status_code == 200
    row = resp.get_json()[0]
    assert row["Job_ID"] == "J1"
    assert row["Title"] == "Engineer"
    assert row["External_Job_link"] == "http://ext"
    assert row["Date_Applied"] == "Pending"


def test_applied_jobs_mark_applied_updates_date(client, tmp_path, monkeypatch):
    import app
    monkeypatch.setattr(app, "PATH", str(tmp_path) + os.sep)
    _write_history_csv(str(tmp_path))

    resp = client.put("/applied-jobs/J1")
    assert resp.status_code == 200

    row = client.get("/applied-jobs").get_json()[0]
    assert row["Date_Applied"] != "Pending"


def test_applied_jobs_missing_file_returns_404(client, tmp_path, monkeypatch):
    import app
    monkeypatch.setattr(app, "PATH", str(tmp_path) + os.sep)  # empty dir, no CSV
    assert client.get("/applied-jobs").status_code == 404


def test_applied_jobs_mark_unknown_id_returns_404(client, tmp_path, monkeypatch):
    import app
    monkeypatch.setattr(app, "PATH", str(tmp_path) + os.sep)
    _write_history_csv(str(tmp_path))
    assert client.put("/applied-jobs/does-not-exist").status_code == 404


# ------------------------------- bot status ---------------------------------
def test_status_reports_not_running(client):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    assert resp.get_json()["running"] is False


# ------------------------------- pages render -------------------------------
def test_control_panel_and_history_pages_render(client):
    assert client.get("/").status_code == 200
    assert client.get("/history").status_code == 200
