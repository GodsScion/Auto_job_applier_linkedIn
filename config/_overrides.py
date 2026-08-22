'''
Author:     Sai Vignesh Golla
License:    MIT License
            https://opensource.org/license/mit
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Loads user settings saved by the local control panel (see app.py) from
`user_config.json` at the project root, and applies them over the Python
defaults defined in the config/*.py files.

If `user_config.json` does not exist, everything here is a no-op and the tool
behaves exactly as it always has: configuration comes entirely from the
config/*.py defaults. This keeps the classic "edit the .py files" workflow
fully working for existing users.
'''

import os
import json

# This file lives in <project_root>/config/, so the project root is one level up.
_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_CONFIG_DIR)
USER_CONFIG_PATH = os.path.join(_ROOT_DIR, "user_config.json")


def load_user_config() -> dict:
    '''
    Returns the full override dictionary from `user_config.json`, or an empty
    dict if the file is missing, unreadable, or not valid JSON. Never raises.
    '''
    try:
        with open(USER_CONFIG_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return {}


def apply(module_name: str, module_globals: dict) -> None:
    '''
    Overrides a config module's existing globals with values from the matching
    section of `user_config.json`.

    - `module_name` is the module's `__name__` (e.g. "config.settings"); the last
      dotted part is the section name looked up in the JSON ("settings").
    - Only keys that ALREADY exist as globals in the module are applied, so the
      JSON can never introduce new names into the config namespace.
    '''
    section_name = module_name.split(".")[-1]
    section = load_user_config().get(section_name, {})
    if not isinstance(section, dict):
        return
    for key, value in section.items():
        if key in module_globals:
            module_globals[key] = value
