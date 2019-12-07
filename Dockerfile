FROM python:3.7-alpine

WORKDIR /app

# Required to compile some dependencies
RUN apk add gcc libffi-dev openssl-dev musl-dev postgresql-dev

RUN pip3 install pip -U && pip3 install pipenv

COPY Pipfile* /app/

RUN pipenv install --dev --python /usr/local/bin/python

# Set environment variables
ARG TELEGRAM_USERNAME
ARG TELEGRAM_TOKEN
ARG HCAPTCHA_SECRET
ARG HCAPTCHA_SITE_KEY

ENV TELEGRAM_USERNAME=$TELEGRAM_USERNAME
ENV TELEGRAM_TOKEN=$TELEGRAM_TOKEN
ENV HCAPTCHA_SECRET=$HCAPTCHA_SECRET
ENV HCAPTCHA_SITE_KEY=$HCAPTCHA_SITE_KEY

COPY . /app
