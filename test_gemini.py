
# REQUIRED IMPORTS
from datetime import datetime
from modules.ai.geminiConnections import *
from modules.helpers import print_lg

#< Global Variables and logics

job_description = """
About the job
Software Engineering Specialist:

Required Skills & Experience

• Bachelor’s Degree and 4 years of working experience, or Master's Degree with 2 years of experience, or minimum 8 years of experience with no degree

• TS/SCI Clearance

• Experience with backend development of multi-process/multi-thread environments

• Experience working in a scrum environment

• Experience with TCP/IP network protocols

• Experience using complex data structures via various methods of storage/access

• Experience with C/C++ or Java

• Experience with Object Oriented Programming (OOP)

• Experience with research, designing, development, testing and maintaining complex software systems

• Experience developing and testing Linux

• Experience with containers, shell scripts, and system service

Nice to Have Skills & Experience

• Experience with Google Protocol Buffer (GPB) data sterilization • Iterative software development process experience (Agile, SCRUM, Kanban) • Experience with DevSecOps, including CI/CD pipelines (Jenkins, GitLab, Artifactory)

Job Description

An employer in the Greenville, TX market is looking for a Software Engineering Specialist to join their team. This person will be responsible for research, design, implementation, development, testing and maintaining multi-tier architectures to configure and manage Mission Communications Systems equipment. This person will analyze design tradeoffs against scope, cost, and schedule constraints. This person will also analyze requirements to determine feasibility of design. This person will also perform coding and unit test of resultant software. This person will also perform software component integration.

Direct Placement Roles:

Compensation:

____60____ to 70 per year annual salary.

Exact compensation may vary based on several factors, including skills, experience, and education.

"""

def main() -> None:
    model = gemini_create_client()
    if model:
        gemini_extract_skills(model, job_description)
        
        # Example for answering a question
        question = "What are the required skills for this role?"
        gemini_answer_question(model, question, job_description=job_description)


if __name__ == "__main__":
    print_lg("######################### GEMINI TEST SCRIPT STARTED #########################")
    print_lg(f"Date and Time: {datetime.now()}")
    print_lg("_______________________________________________________________________")
    try:
        main()
    except Exception as e:
        print_lg("_______________________________________________________________________")
        print_lg(f"Exception occurred: {e}")
    finally:
        print_lg("######################### GEMINI TEST SCRIPT COMPLETED #########################")
