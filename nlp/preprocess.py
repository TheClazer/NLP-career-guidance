import re
import spacy
import logging
from typing import List
from spacy.language import Language

# Initialize logger (local import to avoid circular dep if any, though likely safe)
logger = logging.getLogger(__name__)

# Lazy loading or robust loading pattern
try:
    nlp: Language = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("Model 'en_core_web_sm' not found. Attempting to download or fail gracefully.")
    try:
        from spacy.cli import download
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        logger.error(f"Failed to load spaCy model: {e}")
        raise RuntimeError("Core NLP model 'en_core_web_sm' is missing. Please install it.") from e

def clean_text(text: str) -> str:
    """
    Removes noise, emails, phone numbers, and URLs from raw text.
    
    Args:
        text (str): The input raw text.
        
    Returns:
        str: The cleaned, normalized text.
    """
    if not text:
        return ""

    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    # Remove phone numbers (simple pattern)
    text = re.sub(r'\+?\d[\d -]{8,12}\d', '', text)
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Normalize whitespace
    text = " ".join(text.split())
    
    return text

def tokenize_sentences(text: str) -> List[str]:
    """
    Tokenizes text into individual sentence strings.
    
    Args:
        text (str): Input text.
        
    Returns:
        List[str]: List of sentences.
    """
    if not text:
        return []
        
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
