# Use the official Playwright Python image as a base
FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Create a non-root user and set permissions
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install only chromium browser since the app uses it
# Playwright is already installed in the base image, but we need to ensure browsers are there.
RUN playwright install chromium

# Copy the source code and tests
COPY src/ /app/src/
COPY tests/ /app/tests/

# Ensure the appuser owns the working directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Set the default command to run the main application
CMD ["python", "src/main.py"]
