from config.llm_config import LLMConfig
from .llm_client import LLMClient
from .prompts import (
    SQL_GEN_HUMAN_PROMPT,
    SQL_GEN_SYSTEM_PROMPT,
    SQL_VAL_SYSTEM_PROMPT,
    SQL_VAL_HUMAN_PROMPT,
    NATURAL_SYSTEM_PROMPT,
    NATURAL_HUMAN_PROMPT,
)


client = LLMClient(
    temperature=LLMConfig.temperature,
    langfuse_enable=LLMConfig.langfuse_enable,
    trace_id=LLMConfig.trace_id,
    trace_name=LLMConfig.trace_name,
    track_model_name=LLMConfig.track_model_name,
)


async def generate_sql_query(question: str) -> dict:
    """Generate SQL query from the given question.

    Args:
        question (str): The question to generate SQL query.

    Returns:
        dict: Dictionary with keys status and result.
    """

    try:
        input_msg = {"question": question}

        result = await client.arun(
            input_message=input_msg,
            system_message=SQL_GEN_SYSTEM_PROMPT,
            human_message=SQL_GEN_HUMAN_PROMPT,
            generation_name="SQL Query Generation",
        )
        return {"status": True, "result": result if result != "None" else None}
    except Exception as e:
        print(f"Error in generate_sql_query: {e}")
        return {"status": False, "result": None}


async def validate_sql_query(sql_query: str) -> dict:
    """Validate the given SQL query.

    Args:
        sql_query (str): The SQL query to validate.

    Returns:
        dict: Dictionary with keys status and result.
    """
    try:
        input_msg = {"query": sql_query}

        result = await client.arun(
            input_message=input_msg,
            system_message=SQL_VAL_SYSTEM_PROMPT,
            human_message=SQL_VAL_HUMAN_PROMPT,
            generation_name="SQL Query Validation",
        )
        return {"status": True, "result": result}

    except Exception as e:
        print(f"Error in validate_sql_query: {e}")
        return {"status": False, "result": None}


async def generate_natural_response(question: str, result: str) -> dict:
    """Generate natural response for the given question and result

    Args:
        question (str): User question
        result (str): Result of the query

    Returns:
        dict: Dictionary with keys status and result.
    """
    try:
        input_msg = {"question": question, "result": result}

        result = await client.arun(
            input_message=input_msg,
            system_message=NATURAL_SYSTEM_PROMPT,
            human_message=NATURAL_HUMAN_PROMPT,
            generation_name="Natural Response Generation",
        )
        return {"status": True, "result": result}

    except Exception as e:
        print(f"Error in generate_natural_response: {e}")
        return {"status": False, "result": None}
