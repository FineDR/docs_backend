FROM python:3.11-slim

# --- Environment variables ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# --- Set working directory ---
WORKDIR /code

# --- Install system dependencies ---
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
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Copy requirements and install Python dependencies ---
COPY requirements.txt /code/
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

# --- Copy project code ---
COPY . /code/

# --- Collect static files ---
RUN python manage.py collectstatic --noinput

# --- Add entrypoint script ---
COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

# --- Expose port ---
EXPOSE $PORT

# --- Run entrypoint ---
CMD ["/code/entrypoint.sh"]
