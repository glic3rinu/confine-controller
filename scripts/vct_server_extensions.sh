#!/bin/bash

set -u

. ./confine.functions

SERVER_IMAGE_URL='http://images.confine-project.eu/server/debian-amd64-container-image-v0-latest.ext4.tgz'

vct_server_customize () {
 
    # Prepare Image
    #TODO: image directory?
    wget -O /tmp/server.image.tgz $SERVER_IMAGE_URL 
    if [ $? -eq 0 ]; then 
        local IMAGE_NAME=$(tar xvfz /tmp/server.image.tgz --directory /tmp/)
    else
        server_deployment.sh --type bootable --image /tmp/server.img
        local IMAGE_NAME="server.img"
    fi
    local MOUNT_POINT=$(mktmp -p /tmp)
    trap "rm -fr $MOUNT_POINT" INT TERM EXIT
    mount /tmp/$IMAGE_NAME $MOUNT_POINT || { echo 'Error mounting image' >&2; exit 1; }
    trap "umount $MOUNT_POINT && rm -fr $MOUNT_POINT || { echo 'Error umounting' >&2; exit 1; }" INT TERM EXIT
    
    # SSH keys
    chroot $MOUNT_POINT insserv -r /etc/init.d/generate_ssh_keys
    rm $MOUNT_POINT/etc/init.d/generate_ssh_keys
    chroot $MOUNT_POINT su confine -c "mkdir -p ~/.ssh/"
    chmod 700 $MOUNT_POINT/home/confine/.ssh/
    mkdir -p $MOUNT_POINT/root/.ssh
    chmod 700 $MOUNT_POINT/root/.ssh
    # chroot $MOUNT_POINT ssh-keygen -P '' -f /root/.ssh/id_rsa
    cp $VCT_KEYS_DIR/server_ssh.pub $MOUNT_POINT/home/confine/.ssh/
    cp $VCT_KEYS_DIR/server_ssh $MOUNT_POINT/home/confine/.ssh/

    # Configure Tinc
    rm -rf $MOUNT_POINT/etc/tinc/confine
    mkdir -p $MOUNT_POINT/etc/tinc/confine
    cat <<- EOF > $MOUNT_POINT/etc/tinc/confine/tinc.conf
		BindToAddress = $VCT_SERVER_TINC_IP
		Port = $VCT_SERVER_TINC_PORT
		Name = server
		StrictSubnets = yes
		EOF
    cat <<- EOF > $MOUNT_POINT/etc/tinc/confine/tinc-down 
		#!/bin/sh
		ip -6 addr del $VCT_TESTBED_MGMT_IPV6_PREFIX48:0:0:0:0:2/48 dev "\$INTERFACE"
		ip -6 link set "\$INTERFACE" down
		EOF
    cat <<- EOF > $MOUNT_POINT/etc/tinc/confine/tinc-up
		#!/bin/sh
		ip -6 link set "\$INTERFACE" up mtu 1400
		ip -6 addr add $VCT_TESTBED_MGMT_IPV6_PREFIX48:0:0:0:0:2/48 dev "\$INTERFACE"
		EOF
    mkdir -p $MOUNT_POINT/etc/tinc/confine/hosts
    cat <<- EOF > $MOUNT_POINT/etc/tinc/confine/hosts/server
		Address = $VCT_SERVER_TINC_IP
		Port = $VCT_SERVER_TINC_PORT
		Subnet = $VCT_TESTBED_MGMT_IPV6_PREFIX48:0:0:0:0:2/128
		EOF
    chroot $MOUNT_POINT tincd -n confine -K
    chmod a+rx $MOUNT_POINT/etc/tinc/confine/tinc-{up,down}
    echo confine >> $MOUNT_POINT/etc/tinc/nets.boot

    # Cleaning up
    umount $MOUNT_POINT && rm -fr $MOUNT_POINT || { echo 'Error umounting' >&2; exit 1; } 
    trap - INT TERM EXIT
}



# mkdir /dev/net
# mknod /dev/net/tun c 10 200
# chmod 0666 /dev/net/tun

# ip tuntap add mode tun tun0

