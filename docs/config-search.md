# `config/search.py` — what to search for, and what to skip

These settings decide **which jobs the tool applies to**. Open `config/search.py`, or use
the **Search** and **Filters** tabs of the control panel.

## Search terms

| Setting | What it is |
|---|---|
| `search_terms` | A list of the phrases to search LinkedIn for, e.g. `["Software Engineer", "Python Developer"]` |
| `search_location` | Goes into the "City, state, or zip code" box. `""` leaves it unfilled. Examples: `"United States"`, `"Chicago, Illinois, United States"`, `"90001, Los Angeles, California, United States"`, `"Bengaluru, Karnataka, India"` |
| `switch_number` | How many applications to make on one search term before moving to the next. Any number greater than 0, no quotes |
| `randomize_search_order` | `True` or `False`. Shuffles the order of `search_terms` |

## LinkedIn job filters

These map one-to-one onto LinkedIn's own filter controls. Leave a filter empty to not
select it — `""` for single-choice filters, `[]` for list filters. `True`/`False` filters
cannot be left empty.

| Setting | Kind | Valid values |
|---|---|---|
| `sort_by` | single | `"Most recent"`, `"Most relevant"`, or `""` |
| `date_posted` | single | `"Any time"`, `"Past month"`, `"Past week"`, `"Past 24 hours"`, or `""` |
| `salary` | single | `"$40,000+"` through `"$200,000+"` in $20,000 steps, or `""` |
| `easy_apply_only` | bool | `True` or `False` |
| `experience_level` | multiple | `"Internship"`, `"Entry level"`, `"Associate"`, `"Mid-Senior level"`, `"Director"`, `"Executive"` |
| `job_type` | multiple | `"Full-time"`, `"Part-time"`, `"Contract"`, `"Temporary"`, `"Volunteer"`, `"Internship"`, `"Other"` |
| `on_site` | multiple | `"On-site"`, `"Remote"`, `"Hybrid"` |
| `companies` | dynamic multiple | Company names, matched exactly including capitals, e.g. `["Google", "JPMorgan Chase & Co."]` |
| `location` | dynamic multiple | |
| `industry` | dynamic multiple | |
| `job_function` | dynamic multiple | |
| `job_titles` | dynamic multiple | |
| `benefits` | dynamic multiple | |
| `commitments` | dynamic multiple | |
| `under_10_applicants` | bool | `True` or `False` |
| `in_your_network` | bool | `True` or `False` |
| `fair_chance_employer` | bool | `True` or `False` |

A **multiple** select takes only values from the listed options. A **dynamic multiple**
select takes anything — the entries do not have to match a fixed list.

| Setting | Default | What it does |
|---|---|---|
| `pause_after_filters` | `True` | Pause once the filters are applied so you can adjust the search and results by hand before the tool starts applying |

## Skipping irrelevant jobs

| Setting | What it does |
|---|---|
| `about_company_bad_words` | Skip a company if any of these words appear in its **About company** section. Example: `["Staffing", "Recruiting"]` |
| `about_company_good_words` | Exceptions to the list above — apply anyway if the About company section contains one of these. Example: `["Robert Half", "Dice"]` |
| `bad_words` | Skip a job if any of these words or phrases appear in its **job description**. Case-insensitive, matched as whole words/phrases. Example: `["US Citizen", "No C2C", "PHP", "polygraph", "Security Clearance"]` |
| `security_clearance` | `False` means "I do not hold a clearance", and jobs mentioning clearance or polygraph are skipped. Matched as whole words, so "clearance sale" and "secretary" do not trigger it |
| `did_masters` | `True` means you have a Master's degree. Jobs whose description contains the word "master" are then allowed up to `current_experience + 2` years of required experience |
| `current_experience` | Skip jobs requiring more years than this. Set to `-1` to apply regardless of required experience. This is separate from `years_of_experience` in [`config/questions.py`](config-questions.md), which is only what gets typed into the form |

## Visa sponsorship filtering

Four settings, and they only matter to people who need sponsorship.

> **All four are inert unless [`require_visa = "Yes"`](config-questions.md#work-authorization)
> in `config/questions.py`.** If you do not need sponsorship, they cost you nothing and
> change nothing.

| Setting | Default | What it does |
|---|---|---|
| `skip_non_sponsoring_jobs` | `False` | Skip a job when its description says sponsorship is **not** available. A description that says nothing about sponsorship is still applied to |
| `sponsorship_offered_phrases` | a starter list | Phrases meaning "we DO sponsor". Checked **first**, and an offer always wins. Real postings say both — "we do not require you to have sponsorship... we will sponsor H-1B transfers" is an offer, not a refusal |
| `sponsorship_unavailable_phrases` | a starter list | Phrases meaning "we do NOT sponsor". Matched as **whole phrases, never substrings**, so "sponsorship of our annual conference" and "sponsored content" are safe |
| `skip_jobs_without_sponsorship` | `False` | **Strict mode.** Also skip jobs whose description says nothing either way. Only does anything when `skip_non_sponsoring_jobs` is also `True` |

Both phrase lists are ordinary lists you can edit and extend. Matching is case-insensitive.

### About strict mode

`skip_jobs_without_sponsorship = True` means "apply only where sponsorship is affirmatively
offered". **Most postings never mention sponsorship at all, so this skips a LOT of jobs,
including many employers who would in fact have sponsored you.** Silence is not a refusal.
Recall is worst for exactly the seed and Series-A companies most likely to be silent yet
sponsor, which is why it is off by default.

Why anyone turns it on: LinkedIn caps Easy Apply at roughly 25 applications a day, so your
applications are a rationed daily resource. If your runs end by hitting that daily limit, a
slot spent on a silent posting is a slot denied to one that says "we sponsor". **If your
runs never hit the cap, leave this off** — every skip is then pure loss.

Only the text of the posting itself is read. Whether the employer has ever sponsored anyone
before is deliberately not consulted; absence from that kind of data is not evidence.

---

[← Back to docs index](README.md) · [Configuration overview](configuration.md)
