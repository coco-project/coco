# Open vSwitch

> Guide to setup Open vSwitch as `coco`'s internal networking solution.

## Introduction

As per the `coco` networking requirements, every node must have its unique IPv4 address within a private/internal network that cannot be reached from the outside. With Open vSwitch, we can setup such a network between our nodes. It doesn't matter which reserved IPv4 network range you pick for that network, as long as it doesn't conflict with other existing networks (check with `ifconfig` if you are unsure about other networks in use). This guide assumes the `192.168.0.0/24` network was picked.

## Installation

Open vSwitch packages are available in all major Linux distributions, so the installation should be straight-forward.
On Debian based distributions you'll have to run:

```bash
apt-get install -y openvswitch-switch
```

## Setting up the interface

Now that Open vSwitch is installed, we need to create an Open vSwitch bridge interface, which will act as the nodes' virtual switch. All of the following commands need to be executed on every node (if not stated otherwise).

To create the interface and make it auto-start on boot, issue:

```bash
$ nano /etc/network/interfaces.d/coco-project
```

and append the following lines:

```bash
auto coco_br0
allow-ovs coco_br0
iface coco_br0 inet static
    address 192.168.0.1
    netmask 255.255.255.0
    mtu 1420
    ovs_type OVSBridge
    ovs_extra set bridge ${IFACE} stp_enable=true
```

> `192.168.0.1` is the internal only IPv4 address of the current node. Make sure every node has another IP address. Usually the master node will have `x.x.x.1`.    
> ––––    
> `255.255.255.0` is the netmask of the private network. If you plan to deploy more than 254 nodes, pick a `/16` or `/8` range.

Complete the setup by adding the bridge to the internal Open vSwitch database too:

```bash
ovs-vsctl add-br coco_br0
```

## Establishing connections between the nodes

Open vSwitch is installed and running, but no connections between the nodes have been added yet. Don't worry, adding them is as simple as the installation was.

Basically, the following commands needs to be executed on the two nodes between which the connection should be established:

```bash
nano /etc/network/interfaces.d/coco-project
```

and add an internal Open vSwitch port:

```bash
auto coco_gre1
allow-coco_br0 coco_gre1
iface coco_gre1 inet manual
    ovs_bridge coco_br0
    ovs_type OVSPort
    ovs_extra set interface ${IFACE} type=gre options:remote_ip=10.0.0.2
```

> `coco_gre1` is the connection's name. It must be unique and the same on both nodes.    
> ––––    
> `10.0.0.2` is the IPv4 address under which the remote node can be reached.

Additionally, add the following line (or only the port if already there) to the bridge you created during the setup phase:

```bash
...
ovs_extra set bridge ${IFACE} stp_enable=true
ovs_ports coco_gre1  # newly added
```

Last but not least, add the port to the database:

```bash
ovs-vsctl add-port coco_br0 coco_gre1
```

> To make sure the GRE connections are established before running i.e. custom scripts, you can place `ping -c 1 10.0.0.2` in `/etc/rc.local` where `10.0.0.2` is the IPv4 address of the remote node you want to reach. Every command placed after this line will be able to communicate with the remote node.
