FROM python:3.10.6-slim-bullseye
WORKDIR /app
COPY . .
RUN pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi
