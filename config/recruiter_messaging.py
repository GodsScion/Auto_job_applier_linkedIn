'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    26.01.18.22.50

Contributor: Sanjay Nainwal (sanjaynainwal129@gmail.com) - Feature: Recruiter Messaging
'''


###################################################### RECRUITER MESSAGING CONFIGURATION ######################################################


# Enable recruiter messaging feature
enable_recruiter_messaging = True          # True or False, Note: True or False are case-sensitive


# \u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e Message Sending Preferences \u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c

# Maximum messages to send per day (no InMail cost, so can send more)
max_messages_per_day = 500              # Only Non Negative Integers Eg: 10, 20, 50, 100

# Delay between messages in seconds (to avoid spam detection)
message_delay_seconds = 1             # Only Non Negative Integers Eg: 15, 30, 45, 60

# Skip messaging if already applied to job via Easy Apply?
skip_if_already_applied = False         # True or False, Note: True or False are case-sensitive

# Messaging Only Mode - Skip Easy Apply and only message recruiters?
messaging_only_mode = False            # True or False, Note: True or False are case-sensitive
'''
Set to True if you want to ONLY message recruiters without applying via Easy Apply.
This is useful when you want to focus on direct recruiter outreach.
Note: When True, the bot will:
- Search for jobs
- Message recruiters (if they accept free messages)
- Skip all Easy Apply applications
'''



# \u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e InMail Preservation (CRITICAL) \u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c

# Only message recruiters who accept free messages from anyone (preserves InMail credits)
only_free_messages = True              # True or False, Note: True or False are case-sensitive

# Skip recruiters who require InMail (preserves your LinkedIn Premium InMail credits)
skip_inmail_required = True            # True or False, Note: True or False are case-sensitive


# \u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e Message Templates \u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c

# Message subject line (supports variables: {job_title}, {company_name}, {recruiter_name})
message_subject = "Interested in {job_title} position at {company_name}"

# Message body template (supports multiple variables, see below)
message_template = """Hello {recruiter_name},

I came across the {job_title} position at {company_name} and I'm very interested in this opportunity.

{personalized_intro}

With {years_of_experience} years of experience in backend development, I believe I would be a strong fit for this role. I've worked extensively with Java, Spring Boot, and distributed systems at scale.

{why_interested}

I would love to discuss how my background aligns with your needs. Here are my details:

Resume: https://drive.google.com/file/d/1kLdZWzTeRAAm4QtWrv2UQjHJ-H5ADOgd/view?usp=sharing
LinkedIn: https://www.linkedin.com/in/sanjay-nainwal/
Portfolio: https://sanjaynainwal.vercel.app/
Phone: +91 9720423975

Job Listing: {job_link}

Best regards,
{your_name}
"""

'''
Available template variables:
- {recruiter_name}: Recruiter's first name or full name
- {job_title}: Title of the job posting
- {company_name}: Company name
- {job_link}: Direct link to the job posting
- {your_name}: Your name from personals.py
- {years_of_experience}: Your experience from questions.py
- {personalized_intro}: AI-generated personalized introduction (if AI enabled)
- {why_interested}: AI-generated reason for interest (if AI enabled)
- {key_skills}: Your relevant skills from profile
'''


# \u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e AI-Powered Personalization \u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c

# Use AI to personalize messages based on job description?
use_ai_for_messages = True             # True or False, Note: True or False are case-sensitive

# Level of AI personalization
ai_personalization_level = "high"      # "low", "medium", "high"
'''
- "low": Basic job title and company name insertion
- "medium": Add relevant skills matching from job description
- "high": Full personalization with job-specific intro and interest explanation
'''


# \u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e Message History Tracking \u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c

# File to track all sent messages (prevents duplicates)
message_history_file = "all excels/recruiter_messages_history.csv"


# \u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e\u003e Testing and Safety \u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c\u003c

# Dry run mode - generate messages but don't actually send them (for testing)
dry_run_mode = False                   # True or False, Note: True or False are case-sensitive


# AI Skill Extraction Config

# Enable AI skill extraction from job descriptions?
use_ai_skill_extraction = False         # True or False, Note: True or False are case-sensitive

# You can add more skill extraction settings here in the future



############################################################################################################
'''
THANK YOU for using this tool 😊! Wishing you the best in your job hunt 🙌🏻!

Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. Your support keeps this project alive.

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact.

Your support, whether through donations big or small or simply spreading the word, means the world to me and helps keep this project alive and thriving.

Gratefully yours 🙏🏻,
Sai Vignesh Golla
'''
############################################################################################################
