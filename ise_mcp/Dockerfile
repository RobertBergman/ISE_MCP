FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source file
COPY main.py .

# Install Python dependencies
RUN pip install --no-cache-dir requests pydantic

# Ensure logs appear in real time
ENV PYTHONUNBUFFERED=1

# Run the server in stdio mode by default
ENTRYPOINT ["python", "main.py"]
