FROM ipynbsrv/base-ldap:latest
MAINTAINER FHNW <ipynbsrv@fhnw.ch>

ENV HOME /root
CMD ["/sbin/my_init", "--", "/usr/local/bin/init_cmd"]

# Install system-wide pip for IPython
RUN apt-get update && apt-get -y install python-dev python-pip
# Install IPython + Notebook
RUN pip install terminado
RUN pip install --pre "ipython[all]"

# Packages and modules needed by nbconvert or .html export
RUN apt-get -y install pandoc
RUN pip install pygments

# Copy my_init services into the container and make sure only root user can change it
ADD ipython2-notebook.bin /usr/local/bin/init_cmd
RUN chown root:root /usr/local/bin/init_cmd
RUN chmod 0644 /usr/local/bin/init_cmd
RUN chmod +x /usr/local/bin/init_cmd

# Expose the IPython notebook server; use --publish-all=true
EXPOSE 8888

# Clean up APT when done.
RUN apt-get autoremove && apt-get autoclean && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /etc/*-
