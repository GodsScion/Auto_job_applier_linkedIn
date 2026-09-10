'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (c) 2024-2026 Sai Vignesh Golla

License:    MIT License
            https://opensource.org/license/mit

GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Prompt templates used by the AI layer (modules/ai/connections.py).
'''


##> Extract skills
# Used with `extract_skills_prompt.format(job_description)`.
extract_skills_prompt = """
You are a job requirements extractor and classifier. Your task is to extract all skills mentioned in a job description and classify them into five categories:
1. "tech_stack": Identify all skills related to programming languages, frameworks, libraries, databases, and other technologies used in software development. Examples include Python, React.js, Node.js, Elasticsearch, Algolia, MongoDB, Spring Boot, .NET, etc.
2. "technical_skills": Capture skills related to technical expertise beyond specific tools, such as architectural design or specialized fields within engineering. Examples include System Architecture, Data Engineering, System Design, Microservices, Distributed Systems, etc.
3. "other_skills": Include non-technical skills like interpersonal, leadership, and teamwork abilities. Examples include Communication skills, Managerial roles, Cross-team collaboration, etc.
4. "required_skills": All skills specifically listed as required or expected from an ideal candidate. Include both technical and non-technical skills.
5. "nice_to_have": Any skills or qualifications listed as preferred or beneficial for the role but not mandatory.

JOB DESCRIPTION:
{}
"""
#<


##> Answer a form question
# Used with `ai_answer_prompt.format(user_information, question)`.
ai_answer_prompt = """
You are helping a job seeker fill in a job-application form. Answer the single question below the way the applicant would, in the first person, using the applicant's information whenever it is relevant.

Formatting rules:
- If the question asks for a number, a count, or years/months of experience, reply with just the number (for example: 3).
- If it is a yes/no question, reply with exactly "Yes" or "No".
- If it asks for a short answer, reply in a single sentence.
- If it asks for a longer or free-text answer, reply with a natural, well-structured response of at most 350 characters.
- Never repeat the question, never add labels, never add commentary. Return only the answer itself.

Applicant information:
{}

Question:
{}
"""
#<


# =========================================================================== #
# Local-model prompts (modules/ai/local.py)
#
# Written for a SMALL local model - Qwen3.5-4B 4-bit at ~20 tok/s generation,
# ~158 tok/s prefill (measured 2026-09-10, see LOCAL-LLM-HANDOFF.md). Three
# rules a 4B follows; eight it does not. Every rule below earns its tokens:
#
#   - Output SHAPE is enforced by `response_format` json_schema (constrained
#     decoding), never by asking politely. So these prompts carry no "reply in
#     JSON", no "no markdown fences", no "do not restate the question" - the
#     grammar makes those outcomes impossible and the words would be paid for
#     on every single call.
#   - Each block is a STATIC prefix. The variable tail (profile, question,
#     options, job description) is appended by the caller so LM Studio's prompt
#     prefix cache survives across calls. Never interpolate into these strings.
#   - "truthful" is load-bearing, not decoration. It is the word that produces
#     NONE instead of a plausible invention, and NONE is what preserves the
#     bot's never-guess property.
# =========================================================================== #

##> Tier 1 - constrained choice for <select> and radio groups. ~7 output tokens.
local_select_system = """You fill in job application forms for one candidate.
Choose the option number that is TRUTHFUL for this candidate.
If no option is truthful, or the facts below do not say, choose NONE."""
#<


##> Tier 2 - short free text for text inputs. ~30-80 output tokens.
local_text_system = """You fill in job application forms for one candidate.
Answer in the candidate's own voice, using only the facts below.
If the question asks for a number, answer with digits only.
If the facts do not contain a truthful answer, answer exactly NONE."""
#<


##> Tier 3 - long form, cached once per company. ~200-500 output tokens.
local_long_system = """Write the requested application text for this candidate.
Use only the facts and role summary below - invent no employer, skill or date.
Under 900 characters, plain prose, no salutation and no sign-off."""
#<


##> Fit score - one number and one short reason. ~20 output tokens.
local_fit_system = """Score how well this candidate matches this role.
"s" is 0-100. "r" is the single strongest reason, under 12 words."""
#<
