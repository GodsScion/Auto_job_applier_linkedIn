'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (c) 2024-2026 Sai Vignesh Golla

License:    MIT License
            https://opensource.org/license/mit
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''


# Imports

import os
import sys
import json
import pathlib

import logging

from time import sleep
from random import randint
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pprint import pformat

from config import settings as _settings
from config.settings import logs_folder_path



#### Common functions ####

#< Directories related
def make_directories(paths: list[str]) -> None:
    '''Create any of the given directories that don't yet exist (a path pointing at a file creates its parent folder).'''
    for raw_path in paths:
        target = os.path.expanduser(raw_path).replace("//", "/")
        # If the last segment has an extension it's a file, so keep only its folder.
        if '.' in os.path.basename(target):
            target = os.path.dirname(target)
        if not target:
            continue
        try:
            os.makedirs(target, exist_ok=True)
        except Exception as e:
            print(f'Could not create the directory "{target}":', e)


def get_default_temp_profile() -> str:
    '''
    Absolute path of the throwaway Chrome profile folder, created if it doesn't exist.
    Returns a **bare path** - callers add the `--user-data-dir=` flag themselves.
    '''
    # Thanks to https://github.com/vinodbavage31 for suggestion!
    home = pathlib.Path.home()
    if sys.platform.startswith('win'):
        path = pathlib.Path("C:\\temp\\auto-job-apply-profile")
    elif sys.platform.startswith('linux'):
        path = home / ".auto-job-apply-profile"
    else:
        path = home / "Library" / "Application Support" / "Google" / "Chrome" / "auto-job-apply-profile"
    try:
        # A missing parent is the other cause of "Chrome cannot read and write to its data directory".
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f'Could not create the Chrome profile directory "{path}":', e)
    return str(path)


def find_default_profile_directory() -> str | None:
    '''
    Dynamically finds the default Google Chrome 'User Data' directory path
    across Windows, macOS, and Linux, regardless of OS version.

    Returns the absolute path as a string, or None if the path is not found.
    '''
    
    home = pathlib.Path.home()
    
    # Windows
    if sys.platform.startswith('win'):
        paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data"),
            os.path.expandvars(r"%USERPROFILE%\Local Settings\Application Data\Google\Chrome\User Data")
        ]
    # Linux
    elif sys.platform.startswith('linux'):
        paths = [
            str(home / ".config" / "google-chrome"),
            str(home / ".var" / "app" / "com.google.Chrome" / "data" / ".config" / "google-chrome"),
        ]
    # MacOS ## For some reason, opening with profile in MacOS is not creating a session for undetected-chromedriver!
    # elif sys.platform == 'darwin':
    #     paths = [
    #         str(home / "Library" / "Application Support" / "Google" / "Chrome")
    #     ]
    else:
        return None

    # Check each potential path and return the first one that exists
    for path_str in paths:
        if os.path.exists(path_str):
            return path_str
            
    return None
#>


#< Logging related
# One stdlib logger for the whole tool. The console handler prints the bare message to
# stdout, so live CLI output looks exactly like it always has; the file handler adds the
# timestamp and level, and rotates, so log.txt stops growing without bound.
logger = logging.getLogger("auto_job_applier")


class _StdoutHandler(logging.StreamHandler):
    '''
    A StreamHandler that resolves `sys.stdout` at write time instead of caching the
    object it was built with, so anything that redirects stdout later - app.py, a test
    harness, an embedding caller - actually gets the output.
    '''
    @property
    def stream(self): return sys.stdout

    @stream.setter
    def stream(self, value): pass       # StreamHandler.__init__/setStream assign this


_console_handler: _StdoutHandler = None


def critical_error_log(possible_reason: str, stack_trace: BaseException) -> None:
    '''
    Function to log and print critical errors along with datetime stamp
    '''
    logger.error(possible_reason, exc_info=stack_trace)


def get_log_path():
    '''
    Function to replace '//' with '/' for logs path
    '''
    try:
        path = logs_folder_path+"/log.txt"
        return path.replace("//","/")
    except Exception as e:
        critical_error_log("Failed getting log path! So assigning default logs path: './logs/log.txt'", e)
        return "logs/log.txt"


__logs_file_path = get_log_path()


def _report_log_failure_once(handler: logging.Handler, log_path: str):
    '''
    A locked or unwritable log file used to raise a blocking `alert()` modal, which
    deadlocked any unattended run. Degrade to one console warning and then stay quiet:
    the console handler carries on regardless, so nothing is lost from the live view.
    '''
    def handle_error(record: logging.LogRecord) -> None:
        if getattr(handler, "_write_failure_reported", False): return
        handler._write_failure_reported = True
        print(f'Could not write to "{log_path}" - it may be open in another program. '
              'Continuing with console output only.', file=sys.stderr)
    return handle_error


def setup_logging(log_path: str = None, level: str | int = None) -> logging.Logger:
    '''
    Points `logger` at `log_path` (rotating, timestamped, levelled) and at the console
    (bare message, stdout). Safe to call again: handlers are replaced, not stacked.
    `level` defaults to `log_level` in config/settings.py, read defensively so a config
    written before that setting existed still runs.
    '''
    global _console_handler
    log_path = log_path or __logs_file_path
    if level is None:
        level = getattr(_settings, "log_level", "INFO")
    resolved = level if isinstance(level, int) else logging.getLevelName(str(level).upper())
    logger.setLevel(resolved if isinstance(resolved, int) else logging.INFO)
    logger.propagate = False        # our records already have handlers, don't double up on root

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    # stdout, not StreamHandler's default stderr: app.py pipes the bot's stdout to a file.
    _console_handler = _StdoutHandler()
    _console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_console_handler)

    make_directories([log_path])
    # delay=True so importing this module never creates a file, and an unwritable path
    # fails at emit time - where RotatingFileHandler.emit routes it to handleError
    # instead of raising it at the call site.
    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3,
                                       encoding="utf-8", delay=True)
    file_handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                                                datefmt="%Y-%m-%d %H:%M:%S"))
    file_handler.handleError = _report_log_failure_once(file_handler, log_path)
    logger.addHandler(file_handler)
    return logger


setup_logging()


def print_lg(*msgs: str | dict, end: str = "\n", pretty: bool = False, flush: bool = False, from_critical: bool = False) -> None:
    '''
    Function to log and print. **Note that, `end` and `flush` parameters are ignored if `pretty = True`**

    Compatibility shim over `logger`, kept so the ~130 existing call sites keep working
    unchanged. Everything it emits is INFO (ERROR when `from_critical`). New code that
    genuinely carries a level should call `logger.warning(...)` / `logger.error(...)`.
    '''
    level = logging.ERROR if from_critical else logging.INFO
    for message in msgs:
        # pformat is exactly what pprint prints, so the console stays character-identical.
        text = pformat(message) if pretty else str(message)
        # ponytail: swapping the handler's terminator is the only stdlib way to honour
        # `end`. Fine for this single-threaded bot; needs a lock if it ever threads.
        # `flush` is now a no-op - StreamHandler.emit already flushes every record.
        _console_handler.terminator = "\n" if pretty else end
        try:
            logger.log(level, text)
        finally:
            _console_handler.terminator = "\n"
#>


def buffer(speed: int=0) -> None:
    '''
    Function to wait within a period of selected random range.
    * Will not wait if input `speed <= 0`
    * Will wait within a random range of 
      - `0.6 to 1.0 secs` if `1 <= speed < 2`
      - `1.0 to 1.8 secs` if `2 <= speed < 3`
      - `1.8 to speed secs` if `3 <= speed`
    '''
    if speed<=0:
        return
    elif speed <= 1 and speed < 2:
        return sleep(randint(6,10)*0.1)
    elif speed <= 2 and speed < 3:
        return sleep(randint(10,18)*0.1)
    else:
        return sleep(randint(18,round(speed)*10)*0.1)


def human_type(target, text: str) -> None:
    '''
    Types `text` one character at a time, with a human-ish gap between key strokes,
    instead of pasting the whole string in a single `send_keys` call.
    * `target` can be a Selenium `WebElement` or an `ActionChains` (anything with `.perform`).
    * Does nothing if `text` is empty or `None`.
    * Roughly 1 key in 40 gets a longer "thinking" pause.
    Don't use it for file paths sent to `<input type="file">` or for `Keys.*` chords.
    '''
    if not text:
        return
    # ActionChains only queues keys, it needs a perform() to actually send them. Its
    # perform() empties the queue, so sending per character doesn't repeat earlier ones.
    perform = getattr(target, "perform", None)
    for char in text:
        target.send_keys(char)
        if perform: perform()
        sleep(randint(4,18)*0.01)       # ~40-180ms, roughly 60-150 WPM with jitter
        if randint(1,40) == 1: buffer(1)


def manual_login_retry(is_logged_in: callable, limit: int = 2) -> None:
    '''
    Function to ask and validate manual login
    '''
    count = 0
    while not is_logged_in():
        from pyautogui import alert
        print_lg("Seems like you're not logged in!")
        button = "Confirm Login"
        message = 'After you successfully Log In, please click "{}" button below.'.format(button)
        if count > limit:
            button = "Skip Confirmation"
            message = 'If you\'re seeing this message even after you logged in, Click "{}". Seems like auto login confirmation failed!'.format(button)
        count += 1
        if alert(message, "Login Required", button) and count > limit: return



def calculate_date_posted(time_string: str) -> datetime | None:
    '''
    Turn a LinkedIn "posted" phrase like "3 days ago" into an approximate datetime.
    Returns None when the phrase can't be understood. Months and years are
    approximated as 30 and 365 days respectively.
    '''
    import re
    match = re.search(r'(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago',
                      time_string.strip(), re.IGNORECASE)
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2).lower()
    spans = {
        'second': timedelta(seconds=amount),
        'minute': timedelta(minutes=amount),
        'hour': timedelta(hours=amount),
        'day': timedelta(days=amount),
        'week': timedelta(weeks=amount),
        'month': timedelta(days=amount * 30),
        'year': timedelta(days=amount * 365),
    }
    delta = spans.get(unit)
    return datetime.now() - delta if delta else None


def convert_to_lakhs(value: str) -> str:
    '''
    Converts str value to lakhs, no validations are done except for length and stripping.
    Examples:
    * "100000" -> "1.00"
    * "101,000" -> "10.1," Notice ',' is not removed 
    * "50" -> "0.00"
    * "5000" -> "0.05" 
    '''
    value = value.strip()
    l = len(value)
    if l > 0:
        if l > 5:
            value = value[:l-5] + "." + value[l-5:l-3]
        else:
            value = "0." + "0"*(5-l) + value[:2]
    return value


def convert_to_json(data) -> dict:
    '''
    Function to convert data to JSON, if unsuccessful, returns `{"error": "Unable to parse the response as JSON", "data": data}`
    '''
    try:
        result_json = json.loads(data)
        return result_json
    except json.JSONDecodeError:
        return {"error": "Unable to parse the response as JSON", "data": data}


def truncate_for_csv(data, max_length: int = 131000, suffix: str = "...[TRUNCATED]") -> str:
    '''
    Coerce any value to a string that's safe to write into a CSV cell, shortening it
    (with a marker suffix) if it would exceed max_length. Never raises.
    '''
    try:
        text = "" if data is None else str(data)
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    except Exception as e:
        return f"[could not stringify value: {e}]"


