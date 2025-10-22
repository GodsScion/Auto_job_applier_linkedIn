##> ------ Yang Li : MARKYangL - Feature ------
from config.secrets import *
from config.settings import showAiErrorAlerts
from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *

from pyautogui import confirm
from openai import OpenAI
from openai.types.model import Model
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from typing import Iterator, Literal

def deepseek_create_client() -> OpenAI | None:
    '''
    Creates a DeepSeek client using the OpenAI compatible API.
    * Returns an OpenAI-compatible client configured for DeepSeek
    '''
    try:
        print_lg("Creating DeepSeek client...")
        if not use_AI:
            raise ValueError("AI is not enabled! Please enable it by setting `use_AI = True` in `secrets.py` in `config` folder.")
        
        ##> ------ Tim L : tulxoro - Refactor ------
        base_url = llm_api_url
        

        if base_url.endswith('/'):
            base_url = base_url[:-1]
        
        # Create client with DeepSeek endpoint
        client = OpenAI(base_url=base_url, api_key=llm_api_key)
        
        print_lg("---- SUCCESSFULLY CREATED DEEPSEEK CLIENT! ----")
        print_lg(f"Using API URL: {base_url}")
        print_lg(f"Using Model: {llm_model}")
        print_lg("Check './config/secrets.py' for more details.\n")
        print_lg("---------------------------------------------")
        ##<
        return client
    except Exception as e:
        error_message = f"Error occurred while creating DeepSeek client. Make sure your API connection details are correct."
        critical_error_log(error_message, e)
        if showAiErrorAlerts:
            if "Pause AI error alerts" == confirm(f"{error_message}\n{str(e)}", "DeepSeek Connection Error", ["Pause AI error alerts", "Okay Continue"]):
                showAiErrorAlerts = False
        return None

def deepseek_model_supports_temperature(model_name: str) -> bool:
    '''
    Checks if the specified DeepSeek model supports the temperature parameter.
    * Takes in `model_name` of type `str` - The name of the DeepSeek model
    * Returns `bool` - True if the model supports temperature adjustments
    '''
    # DeepSeek models that support temperature (all current models)
    deepseek_models = ["deepseek-chat", "deepseek-reasoner"]
    return model_name in deepseek_models

def deepseek_completion(client: OpenAI, messages: list[dict], response_format: dict = None, temperature: float = 0, stream: bool = stream_output) -> dict | ValueError:
    '''
    Completes a chat using DeepSeek API and formats the results.
    * Takes in `client` of type `OpenAI` - The DeepSeek client
    * Takes in `messages` of type `list[dict]` - The conversation messages
    * Takes in `response_format` of type `dict` for JSON representation (optional)
    * Takes in `temperature` of type `float` for randomness control (default 0)
    * Takes in `stream` of type `bool` for streaming output (optional)
    * Returns the response as text or JSON
    '''
    if not client: 
        raise ValueError("DeepSeek client is not available!")
    ##> ------ Tim L : tulxoro - Improvement ------
    # Set up parameters for the API call
    params = {
        
        "model": llm_model, 
   
        "messages": messages, 
        "stream": stream,
        "timeout": 30  
    }
    
    # Add temperature if supported
    if deepseek_model_supports_temperature(llm_model):
        params["temperature"] = temperature

    # Add response format if needed (DeepSeek uses OpenAI-compatible API)
    if response_format:
        params["response_format"] = response_format

    try:
        # Make the API call
        print_lg(f"Calling DeepSeek API for completion...")
        print_lg(f"Using model: {llm_model}")
        print_lg(f"Message count: {len(messages)}")
        completion = client.chat.completions.create(**params)
    ##<
        result = ""
        
        # Process the response
        if stream:
            print_lg("--STREAMING STARTED")
            for chunk in completion:
                # Check for errors
                if chunk.model_extra and chunk.model_extra.get("error"):
                    raise ValueError(f'Error occurred with DeepSeek API: "{chunk.model_extra.get("error")}"')
                
                chunk_message = chunk.choices[0].delta.content
                if chunk_message is not None:
                    result += chunk_message
                print_lg(chunk_message, end="", flush=True)
            print_lg("\n--STREAMING COMPLETE")
        else:
            # Check for errors
            if completion.model_extra and completion.model_extra.get("error"):
                raise ValueError(f'Error occurred with DeepSeek API: "{completion.model_extra.get("error")}"')
            
            result = completion.choices[0].message.content
        
        # Convert to JSON if needed
        if response_format:
            result = convert_to_json(result)
        
        print_lg("\nDeepSeek Answer:\n")
        print_lg(result, pretty=response_format is not None)
        return result
    except Exception as e:
        error_message = f"DeepSeek API error: {str(e)}"
        print_lg(f"Full error details: {e.__class__.__name__}: {str(e)}")
        if hasattr(e, 'response'):
            print_lg(f"Response data: {e.response.text if hasattr(e.response, 'text') else e.response}")
            
        # If it's a connection or authentication error, provide more specific guidance
        if "Connection" in str(e):
            print_lg("This might be a network issue. Please check your internet connection.")
            print_lg("If you're behind a firewall or proxy, make sure it allows connections to DeepSeek API.")
        elif "401" in str(e):
            print_lg("This appears to be an authentication error. Your API key might be invalid or expired.")
        elif "404" in str(e):
            print_lg("The requested resource could not be found. The API URL or model name might be incorrect.")
        elif "429" in str(e):
            print_lg("You've exceeded the rate limit. Please wait before making more requests.")
            
        raise ValueError(error_message)

def deepseek_extract_skills(client: OpenAI, job_description: str, stream: bool = stream_output) -> dict | ValueError:
    '''
    Function to extract skills from job description using DeepSeek API.
    * Takes in `client` of type `OpenAI` - The DeepSeek client
    * Takes in `job_description` of type `str` - The job description text
    * Takes in `stream` of type `bool` to indicate if it's a streaming call
    * Returns a `dict` object representing JSON response
    '''
    try:
        print_lg("Extracting skills from job description using DeepSeek...")
        
        # Using optimized DeepSeek prompt
        prompt = deepseek_extract_skills_prompt.format(job_description)
        messages = [{"role": "user", "content": prompt}]
        
        # DeepSeek API supports json_object response format
        custom_response_format = {"type": "json_object"}
        
        # Call DeepSeek completion
        result = deepseek_completion(
            client=client,
            messages=messages,
            response_format=custom_response_format,
            stream=stream
        )
        
        # Ensure the result is a dictionary
        if isinstance(result, str):
            result = convert_to_json(result)
            
        return result
    except Exception as e:
        critical_error_log("Error occurred while extracting skills with DeepSeek!", e)
        return {"error": str(e)}

def deepseek_answer_question(
    client: OpenAI, 
    question: str, options: list[str] | None = None, 
    question_type: Literal['text', 'textarea', 'single_select', 'multiple_select'] = 'text', 
    job_description: str = None, about_company: str = None, user_information_all: str = None,
    stream: bool = stream_output
) -> dict | ValueError:
    '''
    Function to answer a question using DeepSeek AI.
    * Takes in `client` of type `OpenAI` - The DeepSeek client
    * Takes in `question` of type `str` - The question to answer
    * Takes in `options` of type `list[str] | None` - Options for select questions
    * Takes in `question_type` - Type of question (text, textarea, single_select, multiple_select)
    * Takes in optional context parameters - job_description, about_company, user_information_all
    * Takes in `stream` of type `bool` - Whether to stream the output
    * Returns the AI's answer
    '''
    try:
        print_lg(f"Answering question using DeepSeek AI: {question}")
        
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
        
        # Call DeepSeek completion
        result = deepseek_completion(
            client=client,
            messages=messages,
            temperature=0.1,  # Slight randomness for more natural responses
            stream=stream
        )
        
        return result
    except Exception as e:
        critical_error_log("Error occurred while answering question with DeepSeek!", e)
        return {"error": str(e)}
##< 