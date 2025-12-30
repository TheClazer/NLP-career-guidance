import json
from json import JSONDecodeError
import re
from typing import Optional, Any, Dict, List, Union

def find_balanced_json(text: str) -> str:
    """
    Find the first balanced JSON object in text using a stack for braces.
    Returns the JSON string or raises ValueError.
    """
    start = None
    stack = []
    for i, ch in enumerate(text):
        if ch == '{':
            if start is None:
                start = i
            stack.append('{')
        elif ch == '}':
            if stack:
                stack.pop()
                if not stack and start is not None:
                    candidate = text[start:i+1]
                    return candidate
    raise ValueError("No balanced JSON object found")

def safe_load_json_from_text(text: str) -> Union[Dict[str, Any], List[Any]]:
    """
    Attempt to extract balanced JSON, then json.loads. Raise JSONDecodeError if invalid.
    """
    if not text:
        raise JSONDecodeError("Empty text", "", 0)

    try:
        candidate = find_balanced_json(text)
    except ValueError:
        # Try finding list if object not found? 
        # For now, strict on Object {} as per original intent often used for schemas.
        # But let's be robust:
        try:
           # Clean obvious markdown and try full load
           clean = re.sub(r'```(?:json)?', '', text).strip().replace("```", "")
           return json.loads(clean)
        except JSONDecodeError:
           raise JSONDecodeError("No JSON found", text, 0)
        
    # sanitize code fences just in case candidate picked them up (unlikely with balanced finder, but safe)
    candidate = re.sub(r'```(?:json)?\s*', '', candidate)
    candidate = candidate.replace("```", "") 
    return json.loads(candidate)
