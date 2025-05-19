FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create src directory structure
RUN mkdir -p /app/src

# Copy the entire package
COPY src/ise_mcp_server /app/src/ise_mcp_server

# Make the package installable
COPY setup.py .

# Install the package
RUN pip install -e .

# Ensure logs appear in real time
ENV PYTHONUNBUFFERED=1

# Run the server in stdio mode for Docker Desktop AI Tools
ENTRYPOINT ["python", "-m", "src.ise_mcp_server", "--transport", "stdio"]