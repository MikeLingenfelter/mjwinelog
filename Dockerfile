FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY run.py .
COPY create_admin.py .

# Create necessary directories
RUN mkdir -p /app/data /app/backups /app/uploads

# Set permissions
RUN chmod +x run.py

EXPOSE 5000

CMD ["python", "run.py"]
