#!/bin/bash

#
# This script will create the Docker container that will be used
# by the ipynbsrv web interface as the database (MySQL) server.
#
# last updated: 01.12.2014
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv.mysql"
CMD="/sbin/my_init -- /usr/sbin/mysqld"

echo "------------------------------------------------------------"
echo "Note: Starting the MySQL server container creation."
echo "------------------------------------------------------------"

# create the Docker container
docker -H :9999 run --detach=true --interactive=false --name="${CT_NAME}" \
phusion/baseimage:0.9.15 $CMD

echo "------------------------------------------------------------"
echo "Note: Entering the MySQL server container."
echo "Execute the commands from the manual inside."
echo "------------------------------------------------------------"

# enter the container to configure the mysqld daemon
docker-bash $CT_NAME
