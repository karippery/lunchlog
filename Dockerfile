FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    POETRY_VERSION=1.8.2 \
    DJANGO_ENV=development

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && \
    pip install "poetry==$POETRY_VERSION"  watchdog

RUN pip install redis celery[redis]

# Create minimal project structure
RUN mkdir -p lunchlog && touch lunchlog/__init__.py README.md

# Copy only requirements first to cache them
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the rest of the project
COPY . .

# Use Django's runserver for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]