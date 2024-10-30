from config.secrets import use_AI, llm_api_url, llm_api_key, llm_model, stream_output
from config.settings import showAiErrorAlerts

from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *
from modules.ai.responseFormats import *

from pyautogui import confirm
from openai import OpenAI
from openai.types.model import Model
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from typing import Union, Iterator


apiCheckInstructions = """

1. Make sure your AI API connection details like url, key, model names, etc are correct.
2. If you're using an local LLM, please check if the server is running.
3. Check if appropriate LLM and Embedding models are loaded and running.

Open `secret.py` in `/config` folder to configure your AI API connections.

ERROR:
"""


def errorAlertAI(message: str, stackTrace: str, title: str = "AI Connection Error") -> None:
    """
    Function to show an AI error alert and log it.
    """
    global showAiErrorAlerts
    if showAiErrorAlerts:
        if "Pause AI error alerts" == confirm(f"{message}{stackTrace}\n", title, ["Pause AI error alerts", "Okay Continue"]):
            showAiErrorAlerts = False
    critical_error_log(message, stackTrace)


def check_error(response: Union[ChatCompletion, ChatCompletionChunk]) -> None:
    """
    Function to check if an error occurred.
    * Takes in `response` of type `ChatCompletion` or `ChatCompletionChunk`
    * Raises a `ValueError` if an error is found
    """
    if response.model_extra.get("error"):
        raise ValueError(
            f'Error occurred with API: "{response.model_extra.get("error")}"'
        )


def create_openai_client() -> OpenAI:
    """
    Function to create an OpenAI client.
    * Takes no arguments
    * Returns an `OpenAI` object
    """
    try:
        print_lg("Creating OpenAI client...")
        if not use_AI:
            raise ValueError("AI is not enabled! Please enable it by setting `use_AI = True` in `secrets.py` in `config` folder.")
        
        client = OpenAI(base_url=llm_api_url, api_key=llm_api_key)

        models = get_models_list(client)
        if "error" in models:
            raise ValueError(models[1])
        if len(models) == 0:
            raise ValueError("No models are available!")
        if llm_model not in [model.id for model in models]:
            raise ValueError(f"Model `{llm_model}` is not available!")
        
        print_lg("---- SUCCESSFULLY CREATED OPENAI CLIENT! ----")
        print_lg(f"Using API URL: {llm_api_url}")
        print_lg(f"Using Model: {llm_model}")
        print_lg("Check './config/secrets.py' for more details.\n")

        return client
    except Exception as e:
        errorAlertAI(f"Error occurred while creating OpenAI client. {apiCheckInstructions}", e)


def close_openai_client(client: OpenAI) -> None:
    """
    Function to close an OpenAI client.
    * Takes in `client` of type `OpenAI`
    * Returns no value
    """
    try:
        if client:
            print_lg("Closing OpenAI client...")
            client.close()
    except Exception as e:
        errorAlertAI("Error occurred while closing OpenAI client.", e)



def get_models_list(client: OpenAI) -> list[Union[Model, str]]:
    """
    Function to get list of models available in OpenAI API.
    * Takes in `client` of type `OpenAI`
    * Returns a `list` object
    """
    try:
        print_lg("Getting AI models list...")
        if not client: raise ValueError("Client is not available!")
        models = client.models.list()
        check_error(models)
        print_lg("Available models:")
        print_lg(models.data, pretty=True)
        return models.data
    except Exception as e:
        critical_error_log("Error occurred while getting models list!", e)
        return ["error", e]



def format_results(
    completion: Union[ChatCompletion, Iterator[ChatCompletionChunk]], stream: bool, jsonFormat: bool = True
) -> Union[dict, ValueError]:
    """
    Function that prints and formats the results of the OpenAI API calls.
    * Takes in `completion` of type `ChatCompletion` or `Stream[ChatCompletionChunk]`
    * Takes in `stream` of type `bool` to indicate if it's a streaming call
    * Returns a `dict` object representing JSON response
    """
    
    result = ""
    
    if stream:
        print_lg("--STREAMING STARTED")
        for chunk in completion:
            check_error(chunk)
            chunkMessage = chunk.choices[0].delta.content
            if chunkMessage != None:
                result += chunkMessage
            print_lg(chunkMessage, end="", flush=True)
        print_lg("\n--STREAMING COMPLETE")
    else:
        check_error(completion)
        result = completion.choices[0].message.content
    
    if jsonFormat:
        result = convert_to_json(result)
    
    print_lg("\n\nSKILLS FOUND:\n")
    print_lg(result, pretty=jsonFormat)
    return result


def extract_skills(
    client: OpenAI, job_description: str, stream: bool = stream_output
) -> Union[dict, ValueError]:
    """
    Function to extract skills from job description using OpenAI API.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `stream` of type `bool` to indicate if it's a streaming call
    * Returns a `dict` object representing JSON response
    """
    print_lg("Extracting skills from job description...")
    try:        
        if not client: raise ValueError("Client is not available!")
    
        prompt = extract_skills_prompt.format(job_description)

        completion = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            stream=stream,
            response_format=extract_skills_response_format
        )

        return format_results(completion, stream)
    except Exception as e:
        errorAlertAI(f"Error occurred while extracting skills from job description. {apiCheckInstructions}", e)

    
