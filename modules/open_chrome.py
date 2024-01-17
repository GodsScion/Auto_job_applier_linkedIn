'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

'''

from setup.config import run_in_background, undetected_mode
if undetected_mode:
    import undetected_chromedriver as uc
else: 
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg

try:
    # Set up WebDriver with Chrome Profile
    options = uc.ChromeOptions() if undetected_mode else Options()
    options.headless = run_in_background
    profile_dir = find_default_profile_directory()
    if profile_dir: options.add_argument(f"--user-data-dir={profile_dir}")
    else: print_lg("Default profile directory not found. Using a new profile.")
    driver = uc.Chrome(use_subprocess=True, options=options) if undetected_mode else webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
except Exception as e:
    print_lg("Seems like Google Chrome browser is already running or Chrome-driver is out dated. Close Chrome and run setup.sh or update the Chrome-driver and then run this program.")
    critical_error_log("In Opening Chrome", e)
    driver.quit()
