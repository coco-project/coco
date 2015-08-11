# Installation

> A step-by-step guide on how to setup an `ipynbsrv` server/infrastructure.

## Introduction

Before we begin with the installation, it is incessant to leave a few words about the concepts and architecture of `ipynbsrv`. The main reason for that is that `ipynbsrv` is not really an application, but a giant project consisting of several (independent) components – each of it playing an important role within the whole setup. Since most of these components are exchangeable, the necessarily install steps will vary depending on the concrete component implementation/specification you pick. This makes it harder to get started, but once you understand the concepts and ideas behind that approach, you'll be loving it – promised.

### Architecture

Basically, the whole can be seen as a multilayered architecture project. Each component is either part of one layer or defines the layer itself. Additionally, each component can be structured and multilayered itself (i.e. the software stuff).

Because there has to be at least one (sub)component plugging all the others together and coordinating their behavior, minimal requirements are specified for each of them. These specifications come either in the form of contracts (i.e. for the software backends) or formal descriptions (i.e. the networking). Everything together can therefor only work, if every single component fully fulfills its relevant specifications.

Since a specification contains only the minimal set of requirements, two components that are totally specification conform, can have nearly nothing in common. For that reason, every component has to provide its own setup instructions (if any). Depending on the component's layer, its install steps may affect the installation process of other components as well. Besides, the type of deployment (single-server or multi-server) can have an impact too. For that reason, one has to inspect every component's install guide before actually starting. This makes the installation – as initially said – complex.

### Components

As touched in the previous sections, `ipynbsrv` consists of mostly independent and replaceable components. The following list gives you a brief and shorten overview of the different components currently involved:

- **Networking:** To limit access to user created containers to its owner, there has to be a network that is not reachable from the outside. An internal only network has to exist. This network is used for other thing as well and is the most low-end component. The standard implementation uses `Open vSwitch` to create such a network.
- **Core Infrastructure:** The core infrastructure itself is not a component (or if you'd like to call it like that anyway, think of it as one giant component consisting of various parts). Beside a handful of directories on the filesystem, it includes an LDAP directory server, a Postgresql DB server, an Nginx web server and a few Django applications. The project won't work without them and they are not meant to be replaceable, that's why they are grouped under the *Core Infrastructure* name. The default implementation/install guide uses Docker containers to run these services, but one is free to install them somewhere else.
- **Backends:** Backend components are on one hand the most powerful abstraction in `ipynbsrv` (they abstract the storage, container and user/group backends), the most complex on the other hand. Take the `Docker` container backend as an example: it consists of the Docker platform (so it has to provide an install guide for that), Python code to communicate with that platform (it has to provide an `ipynbsrv.contract.container_backend` implementation for that) and a set of preconfigured images to run containers from (it has to provide `Dockerfile`s for that). Depending on the deployment (i.e. multi-server), additional tools like the `Docker Registry` are needed as well.

If you have (roughly) understood this concept of components, you're ready to go.

> PS: Do I have complied with my promise? ;)

## Requirements

The following requirements are only valid for the core infrastructure. Each component may define own requirements as well, so don't take the ones listed here as given:

- a dedicated hardware or virtualized node
- at least 2GB of RAM
- intermediate *nix skills

### Tested operating systems

- OS X 10.10.x (Yosemite)
- CentOS 7 64-bit (in theory only)
- Ubuntu 14.04 (LTS)
- Ubuntu 14.10
- Ubuntu 15.04 (LTS)
- Ubuntu 15.10

> **Recommended OS:** Ubuntu 15.04 (LTS) 64-bit

## Available Components

Below you can find a list of all currently available components. Make sure to consult their documentations before you start, as some might only work in combination with others.

> If you are aware of one not listed, please submit a merge request. Thanks! 

### Container Backends

- [Docker](https://git.rackster.ch/ipynbsrv/backends/blob/master/docs/container_backends.md#docker)
- [HttpRemote](https://git.rackster.ch/ipynbsrv/backends/blob/master/docs/container_backends.md#httpremote)

### Networking

- [Docker](https://git.rackster.ch/ipynbsrv/backends/blob/master/docs/container_backends.md#docker) (single-server only)
- [Open vSwitch](https://git.rackster.ch/ipynbsrv/ipynbsrv/blob/master/docs/install/networking/openvswitch.md)

### Storage Backends

- [LocalFileSystem](https://git.rackster.ch/ipynbsrv/backends/blob/master/docs/storage_backends.md#localfilesystem)

### User/Group Backends

- [LdapBackend](https://git.rackster.ch/ipynbsrv/backends/blob/master/docs/usergroup_backends.md#ldapbackend)

## Getting started

> If you are looking for an easier install guide (this one describes the modular approach), the [Easy Install Guide](https://git.rackster.ch/ipynbsrv/ipynbsrv/blob/master/docs/install/easy_installation.md) might be for you.    
> ––––    
> If you landed here and have not yet read the **Introduction** chapter, do yourself a flavor and start there.

Now that you are familiar enough with `ipynbsrv`'s architecture, we can proceed to the actual installation steps. Because the setup you're going to deploy depends extensively on the components you choose, the following steps are very generic.

The following chapters assume you have a running box (see **Requirements**) and an open `root` console. Commands prefixed with `$` are meant to be run as `root`.

### 1. Setting up Networking

The very first component to setup is networking. Right now, you have the choice between *Docker* and *Open vSwitch* (see **Available Components**). If you plan to deploy a multi-server setup, you cannot use *Docker*. The actual installation steps are defined by the component, so head over to its documentation to get specification comply networking.

> The reference implementation uses `Open vSwitch`.

### 2. Setting up the Core Infrastructure (Part 1)

Setting up the core infrastructure is splitted into two parts. The main reason for that is that backends (see below) might influent the way you have to deploy the core infrastructure. Thus, this first part only includes the steps that *should* not vary, while the second part contains the rest.

#### 2.1 Deploying a PostgreSQL server

The core application relies on a working PostgreSQL server to store its data. Make sure you have one running somewhere the application can access it.

> The reference implementation uses the official PostgreSQL Docker container image and links the container into the application container.

#### 2.2 Deploying an LDAP server

The *Lightweight Directory Access Protocol* is a widely supported protocol to communicate with directory servers like Window's Active Directory. The core application needs full access to such a server to store user and group information on it. While you're free to use other procotols/servers as well, this most likely does not work at the moment.

The server must have two organizational units for users and groups, best named `users` and `groups`. Depending on the container backend you pick, created containers (also on remote nodes) need to access the server.

> The reference implementation runs `slapd` within a Docker container. To ensure containers and remote nodes have access to it, the services is binded onto the internal IPv4 address of the master node.

### 3. Setting up the Storage Backend

Storage backends define the way how and where directories and files are stored. This includes the user's home directories, publication directories and user created share directories.

Because the core application as well as user containers need to access these resources (directories and files), the storage backend should be the first backend to setup. Again, open the documentation of the storage backend in use to see how it needs to be set up.

> The reference implementation uses the `LocalFileSystem` backend. The working directory is set to `/srv/ipynbsrv/data`.

### 4. Setting up the Container Backend

Container backends are by far the most complex component to install (and implement). Since the specification for such backends do not include the required install steps, you have to read the concrete backends documentation again. It should tell you how to install the (container) isolation product itself, how to configure it so it plays nicely with `ipynbsrv`, how to add/create images for it and what additional steps are needed for a working multi-server deployment.

> The reference implementation uses the `Docker` backend in combination with the `HttpRemote` proxy backend (if deploying a multi-server setup).

### 5. Setting up the User Backend

Beside the internal usage of the `LdapBackend` for communication with the core infrastructure LDAP server (if that is the way you go), this backend (talking about it because no alternatives exist atm) can also be used to let users from an external LDAP server access the application. In general, user backends allow one to use an existing user directory to be used as `ipynbsrv`'s authentication backend.

But enough. Please consult the backend's own documentation to get it working.

> The reference implementation uses the `LdapBackend` backend and reuses the LDAP server from the core infrastructure to simulate an external server.

### 6. Setting up the Core Infrastructure (Part 2)

Now that all backends are ready and you have read there documentations for potential notes about setting up the core infrastructure, we can finally deploy the rest of the core.

#### 6.1 Deploying the Nginx Web Server

Nginx is our web server of choice. A lot of the core features (i.e. container access control) depend on it. It will be configured to serve the Django application (but not only), so make sure to install Nginx either directly on the hardware node or within a powerful enough container.

Because special Nginx modules are needed, we decided to use the OpenResty derivate, which includes them out-of-the-box. Sadly, we cannot install the package via apt/aptitude, but need to compile it from source. The following commands will help you with that:

```bash
$ OPENRESTY_VERSION=1.7.10.2
$ apt-get -y install libreadline-dev libncurses5-dev libpcre3-dev libssl-dev perl make wget  # dependencies

$ cd /usr/local/src
$ wget http://openresty.org/download/ngx_openresty-$OPENRESTY_VERSION.tar.gz
$ tar xzvf ngx_openresty-$OPENRESTY_VERSION.tar.gz
$ cd ngx_openresty-$OPENRESTY_VERSION

$ ./configure \
    --user=www-data \
    --group=www-data \
    \
    --with-ipv6 \
    --with-pcre --with-pcre-jit \
    --with-http_auth_request_module \
    \
    --without-http_echo_module \
    --without-http_xss_module \
    --without-http_coolkit_module \
    --without-http_form_input_module \
    --without-http_srcache_module \
    --without-http_lua_module \
    --without-http_lua_upstream_module \
    --without-http_memc_module \
    --without-http_redis2_module \
    --without-http_redis_module \
    --without-http_rds_json_module \
    --without-http_rds_csv_module \
    --without-lua_cjson \
    --without-lua_redis_parser \
    --without-lua_rds_parser \
    --without-lua_resty_dns \
    --without-lua_resty_memcached \
    --without-lua_resty_redis \
    --without-lua_resty_mysql \
    --without-lua_resty_upload \
    --without-lua_resty_upstream_healthcheck \
    --without-lua_resty_string \
    --without-lua_resty_websocket \
    --without-lua_resty_lock \
    --without-lua_resty_lrucache \
    --without-lua_resty_core \
    --without-http_ssi_module \
    --without-http_geo_module \
    --without-http_split_clients_module \
    --without-http_fastcgi_module \
    --without-http_scgi_module \
    --without-http_memcached_module \
    --without-http_limit_conn_module \
    --without-http_limit_req_module \
    --without-http_empty_gif_module \
    --without-http_upstream_ip_hash_module \
    --without-mail_pop3_module \
    --without-mail_imap_module \
    --without-mail_smtp_module

$ make
$ make install
```

> This will install OpenResty under `/usr/local/openresty` and Nginx under `/usr/local/openresty/nginx`.

Make sure the Nginx service is starting on boot by executing `/usr/local/openresty/nginx/sbin/nginx` during startup.

> The reference implementation is creating a dedicated Docker container for the Nginx web server and the stuff from the next chapters.

#### 6.2 Installing additional packages

Not much to say here, those are just some of the packages (mainly Python) we need:

```bash
$ apt-get -y install python-pip  # package manager
$ apt-get -y install uwsgi-plugin-python  # uwsgi plugin (used for Nginx uwsgi_pass)
$ apt-get -y install python-psycopg2  # for Django PostgreSQL
$ apt-get -y install nodejs-legacy npm
$ npm -g install bower less  # for frontend assets
$ pip install mkdocs  # for the user guide
```

#### 6.3 Deploying the Django Application

> Because no code has been publiched to `PyPie` or any other repository yet, everything needs to be installed from source. For that purpose, the source repositories are cloned via `git`. Once the project is mature enough, we expect the installation process to become easier.

##### 6.3.1 Preparing the base

As a first prerequisite, install the `git` package:

```bash
$ apt-get -y install git
```

After creating the directory where the application will resist, it is already time to clone the application repositories:

```bash
BRANCH=master
git clone -b $BRANCH https://git.rackster.ch/ipynbsrv/ipynbsrv.git _repo
```

> A smart location for the repository is `/srv/ipynbsrv/_repo`.

Since the `ipynbsrv` Django application has several dependencies, they need to be installed before the application will work:

```bash
$ cd _repo
$ pip install -r requirements.txt
```

Next, we're going to create a directory that will contain the `uwsgi` socket and tell Nginx about the application's vhost file. This virtual host configuration for Nginx makes sure that i.e. requests are send to the `uwsgi` backend:

```bash
$ mkdir -p /var/run/ipynbsrv/
$ mkdir /usr/local/openresty/nginx/conf/sites-enabled
$ ln -s /srv/ipynbsrv/_repo/lib/confs/nginx/ipynbsrv.conf /usr/local/openresty/nginx/conf/sites-enabled/
```

> The linking command assumes you have cloned the repository to `/srv/ipynbsrv/_repo`.

Last but not least, make sure the Nginx main configuration at `/usr/local/openresty/nginx/conf/nginx.conf` reflects the snippet below:

```bash
user  www-data;
worker_processes  auto;  # = CPU count

http {
    # remove the servers already defined here, but not other stuff like mime.types etc.
    include /usr/local/openresty/nginx/conf/sites-enabled/*.conf;
}
```

##### 6.3.2 Installing additional Python packages

Remember the initial note regarding unpublished packages? They can be manually installed with:

```bash
$ cd /usr/local/src
$ git clone https://git.rackster.ch/ipynbsrv/contract.git
$ cd contract && pip install -e . && cd ..
$ git clone https://git.rackster.ch/ipynbsrv/common.git
$ cd common && pip install -e . && cd ..
$ git clone https://git.rackster.ch/ipynbsrv/client.git
$ cd client && pip install -e . && cd ..
$ git clone https://git.rackster.ch/ipynbsrv/backends.git
$ cd backends && pip install -e . && cd ..
```

> Note: This chapter should be removed once the packages have been published.

##### 6.3.3 Making the application ready

After having completed the above preparation steps, the next few commands will look familiar to everyone already having used Django in the past. They are all about initializing the Django application and should be run in the repository root.

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

As we are using `LESS` to produce `CSS` and `bower` to manage external dependencies, you need to compile the styles and install the deps (like `jQuery` etc.):

```bash
$ cd ipynbsrv/web/static
$ bower install --allow-root  # installs external dependencies
$ mkdir css
$ lessc less/main.less css/main.css  # compile LESS to CSS
$ cd ../../..
```

> If `bower install` doesn't work, try forcing `git` to use the HTTP protocol: `git config --global url.https://.insteadOf git://`

The user guide must be generated as well:

```bash
$ cd docs/user-guide
$ mkdocs build --clean
```

Last but not least, finalize the whole setup by issueing:

```bash
python manage.py collectstatic
python manage.py createsuperuser
```

which will create a local superuser account (the admin account).

### 7. Configuring the Application

TODO: Login to admin, define variables (backends), add backends and servers and images.