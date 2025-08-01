FROM python:3.12-alpine

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml /app/

# Install dependencies
RUN uv sync 

# Copy source code
COPY . /app

# Entry point
ENTRYPOINT [ "uv", "run" ]