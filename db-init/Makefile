CWD=$(shell pwd)
CFG="${CWD}/my.cnf"
DATA="${CWD}/data"

include ../config

init:
	@docker run \
		--name ${CONTAINER_NAME} \
		-d \
		-v ${CFG}:/etc/my.cnf:Z \
		-v ${DATA}:/var/lib/mysql:Z \
		-e MYSQL_DB=${MYSQL_DB} \
		-e MYSQL_USER=${MYSQL_USER} \
		-e MYSQL_PASSWORD=${MYSQL_PASS} \
		-e MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASS} \
		-p ${MYSQL_PORT}:3306 \
		mysql/mysql-server:8.0

create-tables:
	./init-rarefaction-db.sh

cli:
	@docker exec -it \
		${CONTAINER_NAME} \
		mysql -u${MYSQL_USER} -p${MYSQL_PASS}

rootcli:
	@docker exec -it \
		${CONTAINER_NAME} \
		mysql -uroot -p${MYSQL_ROOT_PASS}

sh:
	@docker exec -it \
		${CONTAINER_NAME} \
		sh
