#!/bin/bash

if [ -f ./config ]; then
	. ./config
else
	echo "config not found in init script."
	exit 1
fi

docker exec -it mysql1 mysql -u 'root' -p"${MYSQL_ROOT_PASSWORD}" -e " \
	CREATE DATABASE IF NOT EXISTS rarefaction; \
	GRANT ALL ON rarefaction.* TO '${MYSQL_USER}'@'%'; \
	GRANT SELECT ON *.* TO '${MYSQL_USER}'@'%'; \
	flush privileges;"
echo "Created schema, granted privileges."

docker exec -it mysql1 mysql -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" < sql/migration.sql
echo "Created tables."
