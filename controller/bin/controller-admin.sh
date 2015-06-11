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
    show "${@}"
    "${@}"
}
export -f run


check_root () {
    [ $(whoami) != 'root' ] && { echo -e "\nErr. This should be run as root\n" >&2; exit 1; }
}
export -f check_root


get_controller_dir () {
    if ! $(echo "import controller"|python 2> /dev/null); then
        echo -e "\nErr. Controller not installed.\n" >&2
        exit 1
    fi
    PATH=$(echo "import controller, os; print os.path.dirname(os.path.realpath(controller.__file__))" | python)
    echo $PATH
}
export -f get_controller_dir


function print_install_requirements_help () {
    cat <<- EOF 
		
		${bold}NAME${normal}
		    ${bold}controller-admin.sh install_requirements${normal} - Installs all the controller requirements using apt-get and pip
		
		${bold}OPTIONS${normal}
		    ${bold}-d, --development${normal}
		        Installs minimal controller requirements using apt-get and pip
		    
		    ${bold}-p, --production${normal}
		        Installs all controller requirements using apt-get and pip (default)
		    
		    ${bold}--proxy <proxy>${normal}
                Specify a proxy in the form [user:passwd@]proxy.server:port.
		    
		    ${bold}-h, --help${normal}
		        Displays this help text
		
		EOF
}


function install_requirements () {
    # local is a deprecated option but kept for backwards compatibility
    opts=$(getopt -u -o dlph -l development,local,production,proxy:,help -- "$@") || exit 1
    set -- $opts
    development=false
    production=true
    proxy=''
    
    while [ $# -gt 0 ]; do
        case $1 in
            -d|--development) development=true; production=false; shift ;;
            -l|--local) production=true; shift ;; # backwards compatibility
            -p|--production) production=true; shift ;;
            --proxy) proxy="--proxy $2"; shift 2;;
            -h|--help) print_install_requirements_help; exit 0 ;;
            (--) shift; break;;
            (-*) echo "$0: Err. - unrecognized option $1" 1>&2; exit 1;;
            (*) break;;
        esac
        shift
    done
    unset OPTIND
    unset opt
    
    check_root
    CONTROLLER_PATH=$(get_controller_dir)
    
    DEVELOPMENT_APT="python-pip \
                     python-m2crypto \
                     python-psycopg2 \
                     python-dateutil \
                     postgresql \
                     rabbitmq-server \
                     python-dev gcc \
                     fuseext2 file \
                     tinc \
                     libevent-dev \
                     ntp"
    
    PRODUCTION_APT="libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev" # captcha
    
    #TODO(santiago): django-jsonfield 1.0 breaks backwards compatibility
    #                https://github.com/bradjasper/django-jsonfield/issues/57
    #TODO(santiago): Markdown 2.5 has some backwards incompatible changes
    #                https://pythonhosted.org/Markdown/release-2.5.html
    DEVELOPMENT_PIP="Django==1.6.10 \
                     django-celery-email==1.0.4 \
                     django-fluent-dashboard==0.4 \
                     South==1.0.2 \
                     IPy==0.81 \
                     django-extensions==1.4.9 \
                     django-transaction-signals==1.0.0 \
                     django-celery==3.0.23 \
                     celery==3.0.24 \
                     kombu==2.5.15 \
                     jsonfield==0.9.23 \
                     Markdown==2.4 \
                     django-filter==0.9.2 \
                     django-admin-tools==0.5.2 \
                     djangorestframework==2.3.14 \
                     paramiko==1.15.2 \
                     Pygments==2.0.1 \
                     pyflakes==0.8.1 \
                     requests==2.5.1 \
                     greenlet==0.4.5 \
                     gevent==1.0.2"
    PRODUCTION_PIP="django-simple-captcha==0.4.4 \
                    django-registration==1.0 \
                    django-google-maps==0.2.3"
    
    # Make sure locales are in place before installing postgres
    if [[ $({ perl --help > /dev/null; } 2>&1|grep 'locale failed') ]]; then
        run sed -i "s/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/" /etc/locale.gen
        run locale-gen
        update-locale LANG=en_US.UTF-8
    fi
    
    run apt-get update
    run apt-get install -y $DEVELOPMENT_APT
    run pip install $proxy $DEVELOPMENT_PIP
    
    # Some versions of rabbitmq-server will not start automatically by default unless ...
    sed -i "s/# Default-Start:.*/# Default-Start:     2 3 4 5/" /etc/init.d/rabbitmq-server
    sed -i "s/# Default-Stop:.*/# Default-Stop:      0 1 6/" /etc/init.d/rabbitmq-server
    run update-rc.d rabbitmq-server defaults
    
    if $production; then
        run apt-get install -y $PRODUCTION_APT
        # PIL has some mental problems with library paths
        [ ! -e /usr/lib/libjpeg.so ] && run ln -s /usr/lib/$(uname -m)-linux-gnu/libjpeg.so /usr/lib
        [ ! -e /usr/lib/libfreetype.so ] && run ln -s /usr/lib/$(uname -m)-linux-gnu/libfreetype.so /usr/lib
        [ ! -e /usr/lib/libz.so ] && run ln -s /usr/lib/$(uname -m)-linux-gnu/libz.so /usr/lib
        run pip install $proxy $PRODUCTION_PIP
    fi
    
    if [[ $(rabbitmqctl status|grep RabbitMQ|cut -d'"' -f4) == "1.8.1" ]]; then
        # Debian squeeze compat: Install kombu version compatible with old amq protocol
        run pip install $proxy celery==3.0.17 kombu==2.4.7 --upgrade
    fi
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
    [ "$#" -lt 2 ] && echo "Err. - project name not provided." && exit 1
    local SKELETONE=false
    local PROJECT_NAME="${2}"; shift
    
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
    
    [ $(whoami) == 'root' ] && { echo -e "\nYou don't want to run this as root\n" >&2; exit 1; }
    [ $SKELETONE == false ] && SKELETONE=$PROJECT_NAME
    CONTROLLER_PATH=$(get_controller_dir)
    if [[ ! -e $PROJECT_NAME/manage.py ]]; then
        run django-admin.py startproject $PROJECT_NAME --template="${CONTROLLER_PATH}/conf/project_template"
        # This is a workaround for this issue https://github.com/pypa/pip/issues/317
        run chmod +x $PROJECT_NAME/manage.py
        # End of workaround ###
    else
        echo "Not cloning: $PROJECT_NAME already exists."
    fi
    # Install bash autocompletition for django commands
    if [[ ! $(grep 'source $HOME/.django_bash_completion.sh' ~/.bashrc &> /dev/null) ]]; then
        # run wget https://raw.github.com/django/django/master/extras/django_bash_completion \
        #    --no-check-certificate -O ~/.django_bash_completion.sh
        cp ${CONTROLLER_PATH}/bin/django_bash_completion.sh ~/.django_bash_completion.sh
        echo 'source $HOME/.django_bash_completion.sh' >> ~/.bashrc
    fi

}
export -f clone


# check provided parameters
if [ $# -lt 1 ]; then
    print_help
else
    case $1 in
        clone|install_requirements) $1 "${@}";;
        *) print_help;;
    esac
fi
