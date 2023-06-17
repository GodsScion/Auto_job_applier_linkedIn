import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Example usage
keywords = ["Junior Software Engineer", "Entry level Software Developer", "ReactJs Developer"]

def is_logged_in(driver):
    try:
        sign_in_button = driver.find_element(By.LINK_TEXT, "Sign in")
        sign_in_button.click()
        return False
    except:
        return True

def login(driver, wait):
    while not is_logged_in(driver):
        # Find the username and password fields and fill them with user credentials
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Find the login submit button and click it
        submit_button = driver.find_element(By.CSS_SELECTOR, ".btn__primary--large")
        submit_button.click()

        # Wait until the profile element is visible, indicating successful login
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "nav-item__profile-member-photo")))

def find_default_profile_directory():
    # List of default profile directory locations to search
    default_locations = [
        r"%LOCALAPPDATA%\Google\Chrome\User Data",
        r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data",
        r"%USERPROFILE%\Local Settings\Application Data\Google\Chrome\User Data"
    ]

    for location in default_locations:
        profile_dir = os.path.expandvars(location)
        if os.path.exists(profile_dir):
            return profile_dir

    return None

def apply_to_jobs(keywords):
    # Set up WebDriver with Chrome Profile
    options = Options()
    profile_dir = find_default_profile_directory()
    if profile_dir:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        print("Default profile directory not found. Using a new profile.")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()  # Maximize the browser window
    wait = WebDriverWait(driver, 10)
    
    # Check if the user is logged in
    logged_in = is_logged_in(driver)
    
    # If not logged in, perform the login process
    if not logged_in:
        login(driver, wait)
    
    # Track the job application history
    history_file = ".allHistory.txt"
    if not os.path.exists(history_file):
        # Create .allHistory.txt file if it doesn't exist
        open(history_file, 'w').close()

    with open(history_file, 'r') as f:
        application_history = f.read().splitlines()
    
    for keyword in keywords:
        url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
        driver.get(url)
        
        # Wait until job listings are loaded
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "job-card-container")))
        
        # Find all job listings
        job_listings = driver.find_elements(By.CLASS_NAME, "job-card-container")
        
        for job in job_listings:
            # Extract job details
            title = job.find_element(By.CLASS_NAME, "job-card-search__title").text
            company = job.find_element(By.CLASS_NAME, "job-card-container__company-name").text
            apply_button = job.find_element(By.CLASS_NAME, "job-card-container__apply-method")
            application_link = apply_button.get_attribute("href")
            
            # Check if job has already been applied
            if application_link in application_history:
                continue
            
            # Click on "Quick Apply" button
            apply_button.click()
            
            # Complete the application process (fill out forms, upload resume, etc.)
            # You'll need to identify the necessary form fields and interact with them using Selenium
            
            # Once the application is submitted successfully, add the application link to the history
            application_history.append(application_link)
            with open(history_file, 'a') as f:
                f.write(application_link + '\n')
            
            # Go back to the job listings page
            driver.back()
        
    # Close the browser
    driver.quit()


apply_to_jobs(keywords)
