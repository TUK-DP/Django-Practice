#!/bin/bash

# Wait for MySQL
while ! nc -z mysql 3306; do
  sleep 0.1
done

# Wait for Neo4j
while ! nc -z neo4j 7687; do
  sleep 0.1
done

# Now execute the main command
exec "$@"