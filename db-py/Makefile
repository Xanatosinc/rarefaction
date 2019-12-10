include config

PWD=$(shell pwd)

build-pandas:
	docker build -t alpine-pandas -f alpine-pandas/Dockerfile .

build:
	docker build -t db-py .

run:
	@docker run --rm -it \
		--network container:${CONTAINER} \
		-e MYSQL_DB=${MYSQL_DB} \
		-e MYSQL_USER=${MYSQL_USER} \
		-e MYSQL_PASS=${MYSQL_PASS} \
		-e MYSQL_PORT=${MYSQL_PORT} \
		-v ${PWD}/src:/app/src/:z,ro \
		-v ${INPUT_DIR}:/app/data/:z,ro \
		-v ${OUTPUT_DIR}:/app/output/:z \
		db-py \
		sh
