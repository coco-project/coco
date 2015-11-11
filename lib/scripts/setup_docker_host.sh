#!/bin/bash

#######################################################################################
# This script will setup the host the script is executed on as a coco Docker host.
# For that, it installs the Docker environment, creates the required data directories
# and configures the system to be an LDAP client.
#
# TODO:
#   - fix CentOS 7
#   - detect CentOS/EL version: CentOS 6 has Docker packages in EPEL repo
#
# last updated: 02.02.2015
#######################################################################################

if [ "$EUID" -ne 0 ]; then
  echo "This script must be executed as root user."
  exit 1
fi

# detect the package manager
if `which apt-get &> /dev/null`; then
    PS="deb"
    INSTALL="apt-get install -y"
elif `which yum &> /dev/null`; then
    PS="rpm"
    INSTALL="yum install -y"
else
    echo "Your distribution is not supported. Aborting the setup."
    exit 1
fi

# install prequisites
$INSTALL curl sed sudo tar

# install docker
if [ $PS == "deb" ]; then
    curl -sSL https://get.docker.com/ubuntu/ | sh
    service docker restart
    # autostart on boot
    update-rc.d docker defaults
    update-rc.d docker enable
else
    $INSTALL docker
    systemctl start docker.service
    # autostart docker on boot
    systemctl enable docker.service
fi

# install docker-bash/-ssh
curl --fail -L -O https://github.com/phusion/baseimage-docker/archive/master.tar.gz
tar xzf master.tar.gz
./baseimage-docker-master/install-tools.sh
rm -rf master.tar.gz baseimage-docker-master

# create the data directories
DATA="/srv/coco"
mkdir -p $DATA
# create the LDAP/PostgreSQL container data directories
mkdir -p $DATA/ldap
mkdir -p $DATA/postgresql
# create the directories for the users and shares
mkdir -p $DATA/data/homes
mkdir -p $DATA/data/public
mkdir -p $DATA/data/shares
# ensure secure permissions. just in cast a custom umask is set
chown -R root:root $DATA
chmod -R 0755 $DATA

echo "------------------------------------------------------------"
echo "All done! You should now reboot the machine."
echo "------------------------------------------------------------"
