#!/bin/bash

# Should be executed as root

# USAGE create_server.sh IPV6_PREFIX
#       create_server.sh 2001:db8:cafe


IPV6_PREFIX=$1


if [[ ! $(grep 'confine' /etc/tinc/nets.boot) ]]; then
    echo 'confine' >> /etc/tinc/nets.boot
fi

mkdir -p /etc/tinc/confine/hosts

cat <<- EOF > /etc/tinc/confine/tinc.conf
	BindToAddress = 0.0.0.0
	Port = 655
	Name = server
EOF

echo "Subnet = $IPV6_PREFIX:0:0:0:0:2/128" > /etc/tinc/confine/hosts/server

tincd -n confine -K


cat <<- EOF > /etc/tinc/confine/tinc-up
	#!/bin/sh
	ip -6 link set "\$INTERFACE" up mtu 1400
	ip -6 addr add $IPV6_PREFIX:0:0:0:0:2/48 dev "\$INTERFACE"
EOF

cat <<- EOF > /etc/tinc/confine/tinc-down
	#!/bin/sh
	ip -6 addr del $IPV6_PREFIX:0:0:0:0:2/48 dev "\$INTERFACE"
	ip -6 link set "\$INTERFACE" down
EOF
