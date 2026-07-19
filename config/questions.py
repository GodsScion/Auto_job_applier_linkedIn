# '''
# Author:     Sai Vignesh Golla
# LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

# Copyright (C) 2024 Sai Vignesh Golla

# License:    GNU Affero General Public License
#             https://www.gnu.org/licenses/agpl-3.0.en.html
            
# GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

# Support me: https://github.com/sponsors/GodsScion

# version:    26.01.20.5.08
# '''


###################################################### APPLICATION INPUTS ######################################################


# >>>>>>>>>>> Easy Apply Questions & Inputs <<<<<<<<<<<

# Give an relative path of your default resume to be uploaded. If file in not found, will continue using your previously uploaded resume in LinkedIn.
default_resume_path = ""      # (In Development)

# What do you want to answer for questions that ask about years of experience you have, this is different from current_experience? 
years_of_experience = "15"          # A number in quotes Eg: "0","1","2","3","4", etc.

# Do you need visa sponsorship now or in future?
require_visa = "Yes"               # "Yes" or "No"

# What is the link to your portfolio website, leave it empty as "", if you want to leave this question unanswered
website = ""                        # "www.example.bio" or "" and so on....

# Please provide the link to your LinkedIn profile.
linkedIn = "https://www.linkedin.com/in/saidi-reddy-morthala-3a72b3110/"       # "https://www.linkedin.com/in/example" or "" and so on...

# What is the status of your citizenship? # If left empty as "", tool will not answer the question. However, note that some companies make it compulsory to be answered
# Valid options are: "U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident" or "Other"
us_citizenship = "Non-citizen seeking work authorization"



## SOME ANNOYING QUESTIONS BY COMPANIES 🫠 ##

# What to enter in your desired salary question (American and European), What is your expected CTC (South Asian and others)?, only enter in numbers as some companies only allow numbers,
desired_salary = 40000          # 80000, 90000, 100000 or 120000 and so on... Do NOT use quotes
# '''
# Note: If question has the word "lakhs" in it (Example: What is your expected CTC in lakhs), 
# then it will add '.' before last 5 digits and answer. Examples: 
# * 2400000 will be answered as "24.00"
# * 850000 will be answered as "8.50"
# And if asked in months, then it will divide by 12 and answer. Examples:
# * 2400000 will be answered as "200000"
# * 850000 will be answered as "70833"
# '''

# What is your current CTC? Some companies make it compulsory to be answered in numbers...
current_ctc = 30000            # 800000, 900000, 1000000 or 1200000 and so on... Do NOT use quotes
# '''
# Note: If question has the word "lakhs" in it (Example: What is your current CTC in lakhs), 
# then it will add '.' before last 5 digits and answer. Examples: 
# * 2400000 will be answered as "24.00"
# * 850000 will be answered as "8.50"
# # And if asked in months, then it will divide by 12 and answer. Examples:
# # * 2400000 will be answered as "200000"
# # * 850000 will be answered as "70833"
# '''

# (In Development) # Currency of salaries you mentioned. Companies that allow string inputs will add this tag to the end of numbers. Eg: 
# currency = "INR"                 # "USD", "INR", "EUR", etc.

# What is your notice period in days?
notice_period = 60                   # Any number >= 0 without quotes. Eg: 0, 7, 15, 30, 45, etc.
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
linkedin_headline = "Enterprise Cloud Architect | AWS & Azure | Multi-Cloud Architecture | Cloud Transformation | Security & Governance | Kubernetes | Terraform | Financial Services" # "Headline" or "" to leave this question unanswered

# Your summary in quotes, use \n to add line breaks if using single quotes "Summary".You can skip \n if using triple quotes """Summary"""
linkedin_summary = """
Enterprise Cloud Architect with 15+ years of experience designing, implementing, and governing scalable, secure, and highly available cloud platforms across AWS and Microsoft Azure. Experienced in enterprise cloud transformation, multi-cloud architecture, cloud migration, infrastructure modernization, and building cloud operating models for large-scale environments.

Strong expertise in AWS and Azure services including AWS Organizations, Control Tower, Landing Zones, IAM Identity Center, VPC, Transit Gateway, CloudFront, WAF, EC2, EKS, ECS, RDS, Aurora, S3, Lambda, Azure Virtual Networks, Azure Kubernetes Service, and Azure governance frameworks.

Proven experience in designing enterprise-grade architectures aligned with AWS Well-Architected Framework, Azure Cloud Adoption Framework, security best practices, compliance requirements, and cost optimization strategies. Skilled in implementing cloud governance, security controls, identity management, networking, disaster recovery, high availability, and multi-region active-active architectures.

Hands-on experience with Infrastructure as Code and DevOps automation using Terraform, CloudFormation, CI/CD pipelines, GitHub, Bitbucket, Harness, and container platforms including Kubernetes and Amazon EKS. Experienced in building scalable cloud platforms, observability solutions, automation frameworks, and operational excellence practices.

Specialized in financial services and enterprise environments, delivering secure cloud solutions while balancing business requirements, performance, reliability, and cost efficiency.

Key Skills:
• Enterprise Cloud Architecture
• AWS & Azure Multi-Cloud Solutions
• Cloud Migration & Modernization
• Cloud Governance & Landing Zones
• AWS Control Tower & Azure Governance
• Security Architecture & Compliance
• Kubernetes & Container Platforms
• Terraform & Infrastructure Automation
• DevOps & CI/CD Transformation
• Disaster Recovery & High Availability
• Cost Optimization & Cloud FinOps
• Platform Engineering

Passionate about designing future-ready cloud platforms, enabling digital transformation, and helping organizations achieve secure, scalable, and resilient cloud adoption.
"""


'''
Note: If left empty as "", the tool will not answer the question. However, note that some companies make it compulsory to be answered. Use \n to add line breaks.
''' 

# Your cover letter in quotes, use \n to add line breaks if using single quotes "Cover Letter".You can skip \n if using triple quotes """Cover Letter""" (This question makes sense though)
cover_letter = """
Dear Hiring Manager,

I am excited to apply for the Cloud Architect position. I am an Enterprise Cloud Architect with 15+ years of IT experience, specializing in AWS, Microsoft Azure, multi-cloud architecture, cloud transformation, and enterprise platform engineering.

I have extensive experience designing and implementing secure, scalable, and highly available cloud solutions across AWS and Azure environments. My expertise includes cloud migration, enterprise landing zones, cloud governance, security architecture, networking, disaster recovery, cost optimization, and operational excellence aligned with industry best practices such as AWS Well-Architected Framework and Azure Cloud Adoption Framework.

I have hands-on experience with AWS services including AWS Organizations, Control Tower, IAM Identity Center, VPC, Transit Gateway, EC2, EKS, ECS, RDS, Aurora, S3, CloudFront, WAF, and Lambda, along with Azure services including Azure Kubernetes Service, Virtual Networks, and governance solutions. I also have strong experience with Infrastructure as Code and DevOps automation using Terraform, CloudFormation, CI/CD pipelines, GitHub, Bitbucket, and Kubernetes.

Throughout my career, I have worked with enterprise and financial services environments, delivering cloud solutions that improve scalability, security, reliability, and business agility. I have successfully led cloud modernization initiatives, implemented governance frameworks, optimized cloud costs, and supported mission-critical production platforms.

I am passionate about helping organizations accelerate cloud adoption through secure, innovative, and resilient architectures. I believe my experience in multi-cloud strategy, cloud governance, automation, and platform engineering would add significant value to your organization.

I would welcome the opportunity to discuss how my skills and experience align with your cloud architecture requirements.

Thank you for your consideration.

Best regards,
Saidi Reddy Morthala
+971 - 52 641 74 75 \ +91- 9985 66 66 51
"""
##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------

# Your user_information_all letter in quotes, use \n to add line breaks if using single quotes "user_information_all".You can skip \n if using triple quotes """user_information_all""" (This question makes sense though)
# We use this to pass to AI to generate answer from information , Assuing Information contians eg: resume  all the information like name, experience, skills, Country, any illness etc. 
user_information_all ="""
User Information
"""
##<
'''
Note: If left empty as "", the tool will not answer the question. However, note that some companies make it compulsory to be answered. Use \n to add line breaks.
''' 

# Name of your most recent employer
recent_employer = "Avrioc Technologies LLC" # "", "Lala Company", "Google", "Snowflake", "Databricks"

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
