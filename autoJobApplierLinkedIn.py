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
from selenium.webdriver.common.action_chains import ActionChains

# Example usage
keywords = ["Software Engineer", "Entry level Software Developer", "ReactJs Developer"]
resumes = ["","","","",""]

username = "username@example.com" 
password = "examplepassword"

# Set the amount of time to wait between each click
click_gap = 0

# Preferences for job search
sort_by = "Most relevant"       # "Most recent", "Most relevant"
date_posted = "Past 24 hours"   # "Any time", "Past week", "Past 24 hours", "Past month"
experience_level = ["Internship", "Entry level", "Associate"] # (multiple select) "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"
companies = []                  # (multiple select) "Dice", "JPMorgan Chase & Co.", "Tata Consultancy Services", "Recruiting from Scratch", "Epic", "Elevance Health", and so on. make sure the name you type in list exactly matches, including capitals.
job_type = []                   # (multiple select) "Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"
on_site = []                    # (multiple select) "On-site", "Remote", "Hybrid"
easy_apply_only = False         # True or False
location = []
industry = []
job_function = []
job_titles = []
under_10_applicants = False     # True or False
in_your_network = False         # True or False
fair_chance_employer = False    # True or False
salary = ""                     # "$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+"
benefits = []
commitments = []


def buffer(speed=0):
    if speed<=0:
        return
    elif speed <= 1 and speed < 2:
        return sleep(randint(6,10)*0.1)
    elif speed <= 2 and speed < 3:
        return sleep(randint(10,18)*0.1)
    else:
        return sleep(randint(18,round(speed)*10)*0.1)


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


# Click Functions

def wait_span_click(x):
    if x:
        try:
            button = wait.until(EC.presence_of_element_located((By.XPATH, '//span[normalize-space(.)="'+x+'"]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print("\nClick Failed! Didn't find '"+x+"'\n\n", e)

def multi_sel(l):
    for x in l:
        try:
            button = wait.until(EC.presence_of_element_located((By.XPATH, '//span[normalize-space(.)="'+x+'"]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print("\nClick Failed! Didn't find '"+x+"'\n\n", e)

def multi_sel_noWait(l):
    for x in l:
        try:
            button = driver.find_element(By.XPATH, '//span[normalize-space(.)="'+x+'"]')
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print("\nClick Failed! Didn't find '"+x+"'\n\n", e)

def boolean_button_click(x):
    try:
        list_container = driver.find_element(By.XPATH, '//h3[normalize-space()="'+x+'"]/ancestor::fieldset')
        button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        actions.move_to_element(button).click().perform()
        buffer(click_gap)
    except Exception as e:
        print("\nClick Failed! Didn't find '"+x+"'\n\n", e)


# Login Functions

def is_logged_in():
    if driver.current_url == "https://www.linkedin.com/feed/": return True
    try:
        driver.find_element(By.LINK_TEXT, "Sign in")
        return False
    except Exception as e1:
        try:
            driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]')
            return False
        except Exception as e2:
            print(e1,e2)
            print("\nDidn't find Sign in link, so assuming user is logged in!\n\n")
            return True


def login():
    # Find the username and password fields and fill them with user credentials
    driver.get("https://www.linkedin.com/login")
    # if username == "username@example.com":
    #     print("\nPlease complete login, job automation starts after 60 secs!\n\n")
    #     sleep(60)
    #     return True
    try:
        forgot_password_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            driver.find_element(By.ID, "username").send_keys(username)
        except Exception as e:
            print("\nCouldn't find username field.\n\n", e)
        try:
            driver.find_element(By.ID, "password").send_keys(password)
        except Exception as e:
            print("\nCouldn't find password field.\n\n", e)
        # Find the login submit button and click it
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
    except Exception as e1:
        try:
            profile_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "profile__details")))
            profile_button.click()
        except Exception as e2:
            print(e1,"Couldn't Login!\n\n", e2)

    try:
        # Wait until the profile element is visible, indicating successful login
        wait.until(EC.url_to_be("https://www.linkedin.com/feed/"))
        return print("\nLogin successful!\n\n")
        # wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space(.)="Start a post"]')))
        # return print("\nLogin successful!\n\n")
    except Exception as e:
        print("\nSeems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!\n\n", e)
        count = 0
        while not is_logged_in():
            print("\nSeems like you're not logged in!")
            message = "Press Enter to continue after you logged in..."
            if count > 1:
                message = "If you're seeing this message even after you logged in, type 'skip' and press Enter to continue or just press Enter to try again..."
            count += 1
            value = input(message)
            if value == 'skip':
                return


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

            try:
                #Setting preferences
                recommended_wait = 1 if click_gap < 1 else 0

                wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="All filters"]'))).click()
                buffer(recommended_wait)

                wait_span_click(sort_by)
                wait_span_click(date_posted)
                buffer(recommended_wait)

                multi_sel(experience_level) 
                multi_sel_noWait(companies)
                if experience_level or companies: buffer(recommended_wait)

                multi_sel(job_type)
                multi_sel(on_site)
                if job_type or on_site: buffer(recommended_wait)

                if easy_apply_only: boolean_button_click("Easy Apply")
                
                multi_sel_noWait(location)
                multi_sel_noWait(industry)
                if location or industry: buffer(recommended_wait)

                multi_sel_noWait(job_function)
                multi_sel_noWait(job_titles)
                if job_function or job_titles: buffer(recommended_wait)

                if under_10_applicants: boolean_button_click("Under 10 applicants")
                if in_your_network: boolean_button_click("In your network")
                if fair_chance_employer: boolean_button_click("Fair Chance Employer")

                wait_span_click(salary)
                buffer(recommended_wait)
                
                multi_sel_noWait(benefits)
                multi_sel_noWait(commitments)
                if benefits or commitments: buffer(recommended_wait)

                show_results_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Apply current filters to show")]')
                show_results_button.click()

            except Exception as e:
                print("\nSetting the preferences failed!\n\n", e)    


            

            # Wait until job listings are loaded
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'jobs-search-results__list-item')]")))
            
            # Find all job listings
            job_listings = driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")
            
            for job in job_listings:
                # Extract job details
                job_details_button = job.find_element(By.CLASS_NAME, "job-card-list__title")
                company = job.find_element(By.CLASS_NAME, "job-card-container__primary-description").text
                job_id = job.find_element(By.CSS_SELECTOR, 'li[data-occludable-job-id]').get_attribute('data-occludable-job-id')
                title = job_details_button.text
                driver.execute_script("arguments[0].scrollIntoView(true);", job_details_button)
                job_details_button.click()
                buffer(click_gap)


                application_link = "https://www.linkedin.com/jobs/view/"+job_id

                #---------------------------
# handle if appplied
# <div class="display-flex">
#               <div class="jobs-s-apply jobs-s-apply--fadein inline-flex mr2">
#     <div id="ember2737" class="artdeco-inline-feedback artdeco-inline-feedback--success ember-view" role="alert">    <li-icon aria-hidden="true" type="success-pebble-icon" class="artdeco-inline-feedback__icon" size="small"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" data-supported-dps="16x16" fill="currentColor" class="mercado-match" width="16" height="16" focusable="false">
#   <path d="M8 1a7 7 0 107 7 7 7 0 00-7-7zm-.6 11L4.25 8.85 5.6 7.51 7.1 9l2.63-4H12z"></path>
# </svg></li-icon>

#   <span class="artdeco-inline-feedback__message">
#       Applied 8 seconds ago
# <!---->  </span>
# </div>
#       <a href="/jobs/tracker/applied/" id="ember2738" class="jobs-s-apply__application-link display-flex align-items-center ember-view">
#         See application
#         <span class="a11y-text">
#           Applied 8 seconds ago for Software Engineer
#         </span>
#         <svg role="none" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" data-supported-dps="16x16" data-test-icon="chevron-right-small" class="rtl-flip">
# <!---->    

#     <use href="#chevron-right-small" width="16" height="16"></use>
# </svg>

#       </a>
# </div>

#               <span class="visibility-hidden"></span>

# <!---->          </div>
                #--------------------------

                # Case 1: Apply externally
                try:
                    WebDriverWait(driver,3).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Apply") and not(span[contains(@class, "disabled")])]'))).click()
                    application_link = driver.current_url
                    driver.switch_to.window(driver.window_handles[0])
                    buffer(click_gap)
                except Exception as e1:
                    # Case 2: Easy Apply
                    try:
                        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Easy Apply")]'))).click()
                        buffer(click_gap)
                    except Exception as e2:
                        print(e1,e2)
                        print("\nFailed to apply!\n\n")
                        return True

#--------------------------------------------------------
                
                
                
                # Click on "Quick Apply" button
                # apply_button.click()
                
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
    print("\nDefault profile directory not found. Using a new profile.")
driver = webdriver.Chrome(options=options)
driver.maximize_window()  # Maximize the browser window
driver.switch_to.window(driver.window_handles[0])
wait = WebDriverWait(driver, 10)
actions = ActionChains(driver)



def main():
    try:
        driver.get("https://www.linkedin.com/login")

        # If not logged in, perform the login process
        if not is_logged_in(): login()                    
                
        # Start applying to jobs
        apply_to_jobs(keywords)
        
        

    except Exception as e:
        print(e)
        driver.quit()

main()