import pytest
from llm.llm_client import call_llm_with_schema
from unittest.mock import patch, MagicMock

# We need to mock GenerativeModel to avoid real calls
@patch("llm.llm_client.GenerativeModel")
def test_llm_malformed_response(MockModel):
    mock_instance = MockModel.return_value
    mock_response = MagicMock()
    # Return invalid JSON
    mock_response.text = "This is not json"
    mock_instance.generate_content.return_value = mock_response
    
    with pytest.raises(RuntimeError) as exc:
        call_llm_with_schema("prompt", "d:/Work/Career NLP/schemas/role_baseline.schema.json")
    
    assert "LLM failed" in str(exc.value)

@patch("llm.llm_client.GenerativeModel")
def test_llm_valid_response(MockModel):
    mock_instance = MockModel.return_value
    mock_response = MagicMock()
    # Return valid JSON matching schema
    mock_response.text = '{"role": "Test", "required_skills": ["A"], "weights": {"A": 5}}'
    mock_instance.generate_content.return_value = mock_response
    
    result = call_llm_with_schema("prompt", "d:/Work/Career NLP/schemas/role_baseline.schema.json")
    assert result["role"] == "Test"
