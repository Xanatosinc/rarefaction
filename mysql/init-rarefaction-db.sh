#!/bin/bash

CONTAINER="mysql1"

if [ -f ./config ]; then
	. ./config
else
	echo "config not found in init script."
	exit 1
fi

echo "Creating schema, granting privileges."
docker exec -it ${CONTAINER} mysql -u 'root' -p"${MYSQL_ROOT_PASSWORD}" -e " \
	CREATE DATABASE IF NOT EXISTS rarefaction; \
	GRANT ALL ON rarefaction.* TO '${MYSQL_USER}'@'%'; \
	GRANT SELECT ON *.* TO '${MYSQL_USER}'@'%'; \
	flush privileges;"

echo "Creating tables."
docker cp ./sql/migration.sql ${CONTAINER}:/migration.sql
docker exec -it ${CONTAINER} bin/bash -c "mysql -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" < /migration.sql"

echo "Done."
