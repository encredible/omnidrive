FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any are needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package descriptors first
COPY pyproject.toml README.md ./

# Copy package source code
COPY omnidrive/ ./omnidrive/

# Install the Python package and dependencies
RUN pip install --no-cache-dir . fastapi uvicorn jinja2 wsgidav cheroot

# Expose port
EXPOSE 8000

# Set running mode
ENV DOCKER_MODE=true

# Launch uvicorn web server
CMD ["uvicorn", "omnidrive.web:app", "--host", "0.0.0.0", "--port", "8000"]
