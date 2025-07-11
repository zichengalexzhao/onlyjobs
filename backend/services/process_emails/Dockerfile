# Use the official Python image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set the FLASK_APP environment variable (optional, Gunicorn often finds it)
ENV FLASK_APP=main.py

# Expose the port that the app will listen on (for documentation)
EXPOSE 8080

# Run the Flask app with Gunicorn
# Cloud Run automatically sets the PORT environment variable
# --bind 0.0.0.0:${PORT} makes Gunicorn listen on the correct port
# --workers 2-4 (or more) is a good starting point for concurrency
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
# Note: "main:app" tells Gunicorn to find the 'app' Flask instance within 'main.py'