##> ------ Tim Lor : tulxoro - Feature ------
import requests
import json
from config.secrets import *
from config.settings import showAiErrorAlerts
from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *

from typing import Literal, Union, Optional

def ollama_create_client():
    '''
    Creates an Ollama client using the native Ollama API.
    * Returns a client object configured for Ollama
    '''
    try:
        print_lg("Creating Ollama client...")
        if not use_AI:
            raise ValueError("AI is not enabled! Please enable it by setting `use_AI = True` in `secrets.py` in `config` folder.")
        
        base_url = llm_api_url
        
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        
        # Test connection to Ollama
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Ollama server not responding properly. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Cannot connect to Ollama server at {base_url}. Make sure Ollama is running.")
        
        print_lg("---- SUCCESSFULLY CREATED OLLAMA CLIENT! ----")
        print_lg(f"Using API URL: {base_url}")
        print_lg(f"Using Model: {llm_model}")
        print_lg("Check './config/secrets.py' for more details.\n")
        print_lg("---------------------------------------------")
        
        return {"base_url": base_url, "model": llm_model}
    except Exception as e:
        error_message = f"Error occurred while creating Ollama client. Make sure your API connection details are correct."
        critical_error_log(error_message, e)
        if showAiErrorAlerts:
            print_lg(f"{error_message}\n{str(e)}")
        return None

def ollama_completion(client, messages: list[dict], response_format: Optional[dict] = None, temperature: float = 0, stream: bool = stream_output) -> Union[str, dict]:
    '''
    Completes a chat using Ollama API and formats the results.
    * Takes in `client` - The Ollama client
    * Takes in `messages` of type `list[dict]` - The conversation messages
    * Takes in `response_format` of type `dict` for JSON representation (optional)
    * Takes in `temperature` of type `float` for randomness control (default 0)
    * Takes in `stream` of type `bool` for streaming output (optional)
    * Returns the response as text or JSON
    '''
    if not client: 
        raise ValueError("Ollama client is not available!")

    # Convert OpenAI format messages to Ollama format
    prompt = ""
    for message in messages:
        if message["role"] == "user":
            prompt += message["content"] + "\n"
        elif message["role"] == "assistant":
            prompt += "Assistant: " + message["content"] + "\n"
        elif message["role"] == "system":
            prompt = message["content"] + "\n\n" + prompt

    # Set up parameters for the API call
    params = {
        "model": client["model"],
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": temperature if temperature > 0 else 0.1
        }
    }

    try:
        # Make the API call
        print_lg(f"Calling Ollama API for completion...")
        print_lg(f"Using model: {client['model']}")
        print_lg(f"Message count: {len(messages)}")
        
        response = requests.post(
            f"{client['base_url']}/api/generate",
            json=params,
            timeout=60,
            stream=stream
        )

        if response.status_code != 200:
            raise ValueError(f"Ollama API error: {response.status_code} - {response.text}")

        result = ""
        
        # Process the response
        if stream:
            print_lg("--STREAMING STARTED")
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        chunk = data["response"]
                        result += chunk
                        print_lg(chunk, end="", flush=True)
                    if data.get("done", False):
                        break
            print_lg("\n--STREAMING COMPLETE")
        else:
            data = response.json()
            result = data.get("response", "")
        
        # Convert to JSON if needed
        if response_format:
            result = convert_to_json(result)
        
        print_lg("\nOllama Answer:\n")
        print_lg(result, pretty=response_format is not None)
        return result
    except Exception as e:
        error_message = f"Ollama API error: {str(e)}"
        print_lg(f"Full error details: {e.__class__.__name__}: {str(e)}")
        
        # If it's a connection or authentication error, provide more specific guidance
        if "Connection" in str(e):
            print_lg("This might be a network issue. Please check your internet connection.")
            print_lg("Make sure Ollama is running on your local machine.")
            print_lg("You can start Ollama by running 'ollama serve' in your terminal.")
        elif "404" in str(e):
            print_lg("The requested resource could not be found. The API URL or model name might be incorrect.")
            print_lg("Make sure the model is pulled in Ollama. Run 'ollama pull qwen3' to download the model.")
        elif "500" in str(e):
            print_lg("Internal server error. The model might not be loaded properly.")
            print_lg("Try restarting Ollama: 'ollama serve'")
            
        raise ValueError(error_message)

def ollama_extract_skills(client, job_description: str, stream: bool = stream_output) -> dict:
    '''
    Function to extract skills from job description using Ollama API.
    * Takes in `client` - The Ollama client
    * Takes in `job_description` of type `str` - The job description text
    * Takes in `stream` of type `bool` to indicate if it's a streaming call
    * Returns a `dict` object representing JSON response
    '''
    try:
        print_lg("Extracting skills from job description using Ollama...")
        
        # Using optimized prompt for Ollama
        prompt = extract_skills_prompt.format(job_description)
        messages = [{"role": "user", "content": prompt}]
        
        # Call Ollama completion
        result = ollama_completion(
            client=client,
            messages=messages,
            stream=stream
        )
        
        # Ensure the result is a dictionary
        if isinstance(result, str):
            result = convert_to_json(result)
            
        return result
    except Exception as e:
        critical_error_log("Error occurred while extracting skills with Ollama!", e)
        return {"error": str(e)}

def ollama_answer_question(
    client, 
    question: str, options: Optional[list[str]] = None, 
    question_type: Literal['text', 'textarea', 'single_select', 'multiple_select'] = 'text', 
    job_description: Optional[str] = None, about_company: Optional[str] = None, user_information_all: Optional[str] = None,
    stream: bool = stream_output
) -> Union[str, dict]:
    '''
    Function to answer a question using Ollama AI.
    * Takes in `client` - The Ollama client
    * Takes in `question` of type `str` - The question to answer
    * Takes in `options` of type `list[str] | None` - Options for select questions
    * Takes in `question_type` - Type of question (text, textarea, single_select, multiple_select)
    * Takes in optional context parameters - job_description, about_company, user_information_all
    * Takes in `stream` of type `bool` - Whether to stream the output
    * Returns the AI's answer
    '''
    try:
        print_lg(f"Answering question using Ollama AI: {question}")
        
        # Prepare user information
        user_info = user_information_all or ""
        
        # Prepare prompt based on question type
        prompt = ai_answer_prompt.format(user_info, question)
        
        # Add options to the prompt if available
        if options and (question_type in ['single_select', 'multiple_select']):
            options_str = "OPTIONS:\n" + "\n".join([f"- {option}" for option in options])
            prompt += f"\n\n{options_str}"
            
            if question_type == 'single_select':
                prompt += "\n\nPlease select exactly ONE option from the list above."
            else:
                prompt += "\n\nYou may select MULTIPLE options from the list above if appropriate."
        
        # Add job details for context if available
        if job_description:
            prompt += f"\n\nJOB DESCRIPTION:\n{job_description}"
        
        if about_company:
            prompt += f"\n\nABOUT COMPANY:\n{about_company}"
        
        messages = [{"role": "user", "content": prompt}]
        
        # Call Ollama completion
        result = ollama_completion(
            client=client,
            messages=messages,
            temperature=0.1,  # Slight randomness for more natural responses
            stream=stream
        )
        
        return result
    except Exception as e:
        critical_error_log("Error occurred while answering question with Ollama!", e)
        return {"error": str(e)} 
##<