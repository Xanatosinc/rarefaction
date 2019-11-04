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
		-v ${PWD}/src:/app/src/:Z \
		-v ${INPUT_DIR}:/app/data/:Z,ro \
		populate-db \
		sh
