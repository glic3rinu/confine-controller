#!/bin/bash

set -u

prepare_image() {
    # USAGE: prepare_image file size
    
    local FILE=$1
    local SIZE=$2
        
    dd if=/dev/zero of=$FILE bs=$SIZE count=1
    mkfs.ext4 -F $FILE
}


custom_mount() {
    # USAGE: custom_mount -ldps [ src ] mount_point
    
    local SRC_POS=$(($#-1))
    local SRC=${!SRC_POS}
    local POINT="${!#}"
    
    while getopts ":ldps" opt; do
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
    # USAGE: custom_umount -spdl mount_point
    
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
    
    #TODO: use MAKEDEV?
    
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
		z6:6:respawn:/sbin/sulogin
		1:2345:respawn:/sbin/getty 38400 console
		c1:12345:respawn:/sbin/getty 38400 tty1 linux
		c2:12345:respawn:/sbin/getty 38400 tty2 linux
		c3:12345:respawn:/sbin/getty 38400 tty3 linux
		c4:12345:respawn:/sbin/getty 38400 tty4 linux
		EOF
    
    ln -s /proc/mounts $MOUNT_POINT/etc/mtab
   
    # Turn off doing sync() on every write for syslog's log files
    sed -ie 's@\([[:space:]]\)\(/var/log/\)@\1-\2@' $MOUNT_POINT/etc/*syslog.conf
    
    # Disable uneeded software
    #TODO --exclude this from debootstrap
    chroot $MOUNT_POINT dpkg --purge modutils ppp pppoeconf pppoe pppconfig module-init-tools
    chroot $MOUNT_POINT apt-get --purge clean
    chroot $MOUNT_POINT update-rc.d-insserv -f klogd remove
    chroot $MOUNT_POINT update-rc.d-insserv -f quotarpc remove
    chroot $MOUNT_POINT update-rc.d-insserv -f exim4 remove
    chroot $MOUNT_POINT update-rc.d-insserv -f inetd remove
}


basic_strap_configuration() {
    local PASSWORD=$1
    local KEYBOARD_LAYOUT=$2
    
    sed -i "s/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/" /etc/locale.gen
    locale-gen
    echo "root:$PASSWORD"|chpasswd
    echo confine-server > /etc/hostname
    
    #TODO: only useful for bootable?
    case $KEYBOARD_LAYOUT in
        'spanish') 
            cat <<- EOF > /etc/default/keyboard
				XKBMODEL="pc105"
				XKBLAYOUT="es"
				XKBVARIANT=""
				XKBOPTIONS=""
				EOF
            ;;
        *) ;; 
    esac
    
    # at least provide loopback interface
    echo -e "auto lo\niface lo inet loopback\n" > /etc/network/interfaces
}
export -f basic_strap_configuration


install_kernel_and_grub() {
    local DEVICE=$1
    
    apt-get update
    apt-get install -y linux-image-amd64 
    apt-get install -y dmsetup gettext-base grub-common libdevmapper1.02.1 \
                       libfreetype6 os-prober ucf
    # Download grub and manually install it in order to avoid interactive questions.
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


try_create_system_user() {
    # USAGE: try_create_system_user user password
    
    local USER=$1
    local PASSWORD=$2
    
    if ( ! $(id $USER &> /dev/null) ); then 
        useradd $USER -p '' -s "/bin/bash"
        echo "$USER:$PASSWORD"| chpasswd
        mkdir /home/$USER
        chown $USER.$USER /home/$USER
    fi
}
export -f try_create_system_user


install_portal() {
    # USAGE: install_portal dir username userpassword create_db db_name db_user \
    #                       db_password db_host db_port
    
    local USER=$2
    local PASSWORD=$3
    local install_db=$4
    try_create_system_user $USER $PASSWORD
    # user must exists befor evaluate ~user
    local DIR=$(eval echo $1)
    
    local DB_NAME=$5
    local DB_USER=$6
    local DB_PASSWORD=$7
    local DB_HOST=$8
    local DB_PORT=$9
    
    # Install dependencies
    apt-get update
    apt-get install -y libapache2-mod-wsgi rabbitmq-server git mercurial fuseext2 \
                       screen python-pip python-psycopg2 openssh-server tinc
    
    # Some versions of rabbitmq-server will not start automatically by default unless ...
    sed -i "s/# Default-Start:.*/# Default-Start:     2 3 4 5/" /etc/init.d/rabbitmq-server
    sed -i "s/# Default-Stop:.*/# Default-Stop:      0 1 6/" /etc/init.d/rabbitmq-server
    update-rc.d rabbitmq-server defaults
    
    if ( $install_db ); then 
        apt-get install -y postgresql
        # make sure that postgres will start at port $DB_PORT
        sed -i "s/port = .*/port = $DB_PORT/" /etc/postgresql/*/main/postgresql.conf
    fi
    
    # Install Django
    python -c "import django" 2> /dev/null || { 
        mkdir -p /usr/local/share /usr/lib/${PYVERSION##*' '}/dist-packages /usr/local/bin
        git clone git://github.com/django/django.git /usr/local/share/django-trunk
        local PYVERSION=$(ls -al /usr/bin/python)
        ln -s /usr/local/share/django-trunk/django /usr/local/lib/${PYVERSION##*' '}/dist-packages/
        ln -s /usr/local/share/django-trunk/django/bin/django-admin.py /usr/local/bin/
    }
    hg clone https://bitbucket.org/izi/django-admin-tools /tmp/admin_tools
    python /tmp/admin_tools/setup.py install
    rm -fr /tmp/admin_tools
    pip install django-fluent-dashboard south djangorestframework markdown \
                -e git+https://github.com/alex/django-filter.git#egg=django-filter \
                django-singletons django-extensions django_transaction_signals \
                django-private-files
    
    # Installing and configuring MQ
    pip install django-celery
    wget 'https://raw.github.com/ask/celery/master/contrib/generic-init.d/celeryd' \
         -O /etc/init.d/celeryd
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

		# Name of the projects settings module. (no needed for django +1.4
		#export DJANGO_SETTINGS_MODULE="settings"

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
    chmod +x /etc/init.d/celeryd
    update-rc.d celeryd defaults
    wget "https://raw.github.com/ask/celery/master/contrib/generic-init.d/celeryevcam"\
         -O /etc/init.d/celeryevcam
    chmod +x /etc/init.d/celeryevcam
    update-rc.d celeryevcam defaults
    
    # Install ConFw
    git clone http://git.confine-project.eu/confine/confw.git /usr/local/lib/python2.6/dist-packages/
    [ $(grep "^fuse:" /etc/group &> /dev/null) ] || addgroup fuse
    adduser $USER fuse
    
    # Install the portal
    su $USER -c "git clone http://git.confine-project.eu/confine/controller.git $DIR"
    su $USER -c "echo 'from controller.settings_example import *' > $DIR/controller/settings.py"
    sed -i "s/'NAME': '.*',/'NAME': '$DB_NAME',/" $DIR/controller/settings.py
    sed -i "s/'USER': '.*',/'USER': '$DB_USER',/" $DIR/controller/settings.py
    sed -i "s/'PASSWORD': '.*',/'PASSWORD': '$DB_PASSWORD',/" $DIR/controller/settings.py
    sed -i "s/'HOST': '.*',/'HOST': '$DB_HOST',/" $DIR/controller/settings.py
    sed -i "s/'PORT': '.*',/'PORT': '$DB_PORT',/" $DIR/controller/settings.py
    
    cat <<- EOF > /etc/apache2/httpd.conf
		WSGIScriptAlias / $DIR/controller/wsgi.py
		WSGIPythonPath $DIR
		<Directory $DIR/controller/>
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


echo_generate_ssh_keys () {
    local USER=$1
    
    cat <<- EOF
		# Generate host keys
		ssh-keygen -f /etc/ssh/ssh_host_rsa_key -t rsa -N ""
		ssh-keygen -f /etc/ssh/ssh_host_dsa_key -t dsa -N ""
		
		# Generate ssh keys for $USER and root
		su $USER -c "mkdir -p ~$USER/.ssh/"
		chmod 700 ~$USER/.ssh/
		su $USER -c "ssh-keygen -P '' -f ~$USER/.ssh/id_rsa"
		mkdir -p /root/.ssh
		chmod 700 /root/.ssh
		ssh-keygen -P '' -f /root/.ssh/id_rsa
		EOF

}
export -f echo_generate_ssh_keys

generate_ssh_keys_postponed () {
    local USER=$1
    
    rm -f /etc/ssh/ssh_host_*
    cat <<- EOF > /etc/init.d/generate_ssh_keys
		#!/bin/sh
		### BEGIN INIT INFO
		# Provides:          generate_ssh_keys
		# Required-Start:    $remote_fs $syslog
		# Required-Stop:     $remote_fs $syslog
		# Default-Start:     2 3 4 5
		# Default-Stop:
		# Short-Description: Generates fresh ssh keys on first boot
		# Description:       Generates fresh ssh keys on first boot
		### END INIT INFO
		
		$(echo_generate_ssh_keys $USER)
		
		insserv -r /etc/init.d/generate_ssh_keys
		rm -f \$0
		EOF
    
    chmod a+x /etc/init.d/generate_ssh_keys
    insserv /etc/init.d/generate_ssh_keys
}
export -f generate_ssh_keys_postponed


echo_portal_configuration_script () {
    # USAGE: echo_portal_configuration_steps install_path user create_db \
    #                                        db_name db_user db_password
    
    local DIR=$(eval echo $1)
    local USER=$2
    local create_db=$3
    local DB_NAME=$4
    local DB_USER=$5
    local DB_PASSWORD=$6
    
    $create_db && cat <<- EOF 
		su postgres -c "psql -c \"CREATE USER $DB_USER PASSWORD '$DB_PASSWORD';\""
		su postgres -c "psql -c \"CREATE DATABASE $DB_NAME OWNER $DB_USER;\""
		EOF
    
    cat <<- EOF 
		su $USER -c "python $DIR/manage.py syncdb --noinput"
		su $USER -c "python $DIR/manage.py migrate --noinput"
		su $USER -c "echo \"from django.contrib.auth.models import User; \\
		             User.objects.create_superuser('confine', 'confine@confine-project.eu', 'confine')\" | $DIR/manage.py shell"
		EOF
}
export -f echo_portal_configuration_script

configure_portal_postponed () {
    # USAGE: echo_portal_configuration_steps dir user db_name db_user db_password
    
    # Some configuration commands should run when the database is online, 
    # this function postpone these actions until first boot.
    
    local DIR=$(eval echo $1)
    local USER=$2
    local DB_NAME=$3
    local DB_USER=$4
    local DB_PASSWORD=$5
    
    cat <<- EOF > /etc/init.d/setup_portal_db
		#!/bin/sh
		### BEGIN INIT INFO
		# Provides:          setup_portal_db
		# Required-Start:    \$remote_fs \$syslog \$all
		# Required-Stop:     \$remote_fs \$syslog
		# Default-Start:     2 3 4 5
		# Default-Stop:
		# Short-Description: Creates and fills database on first boot
		# Description:       Creates and fills database on first boot
		### END INIT INFO
		$(echo_portal_configuration_script $DIR $USER true $DB_NAME $DB_USER $DB_PASSWORD)
		insserv -r /etc/init.d/setup_portal_db
		rm -f \$0
		EOF
    
    chmod a+x /etc/init.d/setup_portal_db
    insserv /etc/init.d/setup_portal_db
}
export -f configure_portal_postponed


print_help () {
    local bold=$(tput bold)
    local normal=$(tput sgr0)
    
    cat <<- EOF 
		
		${bold}NAME${normal}
		    server_deployment.sh - Confine server installation script
		    
		${bold}SYNOPSIS${normal}
		    required parameters: -t TYPE ( -d DIRECTORY | -i IMAGE )
		    
		    OS options: [ -u USER ] [ -p PASSWORD ] [ -I INSTALL_PATH ] [ -a ARCH ] [ -s SUITE ] [ -S IMAGE_SIZE ] [ -k KEYBOARD_LAYOUT ]
		    
		    database options: [ -N DB_NAME ] [ -U DB_USER ] [ -W DB_PASSWORD ] [ -H DB_HOST ] [ -P DB_PORT ]
		    
		${bold}OPTIONS${normal}
		    -t, --type
		            installation supported types: 
		                'container' LXC/OpenVZ compatible
		                'bootable' KVM/XEN compatible
		                'local' compatible with any debian-like system
		                'chroot' (notice that process namespace and network stack will be shared with the local system)
		    -i, --image
		            /path/file_name, i.e.: /tmp/confine_portal.img
		            compatible with: container, bootable and chroot
		    
		    -S, --image_size
		            default 2G
		    
		    -d, --directory
		            where the container or chroot will be deployed
		    
		    -u, --user
		            system user that will run the portal, it will be created if it does not exist (default confine)
		    
		    -p, --password
		            password is needed if USER does not exist (default confine)
		    
		    -I, --install_path
		            where the portal code will live (default ~USER/controller)
		    
		    -a, --arch
		            when debootsraping i.e amd64, i386 ... (amd64 by default)
		    
		    -s, --suite
		            debian suite (default stable)
		    
		    -N, --db_name
		            db will be created if not exists (default confine)
		    
		    -U, --db_user
		            user will be created if not exists (default confine)
		    
		    -W, --db_password
		            default confine
		    
		    -H, --db_host 
		            if this option is provided, no DB will be created nor installed (default localhost)
		    
		    -P, --db_port
		            default 5432
		            
		    -k, --keyboard_layout
		            supported layouts: spanish and english (default)
		    
		${bold}EXAMPLES${normal}
		    server_deployment.sh --type bootable --image /tmp/server.img --suite squeeze
		    
		    server_deployment.sh --type local -u confine -p 2hd4nd
		    
		${bold}TODO${normal}
		    #TODO: offer script to raise chroot when chroot deployment type is chosen 
		    #TODO: virtualenv support for local deployment
		    #TODO: always use update.rc instead of insserv for more compatibility? i.e. ubuntu
		    #TODO: Tinc
		    #TODO: Option: Use provided ssh keys instead of generating them
		EOF
}


##############
#### MAIN ####
##############

opts=$(getopt -o Cht:i:S:d:u:p:a:s:U:P:H:I:W:N:k: -l create,user:,password:,help,type:,image:,image_size:,directory:,suite:,arch:,db_name:,db_user:,db_password:,db_host:,db_port:,install_path:,keyboard_layout: -- "$@") || exit 1
set -- $opts

# Default values 
type=false
image=false
IMAGE_SIZE="2G"
image_size=false
directory=false
USER="confine"
PASSWORD="confine"
INSTALL_PATH=false
ARCH="amd64"
SUITE="stable"
create_db=true
DB_NAME="confine"
DB_USER="confine"
DB_PASSWORD="confine"
DB_HOST="localhost"
DB_PORT="5432"
KEYBOARD_LAYOUT=''

while [ $# -gt 0 ]; do
    case $1 in
        -t|--type) TYPE="${2:1:-1}"; type=true; shift ;;
        -i|--image) IMAGE="${2:1:-1}"; image=true; shift ;;
        -S|--image_size) IMAGE_SIZE="${2:1:-1}"; image_size=true; shift ;;
        -d|--directory) DIRECTORY="${2:1:-1}"; directory=true; shift ;;
        -u|--user) USER="${2:1:-1}"; shift ;;
        -I|--install_path) INSTALL_PATH="${2:1:-1}"; shift ;;
        -p|--password) PASSWORD="${2:1:-1}"; shift ;;
        -a|--arch) ARCH="${2:1:-1}"; shift ;;
        -s|--suite) SUITE="${2:1:-1}"; shift ;;
        -U|--db_name) DB_NAME="${2:1:-1}"; shift ;;
        -U|--db_user) DB_USER="${2:1:-1}"; shift ;;
        -W|--db_password) DB_PASSWORD="${2:1:-1}"; shift ;;
        -S|--db_host) DB_HOST="${2:1:-1}"; create_db=false; shift ;;
        -P|--dp_port) DB_PORT="${2:1:-1}"; shift ;;
        -k|--keyboard_layout) KEYBOARD_LAYOUT="${2:1:-1}"; shift ;;
        -h|--help) print_help; exit 0 ;;
        (--) shift; break;;
        (-*) echo "$0: Err. - unrecognized option $1" 1>&2; exit 1;;
        (*) break;;
    esac
    shift
done

[ $(whoami) != 'root' ] && { echo -e "\nErr. You didn't expect to run this without root permission, did you?\n" >&2; exit 1; }

# Input validation
$type || { echo -e "\nErr. --type is required\n" >&2; exit 1; } 
$image_size && ! $image && { echo -e "\nErr. --image_size without --image?\n" >&2; exit 1; }
case $TYPE in 
    'container')
        ( ! $image && ! $directory ) && { echo -e "\nErr. Provide --directory or --image\n" >&2; exit 1; }
        ( $image && $directory ) &&  { echo -e "\nErr. Which one --directory or --image ?\n" >&2; exit 1; }
        ;;
    'bootable')
        ( ! $image || $directory ) && { echo -e "\nErr. Bootable only supported with --image\n" >&2; exit 1; }
        ;;
    'chroot')
        ( $image || ! $directory ) && { echo -e "\nErr. Chroot only supported with --directory\n" >&2; exit 1; }
        ;;
    'local')
        ( $image || $directory ) && { echo -e "\nErr. Local doesn't accept --directory neither --image\n" >&2; exit 1; }
        ;;
    *) echo "Unknown type $TYPE" >&2; exit 1 ;;
esac

[ $INSTALL_PATH == false ] && INSTALL_PATH="~$USER/controller"

if [[ $TYPE != 'local' ]]; then 

    if ( $image ); then 
        DIRECTORY=$(mktemp -d)
        chmod 0644 $DIRECTORY
        prepare_image $IMAGE $IMAGE_SIZE
        custom_mount -l $IMAGE $DIRECTORY
        trap "custom_umount -l $DIRECTORY; $image && rm -fr $DIRECTORY; exit 1;" INT TERM EXIT 
    fi
    
    [ $TYPE == 'bootable' ] && EXCLUDE='' || EXCLUDE='--exclude=udev'
    debootstrap --include=locales --arch=$ARCH $EXCLUDE $SUITE $DIRECTORY || exit 1
    
    custom_mount -s $DIRECTORY
    trap "custom_umount -sl $DIRECTORY; $image && rm -fr $DIRECTORY; exit 1;" INT TERM EXIT 
    chroot $DIRECTORY /bin/bash -c "basic_strap_configuration confine $KEYBOARD_LAYOUT"
    
    if [ $TYPE == 'bootable' ]; then 
        custom_mount -d $DIRECTORY
        trap "custom_umount -sdl $DIRECTORY; $image && rm -fr $DIRECTORY; exit 1;" INT TERM EXIT
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
    chroot $DIRECTORY /bin/bash -c "install_portal $INSTALL_PATH $USER $PASSWORD $create_db $DB_NAME $DB_USER $DB_PASSWORD $DB_HOST $DB_PORT"
    rm -fr $DIRECTORY/usr/sbin/policy-rc.d
    
    chroot $DIRECTORY /bin/bash -c "configure_portal_postponed $INSTALL_PATH $USER $DB_NAME $DB_USER $DB_PASSWORD"
    chroot $DIRECTORY /bin/bash -c "generate_ssh_keys_postponed $USER"
    
    # Clean up
    custom_umount -s $DIRECTORY
    [ $TYPE == 'bootable' ] && custom_umount -d $DIRECTORY
    $image && custom_umount -l $DIRECTORY
    trap - INT TERM EXIT
    $image && [ -e $DIRECTORY ] && { mountpoint -q $DIRECTORY || rm -fr $DIRECTORY; }
else
    install_portal $INSTALL_PATH $USER $PASSWORD $create_db $DB_NAME $DB_USER $DB_PASSWORD $DB_HOST $DB_PORT
#    try_create_system_user $USER $PASSWORD
    /bin/bash -c "$(echo_portal_configuration_script $INSTALL_PATH $USER $create_db $DB_NAME $DB_USER $DB_PASSWORD)"
fi


echo -e "\n ... seems that everything went better than expected :)"

