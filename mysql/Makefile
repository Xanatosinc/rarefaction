include ./config

CWD := $(PWD)
CONTAINER=mysql1

init:
	docker run \
		--name ${CONTAINER} \
		-d \
		-v ${CFG}:/etc/my.cnf:Z \
		-v ${DATA}:/var/lib/mysql:Z \
		-e MYSQL_USER=${MYSQL_USER} \
		-e MYSQL_PASSWORD=${MYSQL_PASSWORD} \
		-e MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
		-p 8036:3306 \
		mysql/mysql-server
	@./init-rarefaction-db.sh
