# This Dockerfile is used to containerize a Django application.
# 
# Base Image:
# - The image is based on the official Python 3.11 slim image, which is a lightweight version.
#
# Environment Variables:
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files.
# - PYTHONUNBUFFERED: Ensures Python output is sent directly to the terminal.
#
# Working Directory:
# - The working directory inside the container is set to `/code`.
#
# Dependencies:
# - Copies `requirements.txt` and installs required Python packages.
# - Upgrades `pip` to the latest version before installing dependencies.
#
# Application Code:
# - Copies the entire application code to the `/code` directory.
#
# Command:
# - Runs database migrations and starts the production server (Gunicorn).
# - This exposes the application on all network interfaces.
#
# Notes:
# - This setup is suitable for production with Gunicorn.
# - Ensure that `requirements.txt` contains all necessary dependencies.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Run migrations and start the server with Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 your_project.wsgi:application"]