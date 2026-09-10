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

from modules.helpers import get_default_temp_profile, make_directories
from config.settings import run_in_background, auto_manage_driver, disable_extensions, safe_mode, file_name, failed_file_name, logs_folder_path, generated_resume_path
from config.questions import default_resume_path
if auto_manage_driver:
    import undetected_chromedriver as uc
else: 
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    # from selenium.webdriver.chrome.service import Service
import os, shutil, subprocess, sys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, logger, print_lg
from selenium.common.exceptions import SessionNotCreatedException

def _adhoc_sign(path: str) -> None:
    """Re-sign `path` ad-hoc on macOS. MUST run AFTER UC has patched the binary."""
    if sys.platform != "darwin":    return      # Gatekeeper is a macOS-only problem
    try:
        subprocess.run(["codesign", "--force", "--sign", "-", path], check=True, capture_output=True)
    except Exception as e:
        # Not fatal, plenty of Macs run unsigned binaries fine. Say what to look for if it isn't one.
        logger.warning("Couldn't ad-hoc re-sign the Chrome driver (%s). If Chrome dies with 'Status code was: -9', install the Xcode command line tools: xcode-select --install", type(e).__name__)


def get_managed_driver_path() -> str | None:
    """Resolve a chromedriver that matches this machine's CPU, patch it, and re-sign it.

    Returns the path, or None to fall back to undetected_chromedriver's own download.

    ponytail: compatibility shim, not a driver manager. undetected-chromedriver 3.5.5
    (Feb 2024, the newest and final release, issue tracker returns HTTP 410) has no
    "mac-arm64" branch in Patcher._set_platform_name(), so every Apple Silicon user
    downloads an x86_64 driver and Chrome never launches:
        OSError: [Errno 86] Bad CPU type in executable
    Selenium Manager, already bundled with the installed selenium, resolves the right one.
    Ceiling: this fixes driver resolution and the Gatekeeper re-sign only, nothing else UC
    gets wrong. The real fix is upstream: UC is abandoned, the author's successor is
    `nodriver`. Delete this whole shim when the bot moves off UC.
    """
    try:
        from selenium.webdriver.common.selenium_manager import SeleniumManager
        source = SeleniumManager().binary_paths(["--browser", "chrome"])["driver_path"]
        # UC rewrites the driver in place, so never hand it the shared ~/.cache/selenium
        # copy that other tools use. Work on our own copy, in UC's own data dir.
        os.makedirs(uc.Patcher.data_path, exist_ok=True)
        target = os.path.join(uc.Patcher.data_path, "chromedriver")
        shutil.copy2(source, target)                    # fresh copy each run, so it can never go stale against a Chrome update
        uc.Patcher(executable_path=target).auto()       # applies UC's cdc_ patch in place
        _adhoc_sign(target)                             # ...which breaks the code signature, hence the re-sign, in this order
        return target                                   # uc.Chrome() then sees it already patched and leaves the signature alone
    except Exception as e:
        logger.warning("Selenium Manager couldn't resolve a Chrome driver (%s: %s). Falling back to undetected_chromedriver's own download.", type(e).__name__, e)
        return None


def createChromeSession(isRetry: bool = False):
    make_directories([file_name,failed_file_name,logs_folder_path+"/screenshots",default_resume_path,generated_resume_path+"/temp"])
    # Set up WebDriver with Chrome Profile
    options = uc.ChromeOptions() if auto_manage_driver else Options()
    # "--headless" is the legacy mode and is trivially detectable, "=new" runs the real browser.
    if run_in_background:   options.add_argument("--headless=new")
    if disable_extensions:  options.add_argument("--disable-extensions")

    print_lg("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM! Or it's highly likely that application will just open browser and not do anything!")
    profile_dir = find_default_profile_directory()
    if isRetry:
        print_lg("Will login with a guest profile, browsing history will not be saved in the browser!")
    elif profile_dir and not safe_mode:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        print_lg("Logging in with a guest profile, Web history will not be saved!")
        options.add_argument(f"--user-data-dir={get_default_temp_profile()}")
    if auto_manage_driver:
        print_lg("Setting up the matching Chrome driver... This may take some time (this happens each run when auto_manage_driver is enabled).")
        driver_path = get_managed_driver_path()
        driver = uc.Chrome(options=options, driver_executable_path=driver_path) if driver_path else uc.Chrome(options=options)
    else:
        # ponytail: warning only, no stealth patching here. Set auto_manage_driver = True if LinkedIn starts blocking.
        logger.warning("auto_manage_driver is False, so we're using plain Selenium with NO anti-detection at all. LinkedIn may flag or block this session, set auto_manage_driver = True in config/settings.py if that happens.")
        driver = webdriver.Chrome(options=options) #, service=Service(executable_path="C:\\Program Files\\Google\\Chrome\\chromedriver-win64\\chromedriver.exe"))
    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
    return options, driver, actions, wait

try:
    options, driver, actions, wait = None, None, None, None
    options, driver, actions, wait = createChromeSession()
except SessionNotCreatedException as e:
    # Recoverable: the guest-profile retry below usually succeeds, so this is not an ERROR.
    logger.warning("Failed to create Chrome Session, retrying with guest profile", exc_info=e)
    options, driver, actions, wait = createChromeSession(True)
except Exception as e:
    msg = 'Seems like Google Chrome is out dated. Update browser and try again! \n\n\nIf issue persists, try Safe Mode. Set, safe_mode = True in config.py \n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn \n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
    if isinstance(e,TimeoutError): msg = "Couldn't download Chrome-driver. Set auto_manage_driver = False in config!"
    logger.error(msg)
    critical_error_log("In Opening Chrome", e)
    from pyautogui import alert
    alert(msg, "Error in opening chrome")
    try: driver.quit()
    except NameError: exit()
    
