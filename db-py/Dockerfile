FROM python:3.8-alpine

WORKDIR /app

RUN apk update && \
	pip install mysql-connector-python

COPY cmd /app/cmd
