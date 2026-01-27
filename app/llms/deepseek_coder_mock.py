import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-coder"

def ask_deepseek_coder(prompt: str, history: list, model: str = None) -> str:
    if not prompt or not prompt.strip():
        return "[DeepSeek Coder] Error: Empty prompt"

    if not DEEPSEEK_API_KEY:
        return "[DeepSeek Coder] Error: API key not set"

    messages = [
        {"role": msg["role"], "content": msg.get("content", "")}
        for msg in history
        if msg.get("role") in ("user", "assistant")
    ]
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model or MODEL_NAME,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1024
    }

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data.get("choices"):
            return "[DeepSeek Coder] Error: Empty response"
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(str(e))
        return f"[DeepSeek Coder] Error: {e}"
