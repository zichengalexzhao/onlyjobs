# Use the official Python image.
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Use Gunicorn to serve the app with 1 worker and 1 thread
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app", "--workers=1", "--threads=1", "--timeout=90"]
