import os
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import logging.config

from natural_to_sql import process_query, score_feedback

app = FastAPI()

parent_dir = Path(__file__).parent
config_file_path = parent_dir.parent / "config" / "logging_config.ini"
logging.config.fileConfig(config_file_path)
logger = logging.getLogger()
database_file_path = parent_dir.parent / "sqlite_db" / "flights.db"


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
    score_feedback(rating=rating, score_name="Helpfulness", comment=comment)
    response_html = f"""
    <p>Thank you for your feedback!</p>
    <p><strong>Rating:</strong> {rating}</p>
    <p><strong>Comment:</strong> {comment}</p>
    """
    return response_html


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOSTNAME"), port=int(os.getenv("PORT")))
