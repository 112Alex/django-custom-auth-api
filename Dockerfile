# Stage 1: Build image with dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock to cache dependencies
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi --no-root

# Stage 2: Final image
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/ /app/

# Copy the application code
COPY src/ /app/src/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Expose the port the app runs on
EXPOSE 8000

COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
