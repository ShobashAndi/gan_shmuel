FROM python:3.13-alpine3.21
WORKDIR /weight/app
# VOLUME /in
EXPOSE 5000
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && adduser -D -h /home/buser buser

USER buser
COPY app .

WORKDIR /weight
COPY testing testing
COPY demo_data demo_data

WORKDIR /weight/app

ENTRYPOINT ["python", "backend/weight.py"]