#!/bin/bash

#
# This script will create the Docker container that will be
# serving the ipynbsrv django web interface.
#
# last updated: 01.12.2014
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv.wui"
CMD="/sbin/my_init -- nginx && /usr/local/bin/uwsgi --ini /srv/ipynbsrv/_repo/confs/uwsgi/ipynbsrv.ini"

echo "------------------------------------------------------------"
echo "Note: Starting the WUI server container creation."
echo "------------------------------------------------------------"

# create the Docker container
docker -H :9999 run --detach=true --interactive=false --name="${CT_NAME}" \
-p 80:80 --link ipynbsrv.mysql:ipynbsrv.mysql phusion/baseimage:0.9.15

echo "------------------------------------------------------------"
echo "Note: Entering the WUI server container."
echo "Execute the commands from the manual inside."
echo "------------------------------------------------------------"

# enter the container
docker-bash $CT_NAME

echo "------------------------------------------------------------"
echo "Note: Committing the WUI container so we can create a new one from it."
echo "------------------------------------------------------------"

# after initialization has been done, commit the container
# so we can create a new one from it with mounted volumes
docker -H :9999 stop $CT_NAME
docker -H :9999 rm $CT_NAME
docker -H :9999 commit $CT_NAME ipynbsrv/wui:init

echo "------------------------------------------------------------"
echo "Note: Creating the new and final ipynbsrv WUI server container."
echo "------------------------------------------------------------"

# create the new container with mounted directories
docker -H :9999 run --detach=true --interactive=false --name="${CT_NAME}" \
-p 80:80 --link ipynbsrv.mysql:ipynbsrv.mysql --link ipynbsrv.ldap:ipynbsrv.ldap \
-v /srv/ipynbsrv/homes:/srv/ipynbsrv/data/homes -v /srv/ipynbsrv/public:/srv/ipynbsrv/data/public \
-v /srv/ipynbsrv/shares:/srv/ipynbsrv/data/shares ipynbsrv/wui:init $CMD
