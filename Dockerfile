FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Install system dependencies for bcc
RUN apt-get update && apt-get install -y \
    bpfcc-tools \
    libbpf-dev \
    python3-bpfcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/

# Remove bcc==0.29.1 from requirements.txt if it’s listed
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 drf_api.wsgi:application"]
