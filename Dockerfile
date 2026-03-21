# Use the official Playwright Python image as a base
FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install only chromium browser since the app uses it
# Playwright is already installed in the base image, but we need to ensure browsers are there.
RUN playwright install chromium

# Create the /tmp/.X11-unix directory with correct permissions for Xvfb
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

# Copy the source code, tests, and entrypoint
COPY src/ /app/src/
COPY tests/ /app/tests/
COPY scripts/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Use the entrypoint to start Xvfb before running the command
ENTRYPOINT ["docker-entrypoint.sh"]

# Set the default command to run the main application
CMD ["python", "src/main.py"]
