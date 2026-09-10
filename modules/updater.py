'''
Author:     Sai Vignesh Golla
License:    MIT License
            https://opensource.org/license/mit
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    26.01.20.5.08

Update check for the control panel: compare the local VERSION file with the one
on the default branch, and offer a one-button `git pull` to fast-forward.

TRUST MODEL: TLS plus trust in the GitHub account - the same ceiling `git pull`
itself has. Nothing here verifies a signature; signing only buys something once
you ship binaries, and this project deliberately ships a git clone instead.
'''

import re
import subprocess
import urllib.request
from pathlib import Path

REPO = "GodsScion/Auto_job_applier_linkedIn"
ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "VERSION"
# raw.githubusercontent, NOT the API: the API allows 60 requests/hour per IP,
# shared by everyone behind one office or campus NAT, and ETag 304s do not
# refund that quota. raw has no rate-limit bucket and needs no releases to exist.
VERSION_URL = "https://raw.githubusercontent.com/%s/main/VERSION" % REPO
_VERSION_RE = re.compile(r"\d+(?:\.\d+){2,5}\Z")
_MANUAL = "\n\nTo update by hand: run `git pull` in this folder, or re-download the project from GitHub."


def current_version():
    '''The version in this working copy, or "" if the VERSION file is missing.'''
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def latest_version(timeout=5):
    '''
    The version published on the default branch, or None if the check fails for
    ANY reason: no internet, DNS failure, timeout, 404, 500, or a body that is
    not a version string (a captive-portal login page is HTML with HTTP 200).
    Never raises - a user with no internet must not see a traceback.
    '''
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=timeout) as response:
            text = response.read(64).decode("utf-8", "replace").strip()
    except Exception:
        return None
    return text if _VERSION_RE.match(text) else None


def is_newer(latest, current):
    '''True only when `latest` is strictly newer. Same or older is not an update.'''
    try:
        return tuple(int(p) for p in latest.split(".")) > tuple(int(p) for p in current.split("."))
    except (AttributeError, ValueError):
        return False


def update_available():
    '''True if a newer version is published. False on any failure.'''
    return is_newer(latest_version(), current_version())


def self_update():
    '''
    Fast-forward this clone to the newest commit. Returns {"ok", "message"}.

    Edits to tracked files are parked with `git stash push` - deliberately with
    no -u, which would also sweep the user's own untracked resumes and notes
    into a stash they will never look in. On every failure path the stash is
    popped straight back, so the tree is never left half-stashed. On success it
    is deliberately KEPT as the backup: popping could conflict with what was
    just pulled, and app.py has already copied the live settings into
    user_config.json before calling this.
    '''
    git = ["git", "-C", str(ROOT), "-c", "core.autocrlf=false"]

    def run(*args):
        return subprocess.run(git + list(args), capture_output=True, text=True, timeout=180)

    stashed = False
    try:
        origin = run("remote", "get-url", "origin")
        if origin.returncode != 0 or REPO.lower() not in origin.stdout.lower():
            return {"ok": False, "message": "This folder is not a git clone of %s." % REPO + _MANUAL}
        stash = run("stash", "push", "-m", "auto-job-applier pre-update")
        stashed = stash.returncode == 0 and "No local changes" not in stash.stdout
        pull = run("pull", "--ff-only")
        if pull.returncode == 0:
            try:
                # start.sh/.bat/.command reinstall requirements whenever this
                # marker is missing, so deleting it brings dependency updates
                # along for free - no extra code in the launchers.
                (ROOT / ".venv" / ".deps_installed").unlink(missing_ok=True)
            except OSError:
                pass
            return {"ok": True, "message": (pull.stdout + pull.stderr).strip() +
                    "\n\nClose this window and start the app again to finish updating."}
        problem = (pull.stdout + pull.stderr).strip()
    except Exception as err:      # git not installed, timed out, unreadable repo
        problem = str(err)
    if stashed:
        try:
            run("stash", "pop")
        except Exception:
            problem += "\n\nYour edits are parked in `git stash`; run `git stash pop` to get them back."
    return {"ok": False, "message": problem + _MANUAL}
