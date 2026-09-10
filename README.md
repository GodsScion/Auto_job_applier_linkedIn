# LinkedIn AI Auto Job Applier 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/downloads/)
[![Discord](https://img.shields.io/badge/Discord-join-5865F2.svg)](https://discord.gg/fFp7uUzWCY)
[![Sponsor](https://img.shields.io/badge/Sponsor-GodsScion-EA4AAA.svg)](https://github.com/sponsors/GodsScion)

A free, open-source tool that automates job applications on LinkedIn. It runs entirely on
your own computer, using your own LinkedIn account. It finds jobs relevant to you, fills in
the application questions — optionally with AI help — and applies using the resume you
provide. Can apply to 100+ jobs in under an hour.

Nothing is uploaded anywhere: your details stay in local files, and the control panel is
reachable only from your own machine.

## 📽️ See it in Action

[![Auto Job Applier demo video](https://github.com/GodsScion/Auto_job_applier_linkedIn/assets/100998531/429f7753-ebb0-499b-bc5e-5b4ee28c4f69)](https://youtu.be/gMbB1fWZDHw)

Click the image above to watch the demo, or use this link: https://youtu.be/gMbB1fWZDHw

## 🚀 Quick start

New here, or not comfortable editing code? Use the built-in control panel. You set
everything up in your web browser and run the tool with a button — no editing Python files,
no terminal commands.

1. **Install Python once.** Get it from https://www.python.org/downloads/ (on Windows, tick
   **"Add Python to PATH"** during install). You also need
   [Google Chrome](https://www.google.com/chrome).
2. **Download this project** (green "Code" button → "Download ZIP", then unzip; or clone it).
3. **Double-click the launcher for your system:**
    - **macOS:** `start.command`
    - **Windows:** `start.bat`
    - **Linux:** `start.sh` (run `./start.sh` in a terminal)

    The first run sets things up automatically (it may take a minute). After that it's quick.
4. Your browser opens the **control panel** automatically (the exact address, e.g.
   `http://127.0.0.1:5000`, is shown in the launcher window). Fill in the tabs —
   **Account, Profile, Search, Filters, Run settings** — and click **Save**.
5. Go to the **Run** tab and click **Start**. A Chrome window opens and begins applying —
   keep it in the foreground. You can watch progress in the log and click **Stop** any time.

Your settings are saved locally in `user_config.json`. If you prefer the classic setup,
editing `config/*.py` by hand still works exactly as before — see
[Installation](docs/install.md) and [Configuration](docs/configuration.md).

> **Tip for your first run:** set `stop_before_submit = True` in `config/settings.py` to have
> the tool fill in every application and stop at the Review step without submitting, so you
> can see what it would say before you trust it.
> [More on dry runs](docs/config-settings.md#dry-runs-stop_before_submit).

## 📚 Documentation

Full documentation lives in **[`docs/`](docs/README.md)**.

| | |
|---|---|
| [Installation](docs/install.md) | Python, Chrome, packages, the Chrome driver, running the bot and the control panel |
| [Configuration](docs/configuration.md) | How configuration works and the order to do it in |
| → [`personals.py`](docs/config-personals.md) | Your name, phone, address, equal-opportunity answers |
| → [`questions.py`](docs/config-questions.md) | Easy Apply answers: experience, work authorization, salary, notice period, resume |
| → [`search.py`](docs/config-search.md) | Search terms, LinkedIn filters, skip rules, visa-sponsorship filtering |
| → [`secrets.py`](docs/config-secrets.md) | LinkedIn login and the optional AI setup |
| → [`settings.py`](docs/config-settings.md) | How the bot runs: click gap, background mode, safe mode, dry runs |
| [Contributing](CONTRIBUTING.md) | Code guidelines, where to send PRs, running the tests |
| [Support and community](docs/support.md) | Discord, GitHub Discussions, socials, sponsoring |
| [Disclaimer, Terms and License](docs/legal.md) | Read this before you use the tool |

Version history and release notes are on the
[Releases page](https://github.com/GodsScion/Auto_job_applier_linkedIn/releases).

## 🙌 Community and socials

- **Discord server**: https://discord.gg/fFp7uUzWCY — the fastest place to get help
- **GitHub Discussions**: https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions
- **LinkedIn**: https://www.linkedin.com/in/saivigneshgolla/
- **X/Twitter**: https://x.com/saivigneshgolla
- **Email**: saivigneshgolla@outlook.com

If this tool helped you, please share it with your peers, or
[sponsor the project](https://github.com/sponsors/GodsScion). It is built by one independent
developer.

## 📜 Disclaimer

**This tool runs on your own computer and acts through your own accounts. It is provided
free and open source, with no warranty of any kind. You are responsible for how you use it,
including making sure your use complies with the terms of any website or service you use it
with.** See [Disclaimer, Terms and Conditions](docs/legal.md).

## ⚖️ License

Copyright (c) 2024-2026 Sai Vignesh Golla. Licensed under the **MIT License** — see
[`LICENSE`](LICENSE). Releases before August 2026 were AGPL-3.0; see [`NOTICE`](NOTICE) for
the relicensing history.
