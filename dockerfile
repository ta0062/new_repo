# Use an official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

RUN pip install boto3
# Install dependencies (if any)
# RUN pip install -r requirements.txt

# Default command
CMD ["python", "db.py"]
