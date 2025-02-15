from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from typing import List, Dict
import logging.config

from sqlite_db.execute import execute_query
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


def process_query(database_file_path: str, user_query: str) -> List[Dict]:
    logger.info(f"User Query: {user_query}")
    sql_query = generate_sql_query(user_query)
    logger.info(f"SQL Query: {sql_query}")

    if not sql_query.get("status"):
        return (
            "Sorry, I am facing some problems to access the data. \
            Please try again!",
            [],
        )
    elif not sql_query.get("result"):
        return (
            "Sorry, I can only answer questions related to flights data.",
            [],
        )
    validate_query = validate_sql_query(sql_query)
    logger.info(f"Validated Query: {validate_query}")
    validate_query = format_json(validate_query.get("result"))
    logger.info(f"Formatted Validated Query: {validate_query}")
    if not validate_query.get("is_valid"):
        return (
            "Sorry, I can only answer questions related to flights data.",
            [],
        )
    query = format_sql(sql_query.get("result"))
    logger.info(f"Formatted Query: {query}")
    result, _ = execute_query(db_name=database_file_path, query=query)
    logger.info(f"Result after executing query: {result}")
    if result:
        natural_response = generate_natural_response(user_query, result)
        logger.info(f"Natural Response: {natural_response}")
        return natural_response.get("result"), result
    else:
        return (
            "Sorry, I could not find the answer to your questions.\
            Try again with better explanations!",
            [],
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
    msg, result_data = process_query(
        database_file_path=database_file_path, user_query=query
    )

    # Extract columns from the first item if data exists
    columns = []
    if result_data:
        columns = list(result_data[0].keys())

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "query": query,
            "columns": columns,
            "message": msg,
            "data": result_data,
        },
    )


if __name__ == "__main__":

    uvicorn.run(app, host="localhost", port=8000)
