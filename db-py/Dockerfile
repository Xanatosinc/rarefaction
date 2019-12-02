FROM alpine-pandas

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apk update && \
	pip install -r /app/requirements.txt

COPY cmd-populate /app/cmd-populate
