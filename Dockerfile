FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port
EXPOSE 8000

# Run migrations and start the server
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 drf_api.wsgi:application"]