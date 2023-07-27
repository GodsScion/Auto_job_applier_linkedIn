# Imports
import os
import csv
from datetime import datetime
from modules.open_chrome import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from setup.config import *
from modules.helpers import *
from modules.clickers_and_finders import *
from modules.validator import validate_config
from resume_generator import is_logged_in_GPT ,login_GPT, open_resume_chat, create_custom_resume



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

        if easy_apply_only: boolean_button_click(driver, actions, "Easy Apply")
        
        multi_sel_noWait(driver, location)
        multi_sel_noWait(driver, industry)
        if location or industry: buffer(recommended_wait)

        multi_sel_noWait(driver, job_function)
        multi_sel_noWait(driver, job_titles)
        if job_function or job_titles: buffer(recommended_wait)

        if under_10_applicants: boolean_button_click(driver, actions, "Under 10 applicants")
        if in_your_network: boolean_button_click(driver, actions, "In your network")
        if fair_chance_employer: boolean_button_click(driver, actions, "Fair Chance Employer")

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
        
    for keyword in keywords:
        driver.get(f"https://www.linkedin.com/jobs/search/?keywords={keyword}")
        print(f'\nNow searching for "{keyword}"\n')

        apply_filters()

        current_count = 0
        try:
            while current_count >= switch_number:
                # Wait until job listings are loaded
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'jobs-search-results__list-item')]")))
                buffer(3)

                # try:
                pagination_element = find_by_class(driver, "artdeco-pagination")
                scroll_to_view(driver, pagination_element)
                current_page = int(pagination_element.find_element(By.XPATH, "//li[contains(@class, 'active')]").text)
                # except Exception as e:
                #     print("Failed to find Pagination element, hence couldn't scroll till end!")
                #     # print(e)


                # Find all job listings in current page
                job_listings = driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")  

            
                for job in job_listings:
                    if current_count >= switch_number: break

                    # Skip if already applied
                    job_id = job.get_dom_attribute('data-occludable-job-id')
                    try:
                        if job_id in applied_jobs or driver.find_element(By.CLASS_NAME, "jobs-s-apply__application-link"):
                            print('Already applied to "{} - {}" job. Job ID: {}!'.format(company, title, job_id))
                            continue
                    except Exception as e:
                        print('Trying to Apply to "{} - {}" job. Job ID: {}'.format(company, title, job_id))

                    job_details_button = job.find_element(By.CLASS_NAME, "job-card-list__title")
                    title = job_details_button.text
                    company = job.find_element(By.CLASS_NAME, "job-card-container__primary-description").text
                    scroll_to_view(driver, job_details_button)
                    job_details_button.click()
                    buffer(click_gap)

                    job_link = "https://www.linkedin.com/jobs/view/"+job_id
                    application_link = "Easy Applied"
                    date_applied = "Pending"
                    hr_link = "Unknown"
                    hr_name = "Unknown"
                    date_listed = "Unknown"
                    description = "Unknown"
                    skills = "Unknown" # Still in development
                    resume = "Pending"
                    repost = False
                    questions_list = None

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
                        # try: time_posted_text = find_by_class(driver, "jobs-unified-top-card__posted-date", 2).text
                        # except: 
                        time_posted_text = driver.find_element(By.XPATH, '//span[contains(normalize-space(), "ago")]').text
                        if time_posted_text.__contains__("Reposted"):
                            repost = True
                            time_posted_text = time_posted_text.replace("Reposted", "")
                        date_listed = calculate_date_posted(time_posted_text)
                    except Exception as e:
                        print("Failed to calculate the date posted!")
                        print(e)

                    # Get job description
                    try:
                        description = find_by_class(driver, "jobs-box__html-content").text
                    except Exception as e:
                        print("Unable to extract job description!")
                        # print(e)

                    # Case 1: Easy Apply Button
                    if wait_span_click(driver, "Easy Apply", 1.5):
                        try: 
                            try:
                                next_button = wait_span_click(driver, "Next", 1)
                                resume = default_resume_path
                                # if description != "Unknown":
                                #     resume = create_custom_resume(description)
                                driver.find_element(By.NAME, "file").send_keys(os.path.abspath(resume))
                                resume = os.path.basename(resume)
                                next_button = wait_span_click(driver, "Next", 1, False)
                                questions_list = []
                                while (next_button):
                                    
                                    # Find all radio buttons with text as Yes and click them
                                    yes_radio_buttons = driver.find_elements(By.XPATH, "//label[normalize-space()='Yes']")
                                    for radio_button in yes_radio_buttons:
                                        radio_button.click()

                                    # Find all text inputs and fill them with years_of_experience if it's empty
                                    text_inputs = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--input")
                                    for text_input in text_inputs:
                                        if not text_input.get_attribute("value"): text_input.send_keys(years_of_experience)

                                    # Find all radio buttons with text as Yes and click them
                                    select_buttons = driver.find_elements(By.XPATH, "//select")
                                    for select in select_buttons:
                                        select = Select(select)
                                        select.select_by_visible_text('Yes')
                                    
                                    # Gathering questions
                                    all_radio_questions = driver.find_elements(By.CLASS_NAME, "fb-dash-form-element__label")
                                    for question in all_radio_questions:
                                        question = question.find_element(By.CLASS_NAME, "visually-hidden").text
                                        questions_list.append((question, "Yes", "radio"))
                                    
                                    all_text_questions = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--label")
                                    for question in all_text_questions:
                                        question = question.text
                                        questions_list.append((question, years_of_experience, "text"))

                                    all_select_questions = driver.find_elements(By.XPATH, "//label[@data-test-text-entity-list-form-title]")
                                    for question in all_select_questions:
                                        question = question.text
                                        questions_list.append((question, "Yes", "select"))
                                    
                                    next_button = driver.find_element(By.XPATH, '//button[contains(span, "Next")]')
                                    next_button.click()
                                    buffer(click_gap)

                            except NoSuchElementException:
                                if questions_list:
                                    print("Answered the following questions...")
                                    print(questions_list)
                                wait_span_click(driver, "Review", 2)
                                wait_span_click(driver, "Submit application", 2)
                                try: driver.find_element(By.XPATH, "//button[@data-test-modal-close-btn]").click()
                                except: pass
                        except Exception as e:
                            print("Failed to Easy apply!")
                            # print(e)
                            failed_job(job_id, job_link, resume, date_listed, "Problem in Easy Applying", e, application_link)
                            actions.send_keys(Keys.ESCAPE).perform()
                            driver.find_element(By.XPATH, "//span[normalize-space()='Discard']").click()
                            continue
                    else:
                        # Case 2: Apply externally
                        if easy_apply_only: raise Exception("Easy apply failed I guess!")
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
                    
                    # Create or append to the CSV file
                    with open(file_name, mode='a', newline='') as csv_file:
                        fieldnames = ['Job ID', 'Title', 'Company', 'Description', 'Skills', 'HR Name', 'HR Link', 'Resume', 'Re-post', 'Date listed', 'Date Applied', 'Job Link', 'External Job link', 'Questions']
                        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                        if csv_file.tell() == 0: writer.writeheader()
                        # Once the application is submitted successfully, add the application details to the CSV
                        writer.writerow({'Job ID':job_id, 'Title':title, 'Company':company, 'Description':description, 'Skills':skills, 
                                            'HR Name':hr_name, 'HR Link':hr_link, 'Resume':resume, 'Re-post':repost, 
                                            'Date listed':date_listed, 'Date Applied':date_applied, 'Job Link':job_link, 
                                            'External Job link':application_link, 'Questions':questions_list})
                    csv_file.close()
                    current_count += 1
                    applied_jobs.add(job_id)

                # Switching to next page
                try: pagination_element.find_element(By.XPATH, f"//button[@aria-label='Page {current_page+1}']").click()
                except NoSuchElementException:
                    print(f"Didn't find Page {current_page+1}. Probably at the end page of result!")
                    break

        except Exception as e:
            print("Failed to find Job listings!")
            critical_error_log("In Applier", e)
            # print(e)

    # Close csv file
    csv_file.close()

        
def run(total_runs):
    print("__________________________________________________________")
    print(f"Cycle number {total_runs+1} ...")
    print("Currently looking for jobs posted within '{date_posted}' and sorting them by '{sort_by}'")
    apply_to_jobs(keywords)
    print("__________________________________________________________")
    print("Sleeping for 10 min...")
    sleep(600)
    print("Few more min... Gonna start with in next 5 min...")
    buffer(300)
    return total_runs + 1



chatGPT_tab = False
linkedIn_tab = False
def main():
    try:
        validate_config()

        # Login to LinkedIn
        driver.get("https://www.linkedin.com/login")
        if not is_logged_in_LN(): login_LN()
        global linkedIn_tab
        linkedIn_tab = driver.current_window_handle

        # Opening ChatGPT tab for resume customization
        # try:
        #     driver.switch_to.new_window('tab')
        #     driver.get("https://chat.openai.com/")
        #     if not is_logged_in_GPT(): login_GPT()
        #     open_resume_chat()
        #     global chatGPT_tab
        #     chatGPT_tab = driver.current_window_handle
        # except Exception as e:
        #     print("Opening OpenAI chatGPT tab failed!")

        # Start applying to jobs
        driver.switch_to.window(linkedIn_tab)
        total_runs = 0
        total_runs = run(total_runs)
        while(run_non_stop):
            if cycle_date_posted:
                date_options = ["Any time", "Past month", "Past week", "Past 24 hours"]
                global date_posted
                date_posted = date_options[0 if date_options.index(date_posted) + 1 > len(date_options) else date_options.index(date_posted) + 1]
            if alternate_sortby:
                total_runs = run(total_runs)
                global sort_by
                sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
            
            total_runs = run(total_runs)
        

    except Exception as e:
        print(e)
        critical_error_log("In Applier Main", e)
        driver.quit()
    finally:
        exit(0)

main()