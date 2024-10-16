from config.secrets import *
from modules.helpers import print_lg
from openai import OpenAI
import json


def extract_skills(client: OpenAI, job_description: str, stream: bool = False) -> dict:
    try:
        prompt = f'''
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
{job_description}
'''
        
        print(prompt)

        job_description # f"Extract skills from the following job description: {job_description}"

        completion = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            stream=stream
        )


        if completion.model_extra and completion.model_extra.get("error"):
            raise ValueError(f'Error occurred: "{completion.model_extra.get("error")}"')

        if completion.model_extra and completion.model_extra.get("function variables"): 
            variables = completion.model_extra["function variables"]
            if variables.get("error"):
                return {"error": variables["error"]}
        result = ""
        # if stream:
        #     for chunk in completion.stream():
        #         result += chunk['choices'][0]['delta'].get('content', '')  # Concatenate the response
        # else:
        #     result = completion.choices[0].message.content

        print("Extracting skills...")
        print(completion)

        # Parse the result as JSON, if applicable
        try:
            result_json = json.loads(result)
            return result_json
        except json.JSONDecodeError:
            return {"error": "Unable to parse the response as JSON", "response": result}
    except Exception as e:
        print_lg(e)
