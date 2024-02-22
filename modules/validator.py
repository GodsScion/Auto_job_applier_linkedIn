'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

'''

from setup.config import *

def validate_TorF(var, var_name):
    if var == True or var == False: return True
    raise Exception(f'Invalid input for {var_name}. Expecting a Boolean input "True" or "False", not "{var}" and do NOT surround True or False in Quotes ("")!')

def validate_String(var, var_name, options=[]):
    if not isinstance(var, str): raise Exception(f'Invalid input for {var_name}. Expecting a String!')
    if len(options) > 0 and var not in options: raise Exception(f'Invalid input for {var_name}. Expecting a value from {options}, not {var}!')
    return True

def validate_Multi(var, var_name, options=[]):
    if not isinstance(var, list): raise Exception(f'Invalid input for {var_name}. Expecting a List!')
    for element in var:
        if not isinstance(element, str): raise Exception(f'Invalid input for {var_name}. All elements in the list must be strings!')
        if len(options) > 0 and element not in options: raise Exception(f'Invalid input for {var_name}. Expecting all elements to be values from {options}. This "{element}" is NOT in options!')
    return True


def validate_config():
    
    validate_String(file_name, "file_name")
    validate_String(failed_file_name, "failed_file_name")

    if not isinstance(click_gap, int) and click_gap >= 0: raise Exception(f'Invalid input for click_gap. Expecting an int greater than or equal to 0, NOT "{click_gap}"!')

    validate_TorF(run_in_background, "run_in_background")
    validate_TorF(smooth_scroll, "smooth_scroll")

    validate_TorF(close_tabs, "close_tabs")

    validate_String(username, "username")
    validate_String(password, "password")

    validate_Multi(search_terms, "search_terms")

    validate_String(sort_by, "sort_by", ["", "Most recent", "Most relevant"])
    validate_String(date_posted, "date_posted", ["", "Any time", "Past week", "Past 24 hours", "Past month"])
    validate_String(salary, "salary", ["", "$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+"])

    validate_Multi(experience_level, "experience_level", ["Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"])
    validate_Multi(job_type, "job_type", ["Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"])
    validate_Multi(on_site, "on_site", ["On-site", "Remote", "Hybrid"])

    validate_Multi(companies, "companies")
    validate_Multi(location, "location")
    validate_Multi(industry, "industry")
    validate_Multi(job_function, "job_function")
    validate_Multi(job_titles, "job_titles")
    validate_Multi(benefits, "benefits")
    validate_Multi(commitments, "commitments")

    validate_TorF(easy_apply_only, "easy_apply_only")
    validate_TorF(under_10_applicants, "under_10_applicants")
    validate_TorF(in_your_network, "in_your_network")
    validate_TorF(fair_chance_employer, "fair_chance_employer")


    validate_String(chatGPT_username, "chatGPT_username")
    validate_String(chatGPT_password, "chatGPT_password")

    validate_String(chatGPT_resume_chat_title, "chatGPT_resume_chat_title")

    return True

