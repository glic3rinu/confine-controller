#!/bin/bash

set -u

bold=$(tput bold)
normal=$(tput sgr0)


run () {
    echo " ${bold}# ${@}${normal}"
    "${@}"
}
export -f run

runsu () {
    local user=$1
    shift
    echo " ${bold}\$ ${@}${normal}"
    su "$user" -c "${@}"
}
export -f runsu


check_root () {
    [ $(whoami) != 'root' ] && { echo -e "\nErr. This should be run as root\n" >&2; exit 1; }
}
export -f check_root


try_create_system_user() {
    # USAGE: try_create_system_user user password
    
    local USER=$1
    local PASSWORD=$2
    
    if [[ ! $(id $USER &> /dev/null) ]]; then
        # disabled user by default
        run useradd $USER -s "/bin/bash"
        [[ $PASSWORD != false ]] && echo "$USER:$PASSWORD"|chpasswd
        run mkdir /home/$USER
        run chown $USER.$USER /home/$USER
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


clean () {
    run rm -fr ~/.cache/pip
    run rm -fr /tmp/pip-*
    run rm -fr /tmp/build
    run rm -fr /tmp/src
    run apt-get clean
}
export -f clean


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
    
    run apt-get update
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


deploy_common () {
    check_root
    
    local DIR=$(eval echo $1)
    local PROJECT_NAME=$2
    local SKELETONE=$3
    local USER=$4
    local PASSWORD=$5
    local BASE_IMAGE_PATH=$6
    local BUILD_PATH=$7
    local VERSION=$8
    
    run apt-get update
    run apt-get install -y --force-yes sudo nano python-pip
    # for cleaning pip garbage afterwards
    cd /tmp
    
    if [[ ! $(pip freeze|grep confine-controller) ]]; then
        if [[ $VERSION == false ]]; then
            run pip install confine-controller --upgrade
        else
            run pip install confine-controller==$VERSION
        fi
    else
        run python $DIR/manage.py upgradecontroller --pip --version $VERSION
    fi
    run controller-admin.sh install_requirements
    try_create_system_user $USER $PASSWORD
    adduser $USER sudo
    cd $(eval echo "~$USER")
    runsu $USER "controller-admin.sh clone $PROJECT_NAME --skeletone $SKELETONE"
}
export -f deploy_common


deploy_running_services () {
    check_root
    
    local DIR=$(eval echo $1)
    local USER=$2
    local DB_NAME=$3
    local DB_USER=$4
    local DB_PASSWORD=$5
    local MGMT_PREFIX=$6
    local TINC_ADDRESS=$7
    local TINC_PORT=$8
    local TINC_PRIV_KEY=$9
    local TINC_PUB_KEY=${10}
    local CURRENT_VERSION=${11}

    local cmd
    
    cd $DIR
    run python manage.py setuppostgres --db_name $DB_NAME --db_user $DB_USER --db_password $DB_PASSWORD
    runsu $USER "python manage.py syncdb --noinput"
    runsu $USER "python manage.py migrate --noinput"
    runsu $USER "python manage.py createsuperuser"  # XXXX asks username, email, name, password

    run python manage.py setupceleryd --username $USER
    
    cmd="python manage.py setuptincd --noinput"
        [[ $MGMT_PREFIX != false ]] && cmd="$cmd --mgmt_prefix $MGMT_PREFIX"
        [[ $TINC_ADDRESS != false ]] && cmd="$cmd --tinc_address $TINC_ADDRESS"
        [[ $TINC_PRIV_KEY != false ]] && cmd="$cmd --tinc_privkey $TINC_PRIV_KEY"
        [[ $TINC_PUB_KEY != false ]] && cmd="$cmd --tinc_pubkey $TINC_PUB_KEY"
        [[ $TINC_PORT != false ]] && cmd="$cmd --tinc_port $TINC_PORT"
        run $cmd
    runsu $USER "python manage.py updatetincd"

    runsu $USER "python manage.py setuppki"  # XXXX asks country, state, locality, orgname, orgunit, email

    runsu $USER "python manage.py collectstatic --noinput"

    run python manage.py setupnginx

    runsu $USER "python manage.py createmaintenancekey --noinput"

    cmd="python manage.py setupfirmware"
        [[ $BASE_IMAGE_PATH != false ]] && cmd="$cmd --base_image_path $BASE_IMAGE_PATH"
        [[ $BUILD_PATH != false ]] && cmd="$cmd --build_path $BUILD_PATH"
        run $cmd
    runsu $USER "python manage.py syncfirmwareplugins"

    run python manage.py restartservices
    [[ $CURRENT_VERSION != false ]] && run python manage.py postupgradecontroller --specifics --from $CURRENT_VERSION
}
export -f deploy_running_services


function deploy_postponed () {
    # USAGE: echo_portal_configuration_steps dir user db_name db_user db_password
    
    # Some configuration commands should run when the database is online, 
    # this function postpone these actions until first boot.
    
    local DIR=$(eval echo $1)
    local USER=$2
    local DB_NAME=$3
    local DB_USER=$4
    local DB_PASSWORD=$5
    local MGMT_PREFIX=$6
    local TINC_ADDRESS=$7
    local TINC_PORT=$8
    local TINC_PRIV_KEY=$9
    local TINC_PUB_KEY=${10}
    
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
		
		controller-admin.sh deploy_running_services "$DIR" "$USER" "$DB_NAME" \
		    "$DB_USER" "$DB_PASSWORD" "$MGMT_PREFIX" "$TINC_ADDRESS" "$TINC_PORT" \
		    "$TINC_PRIV_KEY" "$TINC_PUB_KEY" "false"
		insserv -r /etc/init.d/setup_portal_db
		rm -f \$0
		EOF
    
    chmod a+x /etc/init.d/setup_portal_db
    insserv /etc/init.d/setup_portal_db
}
export -f deploy_postponed


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


print_deploy_help () {
    cat <<- EOF 
		
		${bold}NAME${normal}
		    ${bold}controller-admin.sh deploy${normal} - Confine server deployment subsystem
		    
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
		            system user that will run the portal, it will be created if it
		            does not exist (default confine)
		    
		    ${bold}-p, --password${normal}
		            password is needed if USER does not exist (default user disabled)
		    
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
		            if this option is provided, no DB will be created nor installed
		            (default localhost)
		    
		    ${bold}-P, --db_port${normal}
		            default 5432
		            
		    ${bold}-k, --keyboard_layout${normal}
		            supported layouts: spanish and english (default)
		            
		    ${bold}-j, --project_name${normal}
		            project name, default confine.
		            
		    ${bold}-l, --skeletone${normal}
		            project skeletone, default project_name.
		            
		    ${bold}-A, --tinc_address${normal}
		            tinc port
		    
		    ${bold}-t, --tinc_port${normal}
		            tinc port
		    
		    ${bold}-v, --tinc_priv_key${normal}
		            tinc private key file path
		    
		    ${bold}-e, --tinc_pub_key${normal}
		            tinc pubkey file path
		    
		    ${bold}-m, --mgmt_prefix${normal}
		            management network prefix
		    
		    ${bold}-B, --base_image_path${normal}
		            filesystem path where base images are stored
		    
		    ${bold}-b, --build_image${normal}
		            path where built images gets stored
		    
		${bold}EXAMPLES${normal}
		    controller-admin.sh deploy --type bootable --image /tmp/server.img --suite squeeze
		    
		    controller-admin.sh deploy --type local -u confine -p 2hd4nd
		    
		EOF
}
export -f print_deploy_help


function deploy () {
    opts=$(getopt -o Cht:i:S:d:u:p:a:s:U:P:H:I:W:N:k:j:a:t:v:e:m:l:B:b:c -l create,user:,password:,help,type:,image:,image_size:,directory:,suite:,arch:,db_name:,db_user:,db_password:,db_host:,db_port:,install_path:,keyboard_layout:,project_name:,tinc_address:,tinc_port:,tinc_priv_key:,tinc_pub_key:,mgmt_prefix:,skeletone:,base_image_path:,build_path:,controller_version: -- "$@") || exit 1
    set -- $opts
    
    # Default values
    type=false
    image=false
    IMAGE_SIZE="2G"
    image_size=false
    directory=false
    USER="confine"
    PASSWORD=false
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
    SKELETONE=false
    TINC_ADDRESS=false
    TINC_PORT=false
    TINC_PRIV_KEY=false
    TINC_PUB_KEY=false
    MGMT_PREFIX=false
    BASE_IMAGE_PATH=false
    BUILD_PATH=false
    VERSION=false
    
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
            -D|--db_name) DB_NAME="${2:1:${#2}-2}"; shift ;;
            -U|--db_user) DB_USER="${2:1:${#2}-2}"; shift ;;
            -W|--db_password) DB_PASSWORD="${2:1:${#2}-2}"; shift ;;
            -S|--db_host) DB_HOST="${2:1:${#2}-2}"; create_db=false; shift ;;
            -P|--dp_port) DB_PORT="${2:1:${#2}-2}"; shift ;;
            -k|--keyboard_layout) KEYBOARD_LAYOUT="${2:1:${#2}-2}"; shift ;;
            -j|--project_name) PROJECT_NAME="${2:1:${#2}-2}"; shift ;;
            -l|--skeletone) SKELETONE="${2:1:${#2}-2}"; shift ;;
            -A|--tinc_address) TINC_ADDRESS="${2:1:${#2}-2}"; shift ;;
            -t|--tinc_port) TINC_PORT="${2:1:${#2}-2}"; shift ;;
            -v|--tinc_priv_key) TINC_PRIV_KEY="${2:1:${#2}-2}"; shift ;;
            -e|--tinc_pub_key) TINC_PUB_KEY="${2:1:${#2}-2}"; shift ;;
            -B|--base_image_path) BASE_IMAGE_PATH="${2:1:${#2}-2}"; shift ;;
            -b|--build_path) BUILD_PATH="${2:1:${#2}-2}"; shift ;;
            -m|--mgmt_prefix) MGMT_PREFIX="${2:1:${#2}-2}"; shift ;;
            -c|--controller_version) VERSION="${2:1:${#2}-2}"; shift ;;
            -h|--help) print_deploy_help; exit 0 ;;
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
    
    [ $INSTALL_PATH == false ] && INSTALL_PATH="~$USER/$PROJECT_NAME"
    [ $SKELETONE == false ] && SKELETONE=$PROJECT_NAME
    
    if [[ $TYPE != 'local' ]]; then
        if [[ $image != false ]]; then
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
        chroot $DIRECTORY /bin/bash -c "deploy_common $PROJECT_NAME $SKELETONE $USER $PASSWORD $BASE_IMAGE_PATH $BUILD_PATH $VERSION"
        rm -fr $DIRECTORY/usr/sbin/policy-rc.d
        
        chroot $DIRECTORY /bin/bash -c "deploy_postponed $INSTALL_PATH $USER $DB_NAME \
            $DB_USER $DB_PASSWORD $MGMT_PREFIX $TINC_ADDRESS $TINC_PORT $TINC_PRIV_KEY $TINC_PUB_KEY"
        chroot $DIRECTORY /bin/bash -c "generate_ssh_keys_postponed $USER"
        
        # Clean up
        chroot $DIRECTORY /bin/bash -c "clean"
        custom_umount -s $DIRECTORY
        [ $TYPE == 'bootable' ] && custom_umount -d $DIRECTORY
        $image && custom_umount -l $DIRECTORY
        trap - INT TERM EXIT
        $image && [ -e $DIRECTORY ] && { mountpoint -q $DIRECTORY || rm -fr $DIRECTORY; }
    else
        # local installation
        CURRENT_VERSION=$(python -c "from controller import get_version; print get_version();" || echo false)
        run deploy_common "$INSTALL_PATH" "$PROJECT_NAME" "$SKELETONE" "$USER" "$PASSWORD" "$BASE_IMAGE_PATH" "$BUILD_PATH" "$VERSION"
        run deploy_running_services "$INSTALL_PATH" "$USER" "$DB_NAME" "$DB_USER" \
            "$DB_PASSWORD" "$MGMT_PREFIX" "$TINC_ADDRESS" "$TINC_PORT" "$TINC_PRIV_KEY" \
            "$TINC_PUB_KEY" "$CURRENT_VERSION"
        clean
    fi
    
    echo -e "\n ... seems that everything went better than expected :)"
}
export -f deploy


deploy "${@}"
