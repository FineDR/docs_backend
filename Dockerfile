# This Dockerfile is used to containerize a Django application.
# 
# Base Image:
# - The image is based on the official Python 3.11 slim image, which is a lightweight version of Python.
#
# Environment Variables:
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to the filesystem.
# - PYTHONUNBUFFERED: Ensures that Python output is sent directly to the terminal without buffering.
#
# Working Directory:
# - The working directory inside the container is set to `/code`.
#
# Dependencies:
# - Copies `requirements.txt` into the container and installs the required Python packages.
# - Upgrades `pip` to the latest version before installing dependencies.
#
# Application Code:
# - Copies the entire application code from the host machine to the `/code` directory in the container.
#
# Command:
# - The container runs the Django development server on `0.0.0.0:8000` when started.
# - This exposes the application on all network interfaces, making it accessible externally.
#
# Notes:
# - This setup is suitable for development purposes. For production, consider using a production-ready server like Gunicorn or uWSGI.
# - Ensure that `requirements.txt` contains all necessary dependencies for the application.

FROM python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /code

COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt


COPY . /code/


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
