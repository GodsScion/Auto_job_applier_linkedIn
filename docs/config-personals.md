# `config/personals.py` — your details

The answers that go into the "about you" fields of an application. Open
`config/personals.py` and fill these in, or use the **Profile** tab of the control panel.

## Name and contact

| Setting | What it is |
|---|---|
| `first_name` | Your legal first name, e.g. `"Sai"` |
| `middle_name` | Middle name, or `""` if you do not have one |
| `last_name` | Legal last name |
| `phone_number` | Ten digits in quotes, e.g. `"9876543210"`. Required, and it must be valid |

## Location

| Setting | What it is |
|---|---|
| `current_city` | e.g. `"Austin"`. **If left empty as `""`, the tool answers with the city given in the job posting** — which is usually what you want for "what is your current location?" questions |
| `street` | Street address. Uncommon, but some applications require it |
| `state` | e.g. `"Texas"` |
| `zipcode` | Postal code |
| `country` | e.g. `"United States"` |

## US Equal Opportunity questions

Each of these can be left as `""` to leave the question unanswered — but note that some
companies make them compulsory.

| Setting | Valid values |
|---|---|
| `ethnicity` | `"Decline"`, `"Hispanic/Latino"`, `"American Indian or Alaska Native"`, `"Asian"`, `"Black or African American"`, `"Native Hawaiian or Other Pacific Islander"`, `"White"`, `"Other"` or `""` |
| `gender` | `"Male"`, `"Female"`, `"Other"`, `"Decline"` or `""` |
| `disability_status` | `"Yes"`, `"No"`, `"Decline"` |
| `veteran_status` | `"Yes"`, `"No"`, `"Decline"` |

Answers are case-sensitive and must be one of the listed options. Free-text settings (name,
address) have no restriction other than the quotes.

---

[← Back to docs index](README.md) · [Configuration overview](configuration.md)
