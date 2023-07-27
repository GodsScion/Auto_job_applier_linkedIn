###### CONFIGURE YOUR TOOLS HERE ######


# Directory and name of the files where history of applied jobs is saved.
file_name = "all excels/all_applied_applications_history.csv"
failed_file_name = "all excels/all_failed_applications_history.csv"

# Set the maximum amount of time allowed to wait between each click
click_gap = 0                   # Enter max allowed secs to wait approximately. (Only Non Negative Integers like 0,1,2,3,....)

# If you want to see Chrome running then set this as False. May reduce performance...
run_in_background = False       # True or False





# ----------------------------------------------  AUTO APPLIER  ---------------------------------------------- #

# Keep the External Application tabs open?
close_tabs = True               # True or False

# Login Credentials for LinkedIn
username = "username@example.com" 
password = "examplepassword"


# These Sentences are Searched in LinkedIn
keywords = ["Software Developer", "Software Engineer"]

# Give an relative or absolute path of your default resume...
default_resume_path = "all resumes/default/resume.pdf"

# What do you want to enter in questions...
years_of_experience = '3'

# After how many number of applications should we keep switching? 
switch_number = 100

# Do you want the program to run continuously until you stop it?
run_non_stop = True             # True or False
alternate_sortby = True         # True or False
cycle_date_posted = True        # True or False

### Preferences for job search
''' 
You could set your preferences or leave them empty to not select options except for True or False options.
Examples of how to leave empty to not select...
String_Preferences = ""
Multiple_Select = []
'''

sort_by = "Most relevant"       # "Most recent", "Most relevant" or ("" to not select) 
date_posted = "Any time"        # "Any time", "Past month", "Past week", "Past 24 hours" or ("" to not select)
salary = ""                     # "$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+"

easy_apply_only = True          # True or False

experience_level = ["Internship", "Entry level"] # (multiple select) "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"
job_type = []                   # (multiple select) "Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"
on_site = []                    # (multiple select) "On-site", "Remote", "Hybrid"

companies = []                  # (dynamic multiple select) "Dice", "JPMorgan Chase & Co.", "Tata Consultancy Services", "Recruiting from Scratch", "Epic", "Elevance Health", and so on... make sure the name you type in list exactly matches with the company name you're looking for, including capitals.
location = []                   # (dynamic multiple select)
industry = []                   # (dynamic multiple select)
job_function = []               # (dynamic multiple select)
job_titles = []                 # (dynamic multiple select)
benefits = []                   # (dynamic multiple select)
commitments = []                # (dynamic multiple select)

under_10_applicants = False     # True or False
in_your_network = False         # True or False
fair_chance_employer = False    # True or False




# ----------------------------------------------  RESUME GENERATOR  ---------------------------------------------- #

# Login Credentials for ChatGPT
chatGPT_username = "username@example.com"
chatGPT_password = "examplepassword"

chatGPT_resume_chat_title = "Resume review and feedback."

# Give the path to the folder where all the generated resumes are to be stored
generated_resume_path = "all resumes"
















