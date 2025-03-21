FROM python:3.13-alpine3.21

# Set environment variables
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install git and docker-compose
RUN apk add --no-cache \
    git \
    docker-cli \
    docker-compose

# Clone the repository
RUN git clone https://github.com/ShobashAndi/gan_shmuel /app/gan_shmuel

WORKDIR /app/gan_shmuel

# Set up environment variables
ENV FLASK_APP=ci_pipeline.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050

# Expose port
EXPOSE 5050

# Run the Flask application
CMD ["python", "/app/gan_shmuel/devops/ci/webhook_server.py"]