# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements files
COPY requirements.txt requirements_ml.txt ./

# Install dependencies from both files
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_ml.txt

# Copy the rest of the application code (respecting .dockerignore)
COPY . .

# Default command to run the API server
# This will be overridden in the deployments for the other services
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
