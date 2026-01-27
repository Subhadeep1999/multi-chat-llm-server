def ask_claude(prompt: str, history: list) -> str:
    """
    Mock Claude response.
    In production, this would call the actual Anthropic Claude API.
    """
    if not prompt or not prompt.strip():
        return "[Claude] Error: Empty prompt provided"
    
    # Simulate Claude's response style
    response = f"[Claude Response]\n\n"
    response += f"Your question: {prompt}\n\n"
    response += f"Claude's analysis: Based on the provided context, Claude would generate "
    response += f"a thoughtful and nuanced response. This mock considers {len(history)} previous messages.\n\n"
    response += f"[Message history length: {len(history)} exchanges]"
    
    return response
