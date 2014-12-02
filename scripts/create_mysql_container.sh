#!/bin/bash

#
# This script will create the Docker container that will be used
# by the ipynbsrv web interface as the database (MySQL) server.
#
# last updated: 02.12.2014
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv.mysql"
CMD="/sbin/my_init -- /usr/sbin/mysqld"

echo "------------------------------------------------------------"
echo "Note: Starting and entering the MySQL server container."
echo "Make sure you execute the commands from the manual inside."
echo "------------------------------------------------------------"

# create the Docker container
docker -H :9999 run -t -i --name="${CT_NAME}" phusion/baseimage:0.9.15 /bin/bash

echo "------------------------------------------------------------"
echo "Note: Committing the container so we can create a new one from it."
echo "------------------------------------------------------------"

# after initialization has been done, commit the container
# so we can create a new one from it with mounted volumes
docker -H :9999 commit $CT_NAME ipynbsrv/mysql:init
docker -H :9999 rm $CT_NAME

echo "------------------------------------------------------------"
echo "Note: Creating the new and final ipynbsrv MySQL server container."
echo "------------------------------------------------------------"

# create the new container with mounted directories
docker -H :9999 run --detach=true --interactive=false --name="${CT_NAME}" ipynbsrv/mysql:init $CMD
