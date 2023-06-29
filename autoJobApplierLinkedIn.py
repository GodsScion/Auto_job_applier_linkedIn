import os
import csv
from time import sleep
from random import randint
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Example usage
keywords = ["Java Developer"]
resumes = ["","","","",""]

username = "username@example.com" 
password = "examplepassword"

# Set the amount of time to wait between each click
click_gap = 0                   # Enter how max secs to wait approximately.

# Directory and name of the file where history of applied jobs is saved.
file_name = "all_quick_applied_history.csv"

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
            scroll_to_view(button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print("\n  -->  Click Failed! Didn't find '"+x+"'\n\n", e)

def multi_sel(l):
    for x in l:
        try:
            button = wait.until(EC.presence_of_element_located((By.XPATH, '//span[normalize-space(.)="'+x+'"]')))
            scroll_to_view(button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print("\n  -->  Click Failed! Didn't find '"+x+"'\n\n", e)

def multi_sel_noWait(l):
    for x in l:
        try:
            button = driver.find_element(By.XPATH, '//span[normalize-space(.)="'+x+'"]')
            scroll_to_view(button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print("\n  -->  Click Failed! Didn't find '"+x+"'\n\n", e)

def boolean_button_click(x):
    try:
        list_container = driver.find_element(By.XPATH, '//h3[normalize-space()="'+x+'"]/ancestor::fieldset')
        button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
        scroll_to_view(button)
        actions.move_to_element(button).click().perform()
        buffer(click_gap)
    except Exception as e:
        print("\n  -->  Click Failed! Didn't find '"+x+"'\n\n", e)

# Find functions
def find_by_class(class_name):
    return wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

# Scroll functions
def scroll_to_view(element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)


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
            print("\n  -->  Didn't find Sign in link, so assuming user is logged in!\n\n")
            return True


def login():
    # Find the username and password fields and fill them with user credentials
    driver.get("https://www.linkedin.com/login")
    # if username == "username@example.com":
    #     print("\n  -->  Please complete login, job automation starts after 60 secs!\n\n")
    #     sleep(60)
    #     return True
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            driver.find_element(By.ID, "username").send_keys(username)
        except Exception as e:
            print("\n  -->  Couldn't find username field.\n\n", e)
        try:
            driver.find_element(By.ID, "password").send_keys(password)
        except Exception as e:
            print("\n  -->  Couldn't find password field.\n\n", e)
        # Find the login submit button and click it
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
    except Exception as e1:
        try:
            profile_button = find_by_class("profile__details")
            profile_button.click()
        except Exception as e2:
            print(e1,"Couldn't Login!\n\n", e2)

    try:
        # Wait until the profile element is visible, indicating successful login
        wait.until(EC.url_to_be("https://www.linkedin.com/feed/"))
        return print("\n  -->  Login successful!\n\n")
        # wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space(.)="Start a post"]')))
        # return print("\n  -->  Login successful!\n\n")
    except Exception as e:
        print("\n  -->  Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!\n\n", e)
        count = 0
        while not is_logged_in():
            print("\n  -->  Seems like you're not logged in!")
            message = "Press Enter to continue after you logged in..."
            if count > 1:
                message = "If you're seeing this message even after you logged in, type 'skip' and press Enter to continue or just press Enter to try again..."
            count += 1
            value = input(message)
            if value == 'skip':
                return


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


# Date posted calculator
def calculate_date_posted(time_string):
    now = datetime.now()
    
    if "second" in time_string:
        seconds = int(time_string.split()[0])
        date_posted = now - timedelta(seconds=seconds)
    elif "minute" in time_string:
        minutes = int(time_string.split()[0])
        date_posted = now - timedelta(minutes=minutes)
    elif "hour" in time_string:
        hours = int(time_string.split()[0])
        date_posted = now - timedelta(hours=hours)
    elif "day" in time_string:
        days = int(time_string.split()[0])
        date_posted = now - timedelta(days=days)
    elif "week" in time_string:
        weeks = int(time_string.split()[0])
        date_posted = now - timedelta(weeks=weeks)
    elif "month" in time_string:
        months = int(time_string.split()[0])
        date_posted = now - timedelta(days=months * 30)
    elif "year" in time_string:
        years = int(time_string.split()[0])
        date_posted = now - timedelta(days=years * 365)
    else:
        date_posted = None

    return date_posted


# Apply to jobs function
def apply_to_jobs(keywords):
    applied_jobs = get_applied_job_ids()
    # Create or append to the CSV file
    with open(file_name, mode='a', newline='') as csvfile:
        fieldnames = ['Job ID', 'Job Title', 'Company', 'Job Link', 'Job Description', 'Skills', 'HR Name', 'HR Link', 'Resume Used', 'Date listed', 'Date Applied', 'External Job link' ]
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
                print("\n  -->  Setting the preferences failed!\n\n", e)    


            try:
                # Wait until job listings are loaded
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'jobs-search-results__list-item')]")))
                buffer(3)

                try:
                    pagination_element = find_by_class("artdeco-pagination")
                    scroll_to_view(pagination_element)
                except Exception as e:
                    print("\n  -->  Failed to find Pagination element, hence couldn't scroll till end!\n\n", e)

                # Find all job listings
                job_listings = driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")            
                
                for job in job_listings:
                    # Extract job details 'Job ID', 'Job Title', 'Company', 'Job Link', 'Job Description', 'Skills', 'HR Name', 'HR Link', 'Resume Used', 'Date listed', 'Date Applied', 'External Job link'
                    job_details_button = job.find_element(By.CLASS_NAME, "job-card-list__title")
                    job_id = job.get_dom_attribute('data-occludable-job-id')
                    title = job_details_button.text
                    company = job.find_element(By.CLASS_NAME, "job-card-container__primary-description").text
                    scroll_to_view(job_details_button)
                    job_details_button.click()
                    buffer(click_gap)

                    # Skip if already applied
                    try:
                        if job_id in applied_jobs or driver.find_element(By.CLASS_NAME, "jobs-s-apply__application-link"):
                            print("\n  -->  Already applied to {} job!\n\n".format(title))
                            continue
                    except Exception as e:
                        print("\n  -->  Trying to Apply to {} with Job ID: {}\n\n".format(title,job_id))

                    job_link = "https://www.linkedin.com/jobs/view/"+job_id
                    application_link = "Easy Applied"
                    date_applied = "Pending"
                    hr_link = "Unknown"
                    hr_name = "Unknown"
                    date_listed = "Unknown"
                    description = "Unknown" # Still in development
                    skills = "Unknown" # Still in development
                    resume = "Unknown" # Still in development

                    try:
                        scroll_to_view(find_by_class("jobs-company__box"))
                        buffer(1)
                        scroll_to_view(find_by_class("jobs-unified-top-card__content--two-pane"))
                        buffer(1)
                    except Exception as e:
                        print("\n  -->  Failed to scroll!\n\n", e)


                    # Hiring Manager info
                    try:
                        hr_info_card = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.CLASS_NAME, "hirer-card__hirer-information")))
                        hr_link = hr_info_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        hr_name = hr_info_card.find_element(By.TAG_NAME, "span").text
                    except Exception as e:
                        print("\n  -->  HR info was not given!\n\n", e)

                    # Calculation of date posted
                    try:
                        time_posted_text = find_by_class("jobs-unified-top-card__posted-date").text
                        date_listed = calculate_date_posted(time_posted_text)
                    except Exception as e:
                        print("\n  -->  Failed to calculate the date posted!\n\n", e)

                    # Case 1: Easy Apply Button
                    try:
                        WebDriverWait(driver,1.5).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Easy Apply")]'))).click()
                        date_applied = datetime.now()
                        try:
                            #Logic for easy Apply jobs
                            find_by_class("next")
                        except Exception as e:
                            print("\n  -->  Failed to Easy apply!\n\n", e)
                            continue
                        buffer(click_gap)
                    except Exception as e1:
                        # Case 2: Apply externally
                        if easy_apply_only: raise Exception("\n  -->  Easy apply failed i guess!\n\n")
                        try:
                            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Apply") and not(span[contains(@class, "disabled")])]'))).click()
                            windows = driver.window_handles
                            driver.switch_to.window(windows[len(windows)-1])
                            application_link = driver.current_url
                            driver.switch_to.window(windows[0])
                        except Exception as e2:
                            print(e1,e2)
                            print("\n  -->  Failed to apply!\n\n")
                            continue
                    
                    # Once the application is submitted successfully, add the application details to the CSV
                    writer.writerow({'Job ID':job_id, 'Job Title':title, 'Company':company, 'Job Link':job_link, 'Job Description':description, 'Skills':skills, 'HR Name':hr_name, 'HR Link':hr_link, 'Resume Used':resume, 'Date listed':date_listed, 'Date Applied':date_applied, 'External Job link':application_link})
                    applied_jobs.add(job_id)

            except Exception as e:
                print("\n  -->  Failed to find Job listings!\n\n", e)
    
    # Close the browser and csv file
    csvfile.close()
    driver.quit()


        


# Set up WebDriver with Chrome Profile
options = Options()
profile_dir = find_default_profile_directory()
if profile_dir:
    options.add_argument(f"--user-data-dir={profile_dir}")
else:
    print("\n  -->  Default profile directory not found. Using a new profile.")
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