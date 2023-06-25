import os
import csv
from time import sleep
from random import randint
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Example usage
keywords = ["Junior Software Engineer", "Entry level Software Developer", "ReactJs Developer"]
resumes = ["","","","",""]

username = "username@example.com" 
password = "examplepassword"

# Set the amount of time to wait between each click
click_gap = 0




def buffer(speed=0):
    if speed<=0:
        return
    elif speed <= 1:
        return sleep(randint(7,10)*0.1)
    else:
        return sleep(randint(9,18)*0.1)



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



def is_logged_in():
    try:
        sign_in_button = driver.find_element(By.LINK_TEXT, "Sign in")
        return False
    except Exception as e1:
        try:
            sign_in_button = driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]')
            return False
        except Exception as e2:
            print(e1,e2)
            print("Didn't find Sign in link, so assuming user is logged in!")
            return True



def login():
    while not is_logged_in():
        # Find the username and password fields and fill them with user credentials
        driver.get("https://www.linkedin.com/login")
        # if username == "username@example.com":
        #     print("Please complete login, job automation starts after 60 secs!")
        #     sleep(60)
        #     return True
        try:
            forgot_password_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
            try:
                driver.find_element(By.ID, "username").send_keys(username)
            except Exception as e:
                print("Couldn't find username field.",e)
            try:
                driver.find_element(By.ID, "password").send_keys(password)
            except Exception as e:
                print("Couldn't find password field.",e)
            # Find the login submit button and click it
            driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
        except Exception as e1:
            try:
                profile_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "profile__details")))
                profile_button.click()
            except Exception as e2:
                print(e1,"Couldn't Login!",e2)

        try:
            # Wait until the profile element is visible, indicating successful login
            wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Start a post")]')))
        except Exception as e:
            print("Seems like login attempt failed! Possibly due to wrong credentials or already logged in!",e)
            break



def apply_to_jobs(keywords):
    # Create or append to the CSV file
    with open('all_quick_applied_history.csv', mode='a', newline='') as csvfile:
        fieldnames = ['Job Title', 'Company', 'Application Link', 'Date and Time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        
        for keyword in keywords:
            url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
            driver.get(url)

            #Setting preferences
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="All filters"]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Most recent")]'))).click()
            

            # wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Past 24 hours")]'))).click()

            

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
                
                # Click on "Quick Apply" button
                apply_button.click()
                
                # Complete the application process (fill out forms, upload resume, etc.)
                # You'll need to identify the necessary form fields and interact with them using Selenium
                
                # Once the application is submitted successfully, add the application details to the CSV
                writer.writerow({'Job Title': title, 'Company': company, 'Application Link': application_link, 'Date and Time': datetime.now()})
                
                # Go back to the job listings page
                driver.back()
            
    # Close the browser
    driver.quit()




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



def main():
    try:
        driver.get("https://www.linkedin.com/login")

        # If not logged in, perform the login process
        login()

        apply_to_jobs(keywords)

    except Exception as e:
        print(e)
        driver.quit()

main()