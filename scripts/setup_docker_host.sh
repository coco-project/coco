#!/bin/bash

#######################################################################################
# This script will setup the host the script is executed on as an ipynbsrv Docker host.
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
    # enable memory and swap accounting (not used yet, --memory=limit)
    sed -i 's/GRUB_CMDLINE_LINUX="find_preseed=\/preseed.cfg noprompt"/GRUB_CMDLINE_LINUX="find_preseed=\/preseed.cfg noprompt cgroup_enable=memory swapaccount=1"/' /etc/default/grub
    update-grub
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
# pull the base image for our templates
docker pull phusion/baseimage:0.9.16

# create the data directories
DATA="/srv/ipynbsrv"
mkdir -p $DATA
# create the LDAP/PostgreSQL container data directories
mkdir -p $DATA/ldap
mkdir -p $DATA/postgresql
# create the directories for the users and shares
mkdir -p $DATA/homes
mkdir -p $DATA/public
mkdir -p $DATA/shares
# ensure secure permissions. just in cast a custom umask is set
chown -R root:root $DATA
chmod -R 0755 $DATA

# install the LDAP client tools
# we need to know all LDAP users because the home/share directories will belong to them
echo "------------------------------------------------------------"
echo "Going to install the PAM LDAP package..."
echo "When asked for the nsswitch services to configure, choose 'group', 'passwd' and 'shadow'."
echo "------------------------------------------------------------"
sleep 2
if [ $PS == "deb" ]; then
    $INSTALL libpam-ldap
else
    $INSTALL nss-pam-ldapd
    authconfig-tui
    # disable caching server, made problems
    systemctl stop nslcd.service
    systemctl disable nslcd.service
fi
# configure that we want to use LDAP for passwd etc.
sed -i 's/compat/compat ldap/' /etc/nsswitch.conf

echo "------------------------------------------------------------"
echo "All done! You should now reboot the machine."
echo "------------------------------------------------------------"
