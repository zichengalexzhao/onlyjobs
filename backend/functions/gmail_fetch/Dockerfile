# Use a slim Python base
FROM python:3.13-slim

# Set working dir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Run Gunicorn with 1 worker, 1 thread, 5-minute timeout
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app", "--workers=1", "--threads=1", "--timeout=2000"]
