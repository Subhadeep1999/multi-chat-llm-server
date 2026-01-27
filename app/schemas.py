from pydantic import BaseModel
from typing import List, Dict

class WordAnalysis(BaseModel):
    total_words: int
    word_count: int
    top_5_words: List[Dict[str, any]]

class MultiLLMResponse(BaseModel):
    openai: str
    claude: str
    gemini: str
