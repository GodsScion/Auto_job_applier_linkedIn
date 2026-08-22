'''
Author:     Sai Vignesh Golla
License:    MIT License
            https://opensource.org/license/mit
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Describes every user-editable setting that the local control panel (app.py +
templates/control_panel.html) exposes in the browser.

The panel NEVER edits the config/*.py files. It reads and writes only
`user_config.json` at the project root, which the config/*.py modules load and
apply over their built-in defaults (see config/_overrides.py). This schema is
the single source of truth the web UI renders forms from.

Each field is a dict:
    {
      "section":       tab it appears under in the UI (Account, Profile, ...),
      "config_module": the config/*.py module the setting lives in. This is ALSO
                       the key used for it inside user_config.json, so it must
                       match the module name exactly (secrets, personals,
                       questions, search, settings),
      "key":           the variable name in that module,
      "label":         short human label,
      "type":          one of text, password, textarea, number, bool, select, list,
      "help":          plain-language explanation (from the config comments),
      "options":       list of allowed values (select fields only),
      "advanced":      (optional) True -> shown under a collapsible "Advanced
                       options" section so the default view stays simple,
      "ai":            (optional) True -> the field only matters when "Use AI" is
                       on, so the UI disables it while AI is turned off,
      "models_by_provider": (optional) suggestions for the model field, keyed by
                       AI provider; the UI shows them as a dropdown but still
                       accepts any typed-in model name,
    }

Field types:
    text      - single line of text
    password  - single line, masked in the browser (with a show/hide toggle)
    textarea  - multi-line text
    number    - stored as a number (int/float), not quoted
    bool      - True / False checkbox
    select    - pick one from "options"
    list      - comma-separated text in the UI, stored as a JSON list
'''


# Suggested model names per provider. These are only suggestions shown in a
# dropdown; any model name can still be typed in, since providers add and rename
# models often. Local models (Ollama / LM Studio) use the "openai" provider.
AI_MODELS = {
    "openai": [
        "gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "o4-mini",
        "gpt-5", "gpt-5-mini",
        "llama-3.2-3b-instruct", "qwen2.5:latest",
    ],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
    "gemini": [
        "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash",
        "gemini-1.5-flash", "gemini-1.5-pro",
    ],
}


def _f(section, config_module, key, label, ftype, help,
       options=None, advanced=False, ai=False, models_by_provider=None):
    field = {
        "section": section,
        "config_module": config_module,
        "key": key,
        "label": label,
        "type": ftype,
        "help": help,
    }
    if options is not None:
        field["options"] = options
    if advanced:
        field["advanced"] = True
    if ai:
        field["ai"] = True
    if models_by_provider is not None:
        field["models_by_provider"] = models_by_provider
    return field


# ---------------------------------------------------------------------------
# The schema, grouped into tabs. Each tab is {"section", "fields": [...]}.
# Within a tab, fields marked advanced=True are tucked into a collapsible
# "Advanced options" section by the UI so the everyday view stays simple.
# ---------------------------------------------------------------------------
SCHEMA = [
    {
        "section": "Account",
        "fields": [
            _f("Account", "secrets", "username", "LinkedIn email", "text",
               "The email address you sign in to LinkedIn with. Optional - if left blank the tool tries the browser's saved login, and asks you to log in by hand if that fails."),
            _f("Account", "secrets", "password", "LinkedIn password", "password",
               "Your LinkedIn password. Stored only on this computer in user_config.json (never uploaded anywhere). Optional - leave blank to log in manually."),
            _f("Account", "secrets", "use_AI", "Use AI", "bool",
               "Master switch for AI help (tailoring answers, resumes and cover letters). Turn this on only if you have a paid API key or a local AI model running. While it's off, all the AI settings below are disabled."),
            _f("Account", "secrets", "ai_provider", "AI provider", "select",
               "Which AI service to use. Pick 'openai' for OpenAI or any OpenAI-compatible service (including local ones like Ollama or LM Studio), 'deepseek' for DeepSeek, or 'gemini' for Google Gemini.",
               options=["openai", "deepseek", "gemini"], ai=True),
            _f("Account", "secrets", "llm_model", "AI model", "text",
               "The model to use. Pick a suggestion from the list or type any model name your provider supports.",
               ai=True, models_by_provider=AI_MODELS),
            _f("Account", "secrets", "llm_api_key", "AI API key", "password",
               "Your AI service API key. Use 'not-needed' for local models like Ollama. A wrong key causes errors while AI is on.",
               ai=True),
            # --- advanced AI plumbing ---
            _f("Account", "secrets", "llm_api_url", "AI API URL", "text",
               "The address of your AI service. Examples: https://api.openai.com/v1/ , http://localhost:1234/v1/ , https://api.deepseek.com . Keep the trailing slash. You may not need this for Gemini.",
               ai=True, advanced=True),
            _f("Account", "settings", "showAiErrorAlerts", "Show AI error alerts", "bool",
               "Pop up an alert if there's a problem connecting to the AI service.",
               ai=True, advanced=True),
        ],
    },
    {
        "section": "Profile",
        "fields": [
            # --- everyday details ---
            _f("Profile", "personals", "first_name", "First name", "text",
               "Your legal first name."),
            _f("Profile", "personals", "middle_name", "Middle name", "text",
               "Your middle name. Leave blank if you don't have one."),
            _f("Profile", "personals", "last_name", "Last name", "text",
               "Your legal last name."),
            _f("Profile", "personals", "phone_number", "Phone number", "text",
               "A valid phone number. Applications often require this."),
            _f("Profile", "personals", "current_city", "Current city", "text",
               "The city you live in. If left blank, the tool fills in the job's location instead."),
            _f("Profile", "questions", "years_of_experience", "Years of experience", "text",
               "What to answer for 'how many years of experience do you have' questions. A number in text, e.g. 0, 1, 3, 5."),
            _f("Profile", "questions", "require_visa", "Need visa sponsorship?", "select",
               "Do you need visa sponsorship now or in the future?",
               options=["Yes", "No"]),
            _f("Profile", "questions", "us_citizenship", "Citizenship status", "select",
               "Your work-authorization / citizenship status for US applications.",
               options=["U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident", "Other"]),
            _f("Profile", "questions", "desired_salary", "Desired salary", "number",
               "Your expected salary or CTC as a plain number (no currency symbols or commas), e.g. 100000. Some forms only accept numbers."),
            _f("Profile", "questions", "current_ctc", "Current salary", "number",
               "Your current salary or CTC as a plain number, e.g. 80000."),
            _f("Profile", "questions", "notice_period", "Notice period (days)", "number",
               "Your notice period in days, e.g. 0, 15, 30. The tool converts to weeks or months if a form asks that way."),
            _f("Profile", "questions", "linkedIn", "LinkedIn profile URL", "text",
               "The link to your LinkedIn profile, e.g. https://www.linkedin.com/in/yourname ."),
            _f("Profile", "questions", "website", "Portfolio website", "text",
               "Link to your portfolio or personal website. Leave blank to skip this question."),
            _f("Profile", "questions", "default_resume_path", "Default resume path", "text",
               "Path to the resume file to upload, relative to the project folder, e.g. all resumes/default/resume.pdf . If the file is missing, the tool keeps your last resume on LinkedIn."),
            # --- advanced / less-common details ---
            _f("Profile", "personals", "street", "Street address", "text",
               "Your street address. Some applications require it.", advanced=True),
            _f("Profile", "personals", "state", "State / region", "text",
               "Your state or region.", advanced=True),
            _f("Profile", "personals", "zipcode", "ZIP / postal code", "text",
               "Your ZIP or postal code.", advanced=True),
            _f("Profile", "personals", "country", "Country", "text",
               "The country you live in.", advanced=True),
            _f("Profile", "personals", "ethnicity", "Ethnicity / race", "select",
               "Used for optional US equal-opportunity questions. Choose 'Decline' to prefer not to answer. A blank leaves the question unanswered, but some companies make it required.",
               options=["", "Decline", "Hispanic/Latino", "American Indian or Alaska Native", "Asian", "Black or African American", "Native Hawaiian or Other Pacific Islander", "White", "Other"], advanced=True),
            _f("Profile", "personals", "gender", "Gender", "select",
               "Used for optional equal-opportunity questions. Choose 'Decline' to prefer not to answer, or leave blank to skip (some companies require it).",
               options=["", "Male", "Female", "Other", "Decline"], advanced=True),
            _f("Profile", "personals", "disability_status", "Disability status", "select",
               "Do you have, or have a record of, a disability? Choose 'Decline' to prefer not to answer.",
               options=["Yes", "No", "Decline"], advanced=True),
            _f("Profile", "personals", "veteran_status", "Veteran status", "select",
               "Your veteran status. Choose 'Decline' to prefer not to answer.",
               options=["Yes", "No", "Decline"], advanced=True),
            _f("Profile", "questions", "linkedin_headline", "LinkedIn headline", "text",
               "A short professional headline, e.g. 'Full Stack Developer, MSc Computer Science, 4+ years experience'. Leave blank to skip.", advanced=True),
            _f("Profile", "questions", "linkedin_summary", "LinkedIn summary", "textarea",
               "A few sentences about your background and skills. Used to answer 'tell us about yourself' style questions. Leave blank to skip.", advanced=True),
            _f("Profile", "questions", "cover_letter", "Cover letter", "textarea",
               "A default cover letter to submit when one is requested. Leave blank to skip.", advanced=True),
            _f("Profile", "questions", "recent_employer", "Most recent employer", "text",
               "The name of your most recent employer.", advanced=True),
            _f("Profile", "questions", "confidence_level", "Confidence level (1-10)", "text",
               "For 'on a scale of 1-10, how much experience...' questions. Any number from 1 to 10.", advanced=True),
        ],
    },
    {
        "section": "Search",
        "fields": [
            _f("Search", "search", "search_terms", "Search terms", "list",
               "Job titles to search for, separated by commas, e.g. Software Engineer, Python Developer, Full Stack Developer."),
            _f("Search", "search", "search_location", "Search location", "text",
               "Where to look for jobs. Examples: United States, India, 'Chicago, Illinois, United States'. Leave blank to not set a location."),
            _f("Search", "search", "date_posted", "Date posted", "select",
               "Only include jobs posted within this window. Leave blank to not filter by date.",
               options=["", "Any time", "Past month", "Past week", "Past 24 hours"]),
            _f("Search", "search", "easy_apply_only", "Easy Apply only", "bool",
               "Only apply to jobs that use LinkedIn's Easy Apply. Recommended on."),
            _f("Search", "search", "experience_level", "Experience level", "list",
               "Filter by experience level, comma-separated. Valid values: Internship, Entry level, Associate, Mid-Senior level, Director, Executive. Leave blank for all."),
            _f("Search", "search", "job_type", "Job type", "list",
               "Filter by job type, comma-separated. Valid values: Full-time, Part-time, Contract, Temporary, Volunteer, Internship, Other. Leave blank for all."),
            _f("Search", "search", "on_site", "On-site / Remote", "list",
               "Filter by work setting, comma-separated. Valid values: On-site, Remote, Hybrid. Leave blank for all."),
            _f("Search", "search", "current_experience", "Your years of experience", "number",
               "Your actual years of experience. Jobs asking for more than this are skipped. Set to -1 to ignore required experience and apply to everything."),
            # --- advanced search options ---
            _f("Search", "search", "switch_number", "Applications before switching term", "number",
               "How many applications to submit for one search term before moving on to the next. A number greater than 0.", advanced=True),
            _f("Search", "search", "randomize_search_order", "Randomize search order", "bool",
               "Shuffle the order your search terms are used.", advanced=True),
            _f("Search", "search", "sort_by", "Sort results by", "select",
               "How LinkedIn should sort results. Leave blank to not change it.",
               options=["", "Most recent", "Most relevant"], advanced=True),
            _f("Search", "search", "salary", "Minimum salary", "select",
               "Only include jobs at or above this salary. Leave blank to not filter by salary.",
               options=["", "$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+"], advanced=True),
            _f("Search", "search", "companies", "Only these companies", "list",
               "Only apply at these companies, comma-separated. Names must match LinkedIn exactly (including capitals). Leave blank for all companies.", advanced=True),
            _f("Search", "search", "did_masters", "I have a master's degree", "bool",
               "If on, jobs mentioning 'master' are still considered when their required experience is within about 2 years of yours.", advanced=True),
            _f("Search", "search", "security_clearance", "I have a security clearance", "bool",
               "Whether you hold an active security clearance.", advanced=True),
            _f("Search", "search", "under_10_applicants", "Under 10 applicants only", "bool",
               "Only apply to jobs with fewer than 10 applicants so far.", advanced=True),
            _f("Search", "search", "in_your_network", "In your network only", "bool",
               "Only apply to jobs at companies where you have a connection.", advanced=True),
            _f("Search", "search", "fair_chance_employer", "Fair-chance employers only", "bool",
               "Only apply to employers who identify as fair-chance employers.", advanced=True),
        ],
    },
    {
        "section": "Filters",
        "fields": [
            _f("Filters", "search", "about_company_bad_words", "Skip companies with these words", "list",
               "Skip a company if any of these words appear in its 'About company' section, comma-separated. Example: Staffing, Recruiting."),
            _f("Filters", "search", "about_company_good_words", "Keep companies with these words", "list",
               "Exceptions to the list above: apply anyway if the 'About company' section contains one of these words, comma-separated. Example: Robert Half."),
            _f("Filters", "search", "bad_words", "Skip jobs with these words", "list",
               "Skip a job if any of these words or phrases appear in its description, comma-separated and case-insensitive. Example: US Citizen, No C2C, PHP."),
        ],
    },
    {
        "section": "Run settings",
        "fields": [
            _f("Run settings", "settings", "run_in_background", "Run in background", "bool",
               "Hide the Chrome window while it works. Note: turning this on disables the 'pause before submit' and 'pause on hard questions' safety pauses."),
            _f("Run settings", "questions", "pause_before_submit", "Pause before submitting", "bool",
               "Pause on the final screen of each application so you can review it before it's sent. Recommended on. Ignored when 'Run in background' is on."),
            _f("Run settings", "questions", "pause_at_failed_question", "Pause on hard questions", "bool",
               "Pause and wait for you when the tool can't confidently answer a question. If off, it answers randomly. Ignored when 'Run in background' is on."),
            # --- advanced run options ---
            _f("Run settings", "settings", "auto_manage_driver", "Manage Chrome driver automatically", "bool",
               "Let the tool download and match the right Chrome driver for you. Recommended on so you don't have to install it yourself.", advanced=True),
            _f("Run settings", "settings", "safe_mode", "Safe mode", "bool",
               "Open Chrome in a clean guest profile. Turn on if Chrome is slow to start or you have several browser profiles.", advanced=True),
            _f("Run settings", "settings", "click_gap", "Pause between clicks (seconds)", "number",
               "Roughly how many seconds to wait between actions. A whole number, e.g. 0, 1, 2.", advanced=True),
            _f("Run settings", "settings", "keep_screen_awake", "Keep screen awake", "bool",
               "Stop your computer from sleeping while the tool runs. Turn off if you'd rather manage sleep in your system settings.", advanced=True),
            _f("Run settings", "settings", "close_tabs", "Close external application tabs", "bool",
               "Close tabs opened for external (non-Easy-Apply) applications. If off, remember to close all tabs before closing the browser.", advanced=True),
            _f("Run settings", "settings", "follow_companies", "Follow companies after applying", "bool",
               "Automatically follow a company on LinkedIn after applying to it.", advanced=True),
            _f("Run settings", "questions", "overwrite_previous_answers", "Overwrite saved answers", "bool",
               "Replace answers you've previously entered on LinkedIn with the ones configured here.", advanced=True),
        ],
    },
]


def iter_fields():
    '''Yield every field dict across all sections, in order.'''
    for section in SCHEMA:
        for field in section["fields"]:
            yield field


def valid_keys():
    '''
    Return a mapping {config_module: {key: field}} of every editable setting.
    Used by the API to validate and coerce incoming values and reject unknown
    keys.
    '''
    mapping = {}
    for field in iter_fields():
        mapping.setdefault(field["config_module"], {})[field["key"]] = field
    return mapping
