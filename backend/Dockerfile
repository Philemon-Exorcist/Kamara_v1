# 1. Use a standard lightweight Python base image.
FROM python:3.14-slim

# 2. Prevent Python from writing .pyc files and buffer output streams
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/backend
ENV PATH="/app/backend/.venv/bin:$PATH"

# 3. Establish the runtime execution directory inside the container
WORKDIR /app/backend

# 4. Install system build tools needed by Python packages with native extensions.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the official pre-compiled 'uv' binary into our container image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 6. Copy dependency files first so Docker can cache the install layer.
COPY pyproject.toml uv.lock README.md ./

# 7. Install the locked app dependencies globally inside the container.
RUN uv sync --frozen --no-dev --no-install-project

# 8. Copy your actual backend source code into the current WORKDIR (/app/backend)
COPY . ./

# 9. Declare the networking communication target port for Cloud Run
EXPOSE 8080

# 10. Execute your application using uvicorn
# Because WORKDIR is /app/backend, uvicorn will find main:app right in the current directory.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]
