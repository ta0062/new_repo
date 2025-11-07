# Use an official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir boto3 psycopg2-binary

# Default command
CMD ["python", "db.py"]
