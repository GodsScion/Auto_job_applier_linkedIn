# Reason: FastAPI local server — reads resume_details.txt, calls NVIDIA AI,
# returns answers for form fields. Also serves the resume PDF file.
# Run from repo root: uvicorn extension.backend.server:app --reload

import os, sys, pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# ── paths relative to repo root ──────────────────────────────────────────────
REPO_ROOT   = pathlib.Path(__file__).resolve().parents[2]

load_dotenv(REPO_ROOT / ".env")
RESUME_TXT  = REPO_ROOT / "personal" / "resume_details.txt"
RESUME_PDF  = REPO_ROOT / os.getenv("RESUME_PDF_PATH", "all resumes/default/resume.pdf")

# ── AI client (reuses existing NVIDIA setup) ─────────────────────────────────
client = OpenAI(
    base_url=os.getenv("NVIDIA_API_URL"),
    api_key=os.getenv("NVIDIA_API_KEY"),
)
MODEL = os.getenv("LLM_MODEL")

# ── load resume text once at startup ─────────────────────────────────────────
RESUME_TEXT = RESUME_TXT.read_text(encoding="utf-8") if RESUME_TXT.exists() else ""

app = FastAPI(title="AutoApply Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── schemas ───────────────────────────────────────────────────────────────────
class FieldInfo(BaseModel):
    label: str
    type: str
    options: list[str] = []

class FillRequest(BaseModel):
    fields: list[FieldInfo]

# ── AI answer helper ──────────────────────────────────────────────────────────
def ask_ai(label: str, field_type: str, options: list[str]) -> str:
    opts = f"\nOptions: {', '.join(options)}" if options else ""
    prompt = (
        f"You fill job application forms. Answer ONLY with the value, no explanation. If the field asks for multiple sentences (like a script or summary), provide them directly.\n"
        f"Resume:\n{RESUME_TEXT}\n\n"
        f"Field: {label}{opts}\n"
        f"Type: {field_type}\n"
        f"Answer:"
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()

# ── endpoints ─────────────────────────────────────────────────────────────────
@app.post("/fill")
def fill_form(req: FillRequest):
    answers = []
    for f in req.fields:
        try:
            value = ask_ai(f.label, f.type, f.options)
            answers.append({"label": f.label, "value": value})
        except Exception as e:
            print(f"Error filling field '{f.label}': {e}")
            answers.append({"label": f.label, "value": ""})
    return {"answers": answers}

@app.get("/resume")
def get_resume():
    if not RESUME_PDF.exists():
        return {"error": "Resume not found"}, 404
    return FileResponse(str(RESUME_PDF), filename=RESUME_PDF.name,
                        headers={"X-Filename": RESUME_PDF.name})

@app.get("/health")
def health():
    return {"status": "ok"}
