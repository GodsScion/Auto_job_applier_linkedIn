# Configuration

All configuration lives in the `config/` folder as plain Python files. There are two ways
to change it, and they work together:

- **The control panel** (`python app.py`, or the `start.*` launcher) — a local web page
  with the common settings laid out in tabs: **Account, Profile, Search, Filters, Run
  settings**. What you save there is written to `user_config.json` at the project root.
- **Editing `config/*.py` directly** — the classic route, and still the fullest one: the
  panel builds its own fields by reading these files, so the comments in them are the
  same help text it shows you.

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

One setting is set by editing the `.py` file and has no control-panel field:

| Setting | File | Why |
|---|---|---|
| `llm_temperature` | `config/secrets.py` | Its default is `None`, meaning "leave it to the model". No form control says "unset", and the panel would have to invent a number |

Everything else in `config/*.py` has a field. The panel derives them from these files, so
adding a setting to a `.py` file is all it takes for one to appear.

---

[← Back to docs index](README.md)
