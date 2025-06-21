'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.3.10.30
'''


###################################################### CONFIGURE YOUR TOOLS HERE ######################################################


# Login Credentials for LinkedIn (Optional)
username = "username@example.com"       # Enter your username in the quotes
password = "example_password"           # Enter your password in the quotes


## Artificial Intelligence (Beta Not-Recommended)
# Use AI
##> ------ Tim Lor : tulxoro - Documentation ------
use_AI = True                          # True or False, Note: True or False are case-sensitive
'''
Note: Set it as True only if you want to use AI, and If you either have a
1. Local LLM model running on your local machine, with it's APIs exposed. Note that only Ollama seems to be supported. Example softwares to achieve it are:
    a. Ollama - https://ollama.com/
    b. llama.cpp - https://github.com/ggerganov/llama.cpp
    c. LM Studio - https://lmstudio.ai/ (Recommended)
    d. Jan - https://jan.ai/
2. OR you have a valid OpenAI API Key, and money to spare, and you don't mind spending it.
CHECK THE OPENAI API PIRCES AT THEIR WEBSITE (https://openai.com/api/pricing/). 
'''
##<

##> ------ Yang Li : MARKYangL - Feature ------
##> ------ Tim Lor : tulxoro - Cleanup & Documentation ------
# REMOVED: unnecessary extra variables for DeepSeek models (use llm instead)

# Select AI Provider
ai_provider = "openai"               # "openai", "deepseek"
'''
Note: Select your AI provider.
* "openai" - OpenAI API (GPT models)
* "deepseek" - DeepSeek API (DeepSeek models)
* "ollama" - Ollama API (Ollama API)
'''
##<

# Your Local LLM url or other AI api url and port
llm_api_url = "http://localhost:11434"       # Examples: "https://api.openai.com/v1/", "http://127.0.0.1:1234/v1/", "http://localhost:1234/v1/"
'''
Note: Don't forget to add / at the end of your url.
If you are using deepseek, this URL is compatible with OpenAI interface. The full endpoint will be {deepseek_api_url}/chat/completions.
'''

# Your Local LLM API key or other AI API key 
llm_api_key = ""              # Enter your API key in the quotes, make sure it's valid, if not will result in error.
'''
Note: Leave it empyt as "" or "not-needed" if not needed. Else will result in error!
'''

# Your local LLM model name or other AI model name
llm_model = "deepseek-llm"          # Examples: "gpt-3.5-turbo", "gpt-4o", "llama-3.2-3b-instruct"
'''
Note: If using DeekSeek API, use DeepSeek's model selection
* "deepseek-chat" - DeepSeek-V3, general conversation model
* "deepseek-reasoner" - DeepSeek-R1, reasoning model
'''


#
llm_spec = "openai"                # Examples: "openai", "openai-like", "openai-like-github", "openai-like-mistral"
'''
Note: Currently "openai" and "openai-like" api endpoints are supported.
If you don't know what this means then just leave it as is.
'''
##<

# # Yor local embedding model name or other AI Embedding model name
# llm_embedding_model = "nomic-embed-text-v1.5"

# Do you want to stream AI output?
stream_output = False                    # Examples: True or False. (False is recommended for performance, True is recommended for user experience!)
'''
Set `stream_output = True` if you want to stream AI output or `stream_output = False` if not.
'''
##




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