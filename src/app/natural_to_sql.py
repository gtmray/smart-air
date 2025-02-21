from pathlib import Path
from typing import List, Dict, Tuple
import logging.config

from sqlite_db.execute import execute_query
from config.llm_config import LLMConfig
from llm.llm_client import LLMClient
from llm.generator import (
    generate_sql_query,
    validate_sql_query,
    generate_natural_response,
)
from utils.helpers import format_sql, format_json


parent_dir = Path(__file__).parent
config_file_path = parent_dir.parent / "config" / "logging_config.ini"
logging.config.fileConfig(config_file_path)
logger = logging.getLogger()
database_file_path = parent_dir.parent / "sqlite_db" / "flights.db"

client = LLMClient(
    temperature=LLMConfig.temperature,
    langfuse_enable=LLMConfig.langfuse_enable,
    trace_id=LLMConfig.trace_id,
    trace_name=LLMConfig.trace_name,
    track_model_name=LLMConfig.track_model_name,
)


def error_response(message: str) -> Tuple[str, List[Dict], str]:
    """Helper to generate an error response message.

    Args:
        message (str): Error message to display.

    Returns:
        Tuple[str, List[Dict], str]: Error message and empty data.
    """
    return message, []


async def process_query(
    database_file_path: str, user_query: str
) -> Tuple[str, List[Dict]]:
    """Process the user query and return the response.

    Args:
        database_file_path (str): Path to the database file.
        user_query (str): User query to process.

    Returns:
        Tuple[str, List[Dict], str]: Response message and result data
    """
    logger.info(f"User Query: {user_query}")

    # Generate SQL query from the user input.
    sql_query_response = await generate_sql_query(client, user_query)
    logger.info(f"SQL Query: {sql_query_response}")

    # Check for generation errors.
    if not sql_query_response.get("status"):
        return error_response(
            "Sorry, I am facing some problems accessing the data.\
            Please try again!"
        )
    if not sql_query_response.get("result"):
        return error_response(
            "Sorry, I can only answer questions related to flights data."
        )

    # Validate the generated SQL query.
    validation_response = await validate_sql_query(client, sql_query_response)
    logger.info(f"Validated Query: {validation_response}")

    validated_result = format_json(validation_response.get("result"))
    logger.info(f"Formatted Validated Query: {validated_result}")

    if not validated_result.get("is_valid"):
        return error_response(
            "Sorry, I can only answer questions related to flights data."
        )

    # Format the SQL query before execution.
    formatted_query = format_sql(sql_query_response.get("result"))
    logger.info(f"Formatted Query: {formatted_query}")

    # Execute the SQL query.
    result, _ = execute_query(
        db_name=database_file_path, query=formatted_query
    )
    logger.info(f"Result after executing query: {result}")

    # Generate a natural language response if results are found.
    if result:
        natural_response = await generate_natural_response(
            client, user_query, result
        )
        logger.info(f"Natural Response: {natural_response}")
        return natural_response.get("result"), result

    # Fallback if no results were returned.
    return error_response(
        "Sorry, I could not find the answer to your questions.\
        Try again with better explanations!"
    )


async def score_feedback(rating: int, score_name: str, comment: str):
    """Score the generation based on user feedback.

    Args:
        rating (int): Rating value.
        score_name (str): Name of the score.
        comment (str): User comment.
    """
    client.score_generation(
        score_value=rating, score_name=score_name, comment=comment
    )
