'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

'''


# Imports
from modules.ai.openai import *

#< Global Variables and logics


def main() -> None:
    client = client = OpenAI(base_url="http://127.0.0.1:6000/", api_key=llm_api_key)
    result = extract_skills(client, "Hi, what can you do?")


if __name__ == "__main__":
    main()
