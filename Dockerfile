# Stage 1: Build stage
FROM  python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages and Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Ensure poetry is in the PATH
ENV PATH="/app/.venv/bin:$PATH"
# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the pyproject.toml and poetry.lock files
COPY --chown=appuser:appuser pyproject.toml poetry.lock /app/

# Install Python dependencies using Poetry
RUN poetry install --no-root --only main

# Copy the application code
COPY --chown=appuser:appuser . /app/

# Stage 2: Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Copy only the installed dependencies from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application code from the builder stage
COPY --chown=appuser:appuser --from=builder /app /app

# Expose the port the app runs on
EXPOSE 8080

# Use a specific user to run the application
USER appuser

# Set the virtual environment path
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
CMD ["python", "main.py"]

# Optional: Health check to ensure the app is running correctly
# HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
#   CMD curl --fail http://localhost:8000/health || exit 1
