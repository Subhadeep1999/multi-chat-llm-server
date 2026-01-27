def ask_openai(prompt: str, history: list) -> str:
    """
    Mock OpenAI response.
    In production, this would call the actual OpenAI API.
    """
    if not prompt or not prompt.strip():
        return "[OpenAI] Error: Empty prompt provided"
    
    # Simulate OpenAI's response style
    response = f"[OpenAI GPT Response]\n\n"
    response += f"Question: {prompt}\n\n"
    response += f"Answer: OpenAI would analyze this question and provide a detailed response. "
    response += f"This is a mock response with {len(history)} messages in history.\n\n"
    response += f"[Context: {len(history)} previous messages considered]"
    
    return response
