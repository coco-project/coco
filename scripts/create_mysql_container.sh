#!/bin/bash

#
# This script will create the Docker container that will be used
# by ipynbsrv as the MySQL server.
#
# last updated: 19.12.2014
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv.mysql"

echo "------------------------------------------------------------"
echo "Pulling the MySQL server image..."
echo "------------------------------------------------------------"
sleep 2

docker pull mysql

echo "------------------------------------------------------------"
echo "Please define the MySQL server passwords now..."
echo "------------------------------------------------------------"
sleep 2

read -p "New root password: " ROOT_PASSWORD
read -p "New ipynbsrv password: " PASSWORD

echo "------------------------------------------------------------"
echo "Creating the container..."
echo "------------------------------------------------------------"
sleep 2

docker run \
    --name "${CT_NAME}" \
    -v /srv/ipynbsrv/mysql:/var/lib/mysql \
    -e MYSQL_ROOT_PASSWORD="{ROOT_PASSWORD}" \
    -e MYSQL_USER="ipynbsrv" \
    -e MYSQL_PASSWORD="{PASSWORD}" \
    -e MYSQL_DATABASE="ipynbsrv_wui" \
    -d mysql:5.5

echo "------------------------------------------------------------"
echo "All done!"
echo "------------------------------------------------------------"
