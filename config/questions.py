'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''


###################################################### APPLICATION INPUTS ######################################################


# >>>>>>>>>>> Easy Apply Questions & Inputs <<<<<<<<<<<

# Give an relative path of your default resume to be uploaded. If file in not found, will continue using your previously uploaded resume in LinkedIn.
default_resume_path = "all resumes/default/resume.pdf"      # (In Development)

# What do you want to answer for questions that ask about years of experience you have, this is different from current_experience? 
years_of_experience = "2"          # A number in quotes Eg: "0","1","2","3","4", etc.

# Do you need visa sponsorship now or in future?
require_visa = "No"               # "Yes" or "No"

# What is the link to your portfolio website, leave it empty as "", if you want to leave this question unanswered
website = "aidankimberley.net"                        # "www.example.bio" or "" and so on....

# Please provide the link to your LinkedIn profile.
linkedIn = "https://www.linkedin.com/in/aidan-kimberley-36386221b/"       # "https://www.linkedin.com/in/example" or "" and so on...

# What is the status of your citizenship? # If left empty as "", tool will not answer the question. However, note that some companies make it compulsory to be answered
# Valid options are: "U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident" or "Other"
us_citizenship = "U.S. Citizen/Permanent Resident"



## SOME ANNOYING QUESTIONS BY COMPANIES 🫠 ##

# What to enter in your desired salary question (American and European), What is your expected CTC (South Asian and others)?, only enter in numbers as some companies only allow numbers,
desired_salary = 80000          # 80000, 90000, 100000 or 120000 and so on... Do NOT use quotes
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
current_ctc = 60000            # 800000, 900000, 1000000 or 1200000 and so on... Do NOT use quotes
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
notice_period = 30                   # Any number >= 0 without quotes. Eg: 0, 7, 15, 30, 45, etc.
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
linkedin_headline = "Mechanical Engineering student at McGill University" # "Headline" or "" to leave this question unanswered

# Your summary in quotes, use \n to add line breaks if using single quotes "Summary".You can skip \n if using triple quotes """Summary"""
linkedin_summary = """
Analytical and versatile engineering student at McGill University with experience in robotics R&D, data-driven problem solving, and cross-disciplinary collaboration. 
Adept at applying engineering principles, statistical analysis, and creative design to deliver high-impact solutions. Proven track record in research, leadership, and
technical execution, with work featured at the IEEE International Conference on Robotics and Automation. Seeking opportunities to leverage a blend of technical 
expertise and strategic thinking in engineering, consulting, or finance.
"""

'''
Note: If left empty as "", the tool will not answer the question. However, note that some companies make it compulsory to be answered. Use \n to add line breaks.
''' 

# Your cover letter in quotes, use \n to add line breaks if using single quotes "Cover Letter".You can skip \n if using triple quotes """Cover Letter""" (This question makes sense though)
# Leave this empty to enable AI-generated cover letters for each job
cover_letter = ""  # Leave empty for AI-generated cover letters
'''
Note: If left empty as "", the AI will generate a custom cover letter for each job based on the job description and your profile.
If you provide a static cover letter here, it will be used instead of AI generation.
'''
##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------

# Your user_information_all letter in quotes, use \n to add line breaks if using single quotes "user_information_all".You can skip \n if using triple quotes """user_information_all""" (This question makes sense though)
# We use this to pass to AI to generate answer from information , Assuing Information contians eg: resume  all the information like name, experience, skills, Country, any illness etc. 
user_information_all ="""
AIDAN L. KIMBERLEY
21 Mystic Ave Winchester MA, 01890 USA | aidanlkimberley@gmail.com | (612)-244-6031
US & Canadian Citizenship

Summary
Analytical and versatile engineering student at McGill University with experience in robotics R&D, data-driven problem solving, and cross-disciplinary collaboration. Adept at applying engineering principles, statistical analysis, and creative design to deliver high-impact solutions. Proven track record in research, leadership, and technical execution, with work featured at the IEEE International Conference on Robotics and Automation. Seeking opportunities to leverage a blend of technical expertise and strategic thinking in engineering, consulting, or finance.

Education
McGill University, Montreal, QC. expected graduation 2026
- Bachelor of Engineering, Mechanical Engineering | Minor, Applied Artificial Intelligence
- CGPA: 3.88/4 – Dean's Honor List (top 10% in Faculty of Engineering)
- Awards: SAG Conference Award Foundation Scholarship, for academic merit and leadership

Relevant coursework:
Statistics and Laboratory Measurement Numerical Methods in Mech Eng Principles of Manufacturing Analog and Digital Electronics
Machine Element Design Applied Machine Learning

Work Experience
Altec Research/Delsys, R&D Intern | Natick, MA | May 2025 - August 2025
- Validated cutting edge computer vision software with an injury prevention application
- Motion Capture data collection, processing, and analysis.

Mass General Hospital IHP, Research Intern | Boston, MA | January 2024 - August 2024
- Debugging and optimizing hardware and software for experimental protocols with TMS, and direct current stimulators such as paired associative stimulation and sensory threshold determination.
- Worked independently to solve the technical issues of the lab.
- Data analysis extracting meaningful insights out of noisy data using MATLAB.

Harvard Biodesign Lab, Undergraduate Research Fellow | Conor Walsh, PhD | Boston, MA | April 2022 - August 2023 (summer months)
- Worked on the mechanical design, fabrication, and testing of wearable ankle exoskeleton robots and pneumatic robotic control boxes.
- Made designs in Solidworks.
- Fabricated an ankle device and multiple robot control boxes using SLS + FDM 3D printing, electronics assembly, machining, and carbon fiber molding.
- Ran bench-top testing, using Matlab and Simulink to characterize device mechanical properties and iterated on designs to improve metrics such as mechanical advantage, frequency response, stiffness, part yield strength, device longevity, comfort, and adjustability.
- Ran on-body data collection using Qualysis to capture EMG, mocap, force plate, and internal sensing data.

McGill Formula Electric, Suspension team member | Montreal, CA | October 2022 - May 2023
- Used NX and Finite Element Analysis to design components for the carbon fiber decoupled suspension system of an electric race car.

Cycle Loft Bike Shop, Service Technician | Burlington, MA | May 2021- May 2022
- Built and repaired road, mountain, hybrid, and e-bikes; developed customer service and hands-on problem-solving skills.

Publication
Cooper, M., Canete, S., Eckert-Erdheim, A., Kimberley, A., Siviy, C., Baker, T., Ellis, T. D., Slade, P., & Walsh, C. J. (2024). Design & Systematic Evaluation of Power Transmission Efficiency of an Ankle Exoskeleton for Walking Post-Stroke. 2024 IEEE International Conference on Robotics and Automation (ICRA), 5526–5532.

Skills
Design & Fabrication
- Manufacturing: CNC, Carbon fiber molding, thermoforming, SLS/FDM 3D printing, MasterCAM
- CAD/FEA: SolidWorks, Siemens NX, AutoCAD, Abaqus
- Electronics Assembly: Soldering and cable fabrication

Analytics & Programming
- Programming/Automation: Python, Matlab, C, C++, Java, TypeScript
- Machine Learning: PyTorch, TensorFlow
- Simulation Tools: MATLAB, Simulink, Siemens NX
- Data processing/Statistical Analysis: Python, Excel, Matlab
- Motion Capture: Vicon, Qualisys

Management & Communication
- Technical writing & reporting
- Project coordination & team collaboration
- Presentation development and delivery
- Leadership roles in research and engineering teams

Other
Athletics: McGill XC Ski Team, mountain biking, running, weight lifting, rock climbing, MMA
Hobbies: Piano (jazz and classical), design prototyping
"""
##<

'''
Note: If left empty as "", the tool will not answer the question. However, note that some companies make it compulsory to be answered. Use \n to add line breaks.
''' 

# Name of your most recent employer
recent_employer = "Delsys" # "", "Lala Company", "Google", "Snowflake", "Databricks"

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