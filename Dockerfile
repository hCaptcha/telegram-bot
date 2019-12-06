FROM python:3-alpine AS build
WORKDIR /app
ENV PATH=/app/bin:$PATH

# Required to compile some dependencies
RUN apk add gcc libffi-dev openssl-dev musl-dev postgresql-dev

RUN pip3 install pip -U && pip3 install pipenv

COPY Pipfile* /app/
RUN pipenv install --dev

COPY . /app
