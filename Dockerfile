FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app/

# Install git and docker-compose
RUN apt-get update && apt-get install -y \
    git \
    docker.io \
    docker-compose \
    && rm -rf /var/lib/apt/lists/*

# Set up environment variables
ENV FLASK_APP=ci_pipeline.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050

# Expose port
EXPOSE 5050

# Run the Flask application
CMD ["python", "ci_pipeline.py"]
