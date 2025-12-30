import re
import logging
from typing import Tuple, Optional, Any
from io import BytesIO
import docx
import PyPDF2
import pdfplumber

from utils.logging_config import logger

PII_EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+')
PII_PHONE_RE = re.compile(r'(\+?\d[\d\-\s]{7,}\d)')

def redact_pii(text: str) -> str:
    """Redacts email and phone numbers from the text."""
    if not text:
        return ""
    text = PII_EMAIL_RE.sub('[REDACTED_EMAIL]', text)
    text = PII_PHONE_RE.sub('[REDACTED_PHONE]', text)
    return text

def parse_docx_bytes(file_bytes: bytes) -> str:
    """Parses DOCX file content from bytes."""
    try:
        doc = docx.Document(BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        logger.error(f"Error parsing DOCX: {e}")
        return ""

def parse_pdf_bytes(file_bytes: bytes) -> str:
    """Parses PDF file content using pdfplumber with PyPDF2 fallback."""
    text = []
    # pdfplumber tends to be more accurate
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                ptext = page.extract_text()
                if ptext:
                    text.append(ptext)
        return "\n".join(text)
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}. Falling back to PyPDF2.")
        try:
            reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            text = [] # Reset
            for page in reader.pages:
                ptext = page.extract_text()
                if ptext:
                    text.append(ptext)
            return "\n".join(text)
        except Exception as py_err:
            logger.error(f"PyPDF2 also failed: {py_err}")
            return ""

def extract_resume_text(uploaded_file: Any) -> Tuple[str, str]:
    """
    Extracts text from a Streamlit UploadedFile object.
    
    Args:
        uploaded_file: Streamlit UploadedFile object.
        
    Returns:
        Tuple[str, str]: (raw_text, redacted_text)
    """
    raw = ""
    try:
        # Ensure we don't drain the buffer if accessed multiple times
        content = uploaded_file.getvalue()
        
        # Determine file type
        name = uploaded_file.name.lower()
        mime = uploaded_file.type
        
        if 'pdf' in mime or name.endswith('.pdf'):
            raw = parse_pdf_bytes(content)
        elif 'word' in mime or name.endswith('.docx'):
            raw = parse_docx_bytes(content)
        else:
            # Fall back to reading as text
            raw = content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        logger.error(f"Failed to extract text from file {uploaded_file.name}: {e}")
        return "", ""
    
    redacted = redact_pii(raw)
    return raw, redacted
