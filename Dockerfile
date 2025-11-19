FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY tigerbank /app/tigerbank
COPY wsgi.py /app/

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} wsgi:app"]
