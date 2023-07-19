# Imports
import csv
from datetime import datetime
from modules.open_chrome import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from setup.config import *
from modules.helpers import *
from modules.clickers_and_finders import *
from resume_generator import is_logged_in_GPT ,login_GPT, open_resume_chat



# Login Functions
def is_logged_in_LN():
    if driver.current_url == "https://www.linkedin.com/feed/": return True
    try:
        driver.find_element(By.LINK_TEXT, "Sign in")
        return False
    except Exception as e1:
        try:
            driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]')
            return False
        except Exception as e2:
            # print(e1, e2)
            print("Didn't find Sign in link, so assuming user is logged in!")
            return True


def login_LN():
    # Find the username and password fields and fill them with user credentials
    driver.get("https://www.linkedin.com/login")
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            text_input_by_ID(driver, "username", username, 1)
        except Exception as e:
            print("Couldn't find username field.")
            # print(e)
        try:
            text_input_by_ID(driver, "password", password, 1)
        except Exception as e:
            print("Couldn't find password field.")
            # print(e)
        # Find the login submit button and click it
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
    except Exception as e1:
        try:
            profile_button = find_by_class(driver, "profile__details")
            profile_button.click()
        except Exception as e2:
            # print(e1, e2)
            print("Couldn't Login!")

    try:
        # Wait until successful redirect, indicating successful login
        wait.until(EC.url_to_be("https://www.linkedin.com/feed/")) # wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space(.)="Start a post"]')))
        return print("Login successful!")
    except Exception as e:
        print("Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!")
        # print(e)
        manual_login_retry(is_logged_in_LN)



# Apply filters Function
def apply_filters():
    try:
        recommended_wait = 1 if click_gap < 1 else 0

        wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="All filters"]'))).click()
        buffer(recommended_wait)

        wait_span_click(driver, sort_by)
        wait_span_click(driver, date_posted)
        buffer(recommended_wait)

        multi_sel(driver, experience_level) 
        multi_sel_noWait(driver, companies)
        if experience_level or companies: buffer(recommended_wait)

        multi_sel(driver, job_type)
        multi_sel(driver, on_site)
        if job_type or on_site: buffer(recommended_wait)

        if easy_apply_only: boolean_button_click(driver, "Easy Apply")
        
        multi_sel_noWait(driver, location)
        multi_sel_noWait(driver, industry)
        if location or industry: buffer(recommended_wait)

        multi_sel_noWait(driver, job_function)
        multi_sel_noWait(driver, job_titles)
        if job_function or job_titles: buffer(recommended_wait)

        if under_10_applicants: boolean_button_click(driver, "Under 10 applicants")
        if in_your_network: boolean_button_click(driver, "In your network")
        if fair_chance_employer: boolean_button_click(driver, "Fair Chance Employer")

        wait_span_click(driver, salary)
        buffer(recommended_wait)
        
        multi_sel_noWait(driver, benefits)
        multi_sel_noWait(driver, commitments)
        if benefits or commitments: buffer(recommended_wait)

        show_results_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Apply current filters to show")]')
        show_results_button.click()

    except Exception as e:
        print("Setting the preferences failed!")
        # print(e)



# Apply to jobs function
def apply_to_jobs(keywords):
    applied_jobs = get_applied_job_ids()
    # Create or append to the CSV file
    with open(file_name, mode='a', newline='') as csvfile:
        fieldnames = ['Job ID', 'Title', 'Company', 'Description', 'Skills', 'HR Name', 'HR Link', 'Resume Used', 'Date listed', 'Date Applied', 'Job Link', 'External Job link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        
        for keyword in keywords:
            url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
            driver.get(url)

            apply_filters()

            try:
                # Wait until job listings are loaded
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'jobs-search-results__list-item')]")))
                buffer(3)

                try:
                    pagination_element = find_by_class(driver, "artdeco-pagination")
                    scroll_to_view(driver, pagination_element)
                except Exception as e:
                    print("Failed to find Pagination element, hence couldn't scroll till end!")
                    # print(e)

                # Find all job listings
                job_listings = driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")            
                
                count = 0
                for job in job_listings:
                    count += 1
                    assert count < 4
                    # Extract job details 'Job ID', 'Title', 'Company', 'Description', 'Skills', 'HR Name', 'HR Link', 'Resume Used', 'Date listed', 'Date Applied', 'Job Link', 'External Job link'
                    job_details_button = job.find_element(By.CLASS_NAME, "job-card-list__title")
                    job_id = job.get_dom_attribute('data-occludable-job-id')
                    title = job_details_button.text
                    company = job.find_element(By.CLASS_NAME, "job-card-container__primary-description").text
                    scroll_to_view(driver, job_details_button)
                    job_details_button.click()
                    buffer(click_gap)

                    # Skip if already applied
                    try:
                        if job_id in applied_jobs or driver.find_element(By.CLASS_NAME, "jobs-s-apply__application-link"):
                            print("Already applied to '{}' job  with Job ID: {}!".format(title,job_id))
                            continue
                    except Exception as e:
                        print("Trying to Apply to '{}' with Job ID: {}".format(title,job_id))

                    job_link = "https://www.linkedin.com/jobs/view/"+job_id
                    application_link = "Easy Applied"
                    date_applied = "Pending"
                    hr_link = "Unknown"
                    hr_name = "Unknown"
                    date_listed = "Unknown"
                    description = "Unknown"
                    skills = "Unknown" # Still in development
                    resume = "Unknown" # Still in development

                    try:
                        scroll_to_view(driver, find_by_class(driver, "jobs-company__box"))
                        scroll_to_view(driver, find_by_class(driver, "jobs-unified-top-card__content--two-pane"))
                    except Exception as e:
                        print("Failed to scroll!")
                        # print(e)


                    # Hiring Manager info
                    try:
                        hr_info_card = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.CLASS_NAME, "hirer-card__hirer-information")))
                        hr_link = hr_info_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        hr_name = hr_info_card.find_element(By.TAG_NAME, "span").text
                    except Exception as e:
                        print(f"HR info was not given for '{title}' with Job ID: {job_id}!")
                        # print(e)

                    # Calculation of date posted
                    try:
                        time_posted_text = find_by_class(driver, "jobs-unified-top-card__posted-date").text
                        date_listed = calculate_date_posted(time_posted_text)
                    except Exception as e:
                        print("Failed to calculate the date posted!")
                        # print(e)

                    # Get job description
                    try:
                        description = find_by_class(driver, "jobs-box__html-content").text
                    except Exception as e:
                        print("Unable to extract job description!")
                        # print(e)

                    # Case 1: Easy Apply Button
                    if wait_span_click(driver, "Easy Apply", 1.5): # WebDriverWait(driver,1.5).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Easy Apply")]'))).click()
                        try:
                            try:
                                next_button = wait_span_click(driver, "Next", 1, False) # WebDriverWait(driver,1).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Next")]')))
                                while (next_button):
                                    next_button = driver.find_element(By.XPATH, '//button[contains(span, "Next")]')
                                    
                                    break
                                    print()
                            except TimeoutException:
                                wait_span_click(driver, "Submit application",2)
                                # WebDriverWait(driver,2).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Submit application")]'))).click()

                            date_applied = datetime.now()
                        except Exception as e:
                            print("Failed to Easy apply!")
                            # print(e)
                            failed_job(job_id, job_link, resume, date_listed, "Problem in Easy Applying", e, application_link)
                            continue
                    else:
                        # Case 2: Apply externally
                        if easy_apply_only: raise Exception("Easy apply failed i guess!")
                        try:
                            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Apply") and not(span[contains(@class, "disabled")])]'))).click()
                            windows = driver.window_handles
                            driver.switch_to.window(windows[-1])
                            application_link = driver.current_url
                            if close_tabs: driver.close()
                            driver.switch_to.window(linkedIn_tab)
                        except Exception as e:
                            # print(e)
                            print("Failed to apply!")
                            failed_job(job_id, job_link, resume, date_listed, "Probably didn't find Apply button or unable to switch tabs.", e, application_link)
                            continue
                    
                    # Once the application is submitted successfully, add the application details to the CSV
                    writer.writerow({'Job ID':job_id, 'Title':title, 'Company':company, 'Description':description, 'Skills':skills, 'HR Name':hr_name, 'HR Link':hr_link, 'Resume Used':resume, 'Date listed':date_listed, 'Date Applied':date_applied, 'Job Link':job_link, 'External Job link':application_link})
                    applied_jobs.add(job_id)

            except Exception as e:
                print("Failed to find Job listings!")
                # print(e)
    
    # Close the browser and csv file
    csvfile.close()
    driver.quit()


        




chatGPT_tab = False
linkedIn_tab = False
def main():
    try:
        # Login to LinkedIn
        driver.get("https://www.linkedin.com/login")
        if not is_logged_in_LN(): login_LN()
        global linkedIn_tab
        linkedIn_tab = driver.current_window_handle

        # Opening ChatGPT tab for resume customization
        try:
            driver.switch_to.new_window('tab')
            driver.get("https://chat.openai.com/")
            if not is_logged_in_GPT(): login_GPT()
            open_resume_chat()
            
            global chatGPT_tab
            chatGPT_tab = driver.current_window_handle
        except Exception as e:
            print("Opening OpenAI chatGPT tab failed!")

        # Start applying to jobs
        apply_to_jobs(keywords)
        

    except Exception as e:
        print(e)
        driver.quit()

main()