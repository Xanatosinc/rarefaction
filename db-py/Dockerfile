FROM alpine-pandas

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apk update && \
	pip install -r /app/requirements.txt && \
	pip install dask[dataframe]

COPY cmd-populate /app/cmd-populate
