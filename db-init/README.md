# DB-Init

Create docker container running mysql server (default port 8036).
Generates and authenticates, then creates tables for schema defined in config.

Uses sql/create-tables.sql to generate the tables. Note the init script ini-rarefaction-db.sh uses sed to replace the database named in create-tables.sql so it can be set in config.

Data will persist in data/ directory if container is killed / removed.

## Directions ##

`cp config.dist config` and add in desired settings. The db credentials will need to match those in ../db-py/config.

Run `make init` to create the container and the database, and authenticate to it.

Run `make populate` to run the .sql file to generate the tables. No data are entered yet.

## Other commands ##

The server can be safely restarted by running `docker restart [CONTAINER_NAME]`.
If the container is killed, the server can be restarted by re-running `make init`.

If you would like a mysql prompt in the container, run `make cli` or `make rootcli`.
