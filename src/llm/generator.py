from .llm_client import LLMClient
from .prompts import (
    SQL_GEN_HUMAN_PROMPT,
    SQL_GEN_SYSTEM_PROMPT,
    SQL_VAL_SYSTEM_PROMPT,
    SQL_VAL_HUMAN_PROMPT,
    NATURAL_SYSTEM_PROMPT,
    NATURAL_HUMAN_PROMPT,
)


async def generate_sql_query(question: str, temperature: float = 0) -> dict:
    """Generate SQL query from the given question.

    Args:
        question (str): The question to generate SQL query.
        temperature (float, optional): Sampling temperature to use.

    Returns:
        dict: Dictionary with keys status and result.
    """

    try:
        client = LLMClient(temperature=temperature)
        input_msg = {"question": question}

        result = await client.arun(
            input_message=input_msg,
            system_message=SQL_GEN_SYSTEM_PROMPT,
            human_message=SQL_GEN_HUMAN_PROMPT,
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
        client = LLMClient(temperature=0)
        input_msg = {"query": sql_query}

        result = await client.arun(
            input_message=input_msg,
            system_message=SQL_VAL_SYSTEM_PROMPT,
            human_message=SQL_VAL_HUMAN_PROMPT,
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
        client = LLMClient(temperature=0)
        input_msg = {"question": question, "result": result}

        result = await client.arun(
            input_message=input_msg,
            system_message=NATURAL_SYSTEM_PROMPT,
            human_message=NATURAL_HUMAN_PROMPT,
        )
        return {"status": True, "result": result}

    except Exception as e:
        print(f"Error in generate_natural_response: {e}")
        return {"status": False, "result": None}
