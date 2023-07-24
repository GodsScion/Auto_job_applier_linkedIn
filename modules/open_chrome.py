import undetected_chromedriver as uc
from setup.config import run_in_background
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log

try:
    # Set up WebDriver with Chrome Profile
    options = uc.ChromeOptions()
    options.headless = run_in_background
    profile_dir = find_default_profile_directory()
    if profile_dir:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        print("Default profile directory not found. Using a new profile.")
    driver = uc.Chrome(use_subprocess=True, options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
except Exception as e:
    print("Seems like Google Chrome browser is already running! Close it and run this program.")
    from datetime import datetime
    critical_error_log("", e, datetime.now())
    exit(1)
