#!/bin/bash

# USAGE: mountimage.sh -m BASE_IMAGE MOUNT_POINT TMP_PARTITION_FILE [PARTITION_NUMBER]
#        mountimage.sh -u BASE_IMAGE MOUNT_POINT TMP_PARTITION_FILE [PARTITION_NUMBER]
#
# REQUIREMENTS:
#   Install: fuseext2
#   Add user to fuser grou
#   OpenVZ container: vzctl set 102 --capability sys_admin:on --save


OPERATION=$([ $1 == '-u' ] && echo 'umount' || echo 'mount')
BASE_IMAGE="$2"
MOUNT_POINT="$3"
PARTITION_FILE=$4
PARTITION_NUMBER=$([ $5 ] && echo $5 || echo 12)

SECTOR=$(file $BASE_IMAGE|grep -Po '(?<=startsector ).*?(?=,)'|sed -n ${PARTITION_NUMBER}p)
[[ $SECTOR =~ ^[0-9]+$ ]] || exit 11

if [ $OPERATION == 'mount' ]; then 
    $(mountpoint -q $MOUNT_POINT) && exit 12
    dd if=$BASE_IMAGE of=$PARTITION_FILE skip=$SECTOR || { rm -fr $PARTITION_FILE; exit 13; }
    fuseext2 $PARTITION_FILE $MOUNT_POINT -o rw+ 
    # fuseext2 is a pice of crap since doesn't return a correct exit code, let's kludge
    $(mountpoint -q $MOUNT_POINT) || exit 14;
else
    fusermount -u $MOUNT_POINT || exit 15
    dd if=$PARTITION_FILE of=$BASE_IMAGE seek=$SECTOR || exit 16
fi


# Error Codes
#   11: "Unable to find start sector for partition $PARTITION_NUMBER"
#   12: "$MOUNT_POINT already mounted"
#   13: "Error extracting partition $PARTITION_NUMBER"
#   14: "Cannot mount extracted partition $PARTITION_NUMBER"
#   15: "Unable to unmount $MOUNT_POINT"
#   16: "Error joining extracted partition $PARTITION_NUMBER"


