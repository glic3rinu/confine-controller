#!/bin/bash

# NOTE: This script needs superuser privilefes, you can enable it using the 
#       suid bit or add it on the sudoers file
#
# USAGE: update_tincd.sh host_path subnet pubkey

if [ ! $# -eq 3 ]; then
    echo 'USAGE: update_tincd.sh host_name subnet pubkey' 1>&2
    exit 1
fi

HOSTPATH=$1
SUBNET=$2
PUBKEY=$3

TMPFILE=$(mktemp)

cat <<- EOF > $TMPFILE
	Subnet = $SUBNET
	
	$PUBKEY
EOF

if [[ ! $? -eq 0 ]]; then
    exit 4
fi

if [[ ! -e ${HOSTPATH} || $(diff ${HOSTPATH} ${TMPFILE}) ]]; then
    sudo /bin/mv ${TMPFILE} ${HOSTPATH} || exit 3
    sudo /etc/init.d/tinc restart || exit 2
else
    rm ${HOSTPATH}.tmp || exit 3
fi

exit 0
