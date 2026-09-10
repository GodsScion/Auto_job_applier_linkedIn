# `config/questions.py` — Easy Apply answers

What the tool should say when an application asks you something. Open
`config/questions.py`, or use the **Profile** and **Run settings** tabs of the control panel.

## Resume

| Setting | What it is |
|---|---|
| `default_resume_path` | Relative path to the resume to upload, e.g. `"all resumes/default/resume.pdf"`. **Optional** — if the file is not found, the tool keeps using the resume you last uploaded to LinkedIn |

## Experience and profile

| Setting | What it is |
|---|---|
| `years_of_experience` | A number in quotes, e.g. `"6"`. This is what gets typed into "how many years of experience do you have" questions. It is **not** the same as `current_experience` in [`config/search.py`](config-search.md), which decides whether a job is skipped |
| `website` | Portfolio URL, or `""` to leave the question unanswered |
| `linkedIn` | Your LinkedIn profile URL |
| `linkedin_headline` | Your headline, e.g. `"Full Stack Developer with Masters in Computer Science and 4+ years of experience"`, or `""` |
| `linkedin_summary` | Your summary. Use `\n` for line breaks in a `"..."` string, or use `"""..."""` and write it across lines |
| `cover_letter` | Your cover letter. Same formatting rules as the summary |
| `user_information_all` | Free-form facts about you that the **AI** may use when drafting answers — name, years of experience, key skills, location, work authorization, anything an answer might need. Only used when AI is on (see [secrets](config-secrets.md)) |
| `recent_employer` | Name of your most recent employer, e.g. `"Not Applicable"` |
| `confidence_level` | `"1"` to `"10"` in quotes. Used for "on a scale of 1-10, how much experience do you have..." questions |

Leaving any of these as `""` means the question is left unanswered. Some companies make
them compulsory.

## Work authorization

These are **three different questions**, and someone on a valid work visa answers them
differently. The tool matches them in this order — sponsorship, then authorization, then
citizenship — because "sponsor a new U.S. work visa or work authorization" is a
sponsorship question, not an authorization one.

| Setting | The question it answers | Valid values |
|---|---|---|
| `require_visa` | "Will you now or in the future require sponsorship, or a new/transferred visa?" | `"Yes"` or `"No"` |
| `legally_authorized` | "Are you legally authorized to work in this country?" — i.e. do you **already** have permission (citizen, permanent resident, or a valid work visa such as H-1B or OPT) | `"Yes"` or `"No"` |
| `us_citizenship` | "What is your citizenship status?" | `"U.S. Citizen/Permanent Resident"`, `"Non-citizen allowed to work for any employer"`, `"Non-citizen allowed to work for current employer"`, `"Non-citizen seeking work authorization"`, `"Canadian Citizen/Permanent Resident"`, `"Other"`, or `""` to leave it unanswered |

> **`legally_authorized` is not the opposite of `require_visa`.** Someone on a valid work
> visa answers **`"Yes"` to both**: they are authorized to work today, and they will need a
> transfer or a new petition later.

`legally_authorized` is only settable by editing `config/questions.py` — it has no field in
the control panel. It defaults to `"Yes"`.

`require_visa = "Yes"` is also the switch that activates the sponsorship filters in
[`config/search.py`](config-search.md#visa-sponsorship-filtering). With `require_visa = "No"`
those settings do nothing at all.

## Commuting

| Setting | The question it answers | Valid values |
|---|---|---|
| `comfortable_commuting` | "Are you comfortable commuting to this job's location?" | `"Yes"` or `"No"` |

That question carries the word "location", so before this setting existed the tool
answered it with `current_city` from [`config/personals.py`](config-personals.md) — the
city typed into a Yes/No box. A Yes/No question that merely mentions a field
(location, address, name, phone, experience) is no longer answered with that field's
value; it is either answered from config or left for you.

`comfortable_commuting` is only settable by editing `config/questions.py` — it has no
field in the control panel. It defaults to `"Yes"`.

## Salary and notice period

| Setting | What it is |
|---|---|
| `desired_salary` | Numbers only, no quotes, e.g. `1200000`. Some companies only accept digits |
| `current_ctc` | Your current salary, numbers only, no quotes |
| `notice_period` | Days, no quotes, e.g. `30` |

The tool reshapes these to fit the question it is asked:

- If a salary question contains the word **"lakhs"**, a `.` is inserted before the last five
  digits — `2400000` is answered as `"24.00"`, `850000` as `"8.50"`.
- If a salary question asks **per month**, the value is divided by 12 — `2400000` is
  answered as `"200000"`, `850000` as `"70833"`.
- If a notice-period question contains **"month"** or **"week"**, the value is divided by 30
  or 7 respectively — `notice_period = 66` is answered as `"66"`, or `"2"` in months, or
  `"9"` in weeks.

## Manual-input and answer settings

| Setting | Default | What it does |
|---|---|---|
| `pause_before_submit` | `True` | Pause on the final screen of every application so you can check it before it is sent. The dialog offers **Submit Application**, **Discard Application**, or **Disable Pause** (which turns pausing off for the rest of this run only). **Treated as `False` when `run_in_background = True`** |
| `pause_at_failed_question` | `True` | Pause and wait for you when the tool cannot confidently answer a question. **If set to `False` it answers randomly.** Also treated as `False` when `run_in_background = True` |
| `overwrite_previous_answers` | `False` | The tool remembers the answer it gave to a question and reuses it. Set to `True` to overwrite a saved answer with the current config value |

For a dry run that fills everything in and stops without submitting, see
[`stop_before_submit`](config-settings.md#dry-runs-stop_before_submit).

## Not yet implemented

`currency` (the currency tag appended to salary answers for employers that accept text
input) is commented out in the file and marked *In development*.

---

[← Back to docs index](README.md) · [Configuration overview](configuration.md)
