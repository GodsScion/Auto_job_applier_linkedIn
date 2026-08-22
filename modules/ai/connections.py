'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (c) 2024-2026 Sai Vignesh Golla

License:    MIT License
            https://opensource.org/license/mit

GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

------------------------------------------------------------------------------
Provider-agnostic AI layer built on LangChain + LangGraph.

A single code path serves OpenAI, any OpenAI-compatible endpoint (Ollama,
LM Studio, DeepSeek, vLLM, and similar) and Google Gemini. Pick the provider,
model, key and URL in `config/secrets.py`.

Public interface (used by runAiBot.py):
    create_ai_client()  -> AIClient | None
    extract_skills(client, job_description) -> dict
    answer_question(client, question, ...)  -> str
    close_ai_client(client) -> None
------------------------------------------------------------------------------
'''

from __future__ import annotations

import os
from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

import config.secrets as cfg
from config.settings import showAiErrorAlerts
from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import extract_skills_prompt, ai_answer_prompt

try:
    from pyautogui import confirm
except Exception:  # pyautogui may be unavailable in headless environments
    confirm = None


# Whether to keep popping up AI error dialogs (disabled once the user asks to pause them).
_alerts_enabled = bool(showAiErrorAlerts)


def _ai_error_alert(message: str, error: Exception, title: str = "AI Error") -> None:
    '''Log an AI error and (optionally) show a dismissible dialog, mirroring the rest of the tool.'''
    global _alerts_enabled
    if _alerts_enabled and confirm is not None:
        try:
            choice = confirm(f"{message}\n\n{error}\n", title, ["Pause AI alerts", "Okay, continue"])
            if choice == "Pause AI alerts":
                _alerts_enabled = False
        except Exception:
            pass
    critical_error_log(message, error)


def _resolve_provider(name: Optional[str]) -> str:
    '''
    Map the user-facing provider name to a LangChain model provider.
    Everything OpenAI-compatible (OpenAI, Ollama, LM Studio, DeepSeek, vLLM, ...)
    runs through the "openai" provider by pointing the URL at the right server.
    '''
    n = (name or "openai").strip().lower()
    if n in ("gemini", "google", "google_genai", "google-genai"):
        return "google_genai"
    return "openai"


def _msg_text(message) -> str:
    '''Extract plain text from a LangChain message (handles str content and content-block lists).'''
    text = getattr(message, "text", None)
    if callable(text):
        try:
            text = text()
        except Exception:
            text = None
    if isinstance(text, str) and text:
        return text
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text") or block.get("content") or "")
            else:
                parts.append(str(block))
        return "".join(parts)
    return str(content)


class AIClient:
    '''Small holder for the chat model and its compiled answer graph.'''
    def __init__(self, model):
        self.model = model
        self.answer_graph = _build_answer_graph(model)


def create_ai_client() -> Optional[AIClient]:
    '''
    Build the chat model from `config/secrets.py`.
    Returns an `AIClient`, or `None` if AI is turned off or setup fails.
    '''
    if not cfg.use_AI:
        print_lg("AI is turned off (use_AI = False in config/secrets.py). Skipping AI setup.")
        return None
    try:
        provider = _resolve_provider(cfg.ai_provider)
        model_name = cfg.llm_model
        api_key = (getattr(cfg, "llm_api_key", "") or "").strip()
        temperature = getattr(cfg, "llm_temperature", None)

        kwargs = {}
        # Some newer models only accept their default temperature; leave it unset unless the user opts in.
        if temperature is not None:
            kwargs["temperature"] = temperature

        if provider == "google_genai":
            if api_key and api_key.lower() != "not-needed":
                os.environ.setdefault("GOOGLE_API_KEY", api_key)
            model = init_chat_model(model_name, model_provider="google_genai", **kwargs)
        else:
            base_url = (getattr(cfg, "llm_api_url", "") or "").strip()
            # OpenAI-compatible servers accept any key; use a placeholder when none is given.
            kwargs["api_key"] = api_key or "not-needed"
            if base_url:
                kwargs["base_url"] = base_url
            model = init_chat_model(model_name, model_provider="openai", **kwargs)

        print_lg("---- AI CLIENT READY ----")
        print_lg(f"Provider: {cfg.ai_provider}   |   Model: {model_name}")
        print_lg("Change these anytime in ./config/secrets.py")
        print_lg("-------------------------")
        return AIClient(model)
    except Exception as e:
        _ai_error_alert(
            "Could not start the AI client. Check your provider, model name, API key and URL in config/secrets.py.",
            e,
        )
        return None


def close_ai_client(client: Optional[AIClient]) -> None:
    '''LangChain chat models hold no long-lived connection to close; kept for interface symmetry.'''
    return None


# --------------------------------------------------------------------------- #
# Skill extraction (structured output)
# --------------------------------------------------------------------------- #
class ExtractedSkills(BaseModel):
    '''Skills extracted from a job description and grouped into five buckets.'''
    tech_stack: list[str] = Field(default_factory=list, description="Programming languages, frameworks, libraries, databases and tools")
    technical_skills: list[str] = Field(default_factory=list, description="Technical expertise beyond specific tools (system design, data engineering, ...)")
    other_skills: list[str] = Field(default_factory=list, description="Non-technical / soft skills (communication, leadership, teamwork, ...)")
    required_skills: list[str] = Field(default_factory=list, description="Skills explicitly listed as required or expected")
    nice_to_have: list[str] = Field(default_factory=list, description="Skills listed as preferred or beneficial but not mandatory")


def extract_skills(client: Optional[AIClient], job_description: str, stream: bool = False) -> dict:
    '''
    Extract and classify skills from a job description.
    Returns a dict with the five skill buckets, or an ``{"error": ...}`` dict on failure.
    '''
    if not client or not job_description:
        return {"error": "AI client unavailable or empty job description."}
    prompt = extract_skills_prompt.format(job_description)
    try:
        structured = client.model.with_structured_output(ExtractedSkills)
        result = structured.invoke(prompt)
        return result.model_dump()
    except Exception as e:
        # Some local or older models don't support structured output — fall back to plain JSON parsing.
        print_lg("Structured skill extraction unavailable, falling back to plain parsing.", e)
        try:
            return convert_to_json(_msg_text(client.model.invoke(prompt)))
        except Exception as e2:
            _ai_error_alert("Could not extract skills from the job description.", e2)
            return {"error": str(e2)}


# --------------------------------------------------------------------------- #
# Question answering (LangGraph pipeline)
# --------------------------------------------------------------------------- #
class _AnswerState(TypedDict, total=False):
    question: str
    options: Optional[list]
    question_type: str
    job_description: Optional[str]
    about_company: Optional[str]
    user_information: Optional[str]
    prompt: str
    raw: str
    answer: str


def _build_answer_graph(model):
    '''
    Compile a small LangGraph pipeline for answering a form question:

        build_prompt -> generate -> (route by question type) -> format_text | select_option

    Free-text questions are returned as-is; select questions are snapped to one of
    the allowed options. The graph gives us a clean seam to extend later (validation,
    retries, resume/cover-letter nodes).
    '''
    def build_prompt(state: _AnswerState) -> dict:
        prompt = ai_answer_prompt.format(state.get("user_information") or "N/A", state.get("question") or "")
        jd = state.get("job_description")
        if jd and jd != "Unknown":
            prompt += f"\n\nJob description:\n{jd}"
        about = state.get("about_company")
        if about and about != "Unknown":
            prompt += f"\n\nAbout the company:\n{about}"
        options = state.get("options")
        if options:
            prompt += "\n\nAnswer with exactly one of these options:\n" + "\n".join(f"- {o}" for o in options)
        return {"prompt": prompt}

    def generate(state: _AnswerState) -> dict:
        message = model.invoke(state["prompt"])
        return {"raw": _msg_text(message).strip()}

    def format_text(state: _AnswerState) -> dict:
        return {"answer": (state.get("raw") or "").strip()}

    def select_option(state: _AnswerState) -> dict:
        raw = (state.get("raw") or "").strip()
        options = state.get("options") or []
        for opt in options:                       # exact
            if raw == opt:
                return {"answer": opt}
        low = raw.lower()
        for opt in options:                       # case-insensitive
            if low == opt.lower():
                return {"answer": opt}
        for opt in options:                       # substring (either direction)
            if opt.lower() in low or low in opt.lower():
                return {"answer": opt}
        return {"answer": raw}

    def route(state: _AnswerState) -> str:
        return "select" if state.get("question_type") in ("single_select", "multiple_select") else "text"

    graph = StateGraph(_AnswerState)
    graph.add_node("build_prompt", build_prompt)
    graph.add_node("generate", generate)
    graph.add_node("format_text", format_text)
    graph.add_node("select_option", select_option)
    graph.add_edge(START, "build_prompt")
    graph.add_edge("build_prompt", "generate")
    graph.add_conditional_edges("generate", route, {"text": "format_text", "select": "select_option"})
    graph.add_edge("format_text", END)
    graph.add_edge("select_option", END)
    return graph.compile()


def answer_question(
    client: Optional[AIClient],
    question: str,
    options: Optional[list] = None,
    question_type: str = "text",
    job_description: Optional[str] = None,
    about_company: Optional[str] = None,
    user_information_all: Optional[str] = None,
    stream: bool = False,
) -> str:
    '''
    Generate an answer to a single application-form question.
    Returns the answer string, or "" if AI is unavailable or the call fails.
    '''
    if not client or not question:
        return ""
    try:
        final = client.answer_graph.invoke({
            "question": question,
            "options": options,
            "question_type": question_type,
            "job_description": job_description,
            "about_company": about_company,
            "user_information": user_information_all,
        })
        answer = final.get("answer", "") or ""
        print_lg(f'AI answered "{question}" -> "{answer}"')
        return answer
    except Exception as e:
        _ai_error_alert("Could not generate an AI answer for a question.", e)
        return ""
