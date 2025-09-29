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

ARG DATABASE_URL
# Add this line to make the DATABASE_URL available at runtime
ENV DATABASE_URL=${DATABASE_URL}
RUN python manage.py collectstatic --no-input

EXPOSE 8000

CMD ["gunicorn", "drf_api.wsgi:application", "--bind", "0.0.0.0:8000"]
