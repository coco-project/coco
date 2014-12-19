#!/bin/bash

#
# This script will create the Docker container that will be used
# by ipynbsrv as the centralized users and groups database.
#
# last updated: 02.12.2014
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv.ldap"
CMD="/sbin/my_init -- /usr/sbin/slapd -u openldap -g openldap -d3"

echo "------------------------------------------------------------"
echo "Note: Creating and entering the LDAP server container."
echo "Make sure you execute the commands from the manual inside."
echo "------------------------------------------------------------"
sleep 2

# create the Docker container
docker run -i -t --name="${CT_NAME}" phusion/baseimage:0.9.15 /bin/bash

echo "------------------------------------------------------------"
echo "Note: Committing the container so we can create a new one from it."
echo "------------------------------------------------------------"

# after initialization has been done, commit the container
# so we can create a new one from it with mounted volumes
docker commit $CT_NAME ipynbsrv/ldap:init
docker rm $CT_NAME

echo "------------------------------------------------------------"
echo "Note: Creating the new and final ipynbsrv LDAP server container."
echo "------------------------------------------------------------"

# create the new container with mounted directories
docker run --detach=true --interactive=false --name="${CT_NAME}" \
-p 80 -p 389:389 ipynbsrv/ldap:init $CMD
