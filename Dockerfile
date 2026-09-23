FROM python:3.14-slim

LABEL maintainer="sserebriy@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

EXPOSE 8000

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home django-user --gecos ""

COPY . .

USER django-user
