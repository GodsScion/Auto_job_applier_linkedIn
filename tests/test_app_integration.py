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
