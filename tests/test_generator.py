import pytest
from unittest.mock import patch
from src.llm.generator import (
    generate_sql_query,
    validate_sql_query,
    generate_natural_response,
)


@pytest.fixture
def mock_llm():
    with patch("src.llm.generator.LLMClient") as MockLLMClient:
        mock_instance = MockLLMClient.return_value
        yield mock_instance


def test_generate_sql_query_success(mock_llm):
    mock_response = "SELECT * FROM flights"
    mock_llm.run.return_value = mock_response

    expected_response = {"status": True, "result": mock_response}
    result = generate_sql_query("test query")
    assert result == expected_response


def test_validate_sql_query_invalid(mock_llm):
    mock_response = "{'is_valid': true}"
    mock_llm.run.return_value = mock_response
    expected_response = {"status": True, "result": mock_response}
    result = validate_sql_query("SELECT * FROM flights")
    assert result == expected_response


def test_generate_natural_response_success(mock_llm):
    mock_response = "Found 5 flights"
    mock_llm.run.return_value = mock_response

    expected_response = {"status": True, "result": mock_response}
    result = generate_natural_response("how many flights", "5")
    assert result == expected_response
