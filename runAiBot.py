'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (c) 2024-2026 Sai Vignesh Golla

License:    MIT License
            https://opensource.org/license/mit
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''


# Imports
import os
import sys
import csv
import re
import time
import pyautogui

# Raise the CSV field-size cap so very long job descriptions don't trip the writer.
csv.field_size_limit(1000000)

from random import choice, shuffle
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

if use_AI:
    from modules.ai.connections import create_ai_client, extract_skills, answer_question, close_ai_client

from typing import Literal


pyautogui.FAILSAFE = False
# if use_resume_generator:    from resume_generator import is_logged_in_GPT, login_GPT, open_resume_chat, create_custom_resume


#< Global Variables and logics

if run_in_background == True:
    run_non_stop = False

# pyautogui's alert/confirm are blocking Tk modals. Nobody can click them in a headless
# run, nor when app.py launches this through Popen with stdout redirected to a log file,
# so the process hangs forever and reads as "the bot does nothing". Work that out once
# and degrade every dialog in this file to a log line.
interactive_session = not run_in_background and bool(getattr(sys.stdout, "isatty", lambda: False)())
if not interactive_session:
    pause_at_failed_question = False
    pause_before_submit = False
    pause_after_filters = False
    def _suppressed_dialog(text: str = "", title: str = "", *args, **kwargs) -> None:
        print_lg(f'[Dialog suppressed, non-interactive run] {title}: {text}')
        return None
    pyautogui.alert = _suppressed_dialog
    pyautogui.confirm = _suppressed_dialog

first_name = first_name.strip()
middle_name = middle_name.strip()
last_name = last_name.strip()
full_name = first_name + " " + middle_name + " " + last_name if middle_name else first_name + " " + last_name

useNewResume = True
randomly_answered_questions = set()
# Questions the LAST `answer_questions` pass could not answer at all - reset every pass.
# Two identical passes in a row means the form can never advance on its own.
unanswered_questions = set()

class StoppedBeforeSubmit(Exception):
    '''
    Raised when `stop_before_submit` deliberately halts a fully-filled application at the
    Review step. Nothing failed - the bot did exactly what it was told - so this is counted
    as a skip, not a failure, and must not be logged to the failed-applications CSV.
    '''


class UnansweredQuestions(Exception):
    '''
    Raised when required questions have no answer in `config/questions.py`. The job is
    skipped, not failed - there is nothing broken to retry, the user has to add answers.
    '''

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
about_company_for_ai = None  # filled in later, once we're processing a specific job

# Dry run: fill everything in, reach the Review step, then discard instead of submitting.
# Belongs in config/settings.py; read defensively so an older config keeps working.
stop_before_submit = globals().get("stop_before_submit", False)

# "Are you legally authorized to work here?" is a different question from "do you need
# sponsorship?". Belongs in config/questions.py; read defensively so an older config keeps
# working instead of dying with a NameError on the first Easy Apply dropdown.
legally_authorized = globals().get("legally_authorized", "Yes")

#>


#< Login Functions
# The login page is React now: no <form>, no button[type=submit], empty name attributes and
# ids that are regenerated useId() values. Visible text is the only stable handle left, and it
# has to be an EXACT match - "Sign in with Apple" sits above the real button in the DOM and a
# contains() would pick that one.
sign_in_button_xpath = '//button[normalize-space(.)="Sign in"]'
# The same rewrite removed id="username" / id="password" and name="session_key". `type` is all
# that is left, and the page renders a hidden duplicate of both fields - hence first-displayed.
login_email_css = "input[type='email']"
login_password_css = "input[type='password']"


def fill_visible_input(by: str, value: str, text: str, time: float = 5.0) -> None:
    '''
    Types `text` into the first *displayed* element matching the locator.
    LinkedIn renders hidden 0x0 duplicates of the login fields and `find_element` returns
    the hidden one first, so anything typed into it goes nowhere.
    '''
    field = WebDriverWait(driver, time).until(
        lambda d: pick_first_displayed(d.find_elements(by, value)))
    field.clear()
    human_type(field, text)


def is_logged_in_LN() -> bool:
    '''
    Function to check if user is logged-in in LinkedIn
    * Returns: `True` if user is logged-in or `False` if not
    '''
    # The feed URL now carries query params (?trk=...), so match a prefix, not the whole URL.
    if driver.current_url.startswith("https://www.linkedin.com/feed"): return True
    if try_linkText(driver, "Sign in"): return False
    # click=False: this is a check, it must not press Sign in as a side effect.
    if try_xp(driver, sign_in_button_xpath, False):  return False
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
    if username == "username@example.com" and password == "example_password":
        pyautogui.alert("User did not configure username and password in secrets.py, hence can't login automatically! Please login manually!", "Login Manually","Okay")
        print_lg("User did not configure username and password in secrets.py, hence can't login automatically! Please login manually!")
        manual_login_retry(is_logged_in_LN, 2)
        return
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            fill_visible_input(By.CSS_SELECTOR, login_email_css, username)
        except Exception as e:
            print_lg("Couldn't find username field.")
            print_lg(e)
        try:
            fill_visible_input(By.CSS_SELECTOR, login_password_css, password)
        except Exception as e:
            print_lg("Couldn't find password field.")
            print_lg(e)
        # Find the login submit button and click it. Only one of the duplicated "Sign in"
        # buttons is on screen, so this has to click the displayed one.
        if not wait_xp_click(driver, sign_in_button_xpath):
            raise NoSuchElementException("No visible Sign in button on the login page")
    except Exception as e1:
        try:
            profile_button = find_by_class(driver, "profile__details")
            profile_button.click()
        except Exception as e2:
            print_lg(e1, e2)
            print_lg("Couldn't Login!")

    try:
        # Wait until we land on the feed. That URL now carries query params, so match a prefix.
        wait.until(EC.url_contains("linkedin.com/feed"))
        return print_lg("Login successful!")
    except Exception as e:
        print_lg("Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!")
        print_lg(e)
        manual_login_retry(is_logged_in_LN, 2)
#>



def get_applied_job_ids() -> set[str]:
    '''
    Function to get a `set` of applied job's Job IDs
    * Returns a set of Job IDs from existing applied jobs history csv file
    '''
    job_ids: set[str] = set()
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
            human_type(actions, search_location.strip())
            sleep(2)
            actions.send_keys(Keys.ENTER).perform()
            try_xp(driver, ".//button[@aria-label='Cancel']")
        except Exception as e:
            try_xp(driver, ".//button[@aria-label='Cancel']")
            print_lg("Failed to update search location, continuing with default location!", e)


def recommended_filter_wait(gap: int) -> int:
    '''Pause between filter sections; only skipped when the user asked for no click gap at all.'''
    return 0 if gap < 1 else 1


def apply_filters() -> None:
    '''
    Function to apply job search filters
    '''
    set_search_location()

    try:
        recommended_wait = recommended_filter_wait(click_gap)

        # element_to_be_clickable, not presence: the filters button renders before it's usable.
        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="All filters"]'))).click()
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

        show_results_button: WebElement = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "apply current filters to show")]')))
        show_results_button.click()
        buffer(3)   # let the results reload settle before anything reads the list

        global pause_after_filters
        if pause_after_filters and "Turn off Pause after search" == pyautogui.confirm("These are your configured search results and filter. It is safe to change them while this dialog is open, any changes later could result in errors and skipping this search run.", "Please check your results", ["Turn off Pause after search", "Look's good, Continue"]):
            pause_after_filters = False

    except Exception as e:
        print_lg("Setting the preferences failed!")
        pyautogui.confirm(f"Faced error while applying filters. Please make sure correct filters are selected, click on show results and click on any button of this dialog, I know it sucks. Can't turn off Pause after search when error occurs! ERROR: {e}", ["Doesn't look good, but Continue XD", "Look's good, Continue"])
        # print_lg(e)



def get_page_info() -> tuple[WebElement | None, int | None]:
    '''
    Function to get pagination element and current page number
    '''
    try:
        pagination_element = try_find_by_classes(driver, ["jobs-search-pagination__pages", "artdeco-pagination", "artdeco-pagination__pages"])
        scroll_to_view(driver, pagination_element)
        # ".//" keeps this inside the pagination element; a leading "//" searches the whole document.
        current_page = int(pagination_element.find_element(By.XPATH, ".//button[contains(@class, 'active')]").text)
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
    skip = False
    # Every class on a job card that carried data is now a rotating random string, so anchor
    # on the artdeco lockup structure instead. The title link is no longer the card's first
    # <a> in every layout either, so address it through the lockup title too.
    job_details_button = job.find_element(By.XPATH, ".//div[contains(@class,'artdeco-entity-lockup__title')]//a")
    scroll_to_view(driver, job_details_button, True)
    job_id = job.get_dom_attribute('data-occludable-job-id')
    # aria-label is the whole title; .text of the link also drags in the verified-badge node,
    # and slicing at the first "\n" silently ate the last character when there wasn't one.
    title = job_details_button.get_dom_attribute('aria-label') or job_details_button.text
    title = title.split("\n")[0].removesuffix(" with verification").strip()
    # The subtitle used to read "Company · Location (Style)". It is now the company alone,
    # and the location moved into its own metadata list.
    company = job.find_element(By.XPATH, ".//div[contains(@class,'artdeco-entity-lockup__subtitle')]").text.strip()
    location_ele = try_xp(job, ".//ul[contains(@class,'job-card-container__metadata-wrapper')]//span[@dir='ltr']", False)
    work_location = location_ele.text.strip() if location_ele else "Unknown"
    work_style = "Unknown"
    if '(' in work_location and ')' in work_location:
        work_style = work_location[work_location.rfind('(')+1:work_location.rfind(')')]
        work_location = work_location[:work_location.rfind('(')].strip()
    
    # Skip if previously rejected due to blacklist or already applied
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


def find_bad_word(text: str, words: list[str]) -> str | None:
    '''
    Returns the first entry of `words` that appears in `text` as a whole word, else None.
    A plain substring scan made "java" skip every JavaScript role, so boundaries are
    applied - but only on the alphanumeric edges of the phrase, so ".NET" still matches
    ".NET" and "ASP.NET" while not matching ".NETWORK".
    '''
    for word in words:
        word = str(word).strip()
        if not word: continue
        left = r'(?<!\w)' if word[0].isalnum() or word[0] == '_' else ''
        right = r'(?!\w)' if word[-1].isalnum() or word[-1] == '_' else ''
        if re.search(left + re.escape(word) + right, text, re.IGNORECASE):
            return word
    return None


def label_has(label: str, *words: str) -> bool:
    '''
    Whole-word test for a question label, reusing `find_bad_word`'s boundary rules.
    A plain `'state' in label` matched "...authorized to work in the United States?" and
    answered a work-authorization question with the user's state of residence.
    Word-boundary matching on "state" deliberately does NOT match "States".
    '''
    return find_bad_word(label, list(words)) is not None


# Work-authorization wording overlaps the location questions ("United States" contains
# "state") and the two families collide in every branch below, so it is classified first.
visa_terms = ['sponsor', 'sponsors', 'sponsorship', 'visa', 'visas', 'work permit', 'h-1b', 'h1b']
# "Do you already have permission to work here?" - a Yes/No question. Lumping it in with
# citizenship answered it with the descriptive citizenship status, which is not a valid
# option in a Yes/No dropdown, so the fallback mapped it to "No" and told employers the
# applicant was not authorized to work.
authorization_terms = ['employment eligibility', 'legally authorized', 'legally authorised',
                       'authorized to work', 'authorised to work', 'work authorization',
                       'work authorisation', 'right to work']
citizenship_terms = ['citizen', 'citizens', 'citizenship']

# Answer -> dropdown option mapping (see the NoSuchElementException fallback in
# `answer_questions`). Matched with `find_bad_word`, i.e. whole words: 'no' as a substring
# lives inside "**No**n-citizen ...", "not", "none" and "know".
decline_terms = ['decline', 'prefer not', 'not wish', "don't wish", 'not want', 'rather not']
negation_terms = ['no', 'not', 'never', "don't", "doesn't", "won't", "can't", 'cannot',
                  'disagree', 'decline']

# Checkbox labels that carry legal weight: attestations, certifications, consents,
# agreements, acknowledgements, authorisations. None of these is ever auto-ticked - and
# neither is a checkbox that matches nothing, because a box we cannot classify is unsafe
# too. So this list changes no decision; it names *why* a box was left for the user.
masters_terms = ['master', 'masters', "master's", 'ms', 'm.s.', 'msc', 'm.sc.', 'graduate degree']
clearance_terms = ['polygraph', 'clearance', 'secret', 'top secret', 'ts/sci', 'sci']
attestation_terms = ['certify', 'certifies', 'certification', 'attest', 'attestation',
                     'consent', 'consents', 'agree', 'agreement', 'terms', 'conditions',
                     'policy', 'acknowledge', 'acknowledgement', 'acknowledgment',
                     'authorize', 'authorise', 'authorization', 'authorisation',
                     'background check', 'drug test', 'drug screen', 'drug screening',
                     'accurate', 'accuracy', 'true and complete', 'eligible', 'eligibility',
                     'citizen', 'citizenship', 'clearance', 'i understand', 'i confirm']

# `years_of_experience` is a TOTAL, so it only answers a question that asks for the total.
total_experience_terms = ['years of experience', 'years experience', 'work experience',
                          'working experience', 'professional experience', 'total experience',
                          'overall experience', 'industry experience', 'years of work',
                          'technical experience', 'years of technical', 'engineering experience']
# ...and not when that question is narrowed to one skill: "years of Kubernetes experience",
# "years of experience IN Kubernetes", "experience WITH Python", "how many years USING AWS".
skill_qualifier_terms = ['in', 'with', 'using', 'on']

def work_authorization_answer(label: str) -> str | None:
    '''
    The configured answer for a visa / authorization / citizenship question, else `None`.
    Three distinct questions, and a work-visa holder answers them differently:
      "will you require sponsorship / a new or transferred visa" -> `require_visa`      Yes
      "are you legally authorized to work here"                  -> `legally_authorized` Yes
      "what is your citizenship status"                          -> `us_citizenship`     a status
    Order matters. Sponsorship first: "sponsor a new U.S. work visa or work authorization"
    is a sponsorship question, not an authorization one. Authorization before citizenship:
    "are you a citizen or otherwise legally authorized to work" is a Yes/No question.
    '''
    if find_bad_word(label, visa_terms): return require_visa
    if find_bad_word(label, authorization_terms): return legally_authorized
    if find_bad_word(label, citizenship_terms): return us_citizenship
    return None


def match_answer_to_option(answer: str | None, option_texts: list[str]) -> int | None:
    '''
    Index of the option that honestly carries `answer`, else `None`. One mapper, called by
    both the `<select>` and the radio branch of `answer_questions`, so a fix lands in both.

    Whole words only, in both directions. `'no' in lower_answer` fired on "**No**n-citizen
    allowed to work..." and answered "are you legally authorized to work" with "No";
    `low_phrase in low_option` then let the option "No" match nearly any text. Same bug
    class as `'state'` in "United States" and `'java'` in "JavaScript": same fix,
    `find_bad_word`. `None` means no honest match - the caller must leave the control
    alone, never fall back to the first option.
    '''
    if not answer: return None
    want_negative = None            # None = the answer has no Yes/No polarity
    if find_bad_word(answer, decline_terms):
        candidate_phrases = ["Decline", "not wish", "don't wish", "Prefer not", "not want"]
    elif find_bad_word(answer, ['yes']):
        candidate_phrases = ["Yes", "Agree", "I do", "I have"]
        want_negative = False
    elif find_bad_word(answer, ['no']):
        candidate_phrases = ["No", "Disagree", "I don't", "I do not"]
        want_negative = True
    else:
        candidate_phrases = [answer, answer.lower(), answer.upper(),
                             ''.join(ch for ch in answer if ch.isalnum())]
    for phrase in candidate_phrases:
        for i, option in enumerate(option_texts):
            if not (find_bad_word(option, [phrase]) or find_bad_word(phrase, [option])):
                continue
            # A Yes must never land on a negated option and vice versa:
            # "I do" is a whole-word prefix of "I do not wish to answer".
            if want_negative is not None and want_negative != (find_bad_word(option, negation_terms) is not None):
                continue
            return i
    return None


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
        word = find_bad_word(about_company_org, about_company_bad_words)
        if word:
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
    # Initialise every return value before the try, so an early failure (e.g. the
    # description element not being found) can never leave them unbound.
    jobDescription = "Unknown"
    experience_required = "Unknown"
    skip = False
    skipReason = None
    skipMessage = None
    try:
        found_masters = 0
        jobDescription = find_by_class(driver, "jobs-box__html-content").text
        jobDescriptionLow = jobDescription.lower()
        bad_word = find_bad_word(jobDescription, bad_words)
        if bad_word:
            skipMessage = f'\n{jobDescription}\n\nContains bad word "{bad_word}". Skipping this job!\n'
            skipReason = "Found a Bad Word in About Job"
            skip = True
        # Sponsorship, tier 1: only what THIS posting says. Offers are checked FIRST and an
        # offer always wins, because real postings say both - "we do not require you to have
        # sponsorship ... we will sponsor H-1B transfers" is an offer, not a refusal. Whole
        # phrases via find_bad_word, so "sponsorship of our annual conference" is not one
        # either. Silence means APPLY by default: silence is not a refusal, and most postings
        # are silent. That is a default, not a law - this bot is built to run until LinkedIn's
        # daily Easy Apply cap fires (dailyEasyApplyLimitReached), so applications are
        # RATIONED: a wrong apply costs a slot, a wrong skip costs a slot's worth of chance.
        # Both errors are the same currency, which is why the third state is a user setting
        # and not a hardcoded choice - see skip_jobs_without_sponsorship. It stays OFF by
        # default because recall is worst for the seed/Series-A companies most likely to be
        # silent yet sponsor.
        # ponytail: JD text only. Whether the EMPLOYER has ever sponsored (tier 2, the DOL
        # LCA index) is deliberately not built here - absence from that data is not evidence.
        if (not skip and require_visa == "Yes" and skip_non_sponsoring_jobs
                and not find_bad_word(jobDescription, sponsorship_offered_phrases)):
            no_sponsorship = find_bad_word(jobDescription, sponsorship_unavailable_phrases)
            if no_sponsorship:
                skipMessage = f'\n{jobDescription}\n\nSays "{no_sponsorship}" and offers no sponsorship. Skipping this job!\n'
                skipReason = f'Job description excludes visa sponsorship ("{no_sponsorship}")'
                skip = True
            elif skip_jobs_without_sponsorship:
                skipMessage = f'\n{jobDescription}\n\nSays nothing either way about sponsorship. Skipping this job (strict mode)!\n'
                skipReason = "Job description is silent on visa sponsorship (not a refusal)"
                skip = True
        # Whole words: substring 'clearance' matched "clearance sale" and 'secret' matched
        # "secretary", skipping jobs that had nothing to do with a clearance. Same bug class
        # find_bad_word() was written for.
        if not skip and security_clearance == False and find_bad_word(jobDescriptionLow, clearance_terms):
            skipMessage = f'\n{jobDescription}\n\nFound "Clearance" or "Polygraph". Skipping this job!\n'
            skipReason = "Asking for Security clearance"
            skip = True
        if not skip:
            if did_masters and find_bad_word(jobDescriptionLow, masters_terms):
                print_lg(f'Found the word "master" in \n{jobDescription}')
                found_masters = 2
            experience_required = extract_years_of_experience(jobDescription)
            if current_experience > -1 and experience_required > current_experience + found_masters:
                skipMessage = f'\n{jobDescription}\n\nExperience required {experience_required} > Current Experience {current_experience + found_masters}. Skipping this job!\n'
                skipReason = "Required experience is high"
                skip = True
    except Exception as e:
        if jobDescription == "Unknown":
            # We never read the description, so the bad words, security clearance and
            # experience filters never ran. Skip instead of applying to an unread job.
            print_lg("Unable to extract job description!", e)
            skipReason = "Unable to read the job description"
            skipMessage = f'\nCouldn\'t read the job description, so none of the skip filters could run. Skipping this job!\n{e}\n'
            skip = True
        else:
            experience_required = "Error in extraction"
            print_lg("Unable to extract years of experience required!", e)
    return jobDescription, experience_required, skip, skipReason, skipMessage
        


# Function to upload resume
def upload_resume(modal: WebElement, resume: str) -> tuple[bool, str]:
    try:
        modal.find_element(By.NAME, "file").send_keys(os.path.abspath(resume))
        return True, os.path.basename(default_resume_path)
    except: return False, "Previous resume"

# Function to answer common questions for Easy Apply
def answer_common_questions(label: str, answer: str | None) -> str | None:
    auth_answer = work_authorization_answer(label)
    return auth_answer if auth_answer is not None else answer


# Function to answer the questions for Easy Apply
def answer_questions(modal: WebElement, questions_list: set, work_location: str, job_description: str | None = None ) -> set:
    # Get all questions from the page
     
    # The container class churns (it is `fb-dash-form-element` today, paired with a random
    # class). `data-test-form-element` is the attribute that has survived every restyle.
    all_questions = modal.find_elements(By.XPATH, ".//div[@data-test-form-element]")
    # Per-pass, not cumulative: the caller compares consecutive passes to spot a stall.
    unanswered_questions.clear()
    # all_list_questions = modal.find_elements(By.XPATH, ".//div[@data-test-text-entity-list-form-component]")
    # all_single_line_questions = modal.find_elements(By.XPATH, ".//div[@data-test-single-line-text-form-component]")
    # all_questions = all_questions + all_list_questions + all_single_line_questions

    for Question in all_questions:
        # Only the typeahead text inputs need the follow-up ARROW_DOWN + ENTER. It used to be
        # set inside the text branch alone and read from the textarea branch, so any form with
        # a textarea and no earlier text input died with UnboundLocalError.
        do_actions = False
        # Check if it's a select Question
        select = try_xp(Question, ".//select", False)
        if select:
            label_org = "Unknown"
            try:
                label = Question.find_element(By.TAG_NAME, "label")
                label_org = label.find_element(By.TAG_NAME, "span").text
            except: pass
            # No default answer. `answer = 'Yes'` here meant an unclassified dropdown -
            # "Do you have an active security clearance?" - was answered Yes and submitted,
            # the same defect already removed from the radio branch below.
            answer = None
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
                # Pick a sensible answer for the dropdown from the question label.
                # Whole words only, and work authorization first: "Are you currently legally
                # authorized to work in the United States?" contains "state" and used to be
                # answered with the state of residence.
                auth_answer = work_authorization_answer(label)
                if auth_answer is not None:
                    answer = auth_answer
                elif label_has(label, 'email', 'phone'):
                    answer = prev_answer
                elif label_has(label, 'gender', 'sex', 'sexual orientation'):
                    answer = gender
                elif label_has(label, 'disability'):
                    answer = disability_status
                elif label_has(label, 'proficiency'):
                    answer = 'Professional'
                elif label_has(label, 'location', 'city', 'state', 'country'):
                    if label_has(label, 'country'):
                        answer = country
                    elif label_has(label, 'state'):
                        answer = state
                    elif label_has(label, 'city'):
                        answer = current_city if current_city else work_location
                    else:
                        answer = work_location
                else:
                    answer = answer_common_questions(label, answer)
                try:
                    if answer is None: raise NoSuchElementException(label_org)
                    select.select_by_visible_text(answer)
                except NoSuchElementException:
                    # The exact text isn't an option; map our answer onto the nearest option.
                    matched = match_answer_to_option(answer, optionsText)
                    if matched is not None:
                        select.select_by_visible_text(optionsText[matched])
                        answer = optionsText[matched]
                    else:
                        # Never guess: a random pick gets submitted as a real answer. Leave the
                        # dropdown alone so LinkedIn blocks Next and the failed-question path
                        # (pause_at_failed_question, else a failed application) takes over.
                        print_lg(f'No option matched "{answer or "a configured answer"}" for "{label_org}". Leaving it unanswered instead of guessing.')
                        answer = prev_answer
                        randomly_answered_questions.add((f'{label_org} [ {options} ]', "select"))
                        unanswered_questions.add(f'{label_org} [ {options} ]')
            else: answer = prev_answer
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
            # No default answer. `answer = 'Yes'` here meant an unclassified label - "Do you
            # have an active security clearance?", "Are you a US citizen?" - was submitted as
            # a Yes on a real application.
            answer = None
            label = label_org.lower()

            label_org += ' [ '
            options = radio.find_elements(By.TAG_NAME, 'input')
            options_labels = []
            option_texts = []       # visible label text only: the "<value>" suffix is a urn
            
            for option in options:
                id = option.get_attribute("id")
                option_label = try_xp(radio, f'.//label[@for="{id}"]', False)
                option_texts.append(option_label.text if option_label else "")
                options_labels.append( f'"{option_label.text if option_label else "Unknown"}"<{option.get_attribute("value")}>' ) # Saving option as "label <value>"
                if option.is_selected(): prev_answer = options_labels[-1]
                label_org += f' {options_labels[-1]},'

            if overwrite_previous_answers or prev_answer is None:
                auth_answer = work_authorization_answer(label)
                if auth_answer is not None: answer = auth_answer
                elif label_has(label, 'veteran', 'protected'): answer = veteran_status
                elif label_has(label, 'disability', 'handicapped'): 
                    answer = disability_status
                else: answer = answer_common_questions(label,answer)
                foundOption = try_xp(radio, f".//label[normalize-space()='{answer}']", False) if answer else False
                if foundOption: 
                    actions.move_to_element(foundOption).click().perform()
                else:
                    matched = match_answer_to_option(answer, option_texts)
                    if matched is None:
                        # Never guess: `options[0]` clicked whatever LinkedIn rendered first
                        # and submitted it as a real answer - the radio twin of the
                        # `select_by_index(randint(...))` that was removed from the dropdown.
                        # Leave the group untouched so the stall guard skips the job.
                        print_lg(f'No option matched "{answer}" for "{label_org} ]". Leaving it unanswered instead of guessing.')
                        answer = prev_answer
                        randomly_answered_questions.add((f'{label_org} ]',"radio"))
                        unanswered_questions.add(f'{label_org} ]')
                    else:
                        actions.move_to_element(options[matched]).click().perform()
                        answer = options_labels[matched]
            else: answer = prev_answer
            questions_list.add((label_org+" ]", answer, "radio", prev_answer))
            continue
        
        # Check if it's a text question
        text = try_xp(Question, ".//input[@type='text']", False)
        if text: 
            label = try_xp(Question, ".//label[@for]", False)
            try: label = label.find_element(By.CLASS_NAME,'visually-hidden')
            except: pass
            label_org = label.text if label else "Unknown"
            answer = "" # years_of_experience
            label = label_org.lower()

            prev_answer = text.get_attribute("value")
            if not prev_answer or overwrite_previous_answers:
                auth_answer = work_authorization_answer(label)
                if auth_answer is not None: answer = auth_answer
                elif label_has(label, 'experience', 'years'):
                    # Only the total. "How many years of Kubernetes experience do you have?"
                    # and "...experience with Python?" ask about ONE skill, and the user's
                    # total is a false answer to those - leave them for config/questions.py.
                    if find_bad_word(label, total_experience_terms) and not find_bad_word(label, skill_qualifier_terms):
                        answer = years_of_experience
                elif label_has(label, 'phone', 'mobile'): answer = phone_number
                elif label_has(label, 'street'): answer = street
                elif label_has(label, 'email'):
                    # "Email address" contains the whole word "address", so without this guard it
                    # falls through below and types the user's CITY into the email box. There is no
                    # email value in config/personals.py, so leave it for LinkedIn's own prefill
                    # rather than guessing. ponytail: add `email` to personals.py to answer it.
                    print_lg(f'No configured answer for the email question "{label_org}". Leaving LinkedIn\'s own value in place.')
                elif label_has(label, 'city', 'location', 'address'):
                    answer = current_city if current_city else work_location
                    do_actions = True
                elif label_has(label, 'signature'): answer = full_name # 'signature' in label or 'legal name' in label or 'your name' in label or 'full name' in label: answer = full_name     # What if question is 'name of the city or university you attend, name of referral etc?'
                elif label_has(label, 'name', 'surname'):
                    if label_has(label, 'full'): answer = full_name
                    elif label_has(label, 'first') and not label_has(label, 'last'): answer = first_name
                    elif label_has(label, 'middle') and not label_has(label, 'last'): answer = middle_name
                    elif label_has(label, 'last', 'surname') and not label_has(label, 'first'): answer = last_name
                    elif label_has(label, 'employer'): answer = recent_employer
                    else: answer = full_name
                elif label_has(label, 'notice'):
                    if label_has(label, 'month', 'months', 'monthly'):
                        answer = notice_period_months
                    elif label_has(label, 'week', 'weeks', 'weekly'):
                        answer = notice_period_weeks
                    else: answer = notice_period
                elif label_has(label, 'salary', 'compensation', 'ctc', 'pay'): 
                    if label_has(label, 'current', 'present'):
                        if label_has(label, 'month', 'months', 'monthly'):
                            answer = current_ctc_monthly
                        elif label_has(label, 'lakh', 'lakhs'):
                            answer = current_ctc_lakhs
                        else:
                            answer = current_ctc
                    else:
                        if label_has(label, 'month', 'months', 'monthly'):
                            answer = desired_salary_monthly
                        elif label_has(label, 'lakh', 'lakhs'):
                            answer = desired_salary_lakhs
                        else:
                            answer = desired_salary
                elif label_has(label, 'linkedin'): answer = linkedIn
                elif label_has(label, 'website', 'blog', 'portfolio', 'link', 'links'): answer = website
                elif label_has(label, 'scale of 1-10'): answer = confidence_level
                elif label_has(label, 'headline'): answer = linkedin_headline
                elif label_has(label, 'hear', 'heard', 'come across') and label_has(label, 'this') and label_has(label, 'job', 'position'): answer = "https://github.com/GodsScion/Auto_job_applier_linkedIn"
                elif label_has(label, 'state', 'province'): answer = state
                elif label_has(label, 'zip', 'zipcode', 'postal', 'postcode', 'code'): answer = zipcode
                elif label_has(label, 'country'): answer = country
                else: answer = answer_common_questions(label,answer)
                if answer == "":
                    ai_answer = ""
                    if use_AI and aiClient:
                        try:
                            ai_answer = answer_question(aiClient, label_org, question_type="text", job_description=job_description, user_information_all=user_information_all)
                        except Exception as e:
                            print_lg("Failed to get AI answer!", e)
                    if ai_answer and isinstance(ai_answer, str) and ai_answer.strip():
                        answer = ai_answer.strip()
                        print_lg(f'AI answered "{label_org}": "{answer}"')
                    else:
                        # Leave it empty. It used to fall back to `years_of_experience`, so
                        # "How many years of Kubernetes?", "What is your expected salary?"
                        # and "How many people did you manage?" were all submitted as the
                        # user's total years of experience - wrong data on a real
                        # application. Report it and let the stall guard skip the job.
                        print_lg(f'No answer for the text question "{label_org}". Leaving it empty - add it to config/questions.py.')
                        randomly_answered_questions.add((label_org, "text"))
                        unanswered_questions.add(label_org)
                text.clear()
                human_type(text, answer)
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
                if label_has(label, 'summary'): answer = linkedin_summary
                elif label_has(label, 'cover'): answer = cover_letter
                if answer == "":
                    ai_answer = ""
                    if use_AI and aiClient:
                        try:
                            ai_answer = answer_question(aiClient, label_org, question_type="textarea", job_description=job_description, user_information_all=user_information_all)
                        except Exception as e:
                            print_lg("Failed to get AI answer!", e)
                    if ai_answer and isinstance(ai_answer, str) and ai_answer.strip():
                        answer = ai_answer.strip()
                        print_lg(f'AI answered "{label_org}": "{answer}"')
                    else:
                        randomly_answered_questions.add((label_org, "textarea"))
                        unanswered_questions.add(label_org)
            text_area.clear()
            human_type(text_area, answer)
            questions_list.add((label, text_area.get_attribute("value"), "textarea", prev_answer))
            continue

        # Check if it's a checkbox question
        checkbox = try_xp(Question, ".//input[@type='checkbox']", False)
        if checkbox:
            # The "Follow <company>" box is the one benign checkbox on this form, and
            # `follow_company()` already drives it from `follow_companies`. Ticking it here
            # too would fight that setting, so leave it to its one owner.
            if checkbox.get_attribute("id") == "follow-company-checkbox": continue
            label = try_xp(Question, ".//span[@class='visually-hidden']", False)
            label_org = label.text if label else "Unknown"
            label = label_org.lower()
            answer = try_xp(Question, ".//label[@for]", False)  # Sometimes multiple checkboxes are given for 1 question, Not accounted for that yet
            answer = answer.text if answer else "Unknown"
            prev_answer = checkbox.is_selected()
            checked = prev_answer
            if not prev_answer:
                # Never tick a box just because it is there. Every unticked checkbox used to
                # be clicked, which silently agreed to whatever it said: "I certify I am a
                # U.S. citizen", "I consent to a background check", "I agree to the terms".
                # An attestation has no honest default and the rest cannot be classified, so
                # both are left alone and reported, exactly like the radio branch.
                term = find_bad_word(f'{label_org} {answer}', attestation_terms)
                blocked = f'{label_org} ([ ] {answer})'
                print_lg('Not ticking "{}": it {}. Tick it yourself, it is not something to guess.'.format(
                    blocked, f'is an attestation or consent ("{term}")' if term else 'cannot be classified'))
                randomly_answered_questions.add((blocked, "checkbox"))
                unanswered_questions.add(blocked)
            questions_list.add((f'{label} ([X] {answer})', checked, "checkbox", prev_answer))
            continue


    # Select todays date. Scoped to the modal: on `driver` this clicked any date picker
    # anywhere on the page. It does mean to click, so click stays True here.
    try_xp(modal, ".//button[contains(@aria-label, 'This is today')]")

    # Collect important skills
    # if 'do you have' in label and 'experience' in label and ' in ' in label -> Get word (skill) after ' in ' from label
    # if 'how many years of experience do you have in ' in label -> Get word (skill) after ' in '

    return questions_list




# The apply button, Easy Apply or external. `id` is stable and semantic; the class is the
# fallback for older renders. Never the design-system size token (artdeco-button--<n>).
apply_button_xpath = ".//button[@id='jobs-apply-button-id' or contains(@class,'jobs-apply-button')]"

def external_apply(pagination_element: WebElement, job_id: str, job_link: str, resume: str, date_listed, application_link: str, screenshot_name: str) -> tuple[bool, str, int]:
    '''
    Function to open new tab and save external job application links
    '''
    global tabs_count, dailyEasyApplyLimitReached, skip_count
    if easy_apply_only:
        try:
            if "exceeded the daily application limit" in driver.find_element(By.CLASS_NAME, "artdeco-inline-feedback__message").text: dailyEasyApplyLimitReached = True
        except: pass
        print_lg("Not an Easy Apply job (easy_apply_only is on), skipping it.")
        if pagination_element != None:
            # Count it. This used to return before touching any counter, so a run where
            # Easy Apply detection was broken summarised as 0/0/0/0 - "it found no jobs".
            skip_count += 1
            return True, application_link, tabs_count
    try:
        # The design-system button SIZE class this used to also require (artdeco-button--<n>)
        # has nothing to do with applying and churns with every restyle, so it's gone.
        wait.until(EC.element_to_be_clickable((By.XPATH, apply_button_xpath))).click()
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



# Easy Apply modal buttons. All of these are `type="button"`, so type is no help, and all of
# them must be searched INSIDE the dialog: document-wide, "Next" also matches the search
# results pagination control (aria-label "View next page").
next_button_xpath = './/button[@aria-label="Continue to next step" or contains(normalize-space(.), "Next")]'
review_button_xpath = './/button[@aria-label="Review your application" or normalize-space(.)="Review"]'
submit_button_xpath = './/button[@aria-label="Submit application" or normalize-space(.)="Submit application"]'

# Easy Apply detection strategies, tried in order, most stable signal first. The button also
# still says "Easy Apply" in its aria-label - the widely repeated claim that LinkedIn dropped
# the word is false - but its design-system classes churn, so no single locator carries this.
# Whatever matches is clicked and then confirmed by the Easy Apply modal actually opening; a
# new browser tab instead means the job was external.
easy_apply_locators = [
    ("apply button id", ".//button[@id='jobs-apply-button-id']"),
    # ponytail: not seen in the captured DOM, kept as a cheap extra shot before the classes.
    ("in-app apply URL flag", ".//a[contains(@href, 'openSDUIApplyFlow=true')]"),
    ("aria-label", ".//button[contains(@class,'jobs-apply-button') and contains(@aria-label, 'Easy Apply')]"),
    ("button label", ".//button[contains(@class,'jobs-apply-button')][.//span[contains(normalize-space(.), 'Easy Apply')]]"),
    ("apply button", apply_button_xpath),
]


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
            record = {
                'Job ID': job_id, 'Job Link': job_link, 'Resume Tried': resume,
                'Date listed': date_listed, 'Date Tried': datetime.now(),
                'Assumed Reason': error, 'Stack Trace': exception,
                'External Job link': application_link, 'Screenshot Name': screenshot_name,
            }
            writer.writerow({key: truncate_for_csv(value) for key, value in record.items()})
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
            record = {
                'Job ID': job_id, 'Title': title, 'Company': company, 'Work Location': work_location,
                'Work Style': work_style, 'About Job': description, 'Experience required': experience_required,
                'Skills required': skills, 'HR Name': hr_name, 'HR Link': hr_link, 'Resume': resume,
                'Re-posted': reposted, 'Date Posted': date_listed, 'Date Applied': date_applied,
                'Job Link': job_link, 'External Job link': application_link,
                'Questions Found': questions_list, 'Connect Request': connect_request,
            }
            writer.writerow({key: truncate_for_csv(value) for key, value in record.items()})
        csv_file.close()
    except Exception as e:
        print_lg("Failed to update submitted jobs list!", e)
        pyautogui.alert("Failed to update the excel of applied jobs!\nProbably because of 1 of the following reasons:\n1. The file is currently open or in use by another program\n2. Permission denied to write to the file\n3. Failed to find the file", "Failed Logging")



# The "Save this application?" confirmation that the modal's Dismiss button raises.
# `data-control-name` is the language-independent anchor; the text is the fallback.
discard_button_xpath = ".//button[@data-control-name='discard_application_confirm_btn' or contains(normalize-space(.), 'Discard')]"

def easy_apply_modal_is_open() -> bool:
    '''True while an Easy Apply modal is still on screen and swallowing every click.'''
    try: return any(m.is_displayed() for m in driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-modal"))
    except Exception: return False

# Function to discard the job application
def discard_job() -> None:
    '''
    Close the Easy Apply modal and discard the draft.

    ESCAPE alone does not reliably raise the confirmation, and a modal left open makes
    every later click fail with "Other element would receive the click" - one failed
    discard used to kill the whole run. So: click the real Dismiss button, wait out the
    dialog animation (2s was too short), click Discard, and verify the modal is gone.
    ESCAPE stays as the fallback.
    '''
    for dismiss in (lambda: try_xp(driver, ".//button[@data-test-modal-close-btn]"),
                    lambda: actions.send_keys(Keys.ESCAPE).perform()):
        try: dismiss()
        except Exception as e: print_lg("Couldn't dismiss the application modal.", e)
        wait_xp_click(driver, discard_button_xpath, 5)
        if not easy_apply_modal_is_open(): return
    print_lg("Warning: the Easy Apply modal is still open after trying to discard it.")


def questions_are_stalled(previous_blocked: set | None) -> bool:
    '''
    Called after a pass of `answer_questions`: True when that pass answered nothing new and
    required questions are still unanswered, so LinkedIn will never enable Next and the
    loop can only spin until the attempt ceiling. Not guessing is correct, but it needs an
    exit.
    '''
    return bool(unanswered_questions) and unanswered_questions == previous_blocked






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
                job_index = 0
                while True:
                    # LinkedIn virtualises this list: off-screen <li>s aren't in the DOM yet and
                    # rendered ones go stale as we scroll, so a single snapshot only ever gets
                    # one screenful. Re-query each time instead of holding that snapshot.
                    job_listings = driver.find_elements(By.XPATH, "//li[@data-occludable-job-id]")
                    if job_index >= len(job_listings): break
                    job = job_listings[job_index]
                    job_index += 1
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
                        try:
                            skills = extract_skills(aiClient, description)
                            print_lg(f"Extracted skills using {ai_provider} AI")
                        except Exception as e:
                            print_lg("Failed to extract skills:", e)
                            skills = "Error extracting skills"

                    uploaded = False
                    # Is this an Easy Apply job? Try each locator in `easy_apply_locators` in
                    # turn and confirm by the modal opening; a new browser tab means external.
                    is_easy_apply = False
                    for how, xpath in easy_apply_locators:
                        apply_button = try_xp(driver, xpath, False)  # detect only, never click
                        if not apply_button: continue
                        try:
                            tabs_open = len(driver.window_handles)
                            apply_button.click()
                            buffer(click_gap)
                            if len(driver.window_handles) > tabs_open:
                                # A new tab opened -> external apply. Close it and return to LinkedIn.
                                driver.switch_to.window(driver.window_handles[-1])
                                if close_tabs and driver.current_window_handle != linkedIn_tab:
                                    driver.close()
                                driver.switch_to.window(linkedIn_tab)
                                print_lg(f"A new tab opened ({how}) - external application.")
                                break
                            find_by_class(driver, "jobs-easy-apply-modal", 3)
                            is_easy_apply = True
                            print_lg(f"Easy Apply detected ({how}).")
                            break
                        except Exception as e:
                            print_lg(f"Easy Apply check '{how}' didn't pan out.", e)
                            # Dismiss whatever popped up and let the next strategy try.
                            try: actions.send_keys(Keys.ESCAPE).perform()
                            except: pass
                    if is_easy_apply:
                        try: 
                            # Bound before the try: the finally below scopes its clicks to the
                            # modal, and an unbound name in there would replace the real failure.
                            modal = driver
                            try:
                                errored = ""
                                modal = find_by_class(driver, "jobs-easy-apply-modal")
                                wait_xp_click(modal, next_button_xpath, 1)
                                # if description != "Unknown":
                                #     resume = create_custom_resume(description)
                                resume = "Previous resume"
                                next_button = True
                                questions_list = set()
                                next_counter = 0
                                blocked_questions = None
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
                                    # `pause_at_failed_question` users want the manual prompt the
                                    # counter above gives them, so only bail out when it is off.
                                    if not pause_at_failed_question and questions_are_stalled(blocked_questions):
                                        errored = "stuck"
                                        raise UnansweredQuestions(
                                            'Skipping "{}" - no answer in config/questions.py for:\n  {}'.format(
                                                title, "\n  ".join(sorted(unanswered_questions))))
                                    blocked_questions = set(unanswered_questions)
                                    if useNewResume and not uploaded: uploaded, resume = upload_resume(modal, default_resume_path)
                                    # Scoped to the dialog on purpose: a document-wide search
                                    # for "Next" matches the search results PAGINATION control
                                    # (aria-label "View next page") and paged away mid-application.
                                    try: next_button = modal.find_element(By.XPATH, review_button_xpath)
                                    except NoSuchElementException:  next_button = modal.find_element(By.XPATH, next_button_xpath)
                                    try: next_button.click()
                                    except ElementClickInterceptedException: break    # Happens when it tries to click Next button in About Company photos section
                                    buffer(click_gap)

                            except NoSuchElementException: errored = "nose"
                            finally:
                                # Nothing in here may raise: an exception raised in a finally
                                # REPLACES the pending one, which is why every failure used to be
                                # logged as "Failed to click Submit application" with no cause.
                                # Record the reason and raise it after the try instead.
                                discard_reason = None
                                if questions_list and errored != "stuck": 
                                    print_lg("Answered the following questions...", questions_list)
                                    print("\n\n" + "\n".join(str(question) for question in questions_list) + "\n\n")
                                wait_xp_click(modal, review_button_xpath, 1, scrollTop=True)
                                cur_pause_before_submit = pause_before_submit
                                if errored == "stuck":
                                    discard_reason = "Required questions left unanswered."
                                elif stop_before_submit:
                                    print_lg('"stop_before_submit" is on: reached the Review step with everything filled in. Discarding this application instead of submitting it.')
                                    raise StoppedBeforeSubmit("Reached Review with everything filled in, then discarded because stop_before_submit is on.")
                                elif errored != "stuck" and cur_pause_before_submit:
                                    decision = pyautogui.confirm('1. Please verify your information.\n2. If you edited something, please return to this final screen.\n3. DO NOT CLICK "Submit Application".\n\n\n\n\nYou can turn off "Pause before submit" setting in config.py\nTo TEMPORARILY disable pausing, click "Disable Pause"', "Confirm your information",["Disable Pause", "Discard Application", "Submit Application"])
                                    if decision == "Discard Application": discard_reason = "Job application discarded by user!"
                                    else: pause_before_submit = False if "Disable Pause" == decision else True
                                    # try_xp(modal, ".//span[normalize-space(.)='Review']")
                                if not discard_reason:
                                    follow_company(modal)
                                    if wait_xp_click(modal, submit_button_xpath, 2, scrollTop=True): 
                                        date_applied = datetime.now()
                                        if not wait_span_click(driver, "Done", 2): actions.send_keys(Keys.ESCAPE).perform()
                                    elif errored != "stuck" and cur_pause_before_submit and "Yes" in pyautogui.confirm("You submitted the application, didn't you 😒?", "Failed to find Submit Application!", ["Yes", "No"]):
                                        date_applied = datetime.now()
                                        wait_span_click(driver, "Done", 2)
                                    else:
                                        print_lg("Since, Submit Application failed, discarding the job application...")
                                        # if screenshot_name == "Not Available":  screenshot_name = screenshot(driver, job_id, "Failed to click Submit application")
                                        # else:   screenshot_name = [screenshot_name, screenshot(driver, job_id, "Failed to click Submit application")]
                                        if errored == "nose": discard_reason = "Failed to click Submit application 😑"
                            # Outside the finally, so this only runs when no real exception is
                            # already on its way up - it can't destroy the genuine cause any more.
                            if discard_reason: raise Exception(discard_reason)

                        except StoppedBeforeSubmit as e:
                            # Not a failure: the dry run did what it was asked. Counting it as
                            # failed made a perfectly good stop_before_submit run read as 0/0/all-failed.
                            print_lg(str(e))
                            skip_count += 1
                            discard_job()
                            continue

                        except UnansweredQuestions as e:
                            print_lg(str(e))
                            print_lg("Add those answers to config/questions.py and re-run to apply to this job.")
                            skip_count += 1
                            discard_job()
                            continue

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
                    pagination_element.find_element(By.XPATH, f".//button[@aria-label='Page {current_page+1}']").click()
                    print_lg(f"\n>-> Now on Page {current_page+1} \n")
                except NoSuchElementException:
                    print_lg(f"\n>-> Didn't find Page {current_page+1}. Probably at the end page of results!\n")
                    break

        except (NoSuchWindowException, WebDriverException) as e:
            print_lg("The browser window was closed or the session became invalid. Stopping.", e)
            raise e  # let the outer handler deal with it
        except Exception as e:
            print_lg("Could not read the job listings.")
            critical_error_log("In Applier", e)
            try:
                print_lg(driver.page_source, pretty=True)
            except Exception as dump_error:
                print_lg(f"Could not capture the page source; the browser may have crashed. {dump_error}")

        
def run(total_runs: int) -> int:
    if dailyEasyApplyLimitReached:
        return total_runs
    print_lg("\n########################################################################################################################\n")
    print_lg(f"Date and Time: {datetime.now()}")
    print_lg(f"Cycle number: {total_runs}")
    print_lg(f"Currently looking for jobs posted within '{date_posted}' and sorting them by '{sort_by}'")
    apply_to_jobs(search_terms)
    print_lg("########################################################################################################################\n")
    # Only wait between cycles when there is actually going to be another cycle. This used
    # to run at the end of every single run, which reads as a 10 minute hang.
    if run_non_stop and not dailyEasyApplyLimitReached:
        print_lg("Sleeping for 10 min...")
        sleep(300)
        print_lg("Few more min... Gonna start with in next 5 min...")
        sleep(300)
    buffer(3)
    return total_runs + 1



chatGPT_tab = False
linkedIn_tab = False

def main() -> None:
    pyautogui.alert("Please consider sponsoring this project at:\n\nhttps://github.com/sponsors/GodsScion\n\n", "Support the project", "Okay")
    total_runs = 1
    try:
        global linkedIn_tab, tabs_count, useNewResume, aiClient
        alert_title = "Error Occurred. Closing Browser!"
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
            aiClient = create_ai_client()

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
        print_lg("The browser window was closed or the session became invalid. Exiting.", e)
    except Exception as e:
        critical_error_log("In Applier Main", e)
        pyautogui.alert(e,alert_title)
    finally:
        summary = "Total runs: {}\nJobs Easy Applied: {}\nExternal job links collected: {}\nTotal applied or collected: {}\nFailed jobs: {}\nIrrelevant jobs skipped: {}\n".format(total_runs,easy_applied_count,external_jobs_count,easy_applied_count + external_jobs_count,failed_count,skip_count)
        print_lg(summary)
        print_lg("\n\nTotal runs:                     {}".format(total_runs))
        print_lg("Jobs Easy Applied:              {}".format(easy_applied_count))
        print_lg("External job links collected:   {}".format(external_jobs_count))
        print_lg("                              ----------")
        print_lg("Total applied or collected:     {}".format(easy_applied_count + external_jobs_count))
        print_lg("\nFailed jobs:                    {}".format(failed_count))
        print_lg("Irrelevant jobs skipped:        {}\n".format(skip_count))
        if randomly_answered_questions: print_lg("\n\nQuestions randomly answered:\n  {}  \n\n".format(";\n".join(str(question) for question in randomly_answered_questions)))
        quotes = choice([
            "Never quit. You're one step closer than before. - Sai Vignesh Golla", 
            "All the best with your future interviews, you've got this. - Sai Vignesh Golla", 
            "Keep up with the progress. You got this. - Sai Vignesh Golla", 
            "If you're tired, learn to take rest but never give up. - Sai Vignesh Golla",
            "Success is not final, failure is not fatal, It is the courage to continue that counts. - Winston Churchill (Not a sponsor)",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson (Not a sponsor)",
            "Every job is a self-portrait of the person who does it. Autograph your work with excellence. - Jessica Guidobono (Not a sponsor)",
            "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. - Steve Jobs (Not a sponsor)",
            "Opportunities don't happen, you create them. - Chris Grosser (Not a sponsor)",
            "The road to success and the road to failure are almost exactly the same. The difference is perseverance. - Colin R. Davis (Not a sponsor)",
            "Obstacles are those frightful things you see when you take your eyes off your goal. - Henry Ford (Not a sponsor)",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt (Not a sponsor)",
            ])
        sponsors = "Be the first to have your name here!"
        timeSaved = (easy_applied_count * 80) + (external_jobs_count * 20) + (skip_count * 10)
        timeSavedMsg = ""
        if timeSaved > 0:
            timeSaved += 60
            timeSavedMsg = f"In this run, you saved approx {round(timeSaved/60)} mins ({timeSaved} secs), please consider supporting the project."
        msg = f"{quotes}\n\n\n{timeSavedMsg}\nYou can also get your quote and name shown here, or prioritize your bug reports by supporting the project at:\n\nhttps://github.com/sponsors/GodsScion\n\n\nSummary:\n{summary}\n\n\nBest regards,\nSai Vignesh Golla\nhttps://www.linkedin.com/in/saivigneshgolla/\n\nTop Sponsors:\n{sponsors}"
        pyautogui.alert(msg, "Exiting..")
        print_lg(msg,"Closing the browser...")
        if tabs_count >= 10:
            msg = "NOTE: IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM!\n\nOr it's highly likely that application will just open browser and not do anything next time!" 
            pyautogui.alert(msg,"Info")
            print_lg("\n"+msg)
        if use_AI and aiClient:
            try:
                close_ai_client(aiClient)
                print_lg(f"Closed {ai_provider} AI client.")
            except Exception as e:
                print_lg("Failed to close AI client:", e)
        try:
            if driver:
                driver.quit()
        except WebDriverException as e:
            print_lg("Browser already closed.", e)
        except Exception as e: 
            critical_error_log("When quitting...", e)


if __name__ == "__main__":
    main()
