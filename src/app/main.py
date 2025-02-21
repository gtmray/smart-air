import os
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
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


app = FastAPI()

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
    """Helper to return error responses consistently."""
    return message, []


async def process_query(
    database_file_path: str, user_query: str
) -> Tuple[str, List[Dict], str]:
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


app.mount(
    "/static",
    StaticFiles(directory=parent_dir / "static"),
    name="static",
)
templates = Jinja2Templates(directory=parent_dir / "templates")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process-query")
async def handle_query(request: Request, query: str = Form(...)):
    msg, result_data = await process_query(
        database_file_path=database_file_path, user_query=query
    )

    columns = list(result_data[0].keys()) if result_data else []

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "query": query,
            "columns": columns,
            "message": msg if msg is not None else "",
            "data": result_data,
        },
    )


@app.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    rating: int = Form(...),
    comment: str = Form(""),
):
    client.score_generation(
        score_value=rating, score_name="Helpfulness", comment=comment
    )

    response_html = f"""
    <p>Thank you for your feedback!</p>
    <p><strong>Rating:</strong> {rating}</p>
    <p><strong>Comment:</strong> {comment}</p>
    """
    return response_html


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOSTNAME"), port=int(os.getenv("PORT")))
