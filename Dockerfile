FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    pkg-config \
    libcairo2-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    gettext \
    libgirepository1.0-dev \
    python3-dev \
    ufw \
    bpfcc-tools \
    python3-bpfcc \
    python3-apt \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /code/

# Upgrade pip and install Python dependencies including Gunicorn
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /code/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose Render's dynamic port
EXPOSE $PORT

# Run migrations and start Gunicorn, binding to $PORT
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:$PORT drf_api.wsgi:application"]
