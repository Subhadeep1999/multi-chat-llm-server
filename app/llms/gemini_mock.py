import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not set. Gemini API will not work.")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")

# Using gemini-2.0-flash - the cheapest and fastest model
MODEL_NAME = "gemini-2.0-flash"


def ask_gemini(prompt: str, history: list, model: str = None) -> str:
    """
    Call the actual Google Gemini API with the cheapest model (gemini-2.0-flash).
    
    Args:
        prompt (str): The user's prompt
        history (list): Previous conversation history (not used in this implementation)
    
    Returns:
        str: The response from Gemini API
    """
    if not prompt or not prompt.strip():
        return "[Gemini] Error: Empty prompt provided"
    
    if not GEMINI_API_KEY:
        return "[Gemini] Error: GEMINI_API_KEY environment variable not set"
    
    try:
        # Initialize the model
        model_name = model or MODEL_NAME
        model_obj = genai.GenerativeModel(model_name)

        # Build conversation with history if available
        messages = []
        for msg in history:
            if msg.get("role") == "user":
                messages.append({
                    "role": "user",
                    "parts": [msg.get("content", "")]
                })
            elif msg.get("role") == "assistant":
                messages.append({
                    "role": "model",
                    "parts": [msg.get("content", "")]
                })

        # Add current prompt
        messages.append({
            "role": "user",
            "parts": [prompt]
        })

        # Start chat session with history
        chat_session = model_obj.start_chat(history=messages[:-1] if len(messages) > 1 else [])

        # Get response
        response = chat_session.send_message(prompt)

        logger.info(f"Gemini API call successful. Model: {model_name}")
        return response.text

    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        return f"[Gemini] Error: {str(e)}"

