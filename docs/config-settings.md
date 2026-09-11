# `config/settings.py` — how the bot runs

Behaviour of the tool itself, rather than what it says in an application. Mostly the
**Run settings** tab of the control panel.

## LinkedIn behaviour

| Setting | Default | What it does |
|---|---|---|
| `close_tabs` | `False` | Whether to close the tabs opened for external (non-Easy-Apply) applications. **If you set this to `False`, close all tabs before closing the browser.** |
| `follow_companies` | `False` | Follow a company when submitting an Easy Apply application to it |

## Continuous running (beta)

| Setting | Default | What it does |
|---|---|---|
| `run_non_stop` | `False` | Keep running until you stop it. **Treated as `False` when `run_in_background = True`** |
| `alternate_sortby` | `True` | Alternate the "sort by" filter between runs |
| `cycle_date_posted` | `True` | Cycle through the "date posted" filter between runs |
| `stop_date_cycle_at_24hr` | `True` | Stop that cycle at "Past 24 hours" rather than going wider |

## Files and logs

| Setting | What it is |
|---|---|
| `file_name` | Where the applied-jobs history CSV is written, e.g. `"all excels/all_applied_applications_history.csv"`. Everything after the last `/` is the filename |
| `failed_file_name` | Same, for failed applications |
| `logs_folder_path` | Where run logs go, e.g. `"logs/"` |
| `log_level` | How much detail is written to `logs/log.txt` and printed while the tool runs: `"DEBUG"` for everything, `"INFO"` for the normal running commentary, `"WARNING"` for only what went wrong, `"ERROR"` for only crashes. Case-insensitive; anything unrecognised falls back to `"INFO"` |

## Run behaviour

| Setting | Default | What it does |
|---|---|---|
| `click_gap` | `1` | Maximum seconds to wait between clicks. Non-negative whole numbers only |
| `run_in_background` | `False` | Hide the Chrome window. May reduce performance. **Turning this on forces `pause_before_submit`, `pause_at_failed_question` and `run_non_stop` to `False`** — the safety pauses cannot work with no window to look at |
| `disable_extensions` | `False` | Disable browser extensions. Better for performance |
| `safe_mode` | `True` | Open Chrome in a clean **guest profile**. Turn this on if Chrome takes too long to open, or if you have several browser profiles |
| `smooth_scroll` | `False` | Smooth rather than instantaneous scrolling. Can reduce performance |
| `keep_screen_awake` | `True` | Keep the screen active and stop the machine sleeping. Temporarily deactivates while a dialog box is up (pause before submit, help needed on a question). The alternative is to set your OS sleep settings to Never |
| `auto_manage_driver` | `True` | Download and match the right Chrome driver automatically. If `False`, install a matching ChromeDriver yourself — see [install step 5](install.md#manual-install) |
| `showAiErrorAlerts` | `False` | Alert on errors from the AI API connection |
| `show_ai_suggestion` | `True` | Show a one-time tip at startup when you are not using AI, explaining what it answers for you and how to run a model locally for free. Set to `False` to never see it again |

## Dry runs: `stop_before_submit`

| Setting | Default | What it does |
|---|---|---|
| `stop_before_submit` | `False` | Fill in **every** application and stop at the Review step **without submitting** |

Useful for testing the tool, or for checking what it would answer before you trust it with
a real application. Each application is filled in completely, reaches the Review screen,
and is then discarded.

Two things worth knowing:

- A `stop_before_submit` stop is **not** counted as a failure. It is counted as a skip, so a
  clean dry run reads as skipped rather than as an all-failed run.
- It takes priority over `pause_before_submit` — the application is discarded before the
  confirmation dialog would appear.

`stop_before_submit` is in the **Run settings** tab, and settable by editing
`config/settings.py`.

## In development

| Setting | Status |
|---|---|
| `generated_resume_path` | Folder for generated resumes. Part of the **experimental, in-development** resume generator |
| connect_hr, connect_request_message (commented out, so not settings yet) | Would send connection requests to recruiters with an optional personalised message (LinkedIn allows only 10 personalised invitations a month without Premium) |

---

[← Back to docs index](README.md) · [Configuration overview](configuration.md)
