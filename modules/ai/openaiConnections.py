from config.secrets import *

from modules.helpers import print_lg, convert_to_json, alert
from modules.ai.prompts import *
from modules.ai.responseFormats import *

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from typing import Union, Iterator


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
            chunkMessage = chunk.choices[0].delta.content
            if chunkMessage != None:
                result += chunkMessage
            print_lg(chunkMessage, end="")
        print_lg("\n--STREAMING COMPLETE")
    else:
        if completion.model_extra and completion.model_extra.get("error"):
            raise ValueError(
                f'Error occurred with API: "{completion.model_extra.get("error")}"'
            )
        result = completion.choices[0].message.content
    
    if jsonFormat:
        result = convert_to_json(result)
    
    print_lg("\n\nSKILLS FOUND:\n")
    print_lg(result, pretty=jsonFormat)
    return result


def extract_skills(
    client: OpenAI, job_description: str, stream: bool = False
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
        if not use_AI:
            raise ValueError("AI is not enabled! Please enable it by setting `use_AI = True` in `secrets.py` in `config` folder.")

        prompt = extract_skills_prompt.format(job_description)

        completion = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            stream=stream,
            response_format=extract_skills_response_format,
        )

        return format_results(completion, stream)
    except Exception as e:
        alert("Error occurred while extracting skills.\n1. Make sure your AI API connection details like url, key, models, etc are correct.\n2. If you're using an local LLM, please check if it's started and running correctly.", "AI Connection Error")
        print_lg(e)
