"""
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.3.10.30
"""


##> Common Response Formats
array_of_strings = {"type": "array", "items": {"type": "string"}}
"""
Response schema to represent array of strings `["string1", "string2"]`
"""
#<


##> Extract Skills

# Structure of messages = `[{"role": "user", "content": extract_skills_prompt}]`

extract_skills_prompt = """
You are a job requirements extractor and classifier. Your task is to extract all skills mentioned in a job description and classify them into five categories:
1. "tech_stack": Identify all skills related to programming languages, frameworks, libraries, databases, and other technologies used in software development. Examples include Python, React.js, Node.js, Elasticsearch, Algolia, MongoDB, Spring Boot, .NET, etc.
2. "technical_skills": Capture skills related to technical expertise beyond specific tools, such as architectural design or specialized fields within engineering. Examples include System Architecture, Data Engineering, System Design, Microservices, Distributed Systems, etc.
3. "other_skills": Include non-technical skills like interpersonal, leadership, and teamwork abilities. Examples include Communication skills, Managerial roles, Cross-team collaboration, etc.
4. "required_skills": All skills specifically listed as required or expected from an ideal candidate. Include both technical and non-technical skills.
5. "nice_to_have": Any skills or qualifications listed as preferred or beneficial for the role but not mandatory.
Return the output in the following JSON format with no additional commentary:
{{
    "tech_stack": [],
    "technical_skills": [],
    "other_skills": [],
    "required_skills": [],
    "nice_to_have": []
}}

JOB DESCRIPTION:
{}
"""
"""
Use `extract_skills_prompt.format(job_description)` to insert `job_description`.
"""


extract_skills_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "Skills_Extraction_Response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "tech_stack": array_of_strings,
                "technical_skills": array_of_strings,
                "other_skills": array_of_strings,
                "required_skills": array_of_strings,
                "nice_to_have": array_of_strings,
            },
            "required": [
                "tech_stack",
                "technical_skills",
                "other_skills",
                "required_skills",
                "nice_to_have",
            ],
            "additionalProperties": False
        },
    },
}
"""
Response schema for `extract_skills` function
"""
#<


##> Answer Questions
# Structure of messages = `[{"role": "user", "content": answer_questions_prompt}]`

text_questions_prompt = """
Please answer the following job application question, with no additional commentary, based on the context provided.
Question:
{}
User Info:
{}
"""
#<