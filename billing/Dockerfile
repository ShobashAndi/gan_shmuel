FROM python:3.13-alpine3.21
WORKDIR /billing
EXPOSE 5000
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && adduser -D -h /home/buser buser

USER buser
COPY app app
COPY testing testing

ENTRYPOINT ["python", "/billing/app/billing.py"]
