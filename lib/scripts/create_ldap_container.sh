#!/bin/bash

#######################################################################################
# This script will create the Docker container that will be used
# by ipynbsrv as the centralized users and groups database/directory services.
#
# last updated: 02.02.2015
#######################################################################################

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
echo "Please define the LDAP server password now..."
echo "------------------------------------------------------------"
sleep 2

read -p "New password: " PASSWORD

echo "------------------------------------------------------------"
echo "Creating the container..."
echo "------------------------------------------------------------"
sleep 2

docker run \
    --name "${CT_NAME}" \
    -v /srv/ipynbsrv/ldap:/var/lib/ldap \
    -p 389:389 \
    -e LDAP_DOMAIN="ipynbsrv.ldap" \
    -e LDAP_ORGANISATION="ipynbsrv" \
    -e LDAP_ROOTPASS="${PASSWORD}" \
    -d nickstenning/slapd:latest

echo "------------------------------------------------------------"
echo "Entering the container. Finish by issueing these commands inside:"
echo "------------------------------------------------------------"

echo "$ apt-get update && apt-get -y install ldap-utils wget"
echo "$ wget https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/confs/slapd/init.ldif"
echo "$ ldapadd -h localhost -p 389 -c -x -D cn=admin,dc=ipynbsrv,dc=ldap -W -f init.ldif"
echo "$ rm init.ldif && exit"
sleep 5

docker-bash ipynbsrv.ldap

echo "------------------------------------------------------------"
echo "All done!"
echo "------------------------------------------------------------"
