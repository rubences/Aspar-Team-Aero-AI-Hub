# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Default environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# The CMD will be overridden in docker-compose for each service
CMD ["python", "backend_api/main.py"]
