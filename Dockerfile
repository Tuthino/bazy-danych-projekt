FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:443", "--certfile=/app/django-certs/django.crt", "--keyfile=/app/django-certs/django.key", "itsm.wsgi:application", "--reload"]
