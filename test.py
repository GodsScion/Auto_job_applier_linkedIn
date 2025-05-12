'''
Author:     Sai Vignesh Golla and Alexander James
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

contributor:    Alexander James
LinkedIn:       https://www.linkedin.com/in/alexander-james-170797175/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

'''


# REQUIRED IMPORTS
from datetime import datetime
#from modules.ai.openaiConnections import print_lg
from modules.helpers import print_lg

# TEST RELATED IMPORTS
from modules.ai.openaiConnections import ai_create_openai_client, ai_extract_skills, ai_close_openai_client
from modules.ai.deepseekConnections import deepseek_create_client, deepseek_extract_skills
from pprint import pprint

# Import the AI provider setting from config
try:
    from config.secrets import ai_provider
except ImportError:
    # Default to OpenAI if config not available
    ai_provider = "openai"
    print_lg("Warning: Could not import ai_provider from config.secrets, defaulting to OpenAI")

#< Global Variables and logics

job_description = """
About the job
Software Engineering Specialist:

Required Skills & Experience

• Bachelor's Degree and 4 years of working experience, or Master's Degree with 2 years of experience, or minimum 8 years of experience with no degree

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
    client = None
    try:
        print_lg(f"Using AI provider: {ai_provider}")
        
        # Initialize client based on provider
        if ai_provider.lower() == "openai":
            client = ai_create_openai_client()
            skills = ai_extract_skills(client, job_description)
            print_lg(f"Extracted skills using OpenAI: {skills}")
            ai_close_openai_client(client)
        elif ai_provider.lower() == "deepseek":
            client = deepseek_create_client()
            skills = deepseek_extract_skills(client, job_description)
            print_lg(f"Extracted skills using DeepSeek: {skills}")
            # Close client if needed
            if hasattr(client, "close"):
                client.close()
        else:
            print_lg(f"Unknown AI provider: {ai_provider}. Supported providers are: openai, deepseek")
    except Exception as e:
        print_lg(f"Error with {ai_provider} AI processing: {e}")
    finally:
        # Ensure client is closed if it exists and has a close method
        if client and hasattr(client, "close") and callable(getattr(client, "close")):
            try:
                client.close()
            except Exception:
                pass


if __name__ == "__main__":
    print_lg("######################### TEST SCRIPT STARTED #########################")
    print_lg(f"Date and Time: {datetime.now()}")
    print_lg("_______________________________________________________________________")
    try:
        main()
    except Exception as e:
        print_lg("_______________________________________________________________________")
        print_lg(f"Exception occurred: {e}")
    finally:
        print_lg("######################### TEST SCRIPT COMPLETED #########################")
