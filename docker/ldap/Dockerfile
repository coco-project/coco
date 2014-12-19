# Use phusion/baseimage as base image. To make your builds reproducible, make
# sure you lock down to a specific version, not to `latest`!
# See https://github.com/phusion/baseimage-docker/blob/master/Changelog.md for
# a list of version numbers.
FROM phusion/baseimage:0.9.15
MAINTAINER FHNW <ipynbsrv@fhnw.ch>

# Set correct environment variables.
ENV HOME /root

# Regenerate SSH host keys. baseimage-docker does not contain any, so you
# have to do that yourself. You may also comment out this instruction; the
# init system will auto-generate one during boot.
#RUN /etc/my_init.d/00_regen_ssh_host_keys.sh

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# Prevent root logins
RUN passwd -d root && passwd -l root

# Install LDAP client packages and other tools
RUN apt-get update && apt-get -y install libpam-ldap sed

# Configure the LDAP client (server to use etc.)
RUN sed -i 's/base dc=example,dc=net/base dc=ipynbsrv,dc=ldap/' /etc/ldap.conf
RUN sed -i 's/uri ldapi:\/\/\//uri ldap:\/\/ipynbsrv.ldap/' /etc/ldap.conf
RUN sed -i 's/rootbinddn cn=manager,dc=example,dc=net/rootbinddn cn=admin,dc=ipynbsrv,dc=ldap/' /etc/ldap.conf
RUN sed -i 's/compat/compat ldap/' /etc/nsswitch.conf

# Allow password based SSH login
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

# Disallow login for users where the home directory does not exist -> in our case, those are not the container owner
RUN sed -i 's/DEFAULT_HOME/#DEFAULT_HOME/' /etc/login.defs
RUN echo "DEFAULT_HOME no" >> /etc/login.defs
RUN cat /etc/bash.bashrc > /etc/bash.bashrc_pkg
RUN [ "echo", "[[ ! -x $HOME ]] && exit 1", ">", "/etc/bash.bashrc" ]
RUN cat /etc/bash.bashrc_pkg >> /etc/bash.bashrc
RUN rm /etc/bash.bashrc_pkg

# Create the data directory. /home, /public and /shares will be mounted inside
RUN mkdir /data

# Expose SSH port
EXPOSE 22

# Clean up APT when done.
RUN apt-get autoremove && apt-get autoclean && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /etc/*-
