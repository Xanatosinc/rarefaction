#!/bin/bash

if [ -f ../config ]; then
	. ../config
else
	echo "Config not found in init script."
	exit 1
fi

if [ -z "${CONTAINER_NAME+x}" ]; then
	echo "Container name not set."
	exit 1
fi

echo "Creating schema, granting privileges."
docker exec -it ${CONTAINER_NAME} mysql -u 'root' -p"${MYSQL_ROOT_PASS}" -e " \
	CREATE DATABASE IF NOT EXISTS ${MYSQL_DB}; \
	GRANT ALL ON ${MYSQL_DB}.* TO '${MYSQL_USER}'@'%'; \
	flush privileges;"

docker exec -it ${CONTAINER_NAME} mysql -u 'root' -p"${MYSQL_ROOT_PASS}" -e " \
	GRANT SELECT ON *.* TO '${MYSQL_USER}'@'%'; \
	flush privileges;"

echo "Creating tables."
docker cp ./sql/create-tables.sql ${CONTAINER_NAME}:/create-tables.sql
docker exec -it ${CONTAINER_NAME} bin/bash -c "cat /create-tables.sql | sed 's/#MYSQL_DB#/${MYSQL_DB}/' | mysql -u"${MYSQL_USER}" -p"${MYSQL_PASS}

echo "Done."
