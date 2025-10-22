'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''


###################################################### LINKEDIN SEARCH PREFERENCES ######################################################

# These Sentences are Searched in LinkedIn
# Enter your search terms inside '[ ]' with quotes ' "searching title" ' for each search followed by comma ', ' Eg: ["Software Engineer", "Software Developer", "Selenium Developer"]
search_terms = ["Software Engineer", "Software Developer", "Python Developer", "Selenium Developer", "React Developer", "Java Developer", "Front End Developer", "Full Stack Developer", "Web Developer", "Nodejs Developer"]

# Search location, this will be filled in "City, state, or zip code" search box. If left empty as "", tool will not fill it.
search_location = "United States"               # Some valid examples: "", "United States", "India", "Chicago, Illinois, United States", "90001, Los Angeles, California, United States", "Bengaluru, Karnataka, India", etc.

# After how many number of applications in current search should the bot switch to next search? 
switch_number = 30                 # Only numbers greater than 0... Don't put in quotes

# Do you want to randomize the search order for search_terms?
randomize_search_order = False     # True of False, Note: True or False are case-sensitive


# >>>>>>>>>>> Job Search Filters <<<<<<<<<<<
''' 
You could set your preferences or leave them as empty to not select options except for 'True or False' options. Below are some valid examples for leaving them empty:
This is below format: QUESTION = VALID_ANSWER

## Examples of how to leave them empty. Note that True or False options cannot be left empty! 
* question_1 = ""                    # answer1, answer2, answer3, etc.
* question_2 = []                    # (multiple select)
* question_3 = []                    # (dynamic multiple select)

## Some valid examples of how to answer questions:
* question_1 = "answer1"                  # "answer1", "answer2", "answer3" or ("" to not select). Answers are case sensitive.
* question_2 = ["answer1", "answer2"]     # (multiple select) "answer1", "answer2", "answer3" or ([] to not select). Note that answers must be in [] and are case sensitive.
* question_3 = ["answer1", "Random AnswER"]     # (dynamic multiple select) "answer1", "answer2", "answer3" or ([] to not select). Note that answers must be in [] and need not match the available options.

'''

sort_by = ""                       # "Most recent", "Most relevant" or ("" to not select) 
date_posted = "Past week"         # "Any time", "Past month", "Past week", "Past 24 hours" or ("" to not select)
salary = ""                        # "$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+"

easy_apply_only = True             # True or False, Note: True or False are case-sensitive

experience_level = []              # (multiple select) "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"
job_type = []                      # (multiple select) "Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"
on_site = []                       # (multiple select) "On-site", "Remote", "Hybrid"

companies = []                     # (dynamic multiple select) make sure the name you type in list exactly matches with the company name you're looking for, including capitals. 
                                   # Eg: "7-eleven", "Google","X, the moonshot factory","YouTube","CapitalG","Adometry (acquired by Google)","Meta","Apple","Byte Dance","Netflix", "Snowflake","Mineral.ai","Microsoft","JP Morgan","Barclays","Visa","American Express", "Snap Inc", "JPMorgan Chase & Co.", "Tata Consultancy Services", "Recruiting from Scratch", "Epic", and so on...
location = []                      # (dynamic multiple select)
industry = []                      # (dynamic multiple select)
job_function = []                  # (dynamic multiple select)
job_titles = []                    # (dynamic multiple select)
benefits = []                      # (dynamic multiple select)
commitments = []                   # (dynamic multiple select)

under_10_applicants = False        # True or False, Note: True or False are case-sensitive
in_your_network = False            # True or False, Note: True or False are case-sensitive
fair_chance_employer = False       # True or False, Note: True or False are case-sensitive


## >>>>>>>>>>> RELATED SETTING <<<<<<<<<<<

# Pause after applying filters to let you modify the search results and filters?
pause_after_filters = True         # True or False, Note: True or False are case-sensitive

##




## >>>>>>>>>>> SKIP IRRELEVANT JOBS <<<<<<<<<<<
 
# Avoid applying to these companies, and companies with these bad words in their 'About Company' section...
about_company_bad_words = ["Crossover"]       # (dynamic multiple search) or leave empty as []. Ex: ["Staffing", "Recruiting", "Name of Company you don't want to apply to"]

# Skip checking for `about_company_bad_words` for these companies if they have these good words in their 'About Company' section... [Exceptions, For example, I want to apply to "Robert Half" although it's a staffing company]
about_company_good_words = []      # (dynamic multiple search) or leave empty as []. Ex: ["Robert Half", "Dice"]

# Avoid applying to these companies if they have these bad words in their 'Job Description' section...  (In development)
bad_words = ["US Citizen","USA Citizen","No C2C", "No Corp2Corp", ".NET", "Embedded Programming", "PHP", "Ruby", "CNC"]                     # (dynamic multiple search) or leave empty as []. Case Insensitive. Ex: ["word_1", "phrase 1", "word word", "polygraph", "US Citizenship", "Security Clearance"]

# Do you have an active Security Clearance? (True for Yes and False for No)
security_clearance = False         # True or False, Note: True or False are case-sensitive

# Do you have a Masters degree? (True for Yes and False for No). If True, the tool will apply to jobs containing the word 'master' in their job description and if it's experience required <= current_experience + 2 and current_experience is not set as -1. 
did_masters = True                 # True or False, Note: True or False are case-sensitive

# Avoid applying to jobs if their required experience is above your current_experience. (Set value as -1 if you want to apply to all ignoring their required experience...)
current_experience = 5             # Integers > -2 (Ex: -1, 0, 1, 2, 3, 4...)
##






############################################################################################################
'''
THANK YOU for using my tool 😊! Wishing you the best in your job hunt 🙌🏻!

Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. Your support keeps this project alive.

Support my work on <PATREON_LINK>. Together, we can help more job seekers.

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact.

Your support, whether through donations big or small or simply spreading the word, means the world to me and helps keep this project alive and thriving.

Gratefully yours 🙏🏻,
Sai Vignesh Golla
'''
############################################################################################################