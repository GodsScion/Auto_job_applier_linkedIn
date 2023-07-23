import os
from time import sleep
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv

# Directory and name of the file where history of applied jobs is saved.
file_name = "test_all_quick_applied_history.csv"

easy_apply_only = False

# Get list of applied job's Job IDs function
def get_applied_job_ids():
    job_ids = set()
    try:
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                job_ids.add(row[0])
    except FileNotFoundError:
        print(f"The CSV file '{file_name}' does not exist.")
    return job_ids 

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

click_gap = 0

def buffer(speed=0):
    if speed<=0:
        return
    elif speed <= 1 and speed < 2:
        return sleep(randint(6,10)*0.1)
    elif speed <= 2 and speed < 3:
        return sleep(randint(10,18)*0.1)
    else:
        return sleep(randint(18,round(speed)*10)*0.1)

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







try: 
    applied_jobs = get_applied_job_ids()

    # Wait until job listings are loaded
    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'jobs-search-results__list-item')]")))
    
    pagination_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "artdeco-pagination")))
    driver.execute_script("arguments[0].scrollIntoView();", pagination_element)

    # Find all job listings
    job_listings = driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")

    # Create or append to the CSV file
    with open(file_name, mode='a', newline='') as csv_file:
        fieldnames = ['Job ID', 'Job Title', 'Company', 'Job Link', 'Job Description', 'Skills', 'HR Name', 'HR Link', 'Resume Used', 'Date listed', 'Date Applied', 'Easy Apply' ] #['Job Title', 'Company', 'Application Link', 'Date and Time']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
    
    
    for job in job_listings:
        # Extract job details
        job_details_button = job.find_element(By.CLASS_NAME, "job-card-list__title")
        company = job.find_element(By.CLASS_NAME, "job-card-container__primary-description").text
        job_id = job.get_dom_attribute('data-occludable-job-id')
        title = job_details_button.text
        driver.execute_script("arguments[0].scrollIntoView(true);", job_details_button)
        job_details_button.click()
        buffer(click_gap)


        application_link = "https://www.linkedin.com/jobs/view/"+job_id

        # Skip if already applied
        try:
            if job_id in applied_jobs: continue
            driver.find_element(By.CLASS_NAME, "jobs-s-apply__application-link")
            print("Already applied to {} job!".format(title))
            continue
        except Exception as e:
            print("Trying to Apply to {} with Job ID: {}".format(title,job_id))

        easy_applied = False
        
        # Case 1: Easy Apply Button
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Easy Apply")]'))).click()
            buffer(click_gap)
        except Exception as e2:
            print(e1,e2)
            print("Failed to apply!")

        # Case 1: Apply externally
        try:
            WebDriverWait(driver,3).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Apply") and not(span[contains(@class, "disabled")])]'))).click()
            application_link = driver.current_url
            driver.switch_to.window(driver.window_handles[0])
            buffer(click_gap)
        except Exception as e1:
            


        



    # Once the application is submitted successfully, add the application details to the CSV
    # writer.writerow({'Job Title': title, 'Company': company, 'Application Link': application_link, 'Date and Time': datetime.now()})

    # Go back to the job listings page
    driver.back()
except Exception as e:
    print(e)
    driver.quit()