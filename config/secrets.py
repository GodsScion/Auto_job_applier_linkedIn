'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (c) 2024-2026 Sai Vignesh Golla

License:    MIT License
            https://opensource.org/license/mit
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    24.12.3.10.30
'''


###################################################### CONFIGURE YOUR TOOLS HERE ######################################################


# Login Credentials for LinkedIn (Optional)
username = "username@example.com"       # Enter your username in the quotes
password = "example_password"           # Enter your password in the quotes


## Artificial Intelligence (optional)
# Master switch. Turn AI on to let the tool draft answers to application questions
# and pull the required skills out of job descriptions. It needs either a paid API
# key or a local model server, so it stays off by default.
use_AI = False                           # True or False (case-sensitive)

# Which AI service to use. The tool reaches all of them through LangChain, so this
# one setting is usually all you change:
#   "openai" - OpenAI, or ANY OpenAI-compatible server (Ollama, LM Studio, vLLM,
#              DeepSeek, ...). Point llm_api_url at that server.
#   "gemini" - Google Gemini (uses your Google API key; llm_api_url is ignored).
# ("deepseek" also works and behaves like "openai".)
ai_provider = "openai"                    # "openai", "gemini", or "deepseek"

# The model name to use. Type whatever your provider offers, for example:
#   OpenAI:  "gpt-4o-mini", "gpt-4o", "gpt-5-mini"
#   Local:   "llama-3.2-3b-instruct", "qwen2.5:latest"
#   Gemini:  "gemini-2.5-flash", "gemini-2.5-pro"
llm_model = "gpt-4o-mini"

# Your API key. For local servers (Ollama / LM Studio) any placeholder is fine, so
# leave it as "not-needed". For OpenAI or Gemini, paste a real key.
llm_api_key = "not-needed"

# Base URL of your AI server. Only used by the "openai" provider family.
#   OpenAI:    "https://api.openai.com/v1/"
#   LM Studio: "http://localhost:1234/v1/"
#   Ollama:    "http://localhost:11434/v1/"
#   DeepSeek:  "https://api.deepseek.com/v1"
llm_api_url = "https://api.openai.com/v1/"

# Sampling temperature. Leave as None to use the model's own default (some newer
# models only allow their default). Set a number like 0 or 0.3 to override it.
llm_temperature = None




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

# --- Load user settings saved by the local control panel (user_config.json).
# --- No-op if that file is absent: values fall back to the defaults above.
from config import _overrides as _o
_o.apply(__name__, globals())
############################################################################################################