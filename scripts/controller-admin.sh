#!/bin/bash

set -u

bold=$(tput bold)
normal=$(tput sgr0)


function help () {
    if [[ $# -gt 1 ]]; then
        CMD="print_${2}_help"
        $CMD
    else
        print_help
    fi
}


function print_help () {
    cat <<- EOF 
		
		${bold}NAME${normal}
		    ${bold}controller-admin.sh${normal} - Confine server administration script
		
		${bold}OPTIONS${normal}
		    ${bold}install_requirements${normal}
		        Installs all the controller requirements using apt-get and pip
		    
		    ${bold}clone${normal}
		        Creates a new Confine-Controller instance
		    
		    ${bold}setup_celeryd${normal}
		        Configures Celeryd to run with your controller instance
		    
		    ${bold}setup_postgres${normal}
		        PostgresSQL administration script
		    
		    ${bold}setup_apache2${normal}
		        Configures Apache2 to run with your controller instance
		    
		    ${bold}update_secrete_key${normal}
		        Update your instance secrete key
		    
		    ${bold}setup_firmware${normal}
		        Prepare your system for generating firmware in userspace
		    
		    ${bold}restart_services${normal}
		        Restars all related services, usefull for reload configuration and files
		    
		    ${bold}update_tincd${normal}
		        Updates your tincd instance according to information stored on the database
		    
		    ${bold}full_install${normal}
		        Performs a full install of the controller server.
		        It supports local, container, bootable and chroot deployment types
		        run ${bold}controller-admin.sh help full_install${normal} for more details.
		    
		    ${bold}help${normal}
		        Displays this help text or related help page as argument
		        for example:
		            ${bold}controller-admin.sh help clone${normal}
		
		EOF
}
# in


show () {
    echo " ${bold}\$ ${@}${normal}"
}
export -f show


run () {
    show ${@}
    ${@}
}
export -f run


check_root () {
    [ $(whoami) != 'root' ] && { echo -e "\nErr. This should be run as root\n" >&2; exit 1; }
}
export -f check_root


check_project_dir () {
    [[ -f manage.py ]] || { echo -e "\nErr. Not in project directory\n" >&2; exit 1; }
}
export -f check_project_dir


get_project_dir () {
    CMD="from django.conf import settings; import os;\
         os.path.dirname(os.path.normpath(os.sys.modules[settings.SETTINGS_MODULE].__file__))"
    PATH=$(echo $CMD|python manage.py shell 2> /dev/null|cut -d"'" -f2|head -n1)
    echo $PATH
}
export -f get_project_dir


get_controller_dir () {
    if ! $(echo "import controller"|python 2> /dev/null); then
        echo -e "\nErr. Controller not installed.\n" >&2
        exit 1
    fi
    PATH=$(echo "import controller; print controller.__path__[0]" | python)
    echo $PATH
}
export -f get_controller_dir


function install_requirements () {
    # TODO different requirements levels (basic all...)
    check_root
    CONTROLLER_PATH=$(get_controller_path)
    
    run apt-get update
    run apt-get install -y libapache2-mod-wsgi rabbitmq-server git mercurial fuseext2 \
                           screen python-pip python-psycopg2 openssh-server tinc \
                           python-m2crypto
    
    # Some versions of rabbitmq-server will not start automatically by default unless ...
    sed -i "s/# Default-Start:.*/# Default-Start:     2 3 4 5/" /etc/init.d/rabbitmq-server
    sed -i "s/# Default-Stop:.*/# Default-Stop:      0 1 6/" /etc/init.d/rabbitmq-server
    run update-rc.d rabbitmq-server defaults
    
    run pip install -r "${CONTROLLER_PATH}/requirements.txt"
}
export -f install_requirements


print_clone_help () {
    cat <<- EOF 
		
		${bold}NAME${normal}
		    ${bold}controller-admin.sh clone${normal} - Create a new Confine-Controller instance
		
		${bold}SYNOPSIS${normal}
		    Options: [ -s SKELETONE ]
		    
		${bold}OPTIONS${normal}
		    ${bold}-s, --skeletone${normal}
		            default confine
		    
		    ${bold}-h, --help${normal}
		            This help message
		    
		${bold}EXAMPLES${normal}
		    controller-admin.sh clone communitylab --skeletone communitylab
		    
		    controller-admin.sh clone communitylab
		
		EOF
}


function clone () {
    # Default values
    [ $# -lt 1 ] && { echo -e "Err. project name is missing\n"; exit 1; }
    [ $(whoami) == 'root' ] && { echo -e "\nYou don't want to run this as root\n" >&2; exit 1; }

    local PROJECT_NAME="$1"
    local SKELETONE="confine"
    
    opts=$(getopt -o s:h -l skeletone:,help -- "$@") || exit 1
    set -- $opts
    while [ $# -gt 0 ]; do
        case $1 in
            -s|--skeletone) local SKELETONE="${2:1:${#2}-2}"; shift ;;
            -h|--help) print_clone_help; exit 0 ;;
            (--) shift; break;;
            (-*) echo "$0: Err. - unrecognized option $1" 1>&2; exit 1;;
            (*) break;;
        esac
        shift
    done
    unset OPTIND
    unset opt
    
    CONTROLLER_PATH=$(get_controller_dir)
    run cp -r "${CONTROLLER_PATH}/projects/${SKELETONE}" .
}
export -f clone


print_setup_postgres_help () {
    cat <<- EOF 
		
		${bold}NAME${normal}
		    ${bold}controller-admin.sh setup_postgres${bold} - PostgresSQL administration script
		
		${bold}SYNOPSIS${normal}
		    Options: [ -u USER ] [ -p PASSWORD ] [ -n NAME ] [ -P PORT ]
		    
		${bold}OPTIONS${normal}
		    ${bold}-n, --name${bold}
		            db will be created if not exists (default confine)
		    
		    ${bold}-u, --user${bold}
		            user will be created if not exists (default confine)
		    
		    ${bold}-p, --password${bold}
		            default confine
		    
		    ${bold}-H, --host${bold}
		            if this option is provided, no DB will be created nor installed (default localhost)
		    
		    ${bold}-P, --port${bold}
		            default 5432
		    
		${bold}EXAMPLES${normal}
		    controller-admin.sh setup_postgres --user confine --password confine
		    
		    controller-admin.sh setup_postgres
		
		EOF
}


function setup_postgres () {
    # Default values
    local DB_NAME="controller"
    local DB_USER="confine"
    local DB_PASSWORD="confine"
    local DB_HOST="localhost"
    local DB_PORT="5432"
    
    opts=$(getopt -o u:p:n:P:H:h -l user:,password:,port:,host:,help -- "$@") || exit 1
    set -- $opts
    
    while [ $# -gt 0 ]; do
        case $1 in
            -u|--user) local DB_USER="${2:1:${#2}-2}"; shift ;;
            -p|--password) local DB_PASSWORD="${2:1:${#2}-2}"; shift ;;
            -n|--name) local DB_NAME="${2:1:${#2}-2}"; shift ;;
            -P|--port) local DB_PORT="${2:1:${#2}-2}"; shift ;;
            -H|--host) local DB_HOST="${2:1:${#2}-2}"; shift ;;
            -h|--help) print_setup_postgres_help; exit 0 ;;
            (--) shift; break;;
            (-*) echo "$0: Err. - unrecognized option $1" 1>&2; exit 1;;
            (*) break;;
        esac
        shift
    done
    unset OPTIND
    unset opt
    
    check_root
    check_project_dir
    
    show su postgres -c "psql -c \"CREATE USER $DB_USER PASSWORD '$DB_PASSWORD';\""
    show su postgres -c "psql -c \"CREATE DATABASE $DB_NAME OWNER $DB_USER;\""
    
    local SETTINGS_FILE="$(get_project_dir)/local_settings.py"
    if $(grep 'DATABASES' "$SETTINGS_FILE" &> /dev/null); then
        sed -i "s/'ENGINE': '.*',/'ENGINE': 'django.db.backends.postgresql_psycopg2',/" $SETTINGS_FILE
        sed -i "s/'NAME': '.*',/'NAME': '$DB_NAME',/" $SETTINGS_FILE
        sed -i "s/'USER': '.*',/'USER': '$DB_USER',/" $SETTINGS_FILE
        sed -i "s/'PASSWORD': '.*',/'PASSWORD': '$DB_PASSWORD',/" $SETTINGS_FILE
        sed -i "s/'HOST': '.*',/'HOST': '$DB_HOST',/" $SETTINGS_FILE
        sed -i "s/'PORT': '.*',/'PORT': '$DB_PORT',/" $SETTINGS_FILE
    else
        cat <<- EOF >> $SETTINGS_FILE
			DATABASES = {
			    'default': {
			        'ENGINE': 'django.db.backends.postgresql_psycopg2',
			        'NAME': '$DB_NAME',
			        'USER': '$DB_USER',
			        'PASSWORD': '$DB_PASSWORD',
			        'HOST': '$DB_HOST',
			        'PORT': '$DB_PORT',
			    }
			}
			
			EOF
    fi
}
export -f setup_postgres


function setup_celeryd () {
    check_root
    check_project_dir
    
    local DIR=$(pwd)
    local USER=$(ls -dl|awk {'print $3'})
    [ $USER == 'root' ] && { echo -e "\nYou don't want your project files to be owned by root, please change to a regular user\n" >&2; exit 1; }
    
    wget 'https://raw.github.com/ask/celery/master/contrib/generic-init.d/celeryd' \
        --no-check-certificate -O /etc/init.d/celeryd
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
         --no-check-certificate -O /etc/init.d/celeryevcam
    chmod +x /etc/init.d/celeryevcam
    update-rc.d celeryevcam defaults
}
export -f setup_celeryd


function setup_apache2 () {
    check_project_dir
    check_root
    
    local DIR=$(pwd)
    local USER=$(ls -dl|awk {'print $3'})
    
    cat <<- EOF >> /etc/apache2/httpd.conf
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
    
    # Give upload file permissions to apache
    adduser www-data $USER
    run chmod g+w $DIR/media/firmwares
    run chmod g+w $DIR/media/templates
    run chmod g+w $DIR/private/exp_data
}
export -f setup_apache2 


function setup_firmware () {
    check_root
    check_project_dir
    local USER=$(ls -dl|awk {'print $3'})
    [ $USER == 'root' ] && { echo -e "\nYou don't want your project files to be owned by root, please change to a regular user\n" >&2; exit 1; }
    
    # Configure firmware generation
    [ $(grep "^fuse:" /etc/group &> /dev/null) ] || addgroup fuse
    [ $(grep "^fuse:.*${USER}" /etc/group &> /dev/null) ] || adduser $USER fuse
}
export -f setup_firmware


function update_tincd () {
    check_project_dir
    DIR=$(pwd)
    echo "from mgmtnetworks.tinc.tasks import update_tincd; update_tincd()" | $DIR/manage.py shell
}
export -f update_tincd


print_restart_services_help () {
    cat <<- EOF 
		
		${bold}NAME${normal}
		    ${bold}controller-admin.sh restart_services${normal} - Restars all related services
		
		${bold}SYNOPSIS${normal}
		    service tinc restart
		    service apache2 restart
		    service celeryd restart
		    service celeryevcam restart
		
		EOF
}


function restart_services () {
    opts=$(getopt -o h -l help -- "$@") || exit 1
    set -- $opts
    
    while [ $# -gt 0 ]; do
        case $1 in
            -h|--help) print_restart_services_help; exit 0 ;;
            (--) shift; break;;
            (-*) echo "$0: Err. - unrecognized option $1" 1>&2; exit 1;;
            (*) break;;
        esac
        shift
    done
    unset OPTIND
    unset opt
    
    check_root
    
    run service tinc restart
    run service apache2 restart
    run service celeryd restart
    run service celeryevcam restart
}
export -f restart_services


function update_secrete_key () {
    check_project_dir
    local DIR=$(pwd)
    
    KEY=$(python $DIR/manage.py generate_secret_key)
    local SETTINGS_FILE="$(get_project_dir)/local_settings.py"
    if $(grep 'SECRET_KEY' "$SETTINGS_FILE" &> /dev/null); then
        sed -i "s/SECRET_KEY = '.*'/SECRET_KEY = '$KEY'/" $SETTINGS_FILE
    else
        echo "SECRET_KEY = '$KEY'" >> $DIR/controller/local_settings.py
    fi
}
export -f update_secrete_key


###############################
#### FULL INSTALL OPERATIONS ##
###############################


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


prepare_image() {
    # USAGE: prepare_image file size
    
    local FILE=$1
    local SIZE=$2
    echo "Preparing the image file ..."
    run dd if=/dev/zero of=$FILE bs=$SIZE count=1
    run mkfs.ext4 -F $FILE
}
export -f prepare_image


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
export -f custom_mount


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
export -f custom_umount


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
export -f container_customization


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
    run apt-get install -y linux-image-amd64 
    run apt-get install -y dmsetup gettext-base grub-common libdevmapper1.02.1 \
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


full_install_common () {
    check_root
    
    local PROJECT_NAME=$1
    local SKELETONE=$2
    local USER=$3
    local PASSWORD=$4
    
    controller-admin.sh install_requirements
    
    try_create_system_user $USER $PASSWORD
    su $USER -c "mkdir ~$USER/$PROJECT_NAME"
    su $USER -c "cd ~$USER/$PROJECT_NAME"
    
    su $USER -c "controller-admin.sh clone $PROJECT_NAME --skeletone $SKELETONE"
    run setup_celeryd
    run setup_apache2
    run update_secrete_key
    run setup_firmware
}
export -f full_install_common


full_install_running_services () {
    check_root
    
    local DIR=$(eval echo $1)
    local USER=$2
    local DB_NAME=$3
    local DB_USER=$4
    local DB_PASSWORD=$5
    
    cd $DIR
    sudo controller-admin.sh setup_postgresql --name $DB_NAME --user $DB_USER --password $DB_PASSWORD
    su $USER -c "python manage.py syncdb --noinput"
    su $USER -c "python manage.py migrate --noinput"
    su $USER -c "echo \"from django.contrib.auth import get_user_model; \\
                 User = get_user_model(); \\
                 User.objects.create_superuser('confine', 'confine@confine-project.eu', 'confine')\" | $DIR/manage.py shell"
    
    su $USER -c "python $DIR/manage.py loaddata firmware_config"
    su $USER -c "python $DIR/manage.py collectstatic --noinput"
    
    python $DIR/manage.py create_tinc_server --noinput --safe
    su $USER -c "echo \"from mgmtnetworks.tinc.tasks import update_tincd; \\
                 update_tincd()\" | $DIR/manage.py shell"
    controller-admin.sh restart_services
}
export -f full_install_running_services


function full_install_postponed () {
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
		
		controller-admin.sh full_install_running_services "$DIR" "$USER" "$DB_NAME" "$DB_USER" "$DB_PASSWORD"
		insserv -r /etc/init.d/setup_portal_db
		rm -f \$0
		EOF
    
    chmod a+x /etc/init.d/setup_portal_db
    insserv /etc/init.d/setup_portal_db
}
export -f full_install_postponed


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


print_full_install_help () {
    cat <<- EOF 
		
		${bold}NAME${normal}
		    ${bold}controller-admin.sh full_install${normal} - Confine server deployment subsystem
		    
		${bold}SYNOPSIS${normal}
		    ${bold}required parameters: -t TYPE ( -d DIRECTORY | -i IMAGE )${normal}
		    
		    OS options: [ -u USER ] [ -p PASSWORD ] [ -I INSTALL_PATH ] [ -a ARCH ] [ -s SUITE ] [ -S IMAGE_SIZE ] [ -k KEYBOARD_LAYOUT ]
		    
		    database options: [ -N DB_NAME ] [ -U DB_USER ] [ -W DB_PASSWORD ] [ -H DB_HOST ] [ -P DB_PORT ]
		    
		    controller options: [ -j PROJECT_NAME ] [ -l SKELETONE ] [ -t TINC_PORT ] [ -m MGMT_PREFIX ]
		    
		${bold}OPTIONS${normal}
		    ${bold}-t, --type${normal}
		            installation supported types: 
		                'container'${normal} LXC/OpenVZ compatible
		                'bootable'${normal} KVM/XEN compatible
		                'local'${normal} compatible with any debian-like system
		                'chroot'${normal} (notice that process namespace and network stack will be shared with the local system)
		            
		    ${bold}-i, --image${normal}
		            /path/file_name, i.e.: /tmp/confine_portal.img
		            compatible with: container, bootable and chroot
		    
		    ${bold}-S, --image_size${normal}
		            default 2G
		    
		    ${bold}-d, --directory${normal}
		            where the container or chroot will be deployed
		    
		    ${bold}-u, --user${normal}
		            system user that will run the portal, it will be created if it does not exist (default confine)
		    
		    ${bold}-p, --password${normal}
		            password is needed if USER does not exist (default confine)
		    
		    ${bold}-I, --install_path${normal}
		            where the portal code will live (default ~USER/controller)
		    
		    ${bold}-a, --arch${normal}
		            when debootsraping i.e amd64, i386 ... (amd64 by default)
		    
		    ${bold}-s, --suite${normal}
		            debian suite (default stable)
		    
		    ${bold}-N, --db_name${normal}
		            db will be created if not exists (default confine)
		    
		    ${bold}-U, --db_user${normal}
		            user will be created if not exists (default confine)
		    
		    ${bold}-W, --db_password${normal}
		            default confine
		    
		    ${bold}-H, --db_host${normal}
		            if this option is provided, no DB will be created nor installed (default localhost)
		    
		    ${bold}-P, --db_port${normal}
		            default 5432
		            
		    ${bold}-k, --keyboard_layout${normal}
		            supported layouts: spanish and english (default)
		            
		    ${bold}-j, --project_name${normal}
		            project name, default confine.
		            
		    ${bold}-l, --skeletone${normal}
		            project skeletone, default confine.
		            
		    ${bold}-t, --tinc_port${normal}
		            tinc port
		            
		    ${bold}-m, --mgmt_prefix${normal}
		            management network prefix
		    
		${bold}EXAMPLES${normal}
		    controller-admin.sh full_install --type bootable --image /tmp/server.img --suite squeeze
		    
		    controller-admin.sh full_install --type local -u confine -p 2hd4nd
		    
		EOF
}
export -f print_full_install_help


function full_install () {
    opts=$(getopt -o Cht:i:S:d:u:p:a:s:U:P:H:I:W:N:k:j:t:m:l: -l create,user:,password:,help,type:,image:,image_size:,directory:,suite:,arch:,db_name:,db_user:,db_password:,db_host:,db_port:,install_path:,keyboard_layout:,project_name:,tinc_port:,mgmt_prefix:,skeletone: -- "$@") || exit 1
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
    DB_NAME="controller"
    DB_USER="confine"
    DB_PASSWORD="confine"
    DB_HOST="localhost"
    DB_PORT="5432"
    KEYBOARD_LAYOUT=''
    PROJECT_NAME='confine'
    SKELETONE='confine'
    TINC_PORT=''
    MGMT_PREFIX=''

    while [ $# -gt 0 ]; do
        case $1 in
            -t|--type) TYPE="${2:1:${#2}-2}"; type=true; shift ;;
            -i|--image) IMAGE="${2:1:${#2}-2}"; image=true; shift ;;
            -S|--image_size) IMAGE_SIZE="${2:1:${#2}-2}"; image_size=true; shift ;;
            -d|--directory) DIRECTORY="${2:1:${#2}-2}"; directory=true; shift ;;
            -u|--user) USER="${2:1:${#2}-2}"; shift ;;
            -I|--install_path) INSTALL_PATH="${2:1:${#2}-2}"; shift ;;
            -p|--password) PASSWORD="${2:1:${#2}-2}"; shift ;;
            -a|--arch) ARCH="${2:1:${#2}-2}"; shift ;;
            -s|--suite) SUITE="${2:1:${#2}-2}"; shift ;;
            -U|--db_name) DB_NAME="${2:1:${#2}-2}"; shift ;;
            -U|--db_user) DB_USER="${2:1:${#2}-2}"; shift ;;
            -W|--db_password) DB_PASSWORD="${2:1:${#2}-2}"; shift ;;
            -S|--db_host) DB_HOST="${2:1:${#2}-2}"; create_db=false; shift ;;
            -P|--dp_port) DB_PORT="${2:1:${#2}-2}"; shift ;;
            -k|--keyboard_layout) KEYBOARD_LAYOUT="${2:1:${#2}-2}"; shift ;;
            -j|--project_name) PROJECT_NAME="${2:1:${#2}-2}"; shift ;;
            -l|--skeletone) SKELETONE="${2:1:${#2}-2}"; shift ;;
            -t|--tinc_port) TINC_PORT="${2:1:${#2}-2}"; shift ;;
            -m|--mgmt_prefix) MGMT_PREFIX="${2:1:${#2}-2}"; shift ;;
            -h|--help) print_full_install_help; exit 0 ;;
            (--) shift; break;;
            (-*) echo "$0: Err. - unrecognized option $1" 1>&2; exit 1;;
            (*) break;;
        esac
        shift
    done
    unset OPTIND
    unset opt
    
    check_root
    
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
        echo "Debootstraping a base system ..."
        run debootstrap --include=locales --arch=$ARCH $EXCLUDE $SUITE $DIRECTORY || exit 1
        
        custom_mount -s $DIRECTORY
        trap "custom_umount -sl $DIRECTORY; $image && rm -fr $DIRECTORY; exit 1;" INT TERM EXIT 
        chroot $DIRECTORY /bin/bash -c "basic_strap_configuration $PASSWORD $KEYBOARD_LAYOUT"
        
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
            echo -e "#!/bin/sh\nexit 101\n" > $DIRECTORY/usr/sbin/policy-rc.d
            chmod 755 $DIRECTORY/usr/sbin/policy-rc.d
        fi
        chroot $DIRECTORY /bin/bash -c "full_install_common $PROJECT_NAME $SKELETONE $USER $PASSWORD"
        rm -fr $DIRECTORY/usr/sbin/policy-rc.d
        
        chroot $DIRECTORY /bin/bash -c "full_install_postponed $INSTALL_PATH $USER $DB_NAME $DB_USER $DB_PASSWORD"
        chroot $DIRECTORY /bin/bash -c "generate_ssh_keys_postponed $USER"
        
        # Clean up
        custom_umount -s $DIRECTORY
        [ $TYPE == 'bootable' ] && custom_umount -d $DIRECTORY
        $image && custom_umount -l $DIRECTORY
        trap - INT TERM EXIT
        $image && [ -e $DIRECTORY ] && { mountpoint -q $DIRECTORY || rm -fr $DIRECTORY; }
    else
        # local installation
        run full_install_common "$PROJECT_NAME" "$SKELETONE" "$USER" "$PASSWORD"
        run full_install_running_services "$INSTALL_PATH" "$USER" "$DB_NAME" "$DB_USER" "$DB_PASSWORD"
    fi
    
    echo -e "\n ... seems that everything went better than expected :)"
}
export -f full_install


[ $# -lt 1 ] && print_help
$1 "${@}"
