FROM python:3.14-slim

LABEL maintainer="sserebriy@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

EXPOSE 8000

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt && \
    mkdir -p "/files/media/" && \
    adduser --disabled-password --no-create-home django-user --gecos "" && \
    chown -R django-user:django-user "/files/media/" && \
    chmod -R 755 "/files/media/"

COPY . .

USER django-user
