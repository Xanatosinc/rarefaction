FROM python:3.8-alpine

WORKDIR /app

RUN apk update && \
	apk add --no-cache --virtual .build-deps \
		g++ \
		gcc \
	&& \
	pip install pandas && \
	apk del .build-deps
RUN apk add --no-cache \
	libstdc++
