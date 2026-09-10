# Configuration

All configuration lives in the `config/` folder as plain Python files. There are two ways
to change it, and they work together:

- **The control panel** (`python app.py`, or the `start.*` launcher) — a local web page
  with the common settings laid out in tabs: **Account, Profile, Search, Filters, Run
  settings**. What you save there is written to `user_config.json` at the project root.
- **Editing `config/*.py` directly** — the classic route, and the only route for the
  handful of settings the control panel does not expose.

`user_config.json` is applied *over* the defaults in `config/*.py`, and only for names that
already exist there — so the panel can never introduce a setting the code does not know
about. If `user_config.json` does not exist, everything comes from the `.py` files and the
tool behaves exactly as it always has. Nothing is ever uploaded anywhere.

## Do it in this order

| Step | File | What goes in it |
|---|---|---|
| 1 | [`config/personals.py`](config-personals.md) | Your name, phone, address, and the equal-opportunity answers |
| 2 | [`config/questions.py`](config-questions.md) | Answers to Easy Apply questions: experience, work authorization, salary, notice period, resume path |
| 3 | [`config/search.py`](config-search.md) | What to search for, which filters to apply, and which jobs to skip |
| 4 | [`config/secrets.py`](config-secrets.md) | LinkedIn login (optional) and the optional AI setup |
| 5 | [`config/settings.py`](config-settings.md) | How the bot itself runs: click gap, background mode, screen awake, driver management |

Then run `runAiBot.py` and watch it work. Or run `app.py` for the control panel, which also
shows your Applied Jobs history.

## Rules that apply to every config file

- Values are **case-sensitive**. `True` and `False` must be capitalised exactly like that.
- Strings need quotes: `"like this"`. Numbers do not: `desired_salary = 120000`.
- A **multiple select** setting takes a list: `["answer1", "answer2"]`. Leave it as `[]` to
  select nothing.
- A **dynamic multiple select** takes a list too, but the entries do not have to match a
  fixed set of options.
- A single-select setting takes one string, or `""` to leave the question unanswered.
  Beware: some companies make a question compulsory, and an unanswered compulsory question
  will make the application fail or pause.
- Invalid values raise a validation error on startup rather than failing halfway through a
  run. See `modules/validator.py`.

## Not everything is in the control panel

These are set by editing the `.py` file, and have no control-panel field:

| Setting | File | Page |
|---|---|---|
| `stop_before_submit` | `config/settings.py` | [Settings](config-settings.md#dry-runs-stop_before_submit) |
| `legally_authorized` | `config/questions.py` | [Questions](config-questions.md#work-authorization) |
| `comfortable_commuting` | `config/questions.py` | [Questions](config-questions.md#commuting) |

---

[← Back to docs index](README.md)
