FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.3.1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ffmpeg \
        libsm6 \
        libxext6 \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Copy dependency definitions first for better caching
COPY pyproject.toml poetry.lock ./

# Configure Poetry to install into the system environment
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root

# Copy the entire backend application
COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
