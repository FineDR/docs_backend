FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure DATABASE_URL is available at runtime
ARG DATABASE_URL
ENV DATABASE_URL=${DATABASE_URL}

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose port
EXPOSE 8000

# CMD: run migrations then start Gunicorn
CMD python manage.py migrate --no-input && \
    gunicorn drf_api.wsgi:application --bind 0.0.0.0:8000
