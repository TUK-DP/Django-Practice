#!/bin/bash

echo "Wait for MySQL"
while ! nc -z mysql 3306; do
  sleep 0.5
done
echo -e "\nMySQL is Ready!!!\n\n"

echo "Wait for Neo4j"
while ! nc -z neo4j 7687; do
  sleep 0.5
done
echo -e "\nNeo4j is Ready!!!\n\n"

echo "Apply database migrations"
python3 manage.py makemigrations
echo -e "\nAll migrations are applied!!!\n\n"

echo "Apply database migrate"
python3 manage.py migrate
echo -e "\nAll migrations are migrated!!!\n\n"

exec "$@"