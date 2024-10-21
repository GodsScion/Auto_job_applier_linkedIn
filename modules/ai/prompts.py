"""
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

"""

extract_skills_prompt = """
You are a job requirements extractor, your job is to extract all the skills given in the job description. Skills must be classified into 
1. "tech_stack" - All skills mentioned for ideal candidates. Examples: Python, React.js, Node.js, Elastic Search, Algolia, MongoDB, Spring Boot, .NET, etc.
2. "technical_skills" - Examples: System Architecture, Data Engineering, System Design, Micro Services, Distributed Systems, etc.
3. "other_skills" - Examples: Communication skills, Managerial roles, Cross-team collaborations, etc. 
4. "nice_to_have" - All skills mentioned in Nice to have.
Return the output in JSON format given below, without any preamble or explanation
JSON format: {{
    "tech_stack": [ ],
    "technical_skills": [ ],
    "other_skills": [ ],
    "nice_to_have": [ ]
}}

JOB DESCRIPTION:
{}
"""
"""
Use `extract_skills_prompt.format(job_description)` to insert `job_description`.
"""
