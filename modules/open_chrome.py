'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

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
    driver = uc.Chrome(options=options) if undetected_mode else webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
except Exception as e:
    msg = "Seems like Google Chrome browser is already running or Chrome-driver is out dated. Close Chrome and run windows-setup.bat for windows or try your luck with setup.sh or update the Chrome-driver and then run this program! If error occurred when using undetected_mode uninstall and install undetected-chromedriver. (Open  terminal and use commands 'pip uninstall undetected-chromedriver' and 'pip install undetected-chromedriver' respectively.)"
    print_lg(msg)
    critical_error_log("In Opening Chrome", e)
    from pyautogui import alert
    alert(msg, "Error in opening chrome")
    driver.quit()
