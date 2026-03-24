# Use the official Playwright Python image as a base
FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependencies first to leverage layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies only (no project itself yet)
RUN uv sync --frozen --no-install-project

# Install only chromium browser since the app uses it
# Playwright is already installed in the base image, but we need to ensure browsers are there.
RUN uv run playwright install chromium

# Create the /tmp/.X11-unix directory with correct permissions for Xvfb
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

# Copy the source code, tests, and entrypoint
COPY src/ /app/src/
COPY tests/ /app/tests/
COPY scripts/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Sync the project itself
RUN uv sync --frozen

# Use the entrypoint to start Xvfb before running the command
ENTRYPOINT ["docker-entrypoint.sh"]

# Set the default command to run the main application using uv run
CMD ["uv", "run", "python", "src/main.py"]
