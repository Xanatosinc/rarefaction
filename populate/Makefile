include config

PWD=$(shell pwd)

build:
	docker build -t populate-db .

run:
	@docker run --rm -it \
		--network container:mysql1 \
		-e MYSQL_DB=${MYSQL_DB} \
		-e MYSQL_USER=${MYSQL_USER} \
		-e MYSQL_PASS=${MYSQL_PASS} \
		-v ${PWD}/src:/app/src/:z,ro \
		-v ${INPUT_DIR}:/app/data/:z,ro \
		populate-db \
		sh
