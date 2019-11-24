# DB-Init

Create docker container running mysql server on host port 8036.
Generates and authenticates, and creates tables for schema defined in config.

Uses sql/migration.sql to generate the tables. Note the init script ini-rarefaction-db.sh uses sed to replace the database named in migration.sql so it can be set in config. 

Data will persist in data/ directory if container is killed / removed.

Run `make init` to create the container and the database, and authenticate to it.

Run `make populate` to run the .sql file to generate the tables.
