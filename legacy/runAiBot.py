'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''


# Imports
import os
import csv
import re
import pyautogui

# Set CSV field size limit to prevent field size errors
csv.field_size_limit(1000000)  # Set to 1MB instead of default 131KB

from random import choice, shuffle, randint
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException, ElementNotInteractableException, WebDriverException

from config.personals import *
from config.questions import *
from config.search import *
from config.secrets import use_AI, username, password, ai_provider
from config.settings import *

from modules.open_chrome import *
from modules.helpers import *
from modules.clickers_and_finders import *
from modules.validator import validate_config
from modules.ai.openaiConnections import ai_create_openai_client, ai_extract_skills, ai_answer_question, ai_close_openai_client
from modules.ai.deepseekConnections import deepseek_create_client, deepseek_extract_skills, deepseek_answer_question
from modules.ai.geminiConnections import gemini_create_client, gemini_extract_skills, gemini_answer_question

from typing import Literal


pyautogui.FAILSAFE = False
# if use_resume_generator:    from resume_generator import is_logged_in_GPT, login_GPT, open_resume_chat, create_custom_resume


#< Global Variables and logics

if run_in_background == True:
    pause_at_failed_question = False
    pause_before_submit = False
    run_non_stop = False

first_name = first_name.strip()
middle_name = middle_name.strip()
last_name = last_name.strip()
full_name = first_name + " " + middle_name + " " + last_name if middle_name else first_name + " " + last_name

useNewResume = True
randomly_answered_questions = set()

tabs_count = 1
easy_applied_count = 0
external_jobs_count = 0
failed_count = 0
skip_count = 0
dailyEasyApplyLimitReached = False

re_experience = re.compile(r'[(]?\s*(\d+)\s*[)]?\s*[-to]*\s*\d*[+]*\s*year[s]?', re.IGNORECASE)

desired_salary_lakhs = str(round(desired_salary / 100000, 2))
desired_salary_monthly = str(round(desired_salary/12, 2))
desired_salary = str(desired_salary)

current_ctc_lakhs = str(round(current_ctc / 100000, 2))
current_ctc_monthly = str(round(current_ctc/12, 2))
current_ctc = str(current_ctc)

notice_period_months = str(notice_period//30)
notice_period_weeks = str(notice_period//7)
notice_period = str(notice_period)

aiClient = None
##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------
about_company_for_ai = None # TODO extract about company for AI
##<

#>


#< Login Functions
def is_logged_in_LN() -> bool:
    '''
    Function to check if user is logged-in in LinkedIn
    * Returns: `True` if user is logged-in or `False` if not
    '''
    if driver.current_url == "https://www.linkedin.com/feed/": return True
    if try_linkText(driver, "Sign in"): return False
    if try_xp(driver, '//button[@type="submit" and contains(text(), "Sign in")]'):  return False
    if try_linkText(driver, "Join now"): return False
    print_lg("Didn't find Sign in link, so assuming user is logged in!")
    return True


def login_LN() -> None:
    '''
    Function to login for LinkedIn
    * Tries to login using given `username` and `password` from `secrets.py`
    * If failed, tries to login using saved LinkedIn profile button if available
    * If both failed, asks user to login manually
    '''
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



def get_applied_job_ids() -> set:
    '''
    Function to get a `set` of applied job's Job IDs
    * Returns a set of Job IDs from existing applied jobs history csv file
    '''
    job_ids = set()
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                job_ids.add(row[0])
    except FileNotFoundError:
        print_lg(f"The CSV file '{file_name}' does not exist.")
    return job_ids



def set_search_location() -> None:
    '''
    Function to set search location
    '''
    if search_location.strip():
        try:
            print_lg(f'Setting search location as: "{search_location.strip()}"')
            search_location_ele = try_xp(driver, ".//input[@aria-label='City, state, or zip code'and not(@disabled)]", False) #  and not(@aria-hidden='true')]")
            text_input(actions, search_location_ele, search_location, "Search Location")
        except ElementNotInteractableException:
            try_xp(driver, ".//label[@class='jobs-search-box__input-icon jobs-search-box__keywords-label']")
            actions.send_keys(Keys.TAB, Keys.TAB).perform()
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            actions.send_keys(search_location.strip()).perform()
            sleep(2)
            actions.send_keys(Keys.ENTER).perform()
            try_xp(driver, ".//button[@aria-label='Cancel']")
        except Exception as e:
            try_xp(driver, ".//button[@aria-label='Cancel']")
            print_lg("Failed to update search location, continuing with default location!", e)


def apply_filters() -> None:
    '''
    Function to apply job search filters
    '''
    set_search_location()

    try:
        recommended_wait = 1 if click_gap < 1 else 0

        wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="All filters"]'))).click()
        buffer(recommended_wait)

        wait_span_click(driver, sort_by)
        wait_span_click(driver, date_posted)
        buffer(recommended_wait)

        multi_sel_noWait(driver, experience_level) 
        multi_sel_noWait(driver, companies, actions)
        if experience_level or companies: buffer(recommended_wait)

        multi_sel_noWait(driver, job_type)
        multi_sel_noWait(driver, on_site)
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

        show_results_button: WebElement = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Apply current filters to show")]')
        show_results_button.click()

        global pause_after_filters
        if pause_after_filters and "Turn off Pause after search" == pyautogui.confirm("These are your configured search results and filter. It is safe to change them while this dialog is open, any changes later could result in errors and skipping this search run.", "Please check your results", ["Turn off Pause after search", "Look's good, Continue"]):
            pause_after_filters = False

    except Exception as e:
        print_lg("Setting the preferences failed!")
        # print_lg(e)



def get_page_info() -> tuple[WebElement | None, int | None]:
    '''
    Function to get pagination element and current page number
    '''
    try:
        pagination_element = try_find_by_classes(driver, ["jobs-search-pagination__pages", "artdeco-pagination", "artdeco-pagination__pages"])
        scroll_to_view(driver, pagination_element)
        current_page = int(pagination_element.find_element(By.XPATH, "//button[contains(@class, 'active')]").text)
    except Exception as e:
        print_lg("Failed to find Pagination element, hence couldn't scroll till end!")
        pagination_element = None
        current_page = None
        print_lg(e)
    return pagination_element, current_page



def get_job_main_details(job: WebElement, blacklisted_companies: set, rejected_jobs: set) -> tuple[str, str, str, str, str, bool]:
    '''
    # Function to get job main details.
    Returns a tuple of (job_id, title, company, work_location, work_style, skip)
    * job_id: Job ID
    * title: Job title
    * company: Company name
    * work_location: Work location of this job
    * work_style: Work style of this job (Remote, On-site, Hybrid)
    * skip: A boolean flag to skip this job
    '''
    job_details_button = job.find_element(By.TAG_NAME, 'a')  # job.find_element(By.CLASS_NAME, "job-card-list__title")  # Problem in India
    scroll_to_view(driver, job_details_button, True)
    job_id = job.get_dom_attribute('data-occludable-job-id')
    title = job_details_button.text
    title = title[:title.find("\n")]
    # company = job.find_element(By.CLASS_NAME, "job-card-container__primary-description").text
    # work_location = job.find_element(By.CLASS_NAME, "job-card-container__metadata-item").text
    other_details = job.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle').text
    index = other_details.find(' · ')
    company = other_details[:index]
    work_location = other_details[index+3:]
    work_style = work_location[work_location.rfind('(')+1:work_location.rfind(')')]
    work_location = work_location[:work_location.rfind('(')].strip()
    
    # Skip if previously rejected due to blacklist or already applied
    skip = False
    if company in blacklisted_companies:
        print_lg(f'Skipping "{title} | {company}" job (Blacklisted Company). Job ID: {job_id}!')
        skip = True
    elif job_id in rejected_jobs: 
        print_lg(f'Skipping previously rejected "{title} | {company}" job. Job ID: {job_id}!')
        skip = True
    try:
        if job.find_element(By.CLASS_NAME, "job-card-container__footer-job-state").text == "Applied":
            skip = True
            print_lg(f'Already applied to "{title} | {company}" job. Job ID: {job_id}!')
    except: pass
    try: 
        if not skip: job_details_button.click()
    except Exception as e:
        print_lg(f'Failed to click "{title} | {company}" job on details button. Job ID: {job_id}!') 
        # print_lg(e)
        discard_job()
        job_details_button.click() # To pass the error outside
    buffer(click_gap)
    return (job_id,title,company,work_location,work_style,skip)


# Function to check for Blacklisted words in About Company
def check_blacklist(rejected_jobs: set, job_id: str, company: str, blacklisted_companies: set) -> tuple[set, set, WebElement] | ValueError:
    jobs_top_card = try_find_by_classes(driver, ["job-details-jobs-unified-top-card__primary-description-container","job-details-jobs-unified-top-card__primary-description","jobs-unified-top-card__primary-description","jobs-details__main-content"])
    about_company_org = find_by_class(driver, "jobs-company__box")
    scroll_to_view(driver, about_company_org)
    about_company_org = about_company_org.text
    about_company = about_company_org.lower()
    skip_checking = False
    for word in about_company_good_words:
        if word.lower() in about_company:
            print_lg(f'Found the word "{word}". So, skipped checking for blacklist words.')
            skip_checking = True
            break
    if not skip_checking:
        for word in about_company_bad_words: 
            if word.lower() in about_company: 
                rejected_jobs.add(job_id)
                blacklisted_companies.add(company)
                raise ValueError(f'\n"{about_company_org}"\n\nContains "{word}".')
    buffer(click_gap)
    scroll_to_view(driver, jobs_top_card)
    return rejected_jobs, blacklisted_companies, jobs_top_card



# Function to extract years of experience required from About Job
def extract_years_of_experience(text: str) -> int:
    # Extract all patterns like '10+ years', '5 years', '3-5 years', etc.
    matches = re.findall(re_experience, text)
    if len(matches) == 0: 
        print_lg(f'\n{text}\n\nCouldn\'t find experience requirement in About the Job!')
        return 0
    return max([int(match) for match in matches if int(match) <= 12])



def get_job_description(
) -> tuple[
    str | Literal['Unknown'],
    int | Literal['Unknown'],
    bool,
    str | None,
    str | None
    ]:
    '''
    # Job Description
    Function to extract job description from About the Job.
    ### Returns:
    - `jobDescription: str | 'Unknown'`
    - `experience_required: int | 'Unknown'`
    - `skip: bool`
    - `skipReason: str | None`
    - `skipMessage: str | None`
    '''
    try:
        ##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------
        jobDescription = "Unknown"
        ##<
        experience_required = "Unknown"
        found_masters = 0
        jobDescription = find_by_class(driver, "jobs-box__html-content").text
        jobDescriptionLow = jobDescription.lower()
        skip = False
        skipReason = None
        skipMessage = None
        for word in bad_words:
            if word.lower() in jobDescriptionLow:
                skipMessage = f'\n{jobDescription}\n\nContains bad word "{word}". Skipping this job!\n'
                skipReason = "Found a Bad Word in About Job"
                skip = True
                break
        if not skip and security_clearance == False and ('polygraph' in jobDescriptionLow or 'clearance' in jobDescriptionLow or 'secret' in jobDescriptionLow):
            skipMessage = f'\n{jobDescription}\n\nFound "Clearance" or "Polygraph". Skipping this job!\n'
            skipReason = "Asking for Security clearance"
            skip = True
        if not skip:
            if did_masters and 'master' in jobDescriptionLow:
                print_lg(f'Found the word "master" in \n{jobDescription}')
                found_masters = 2
            experience_required = extract_years_of_experience(jobDescription)
            if current_experience > -1 and experience_required > current_experience + found_masters:
                skipMessage = f'\n{jobDescription}\n\nExperience required {experience_required} > Current Experience {current_experience + found_masters}. Skipping this job!\n'
                skipReason = "Required experience is high"
                skip = True
    except Exception as e:
        if jobDescription == "Unknown":    print_lg("Unable to extract job description!")
        else:
            experience_required = "Error in extraction"
            print_lg("Unable to extract years of experience required!")
            # print_lg(e)
    finally:
        return jobDescription, experience_required, skip, skipReason, skipMessage
        


# Function to upload resume
def upload_resume(modal: WebElement, resume: str) -> tuple[bool, str]:
    try:
        modal.find_element(By.NAME, "file").send_keys(os.path.abspath(resume))
        return True, os.path.basename(default_resume_path)
    except: return False, "Previous resume"

# Function to answer common questions for Easy Apply
def answer_common_questions(label: str, answer: str) -> str:
    if 'sponsorship' in label or 'visa' in label: answer = require_visa
    return answer


# Function to answer the questions for Easy Apply
def answer_questions(modal: WebElement, questions_list: set, work_location: str, job_description: str | None = None ) -> set:
    # Get all questions from the page
     
    all_questions = modal.find_elements(By.XPATH, ".//div[@data-test-form-element]")
    # all_questions = modal.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-element")
    # all_list_questions = modal.find_elements(By.XPATH, ".//div[@data-test-text-entity-list-form-component]")
    # all_single_line_questions = modal.find_elements(By.XPATH, ".//div[@data-test-single-line-text-form-component]")
    # all_questions = all_questions + all_list_questions + all_single_line_questions

    for Question in all_questions:
        # Check if it's a select Question
        select = try_xp(Question, ".//select", False)
        if select:
            label_org = "Unknown"
            try:
                label = Question.find_element(By.TAG_NAME, "label")
                label_org = label.find_element(By.TAG_NAME, "span").text
            except: pass
            answer = 'Yes'
            label = label_org.lower()
            select = Select(select)
            selected_option = select.first_selected_option.text
            optionsText = []
            options = '"List of phone country codes"'
            if label != "phone country code":
                optionsText = [option.text for option in select.options]
                options = "".join([f' "{option}",' for option in optionsText])
            prev_answer = selected_option
            if overwrite_previous_answers or selected_option == "Select an option":
                ##> ------ WINDY_WINDWARD Email:karthik.sarode23@gmail.com - Added fuzzy logic to answer location based questions ------
                if 'email' in label or 'phone' in label: 
                    answer = prev_answer
                elif 'gender' in label or 'sex' in label: 
                    answer = gender
                elif 'disability' in label: 
                    answer = disability_status
                elif 'proficiency' in label: 
                    answer = 'Professional'
                # Add location handling
                elif any(loc_word in label for loc_word in ['location', 'city', 'state', 'country']):
                    if 'country' in label:
                        answer = country 
                    elif 'state' in label:
                        answer = state
                    elif 'city' in label:
                        answer = current_city if current_city else work_location
                    else:
                        answer = work_location
                else: 
                    answer = answer_common_questions(label,answer)
                try: 
                    select.select_by_visible_text(answer)
                except NoSuchElementException as e:
                    # Define similar phrases for common answers
                    possible_answer_phrases = []
                    if answer == 'Decline':
                        possible_answer_phrases = ["Decline", "not wish", "don't wish", "Prefer not", "not want"]
                    elif 'yes' in answer.lower():
                        possible_answer_phrases = ["Yes", "Agree", "I do", "I have"]
                    elif 'no' in answer.lower():
                        possible_answer_phrases = ["No", "Disagree", "I don't", "I do not"]
                    else:
                        # Try partial matching for any answer
                        possible_answer_phrases = [answer]
                        # Add lowercase and uppercase variants
                        possible_answer_phrases.append(answer.lower())
                        possible_answer_phrases.append(answer.upper())
                        # Try without special characters
                        possible_answer_phrases.append(''.join(c for c in answer if c.isalnum()))
                    ##<
                    foundOption = False
                    for phrase in possible_answer_phrases:
                        for option in optionsText:
                            # Check if phrase is in option or option is in phrase (bidirectional matching)
                            if phrase.lower() in option.lower() or option.lower() in phrase.lower():
                                select.select_by_visible_text(option)
                                answer = option
                                foundOption = True
                                break
                    if not foundOption:
                        #TODO: Use AI to answer the question need to be implemented logic to extract the options for the question
                        print_lg(f'Failed to find an option with text "{answer}" for question labelled "{label_org}", answering randomly!')
                        select.select_by_index(randint(1, len(select.options)-1))
                        answer = select.first_selected_option.text
                        randomly_answered_questions.add((f'{label_org} [ {options} ]',"select"))
            questions_list.add((f'{label_org} [ {options} ]', answer, "select", prev_answer))
            continue
        
        # Check if it's a radio Question
        radio = try_xp(Question, './/fieldset[@data-test-form-builder-radio-button-form-component="true"]', False)
        if radio:
            prev_answer = None
            label = try_xp(radio, './/span[@data-test-form-builder-radio-button-form-component__title]', False)
            try: label = find_by_class(label, "visually-hidden", 2.0)
            except: pass
            label_org = label.text if label else "Unknown"
            answer = 'Yes'
            label = label_org.lower()

            label_org += ' [ '
            options = radio.find_elements(By.TAG_NAME, 'input')
            options_labels = []
            
            for option in options:
                id = option.get_attribute("id")
                option_label = try_xp(radio, f'.//label[@for="{id}"]', False)
                options_labels.append( f'"{option_label.text if option_label else "Unknown"}"<{option.get_attribute("value")}>' ) # Saving option as "label <value>"
                if option.is_selected(): prev_answer = options_labels[-1]
                label_org += f' {options_labels[-1]},'

            if overwrite_previous_answers or prev_answer is None:
                if 'citizenship' in label or 'employment eligibility' in label: answer = us_citizenship
                elif 'veteran' in label or 'protected' in label: answer = veteran_status
                elif 'disability' in label or 'handicapped' in label: 
                    answer = disability_status
                else: answer = answer_common_questions(label,answer)
                foundOption = try_xp(radio, f".//label[normalize-space()='{answer}']", False)
                if foundOption: 
                    actions.move_to_element(foundOption).click().perform()
                else:    
                    possible_answer_phrases = ["Decline", "not wish", "don't wish", "Prefer not", "not want"] if answer == 'Decline' else [answer]
                    ele = options[0]
                    answer = options_labels[0]
                    for phrase in possible_answer_phrases:
                        for i, option_label in enumerate(options_labels):
                            if phrase in option_label:
                                foundOption = options[i]
                                ele = foundOption
                                answer = f'Decline ({option_label})' if len(possible_answer_phrases) > 1 else option_label
                                break
                        if foundOption: break
                    # if answer == 'Decline':
                    #     answer = options_labels[0]
                    #     for phrase in ["Prefer not", "not want", "not wish"]:
                    #         foundOption = try_xp(radio, f".//label[normalize-space()='{phrase}']", False)
                    #         if foundOption:
                    #             answer = f'Decline ({phrase})'
                    #             ele = foundOption
                    #             break
                    actions.move_to_element(ele).click().perform()
                    if not foundOption: randomly_answered_questions.add((f'{label_org} ]',"radio"))
            else: answer = prev_answer
            questions_list.add((label_org+" ]", answer, "radio", prev_answer))
            continue
        
        # Check if it's a text question
        text = try_xp(Question, ".//input[@type='text']", False)
        if text: 
            do_actions = False
            label = try_xp(Question, ".//label[@for]", False)
            try: label = label.find_element(By.CLASS_NAME,'visually-hidden')
            except: pass
            label_org = label.text if label else "Unknown"
            answer = "" # years_of_experience
            label = label_org.lower()

            prev_answer = text.get_attribute("value")
            if not prev_answer or overwrite_previous_answers:
                if 'experience' in label or 'years' in label: answer = years_of_experience
                elif 'phone' in label or 'mobile' in label: answer = phone_number
                elif 'street' in label: answer = street
                elif 'city' in label or 'location' in label or 'address' in label:
                    answer = current_city if current_city else work_location
                    do_actions = True
                elif 'signature' in label: answer = full_name # 'signature' in label or 'legal name' in label or 'your name' in label or 'full name' in label: answer = full_name     # What if question is 'name of the city or university you attend, name of referral etc?'
                elif 'name' in label:
                    if 'full' in label: answer = full_name
                    elif 'first' in label and 'last' not in label: answer = first_name
                    elif 'middle' in label and 'last' not in label: answer = middle_name
                    elif 'last' in label and 'first' not in label: answer = last_name
                    elif 'employer' in label: answer = recent_employer
                    else: answer = full_name
                elif 'notice' in label:
                    if 'month' in label:
                        answer = notice_period_months
                    elif 'week' in label:
                        answer = notice_period_weeks
                    else: answer = notice_period
                elif 'salary' in label or 'compensation' in label or 'ctc' in label or 'pay' in label: 
                    if 'current' in label or 'present' in label:
                        if 'month' in label:
                            answer = current_ctc_monthly
                        elif 'lakh' in label:
                            answer = current_ctc_lakhs
                        else:
                            answer = current_ctc
                    else:
                        if 'month' in label:
                            answer = desired_salary_monthly
                        elif 'lakh' in label:
                            answer = desired_salary_lakhs
                        else:
                            answer = desired_salary
                elif 'linkedin' in label: answer = linkedIn
                elif 'website' in label or 'blog' in label or 'portfolio' in label or 'link' in label: answer = website
                elif 'scale of 1-10' in label: answer = confidence_level
                elif 'headline' in label: answer = linkedin_headline
                elif ('hear' in label or 'come across' in label) and 'this' in label and ('job' in label or 'position' in label): answer = "https://github.com/GodsScion/Auto_job_applier_linkedIn"
                elif 'state' in label or 'province' in label: answer = state
                elif 'zip' in label or 'postal' in label or 'code' in label: answer = zipcode
                elif 'country' in label: answer = country
                else: answer = answer_common_questions(label,answer)
                ##> ------ Yang Li : MARKYangL - Feature ------
                if answer == "":
                    if use_AI and aiClient:
                        try:
                            if ai_provider.lower() == "openai":
                                answer = ai_answer_question(aiClient, label_org, question_type="text", job_description=job_description, user_information_all=user_information_all)
                            elif ai_provider.lower() == "deepseek":
                                answer = deepseek_answer_question(aiClient, label_org, options=None, question_type="text", job_description=job_description, about_company=None, user_information_all=user_information_all)
                            elif ai_provider.lower() == "gemini":
                                answer = gemini_answer_question(aiClient, label_org, options=None, question_type="text", job_description=job_description, about_company=None, user_information_all=user_information_all)
                            else:
                                randomly_answered_questions.add((label_org, "text"))
                                answer = years_of_experience
                            if answer and isinstance(answer, str) and len(answer) > 0:
                                print_lg(f'AI Answered received for question "{label_org}" \nhere is answer: "{answer}"')
                            else:
                                randomly_answered_questions.add((label_org, "text"))
                                answer = years_of_experience
                        except Exception as e:
                            print_lg("Failed to get AI answer!", e)
                            randomly_answered_questions.add((label_org, "text"))
                            answer = years_of_experience
                    else:
                        randomly_answered_questions.add((label_org, "text"))
                        answer = years_of_experience
                ##<
                text.clear()
                text.send_keys(answer)
                if do_actions:
                    sleep(2)
                    actions.send_keys(Keys.ARROW_DOWN)
                    actions.send_keys(Keys.ENTER).perform()
            questions_list.add((label, text.get_attribute("value"), "text", prev_answer))
            continue

        # Check if it's a textarea question
        text_area = try_xp(Question, ".//textarea", False)
        if text_area:
            label = try_xp(Question, ".//label[@for]", False)
            label_org = label.text if label else "Unknown"
            label = label_org.lower()
            answer = ""
            prev_answer = text_area.get_attribute("value")
            if not prev_answer or overwrite_previous_answers:
                if 'summary' in label: answer = linkedin_summary
                elif 'cover' in label: answer = cover_letter
                if answer == "":
                ##> ------ Yang Li : MARKYangL - Feature ------
                    if use_AI and aiClient:
                        try:
                            if ai_provider.lower() == "openai":
                                answer = ai_answer_question(aiClient, label_org, question_type="textarea", job_description=job_description, user_information_all=user_information_all)
                            elif ai_provider.lower() == "deepseek":
                                answer = deepseek_answer_question(aiClient, label_org, options=None, question_type="textarea", job_description=job_description, about_company=None, user_information_all=user_information_all)
                            elif ai_provider.lower() == "gemini":
                                answer = gemini_answer_question(aiClient, label_org, options=None, question_type="textarea", job_description=job_description, about_company=None, user_information_all=user_information_all)
                            else:
                                randomly_answered_questions.add((label_org, "textarea"))
                                answer = ""
                            if answer and isinstance(answer, str) and len(answer) > 0:
                                print_lg(f'AI Answered received for question "{label_org}" \nhere is answer: "{answer}"')
                            else:
                                randomly_answered_questions.add((label_org, "textarea"))
                                answer = ""
                        except Exception as e:
                            print_lg("Failed to get AI answer!", e)
                            randomly_answered_questions.add((label_org, "textarea"))
                            answer = ""
                    else:
                        randomly_answered_questions.add((label_org, "textarea"))
            text_area.clear()
            text_area.send_keys(answer)
            if do_actions:
                    sleep(2)
                    actions.send_keys(Keys.ARROW_DOWN)
                    actions.send_keys(Keys.ENTER).perform()
            questions_list.add((label, text_area.get_attribute("value"), "textarea", prev_answer))
            ##<
            continue

        # Check if it's a checkbox question
        checkbox = try_xp(Question, ".//input[@type='checkbox']", False)
        if checkbox:
            label = try_xp(Question, ".//span[@class='visually-hidden']", False)
            label_org = label.text if label else "Unknown"
            label = label_org.lower()
            answer = try_xp(Question, ".//label[@for]", False)  # Sometimes multiple checkboxes are given for 1 question, Not accounted for that yet
            answer = answer.text if answer else "Unknown"
            prev_answer = checkbox.is_selected()
            checked = prev_answer
            if not prev_answer:
                try:
                    actions.move_to_element(checkbox).click().perform()
                    checked = True
                except Exception as e: 
                    print_lg("Checkbox click failed!", e)
                    pass
            questions_list.add((f'{label} ([X] {answer})', checked, "checkbox", prev_answer))
            continue


    # Select todays date
    try_xp(driver, "//button[contains(@aria-label, 'This is today')]")

    # Collect important skills
    # if 'do you have' in label and 'experience' in label and ' in ' in label -> Get word (skill) after ' in ' from label
    # if 'how many years of experience do you have in ' in label -> Get word (skill) after ' in '

    return questions_list




def external_apply(pagination_element: WebElement, job_id: str, job_link: str, resume: str, date_listed, application_link: str, screenshot_name: str) -> tuple[bool, str, int]:
    '''
    Function to open new tab and save external job application links
    '''
    global tabs_count, dailyEasyApplyLimitReached
    if easy_apply_only:
        try:
            if "exceeded the daily application limit" in driver.find_element(By.CLASS_NAME, "artdeco-inline-feedback__message").text: dailyEasyApplyLimitReached = True
        except: pass
        print_lg("Easy apply failed I guess!")
        if pagination_element != None: return True, application_link, tabs_count
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3')]"))).click() # './/button[contains(span, "Apply") and not(span[contains(@class, "disabled")])]'
        wait_span_click(driver, "Continue", 1, True, False)
        windows = driver.window_handles
        tabs_count = len(windows)
        driver.switch_to.window(windows[-1])
        application_link = driver.current_url
        print_lg('Got the external application link "{}"'.format(application_link))
        if close_tabs and driver.current_window_handle != linkedIn_tab: driver.close()
        driver.switch_to.window(linkedIn_tab)
        return False, application_link, tabs_count
    except Exception as e:
        # print_lg(e)
        print_lg("Failed to apply!")
        failed_job(job_id, job_link, resume, date_listed, "Probably didn't find Apply button or unable to switch tabs.", e, application_link, screenshot_name)
        global failed_count
        failed_count += 1
        return True, application_link, tabs_count



def follow_company(modal: WebDriver = driver) -> None:
    '''
    Function to follow or un-follow easy applied companies based om `follow_companies`
    '''
    try:
        follow_checkbox_input = try_xp(modal, ".//input[@id='follow-company-checkbox' and @type='checkbox']", False)
        if follow_checkbox_input and follow_checkbox_input.is_selected() != follow_companies:
            try_xp(modal, ".//label[@for='follow-company-checkbox']")
    except Exception as e:
        print_lg("Failed to update follow companies checkbox!", e)
    


#< Failed attempts logging
def failed_job(job_id: str, job_link: str, resume: str, date_listed, error: str, exception: Exception, application_link: str, screenshot_name: str) -> None:
    '''
    Function to update failed jobs list in excel
    '''
    try:
        with open(failed_file_name, 'a', newline='', encoding='utf-8') as file:
            fieldnames = ['Job ID', 'Job Link', 'Resume Tried', 'Date listed', 'Date Tried', 'Assumed Reason', 'Stack Trace', 'External Job link', 'Screenshot Name']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0: writer.writeheader()
            writer.writerow({'Job ID':truncate_for_csv(job_id), 'Job Link':truncate_for_csv(job_link), 'Resume Tried':truncate_for_csv(resume), 'Date listed':truncate_for_csv(date_listed), 'Date Tried':datetime.now(), 'Assumed Reason':truncate_for_csv(error), 'Stack Trace':truncate_for_csv(exception), 'External Job link':truncate_for_csv(application_link), 'Screenshot Name':truncate_for_csv(screenshot_name)})
            file.close()
    except Exception as e:
        print_lg("Failed to update failed jobs list!", e)
        pyautogui.alert("Failed to update the excel of failed jobs!\nProbably because of 1 of the following reasons:\n1. The file is currently open or in use by another program\n2. Permission denied to write to the file\n3. Failed to find the file", "Failed Logging")


def screenshot(driver: WebDriver, job_id: str, failedAt: str) -> str:
    '''
    Function to to take screenshot for debugging
    - Returns screenshot name as String
    '''
    screenshot_name = "{} - {} - {}.png".format( job_id, failedAt, str(datetime.now()) )
    path = logs_folder_path+"/screenshots/"+screenshot_name.replace(":",".")
    # special_chars = {'*', '"', '\\', '<', '>', ':', '|', '?'}
    # for char in special_chars:  path = path.replace(char, '-')
    driver.save_screenshot(path.replace("//","/"))
    return screenshot_name
#>



def submitted_jobs(job_id: str, title: str, company: str, work_location: str, work_style: str, description: str, experience_required: int | Literal['Unknown', 'Error in extraction'], 
                   skills: list[str] | Literal['In Development'], hr_name: str | Literal['Unknown'], hr_link: str | Literal['Unknown'], resume: str, 
                   reposted: bool, date_listed: datetime | Literal['Unknown'], date_applied:  datetime | Literal['Pending'], job_link: str, application_link: str, 
                   questions_list: set | None, connect_request: Literal['In Development']) -> None:
    '''
    Function to create or update the Applied jobs CSV file, once the application is submitted successfully
    '''
    try:
        with open(file_name, mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['Job ID', 'Title', 'Company', 'Work Location', 'Work Style', 'About Job', 'Experience required', 'Skills required', 'HR Name', 'HR Link', 'Resume', 'Re-posted', 'Date Posted', 'Date Applied', 'Job Link', 'External Job link', 'Questions Found', 'Connect Request']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if csv_file.tell() == 0: writer.writeheader()
            writer.writerow({'Job ID':truncate_for_csv(job_id), 'Title':truncate_for_csv(title), 'Company':truncate_for_csv(company), 'Work Location':truncate_for_csv(work_location), 'Work Style':truncate_for_csv(work_style), 
                            'About Job':truncate_for_csv(description), 'Experience required': truncate_for_csv(experience_required), 'Skills required':truncate_for_csv(skills), 
                                'HR Name':truncate_for_csv(hr_name), 'HR Link':truncate_for_csv(hr_link), 'Resume':truncate_for_csv(resume), 'Re-posted':truncate_for_csv(reposted), 
                                'Date Posted':truncate_for_csv(date_listed), 'Date Applied':truncate_for_csv(date_applied), 'Job Link':truncate_for_csv(job_link), 
                                'External Job link':truncate_for_csv(application_link), 'Questions Found':truncate_for_csv(questions_list), 'Connect Request':truncate_for_csv(connect_request)})
        csv_file.close()
    except Exception as e:
        print_lg("Failed to update submitted jobs list!", e)
        pyautogui.alert("Failed to update the excel of applied jobs!\nProbably because of 1 of the following reasons:\n1. The file is currently open or in use by another program\n2. Permission denied to write to the file\n3. Failed to find the file", "Failed Logging")



# Function to discard the job application
def discard_job() -> None:
    actions.send_keys(Keys.ESCAPE).perform()
    wait_span_click(driver, 'Discard', 2)






# Function to apply to jobs
def apply_to_jobs(search_terms: list[str]) -> None:
    applied_jobs = get_applied_job_ids()
    rejected_jobs = set()
    blacklisted_companies = set()
    global current_city, failed_count, skip_count, easy_applied_count, external_jobs_count, tabs_count, pause_before_submit, pause_at_failed_question, useNewResume
    current_city = current_city.strip()

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
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[@data-occludable-job-id]")))

                pagination_element, current_page = get_page_info()

                # Find all job listings in current page
                buffer(3)
                job_listings = driver.find_elements(By.XPATH, "//li[@data-occludable-job-id]")  

            
                for job in job_listings:
                    if keep_screen_awake: pyautogui.press('shiftright')
                    if current_count >= switch_number: break
                    print_lg("\n-@-\n")

                    job_id,title,company,work_location,work_style,skip = get_job_main_details(job, blacklisted_companies, rejected_jobs)
                    
                    if skip: continue
                    # Redundant fail safe check for applied jobs!
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
                    skills = "Needs an AI" # Still in development
                    resume = "Pending"
                    reposted = False
                    questions_list = None
                    screenshot_name = "Not Available"

                    try:
                        rejected_jobs, blacklisted_companies, jobs_top_card = check_blacklist(rejected_jobs,job_id,company,blacklisted_companies)
                    except ValueError as e:
                        print_lg(e, 'Skipping this job!\n')
                        failed_job(job_id, job_link, resume, date_listed, "Found Blacklisted words in About Company", e, "Skipped", screenshot_name)
                        skip_count += 1
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
                        time_posted_text = jobs_top_card.find_element(By.XPATH, './/span[contains(normalize-space(), " ago")]').text
                        print("Time Posted: " + time_posted_text)
                        if time_posted_text.__contains__("Reposted"):
                            reposted = True
                            time_posted_text = time_posted_text.replace("Reposted", "")
                        date_listed = calculate_date_posted(time_posted_text.strip())
                    except Exception as e:
                        print_lg("Failed to calculate the date posted!",e)


                    description, experience_required, skip, reason, message = get_job_description()
                    if skip:
                        print_lg(message)
                        failed_job(job_id, job_link, resume, date_listed, reason, message, "Skipped", screenshot_name)
                        rejected_jobs.add(job_id)
                        skip_count += 1
                        continue

                    
                    if use_AI and description != "Unknown":
                        ##> ------ Yang Li : MARKYangL - Feature ------
                        try:
                            if ai_provider.lower() == "openai":
                                skills = ai_extract_skills(aiClient, description)
                            elif ai_provider.lower() == "deepseek":
                                skills = deepseek_extract_skills(aiClient, description)
                            elif ai_provider.lower() == "gemini":
                                skills = gemini_extract_skills(aiClient, description)
                            else:
                                skills = "In Development"
                            print_lg(f"Extracted skills using {ai_provider} AI")
                        except Exception as e:
                            print_lg("Failed to extract skills:", e)
                            skills = "Error extracting skills"
                        ##<

                    uploaded = False
                    # Case 1: Easy Apply Button
                    if try_xp(driver, ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3') and contains(@aria-label, 'Easy')]"):
                        try: 
                            try:
                                errored = ""
                                modal = find_by_class(driver, "jobs-easy-apply-modal")
                                wait_span_click(modal, "Next", 1)
                                # if description != "Unknown":
                                #     resume = create_custom_resume(description)
                                resume = "Previous resume"
                                next_button = True
                                questions_list = set()
                                next_counter = 0
                                while next_button:
                                    next_counter += 1
                                    if next_counter >= 15: 
                                        if pause_at_failed_question:
                                            screenshot(driver, job_id, "Needed manual intervention for failed question")
                                            pyautogui.alert("Couldn't answer one or more questions.\nPlease click \"Continue\" once done.\nDO NOT CLICK Back, Next or Review button in LinkedIn.\n\n\n\n\nYou can turn off \"Pause at failed question\" setting in config.py", "Help Needed", "Continue")
                                            next_counter = 1
                                            continue
                                        if questions_list: print_lg("Stuck for one or some of the following questions...", questions_list)
                                        screenshot_name = screenshot(driver, job_id, "Failed at questions")
                                        errored = "stuck"
                                        raise Exception("Seems like stuck in a continuous loop of next, probably because of new questions.")
                                    questions_list = answer_questions(modal, questions_list, work_location, job_description=description)
                                    if useNewResume and not uploaded: uploaded, resume = upload_resume(modal, default_resume_path)
                                    try: next_button = modal.find_element(By.XPATH, './/span[normalize-space(.)="Review"]') 
                                    except NoSuchElementException:  next_button = modal.find_element(By.XPATH, './/button[contains(span, "Next")]')
                                    try: next_button.click()
                                    except ElementClickInterceptedException: break    # Happens when it tries to click Next button in About Company photos section
                                    buffer(click_gap)

                            except NoSuchElementException: errored = "nose"
                            finally:
                                if questions_list and errored != "stuck": 
                                    print_lg("Answered the following questions...", questions_list)
                                    print("\n\n" + "\n".join(str(question) for question in questions_list) + "\n\n")
                                wait_span_click(driver, "Review", 1, scrollTop=True)
                                cur_pause_before_submit = pause_before_submit
                                if errored != "stuck" and cur_pause_before_submit:
                                    decision = pyautogui.confirm('1. Please verify your information.\n2. If you edited something, please return to this final screen.\n3. DO NOT CLICK "Submit Application".\n\n\n\n\nYou can turn off "Pause before submit" setting in config.py\nTo TEMPORARILY disable pausing, click "Disable Pause"', "Confirm your information",["Disable Pause", "Discard Application", "Submit Application"])
                                    if decision == "Discard Application": raise Exception("Job application discarded by user!")
                                    pause_before_submit = False if "Disable Pause" == decision else True
                                    # try_xp(modal, ".//span[normalize-space(.)='Review']")
                                follow_company(modal)
                                if wait_span_click(driver, "Submit application", 2, scrollTop=True): 
                                    date_applied = datetime.now()
                                    if not wait_span_click(driver, "Done", 2): actions.send_keys(Keys.ESCAPE).perform()
                                elif errored != "stuck" and cur_pause_before_submit and "Yes" in pyautogui.confirm("You submitted the application, didn't you 😒?", "Failed to find Submit Application!", ["Yes", "No"]):
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
                            failed_count += 1
                            discard_job()
                            continue
                    else:
                        # Case 2: Apply externally
                        skip, application_link, tabs_count = external_apply(pagination_element, job_id, job_link, resume, date_listed, application_link, screenshot_name)
                        if dailyEasyApplyLimitReached:
                            print_lg("\n###############  Daily application limit for Easy Apply is reached!  ###############\n")
                            return
                        if skip: continue

                    submitted_jobs(job_id, title, company, work_location, work_style, description, experience_required, skills, hr_name, hr_link, resume, reposted, date_listed, date_applied, job_link, application_link, questions_list, connect_request)
                    if uploaded:   useNewResume = False

                    print_lg(f'Successfully saved "{title} | {company}" job. Job ID: {job_id} info')
                    current_count += 1
                    if application_link == "Easy Applied": easy_applied_count += 1
                    else:   external_jobs_count += 1
                    applied_jobs.add(job_id)



                # Switching to next page
                if pagination_element == None:
                    print_lg("Couldn't find pagination element, probably at the end page of results!")
                    break
                try:
                    pagination_element.find_element(By.XPATH, f"//button[@aria-label='Page {current_page+1}']").click()
                    print_lg(f"\n>-> Now on Page {current_page+1} \n")
                except NoSuchElementException:
                    print_lg(f"\n>-> Didn't find Page {current_page+1}. Probably at the end page of results!\n")
                    break

        except (NoSuchWindowException, WebDriverException) as e:
            print_lg("Browser window closed or session is invalid. Ending application process.", e)
            raise e # Re-raise to be caught by main
        except Exception as e:
            print_lg("Failed to find Job listings!")
            critical_error_log("In Applier", e)
            try:
                print_lg(driver.page_source, pretty=True)
            except Exception as page_source_error:
                print_lg(f"Failed to get page source, browser might have crashed. {page_source_error}")
            # print_lg(e)

        
def run(total_runs: int) -> int:
    if dailyEasyApplyLimitReached:
        return total_runs
    print_lg("\n########################################################################################################################\n")
    print_lg(f"Date and Time: {datetime.now()}")
    print_lg(f"Cycle number: {total_runs}")
    print_lg(f"Currently looking for jobs posted within '{date_posted}' and sorting them by '{sort_by}'")
    apply_to_jobs(search_terms)
    print_lg("########################################################################################################################\n")
    if not dailyEasyApplyLimitReached:
        print_lg("Sleeping for 10 min...")
        sleep(300)
        print_lg("Few more min... Gonna start with in next 5 min...")
        sleep(300)
    buffer(3)
    return total_runs + 1



chatGPT_tab = False
linkedIn_tab = False

def main() -> None:
    try:
        global linkedIn_tab, tabs_count, useNewResume, aiClient
        alert_title = "Error Occurred. Closing Browser!"
        total_runs = 1        
        validate_config()
        
        if not os.path.exists(default_resume_path):
            pyautogui.alert(text='Your default resume "{}" is missing! Please update it\'s folder path "default_resume_path" in config.py\n\nOR\n\nAdd a resume with exact name and path (check for spelling mistakes including cases).\n\n\nFor now the bot will continue using your previous upload from LinkedIn!'.format(default_resume_path), title="Missing Resume", button="OK")
            useNewResume = False
        
        # Login to LinkedIn
        tabs_count = len(driver.window_handles)
        driver.get("https://www.linkedin.com/login")
        if not is_logged_in_LN(): login_LN()
        
        linkedIn_tab = driver.current_window_handle

        # # Login to ChatGPT in a new tab for resume customization
        # if use_resume_generator:
        #     try:
        #         driver.switch_to.new_window('tab')
        #         driver.get("https://chat.openai.com/")
        #         if not is_logged_in_GPT(): login_GPT()
        #         open_resume_chat()
        #         global chatGPT_tab
        #         chatGPT_tab = driver.current_window_handle
        #     except Exception as e:
        #         print_lg("Opening OpenAI chatGPT tab failed!")
        if use_AI:
            if ai_provider == "openai":
                aiClient = ai_create_openai_client()
            ##> ------ Yang Li : MARKYangL - Feature ------
            # Create DeepSeek client
            elif ai_provider == "deepseek":
                aiClient = deepseek_create_client()
            elif ai_provider == "gemini":
                aiClient = gemini_create_client()
            ##<

            try:
                about_company_for_ai = " ".join([word for word in (first_name+" "+last_name).split() if len(word) > 3])
                print_lg(f"Extracted about company info for AI: '{about_company_for_ai}'")
            except Exception as e:
                print_lg("Failed to extract about company info!", e)
        
        # Start applying to jobs
        driver.switch_to.window(linkedIn_tab)
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
            if dailyEasyApplyLimitReached:
                break
        

    except (NoSuchWindowException, WebDriverException) as e:
        print_lg("Browser window closed or session is invalid. Exiting.", e)
    except Exception as e:
        critical_error_log("In Applier Main", e)
        pyautogui.alert(e,alert_title)
    finally:
        print_lg("\n\nTotal runs:                     {}".format(total_runs))
        print_lg("Jobs Easy Applied:              {}".format(easy_applied_count))
        print_lg("External job links collected:   {}".format(external_jobs_count))
        print_lg("                              ----------")
        print_lg("Total applied or collected:     {}".format(easy_applied_count + external_jobs_count))
        print_lg("\nFailed jobs:                    {}".format(failed_count))
        print_lg("Irrelevant jobs skipped:        {}\n".format(skip_count))
        if randomly_answered_questions: print_lg("\n\nQuestions randomly answered:\n  {}  \n\n".format(";\n".join(str(question) for question in randomly_answered_questions)))
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
        msg = f"\n{quote}\n\n\nBest regards,\nSai Vignesh Golla\nhttps://www.linkedin.com/in/saivigneshgolla/\n\n"
        pyautogui.alert(msg, "Exiting..")
        print_lg(msg,"Closing the browser...")
        if tabs_count >= 10:
            msg = "NOTE: IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM!\n\nOr it's highly likely that application will just open browser and not do anything next time!" 
            pyautogui.alert(msg,"Info")
            print_lg("\n"+msg)
        ##> ------ Yang Li : MARKYangL - Feature ------
        if use_AI and aiClient:
            try:
                if ai_provider.lower() == "openai":
                    ai_close_openai_client(aiClient)
                elif ai_provider.lower() == "deepseek":
                    ai_close_openai_client(aiClient)
                elif ai_provider.lower() == "gemini":
                    pass # Gemini client does not need to be closed
                print_lg(f"Closed {ai_provider} AI client.")
            except Exception as e:
                print_lg("Failed to close AI client:", e)
        ##<
        try:
            if driver:
                driver.quit()
        except WebDriverException as e:
            print_lg("Browser already closed.", e)
        except Exception as e: 
            critical_error_log("When quitting...", e)


if __name__ == "__main__":
    main()
