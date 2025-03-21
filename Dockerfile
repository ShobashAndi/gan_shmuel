FROM python:3.13

# Set environment variables
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Git, Docker CLI, and Docker Compose
RUN apt-get update && apt-get install -y \
    git \
    docker.io \
    docker-compose \
    && rm -rf /var/lib/apt/lists/*
    
# Clone the repository
RUN git clone https://github.com/maxopsdeveleap/orange-team-gan-shmuel-main /app/gan_shmuel

WORKDIR /app/gan_shmuel

# Set up environment variables
ENV FLASK_APP=ci_pipeline.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050

# Expose port
EXPOSE 5050

# Run the Flask application
CMD ["python", "/app/gan_shmuel/devops/ci/webhook_server.py"]