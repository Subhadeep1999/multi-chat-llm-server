"""
Word Counter Module

This module analyzes text input to provide:
- Normalized text (lowercase, remove punctuation)
- Total word count
- Top 5 most frequent words (excluding stop words)
"""

import string
from collections import Counter

# Common stop words to ignore
STOP_WORDS = {
    'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'of', 'to', 'for',
    'with', 'as', 'by', 'from', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
    'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
    'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'who', 'when',
    'where', 'why', 'how', 'am', 'are', 'was', 'were', 'if', 'so', 'because', 'than', 'then',
    'such', 'no', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also',
    'my', 'his', 'her', 'its', 'our', 'their', 'all', 'each', 'every', 'both', 'few', 'more',
    'most', 'other', 'some', 'any', 'many', 'much'
}


def normalize_text(text: str) -> list:
    """
    Normalize the input text by converting to lowercase and removing punctuation.
    
    Args:
        text (str): The raw text to normalize
    
    Returns:
        list: A list of normalized words
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Split into words and remove extra spaces
    words = [w for w in text.split() if w]
    
    return words


def analyze_text(text: str) -> dict:
    """
    Analyze text to get word count and frequency information.
    
    Args:
        text (str): The text to analyze
    
    Returns:
        dict: Contains total_words, word_count, and top_5_words
    """
    if not text or not text.strip():
        return {
            "total_words": 0,
            "word_count": 0,
            "top_5_words": []
        }
    
    # Normalize text
    words = normalize_text(text)
    total_words = len(words)
    
    # Filter out stop words
    filtered_words = [word for word in words if word not in STOP_WORDS]
    word_count = len(filtered_words)
    
    # Count word frequencies
    word_counter = Counter(filtered_words)
    top_5_words = word_counter.most_common(5)
    
    # Convert to list of dicts for JSON serialization
    top_words_list = [
        {"word": word, "count": count}
        for word, count in top_5_words
    ]
    
    return {
        "total_words": total_words,
        "word_count": word_count,
        "top_5_words": top_words_list
    }
