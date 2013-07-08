#!/bin/bash

set -u


NET_NAME='confine'
PORT_NUM=655
URL=''
create=''
USERNAME=''
PASSWORD=''
BASE_URL=''
HOST_URL=''


bold=$(tput bold)
normal=$(tput sgr0)
red=$(tput setf 4)
green=$(tput setf 2)
counter=0


print_help () {
    cat <<- EOF
		
		  ${bold}NAME${normal}
		      ${bold}tincd_autoconfig.sh${normal} - Tinc daemon autoconfiguration tool
		    
		  ${bold}SYNOPSIS${normal}
		      ${bold}tincd_autoconfig.sh [options] [url] ${normal}
		    
		  ${bold}OPTIONS${normal}
		      ${bold}-n, --net${normal}
		          Tinc net name
		    
		      ${bold}-p, --port${normal}
		          Tinc port number
		    
		      ${bold}-u, --username${normal}
		          Your controller's username
		     
		      ${bold}-w, --password${normal}
		          Your username's password
		    
		      ${bold}-c, --create${normal}
		          Whether create a new host or not
		          API base url should be provided
		    
		      ${bold}-h, --help${normal}
		          This help
		    
		  ${bold}USAGE${normal}
		      ${bold}Configure an existing host${normal}
		          autoconfig.sh http://api.url-to.your/hosts/xxx
		    
		      ${bold}Create a new host${normal}
		          autoconfig.sh http://base.api.url/ -c
		    
		EOF
}


opts_fail () {
    echo -e "${red}$@${normal}" >& 2
    exit 2
}


opts=$(getopt -o n:p:w:u:hc -l net:,port:,password:,username:,help,create -- "$@") || exit 1
set -- $opts

while [ $# -gt 0 ]; do
    case $1 in
        -n|--net) NET_NAME="${2:1:${#2}-2}"; shift ;;
        -p|--port) PORT_NUM="${2:1:${#2}-2}"; shift ;;
        -u|--username) USERNAME="${2:1:${#2}-2}"; shift ;;
        -w|--password) PASSWORD="${2:1:${#2}-2}"; shift ;;
        -c|--create) create=true; ;;
        -h|--help) print_help; exit 0 ;;
        (--) [[ $# -ne 2 ]] && opts_fail "What url?" $@; \
             URL="${2:1:${#2}-2}"; shift; break;;
        (-*) echo opts_fail "Unrecognized option $1";;
        (*) break;;
    esac
    shift
done
unset OPTIND
unset opt


echo_ok () {
    echo "${bold}${green}OK${normal}$@" >& 2
}


fail () {
    echo -e "${bold}${red}FAIL${normal}\n\n${red}$@${normal}" >& 2
    exit $counter
}


echo_step () {
    counter=$((counter+1))
    echo -n "  ${counter}. $@... "  >& 2
}


api_call () {
    # curl wrapper specialized in REST+json calls
    local RESPONSE; local HTTP_CODE;
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -H "Accept: application/json" "${@}")
    HTTP_CODE=$(echo "$RESPONSE"|grep '^HTTP_CODE:'|cut -d':' -f2|head -n1)
    RESPONSE=$(echo "$RESPONSE"|grep -v "^HTTP_CODE:")
    RESPONSE=$(echo "$RESPONSE"|python -mjson.tool 2> /dev/null) && echo "$RESPONSE"
    local error=$?
    local good=''
    for code in $(echo "000 200 201"); do
        if [[ "$HTTP_CODE" == "$code" ]]; then
            [[ $error != 0 ]] && exit 2
            good=true
        fi
    done
    if [[ ! $good ]]; then
        echo "HTTP_CODE:$HTTP_CODE"
        exit $HTTP_CODE
    fi
}


get_member () {
    # Returns selected nested JSON object from stdin
    local lines=""
    while read -r line; do
        lines="$lines$line"
    done
    local get=''
    for obj in $@; do
        get="${get}.get('$obj')"
    done
    lines=$(echo "$lines"|tr "'" '"')
    local CMD="import json, sys; print json.dumps(json.loads(sys.stdin.read())$get)"
    OBJECT=$(echo "$lines"|python -c "$CMD" 2> /dev/null)
    local error=$?
    echo "$OBJECT" | sed -e 's/^\"//g' -e 's/\"$//g'
    exit $error
}


get_multiple_objects () {
    # Returns each of the objects in a JSON list from stdin
    local lines=""
    while read -r line; do
        lines="$lines$line"
    done
    lines=$(echo "$lines"|tr "'" '"')
    lines=$(echo "$lines"|sed "s/: true,/: True,/g"|sed "s/: false,/: False,/g")
    lines=$(echo "$lines"|sed "s/: true}/: True}/g"|sed "s/: false}/: False}/g")
    local CMD="import json, sys \nfor obj in eval(sys.stdin.read()): print json.dumps(obj)"
    echo "$lines"|python -c "$(echo -e $CMD)" 2> /dev/null
}


get_link () {
    # Given a URL and a REL returns its link from Links header
    local URL=$1
    local REL=$2
    local HEADERS=$(curl -s -I $URL) || fail "$HEADERS"
    local LINK_HEADERS=$(echo "$HEADERS"|grep 'Link: '|tr ',' '\n')
    local HEADER=$(echo "$LINK_HEADERS"|grep "rel=\"$REL\""|awk -F"[<>;]" '{print $2}')
    [[ "$HEADER" ]] || exit 2
    echo "$HEADER"
}


echo -e "\n${bold} Confine-controller tincd auto-configuration tool ${normal}"


$(apt-get --help &> /dev/null) || fail 'Debian-like OS is required'
$(python --version &> /dev/null) || fail 'Python is required'
sudo echo -n || fail 'Sudo is required to run this script'


if [[ $create ]]; then
    BASE_URL=$URL
    if [[ ! $USERNAME ]]; then
        DOMAIN=$(echo $BASE_URL|cut -d'/' -f3)
        echo -n "     Enter your $DOMAIN username: "
        read USERNAME
    fi
else
    HOST_URL=$URL
    echo_step "Retrieving current host description"
        HOST=$(api_call $HOST_URL) || fail "$HOST"
        HOST_ADDR=$(echo "$HOST"|get_member "mgmt_net" "addr") || fail
        HOST_NAME=$(echo "$HOST"|get_member "mgmt_net" "tinc_client" "name") || fail
    echo_ok
    if [[ ! $USERNAME ]]; then
        echo_step "Getting host username"
            USER_URL=$(echo "$HOST"|get_member "owner" "uri")
            USER=$(api_call $USER_URL) || fail "$USER"
            USERNAME=$(echo "$USER"|get_member "username")
        echo_ok
    fi
fi


if [[ ! $PASSWORD ]]; then
    echo -n "     Enter password for user $USERNAME: "
        read -s PASSWORD
    echo ''
fi


echo_step "Authenticating with the server"
    # TODO create auth relation type
    AUTH_URL="http://sandbox.confine-project.eu/api-token-auth/"
    DATA="username=$USERNAME&password=$PASSWORD"
    AUTH=$(api_call -X POST $AUTH_URL -d "$DATA") || fail "$AUTH"
echo_ok


echo_step "Reading auth token"
    TOKEN=$(echo "$AUTH"|grep '"token":') || fail
    TOKEN=$(echo "$TOKEN"|cut -d'"' -f4)
    TOKEN_HEADER="Authorization: Token $TOKEN"
echo_ok


if [[ $create ]]; then
    echo_step "Creating remote tinc host"
        USER_URL=$(get_link $BASE_URL 'http://confine-project.eu/rel/server/user-list') || fail
        USER=$(api_call "${USER_URL}?username=$USERNAME")
        USER=$(echo "$USER"|get_multiple_objects)
        USER_URL=$(echo "$USER"|get_member "uri")
        LIST_URL=$(get_link $BASE_URL 'http://confine-project.eu/rel/server/host-list') || fail
        HOST_NAME=$(hostname)
        DATA="{\"owner\": {\"uri\": \"$USER_URL\"}, \"description\": \"$HOSTNAME\", \"mgmt_net\": []}"
        JSON="Content-Type: application/json"
        HOST=$(api_call "$LIST_URL" -H "$TOKEN_HEADER" -H "$JSON" -d "$DATA" -X POST) || fail "$HOST"
        HOST_URL=$(echo "$HOST"|get_member 'uri') || fail
    echo_ok
fi


echo_step "Retreiving server and gateways configuration"
    [[ ! $BASE_URL ]] && {
        BASE_URL=$(get_link $HOST_URL 'http://confine-project.eu/rel/server/base') || fail; }
    SERVER_URL=$(get_link $BASE_URL 'http://confine-project.eu/rel/server/server') || fail
    SERVER=$(api_call $SERVER_URL) || fail "$SERVER"
    SERVER_PUBKEY=$(echo "$SERVER"|get_member 'mgmt_net' 'tinc_server' 'pubkey')
    SERVER_ADDR=$(echo "$SERVER"|get_member "mgmt_net" "addr")
    ADDRS=$(echo "$SERVER"|get_member "mgmt_net" "tinc_server" "addresses")
    HOST_ISLAND=$(echo "$HOST"|get_member "mgmt_net" "tinc_client" "island" "uri")
    SERVER_ADDRS=""
    while read obj; do
        ADDR=$(echo "$obj"|get_member "addr")
        PORT=$(echo "$obj"|get_member "port")
        ISLAND=$(echo "$obj"|get_member "island" "uri")
        # Addr priority based on island
        if [[ "$ISLAND" == "$HOST_ISLAND" ]]; then
            SERVER_ADDRS="${ADDR} ${PORT}\n${SERVER_ADDRS}"
        else
            SERVER_ADDRS="${SERVER_ADDRS}${ADDR} ${PORT}\n"
        fi
    done < <(echo "$ADDRS"|get_multiple_objects)
    SERVER_ADDRS=${SERVER_ADDRS::-2}
echo_ok


$(tincd --help &> /dev/null) || {
    echo_step "Installing tincd"
        sudo apt-get update &> /dev/null || fail
        sudo apt-get install --force-yes tinc &> /dev/null || fail
    echo_ok
}


echo_step "Creating tincd config files"
    echo_tinc_conf () {
        echo "ConnectTo = server"
        echo "Name = $HOST_NAME"
        echo "Port = $PORT_NUM"
    }
    echo_server_host () {
        echo -e "$SERVER_ADDRS" | while read line; do
            echo "Address = $line"
        done
        echo "Subnet = $SERVER_ADDR"
        echo -e "\n$SERVER_PUBKEY"
    }
    echo_tinc_up () {
        echo '#!/bin/sh'
        echo 'ip -6 link set "$INTERFACE" up mtu 1400'
        echo "ip -6 addr add $HOST_ADDR/48 dev \"\$INTERFACE\""
    }
    echo_tinc_down () {
        echo '#!/bin/sh'
        echo "ip -6 addr del $HOST_ADDR/48 dev \"\$INTERFACE\""
        echo 'ip -6 link set "$INTERFACE" down'
    }
    dev_null_wrapper () {
        local BASE_DIR="/etc/tinc/${NET_NAME}"
        # Create and configure the confine network
        sudo mkdir -p ${BASE_DIR}/hosts || fail
        echo_tinc_conf | sudo tee ${BASE_DIR}/tinc.conf || fail
        echo "Subnet = $HOST_ADDR" | sudo tee ${BASE_DIR}/hosts/${HOST_NAME}
        echo_server_host | sudo tee ${BASE_DIR}/hosts/server || fail
        
        # Create scripts for setting up and down the network interface
        echo_tinc_up | sudo tee ${BASE_DIR}/tinc-up || fail
        echo_tinc_down | sudo tee ${BASE_DIR}/tinc-down || fail
        sudo chmod a+rx ${BASE_DIR}/tinc-{up,down} || fail
        
        # Enable confine network to automatically start on boot
        grep ${NET_NAME} /etc/tinc/nets.boot &> /dev/null || {
            echo ${NET_NAME} | sudo tee -a /etc/tinc/nets.boot || fail
        }
    }
    dev_null_wrapper > /dev/null || fail
echo_ok


if [ -e /etc/tinc/$NET_NAME/rsa_key.priv ]; then
    echo_step "Getting existing local public key"
        CMD="openssl rsa -in /etc/tinc/$NET_NAME/rsa_key.priv -pubout"
        PUBKEY=$(sudo $CMD 2> /dev/null) || fail
        PUBKEY=$(echo "$PUBKEY"|tr '\n' '"'|sed "s/\"/\\\\\\\n/g")
        HOST=$(echo "$HOST"|sed "s=\"pubkey\":.*=\"pubkey\": \"$PUBKEY\"=") || fail
    echo_ok
else
    echo_step "Generating new private key"
        echo -e "\r"|sudo tincd -n $NET_NAME -K &> /dev/null || fail
    echo_ok
fi


echo_step "Uploading public key to remote server"
    JSON="Content-Type: application/json"
    HOST=$(api_call "$HOST_URL" -H "$TOKEN_HEADER" -H "$JSON" -d "$HOST" -X PUT) || fail "$HOST"
echo_ok


echo_step "Restarting tinc daemon"
    sudo /etc/init.d/tinc restart &> /dev/null || fail
echo_ok


echo ""
echo "Ping the server for testing the connectivity!"
echo "    ping6 $SERVER_ADDR"
echo ""
