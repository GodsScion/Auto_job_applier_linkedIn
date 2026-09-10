'''
Author:     Sai Vignesh Golla
License:    MIT License
            https://opensource.org/license/mit
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

The field schema the local control panel (app.py + templates/control_panel.html)
renders its forms from, DERIVED from config/*.py rather than hand-copied.

config/*.py is the single source of truth. This module parses those files with
`ast` and turns every top-level literal assignment into a form field:

  * the comment lines directly ABOVE an assignment - plus a triple-quoted note
    right below it - become the field's help text,
  * the trailing comment lists the legal values, so
    `require_visa = "No"   # "Yes" or "No"` becomes a dropdown,
  * the literal's type picks the control: bool -> checkbox, int -> number,
    list -> comma-separated, a string with line breaks -> textarea,
  * `# >>>>> Something <<<<<` headers group the settings inside a file.

Nothing about a setting is written down twice, so nothing can drift out of sync.
The only things kept here are the ones that exist ONLY in the browser and have
no home in a config file: which tab a setting belongs to, whether it hides under
"Advanced options", and whether it is an AI-only field.

The panel NEVER edits config/*.py. It reads and writes only `user_config.json`,
which those modules load over their defaults (see config/_overrides.py).

Each derived field is a dict:
    {"section", "config_module", "key", "label", "type", "help",
     "options"?, "step"?, "advanced"?, "ai"?, "models_by_provider"?}

Field types:
    text / password / textarea / number / bool / select / list
'''

import ast
import os
import re

_CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")

# The config files, in the order the docs tell people to fill them in.
MODULES = ("secrets", "personals", "questions", "search", "settings")

# Tabs, in the order the panel shows them.
TAB_ORDER = ("Account", "Profile", "Search", "Filters", "Run settings")

# Which tab a file's settings land on, plus the two `>>>>> ... <<<<<` groups and
# the one setting that belong somewhere other than their file's tab.
TAB_BY_MODULE = {"secrets": "Account", "personals": "Profile", "questions": "Profile",
                 "search": "Search", "settings": "Run settings"}
TAB_BY_GROUP = {("questions", "RELATED SETTINGS"): "Run settings",
                ("search", "SKIP IRRELEVANT JOBS"): "Filters"}
TAB_BY_KEY = {"showAiErrorAlerts": "Account"}   # an AI switch that lives in settings.py

# Tucked under the collapsible "Advanced options" block, so the everyday view stays short.
ADVANCED = {
    "llm_api_url", "local_llm_api_url", "local_llm_model", "showAiErrorAlerts",
    "street", "state", "zipcode", "country",
    "ethnicity", "gender", "disability_status", "veteran_status",
    "linkedin_headline", "linkedin_summary", "cover_letter", "user_information_all",
    "recent_employer", "confidence_level", "overwrite_previous_answers",
    "switch_number", "randomize_search_order", "sort_by", "salary", "companies",
    "location", "industry", "job_function", "job_titles", "benefits", "commitments",
    "did_masters", "security_clearance", "under_10_applicants", "in_your_network",
    "fair_chance_employer", "pause_after_filters",
    "close_tabs", "follow_companies", "run_non_stop", "alternate_sortby",
    "cycle_date_posted", "stop_date_cycle_at_24hr", "generated_resume_path",
    "file_name", "failed_file_name", "logs_folder_path", "log_level", "click_gap",
    "disable_extensions", "safe_mode", "smooth_scroll", "keep_screen_awake",
    "auto_manage_driver",
}

# Only meaningful while "Use AI" is on; the panel greys these out while it is off.
AI_FIELDS = {"ai_provider", "llm_model", "llm_api_key", "llm_api_url",
             "local_llm_api_url", "local_llm_model", "user_information_all",
             "showAiErrorAlerts"}

# Labels that read badly when derived from the variable name.
LABELS = {"username": "LinkedIn email", "password": "LinkedIn password", "use_AI": "Use AI",
          "ai_provider": "AI provider", "llm_model": "AI model", "llm_api_key": "AI API key",
          "llm_api_url": "AI API URL", "local_llm_api_url": "Local AI server URL",
          "local_llm_model": "Local AI model", "showAiErrorAlerts": "Show AI error alerts",
          "linkedIn": "LinkedIn profile URL", "linkedin_headline": "LinkedIn headline",
          "linkedin_summary": "LinkedIn summary", "us_citizenship": "Citizenship status",
          "require_visa": "Need visa sponsorship?", "current_ctc": "Current salary",
          "did_masters": "I have a master's degree"}

# Suggested model names per provider. Only suggestions shown in a dropdown; any model
# name can still be typed in, since providers add and rename models often. Local models
# (Ollama / LM Studio) use the "openai" provider.
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

_GROUP = re.compile(r"#+\s*>{3,}\s*(.*?)\s*<{3,}")      # `# >>>>> Job Search Filters <<<<<`
_BANNER = re.compile(r"^#*\s*$|>{3}|<{3}|^#{3,}")       # separator lines, not help
_QUOTED = re.compile(r'"([^"]*)"')
# A trailing comment listing EXAMPLES is not a list of legal values.
_EXAMPLE = re.compile(r"\beg:|\be\.g|\bex:|example|and so on|etc\b", re.IGNORECASE)


def _label(key):
    '''"phone_number" -> "Phone number", "showAiErrorAlerts" -> "Show Ai Error Alerts".'''
    if key in LABELS:
        return LABELS[key]
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", key.replace("_", " "))
    return text[0].upper() + text[1:]


def _help_above(lines, index):
    '''The comment block directly above 0-based line `index`, as one paragraph.'''
    block = []
    index -= 1
    while index >= 0 and lines[index].startswith("#"):
        if not _BANNER.search(lines[index]):
            block.append(lines[index].lstrip("#").strip())
        index -= 1
    return " ".join(reversed(block))


def _note_below(body, position, assign):
    '''A triple-quoted note written right under an assignment, e.g. the "in lakhs"
    worked examples under `desired_salary`. Anything further down the file belongs
    to the next section, not to this setting.'''
    following = body[position + 1] if position + 1 < len(body) else None
    if (isinstance(following, ast.Expr) and isinstance(following.value, ast.Constant)
            and isinstance(following.value.value, str)
            and following.lineno - assign.end_lineno <= 2):
        return " ".join(following.value.value.split())
    return ""


def _options(trailing):
    '''Legal values from a trailing comment like `# "Yes" or "No"`, blank first.'''
    if _EXAMPLE.search(trailing):
        return []
    found = _QUOTED.findall(trailing)
    if len(found) < 2:
        return []
    if "" in found:
        found = [""] + [option for option in found if option != ""]
    return found


def _field(module, key, default, help_text, trailing, group):
    field = {
        "section": TAB_BY_KEY.get(key) or TAB_BY_GROUP.get((module, group))
                   or TAB_BY_MODULE[module],
        "config_module": module,
        "key": key,
        "label": _label(key),
        "type": "text",
        "help": help_text,
    }
    options = _options(trailing)
    if isinstance(default, bool):
        field["type"] = "bool"
    elif isinstance(default, (int, float)):
        field["type"] = "number"
        # Every numeric setting is a whole number today; `step` says so to the browser
        # and to app.py, which rejects 1.5 the same way modules/validator.py does.
        field["step"] = 1 if isinstance(default, int) else "any"
    elif isinstance(default, list):
        field["type"] = "list"
    elif "password" in key or key.endswith("api_key"):
        field["type"] = "password"
    elif "\n" in default:
        field["type"] = "textarea"
    elif options:
        field["type"] = "select"
    if options:
        field["options"] = options
    if key in ADVANCED:
        field["advanced"] = True
    if key in AI_FIELDS:
        field["ai"] = True
    if key == "llm_model":
        field["models_by_provider"] = AI_MODELS
    return field


def _parse(module):
    '''Every top-level literal assignment in config/<module>.py, as a field dict.'''
    with open(os.path.join(_CONFIG_DIR, module + ".py"), encoding="utf-8") as handle:
        source = handle.read()
    lines = source.splitlines()
    body = ast.parse(source).body
    groups, group = [], ""          # the `>>>>> ... <<<<<` header each line sits under
    for line in lines:
        found = _GROUP.match(line.strip())
        group = found.group(1) if found else group
        groups.append(group)
    fields = []
    for position, node in enumerate(body):
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            continue
        key = node.targets[0].id
        try:
            default = ast.literal_eval(node.value)
        except ValueError:
            continue                    # an import or an expression, not a setting
        if key.startswith("_") or default is None:
            continue                    # `None` carries no type a form control can render
        # Bytes, because ast column offsets are UTF-8 offsets and comments carry emoji.
        end = lines[node.value.end_lineno - 1].encode("utf-8")
        trailing = end[node.value.end_col_offset:].decode("utf-8").strip()
        help_text = " ".join(filter(None, [_help_above(lines, node.lineno - 1),
                                           _note_below(body, position, node)]))
        fields.append(_field(module, key, default, help_text, trailing,
                             groups[node.lineno - 1]))
    return fields


def _build():
    fields = [field for module in MODULES for field in _parse(module)]
    return [{"section": tab, "fields": [f for f in fields if f["section"] == tab]}
            for tab in TAB_ORDER]


SCHEMA = _build()


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
