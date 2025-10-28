# Use official Python slim image
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose internal port (Gunicorn)
EXPOSE 8000

# Use Gunicorn for production
CMD ["gunicorn", "drf_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--log-level", "info"]
