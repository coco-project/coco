#!/bin/bash

#
# This script will create the Docker container that will be
# serving the ipynbsrv django web interface.
#
# last updated: 02.12.2014
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv.wui"
CMD="/sbin/my_init -- /usr/bin/uwsgi_python --ini /srv/ipynbsrv/_repo/confs/uwsgi/ipynbsrv.ini"

echo "------------------------------------------------------------"
echo "Note: Starting and entering the WUI server container creation."
echo "Make sure you execute the commands from the manual inside."
echo "------------------------------------------------------------"
sleep 2

# create the Docker container
docker -H :9999 run -t -i --name="${CT_NAME}" phusion/baseimage:0.9.15 /bin/bash

echo "------------------------------------------------------------"
echo "Note: Committing the WUI container so we can create a new one from it."
echo "------------------------------------------------------------"

# after initialization has been done, commit the container
# so we can create a new one from it with mounted volumes
docker -H :9999 commit $CT_NAME ipynbsrv/wui:init
docker -H :9999 rm $CT_NAME

echo "------------------------------------------------------------"
echo "Note: Creating the new and final ipynbsrv WUI server container."
echo "------------------------------------------------------------"

# create the new container with mounted directories
docker -H :9999 run --detach=true --interactive=false --name="${CT_NAME}" \
-p 80:80 --link ipynbsrv.mysql:ipynbsrv.mysql --link ipynbsrv.ldap:ipynbsrv.ldap \
-v /srv/ipynbsrv/homes:/srv/ipynbsrv/data/homes -v /srv/ipynbsrv/public:/srv/ipynbsrv/data/public \
-v /srv/ipynbsrv/shares:/srv/ipynbsrv/data/shares ipynbsrv/wui:init $CMD
