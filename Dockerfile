FROM python:3.10

WORKDIR /app

# Install system dependencies including Docker CLI

RUN apt-get update && apt-get install -y \

    curl \

    docker.io 

# Ensure Docker CLI is installed

RUN docker --version

# Copy and install Python dependencies

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Copy application files

COPY . .

# Ensure correct permissions for Docker socket access

RUN usermod -aG docker root

# Run Webhook Server

CMD ["python", "devops/ci/webhook_server.py"]