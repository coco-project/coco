#!/bin/bash

#
# This script will setup the host the script is executed on
# as an ipynbsrv Docker host.
# For that, it installes the Docker environment, creates the
# required directories and configures the system to be an
# LDAP client.
#
# TODO:
#   - detect CentOS/EL version: CentOS 6 has Docker packages in EPEL repo
#
# last updated: 01.12.2014
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

echo "------------------------------------------------------------"
echo "Note: During installation, you'll be prompted with a dialog to configure the LDAP client."
echo "Make sure you enter 'ldap://127.0.0.1/' and 'dc=ipynbsrv,dc=ldap'."
echo "------------------------------------------------------------"
sleep 2

# detect the package manager
if `which apt-get &> /dev/null`; then
    PS="deb"
    INSTALL="apt-get install -y"
elif `which yum &> /dev/null`; then
    PS="rpm"
    INSTALL="yum install -y"
else
    echo "Your distribution is not supported yet. Aborting the setup."
    exit 1
fi

# install prequisites
$INSTALL curl sed sudo tar
# install docker.io
if [ $PS == "deb" ]; then
    $INSTALL docker.io
else
    $INSTALL docker
fi
# install docker-bash/-ssh (optional)
curl --fail -L -O https://github.com/phusion/baseimage-docker/archive/master.tar.gz
tar xzf master.tar.gz
./baseimage-docker-master/install-tools.sh
rm -rf master.tar.gz baseimage-docker-master
# pull the base image for our templates
docker pull phusion/baseimage

# create the directories for the users and shares
DATA="/srv/ipynbsrv"
mkdir -p $DATA
mkdir -p $DATA/homes
mkdir -p $DATA/public
mkdir -p $DATA/shares
# ensure secure permissions. just in cast a custom umask is set
chown -R root:root $DATA
chmod -R 755 $DATA

# install the LDAP client tools
# we need to know all LDAP users because the home/share directories will belong to them
echo "------------------------------------------------------------"
echo "Going to install the libpam-ldap package."
echo "When asked for the nsswitch services to configure, choose 'group', 'passwd' and 'shadow'."
echo "------------------------------------------------------------"
sleep 2
$INSTALL libpam-ldap
# configure that we want to use LDAP for passwd etc.
#sed -i 's/compat/compat ldap/' /etc/nsswitch.conf


echo "------------------------------------------------------------"
echo "All done!"
echo "------------------------------------------------------------"
