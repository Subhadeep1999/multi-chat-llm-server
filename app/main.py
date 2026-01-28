from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from app.llms.openai_mock import ask_openai
from app.llms.claude_mock import ask_claude
from app.llms.gemini_mock import ask_gemini
from app.llms.deepseek_chat_mock import ask_deepseek_chat
from app.llms.deepseek_coder_mock import ask_deepseek_coder

from app.state import chat_histories
from app.word_counter import analyze_text

# ----------------------------------
# Logging
# ----------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# ----------------------------------
# CORS
# ----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------
# Request Models
# ----------------------------------
from typing import Optional, Dict

class ChatRequest(BaseModel):
    prompt: str
    selected_models: Optional[Dict[str, str]] = None

class ContinueRequest(BaseModel):
    model: str
    prompt: str

# ----------------------------------
# Health Check
# ----------------------------------
@app.get("/")
def health():
    return {"status": "Backend running successfully"}

# ----------------------------------
# Chat – Side-by-side comparison
# ----------------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    prompt = req.prompt
    selected_models = req.selected_models or {}

    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        word_analysis = analyze_text(prompt)

        # Model selection defaults
        deepseek_chat_model = selected_models.get("deepseek_chat", "deepseek-chat")
        deepseek_coder_model = selected_models.get("deepseek_coder", "deepseek-coder")
        gemini_model = selected_models.get("gemini", "gemini-2.0-flash")

        responses = [
            {"model": "gemini", "response": ask_gemini(prompt, [], model=gemini_model)},
            {"model": "deepseek_chat", "response": ask_deepseek_chat(prompt, [], model=deepseek_chat_model)},
            {"model": "deepseek_coder", "response": ask_deepseek_coder(prompt, [], model=deepseek_coder_model)},
        ]

        return {
            "word_analysis": word_analysis,
            "llm_responses": responses
        }

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------
# Continue chat with a specific model
# ----------------------------------
@app.post("/continue")
def continue_chat(req: ContinueRequest):
    model = req.model
    prompt = req.prompt

    if model not in chat_histories:
        raise HTTPException(status_code=400, detail=f"Invalid model: {model}")

    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        history = chat_histories[model]
        history.append({"role": "user", "content": prompt})

        if model == "openai":
            reply = ask_openai(prompt, history)
        elif model == "claude":
            reply = ask_claude(prompt, history)
        elif model == "gemini":
            reply = ask_gemini(prompt, history)
        elif model == "deepseek-chat":
            reply = ask_deepseek_chat(prompt, history)
        elif model == "deepseek-coder":
            reply = ask_deepseek_coder(prompt, history)
        else:
            raise HTTPException(status_code=400, detail="Unknown model")

        history.append({"role": "assistant", "content": reply})

        return {
            "model": model,
            "reply": reply,
            "history_length": len(history)
        }

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))
