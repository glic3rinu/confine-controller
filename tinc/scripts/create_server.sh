#!/bin/bash

# Should be executed as root

# USAGE create_server.sh NET_NAME IPV6_PREFIX
#       create_server.sh confine 2001:db8:cafe


NET_NAME=$1
IPV6_PREFIX=$2

if [[ ! $(grep $NET_NAME /etc/tinc/nets.boot) ]]; then
    echo $NET_NAME >> /etc/tinc/nets.boot
fi

mkdir -p /etc/tinc/$NET_NAME/hosts

cat <<- EOF > /etc/tinc/$NET_NAME/tinc.conf
	BindToAddress = 0.0.0.0
	Port = 655
	Name = server
EOF

# TODO autodiscover somhow the netmask
echo "Subnet = $IPV6_PREFIX:0:0:0:0:2/128" > /etc/tinc/$NET_NAME/hosts/server

tincd -n $NET_NAME -K


# TODO autodiscover somhow the netmask
cat <<- EOF > /etc/tinc/$NET_NAME/tinc-up
	#!/bin/sh
	ip -6 link set "\$INTERFACE" up mtu 1400
	ip -6 addr add $IPV6_PREFIX:0:0:0:0:2/48 dev "\$INTERFACE"
EOF

# TODO autodiscover somhow the netmask
cat <<- EOF > /etc/tinc/$NET_NAME/tinc-down
	#!/bin/sh
	ip -6 addr del $IPV6_PREFIX:0:0:0:0:2/48 dev "\$INTERFACE"
	ip -6 link set "\$INTERFACE" down
EOF
