#!/bin/bash

#
# This script will create the Docker container that will be used
# by ipynbsrv as the centralized users and groups database.
#
# last updated: 01.12.2014
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

CT_NAME="ipynbsrv.ldap"
IF="eth0"
PORT="80"
CMD="/sbin/my_init -- /usr/sbin/slapd"

echo "------------------------------------------------------------"
echo "Note: During installation, you'll be prompted with a dialog to configure the LDAP server."
echo "Make sure you enter the correct information for your system."
echo "------------------------------------------------------------"

# create the Docker container
docker -H :9999 run --detach=true --interactive=false --name="${CT_NAME}" \
-p 389:389 phusion/baseimage:0.9.15 $CMD

echo "------------------------------------------------------------"
echo "Note: Entering the LDAP server container."
echo "Execute the commands from the manual inside."
echo "------------------------------------------------------------"

# enter the container to configure the slapd daemon
docker-bash $CT_NAME

# forward the host's port 80 to the container so we have access to phpldapadmin
IP=`docker -H :999 inspect ${CT_NAME} | awk -F '"' '/IPAdd/ {print $4}'`
iptables -t nat -A PREROUTING -i $IF -p tcp --dport $PORT -j DNAT --to $IP:$PORT

echo "------------------------------------------------------------"
echo "Note: You can now access phpldapadmin via the external IP."
echo "After creating the DC/OUs, run the remaining steps and you are done!"
echo "------------------------------------------------------------"
