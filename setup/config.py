
'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

'''

###################################################### CONFIGURE YOUR TOOLS HERE ######################################################

# >>>>>>>>>>> Global Settings <<<<<<<<<<<

# Directory and name of the files where history of applied jobs is saved (Sentence after the last "/" will be considered as the file name).
file_name = "all excels/all_applied_applications_history.csv"
failed_file_name = "all excels/all_failed_applications_history.csv"
logs_folder_path = "logs/"

# Set the maximum amount of time allowed to wait between each click in secs
click_gap = 1                   # Enter max allowed secs to wait approximately. (Only Non Negative Integers like 0,1,2,3,....)

# If you want to see Chrome running then set run_in_background as False. May reduce performance...
run_in_background = False       # True or False

# If enabled (True), the program would keep your screen active and prevent PC from sleeping. Instead you could disable this feature (set it to false) and adjust your PC sleep settings to Never Sleep or a preferred time. 
keep_screen_awake = False        # True or False

# Run in undetected mode to bypass anti-bot protections (Preview Feature, unstable. Recommended to leave it as False)
undetected_mode = False         # True or False

# Use ChatGPT for resume building (Experimental Feature can break the application. Recommended to leave it as False) 
use_resume_generator = False    # True or False ,   This feature may only work with 'undetected_mode' = True. As ChatGPT website is hosted by CloudFlare which is protected by Anti-bot protections!

# ----------------------------------------------  AUTO APPLIER  ---------------------------------------------- #


# Login Credentials for LinkedIn
username = "username@example.com" 
password = "examplepassword"


# These Sentences are Searched in LinkedIn
keywords = ["Software Developer", "Software Engineer", "Junior Software Developer", "Junior Software Engineer", "React Developer", "Nodejs Developer", "Junior Full Stack Developer", "New Grad Software Developer", "New Grad Software Engineer"]



# >>>>>>>>>>> Easy Apply Inputs <<<<<<<<<<<

# Give an relative or absolute path of your default resume to be uploaded...
default_resume_path = "all resumes/default/resume.pdf"

# What do you want to answer for years of experience you have?
years_of_experience = '3'

# Do you need visa sponsorship now or in future?
require_visa = "No"             # "Yes" or "No"

# What is the status of your citizenship? 
# "U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident" or "Other"
us_citizenship = "Non-citizen allowed to work for any employer" # If left empty as "", tool will not answer the question. However, note that some companies make compulsory to be answered

# What is the link to your portfolio website, leave it empty as "" if you don't want to enter anything
website = "https://github.com/GodsScion" # "www.example.bio" or "" and so on....

# What is your desired salary, only enter in numbers
desired_salary = "90000"        # "80000", "90000", "100000" or "120000" and so on....

# Example question: "On a scale of 1-10 how much experience do you have building web or mobile applications? 1 being very little or only in school, 10 being that you have built and launched applications to real users"
confidence_level = "8"          # Any number between "1" to "10", put em in quotes ""

# How do you identify yourself? If left empty as "", tool will not answer the question. However, note that some companies make compulsory to be answered
gender = "Male"                 # "Male", "Female", "Other", "Decline" or ""
disability_status = ""
full_name = "Sai Vignesh Golla" # Your name in quotes




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

experience_level = []           # (multiple select) "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"
job_type = []                   # (multiple select) "Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"
on_site = []                    # (multiple select) "On-site", "Remote", "Hybrid"

companies = []                  # (dynamic multiple select) "JPMorgan Chase & Co.", "Tata Consultancy Services", "Recruiting from Scratch", "Epic", "Elevance Health", and so on... make sure the name you type in list exactly matches with the company name you're looking for, including capitals.
location = []                   # (dynamic multiple select)
industry = []                   # (dynamic multiple select)
job_function = []               # (dynamic multiple select)
job_titles = []                 # (dynamic multiple select)
benefits = []                   # (dynamic multiple select)
commitments = []                # (dynamic multiple select)

under_10_applicants = False     # True or False
in_your_network = False         # True or False
fair_chance_employer = False    # True or False



# >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<<

# Avoid applying to companies with these words in their description...
blacklist_words = ["Staffing", "Recruiting"] # (dynamic multiple select) or leave empty as []

# Upcoming features
# # Send connection requests to HR's
# connect_hr = True               # True or False

# # What message do you want to send during connection request? (Max. 200 Characters)
# connect_request_message = ""    # Leave Empty to send connection request without personalized invitation (recommended to leave it empty, since you only get 10 per month without LinkedIn Premium*)

# Keep the External Application tabs open?
close_tabs = True               # True or False

# After how many number of applications should we keep switching? 
switch_number = 50              # Only numbers greater than 25... Don't put in quotes

# Do you want the program to run continuously until you stop it?
run_non_stop = False             # True or False
alternate_sortby = True         # True or False
cycle_date_posted = True        # True or False
stop_date_cycle_at_24hr = True  # True or False

# ----------------------------------------------  RESUME GENERATOR (Experimental)  ---------------------------------------------- #

# Login Credentials for ChatGPT
chatGPT_username = "username@example.com"
chatGPT_password = "examplepassword"

chatGPT_resume_chat_title = "Resume review and feedback."

# Give the path to the folder where all the generated resumes are to be stored
generated_resume_path = "all resumes/"
















############################################################################################################
'''
THANK YOU for using my tool! Wishing you the best in your job hunt!

Sharing is caring! If you found this tool helpful, please share it with your peers. Your support keeps this project alive.

Support my work on <PATREON_LINK>. Together, we can help more job seekers.

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact.

Your support, whether through donations big or small or simply spreading the word, means the world to me and helps keep this project alive and thriving.

Gratefully yours,
Sai Vignesh Golla
'''
############################################################################################################