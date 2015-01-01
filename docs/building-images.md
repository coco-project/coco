# ipynbsrv

> IPython Notebook Multi-User Server

## Building Images

The following chapters will tell you how to build Docker images to be used in ipynbsrv. Through the currently available images aren't very generic, one should be able to create others as well by extracting some of the information found here.

### Base LDAP

This is the base image for all images that will be made available to end users. It performs operations such as:

- Initializing the LDAP client/configuration
- Disable root login
- Prevent non-authorized (in the sense of not owner) users from accessing the container
- etc.

Other images should inherit from it by declaring:

    FROM ipynbsrv/base-ldap:latest

at the very top of the corresponding `Dockerfile`.

To build the image, execute the following commands on the Docker host:

```bash
$ IMG_NAME=base-ldap
$ mkdir ${IMG_NAME}
$ cd ${IMG_NAME}
$ wget https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/docker/ldap/Dockerfile
$ docker build -t ipynbsrv/${IMG_NAME} .
```

### IPython3 Notebook

The **ipynbsrv** stack was documented and developed as part of a school project. The main goal was the creation of a multi-user IPython notebook server, so it's not a surprise the only available image right now is an IPython one.

Within the `Dockerfile` and startup script, those actions are performed:

- Install the latest IPython version
- Create a working directory `/data` which contains the user's home directory, the shares and public dirs
- Initialize an IPython profile, set the `base_url` and start a new notebook instance
- some more...

To build the image, issue the commands below:

> Make sure you have already built the `base-ldap` image. It is the base image in use!

```bash
$ IMG_NAME=ipython3-notebook
$ mkdir ${IMG_NAME}
$ cd ${IMG_NAME}
$ wget https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/docker/ipython/Dockerfile
$ wget https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/docker/ipython/${IMG_NAME}.bin
$ docker build -t ipynbsrv/${IMG_NAME} .
```

During the build process, some errors might show up. That is because some commands try to open an interactive dialog - and that is not possible. Just ignore them for now.

#### Adding to Django

To make the image available to end users, you have to add the image to our application.

Open the administration interface (`http://"dedicated node"/admin`) and login with the superuser account. Click on `Images` in the `IPython Notebook Server Web Interface` box and create a new entry like on the screen below:

![Django Admin Interface: Adding the IPython Notebook image](https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/docs/img/django_add_ipython_image.png)