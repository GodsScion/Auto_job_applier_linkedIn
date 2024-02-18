'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

'''


# Imports
import os
import csv
import re
from pyautogui import press, alert, confirm
from random import choice, shuffle
from datetime import datetime
from modules.open_chrome import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException
from setup.config import *
from modules.helpers import *
from modules.clickers_and_finders import *
from modules.validator import validate_config
if use_resume_generator:    from resume_generator import is_logged_in_GPT, login_GPT, open_resume_chat, create_custom_resume



#< Login Functions

# Function to check if user is logged-in in LinkedIn
def is_logged_in_LN():
    if driver.current_url == "https://www.linkedin.com/feed/": return True
    if try_linkText(driver, "Sign in"): return False
    if try_xp(driver, '//button[@type="submit" and contains(text(), "Sign in")]'):  return False
    if try_linkText(driver, "Join now"): return False
    print_lg("Didn't find Sign in link, so assuming user is logged in!")
    return True

# Function to login for LinkedIn
def login_LN():
    # Find the username and password fields and fill them with user credentials
    driver.get("https://www.linkedin.com/login")
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            text_input_by_ID(driver, "username", username, 1)
        except Exception as e:
            print_lg("Couldn't find username field.")
            # print_lg(e)
        try:
            text_input_by_ID(driver, "password", password, 1)
        except Exception as e:
            print_lg("Couldn't find password field.")
            # print_lg(e)
        # Find the login submit button and click it
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
    except Exception as e1:
        try:
            profile_button = find_by_class(driver, "profile__details")
            profile_button.click()
        except Exception as e2:
            # print_lg(e1, e2)
            print_lg("Couldn't Login!")

    try:
        # Wait until successful redirect, indicating successful login
        wait.until(EC.url_to_be("https://www.linkedin.com/feed/")) # wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space(.)="Start a post"]')))
        return print_lg("Login successful!")
    except Exception as e:
        print_lg("Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!")
        # print_lg(e)
        manual_login_retry(is_logged_in_LN, 2)
#>



# Function to get list of applied job's Job IDs
def get_applied_job_ids():
    job_ids = set()
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                job_ids.add(row[0])
    except FileNotFoundError:
        print_lg(f"The CSV file '{file_name}' does not exist.")
    return job_ids



# Function to apply job search filters
def apply_filters():
    try:
        recommended_wait = 1 if click_gap < 1 else 0

        wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="All filters"]'))).click()
        buffer(recommended_wait)

        wait_span_click(driver, sort_by)
        wait_span_click(driver, date_posted)
        buffer(recommended_wait)

        multi_sel(driver, experience_level) 
        multi_sel_noWait(driver, companies, actions)
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
        print_lg("Setting the preferences failed!")
        # print_lg(e)



# Function to get pagination element and current page number
def get_page_info():
    try:
        pagination_element = find_by_class(driver, "artdeco-pagination")
        scroll_to_view(driver, pagination_element)
        current_page = int(pagination_element.find_element(By.XPATH, "//li[contains(@class, 'active')]").text)
    except Exception as e:
        print_lg("Failed to find Pagination element, hence couldn't scroll till end!")
        pagination_element = None
        current_page = None
        # print_lg(e)
    return pagination_element, current_page



# Function to get job main details
def get_job_main_details(job):
    job_details_button = job.find_element(By.CLASS_NAME, "job-card-list__title")
    scroll_to_view(driver, job_details_button, True)
    title = job_details_button.text
    company = job.find_element(By.CLASS_NAME, "job-card-container__primary-description").text
    job_id = job.get_dom_attribute('data-occludable-job-id')
    work_location = job.find_element(By.CLASS_NAME, "job-card-container__metadata-item").text
    work_style = work_location[work_location.rfind('(')+1:work_location.rfind(')')]
    work_location = work_location[:work_location.rfind('(')].strip()
    try: job_details_button.click()
    except Exception as e:
        print_lg(f'Failed to click "{title} | {company}" job on details button. Job ID: {job_id}!') 
        # print_lg(e)
        discard_job()
        job_details_button.click()
    buffer(click_gap)
    return (job_id,title,company,work_location,work_style)


# Function to check for Blacklisted words in About Company
def check_blacklist(rejected_jobs,job_id):
    about_company_org = find_by_class(driver, "jobs-company__box")
    scroll_to_view(driver, about_company_org)
    about_company_org = about_company_org.text
    about_company = about_company_org.lower()
    for word in blacklist_words: 
        if word.lower() in about_company: 
            rejected_jobs.add(job_id)
            raise ValueError(f'Found the word "{word}" in \n"{about_company_org}"')
    buffer(1)
    scroll_to_view(driver, find_by_class(driver, "jobs-unified-top-card"))
    return rejected_jobs



# Function to extract years of experience required from About Job
def extract_years_of_experience(text):
    # Extract all patterns like '10+ years', '5 years', '3-5 years', etc.
    matches = re.findall(r'[(]?\s*(\d+)\s*[)]?\s*[-to]*\s*\d*[+]*\s*year[s]?', text, flags=re.IGNORECASE)
    if len(matches) == 0: 
        print_lg(f'Couldn\'t find experience requirement in About job \n{text}\n')
    return max([int(match) for match in matches if int(match) <= 12])



# Function to answer the questions for Easy Apply
def answer_questions(questions_list):
    # Find all Select Questions
    select_buttons = driver.find_elements(By.XPATH, "//select")
    for select in select_buttons:
        label_org = "Unknown"
        try: label_org = driver.find_element(By.XPATH, f"//label[@for='{select.get_attribute('id')}']").find_element(By.CLASS_NAME, "visually-hidden").text
        except: pass
        answer = 'Yes'
        label = label_org.lower()
        if 'gender' in label or 'sex' in label: answer = gender
        if 'disability' in label: answer = disability_status
        select = Select(select)
        selected_option = select.first_selected_option.text
        if selected_option != "Select an option": continue
        try:
            select.select_by_visible_text(answer)
        except NoSuchElementException as e:
            print_lg(f'Failed to find an option with text "{answer}" for question labelled "{label_org}", answering randomly!')
        questions_list.add((label_org, select.first_selected_option.text, "select")) # <<<<<<<<<<<<<<<<<<


    # Find all radio questions
    all_radio_questions = driver.find_elements(By.XPATH, '//fieldset[@data-test-form-builder-radio-button-form-component="true"]')
    for question in all_radio_questions:
        label = question.find_elements(By.XPATH, './/span[@data-test-form-builder-radio-button-form-component__title]')
        label = label[0].find_element(By.CLASS_NAME, 'visually-hidden').text if len(label) > 0 else "Unknown"
        label = label.lower()
        answer = 'Yes'
        if 'citizenship' in label or 'employment eligibility' in label: answer = us_citizenship
        if 'sponsorship' in label or 'visa' in label: answer = require_visa
        try: question.find_element(By.XPATH, f".//label[normalize-space()='{answer}']").click()
        except:
            random = question.find_element(By.XPATH, ".//label[@data-test-text-selectable-option__label]")
            answer = random.text
            random.click()
        questions_list.add((label, answer, "radio"))
    
    # Find all text questions and answer them
    all_text_questions = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--container")
    for question in all_text_questions:
        label_org = "Unknown"
        try: label_org = question.find_element(By.CLASS_NAME, "artdeco-text-input--label").text
        except: continue
        answer = years_of_experience
        label = label_org.lower()
        if 'your name' in label or 'full name' in label: answer = full_name
        if 'website' in label or 'blog' in label or 'portfolio' in label: answer = website
        if 'salary' in label or 'compensation' in label: answer = desired_salary
        if 'scale of 1-10' in label: answer = confidence_level
        if 'city' in label or 'location' in label: answer = current_city
        text_input = question.find_element(By.CLASS_NAME, "artdeco-text-input--input")
        if not text_input.get_attribute("value"): text_input.send_keys(answer)
        questions_list.add((label_org, text_input.get_attribute("value"), "text"))

    try_xp(driver, "//button[contains(@aria-label, 'This is today')]")

    # Redundancy

    # # Fill any left out texts with years_of_experience
    # text_inputs = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--input")
    # for text_input in text_inputs:
    #     if not text_input.get_attribute("value"): text_input.send_keys(years_of_experience)

    # # All select questions
    # all_select_questions = driver.find_elements(By.XPATH, "//label[@data-test-text-entity-list-form-title]")
    # for question in all_select_questions:
    #     question = question.text
    #     questions_list.add((question, "Yes", "select"))    

    return questions_list










#< Failed attempts logging

# Function to update failed jobs list in excel
def failed_job(job_id, job_link, resume, date_listed, error, exception, application_link, screenshot_name):
    with open(failed_file_name, 'a', newline='', encoding='utf-8') as file:
        fieldnames = ['Job ID', 'Job Link', 'Resume Tried', 'Date listed', 'Date Tried', 'Assumed Reason', 'Stack Trace', 'External Job link', 'Screenshot Name']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0: writer.writeheader()
        writer.writerow({'Job ID':job_id, 'Job Link':job_link, 'Resume Tried':resume, 'Date listed':date_listed, 'Date Tried':datetime.now(), 'Assumed Reason':error, 'Stack Trace':exception, 'External Job link':application_link, 'Screenshot Name':screenshot_name})
        file.close()


# Function to to take screenshot for debugging
def screenshot(driver, job_id, failedAt):
    screenshot_name = "{} - {} - {}.png".format( job_id, failedAt, str(datetime.now()) )
    path = logs_folder_path+"/screenshots/"+screenshot_name.replace(":",".")
    # special_chars = {'*', '"', '\\', '<', '>', ':', '|', '?'}
    # for char in special_chars:  path = path.replace(char, '-')
    driver.save_screenshot(path.replace("//","/"))
    return screenshot_name
#>



# Function to create or append to the CSV file, once the application is submitted successfully
def submitted_jobs(job_id, title, company, work_location, work_style, description, experience_required, skills, hr_name, hr_link, resume, reposted, date_listed, date_applied, job_link, application_link, questions_list, connect_request):
    with open(file_name, mode='a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Job ID', 'Title', 'Company', 'Work Location', 'Work Style', 'About Job', 'Experience required', 'Skills required', 'HR Name', 'HR Link', 'Resume', 'Re-posted', 'Date Posted', 'Date Applied', 'Job Link', 'External Job link', 'Questions Found', 'Connect Request']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0: writer.writeheader()
        writer.writerow({'Job ID':job_id, 'Title':title, 'Company':company, 'Work Location':work_location, 'Work Style':work_style, 
                        'About Job':description, 'Experience required': experience_required, 'Skills required':skills, 
                            'HR Name':hr_name, 'HR Link':hr_link, 'Resume':resume, 'Re-posted':reposted, 
                            'Date Posted':date_listed, 'Date Applied':date_applied, 'Job Link':job_link, 
                            'External Job link':application_link, 'Questions Found':questions_list, 'Connect Request':connect_request})
    csv_file.close()



# Function to discard the job application
def discard_job():
    actions.send_keys(Keys.ESCAPE).perform()
    wait_span_click(driver, 'Discard', 2)






# Function to apply to jobs
def apply_to_jobs(search_terms):
    applied_jobs = get_applied_job_ids()
    rejected_jobs = set()

    if randomize_search_order:  shuffle(search_terms)
    for searchTerm in search_terms:
        driver.get(f"https://www.linkedin.com/jobs/search/?keywords={searchTerm}")
        print_lg("\n________________________________________________________________________________________________________________________\n")
        print_lg(f'\n>>>> Now searching for "{searchTerm}" <<<<\n\n')

        apply_filters()

        current_count = 0
        try:
            while current_count < switch_number:
                # Wait until job listings are loaded
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'jobs-search-results__list-item')]")))

                pagination_element, current_page = get_page_info()

                # Find all job listings in current page
                buffer(3)
                job_listings = driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")  

            
                for job in job_listings:
                    if keep_screen_awake: press('shiftright')
                    if current_count >= switch_number: break
                    print_lg("\n-@-\n")

                    job_id,title,company,work_location,work_style = get_job_main_details(job)
                    
                    # Skip if previously rejected due to blacklist or already applied
                    if job_id in rejected_jobs: 
                        print_lg(f'Skipping previously rejected "{title} | {company}" job. Job ID: {job_id}!')
                        continue
                    try:
                        if job_id in applied_jobs or find_by_class(driver, "jobs-s-apply__application-link", 2):
                            print_lg(f'Already applied to "{title} | {company}" job. Job ID: {job_id}!')
                            continue
                    except Exception as e:
                        print_lg(f'Trying to Apply to "{title} | {company}" job. Job ID: {job_id}')

                    job_link = "https://www.linkedin.com/jobs/view/"+job_id
                    application_link = "Easy Applied"
                    date_applied = "Pending"
                    hr_link = "Unknown"
                    hr_name = "Unknown"
                    connect_request = "In Development" # Still in development
                    date_listed = "Unknown"
                    description = "Unknown"
                    experience_required = "Unknown"
                    skills = "In Development" # Still in development
                    resume = "Pending"
                    reposted = False
                    questions_list = None
                    screenshot_name = "Not Available"

                    try:
                        rejected_jobs = check_blacklist(rejected_jobs,job_id)
                    except ValueError as e:
                        print_lg('Skipping this job.', e)
                        failed_job(job_id, job_link, resume, date_listed, "Found Blacklisted words in About Company", e, "Skipped", screenshot_name)
                        continue
                    except Exception as e:
                        print_lg("Failed to scroll to About Company!")
                        # print_lg(e)



                    # Hiring Manager info
                    try:
                        hr_info_card = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.CLASS_NAME, "hirer-card__hirer-information")))
                        hr_link = hr_info_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        hr_name = hr_info_card.find_element(By.TAG_NAME, "span").text
                        # if connect_hr:
                        #     driver.switch_to.new_window('tab')
                        #     driver.get(hr_link)
                        #     wait_span_click("More")
                        #     wait_span_click("Connect")
                        #     wait_span_click("Add a note")
                        #     message_box = driver.find_element(By.XPATH, "//textarea")
                        #     message_box.send_keys(connect_request_message)
                        #     if close_tabs: driver.close()
                        #     driver.switch_to.window(linkedIn_tab) 
                        # def message_hr(hr_info_card):
                        #     if not hr_info_card: return False
                        #     hr_info_card.find_element(By.XPATH, ".//span[normalize-space()='Message']").click()
                        #     message_box = driver.find_element(By.XPATH, "//div[@aria-label='Write a message…']")
                        #     message_box.send_keys()
                        #     try_xp(driver, "//button[normalize-space()='Send']")        
                    except Exception as e:
                        print_lg(f'HR info was not given for "{title}" with Job ID: {job_id}!')
                        # print_lg(e)


                    # Calculation of date posted
                    try:
                        # try: time_posted_text = find_by_class(driver, "jobs-unified-top-card__posted-date", 2).text
                        # except: 
                        jobs_top_card = try_find_by_classes(driver, ["job-details-jobs-unified-top-card__primary-description-container","job-details-jobs-unified-top-card__primary-description","jobs-unified-top-card__primary-description"])
                        time_posted_text = jobs_top_card.find_element(By.XPATH, './/span[contains(normalize-space(), "ago")]').text
                        if time_posted_text.__contains__("Reposted"):
                            reposted = True
                            time_posted_text = time_posted_text.replace("Reposted", "")
                        date_listed = calculate_date_posted(time_posted_text)
                    except Exception as e:
                        print_lg("Failed to calculate the date posted!",e)

                    # Get job description
                    try:
                        description = find_by_class(driver, "jobs-box__html-content").text
                        if did_masters and current_experience >= 2 and 'master' in description.lower():
                            print_lg(f'Skipped checking for minimum years of experience required cause found the word "master" in \n{description}')
                        else:
                            experience_required = extract_years_of_experience(description)
                            if current_experience > -1 and experience_required > current_experience:
                                message = f'Experience required {experience_required} > Current Experience {current_experience}\n{description}'
                                print_lg('Skipping this job.', message)
                                failed_job(job_id, job_link, resume, date_listed, "Required experience is high", message, "Skipped", screenshot_name)
                                rejected_jobs.add(job_id)
                                continue
                    except Exception as e:
                        if description == "Unknown":    print_lg("Unable to extract job description!")
                        else:
                            experience_required = "Error in extraction"
                            print_lg("Unable to extract years of experience required!")
                        # print_lg(e)

                    # Case 1: Easy Apply Button
                    if wait_span_click(driver, "Easy Apply", 2):
                        try: 
                            try:
                                errored = ""
                                wait_span_click(driver, "Next", 1)
                                resume = default_resume_path
                                # if description != "Unknown":
                                #     resume = create_custom_resume(description)
                                wait_span_click(driver, "Next", 1)
                                # driver.find_element(By.NAME, "file").send_keys(os.path.abspath(resume))
                                resume = os.path.basename(resume)
                                next_button = True
                                questions_list = set()
                                next_counter = 0
                                while next_button:
                                    next_counter += 1
                                    if next_counter >= 6: 
                                        if pause_at_failed_question:
                                            screenshot(driver, job_id, "Needed manual intervention for failed question")
                                            alert("Couldn't answer one or more questions.\nPlease click \"Continue\" once done.\nDO NOT CLICK Next or Review button in LinkedIn.\n\n\n\n\nYou can turn off \"Pause at failed question\" setting in config.py", "Help Needed", "Continue")
                                            next_counter = 1
                                            continue
                                        if questions_list: print_lg("Stuck for one or some of the following questions...", questions_list)
                                        screenshot_name = screenshot(driver, job_id, "Failed at questions")
                                        errored = "stuck"
                                        raise Exception("Seems like stuck in a continuous loop of next, probably because of new questions.")
                                    questions_list = answer_questions(questions_list)
                                    try:    next_button = driver.find_element(By.XPATH, '//button[contains(span, "Next")]')
                                    except NoSuchElementException:  next_button = driver.find_element(By.XPATH, '//span[normalize-space(.)="Review"]')
                                    try: next_button.click()
                                    except ElementClickInterceptedException:    break   # Happens when it tries to click Next button in About Company photos section
                                    buffer(click_gap)

                            except NoSuchElementException:
                                if questions_list: print_lg("Answered the following questions...", questions_list)
                                errored = "nose"
                            finally:
                                wait_span_click(driver, "Review", 2, scrollTop=True)
                                if errored != "stuck" and pause_before_submit: alert('1. Please verify your information.\n2. If you edited something, please return to this final screen.\n3. DO NOT CLICK "Submit Application".\n\n\n\n\nYou can turn off "Pause before submit" setting in config.py',"Paused")
                                if wait_span_click(driver, "Submit application", 2, scrollTop=True): 
                                    date_applied = datetime.now()
                                    if not wait_span_click(driver, "Done", 2): actions.send_keys(Keys.ESCAPE).perform()
                                elif errored != "stuck" and pause_before_submit and "Yes" in confirm("You submitted the application, didn't you 😒?", "Failed to find Submit Application!", ["Yes", "No"]):
                                    date_applied = datetime.now()
                                    wait_span_click(driver, "Done", 2)
                                else:
                                    print_lg("Since, Submit Application failed, discarding the job application...")
                                    # if screenshot_name == "Not Available":  screenshot_name = screenshot(driver, job_id, "Failed to click Submit application")
                                    # else:   screenshot_name = [screenshot_name, screenshot(driver, job_id, "Failed to click Submit application")]
                                    if errored == "nose": raise Exception("Failed to click Submit application 😑")


                        except Exception as e:
                            print_lg("Failed to Easy apply!")
                            # print_lg(e)
                            critical_error_log("Somewhere in Easy Apply process",e)
                            failed_job(job_id, job_link, resume, date_listed, "Problem in Easy Applying", e, application_link, screenshot_name)
                            discard_job()
                            continue
                    else:
                        # Case 2: Apply externally
                        if easy_apply_only: 
                            print_lg("Easy apply failed I guess!")
                            if pagination_element != None: continue
                        try:
                            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Apply") and not(span[contains(@class, "disabled")])]'))).click()
                            windows = driver.window_handles
                            driver.switch_to.window(windows[-1])
                            application_link = driver.current_url
                            print_lg('Got the external application link "{}"'.format(application_link))
                            if close_tabs: driver.close()
                            driver.switch_to.window(linkedIn_tab) 
                        except Exception as e:
                            # print_lg(e)
                            print_lg("Failed to apply!")
                            failed_job(job_id, job_link, resume, date_listed, "Probably didn't find Apply button or unable to switch tabs.", e, application_link, screenshot_name)
                            continue
                    
                    submitted_jobs(job_id, title, company, work_location, work_style, description, experience_required, skills, hr_name, hr_link, resume, reposted, date_listed, date_applied, job_link, application_link, questions_list, connect_request)

                    print_lg(f'Successfully saved "{title} | {company}" job. Job ID: {job_id} info')
                    current_count += 1
                    applied_jobs.add(job_id)

                # Switching to next page
                if pagination_element == None:
                    print_lg("Couldn't find pagination element, probably at the end page of results!")
                    break
                try:
                    pagination_element.find_element(By.XPATH, f"//button[@aria-label='Page {current_page+1}']").click()
                    print_lg(f"\n>-> Now on Page {current_page+1} \n")
                except NoSuchElementException:
                    print_lg(f"Didn't find Page {current_page+1}. Probably at the end page of results!")
                    break

        except Exception as e:
            print_lg("Failed to find Job listings!")
            critical_error_log("In Applier", e)
            # print_lg(e)

        
def run(total_runs):
    print_lg("\n########################################################################################################################\n")
    print_lg(f"Date and Time: {datetime.now()}")
    print_lg(f"Cycle number: {total_runs+1}")
    print_lg(f"Currently looking for jobs posted within '{date_posted}' and sorting them by '{sort_by}'")
    apply_to_jobs(search_terms)
    print_lg("########################################################################################################################\n")
    print_lg("Sleeping for 10 min...")
    sleep(0)
    print_lg("Few more min... Gonna start with in next 5 min...")
    buffer(-3)
    return total_runs + 1



chatGPT_tab = False
linkedIn_tab = False
def main():
    try:
        alert_title = "Error Occurred. Closing Browser!"
        validate_config()
        make_directories([file_name,failed_file_name,logs_folder_path+"/screenshots",default_resume_path,generated_resume_path+"/temp"])
        if not os.path.exists(default_resume_path):   raise Exception('Your default resume "{}" is missing! Please update it\'s folder path in config.py or add a resume with exact name and path (check for spelling mistakes including cases).'.format(default_resume_path))
        
        # Login to LinkedIn
        driver.get("https://www.linkedin.com/login")
        if not is_logged_in_LN(): login_LN()
        global linkedIn_tab
        linkedIn_tab = driver.current_window_handle

        # Login to ChatGPT in a new tab for resume customization
        if use_resume_generator:
            try:
                driver.switch_to.new_window('tab')
                driver.get("https://chat.openai.com/")
                if not is_logged_in_GPT(): login_GPT()
                open_resume_chat()
                global chatGPT_tab
                chatGPT_tab = driver.current_window_handle
            except Exception as e:
                print_lg("Opening OpenAI chatGPT tab failed!")

        # Start applying to jobs
        driver.switch_to.window(linkedIn_tab)
        total_runs = 0
        total_runs = run(total_runs)
        while(run_non_stop):
            if cycle_date_posted:
                date_options = ["Any time", "Past month", "Past week", "Past 24 hours"]
                global date_posted
                date_posted = date_options[date_options.index(date_posted)+1 if date_options.index(date_posted)+1 > len(date_options) else -1] if stop_date_cycle_at_24hr else date_options[0 if date_options.index(date_posted)+1 >= len(date_options) else date_options.index(date_posted)+1]
            if alternate_sortby:
                global sort_by
                sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
                total_runs = run(total_runs)
                sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
            
            total_runs = run(total_runs)
        

    except NoSuchWindowException:   pass
    except Exception as e:
        critical_error_log("In Applier Main", e)
        alert(e,alert_title)
    finally:
        quote = choice([
            "You're one step closer than before.", 
            "All the best with your future interviews.", 
            "Keep up with the progress. You got this.", 
            "If you're tired, learn to take rest but never give up.",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
            "Every job is a self-portrait of the person who does it. Autograph your work with excellence.",
            "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. - Steve Jobs",
            "Opportunities don't happen, you create them. - Chris Grosser",
            "The road to success and the road to failure are almost exactly the same. The difference is perseverance.",
            "Obstacles are those frightful things you see when you take your eyes off your goal. - Henry Ford",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt"
            ])
        msg = f"{quote}\n\n\nBest regards,\nSai Vignesh Golla\nhttps://www.linkedin.com/in/saivigneshgolla/"
        alert(msg, "Exiting..")
        print_lg(msg,"Closing the browser...")
        driver.quit()

main()