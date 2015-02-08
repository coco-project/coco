# ipynbsrv

> IPython Notebook Multi-User Server

## Setup

The following introduction steps explain how to setup a fresh box as an IPython notebook multi-user server.    
If you follow the whole guide step-by-step, you should end-up with a fully functional, ready-to-use system.

### Requirements

- a dedicated hardware/virtualized node (will be the `Docker` host)
- around 4GB of ram (at very least 2GB as per the `Docker` requirements)
- some basic Linux skills

### Tested Distributions

- CentOS 7 (in theory only)
- Ubuntu 14.04 (LTS)
- Ubuntu 14.10

> **Recommended distro:** Ubuntu 14.04 (LTS)

### Dedicated Node

Everything starts at the dedicated node, which will be configured to host Docker containers. We assume you already installed a fresh copy of the recommended distro on the machine and are connected to it either directly or via SSH.

To make the setup as easy as possible, we wrote a tiny shell script that will perform all needed operations for you. Just fetch and execute it as follow:

```bash
$ apt-get -y install wget  # or yum for EL
$ BRANCH=master  # use develop for development version
$ wget https://git.rackster.ch/fhnw/ipynbsrv/raw/$BRANCH/scripts/setup_docker_host.sh
$ chmod +x setup_docker_host.sh && ./setup_docker_host.sh
```

> Note: Commands prefixed with `$` are meant to be run under `root` account.

All it does is, create some directories inside `/srv/ipynbsrv`, install the Docker packages/environment and configure the system to use `LDAP` as an additional backend for user management.

**Ubuntu only:** There is one thing you should double-check (we noticed serveral *problems* here) however. Open the file `/etc/nsswitch.conf` and ensure the lines for `passwd`, `group` and `shadow` end with `ldap`, like so:

```bash
passwd:         compat ldap
group:          compat ldap
shadow:         compat ldap
```

### LDAP Container

> It is already time to bootstrap your first Docker container. Yay!

The Django application (more on that later) itself and some core features like `user shares` depend on a centralized account directory. We have choosen an LDAP server for that purpose, so the next thing you're going to do is to create a container for it.

Again, there is a shell script available that will perform most operations for you.    
Start over by issueing:

```bash
$ wget https://git.rackster.ch/fhnw/ipynbsrv/raw/$BRANCH/scripts/create_ldap_container.sh
$ chmod +x create_ldap_container.sh && ./create_ldap_container.sh
```

and follow the introductions printed on screen.

If everything went well, you should end up with an  **All done!** message.

#### User Management

As said, we will use the newly created container for user management. So why not create one right away?

> To be honest, we are not LDAP experts at all. We therefor use a graphical application called `Apache Directory Studio` to manage our users/groups. Head over and install a local copy for the next steps: [https://directory.apache.org/studio/downloads.html](https://directory.apache.org/studio/downloads.html)

> Note: At this stage it is assumed that you have created the LDAP container, installed the `Apache Directory Studio` and know the IP address of your dedicated box (Docker host).

Open `Apache Directory Studio` and create a new connection:

    File -> New -> LDAP Browser -> LDAP Connection

Enter the IP address of your dedicated box into the `Hostname` field and verify the parameters by clicking on `Test connection`. If it works, you can continue to the next wizard page.

You will be asked for authentication credentials. Fill them like this:

    Authentification method: Simple Authentification
    Bind DN or user: cn=admin,dc=ipynbsrv,dc=ldap
    Bind password: "the password you took when creating the LDAP container"

and verify they are correct. If they are, you can finish the wizard and connect to your LDAP container.

You should have a view similiar to this:

![Apache Directory Studio Connection](https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/docs/img/apache_directory_studio_connection.png)

##### Creating Records

Now that you are connected to the LDAP server, we can continue by creating a new group (needed by the user) and the user itself afterwards.

###### Creating a Group

    Right-click on "ou=groups" -> New -> New Entry -> Create entry from scratch

In the upcoming dialog, choose the object class `posixGroup`, click `Add` and go on to the next screen, which you should fill in like this:

![Apache Directory Studion Group Creation CN](https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/docs/img/apache_directory_studio_group_cn.png)

> The value of `cn` is the desired username for which this group is.

Click `Next` and enter a group ID. If this is your first group (and it should be), enter something like `2500` (so we have some offset to the default system groups which are around `500`) and finish the process.

Again, you should end up with a view like this:

![Apache Directory Studio Group Overview](https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/docs/img/apache_directory_studio_group.png)

I have already right-clicked somewhere in the information window, because we need to add another attribute to the group:

    Right-click -> New Attribute -> memberUid -> Finish

and enter the same username in the red-colored field. Done!

![Apache Directory Studio Group Overview](https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/docs/img/apache_directory_studio_group_final.png)

> Note: From now on, you should choose `Use existing entry as template` when creating a new group. That way you do not have to fill in everything again each time (**but do not forget to change the username fields**).

###### Creating a User

    Right-click on "ou=users" -> New -> New Entry -> Create entry from scratch

In the upcoming dialog, choose the object classes `inetOrgPerson` and `posixAccount`, click `Add` and go on to the next screen.

As with the group, use `cn=username` as `RND` and click `Next`. You end up with a window that has some red-bordered fields (`gidNumber`, `sn` etc.), which you must fill out like on the screen below:

![Apache Directory Studio User Wizard](https://git.rackster.ch/fhnw/ipynbsrv/raw/develop/docs/img/apache_directory_studio_user.png)

> The `gidNumber` is the ID of the group you have just created. I like to keep it in sync with the `uidNumber`, so it is easier to remember.

Close the window by clicking on `Finish`. As a last step, you have to add a password to this user account. Proceed as follow:

    Right-click -> New Attribute -> userPassword -> Finish

and enter the desired password in the popping-out window. Done.

> Right now, only the default (and not so secure) `MD5` hashing algorithm is supported...

> Note: From now on, you should choose `Use existing entry as template` when creating a new user. That way you do not have to fill in everything again each time (**but do not forget to change the username/group/password fields**).

### Postgres Container

As most useful applications, we need a database to store application information. We decided to use `Postgres` for that purpose. For that reason, we're going to create yet another container.

Again, there is a shell script available that will perform most operations for you.    
Start over by issueing:

```bash
$ wget https://git.rackster.ch/fhnw/ipynbsrv/raw/$BRANCH/scripts/create_postgresql_container.sh
$ chmod +x create_postgresql_container.sh && ./create_postgresql_container.sh
```

and follow the introductions printed on screen.

If everything went well, you should end up with an  **All done!** message.

> That was an easy one, wasn't it?

### Web Interface (WUI) Container

The WUI container is the trickiest one to setup, yet everyone should be able to suceed. The container will communicate with the others we have created (`LDAP` and `Postgres`) and expose our web application over `HTTP`.

Yes, you have guessed correctly. There is yet another script to bootstrap the container for you:

```bash
$ wget https://git.rackster.ch/fhnw/ipynbsrv/raw/$BRANCH/scripts/create_wui_container.sh
$ chmod +x create_wui_container.sh && ./create_wui_container.sh
```

It will bring you right into the container, where you need to issue all the commands found below.

#### LDAP

As already done on the dedicated node, we need to install and configure the `PAM LDAP` module:

```bash
$ apt-get update
$ apt-get -y install libpam-ldap
```

When prompted, enter:

    LDAP server: ldap://ipynbsrv.ldap/
    Distinguished name: dc=ipynbsrv,dc=ldap
    3, No, No

There is one thing you should double-check. Open the file `/etc/nsswitch.conf` and ensure the lines for `passwd`, `group` and `shadow` end with `ldap`, like so:

```bash
passwd:         compat ldap
group:          compat ldap
shadow:         compat ldap
```

#### Nginx/OpenResty

Because we need special Nginx modules, we decided to use the `OpenResty` derivate, which includes them.    
Sadly we cannot install the package via `apt/aptitude`, but need to compile it from source:

```bash
$ OPENRESTY_VERSION=1.7.7.1
$ apt-get -y install libreadline-dev libncurses5-dev libpcre3-dev libssl-dev perl make wget

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

To make it auto-start on boot, create the file `/etc/my_init.d/nginx.sh` with those lines inside:

```bash
#!/bin/sh
exec /usr/local/openresty/nginx/sbin/nginx
```

and ensure it is executable:

```bash
chmod +x /etc/my_init.d/nginx.sh
```

#### Python/uwsgi/npm

Not much to say here, those are just some of the packages (mainly Python stuff) we need.

```bash
$ apt-get -y install python-pip uwsgi-plugin-python
$ apt-get -y install python-dev libldap2-dev libsasl2-dev libssl-dev  # for django-auth-ldap
$ apt-get -y install python-psycopg2  # for Django PostgreSQL
$ apt-get -y install nodejs-legacy npm
$ npm -g install bower less  # for frontend assets
$ pip install mkdocs  # for the user guide
```

#### Django/Application

Finally here, you are going to clone the source code repository, create a dedicated user (things should not be run under `root`, should they?) and populate the database.

First, install the `git` version control system:

```bash
$ apt-get -y install git
```

and continue by creating the dedicated user and cloning the repository:

```bash
$ useradd --home-dir /srv/ipynbsrv --create-home --system ipynbsrv
$ su ipynbsrv
```

```bash
cd ~
mkdir -p data/homes data/public data/shares
BRANCH=master  # use develop for development version
git clone -b $BRANCH https://git.rackster.ch/fhnw/ipynbsrv.git _repo
ln -s /srv/ipynbsrv/_repo/wui/ /srv/ipynbsrv/www
```

As `root` again (use `exit` to become `root`), install some more Python modules and configure `Nginx`:

```bash
$ cd /srv/ipynbsrv/_repo/wui/
$ pip install -r requirements.txt
$ mkdir -p /var/run/ipynbsrv/
$ mkdir /usr/local/openresty/nginx/conf/sites-enabled
$ ln -s /srv/ipynbsrv/_repo/confs/nginx/ipynbsrv.conf /usr/local/openresty/nginx/conf/sites-enabled/

$ nano /usr/local/openresty/nginx/conf/nginx.conf
```

and change these values to:

```bash
user  www-data;
worker_processes  auto;

http {
    # remove the servers already defined here
    include /usr/local/openresty/nginx/conf/sites-enabled/*.conf;
}
```

and you are mostly done with the preparation!

##### Django Application

The final steps include defining the Django application settings, populating the database and some other little changes.

Start over by changing to the `ipynbsrv` user account:

```bash
$ su ipynbsrv
cd ~/www
```

###### settings.py

Everyone familiar with `Django` knows this file. It contains the application's settings.    
Some of them need adjustment, so open it with `nano ipynbsrv/settings.py` and define those options:

| Option                     | Value
|----------------------------|-------------------------------------
| SECRET_KEY                 | Some randomly generated characters
| DEBUG                      | Change to `False`
| TEMPLATE_DEBUG             | Change to `False`
| ALLOWED_HOSTS              | ['*']
| DATABASES.default.PASSWORD | The `Postgres` password you took
| DATABASES.ldap.PASSWORD    | The `LDAP` admin password you took
| TIME_ZONE                  | Your timezone (e.g. `Europe/Zurich`)
| DOCKER\_API\_VERSION       | Get it with `docker version`
| DOCKER\_IFACE\_IP          | The IP address of the `docker0` iface

> Note: For `DOCKER_IFACE_IP` issue `ifconfig docker0 | grep inet\ addr:` on the dedicated node.

All other values should be fine.

Now that you have the `DOCKER_IFACE_IP`, open `/srv/ipynbsrv/_repo/confs/nginx/ipynbsrv.conf` and replace:

    proxy_pass  http://172.17.42.1:$1;

with:

    proxy_pass http://"DOCKER_IFACE_IP":$1;

###### manage.py

`manage.py` is Django's utility script to perform setup and maintenance tasks.

Use it to create migrations (if any) and populate/alter the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

Because we are using `LESS` to produce `CSS` and `bower` to manage external dependencies, you need to compile the styles and install the deps (like `jQuery` etc.):

```bash
cd ipynbsrv/wui/static/
bower install  # installs external dependencies
mkdir css
lessc --compress less/main.less css/main.css  # compile LESS to CSS
cd ~/www
```

The user guide must be generated as well:

```bash
cd /srv/ipynbsrv/_repo/docs/user-guide/
mkdocs build --clean
```

Last but not least, finalize the whole setup by issueing:

```bash
python manage.py collectstatic
python manage.py createsuperuser
```

which will create a local superuser account (the admin account).

Leave the container with:

```bash
exit
exit
```

so the script continues. It will create a local image from the container and bootstrap a new instance using that one. As soon as it has completed, you're all done.

Congratulations!

## What's Next?

- [Build the Docker base image for user container images (`base-ldap`)](building-images.md#base-ldap)
- [Build the IPython Notebook Docker image](building-images.md#ipython3-notebook)