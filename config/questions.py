
###################################################### APPLICATION INPUTS ######################################################


# >>>>>>>>>>> Easy Apply Questions & Inputs <<<<<<<<<<<

# Give an relative path of your default resume to be uploaded. If file in not found, will continue using your previously uploaded resume in LinkedIn.
default_resume_path = "all resumes/default/resume.pdf"      # (In Development)

# What do you want to answer for questions that ask about years of experience you have, this is different from current_experience? 
years_of_experience = "1"          # A number in quotes Eg: "0","1","2","3","4", etc.

# Do you need visa sponsorship now or in future?
require_visa = "No"               # "Yes" or "No"

# What is the link to your portfolio website, leave it empty as "", if you want to leave this question unanswered
website = "https://github.com/aman012"                        # "www.example.bio" or "" and so on....

# Please provide the link to your LinkedIn profile.
linkedIn = "https://www.linkedin.com/in/aman-kumar-srivastava"       # "https://www.linkedin.com/in/example" or "" and so on...

# What is the status of your citizenship? # If left empty as "", tool will not answer the question. However, note that some companies make it compulsory to be answered
# Valid options are: "U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident" or "Other"
us_citizenship = "U.S. Citizen/Permanent Resident"



## SOME ANNOYING QUESTIONS BY COMPANIES 🫠 ##

# What to enter in your desired salary question (American and European), What is your expected CTC (South Asian and others)?, only enter in numbers as some companies only allow numbers,
desired_salary = 600000          # 80000, 90000, 100000 or 120000 and so on... Do NOT use quotes
'''
Note: If question has the word "lakhs" in it (Example: What is your expected CTC in lakhs), 
then it will add '.' before last 5 digits and answer. Examples: 
* 2400000 will be answered as "24.00"
* 850000 will be answered as "8.50"
And if asked in months, then it will divide by 12 and answer. Examples:
* 2400000 will be answered as "200000"
* 850000 will be answered as "70833"
'''

# What is your current CTC? Some companies make it compulsory to be answered in numbers...
current_ctc = 300000            # 800000, 900000, 1000000 or 1200000 and so on... Do NOT use quotes
'''
Note: If question has the word "lakhs" in it (Example: What is your current CTC in lakhs), 
then it will add '.' before last 5 digits and answer. Examples: 
* 2400000 will be answered as "24.00"
* 850000 will be answered as "8.50"
# And if asked in months, then it will divide by 12 and answer. Examples:
# * 2400000 will be answered as "200000"
# * 850000 will be answered as "70833"
'''

# (In Development) # Currency of salaries you mentioned. Companies that allow string inputs will add this tag to the end of numbers. Eg: 
# currency = "INR"                 # "USD", "INR", "EUR", etc.

# What is your notice period in days?
notice_period = 10                # Any number >= 0 without quotes. Eg: 0, 7, 15, 30, 45, etc.
'''
Note: If question has 'month' or 'week' in it (Example: What is your notice period in months), 
then it will divide by 30 or 7 and answer respectively. Examples:
* For notice_period = 66:
  - "66" OR "2" if asked in months OR "9" if asked in weeks
* For notice_period = 15:"
  - "15" OR "0" if asked in months OR "2" if asked in weeks
* For notice_period = 0:
  - "0" OR "0" if asked in months OR "0" if asked in weeks
'''

# Your LinkedIn headline in quotes Eg: "Software Engineer @ Google, Masters in Computer Science", "Recent Grad Student @ MIT, Computer Science"
linkedin_headline = "Data Engineer with hands-on production experience building modern lakehouse pipelines" # "Headline" or "" to leave this question unanswered

# Your summary in quotes, use \n to add line breaks if using single quotes "Summary".You can skip \n if using triple quotes """Summary"""
linkedin_summary = """
Data Engineer with hands-on production experience building modern lakehouse pipelines on the Cloudflare + Trino + Apache Iceberg stack. Strong Python and SQL foundation.
"""

'''
Note: If left empty as "", the tool will not answer the question. However, note that some companies make it compulsory to be answered. Use \n to add line breaks.
''' 

# Your cover letter in quotes, use \n to add line breaks if using single quotes "Cover Letter".You can skip \n if using triple quotes """Cover Letter""" (This question makes sense though)
cover_letter = """
Aman Kumar Srivastava
aman.apk01@gmail.com | +91-7739704188 | Varanasi, U.P, India

Dear Hiring Manager,
I am a Data Engineer with hands-on production experience building lakehouse pipelines using Cloudflare, Trino, and Apache Iceberg. At HumanizeIQ.ai, I have designed ELT workflows, orchestrated 10+ automation pipelines with n8n, and reduced manual data operations by ~8 hours/week.
My background spans data engineering, ML deployment, and full-stack AI applications — backed by a strong foundation in Python, SQL, FastAPI, and Docker. I have a proven track record of delivering measurable impact: cutting pipeline latency by ~70%, reducing stakeholder-reported data discrepancies by ~50%, and serving dashboards to 300+ active users.
I am excited to bring this experience to a team where I can contribute to scalable, production-grade data systems from day one.
Thank you for your time and consideration. I would love to discuss how I can add value to your team.
Warm regards,
Aman Kumar Srivastava
linkedin.com/in/aman-kumar-srivastava | github.com/aman012
"""
# We use this to pass to AI to generate answer from information , Assuing Information contians eg: resume  all the information like name, experience, skills, Country, any illness etc. 
user_information_all ="""
--- PROFESSIONAL PROFILE ---
Aman Kumar Srivastava
Data Engineer | AI Engineer
Experience: 1 Year
Current CTC: ₹300,000 | Expected CTC: ₹600,000
Notice Period: 10 Days

--- PROFESSIONAL SUMMARY ---
Data Engineer with hands-on production experience building modern lakehouse pipelines on the Cloudflare + Trino + Apache Iceberg stack. Designed and maintained ELT workflows ingesting data from Cloudflare D1 into R2-backed cold storage, configured federated SQL layers via Trino for schema-on-read analytics, and orchestrated 10+ automation workflows using n8n. Strong Python and SQL foundation; experienced deploying scalable backends with FastAPI and Docker.

--- TECHNICAL SKILLS ---
Data Engineering: Trino, Apache Iceberg, Apache Hive, ELT Pipelines, Data Lake Architecture, Cloudflare D1 & R2, PostgreSQL, MySQL, Pandas, NumPy
Workflow & Analytics: n8n, Apache Superset, Metabase, Data Lineage, Data Quality Checks, Self-Serve BI, KPI Dashboards
Backend & DevOps: FastAPI, RESTful APIs, Docker, Docker Swarm, GitHub Actions, CI/CD Pipelines, AWS, GCP, Cloudflare, Linux
ML & AI: PyTorch, Scikit-learn, Hugging Face Transformers, Prompt Engineering
Languages: Python, SQL, HTML, CSS

--- WORK EXPERIENCE ---
HumanizeIQ.ai | Data Engineer | Nov 2025 -- Present
- Designed and built a production ELT pipeline ingesting data from Cloudflare D1 into Cloudflare R2.
- Configured Trino over R2-backed Apache Iceberg catalogs as a federated SQL engine.
- Orchestrated 10+ n8n workflows automating D1-to-R2 sync and Trino query triggering.
- Built Metabase dashboards on the Trino layer for self-serve BI reporting and KPI tracking.
- Maintained data quality checks and lineage documentation, reducing discrepancies by 50%.

HumanizeIQ.ai | AI Engineer Intern | June 2025 -- Oct 2025
- Architected 5+ Apache Superset dashboards serving 300+ users, cutting turnaround by 40%.
- Built and deployed production ML solutions using FastAPI and Scikit-learn.
- Drove adoption of dashboards across 3 business teams, reducing ad-hoc SQL requests by 60%.

--- KEY PROJECTS ---
PDF Summarization --- Full-Stack AI Web App (botzcoder.com)
- Engineered PDF ingestion and storage on Cloudflare R2 with async FastAPI workers.
- Built full-stack app with Next.js frontend, FastAPI backend, and Neon PostgreSQL.
- Applied LoRA-based fine-tuning on Mistral-7B, cutting trainable parameters by 99%.

AI Chatbot --- Food Delivery Platform
- Built FastAPI + MySQL backend handling concurrent order sessions with ACID transactions.
- Optimized query execution, reducing p95 response time from 800ms to 120ms.
- Integrated Dialogflow NLP for multi-intent classification (tracking, lookup, complaints).

--- EDUCATION ---
Indian Institute of Information Technology, Kottayam (2020 -- 2024)
B.Tech, Computer Science & Engineering | GPA: 7.48 / 10.0
"""

##<
'''
Note: If left empty as "", the tool will not answer the question. However, note that some companies make it compulsory to be answered. Use \n to add line breaks.
''' 

# Name of your most recent employer
recent_employer = "Not Applicable" # "", "Lala Company", "Google", "Snowflake", "Databricks"

# Example question: "On a scale of 1-10 how much experience do you have building web or mobile applications? 1 being very little or only in school, 10 being that you have built and launched applications to real users"
confidence_level = "8"             # Any number between "1" to "10" including 1 and 10, put it in quotes ""
##



# >>>>>>>>>>> RELATED SETTINGS <<<<<<<<<<<

## Allow Manual Inputs
# Should the tool pause before every submit application during easy apply to let you check the information?
pause_before_submit = True         # True or False, Note: True or False are case-sensitive
'''
Note: Will be treated as False if `run_in_background = True`
'''

# Should the tool pause if it needs help in answering questions during easy apply?
# Note: If set as False will answer randomly...
pause_at_failed_question = True    # True or False, Note: True or False are case-sensitive
'''
Note: Will be treated as False if `run_in_background = True`
'''
##

# Do you want to overwrite previous answers?
overwrite_previous_answers = False # True or False, Note: True or False are case-sensitive






