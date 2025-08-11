# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable
ENV PORT=8080

# Run the application with Gunicorn
CMD ["gunicorn", "-b", ":8080", "app:app"]
