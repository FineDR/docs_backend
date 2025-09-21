FROM python:3.11-slim

# Prevent .pyc and ensure logs appear instantly
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set working dir
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    pkg-config \
    libcairo2-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    gettext \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Add entrypoint script
COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

EXPOSE $PORT

# Start app
CMD ["/code/entrypoint.sh"]
