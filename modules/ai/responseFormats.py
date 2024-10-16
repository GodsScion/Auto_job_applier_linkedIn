"""
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

"""

array_of_strings = {"type": "array", "items": {"type": "string"}}
"""
Response schema to represent array of strings `["string1", "string2"]`
"""

extract_skills_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "Skills Extraction Response",
        "strict": "true",
        "schema": {
            "type": "object",
            "properties": {
                "tech_stack": array_of_strings,
                "technical_skills": array_of_strings,
                "other_skills": array_of_strings,
                "nice_to_have": array_of_strings,
            },
            "required": [
                "tech_stack",
                "technical_skills",
                "other_skills",
                "nice_to_have",
            ],
        },
    },
}
"""
Response schema for `extract_skills` function
"""
