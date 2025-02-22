FROM python:3.10.6-slim-bullseye
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the project
COPY . .

RUN poetry install --no-interaction --no-ansi
