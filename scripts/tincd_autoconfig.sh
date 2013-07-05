#!/bin/sh

set -u


USERNAME='confine'
PASSWORD='confine'
PUBKEY_FILE='/etc/tinc/confine/hosts/host_31'
# TODO get urls from base
APIBASE='http://devel.controller.confine-project.eu:8888/api/'


bold=$(tput bold)
normal=$(tput sgr0)
red=$(tput setf 4)
green=$(tput setf 2)
counter=0


echo_ok () {
    echo "${bold}${green}OK${normal}$@" >& 2
}


fail () {
    echo "${bold}${red}FAIL${normal}\n\n${red}$@${normal}" >& 2
    exit $counter
}


echo_step () {
    counter=$((counter+1))
    echo -n "  ${counter}. $@... "  >& 2
}


api_call () {
    # curl wrapper specialized in REST+json calls
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -H "Accept: application/json" "${@}")
    error=$?
    HTTP_CODE=$(echo "$RESPONSE"|grep '^HTTP_CODE:'|cut -d':' -f2|head -n1)
    RESPONSE=$(echo "$RESPONSE"|grep -v "^HTTP_CODE:")
    RESPONSE=$(echo "$RESPONSE"|python -mjson.tool 2> /dev/null) && echo "$RESPONSE"
    if [ "$HTTP_CODE" != "" ] && [ "$HTTP_CODE" != "200" ]; then
        echo "HTTP_CODE:$HTTP_CODE"
        exit $HTTP_CODE
    fi
    if [ $error != 0 ]; then
        exit $error
    fi
}


echo "\n${bold} Confine-controller tincd auto-configuration tool ${normal}"


if [ ! $PASSWORD ]; then
    echo -n "\n     Enter password for user $USERNAME: "
    stty -echo
    read PASSWORD
    stty echo
    echo ''
fi


echo_step "Authenticating with the server"
    URL="http://devel.controller.confine-project.eu:8888/api-token-auth/"
    DATA="username=$USERNAME&password=$PASSWORD"
    AUTH=$(api_call -X POST $URL -d "$DATA") || fail "$AUTH"
echo_ok


echo_step "Reading auth token"
    TOKEN=$(echo "$AUTH"|grep '"token":') || fail
    TOKEN=$(echo "$TOKEN"|cut -d'"' -f4)
    TOKEN_HEADER="Authorization: Token $TOKEN"
echo_ok


echo_step "Retrieving current host description"
    URL="http://devel.controller.confine-project.eu:8888/api/hosts/3"
    HOST=$(api_call $URL) || fail "$HOST"
echo_ok


echo_step "Getting local public key"
    PUBKEY=$(cat $PUBKEY_FILE | \
         grep -A 100 -- '-----BEGIN RSA PUBLIC KEY-----' | \
         grep -B 100 -- '-----END RSA PUBLIC KEY-----') || fail
    PUBKEY=$(echo "$PUBKEY"|tr '\n' '"'|sed "s/\"/\\\\\\\n/g")
    HOST=$(echo "$HOST"|sed "s=\"pubkey\":.*=\"pubkey\": \"$PUBKEY\"=") || fail
echo_ok


echo_step "Uploading public key to remote server"
    URL="http://devel.controller.confine-project.eu:8888/api/hosts/3"
    JSON="Content-Type: application/json"
    HOST=$(api_call "$URL" -H "$TOKEN_HEADER" -H "$JSON" -d "$HOST" -X PUT) || fail "$HOST"
echo_ok


echo "$HOST"|python -mjson.tool
