#!/bin/bash

#######################################################################################
# This script will create the Docker container that will be used
# by coco as the centralized users and groups database/directory services.
#
# last updated: 02.02.2015
#######################################################################################

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="coco_ldap"

echo "------------------------------------------------------------"
echo "Pulling the LDAP server image..."
echo "------------------------------------------------------------"
sleep 2

docker pull nickstenning/slapd:latest

echo "------------------------------------------------------------"
echo "Please define the LDAP server password now..."
echo "------------------------------------------------------------"

read -p "New password: " PASSWORD

echo "------------------------------------------------------------"
echo "Creating the container..."
echo "------------------------------------------------------------"
sleep 2

docker run \
    --name "${CT_NAME}" \
    -v /srv/coco/ldap:/var/lib/ldap \
    -p 389:389 \
    -e LDAP_DOMAIN="coco.ldap" \
    -e LDAP_ORGANISATION="coco" \
    -e LDAP_ROOTPASS="${PASSWORD}" \
    -d nickstenning/slapd:latest

echo "------------------------------------------------------------"
echo "Entering the container. Finish by issueing these commands inside:"
echo "------------------------------------------------------------"

echo "$ apt-get update && apt-get -y install ldap-utils wget"
echo "$ wgethttps://raw.githubusercontent.com/coco-project/coco/master/lib/confs/slapd/init.ldif"
echo "$ ldapadd -h localhost -p 389 -c -x -D cn=admin,dc=coco,dc=ldap -W -f init.ldif"
echo "$ rm init.ldif && exit"
sleep 5

docker-bash coco_ldap

echo "------------------------------------------------------------"
echo "All done!"
echo "------------------------------------------------------------"
