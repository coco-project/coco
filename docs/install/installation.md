# Installation

> A step-by-step guide on how to setup an `ipynbsrv` server/infrastructure.

## Introduction

Before we begin with the installation, it is incessant to leave a few words about the concepts and architecture of `ipynbsrv`. The main reason for that is that `ipynbsrv` is not really an application, but a giant project consisting of several (independent) components – each of it playing an important role within the whole setup. Because most of these components are exchangeable, the necessarily install steps depend on the concrete component implementation/specification you pick. This makes it harder to get started, but once you understand the concepts and ideas behind that approach, you'll be loving it – promised.

### Architecture

Basically, the whole can be seen as a multilayered architecture project. Each component is either part of one layer or defines the layer itself. Additionally, each component can itself be structured and multilayered (i.e. the software stuff).

Because there has to be at least one (sub)component plugging all the others together and coordinating their behavior, minimal requirements are specified for each of them. These specifications come either in the form of contracts (i.e. for the software backends) or formal descriptions (i.e. the networking). Everything together can therefor only work, if every single component fully fulfills its relevant specifications.

Since a specification contains only the minimal set of requirements, two components that are totally specification conform, can have nearly nothing in common. For that reason, every component has to provide its own setup instructions (if any). Depending on the component's layer, its install steps may affect the installation process of other components as well. The type of deployment (single-server or multi-server) can have an impact too. For that reason, one has to inspect every component's install guide before actually starting. This makes the installation – as initially said – complex.

### Components

As touched in the previous passages, `ipynbsrv` consists of mostly independent and replaceable components. The following list gives you a brief and shorten overview of the different components currently involved:

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

> If you are aware of one not listed, plese submit a merge request. Thanks! 

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

Now that you are familiar enough with `ipynbsrv`'s architecture, we can proceed to the actual installation steps. Because the setup you're going to deploy depends a lot on the components you choose, this steps are very generic.

The following chapters assume you have a running box (see **Requirements**) and an open `root` console. Commands prefixed with `$` are meant to be run as `root`.

### 1. Setting up Networking

The very first component to setup is networking. Right now, you have the choice between *Docker* and *Open vSwitch* (see **Available Components**). If you plan to deploy a multi-server setup, you cannot use *Docker*. The actual installation steps are defined by the component, so head over to its documentation to get specification comply networking.

> The reference implementation uses `Open vSwitch`.

### 2. Setting up the Core Infrastructure (Part 1)

Setting up the core infrastructure is splitted into two parts. The main reason for that is that backends (see below) might influent the way you have to deploy the core infrastructure. Because of that, this first part only includes the steps that *should* not vary, while the second part contains the rest.

#### 2.1 Deploying a PostgreSQL server

The core application is expecing a working PostgreSQL server to store its data. Make sure you have one running somewhere the application can access it.

> The reference implementation uses the official PostgreSQL Docker container image and links the container into the application container.

#### 2.2 Deploying an LDAP server

The *Lightweight Directory Access Protocol* is a widly supported protocol to communicate with directory servers like Window's Active Directory. The core application needs full access to such a server to store user and group information on it. While you're free to use other procotols/servers as well, this most likely does not work at the moment.

The server must have two organizational units for users and groups, best named `users` and `groups`. Depending on the container backend you pick, created containers (also on remote nodes) need to access the server.

> The reference implementation runs `slapd` within a Docker container. To ensure containers and remote nodes have access to it, the services is binded onto the internal IPv4 address of the master node.

### 3. Setting up the Storage Backend

Storage backends define the way how and where directories and files are stored. This includes the user's home directories, publication directories and user created share directories.

Because the core application as well as user containers need to access these resources (directories and files), the storage backend should be the first backend to setup.

> The reference implementation uses the `LocalFileSystem` backend. The working directory is set to `/srv/ipynbsrv/data`.

### 4. Setting up the Container Backend

...

> The reference implementation uses the `Docker` backend in combination with the `HttpRemote` proxy backend (if deploying a multi-server setup).

### 5. Setting up the User Backend

...

> The reference implementation uses the `LdapBackend` backend and reuses the LDAP server from the core infrastructure to simulate an external server.

### 6. Setting up the Core Infrastructure (Part 2)

### 7. Configuring the Application

...