"""
Example configuration for questions.py
Copy this file to questions.py and fill in your details.
"""

default_resume_path = "all resumes/default/resume.pdf"

# >>>>>>>>>>> MULTI-RESUME SETTINGS <<<<<<<<<<<
# Map job title keywords to specific resume files. The bot checks in order — first keyword match wins.
# If no keywords match, falls back to default_resume_path above.
# Create your resume PDFs at the paths you specify below.
# Format: [(["keyword1", "keyword2", ...], "relative/path/to/resume.pdf"), ...]
#
# Examples:
#   (["Python", "ML Engineer", "Data Scientist"], "all resumes/python.pdf"),
#   (["Java", "Spring Boot", "Java Developer"], "all resumes/java.pdf"),
#   (["Frontend", "React", "UI Developer"], "all resumes/frontend.pdf"),
#
resume_rules = [
    (
        ["Example Role", "Example Title"],
        "all resumes/example.pdf",
    ),
]

years_of_experience = "0"
require_visa = "No"
website = ""
linkedIn = ""
us_citizenship = ""
desired_salary = 0
current_ctc = 0
notice_period = 30
linkedin_headline = ""
linkedin_summary = ""
cover_letter = ""
user_information_all = ""
recent_employer = ""
confidence_level = "5"
pause_before_submit = True
pause_at_failed_question = True
overwrite_previous_answers = False
