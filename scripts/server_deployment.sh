#!/bin/bash

set -u

prepare_image() {

    # USAGE: prepare_image file
    
    local FILE=$1
    
    dd if=/dev/zero of=$FILE bs=1G count=5
    mkfs.ext4 -F $FILE
}


custom_mount() {

    # USAGE: custom_mount -opts src mount_point
    
    local SRC_POS=$(($#-1))
    local SRC=${!SRC_POS}
    local POINT="${!#}"

    while getopts ":ldps" opt; do
        if [[ $opt != 'l' ]]; then
            mountpoint -q $POINT || { echo 'ERROR: mount loop first' >&2; exit 2; }
        fi
        case $opt in
            l) mountpoint -q $POINT || mount $SRC $POINT ;;
            d) mountpoint -q $POINT/dev || mount --bind /dev $POINT/dev ;;
            p) mountpoint -q $POINT/proc || mount -t proc none $POINT/proc ;;
            s) mountpoint -q $POINT/sys || mount -t sysfs none $POINT/sys ;;
        esac
        shift $(($OPTIND-1))
    done
    
    unset OPTIND
    unset opt
}


custom_umount() {

    # USAGE: custom_umount -opts mount_point
    
    local POINT="${!#}"

    # wait half a second, otherwise it will fail, sometimes
    sleep 0.5
    
    while getopts ":spdl" opt; do
        case $opt in
            s) umount $POINT/sys ;;
            p) umount $POINT/proc ;;
            d) umount $POINT/dev ;;
            l) umount $POINT ;;
        esac
        shift $(($OPTIND-1))
    done
    
    unset OPTIND
    unset opt
}


container_customization () {
    
    # USAGE: container_customization mount_point
    
    local MOUNT_POINT=$1
    local DEV=$MOUNT_POINT/dev

    #TODO: use makedev?

    rm -rf ${DEV}
    mkdir ${DEV}
    mknod -m 666 ${DEV}/null c 1 3
    mknod -m 666 ${DEV}/zero c 1 5
    mknod -m 666 ${DEV}/random c 1 8
    mknod -m 666 ${DEV}/urandom c 1 9
    mkdir -m 755 ${DEV}/pts
    mkdir -m 1777 ${DEV}/shm
    mknod -m 666 ${DEV}/tty c 5 0
    mknod -m 666 ${DEV}/tty0 c 4 0
    mknod -m 666 ${DEV}/tty1 c 4 1
    mknod -m 666 ${DEV}/tty2 c 4 2
    mknod -m 666 ${DEV}/tty3 c 4 3
    mknod -m 666 ${DEV}/tty4 c 4 4
    mknod -m 600 ${DEV}/console c 5 1
    mknod -m 666 ${DEV}/full c 1 7
    mknod -m 600 ${DEV}/initctl p
    mknod -m 666 ${DEV}/ptmx c 5 2    
    
    cat <<- EOF > $MOUNT_POINT/etc/inittab
		id:2:initdefault:
		si::sysinit:/etc/init.d/rcS
		l0:0:wait:/etc/init.d/rc 0
		l1:1:wait:/etc/init.d/rc 1
		l2:2:wait:/etc/init.d/rc 2
		l3:3:wait:/etc/init.d/rc 3
		l4:4:wait:/etc/init.d/rc 4
		l5:5:wait:/etc/init.d/rc 5
		l6:6:wait:/etc/init.d/rc 6
		# Normally not reached, but fallthrough in case of emergency.
		z6:6:respawn:/sbin/sulogin
		
		c1:12345:respawn:/sbin/getty 38400 tty1 linux
		c2:12345:respawn:/sbin/getty 38400 tty2 linux
		c3:12345:respawn:/sbin/getty 38400 tty3 linux
		c4:12345:respawn:/sbin/getty 38400 tty4 linux
		EOF

    cat <<- EOF > $MOUNT_POINT/etc/mtab
		proc /proc proc rw,noexec,nosuid,nodev 0 0
		sysfs /sys sysfs rw,noexec,nosuid,nodev 0 0
		devpts /dev/pts devpts rw,noexec,nosuid,gid=5,mode=620 0 0
		rootfs / rootfs rw 0 0
		EOF
    
    # Turn off doing sync() on every write for syslog's log files
    sed -ie 's@\([[:space:]]\)\(/var/log/\)@\1-\2@' $MOUNT_POINT/etc/*syslog.conf
    
    # Disable uneeded software
    chroot $MOUNT_POINT dpkg --purge modutils ppp pppoeconf pppoe pppconfig module-init-tools
    chroot $MOUNT_POINT apt-get --purge clean
    chroot $MOUNT_POINT update-rc.d-insserv -f klogd remove
    chroot $MOUNT_POINT update-rc.d-insserv -f quotarpc remove
    chroot $MOUNT_POINT update-rc.d-insserv -f exim4 remove
    chroot $MOUNT_POINT update-rc.d-insserv -f inetd remove
}


basic_strap_configuration() {
    
    local PWD=$1
    
    sed -i "s/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/" /etc/locale.gen
    locale-gen
    echo "root:$PWD"|chpasswd
    echo confine-server > /etc/hostname

}
export -f basic_strap_configuration


install_kernel_and_grub() {

    DEVICE=$1
    
    apt-get update
    apt-get install -y linux-image-amd64 
    apt-get install -y dmsetup gettext-base grub-common libdevmapper1.02.1 libfreetype6 os-prober ucf
    apt-get -dy install grub-pc
    local GRUB_PKG=$(find /var/cache/apt/archives/ -type f -name grub-pc*.deb)
    dpkg -x $GRUB_PKG /

    mkdir -p /boot/grub
    echo "(hd0) $DEVICE" > /boot/grub/device.map
    grub-mkconfig -o /boot/grub/grub.cfg
    sed -i "s/timeout=5/timeout=0/" /boot/grub/grub.cfg

    grub-install --no-floppy --grub-mkdevicemap=/boot/grub/device.map $DEVICE --force
}
export -f install_kernel_and_grub


install_portal() {
    
    #USAGE: install_portal dir username userpassword

    local DIR=$1
    local USER=$2
    local PWD=$3

    # Install dependencies
    apt-get update
    apt-get install -y postgresql libapache2-mod-wsgi \
        rabbitmq-server git python-paramiko screen python-pip python-psycopg2

    # Install Django
    git clone git://github.com/django/django.git /usr/share/django-trunk
    local PYVERSION=$(ls -al /usr/bin/python)
    ln -s /usr/share/django-trunk/django /usr/lib/${PYVERSION##*' '}/dist-packages/
    ln -s /usr/share/django-trunk/django/bin/django-admin.py /usr/bin
    pip install django-admin-tools django-fluent-dashboard south

    # Installing MQ broker
    pip install django-celery
    wget "https://raw.github.com/ask/celery/master/contrib/generic-init.d/celeryd" -O /etc/init.d/celeyd
    cat <<- EOF > /etc/default/celeryd
		# Name of nodes to start, here we have a single node
		CELERYD_NODES="w1"
		# Where to chdir at start.
		CELERYD_CHDIR="$DIR"
		# How to call "manage.py celeryd_multi"
		CELERYD_MULTI="\$CELERYD_CHDIR/manage.py celeryd_multi"
		# Extra arguments to celeryd
		CELERYD_OPTS="--time-limit=300 --concurrency=8 -B"
		# Name of the celery config module.
		CELERY_CONFIG_MODULE="celeryconfig"
		# %n will be replaced with the nodename.
		CELERYD_LOG_FILE="/var/log/celery/%n.log"
		CELERYD_PID_FILE="/var/run/celery/%n.pid"
		# Workers should run as an unprivileged user.
		CELERYD_USER="$USER"
		CELERYD_GROUP="\$CELERYD_USER"
		# Name of the projects settings module.
		export DJANGO_SETTINGS_MODULE="settings"
		# Path to celeryd
		CELERYEV="\$CELERYD_CHDIR/manage.py"
		# Extra arguments to manage.py
		CELERYEV_OPTS="celeryev"
		# Camera class to use (required)
		CELERYEV_CAM="djcelery.snapshot.Camera"
		# Celerybeat
		#CELERY_OPTS="\$CELERY_OPTS -B -S djcelery.schedulers.DatabaseScheduler"
		# Persistent revokes
		CELERYD_STATE_DB="\$CELERYD_CHDIR/persistent_revokes"
		EOF
    chmod +x /etc/init.d/celeyd
    update-rc.d celeryd defaults
    wget "https://raw.github.com/ask/celery/master/contrib/generic-init.d/celeryevcam" -O /etc/init.d/celeryevcam
    chmod +x /etc/init.d/celeryevcam
    update-rc.d celeryevcam defaults
    chmod +x /etc/init.d/celeryevcam

    # Create user if it doesn't exist
    if ( ! $(id $USER &> /dev/null) ); then 
        useradd $USER -p '' -s "/bin/bash"
        echo "$USER:$PWD"| chpasswd
        mkdir /home/$USER
        chown $USER.$USER /home/$USER
    fi
    
    # Install the portal
    su $USER -c "git clone http://git.confine-project.eu/confine/controller.git $DIR"

    cat <<- EOF > /etc/apache2/httpd.conf
		WSGIScriptAlias / $DIR/confine/wsgi.py
		WSGIPythonPath $DIR
		<Directory $DIR/confine/>
		    <Files wsgi.py>
		        Order deny,allow
		        Allow from all
		    </Files>
		</Directory>
		Alias /media/ $DIR/media/
		Alias /static/ $DIR/static/
		EOF
}
export -f install_portal


configure_portal () {

    # WARN: this code should be performed within a running machine
    #TODO: maybe create an rcinit script that boots executes this the first time the machine is botting and auto-delete it when finished?

    local DIR=$1
    local USER=$2

    su postgres -c "psql -c \"CREATE USER confine PASSWORD 'confine';\""
    su postgres -c "psql -c \"CREATE DATABASE confine OWNER 'confine';\""
    su $USER -c "python $DIR/manage.py syncdb --noinput"
    su $USER -c "python $DIR/manage.py migrate --noinput"
}
    
### MAIN 

print_help () {

    local bold=$(tput bold)
    local normal=$(tput sgr0)

    cat <<- EOF 
		
		${bold}NAME${normal}
		    server_deployment.sh - Confine server installation script

		${bold}OPTIONS${normal}
		    -t, --type
		            installation supported types: 
		                'container' LXC/OpenVZ compatible
		                'bootable' KVM/XEN compatible
		                'local' compatible with any debian-like system
		                'chroot' (notice that proces namespace and network stack will be shared with the local system)
		    -i, --image
		            /path/file_name, i.e.: /tmp/confine_portal.img
		            compatible with: container, bootable and chroot

		    -d, --directory
		            where the container or chroot will be deployed
		            
		EOF
}

        
#TODO: user, password, image_size, architecture, debian_distro customizations
#TODO: script to raise chroot
#TODO: update_portal function "git pull origin"
#TODO: rm randompoint when finish
#TODO: virtualenv support ?
#TODO: smart image creation: if something is already done, skip

opts=$(getopt -o ht:i:d: -l help,type:,image:,directory: -- "$@") || exit 1
set -- $opts

type=false
image=false
directory=false

while [ $# -gt 0 ]; do  
    case $1 in
        -t|--type) TYPE="${2:1:-1}"; type=true; shift ;;
        -i|--image) IMAGE="${2:1:-1}"; image=true; shift ;;
        -d|--directory) DIRECTORY="${2:1:-1}"; directory=true shift ;;
        -h|--help) print_help; exit 0;;
        (--) shift; break;;
        (-*) echo "$0: error - unrecognized option $1" 1>&2; exit 1;;
        (*) break;;
    esac
    shift
done

# Input validation
$type || { echo "--type is required" >&2; exit 1; } 
case $TYPE in 
    'container') 
        ( ! $image && ! $directory ) && { echo -e "\n\tProvide --directory or --image\n" >&2; exit 1; }
        ( $image && $directory ) &&  { echo -e "\n\tWhich one --directory or --image ?\n" >&2; exit 1; }
        ;;
    'bootable')
        ( ! $image || $directory ) && { echo -e "\n\tBootable only supported with --image\n" >&2; exit 1; }
        ;;
    'chroot')
        ( $image || ! $directory ) && { echo -e "\n\tChroot only supported with --directory\n" >&2; exit 1; }
        ;;
    'local')
        ( $image || $directory ) && { echo -e "\n\tLocal doesn't accept --directory neither --image\n" >&2; exit 1; }
        ;;
    *) echo "Unknown type $TYPE" >&2; exit 1 ;;
esac


if [[ $TYPE != 'local' ]]; then 

    if ( $image ); then 
        DIRECTORY="/tmp/raNDOM_point"
        prepare_image $IMAGE
        [ -e $DIRECTORY ] || mkdir $DIRECTORY
        custom_mount -l $IMAGE $DIRECTORY
        trap "custom_umount -l $DIRECTORY; exit 2;" INT TERM EXIT 
    fi
    
    debootstrap --include=locales --exclude=udev stable $DIRECTORY

    custom_mount -ds $IMAGE $DIRECTORY
    trap "custom_umount -sdl $DIRECTORY; exit 2;" INT TERM EXIT 
    chroot $DIRECTORY /bin/bash -c "basic_strap_configuration root"

    if [ $TYPE == 'bootable' ]; then 
        DEVICE=$(losetup -j $IMAGE|cut -d':' -f1) || { echo "ERROR: $IMAGE not mapped" >&2; exit 2; }
        chroot $DIRECTORY /bin/bash -c "install_kernel_and_grub $DEVICE"
    elif [ $TYPE == 'container' ]; then
        container_customization $DIRECTORY
    fi
    
    # Prevent apt-get from starting daemons
    if [[ $TYPE != 'chroot' ]]; then 
        cat <<- EOF > $DIRECTORY/usr/sbin/policy-rc.d
			#!/bin/sh
			exit 101
			EOF
        chmod 755 $DIRECTORY/usr/sbin/policy-rc.d
    fi
    chroot $DIRECTORY /bin/bash -c "install_portal /home/confine/controller confine confine"
    rm -fr $DIRECTORY/usr/sbin/policy-rc.d

    custom_umount -sdl $DIRECTORY
    trap - INT TERM EXIT

else
    install_portal /home/confine/controller confine confine
    #TODO add local user confine
    configure_portal  /home/confine/controller confine
fi


echo -e "\n ... seems that everything went better than expected :)"

