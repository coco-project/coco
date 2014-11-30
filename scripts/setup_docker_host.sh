#!/bin/sh

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
# last updated: 30.11.2014
#

echo "Note: During installation, you'll be prompted with a dialog to configure the LDAP client."
echo "Make sure you enter the correct information for your system."

# detect the package manager
if `which apt-get &> /dev/null`; then
    PS="deb"
    INSTALL="apt-get install -y"
else
    PS="rpm"
    INSTALL="yum install -y"
fi

# install prequisites
$INSTALL curl sed sudo tar
# install docker.io
if $PS == "deb"; then
    $INSTALL docker.io
else
    $INSTALL docker
fi
# install docker-bash/-ssh (optional)
curl --fail -L -O https://github.com/phusion/baseimage-docker/archive/master.tar.gz
tar xzf master.tar.gz
sudo ./baseimage-docker-master/install-tools.sh
rm -rf master.tar.gz baseimage-docker-mages
# pull the base image for our templates
docker pull phusion/baseimage

# create the directories for the users and shares
mkdir -p /srv/homes
mkdir -p /srv/shares

# install the LDAP client tools
# we need to know all LDAP users because the home/share directories will belong to them
$INSTALL libpam-ldapd

# configure that we want to use LDAP for passwd etc.
sed -i 's/compat/compat ldap/' /etc/nsswitch.conf

# TODO:
#  - clone the repository with the Dockerfiles
#  - build the images: LDAP (or NIS), IPython etc.
