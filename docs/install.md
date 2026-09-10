# Installation

There are two ways to set this up. Both need the same two things installed first:
**Python** and **Google Chrome**.

- **Easy start (recommended)** — a double-click launcher that does the rest for you.
  See [Quick start in the README](../README.md#-quick-start).
- **Manual install** — the classic route, described below. Use it if you want to run
  `runAiBot.py` yourself, or if the launcher does not work on your system.

[![Auto Job Applier setup tutorial video](https://github.com/user-attachments/assets/9e876187-ed3e-4fbf-bd87-4acc145880a2)](https://youtu.be/f9rdz74e1lM?si=4fRBcte0nuvr6tEH)

Click the image above to watch the setup and configuration tutorial, or use this link:
https://youtu.be/f9rdz74e1lM (recommended to watch at 2x speed).

## Manual install

1. **Install [Python 3.10](https://www.python.org/) or above.** Download it from
   https://www.python.org/downloads/, or on Windows search for "Python" in the Microsoft
   Store. **Make sure Python is added to Path in your System Environment Variables.**

2. **Get the project.** Clone the repo or download it as a ZIP:
   https://github.com/GodsScion/Auto_job_applier_linkedIn

3. **Install the Python packages.** Open a console/terminal in the project folder and run
   the command below. It uses [pip](https://pip.pypa.io/en/stable) to install everything
   listed in `requirements.txt`.

   ```
   pip install -r requirements.txt
   ```

4. **Install [Google Chrome](https://www.google.com/chrome)** in its default location.
   Download the installer from https://www.google.com/chrome.

5. **Chrome Driver is taken care of for you.** `auto_manage_driver = True` (the default in
   `config/settings.py`) downloads the matching driver automatically. If you would rather
   manage it yourself, set it to `False` and place the matching
   [Chrome Driver](https://googlechromelabs.github.io/chrome-for-testing/) where Chrome is
   installed.

6. **Configure the tool** — see [Configuration](configuration.md).

7. **Run it.**

   ```
   python runAiBot.py     # the bot
   python app.py          # the local control panel (settings, run controls, applied-jobs history)
   ```

   `app.py` prints the address to open, e.g. `http://127.0.0.1:5000`, or another port if
   5000 is busy (on macOS, port 5000 is often taken by AirPlay Receiver).

## Need help?

If you have questions or need help setting it up, or just want to talk, join the Discord
server: https://discord.gg/fFp7uUzWCY — see also [Support](support.md).

---

[← Back to docs index](README.md)
