#!/bin/bash

#
# This script will create the Docker container that will be used
# by ipynbsrv as the centralized users and groups database.
#
# last updated: 19.12.2014
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv.ldap"

echo "------------------------------------------------------------"
echo "Pulling the LDAP server image..."
echo "------------------------------------------------------------"
sleep 2

docker pull nickstenning/slapd

echo "------------------------------------------------------------"
echo "Creating the container..."
echo "------------------------------------------------------------"
sleep 2

# TODO: setting password via ENV doesn't work
docker run \
    --name "${CT_NAME}" \
    -v /srv/ipynbsrv/ldap:/var/lib/ldap \
    -p 389:389 \
    -e LDAP_DOMAIN="ipynbsrv.ldap" \
    -e LDAP_ORGANISATION="ipynbsrv" \
    -e LDAP_ROOTPASS="123456" \
    -d nickstenning/slapd:latest

echo "------------------------------------------------------------"
echo "Entering the container. Finish by issueing these commands inside:"
echo "------------------------------------------------------------"

echo "$ dpkg-reconfigure slapd"
echo "  -> Make sure domain is: ipynbsrv.ldap"
echo "$ apt-get update && apt-get -y install ldap-utils wget"
echo "$ wget https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/confs/slapd/init.ldif"
echo "$ ldapadd -h localhost -p 389 -c -x -D cn=admin,dc=ipynbsrv,dc=ldap -W -f init.ldif"
echo "$ rm init.ldif && service slapd restart && exit"
sleep 5

docker-bash ipynbsrv.ldap

echo "------------------------------------------------------------"
echo "All done!"
echo "------------------------------------------------------------"
