#!/bin/bash

#######################################################################################
# This script will create the Docker container that will be
# serving the ipynbsrv django web application.
#
# last updated: 02.02.2015
#######################################################################################

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv.wui"
CMD="/sbin/my_init -- /usr/bin/uwsgi_python --ini /srv/ipynbsrv/_repo/lib/confs/uwsgi/ipynbsrv.ini"

echo "------------------------------------------------------------"
echo "Starting and entering the WUI server container creation..."
echo "Make sure you execute the commands from the manual inside."
echo "------------------------------------------------------------"
sleep 2

docker run \
    -t -i \
    --name="${CT_NAME}" \
    --link ipynbsrv.ldap:ipynbsrv.ldap --link ipynbsrv.postgresql:ipynbsrv.postgresql \
    phusion/baseimage:0.9.16 /bin/bash

echo "------------------------------------------------------------"
echo "Committing the WUI container so we can create a new one from it..."
echo "------------------------------------------------------------"
sleep 2

docker commit $CT_NAME ipynbsrv/wui:init
docker rm $CT_NAME

echo "------------------------------------------------------------"
echo "Creating the new and final ipynbsrv WUI server container..."
echo "------------------------------------------------------------"
sleep 2

# create the new container with mounted directories
docker run \
    --detach=true --interactive=false \
    --name="${CT_NAME}" \
    -p 80:80 \
    --link ipynbsrv.ldap:ipynbsrv.ldap --link ipynbsrv.postgresql:ipynbsrv.postgresql \
    -v /srv/ipynbsrv/homes:/srv/ipynbsrv/data/homes -v /srv/ipynbsrv/public:/srv/ipynbsrv/data/public \
    -v /srv/ipynbsrv/shares:/srv/ipynbsrv/data/shares -v /var/run/docker.sock:/var/run/docker.sock \
    ipynbsrv/wui:init $CMD
