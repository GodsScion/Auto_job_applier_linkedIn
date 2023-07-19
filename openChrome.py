from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from helpers import find_default_profile_directory

try:
    # Set up WebDriver with Chrome Profile
    options = Options()
    profile_dir = find_default_profile_directory()
    if profile_dir:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        print("Default profile directory not found. Using a new profile.")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()  # Maximize the browser window
    driver.switch_to.window(driver.window_handles[0])
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
except:
    print("Seems like Google Chrome browser is already running! Close it and run this program.")
    exit(1)