# Open vSwitch

> Guide to setup Open vSwitch as `ipynbsrv`'s internal networking solution.

## Introduction

As per the `ipynbsrv` networking requirements, every node must have its unique IPv4 address within a private/internal network that cannot be reached from the outside. With Open vSwitch, we can setup such a network between our nodes. It doesn't matter which reserved IPv4 network range you pick for that network, as long as it doesn't conflict with other existing networks (check with `ifconfig` if you are unsure about other networks in use). This guide assumes the `192.168.0.0/24` network was picked.

## Installation

Open vSwitch packages are available in all major Linux distributions, so the installation should be straight-forward.
On Debian based distributions you'll have to run:

```bash
apt-get install -y openvswitch-switch openvswitch-ipsec
```

> If the nodes are protected by a firewall, make sure to open the ports `500, 1723 and 4500` as well as to allow the `esp` and `ah` IP protocols.

## Setting up the interface

Now that Open vSwitch is installed, we need to create an Open vSwitch bridge interface, which will act as the nodes' virtual switch. All of the following commands need to be executed on every node (if not stated otherwise).



To create the interface, issue:

```bash
$ ovs-vsctl add-br ovsbr0
$ ovs-vsctl set bridge ovsbr0 stp_enable=true
```

To assign an IPv4 address from the picked range to the created `ovsbr0` interface, execute the following statements:

```bash
$ ifconfig ovsbr0 up 192.168.0.1 netmask 255.255.255.0
$ ifconfig ovsbr0 mtu 1420
```

> `192.168.0.1` is the internal only IPv4 address of the current node. Make sure every node has another IP address. Usually the master node will have `x.x.x.1`.    
> ––––    
> `255.255.255.0` is the netmask of the private network. If you plan to deploy more than 254 nodes, pick a `/16` or `/8` range.    
> ––––    
> These commands are best placed in `/etc/rc.local` so they are executed on boot. Make sure to put them before `exit 0`.

## Establishing connections between the nodes

Open vSwitch is installed and running, but no connections between the nodes have been added yet. Don't worry, adding them is as simple as the installation was.

Basically, the following command needs to be executed on the two nodes between which the connection should be established. Executing that command instructs Open vSwitch to create and establish a `GRE over IPSec` connection beween the two nodes:

```bash
$ ovs-vsctl add-port ovsbr0 gre_master_slave1 -- set interface gre_master_slave1 type=ipsec_gre options:remote_ip=10.0.0.2 options:psk=ipynbsrv
```

> `gre_master_slave1` is the connection's name. It must be unique and the same on both nodes.    
> ––––    
> `10.0.0.2` is the IPv4 address under which the remote node can be reached.    
> ––––    
> `psk=ipynbsrv` is the password used to encrypt the connection.

For a minimal setup, you have to establish one connection to the master node at least. A full-meshed network might however perform better, so you're encouraged to establish additional connections between other nodes as well.

## Troubleshooting

### 1. Connections are not established after a reboot

We saw this quite often. The solution is to restart the Open vSwitch services on the nodes:

```bash
$ service openvswitch-ipsec restart && service openvswitch-switch restart
```

> Other services connecting to remote nodes via the internal network might need a restart as well, as soon as the connections have been established.