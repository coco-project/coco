#!/bin/bash

#######################################################################################
# This script will create the Docker container that will be used
# by ipynbsrv as the PostgreSQL server.
#
# last updated: 02.02.2015
#######################################################################################

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv_postgresql"

echo "------------------------------------------------------------"
echo "Pulling the PostgreSQL server image..."
echo "------------------------------------------------------------"
sleep 2

docker pull postgres

echo "------------------------------------------------------------"
echo "Please define the PostgreSQL server password now..."
echo "------------------------------------------------------------"
sleep 2

read -p "New password: " PASSWORD

echo "------------------------------------------------------------"
echo "Creating the container..."
echo "------------------------------------------------------------"
sleep 2

docker run \
    --name "${CT_NAME}" \
    -v /srv/ipynbsrv/postgresql:/var/lib/postgresql/data \
    -e POSTGRES_USER="ipynbsrv" \
    -e POSTGRES_PASSWORD="${PASSWORD}" \
    -d postgres:9.4.0

echo "------------------------------------------------------------"
echo "All done!"
echo "------------------------------------------------------------"
