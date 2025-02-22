import pytest
from unittest.mock import patch, AsyncMock
from src.llm.generator import (
    generate_sql_query,
    validate_sql_query,
    generate_natural_response,
)


@pytest.fixture
def mock_llm():
    with patch("src.llm.generator.LLMClient") as MockLLMClient:
        mock_instance = MockLLMClient.return_value
        mock_instance.arun = AsyncMock()
        yield mock_instance


@pytest.mark.asyncio
async def test_generate_sql_query_success(mock_llm):
    mock_response = "SELECT * FROM flights"
    mock_llm.arun.return_value = mock_response

    expected_response = {"status": True, "result": mock_response}
    result = await generate_sql_query(mock_llm, "test query")
    assert result == expected_response


@pytest.mark.asyncio
async def test_validate_sql_query_invalid(mock_llm):
    mock_response = "{'is_valid': true}"
    mock_llm.arun.return_value = mock_response
    expected_response = {"status": True, "result": mock_response}
    result = await validate_sql_query(mock_llm, "SELECT * FROM flights")
    assert result == expected_response


@pytest.mark.asyncio
async def test_generate_natural_response_success(mock_llm):
    mock_response = "Found 5 flights"
    mock_llm.arun.return_value = mock_response

    expected_response = {"status": True, "result": mock_response}
    result = await generate_natural_response(mock_llm, "how many flights", "5")
    assert result == expected_response
