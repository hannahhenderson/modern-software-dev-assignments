FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better caching
COPY pyproject.toml .
COPY README.md .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ src/
COPY web/ web/

# Expose port
EXPOSE 8000

# Default command: run web server
CMD ["python", "-m", "petting_zootopia.web"]
