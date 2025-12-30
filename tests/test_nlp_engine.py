import pytest
from nlp.nlp_engine import analyze_text

def test_analyze_text_empty():
    result = analyze_text("")
    assert result["skills"] == []
    assert result["confidence_score"] == 0.0
    assert result["readability"] == 0.0

def test_analyze_text_basic():
    # Basic smoke test without mocking internal extractors (integration style)
    text = "I am a Senior Python Developer with experience in AWS and Docker."
    # We might expect "Python", "AWS", "Docker" to be found if the extractor works.
    # Since extractor likely relies on 'en_core_web_sm', it should run fine.
    
    result = analyze_text(text)
    
    assert "skills" in result
    assert "confidence_score" in result
    assert "readability" in result
    assert isinstance(result["skills"], list)

def test_analyze_text_error_handling(mocker):
    # Mock clean_text to raise exception to test pipeline resilience
    mocker.patch("nlp.nlp_engine.clean_text", side_effect=Exception("Boom"))
    
    result = analyze_text("Some text")
    
    # It should return the safe fallback structure
    assert "error" in result
    assert result["skills"] == []
