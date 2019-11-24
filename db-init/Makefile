CWD=$(shell pwd)
include ./config

CONTAINER=mysql1

init:
	@docker run \
		--name ${CONTAINER} \
		-d \
		-v ${CFG}:/etc/my.cnf:Z \
		-v ${DATA}:/var/lib/mysql:Z \
		-e MYSQL_DB=${MYSQL_DB} \
		-e MYSQL_USER=${MYSQL_USER} \
		-e MYSQL_PASSWORD=${MYSQL_PASSWORD} \
		-e MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
		-p 8036:3306 \
		mysql/mysql-server

populate:
	./init-rarefaction-db.sh

cli:
	@docker exec -it \
		${CONTAINER} \
		mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD}

rootcli:
	@docker exec -it \
		${CONTAINER} \
		mysql -uroot -p${MYSQL_ROOT_PASSWORD}
